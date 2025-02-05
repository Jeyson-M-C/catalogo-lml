
import os
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "¡Hola desde Render!"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Usa el puerto de la variable de entorno o 8000 por defecto
    uvicorn.run("main:app", host="0.0.0.0", port=port)