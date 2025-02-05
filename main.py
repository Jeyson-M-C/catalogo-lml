# backend/main.py
from fastapi import FastAPI, APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi.encoders import jsonable_encoder
from config import db
from models import Categoria, Enlace, User
from passlib.context import CryptContext
from typing import Dict
from bson import ObjectId

app = FastAPI()

origins = [
    "http://localhost:3000",  # URL del frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Configura un contexto de hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración del superadmin por defecto
DEFAULT_SUPERADMIN_USERNAME = "admin"
DEFAULT_SUPERADMIN_PASSWORD = os.getenv("DEFAULT_SUPERADMIN_PASSWORD", "admin/$123$/77/ADMIN")

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

# Modificar tu endpoint de login para manejar el admin por defecto
@app.post("/login")
async def login(user: User) -> Dict[str, bool]:
    # Buscar el usuario en la base de datos
    usuario = await db["usuarios"].find_one({"username": user.username})
    
    # Verificar si el usuario existe y la contraseña es correcta
    if not usuario or not pwd_context.verify(user.password, usuario['password']):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Determinar si el usuario es un superadmin
    is_admin = usuario.get('is_admin', False)
    is_default_admin = usuario.get('is_default_admin', False)
    
    return {
        "is_admin": is_admin,
        "is_default_admin": is_default_admin
    }

# Endpoint para prevenir la eliminación del superadmin por defecto
@app.delete("/usuarios/{username}")
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

# En tu función de inicio de la aplicación o configuración
@app.on_event("startup")
async def startup_event():
    # Crear superadmin por defecto al iniciar la aplicación
    await crear_superadmin_por_defecto(db)


@app.post("/superadmin/")
async def crear_superadmin(user: User):
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

# Función para verificar contraseña
async def verificar_password(username: str, password_ingresada: str) -> bool:
    user = await db["usuarios"].find_one({"username": username})
    if not user:
        return False
    
    # Verifica la contraseña
    return pwd_context.verify(password_ingresada, user['password'])


# Rutas de categorías
@app.post("/categorias/")
async def crear_categoria(categoria: Categoria):
    result = await db["categorias"].insert_one(categoria.dict())
    return {"mensaje": "Categoría creada con éxito"}
    
@app.put("/categorias/{categoria_id}")
async def actualizar_categoria(categoria_id: str, categoria: Categoria):
    try:
        # Verificar que el ID sea válido
        if not ObjectId.is_valid(categoria_id):
            raise HTTPException(status_code=400, detail="ID de categoría inválido")

        categoria_id_obj = ObjectId(categoria_id)

        # Filtrar solo los campos proporcionados
        update_data = {k: v for k, v in categoria.dict().items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")

        result = await db["categorias"].update_one(
            {"_id": categoria_id_obj},
            {"$set": update_data}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Categoría no encontrada o sin cambios")

        categoria_actualizada = await db["categorias"].find_one({"_id": categoria_id_obj})

        return {
            "mensaje": "Categoría actualizada exitosamente",
            "categoria": {
                "_id": str(categoria_actualizada["_id"]),
                "nombre": categoria_actualizada["nombre"]
            }
        }

    except Exception as e:
        print(f"Error al actualizar categoría: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/categorias/")
async def leer_categorias():
    categorias = await db["categorias"].find().to_list(1000)
    return jsonable_encoder([{**categoria, "_id": str(categoria["_id"]), "nombre": categoria["nombre"]} for categoria in categorias])

# Rutas de enlaces
@app.post("/enlaces/")
async def crear_enlace(enlace: Enlace):
    try:
        # Validar que categoria_id es un ObjectId válido
        if not ObjectId.is_valid(enlace.categoria_id):
            raise HTTPException(status_code=400, detail="ID de categoría inválido")

        categoria_id = ObjectId(enlace.categoria_id)  # Convertir a ObjectId

        # Buscar la categoría en la base de datos
        categoria = await db["categorias"].find_one({"_id": categoria_id})
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        # Crear el nuevo enlace
        nuevo_enlace = {
            "titulo": enlace.titulo,
            "url": enlace.url,
            "descripcion": enlace.descripcion,
            "categoria_id": categoria_id,  # Guardar como ObjectId
        }

        # Insertar en la base de datos
        result = await db["enlaces"].insert_one(nuevo_enlace)

        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="No se pudo crear el enlace")

        return {"mensaje": "Enlace creado exitosamente", "_id": str(result.inserted_id)}

    except Exception as e:
        print(f"Error al crear enlace: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/enlaces/")
async def leer_enlaces():
    enlaces = await db["enlaces"].find().to_list(1000)
    
    # Obtener todas las categorías y mapearlas {id: nombre}
    categorias = await db["categorias"].find().to_list(1000)
    categorias_dict = {str(cat["_id"]): cat["nombre"] for cat in categorias}

    # Agregar el nombre de la categoría a cada enlace
    enlaces_con_categoria = []
    for enlace in enlaces:
        enlaces_con_categoria.append({
            **enlace,
            "_id": str(enlace["_id"]),
            "categoria_id": str(enlace["categoria_id"]),
            "categoria_nombre": categorias_dict.get(str(enlace["categoria_id"]), "Sin categoría")
        })

    return jsonable_encoder(enlaces_con_categoria)

@app.put("/enlaces/{enlace_id}")
async def actualizar_enlace(enlace_id: str, enlace: Enlace):
    try:
        # Verificar que el ID sea válido
        if not ObjectId.is_valid(enlace_id):
            raise HTTPException(status_code=400, detail="ID de enlace inválido")

        # Convertir el ID a ObjectId
        enlace_id = ObjectId(enlace_id)

        # Preparar los datos para actualizar (solo campos proporcionados)
        update_data = {k: v for k, v in enlace.dict().items() if v is not None}

        # Verificar si la categoría existe si se proporciona
        if "categoria_id" in update_data:
            if not ObjectId.is_valid(update_data["categoria_id"]):
                raise HTTPException(status_code=400, detail="ID de categoría inválido")

            categoria = await db["categorias"].find_one({"_id": ObjectId(update_data["categoria_id"])})
            if not categoria:
                raise HTTPException(status_code=400, detail="Categoría no encontrada")

        # Actualizar el enlace
        result = await db["enlaces"].update_one(
            {"_id": enlace_id},
            {"$set": update_data}
        )

        # Verificar si se modificó
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Enlace no encontrado o sin cambios")

        # Obtener el enlace actualizado
        enlace_actualizado = await db["enlaces"].find_one({"_id": enlace_id})

        return {
            "mensaje": "Enlace actualizado exitosamente",
            "enlace": {
                "_id": str(enlace_actualizado["_id"]),
                "titulo": enlace_actualizado["titulo"],
                "url": enlace_actualizado["url"],
                "descripcion": enlace_actualizado["descripcion"],
                "categoria_id": str(enlace_actualizado["categoria_id"])
            }
        }

    except Exception as e:
        print(f"Error al actualizar enlace: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.get("/enlaces-por-categoria/{categoria_id}")
async def leer_enlaces_por_categoria(categoria_id: str):
    if not ObjectId.is_valid(categoria_id):
        raise HTTPException(status_code=400, detail="ID de categoría inválido")
    
    categoria_obj_id = ObjectId(categoria_id)

    # Busca enlaces con la categoría correcta
    enlaces = await db["enlaces"].find({"categoria_id": str(categoria_obj_id)}).to_list(1000)

    return {
        "enlaces": [
            {
                "_id": str(enlace["_id"]),
                "titulo": enlace["titulo"],
                "url": enlace["url"],
                "descripcion": enlace.get("descripcion", "")
            }
            for enlace in enlaces
        ]
    }