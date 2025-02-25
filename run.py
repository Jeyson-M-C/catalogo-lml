import os
import uvicorn
import signal

class TimeoutError(Exception): 
    pass 

def input_with_timeout(prompt, timeout):
    def alarm_handler(signum, frame):
        raise TimeoutError

    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(timeout)

    try:
        return input(prompt)
    finally:
        signal.alarm(0)

def main():
    try:
        response = input_with_timeout("¿Deseas ejecutar en modo local? (1 para local, cualquier otra tecla para producción): ", 10)
        return response == "1"
    except TimeoutError:
        print("\nNo se recibió respuesta. Ejecutando en modo PRODUCCIÓN por defecto.")
        return False

# Pregunta al usuario por el entorno
if __name__ == "__main__":
    DEBUG = main()

    # Configuración del entorno
    HOST = "localhost" if DEBUG else "0.0.0.0"  # Ajusta el host según el entorno
    PORT = int(os.getenv("PORT", "8000"))  # Asegura que el puerto sea un entero

    # Imprimir la configuración
    environment = "LOCAL" if DEBUG else "PRODUCCIÓN"
    print(f"Corriendo en modo: {environment}")
    print(f"Escuchando en host: {HOST}, puerto: {PORT}")

    # Ejecutar Uvicorn
    uvicorn.run(
        "main:app",  # Importante: usa el nombre del archivo y la instancia de la app
        host=HOST,
        port=PORT,
        reload=DEBUG,  # Activa la recarga automática solo en modo debug
        log_level="debug" if DEBUG else "info"  # Nivel de log según el entorno
    )
