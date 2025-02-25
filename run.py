import os
import uvicorn

# Configuración del entorno
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
HOST = "localhost" if DEBUG else "0.0.0.0"  # Ajusta el host según el entorno
PORT = int(os.getenv("PORT", "8000"))  # Asegura que el puerto sea un entero

# Imprimir la configuración
environment = "LOCAL" if DEBUG else "PRODUCCIÓN"
print(f"Corriendo en modo: {environment}")
print(f"Escuchando en host: {HOST}, puerto: {PORT}")

# Ejecutar Uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # Importante: usa el nombre del archivo y la instancia de la app
        host=HOST,
        port=PORT,
        reload=DEBUG,  # Activa la recarga automática solo en modo debug
        log_level="debug" if DEBUG else "info"  # Nivel de log según el entorno
    )
