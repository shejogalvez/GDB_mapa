from pydantic import BaseModel
from typing import Annotated, Optional
from fastapi import UploadFile, File

class SubNode(BaseModel):
    node_id: str
    properties: dict[str, str]
    relation_label: str
    node_label: str

class NodeCreate(BaseModel):
    id: Optional[str] = None
    properties: dict[str, str]  # Properties to update on the main node
    connected_nodes: list[SubNode]  # Each connected node and its properties
    image: Optional[UploadFile]

class NodeUpdate(NodeCreate):
    node_id: str

class PieceCreate(NodeCreate):
    components: list[NodeCreate]