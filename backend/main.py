from typing import Annotated, Optional, List, Literal, IO, Any, Callable
from fastapi import FastAPI, Query, Depends, Body, File, Form, UploadFile, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from contextlib import asynccontextmanager
from neo4j.exceptions import ConstraintError
import shutil
import os
import json

from pathlib import Path
import asyncio
import filetype
from datetime import datetime
import io
import pandas as pd
import numpy as np

import db
import user
from user import get_admin_permission_user, get_read_permission_user, get_write_permission_user, get_current_user, add_user
from models import PieceCreate, Log, UserInDB, NodeCreate, SubNode, Filter, RoleEnum, NodeLabel, UserForm, NODES_RELATIONS

@asynccontextmanager
async def lifespan(app: FastAPI):
    "create admin user from env credentials if dont exists already"
    admin_users = db.get_all_nodes_property_filter("user", [Filter(key="role", operation= "=", val="admin")])   
    if (not admin_users):
        # else create admin user from .env credentials
        user = UserForm(
            username=os.getenv("ADMIN_USER", "admin"), 
            password=os.getenv("ADMIN_PASSWORD", "admin"), 
            role=RoleEnum.admin
        )
        await add_user(user)
    else:
        print("superuser already exists")
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(user.router)

origins = [
    "http://localhost",
    "http://localhost:8001",
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
UPLOAD_DIR = os.getenv("IMPORT_PATH", "uploaded_images")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

### UTILS ###
def request_to_log(request: Request, user: UserInDB, body: NodeCreate, node_id: str) -> Log:
    endpoint = request.url.path
    request_method = request.method
    # print(f"{user.username=} {endpoint=}", f"{request_method=}", f"{body.model_dump_json()=} {body.id=}")
    return Log(username=user.username, endpoint=endpoint, request_method=request_method, request_body=body.model_dump_json(), node_elementid=node_id)

def upload_file(file: UploadFile, relative_path: str):
    file_path = os.path.join(UPLOAD_DIR, relative_path)
        
    # Get the absolute destination path
    destination_path = os.path.abspath(file_path)

    # Ensure the destination folder exists; create it if it doesn't
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)

    # Copy the file to the destination
    with open(destination_path, 'wb') as dest_file:
        shutil.copyfileobj(file.file, dest_file)

def validate_file(accepted_file_types: list[str], max_file_size: int = 8388608) -> Callable[[IO], None]:
    def validate_file_size_type(file: IO):
        FILE_SIZE = max_file_size # 8MB

        file_info = filetype.guess(file.file)
        if file_info is None:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unable to determine file type",
            )

        detected_content_type = file_info.extension.lower()

        if (
            file.content_type not in accepted_file_types
            or detected_content_type not in accepted_file_types
        ):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported file type",
            )
        
        if file.size > FILE_SIZE:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Too large")
    return validate_file_size_type

validate_images = validate_file(accepted_file_types = [
    "image/png", "image/jpeg", "image/jpg", "image/heic", "image/heif", "image/heics", "png","jpeg", "jpg", "heic", "heif", "heics" 
])

validate_docs = validate_file(accepted_file_types = [
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/pdf", "application/msword", "text/plain",                     # TXT
    "application/vnd.oasis.opendocument.text", "pdf", "docx", "doc", "txt", "odt"
])

def attach_files_subnode_to_node(node_data: NodeCreate,
                                 files: List[UploadFile],
                                 subnode_label: NodeLabel = "imagen",
                                 prefix: str = "",
                                 validate_function: Callable = validate_images):
    if not files: return
    if type(node_data) == PieceCreate:
        mainnode_label = 'pieza'
    else:
        mainnode_label = 'componente'
    relation_label = NODES_RELATIONS[(mainnode_label, subnode_label)]
    for file in files:
        validate_function(file)
        relative_path = f"{prefix}_{str(datetime.now())}{file.filename}"
        upload_file(file, relative_path)
        file_properties = {"size" : file.size, "name" : file.filename}
        file_node = SubNode(node_id= relative_path, 
                            properties=file_properties, 
                            relation_label=relation_label, 
                            node_label=subnode_label, 
                            id_key='filename', 
                            method='CREATE')
        node_data.connected_nodes.append(file_node)

def parse_component_files(files: list[UploadFile], n_components: int) -> list[list[UploadFile]]:
    if not files: 
        files = []
    result = [[] for _ in range(n_components)] # create array with n_component list elements
    for file in files:
        # sorts files corresponding to each component
        component_index, index, filename = file.filename.split('_', 2)
        result[int(component_index)].append(file)
        # extracts original filename
        file.filename = filename
    return result

def delete_images(node_with_images: NodeCreate, tg: asyncio.TaskGroup):
    for image in filter(lambda node: node.node_label == 'imagen', node_with_images.connected_nodes):
        tg.create_task(os.remove(image.properties['filename']))

