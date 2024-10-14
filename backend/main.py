from typing import Annotated, Optional, List, Literal
from fastapi import FastAPI, Query, Depends, Body, File, Form, UploadFile, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import json

from pydantic import model_validator

import db
import user
from user import get_admin_permission_user, get_read_permission_user, get_write_permission_user, get_current_user
from models import NodeUpdate, PieceCreate, Log, UserInDB, BaseModel, NodeCreate, SubNode, Operation, QueryFilter, Filter

app = FastAPI()
app.include_router(user.router)

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://frontend_vue:3000",
    "http://frontend_vue:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory where images will be stored
UPLOAD_DIR = "uploaded_images"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def request_to_log(request: Request, user: UserInDB, body: BaseModel) -> Log:
    endpoint = request.url.path
    request_method = request.method
    return Log(username=user.username, endpoint=endpoint, request_method=request_method, request_body=body.model_dump_json())

def upload_file(file: UploadFile, file_path: str):
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

@app.get("/")
async def root():
    result = list(db.get_pieces_info_paginated(3875, 25))
    print(result[0])
    return result

@app.get("/pieces/", dependencies=[Depends(get_read_permission_user)])
async def get_pieces(skip: int = 0, limit: int = 0):
    return db.get_nodes_paginated(" :pieza", skip, limit)

@app.get("/components/", dependencies=[Depends(get_read_permission_user)])
async def get_piece_components(piece_id: int):
    return db.get_piece_components(piece_id)

@app.get("/pieces-by-nodes/", dependencies=[Depends(get_read_permission_user)])
async def get_piece_by_nodes(node_names: Annotated[list[str], Query()], nodes_label: str = ""):
    return db.filter_by_nodes_names_connected(node_names, "pieza", nodes_label)

@app.get("/piece-connected-nodes/", dependencies=[Depends(get_read_permission_user)])
async def get_nodes_connected_to_piece(piece_id: str):
    return db.get_nodes_without_tag_connected_to_node("componente", "pieza", id = piece_id)

@app.get("/component-connected-nodes/", dependencies=[Depends(get_read_permission_user)])
async def get_nodes_connected_to_component(component_id: str):
    return db.get_nodes_without_tag_connected_to_node("pieza", "componente", id = component_id)

@app.post("/pieces/")
def get_pieces_filtered(query_filters: dict[str, list[Filter]], skip: int = 0, limit: int = 50):
    # tag = params["tag"]
    # property_filter = json.decoder.JSONDecoder().decode(params["property_filter"])
    return db.get_pieces_info_paginated_filtered(query_filters, skip, limit)
    return params


@app.put("/add-piece", dependencies=[Depends(get_write_permission_user)])
def add_piece(request: Request, node_create: Annotated[PieceCreate, Body(...)], user: Annotated[UserInDB, Depends(get_current_user)], images: List[UploadFile] = File(...)):
    for file in images:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        upload_file(file, file_path)
        file_properties = {"size" : file.size}
        file_node = SubNode(node_id= file_path, properties=file_properties, relation_label="has_image", node_label="image")
        node_create.connected_nodes.append(file_node)
    result = db.create_update_piece(node_create.id, node_create.components, node_create.connected_nodes, node_create.properties)
    log = request_to_log(request, user, node_create)
    logdb = db.create_log(log)
    return result

@app.put("/add-component", dependencies=[Depends(get_write_permission_user)])
async def add_component(request: Request, 
                        user: Annotated[UserInDB, Depends(get_current_user)], 
                        node_create: Annotated[NodeCreate, Body(...)],
                        piece_id: Annotated[str, Form(...)],
                        images: List[UploadFile] = File(...)):
    for file in images:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        upload_file(file, file_path)
        file_properties = {"size" : file.size}
        file_node = SubNode(node_id= file_path, properties=file_properties, relation_label="has_image", node_label="image")
        node_create.connected_nodes.append(file_node)
    result = db.create_update_component(piece_id, node_create.id, node_create.connected_nodes, node_create.properties)
    log = request_to_log(request, user, node_create)
    logdb = db.create_log(log)
    return result

@app.delete("/pieza/", dependencies=[Depends(get_write_permission_user)])
async def delete_piece(node_id):
    to_delete = ["forma", "componente"]
    with db.get_db_driver() as driver:
        with driver.session() as session:
            with session.begin_transaction() as tx:
                return db.detete_piece(tx, node_id, to_delete)

@app.post("/upload-image/", dependencies=[Depends(get_write_permission_user)])
async def upload_image(node_id: str = Form(...), file: UploadFile = File(...)):
    # Save the uploaded file to the server's local file system
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        upload_file(file, file_path)

        # After saving the file, connect the image file path to the existing node in Neo4j
        with db.get_db_driver().session() as session:
            query = """
            MATCH (n {id: $node_id})
            SET n.image = $image_path
            RETURN n
            """
            result = session.run(query, node_id=node_id, image_path=file_path)

            # Ensure node exists and was updated
            updated_node = result.single()
            if not updated_node:
                raise HTTPException(status_code=404, detail="Node not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

    return {"message": f"Image uploaded and connected to node {node_id}", "file_path": file_path}

