# backend/models.py
from pydantic import BaseModel
import uuid

class Categoria(BaseModel):
    id: str = uuid.uuid4().hex
    nombre: str

class Enlace(BaseModel):
    id: str = uuid.uuid4().hex
    titulo: str
    url: str
    descripcion: str
    categoria_id: str

class User(BaseModel):
    username: str
    password: str