# TEST ROUTE
@app.get("/")
async def root():
    result = list(db.get_pieces_info_paginated(3875, 25))
    print(result[0])
    return result

### ROUTES ###
@app.get("/nodes", dependencies=[Depends(get_read_permission_user)])
async def get_nodes(labels: Annotated[list[NodeLabel], Query()]):
    return db.get_nodes_paginated(labels=labels, skip=0, limit=0)

@app.get("/nodes/tree", dependencies=[Depends(get_read_permission_user)])
async def get_nodes_tree(labels: Annotated[list[NodeLabel], Query()], rel_label: Annotated[str, Query()]):
    return db.get_nodes_as_tree(labels=labels, relation_label=rel_label)

@app.delete("/nodes", dependencies=[Depends(get_read_permission_user)])
async def delete_node(element_id: str):
    return db.delete_node_by_elementid(element_id)

@app.delete("/nodes/id", dependencies=[Depends(get_read_permission_user)])
async def delete_node_by_key(label: NodeLabel, key: str, val: Any):
    return db.delete_node_by_id_key(labels=[label], key=key, val=val)

@app.get("/pieces/", dependencies=[Depends(get_read_permission_user)])
async def get_pieces(skip: int = 0, limit: int = 50):
    return db.get_pieces_info_paginated(skip, limit)

@app.get("/components/", dependencies=[Depends(get_read_permission_user)])
async def get_piece_components(piece_id: Annotated[str, Query()]):
    return db.get_piece_components(piece_id)

@app.get("/pieces-by-nodes/", dependencies=[Depends(get_read_permission_user)])
async def get_piece_by_nodes(node_names: Annotated[list[str], Query()], nodes_label: Optional[NodeLabel] = None):
    return db.filter_by_nodes_names_connected(node_names, "pieza", nodes_label)

@app.get("/piece-connected-nodes/", dependencies=[Depends(get_read_permission_user)])
async def get_nodes_connected_to_piece(piece_id: str):
    return db.get_nodes_without_tag_connected_to_node("componente", "pieza", id = piece_id)

@app.get("/component-connected-nodes/", dependencies=[Depends(get_read_permission_user)])
async def get_nodes_connected_to_component(component_id: str):
    return db.get_nodes_without_tag_connected_to_node("pieza", "componente", id = component_id)

@app.post("/pieces/", dependencies=[Depends(get_read_permission_user)])
def get_pieces_filtered(query_filters: dict[NodeLabel, list[Filter]], skip: int = 0, limit: int = 50):
    # tag = params["tag"]
    # property_filter = json.decoder.JSONDecoder().decode(params["property_filter"])
    return db.get_pieces_info_paginated_filtered(query_filters, skip, limit)

@app.put("/add-piece", dependencies=[Depends(get_write_permission_user)])
def add_piece(request: Request, 
              node_create: Annotated[PieceCreate, Body(...)], 
              user: Annotated[UserInDB, Depends(get_current_user)], 
              images: Annotated[list[UploadFile], File()] = None,
              component_images: Annotated[list[UploadFile], File()] = None,
              component_interventions: Annotated[list[UploadFile], File()] = None,):
    """
    Creates/Updates a piece node, creates connections based on ``SubNode``'s specifications and Creates/Updates Components
    attached to this piece on the same transaction, images files are saved in `UPLOAD_DIR` and nodes created are connected 
    to the piece node

    endpoint expects paramaters encoded as multipart form 

    parameters
    ----------
    node_create: str
        string JSON with PieceCreate schema
    images: list[UploadFile]
        images that will attach to the piece node
    """
    if len(node_create.components) < 1: return HTTPException(422, detail="Se espera al menos 1 componente para esta pieza")
    attach_files_subnode_to_node(node_create, images)
    parsed_component_images = parse_component_files(component_images, len(node_create.components))
    parsed_component_interventions = parse_component_files(component_interventions, len(node_create.components))
    for i, component in enumerate(node_create.components):
        attach_files_subnode_to_node(component, parsed_component_images[i])
        attach_files_subnode_to_node(component, parsed_component_interventions[i], subnode_label='intervencion', prefix='intervenciones/', validate_function=validate_docs)
    #print(node_create.components)
    with db.Tx() as tx:
        try:
            result = db.create_update_piece(node_create.id, node_create.components, node_create.connected_nodes, node_create.properties, tx=tx)
        except ConstraintError:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Número de inventario repetido")
        #print(result)
        log = request_to_log(request, user, node_create, result[0]['id'])
        logdb = db.create_log(log, tx=tx)
        print(logdb)
    return result

