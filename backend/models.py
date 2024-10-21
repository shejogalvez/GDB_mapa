from pydantic import BaseModel, model_validator, Field
from typing import Annotated, Optional, Any, Literal, List
from fastapi import UploadFile, File, Query
from enum import Enum
from dataclasses import dataclass

import json

#NodeLabel: labels de nodos válidos para hacer match al momento de hacer queries
NodeLabel = Literal["pieza", "pais", "localidad", "exposicion", "cultura", "imagen", "componente", "forma", "ubicacion"]

class SubNode(BaseModel):
    node_id: str
    properties: dict[str, Any]
    relation_label: Optional[str]
    node_label: Optional[NodeLabel]
    id_key: str = 'id'
    method: Literal['DELETE', 'UPDATE', 'CREATE'] = 'UPDATE'

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
    node_elementid: str

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

# Operation: keywords que representan operacionaes para comparar campos al filtrar
Operation = Literal['=', '>=', '<', '<=', '>', 'contains']

class Filter(BaseModel):
    key: str 
    operation: Operation
    val: Any
class QueryFilter(BaseModel):
    label: Optional[str] = None
    filters: list[Filter]