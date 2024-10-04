from typing import Annotated, Optional
from fastapi import FastAPI, Query, Depends, File, Form, UploadFile, HTTPException
import shutil
import os

import db
import user
from user import get_admin_permission_user, get_read_permission_user, get_write_permission_user
from models import NodeUpdate, PieceCreate

app = FastAPI()
app.include_router(user.router)

# Directory where images will be stored
UPLOAD_DIR = "uploaded_images"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def upload_file(file: UploadFile, file_path: str):
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

@app.get("/")
async def root():
    return list(db.get_all_nodes())

@app.get("/pieces/")
async def get_pieces(skip: int = 0, limit: int = 0):
    return db.get_nodes_paginated(" :pieza", skip, limit)

@app.get("/components/")
async def get_piece_components(piece_id: int):
    return db.get_piece_components(piece_id)

@app.get("/pieces-by-nodes/")
async def get_piece_by_nodes(node_names: Annotated[list[str], Query()], nodes_label: str = ""):
    return db.filter_by_nodes_names_connected(node_names, "pieza", nodes_label)

@app.get("/piece-connected-nodes/")
async def get_nodes_connected_to_piece(piece_id: int):
    return db.get_nodes_without_tag_connected_to_node("componente", "pieza", id = piece_id)

@app.get("/component-connected-nodes/")
async def get_nodes_connected_to_piece(component_id: str):
    return db.get_nodes_without_tag_connected_to_node("componente", "pieza", id = component_id)

@app.put("/edit-piece/", dependencies=[Depends(get_write_permission_user)])
async def edit_piece(node_update: NodeUpdate):
    # validate form??
    ...
    

@app.put("/add-piece", dependencies=[Depends(get_write_permission_user)])
async def add_piece(node_create: Annotated[PieceCreate, Form()]):
    result = db.create_update_piece(node_create.id, node_create.components, node_create.connected_nodes, node_create.properties)
    print(result)
    return result

@app.delete("/pieza/", dependencies=[Depends(get_write_permission_user)])
async def delete_piece(node_id):
    to_delete = ["forma", "componente"]
    with db.get_db_driver() as driver:
        with driver.session() as session:
            with session.begin_transaction() as tx:
                return db.detete_piece(tx, node_id, to_delete)

@app.post("/upload-image/")
async def upload_image(node_id: str = Form(...), file: UploadFile = File(...)):
    # Save the uploaded file to the server's local file system
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        upload_file(file)

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