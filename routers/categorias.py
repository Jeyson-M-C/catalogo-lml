from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import List
from fastapi.encoders import jsonable_encoder
from models import Categoria
from pydantic import ValidationError
from config import db
from fastapi import status


router = APIRouter()


@router.post("/", response_description="Crear una nueva categoría")
async def crear_categoria(categoria: Categoria):
    try:
        # Verificar si la categoría ya existe (insensible a mayúsculas)
        existing_categoria = await db["categorias"].find_one({
            "nombre": {"$regex": f"^{categoria.nombre}$", "$options": "i"}
        })
        
        if existing_categoria:
            raise HTTPException(
                status_code=400,
                detail="El nombre de la categoría ya está registrado."
            )

        # Insertar la nueva categoría en la base de datos
        result = await db["categorias"].insert_one(categoria.dict())
        
        return {"mensaje": "Categoría creada con éxito"}
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error al crear categoría: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.put("/{categoria_id}", response_description="Actualizar una categoría")
async def actualizar_categoria(categoria_id: str, categoria: Categoria):
    try:
        if not ObjectId.is_valid(categoria_id):
            raise HTTPException(status_code=400, detail="ID de categoría inválido")

        categoria_id_obj = ObjectId(categoria_id)
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

@router.get("/", response_description="Listar todas las categorías")
async def leer_categorias():
    categorias = await db["categorias"].find().to_list(1000)
    return jsonable_encoder([{**categoria, "_id": str(categoria["_id"]), "nombre": categoria["nombre"]} for categoria in categorias])

@router.delete("/{categoria_id}", response_description="Eliminar una categoría")
async def eliminar_categoria(categoria_id: str):
    try:
        if not ObjectId.is_valid(categoria_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de categoría inválido"
            )

        result = await db["categorias"].delete_one({"_id": ObjectId(categoria_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        return {"mensaje": "Categoría eliminada exitosamente"}

    except Exception as e:
        print(f"Error al eliminar categoría: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

