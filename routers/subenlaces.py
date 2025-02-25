from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from models import Subenlace
from pydantic import HttpUrl,ValidationError
from config import db
from pydantic import constr

router = APIRouter()


@router.post("/", response_description="Crear un nuevo subenlace")
async def crear_subenlace(subenlace: Subenlace):
    try:
        # Validar que el enlace_id sea un ObjectId válido
        if not ObjectId.is_valid(subenlace.enlace_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de enlace inválido"
            )

        # Buscar el enlace en la base de datos
        enlace = await db["enlaces"].find_one({"_id": ObjectId(subenlace.enlace_id)})
        if not enlace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enlace no encontrado"
            )

        # Verificar si el título ya existe (insensible a mayúsculas)
        existing_subenlace = await db["subenlaces"].find_one({
            "titulo": {"$regex": f"^{subenlace.titulo}$", "$options": "i"}
        })
        
        # Si existe y no es el mismo subenlace que se está editando, lanzar error
        if existing_subenlace:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El título del subenlace ya está registrado."
            )

        # Crear el nuevo subenlace
        nuevo_subenlace = {
            "titulo": subenlace.titulo,
            "url": str(subenlace.url),  # Convertir a string
            "descripcion": subenlace.descripcion,
            "enlace_id": ObjectId(subenlace.enlace_id)  # Relacionar con el enlace
        }

        # Insertar el subenlace en la base de datos
        result = await db["subenlaces"].insert_one(nuevo_subenlace)

        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo crear el subenlace"
            )

        return {"mensaje": "Subenlace creado exitosamente", "_id": str(result.inserted_id)}

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error al crear subenlace: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.get("/{enlace_id}", response_description="Obtener subenlaces por enlace_id")
async def leer_subenlaces_por_enlace(enlace_id: str):
    try:
        if not ObjectId.is_valid(enlace_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de enlace inválido"
            )
        
        enlace_obj_id = ObjectId(enlace_id)
        
        # Busca subenlaces con el enlace correcto
        subenlaces = await db["subenlaces"].find({"enlace_id": enlace_obj_id}).to_list(1000)

        # Devuelve los subenlaces encontrados
        return {
            "subenlaces": [
                {
                    "_id": str(subenlace["_id"]),
                    "titulo": subenlace["titulo"],
                    "url": subenlace["url"],
                    "descripcion": subenlace.get("descripcion", "")
                }
                for subenlace in subenlaces
            ]
        }
    except Exception as e:
        print(f"Error al obtener subenlaces: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.put("/{subenlace_id}", response_description="Actualizar un subenlace")
async def actualizar_subenlace(subenlace_id: str, subenlace: Subenlace):
    try:
        # Validar que el subenlace_id sea un ObjectId válido
        if not ObjectId.is_valid(subenlace_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de subenlace inválido"
            )

        # Validar que el enlace_id sea un ObjectId válido
        if not ObjectId.is_valid(subenlace.enlace_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de enlace inválido"
            )

        subenlace_id_obj = ObjectId(subenlace_id)
        enlace_id_obj = ObjectId(subenlace.enlace_id)

        # Verificar si el enlace existe
        enlace = await db["enlaces"].find_one({"_id": enlace_id_obj})
        if not enlace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enlace no encontrado"
            )

        # Obtener el subenlace actual para comparar
        subenlace_actual = await db["subenlaces"].find_one({"_id": subenlace_id_obj})
        if not subenlace_actual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subenlace no encontrado"
            )

        # Preparar los datos para actualizar
        update_data = {
            "url": str(subenlace.url),  # Convertir a string
            "descripcion": subenlace.descripcion,
            "enlace_id": enlace_id_obj  # Relacionar con el enlace
        }

        # Solo verificar y actualizar el título si ha cambiado
        if subenlace.titulo != subenlace_actual["titulo"]:
            existing_subenlace = await db["subenlaces"].find_one({
                "titulo": {"$regex": f"^{subenlace.titulo}$", "$options": "i"},
                "enlace_id": enlace_id_obj,  # Limitar a este enlace
                "_id": {"$ne": subenlace_id_obj}  # Excluir el propio subenlace actual
            })
            if existing_subenlace:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El título del subenlace ya está registrado."
                )
            update_data["titulo"] = subenlace.titulo  # Solo agregar si ha cambiado

        # Actualizar el subenlace en la base de datos
        result = await db["subenlaces"].update_one(
            {"_id": subenlace_id_obj},
            {"$set": update_data}
        )
        
        # Obtener el subunelace actualizado para devolverlo
        subunelace_actualizado = await db["subenlaces"].find_one({"_id": subenlace_id_obj})

        return {
            "mensaje": "Subunelace actualizado exitosamente",
            "subunelace": {
                "_id": str(subunelace_actualizado["_id"]),
                "titulo": subunelace_actualizado["titulo"],
                "url": subunelace_actualizado["url"],
                "descripcion": subunelace_actualizado["descripcion"],
                "enlace_id": str(subunelace_actualizado["enlace_id"])
            }
        }

    except Exception as e:
        print(f"Error al actualizar subunelace: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.delete("/{subenlace_id}", response_description="Eliminar un subenlace")
async def eliminar_subenlace(subenlace_id: str):
    try:
        # Validar que el subenlace_id sea un ObjectId válido
        if not ObjectId.is_valid(subenlace_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de subenlace inválido"
            )

        subenlace_id_obj = ObjectId(subenlace_id)

        # Eliminar el subenlace de la base de datos
        result = await db["subenlaces"].delete_one({"_id": subenlace_id_obj})

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subenlace no encontrado"
            )

        return {"mensaje": "Subenlace eliminado exitosamente"}

    except Exception as e:
        print(f"Error al eliminar subenlace: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )
