from pydantic import BaseModel, model_validator, Field
from typing import Annotated, Optional, Any, Literal, List
from fastapi import UploadFile, File, Query
from enum import Enum
from dataclasses import dataclass

import json

#NodeLabel: labels de nodos válidos para hacer match al momento de hacer queries
NodeLabel = Literal["pieza", "pais", "localidad", "exposicion", "cultura", "imagen", "componente", "forma", "ubicacion"]

# NODES_RELATIONS: diccionario para asignar labels de relaciones entre tipos de nodo
NODES_RELATIONS: dict[tuple[NodeLabel, NodeLabel], str] = {
    ('pieza', 'pais'): 'de_pais',
    ('pieza', 'cultura'): 'de_cultura',
    ('pieza', 'localidad'): 'de_localidad',
    ('pieza', 'componente'): 'compuesto_por',
    ('pieza', 'exposicion'): 'expuesta_en',
    ('pieza', 'imagen'): 'tiene_imagen',
    ('componente', 'imagen'): 'tiene_imagen',
    ('componente', 'forma'): 'tiene_forma',
    ('componente', 'ubicacion'): 'ubicacion_componente',
    ('ubicacion', 'ubicacion'): 'ubicacion_contiene',
}

class SubNode(BaseModel):
    """Represents a node that is connected to a main node when creating/updating the main node, subnodes are represented by 
    {node_id} which is the property with label {id_key}, depending on the method the action will be determinded:
        - CREATE: Creates connection between subnode and main node, creates subnode if node_id noesn't exists and sets {properties}
        - UPDATE: The same as CREATE but deletes all other connections that matches (main node) -> (:{node_label})
        - DELETE: Deletes subnode if exists
        - DETACH: Deletes conection with subnode if exists"""
    node_id: Optional[str] = None 
    properties: Optional[dict[str, Any]] = None
    #relation_label: Optional[str] = None
    node_label: Optional[NodeLabel] = None
    id_key: Optional[str] = None
    method: Literal['DELETE', 'UPDATE', 'CREATE', 'DETACH'] = 'UPDATE'

class NodeCreate(BaseModel):
    id: Optional[str] = None
    properties: Optional[dict[str, Any]] = None # Properties to update on the main node
    connected_nodes: list[SubNode]  # Each connected node and its properties
    
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


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

class UserForm(User):
    password: str

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