@app.put("/add-component", dependencies=[Depends(get_write_permission_user)])
async def add_component(request: Request, 
                        user: Annotated[UserInDB, Depends(get_current_user)], 
                        node_create: Annotated[NodeCreate, Form(...)],
                        piece_id: Annotated[str, Form(...)],
                        images: list[UploadFile] = None,
                        interventions: list[UploadFile] = None,):
    """
    endpoint expects paramaters encoded as multipart form 

    parameters
    ----------
    node_create: str
        string JSON with NodeCreate schema
    piece_id: str
        neo4j's elementid() property of piece node
    images: list[UploadFile]
        images that will attach to the component node
    """
    attach_files_subnode_to_node(node_create, images)
    attach_files_subnode_to_node(node_create, interventions, subnode_label='intervencion', prefix='intervenciones/')
    with db.Tx() as tx:
        result = db.create_update_component(piece_id, node_create.id, node_create.connected_nodes, node_create.properties, tx=tx)
        #print(result)
        log = request_to_log(request, user, node_create, piece_id)
        logdb = db.create_log(log, tx=tx)
    return result

@app.delete("/pieces/", dependencies=[Depends(get_write_permission_user)])
async def delete_piece(node_id: str):
    files_to_delete = db.detete_piece(node_id)
    for image in files_to_delete:
        filename = image["filename"]
        if (filename):
            # print(filename)
            try:
                path = os.path.join(UPLOAD_DIR, filename)
                os.remove(path)
            except OSError:
                pass
                # return HTTPException(status_code=404, detail=f"image to delete was not found")
    return 

@app.post("/upload-image/", dependencies=[Depends(get_write_permission_user)])
async def upload_image(files: List[UploadFile] = File(...)):
    # Save the uploaded file to the server's local file system
    result: list[SubNode] = []
    try:
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            upload_file(file, file_path)
            file_properties = {"size" : file.size}
            result.append(SubNode(node_id= file_path, properties=file_properties, relation_label="has_image", node_label="image"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

    return result

@app.get("/get-image/", dependencies=[Depends(get_read_permission_user)])
def get_image(image_url: Annotated[str, Query()]):
    image_url = os.path.join(UPLOAD_DIR, image_url)
    image_path = Path(image_url)
    print(image_path)
    if not image_path.is_file():
        return HTTPException(status_code=404, detail=f"image not found")
    return FileResponse(image_path)

@app.patch("/update-piece/", dependencies=[Depends(get_write_permission_user)])
async def update_piece(request: Request, 
                       node_create: Annotated[PieceCreate, Body(...)], 
                       user: Annotated[UserInDB, Depends(get_current_user)], 
                       images: Annotated[list[UploadFile], File()] = None,
                       component_images: Annotated[list[UploadFile], File()] = []):
    async with asyncio.TaskGroup() as tg:
        delete_images(node_create, tg)
        for component in node_create.components:
            delete_images(component, tg)
    
    return add_piece(request, node_create, user, images, component_images)

@app.delete("/images/", dependencies=[Depends(get_write_permission_user)])
async def delete_image(request: Request, user: Annotated[UserInDB, Depends(get_current_user)], filename: str, piece_id: str):
    try:
        path = os.path.join(UPLOAD_DIR, filename)
        print(path)
        with db.Tx() as tx:
            db.delete_image_by_filename(filename, tx=tx)
            log = Log(username=user.username, endpoint=request.url.path, request_method=request.method, node_elementid=piece_id)
            logdb = db.create_log(log, tx=tx)
        os.remove(path)
        return logdb
    except OSError:
        return HTTPException(status_code=404, detail=f"image to delete was not found")

@app.post("/csv/", dependencies=[Depends(get_read_permission_user)])
def get_filtered_data_csv(query_filters: dict[NodeLabel, list[Filter]]):
    data, _ = db.get_pieces_with_components_paginated_filtered(query_filters, 0, -1)
    df = pd.json_normalize(data, sep=".")
    # # Set order in which excel df columns will be presented
    # desired_order = []
    # for col in desired_order:
    #     if col not in df.columns:
    #         df[col] = np.nan  # Add missing columns with NaN values

    # # Rearrange the DataFrame columns to match the desired order
    # df = df[desired_order].rename()

    #print(df)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        df.to_excel(writer, index=False)
        
    response = StreamingResponse(iter([buffer.getvalue()]),
                                 media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
    response.headers["Content-Disposition"] = "attachment; filename=export.xlsx"
    return response

@app.put("/exposicion/", dependencies=[Depends(get_write_permission_user)])
def add_exposicion(piezas_element_ids: Annotated[list[str], Body(...)],
                   properties: Annotated[dict[str, Any], Body(...)]):
    id_label_list = [(id, "pieza") for id in piezas_element_ids]
    return db.create_node_and_connect_nodes_to_self("exposicion", id_label_list, **properties)
