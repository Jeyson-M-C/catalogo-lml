from pydantic import BaseModel, HttpUrl
from typing import Optional
from pydantic import constr

class Categoria(BaseModel):
    nombre: constr(min_length=3, max_length=100)  # Validar longitud del nombre

class Enlace(BaseModel):
    titulo: constr(min_length=3, max_length=200)  # Validar longitud del título
    url: HttpUrl  # Usa HttpUrl para validar que sea una URL válida
    descripcion: Optional[constr(max_length=500)] = None  # Validar longitud de la descripción
    categoria_id: str

class Subenlace(BaseModel):
    titulo: constr(min_length=3, max_length=200)
    url: HttpUrl
    descripcion: Optional[constr(max_length=500)] = None
    enlace_id: str

class User(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: str
