# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from routers.categorias import router as categorias_router
from routers.enlaces import router as enlaces_router
from routers.subenlaces import router as subenlaces_router
from routers.usuarios import router as usuarios_router
from routers.noticias import router as noticias_router

app = FastAPI()

# Configurar CORS

origins = [
    "http://localhost:3000", # Para desarrollo
    "https://catalogo-lml.vercel.app" # Para producción
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(noticias_router, prefix="/noticias", tags=["noticias"])

app.include_router(usuarios_router, prefix="/usuarios", tags=["usuarios"])

app.include_router(categorias_router, prefix="/categorias", tags=["categorias"])

app.include_router(enlaces_router, prefix="/enlaces", tags=["enlaces"])

app.include_router(subenlaces_router, prefix="/subenlaces", tags=["subenlaces"])

@app.get("/")
def read_root():
    return {"message": "¡Catalogo lml!"}

