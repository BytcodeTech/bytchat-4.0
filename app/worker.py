from celery import Celery
from .config import settings
import time

# Crear la instancia de la aplicación Celery
# El primer argumento es el nombre del módulo actual.
# El 'broker' es la URL de nuestro servicio Redis, que leemos desde la configuración.
celery_app = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Definimos una tarea de ejemplo para probar que todo funciona
@celery_app.task
def example_task(x, y):
    time.sleep(5)  # Simula una tarea larga
    return x + y

# En un futuro, aquí moveríamos la lógica de 'indexer.py'
# a una tarea como esta:
#
# @celery_app.task
# def process_training_documents(bot_id: int, file_paths: list):
#     print(f"Iniciando entrenamiento para el bot {bot_id}...")
#     # ... aquí iría toda la lógica de indexer.py ...
#     print("Entrenamiento completado.")
#     return {"status": "success", "bot_id": bot_id}