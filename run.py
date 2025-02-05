
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Usa el puerto de la variable de entorno o 8000 por defecto
    uvicorn.run("main:app", host="0.0.0.0", port=port)