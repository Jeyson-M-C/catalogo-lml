from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import List
from fastapi.encoders import jsonable_encoder
from models import Enlace
from pydantic import HttpUrl,ValidationError
from config import db
from fastapi import status

router = APIRouter()

@router.post("/", response_description="Crear un nuevo enlace")
async def crear_enlace(enlace: Enlace):
    try:
        # Verificar si el ID de categoría es válido
        if not ObjectId.is_valid(enlace.categoria_id):
            raise HTTPException(status_code=400, detail="ID de categoría inválido")

        categoria_id = ObjectId(enlace.categoria_id)
        
        # Comprobar si la categoría existe
        if not await db["categorias"].find_one({"_id": categoria_id}):
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        # Verificar si el título ya está registrado (insensible a mayúsculas)
        existing_enlace = await db["enlaces"].find_one({"titulo": {"$regex": f"^{enlace.titulo}$", "$options": "i"}})
        if existing_enlace:
            raise HTTPException(status_code=400, detail="El título del enlace ya está registrado.")

        # Validar la URL
        try:
            # Esto lanzará un error si la URL no es válida
            valid_url = HttpUrl(enlace.url)
        except ValidationError:
            raise HTTPException(status_code=400, detail="La URL proporcionada no es válida.")

        # Crear el nuevo enlace
        nuevo_enlace = {
            "titulo": enlace.titulo,
            "url": str(valid_url),  # Convertir a string
            "descripcion": enlace.descripcion,
            "categoria_id": categoria_id,
        }
        
        result = await db["enlaces"].insert_one(nuevo_enlace)
        
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="No se pudo crear el enlace")

        return {"mensaje": "Enlace creado exitosamente", "_id": str(result.inserted_id)}

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error al crear enlace: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/", response_description="Listar todos los enlaces")
async def leer_enlaces():
    enlaces = await db["enlaces"].find().to_list(1000)
    categorias = await db["categorias"].find().to_list(1000)
    categorias_dict = {str(cat["_id"]): cat["nombre"] for cat in categorias}
    enlaces_con_categoria = []
    for enlace in enlaces:
        enlaces_con_categoria.append({
            **enlace,
            "_id": str(enlace["_id"]),
            "categoria_id": str(enlace["categoria_id"]),
            "categoria_nombre": categorias_dict.get(str(enlace["categoria_id"]), "Sin categoría")
        })
    return jsonable_encoder(enlaces_con_categoria)

@router.put("/{enlace_id}", response_description="Actualizar un enlace")
async def actualizar_enlace(enlace_id: str, enlace: Enlace):
    try:
        if not ObjectId.is_valid(enlace_id):
            raise HTTPException(status_code=400, detail="ID de enlace inválido")
        
        enlace_id = ObjectId(enlace_id)
        
        # Obtener el enlace actual para comparar
        enlace_actual = await db["enlaces"].find_one({"_id": enlace_id})
        if not enlace_actual:
            raise HTTPException(status_code=404, detail="Enlace no encontrado")

        # Crear un diccionario con los datos a actualizar
        update_data = {k: v for k, v in enlace.dict().items() if v is not None}

        # Verificar si se cambió el título y si ya existe otro enlace con ese título
        if "titulo" in update_data and update_data["titulo"] != enlace_actual["titulo"]:
            existing_enlace = await db["enlaces"].find_one({
                "titulo": {"$regex": f"^{update_data['titulo']}$", "$options": "i"},
                "_id": {"$ne": enlace_id}  # Excluir el propio enlace actual
            })
            if existing_enlace:
                raise HTTPException(status_code=400, detail="El título del enlace ya está registrado.")

        # Verificar la categoría si se ha actualizado
        if "categoria_id" in update_data:
            if not ObjectId.is_valid(update_data["categoria_id"]):
                raise HTTPException(status_code=400, detail="ID de categoría inválido")
            categoria = await db["categorias"].find_one({"_id": ObjectId(update_data["categoria_id"])})
            if not categoria:
                raise HTTPException(status_code=400, detail="Categoría no encontrada")

        # Convertir categoria_id a ObjectId
            update_data["categoria_id"] = ObjectId(update_data["categoria_id"])
            
            categoria = await db["categorias"].find_one({"_id": update_data["categoria_id"]})
            if not categoria:
                raise HTTPException(status_code=400, detail="Categoría no encontrada")

        # Convertir HttpUrl a string antes de actualizar
        if "url" in update_data:
            update_data["url"] = str(update_data["url"])

        # Actualizar el enlace
        result = await db["enlaces"].update_one({"_id": enlace_id}, {"$set": update_data})
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Enlace no encontrado o sin cambios")

        # Obtener el enlace actualizado para devolverlo
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

@router.get("/enlaces-por-categoria/{categoria_id}", response_description="Obtener enlaces por categoría")
async def leer_enlaces_por_categoria(categoria_id: str):
    try:
        if not ObjectId.is_valid(categoria_id):
            raise HTTPException(status_code=400, detail="ID de categoría inválido")
        
        categoria_obj_id = ObjectId(categoria_id)

        # Busca enlaces con la categoría correcta
        enlaces = await db["enlaces"].find({"categoria_id": categoria_obj_id}).to_list(1000)
        
        return {"enlaces": [
            {
                "_id": str(enlace["_id"]),
                "titulo": enlace["titulo"],
                "url": enlace["url"],
                "descripcion": enlace.get("descripcion", "")
            }
            for enlace in enlaces
        ]}
    except Exception as e:
        print(f"Error al obtener enlaces por categoría: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")