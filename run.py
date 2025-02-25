import os
import uvicorn

if __name__ == "__main__":
    # Detecta si estás en un entorno de desarrollo local
    DEBUG = bool(os.getenv("DEBUG", False))  # Usa una variable de entorno para controlar el modo debug

    host = "localhost" if DEBUG else "0.0.0.0"
    port = int(os.getenv("PORT", 8000))

    print(f"Running on host: {host} and port: {port}")

    uvicorn.run("main:app", host=host, port=port, reload=DEBUG)
