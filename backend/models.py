from pydantic import BaseModel, model_validator
from typing import Annotated, Optional
from fastapi import UploadFile, File
from enum import Enum

import json

class SubNode(BaseModel):
    node_id: str
    properties: dict[str, str | int | bool]
    relation_label: str
    node_label: str

class NodeCreate(BaseModel):
    id: Optional[str] = None
    properties: dict[str, str]  # Properties to update on the main node
    connected_nodes: list[SubNode]  # Each connected node and its properties
    
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

class NodeUpdate(NodeCreate):
    node_id: str

class PieceCreate(NodeCreate):
    components: list[NodeCreate]

class Log(BaseModel):
    username: str
    endpoint: str
    request_method: str
    request_body: str

class RoleEnum(Enum):
    reader = "reader"
    writer = "writer"
    admin = "admin"

class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: RoleEnum

class UserInDB(User):
    hashed_password: str
    salt: Optional[str] = "" #TODO: not optional