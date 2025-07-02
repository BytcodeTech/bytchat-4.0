# app/worker.py

import os
import shutil
from sqlalchemy.orm import Session
from celery import Celery

# Importaciones de tu proyecto
from . import crud, models, database
from .config import settings

# Nuevos imports para el procesamiento de documentos (LangChain)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.text import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# --- Configuración de Celery ---
celery_app = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# --- Configuración del Modelo de Embeddings ---
# Asegúrate de que GOOGLE_API_KEY está en tu archivo .env
if not settings.GOOGLE_API_KEY:
    raise ValueError("La GOOGLE_API_KEY no se encontró en las variables de entorno.")
# Inicializamos el modelo de embeddings una sola vez para reutilizarlo.
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


def get_db_session():
    """
    Función de ayuda para crear una sesión de base de datos
    independiente para cada tarea de Celery.
    """
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- TAREA ÚNICA Y MEJORADA ---
@celery_app.task(name="process_document_task")
def process_document_task(bot_id: int, file_path: str, doc_id: int):
    """
    Tarea de Celery para procesar un documento: lo carga, divide, vectoriza
    y guarda su índice FAISS, actualizando el estado en la BD.
    """
    # Obtenemos una sesión de BD para esta tarea específica
    db: Session = next(get_db_session())

    try:
        print(f"✅ Iniciando procesamiento para doc_id: {doc_id} en el bot_id: {bot_id}")

        # 1. Actualizar estado del documento a "procesando"
        crud.update_document_status(db, doc_id=doc_id, status=models.DocumentStatus.PROCESSING)

        # 2. Cargar el documento (PDF o Texto)
        file_extension = os.path.splitext(file_path)[1].lower()
        loader = PyPDFLoader(file_path) if file_extension == '.pdf' else TextLoader(file_path, encoding='utf-8')
        documents = loader.load()

        # 3. Dividir el documento en trozos (chunks)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        docs = text_splitter.split_documents(documents)
        print(f"📄 Documento dividido en {len(docs)} chunks.")

        # 4. Crear el índice de vectores FAISS usando el modelo de embeddings
        vector_store = FAISS.from_documents(docs, embeddings_model)

        # 5. Guardar el índice en el disco
        storage_path = f"storage/bot_{bot_id}"
        os.makedirs(storage_path, exist_ok=True)
        index_path = os.path.join(storage_path, f"doc_{doc_id}.faiss")
        vector_store.save_local(index_path)
        print(f"💾 Índice FAISS guardado en: {index_path}")

        # 6. Actualizar el registro en la BD con la ruta del índice y marcar como "completado"
        db_doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
        if db_doc:
            db_doc.vector_index_path = index_path
            db_doc.status = models.DocumentStatus.COMPLETED
            db.commit()
        
        print(f"🎉 Procesamiento completado con éxito para doc_id: {doc_id}.")

    except Exception as e:
        # Si algo sale mal, se marca como "fallido"
        print(f"❌ ERROR: Falló el procesamiento del doc_id {doc_id}. Error: {e}")
        crud.update_document_status(db, doc_id=doc_id, status=models.DocumentStatus.FAILED)
    
    finally:
        # Limpiar el archivo temporal, independientemente del resultado
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Archivo temporal eliminado: {file_path}")