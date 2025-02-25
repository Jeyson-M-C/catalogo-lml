# routers/usuarios.py

from fastapi import APIRouter, HTTPException
from models import User
from passlib.context import CryptContext
import os
from config import db
from dotenv import load_dotenv

router = APIRouter()

# Configura un contexto de hash (si no lo tienes ya configurado globalmente)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEFAULT_SUPERADMIN_USERNAME = "admin"
DEFAULT_SUPERADMIN_PASSWORD = os.getenv("PASS_ADMIN")

async def crear_superadmin_por_defecto(db):
    # Verificar si ya existe un superadmin por defecto
    existing_user = await db["usuarios"].find_one({
        "username": DEFAULT_SUPERADMIN_USERNAME,
        "is_default_admin": True
    })
    
    if not existing_user:
        # Crear superadmin por defecto
        hashed_password = pwd_context.hash(DEFAULT_SUPERADMIN_PASSWORD)
        
        await db["usuarios"].insert_one({
            "username": DEFAULT_SUPERADMIN_USERNAME,
            "password": hashed_password,
            "is_admin": True,
            "is_default_admin": True,  # Marca como admin por defecto
            "is_deletable": False      # Marca como no borrable
        })
        print("Superadmin por defecto creado exitosamente")
    else:
        print("Superadmin por defecto ya existe")


@router.on_event("startup")
async def startup_event():
    # Crear superadmin por defecto al iniciar la aplicación (Nota: Esto debe estar en main.py realmente)
    await crear_superadmin_por_defecto(db)


@router.post("/superadmin/")
async def crear_superadministrador(user: User):
    existing_user = await db["usuarios"].find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    # Hashear la contraseña usando bcrypt
    hashed_password = pwd_context.hash(user.password)
    
    await db["usuarios"].insert_one({
        "username": user.username, 
        "password": hashed_password,
        "is_admin": True 
    })
    
    return {"mensaje": "Superadministrador creado con éxito"}

# Función para verificar contraseña (ya está implementada dentro del login)

@router.post("/login")
async def login(user: User) -> dict:
    # Buscar el usuario en la base de datos
    usuario = await db["usuarios"].find_one({"username": user.username})
    
    # Verificar si el usuario existe y la contraseña es correcta
    if not usuario or not pwd_context.verify(user.password, usuario['password']):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Determinar si el usuario es un superadmin o admin normalmente.
    is_admin = usuario.get('is_admin', False)
    
    return {
          'usuario':user.username ,
          'is-admin': is_admin ,
    }

# Endpoint para prevenir la eliminación del superadmin por defecto
@router.delete("/{username}")
async def eliminar_usuario(username: str):
    # Verificar si es el admin por defecto
    usuario = await db["usuarios"].find_one({"username": username})
    
    if usuario and usuario.get('is_default_admin', False):
        raise HTTPException(
            status_code=403, 
            detail="No se puede eliminar el superadmin por defecto"
        )
    
    # Lógica normal de eliminación de usuario
    result = await db["usuarios"].delete_one({"username": username})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {"mensaje": "Usuario eliminado exitosamente"}
