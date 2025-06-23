import os
import json
import numpy as np
import faiss
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings

from celery import Celery
from .config import settings

# Crear la instancia de la aplicación Celery
celery_app = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# --- NUEVA TAREA PARA PROCESAR E INDEXAR DOCUMENTOS ---
@celery_app.task(name="process_and_index_documents_task")
def process_and_index_documents(bot_id: int, file_path: str):
    """
    Tarea de Celery que lee un documento de texto, lo procesa y crea
    un índice vectorial FAISS específico para un bot.
    """
    print(f"Iniciando procesamiento de documentos para el bot_id: {bot_id} desde el archivo: {file_path}")

    try:
        # --- 1. Leer y Dividir el Documento ---
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        print(f"Documento dividido en {len(chunks)} chunks.")

        # --- 2. Crear los Embeddings ---
        embeddings_generator = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        embeddings = embeddings_generator.embed_documents(chunks)
        print("Embeddings creados exitosamente.")

        # --- 3. Crear y Guardar el Índice FAISS ---
        # La ruta ahora es dinámica basada en el bot_id
        vector_db_path = f"data/vector_db/{bot_id}"
        os.makedirs(vector_db_path, exist_ok=True)

        faiss_index = faiss.IndexFlatL2(len(embeddings[0]))
        faiss_index.add(np.array(embeddings, dtype=np.float32))
        
        index_file = os.path.join(vector_db_path, "index.faiss")
        faiss.write_index(faiss_index, index_file)
        print(f"Índice FAISS guardado en: {index_file}")

        # --- 4. Guardar el Mapeo de Chunks ---
        chunks_map = {i: chunk for i, chunk in enumerate(chunks)}
        map_file = os.path.join(vector_db_path, "chunks_map.json")
        with open(map_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_map, f, ensure_ascii=False, indent=4)
        print(f"Mapa de chunks guardado en: {map_file}")
        
        # Limpiar el archivo temporal subido
        os.remove(file_path)
        print(f"Archivo temporal {file_path} eliminado.")

        return {"status": "success", "bot_id": bot_id, "chunks_indexed": len(chunks)}

    except Exception as e:
        print(f"ERROR durante la indexación para el bot {bot_id}: {e}")
        # En un sistema real, aquí se podría reintentar la tarea o notificar el error.
        return {"status": "error", "bot_id": bot_id, "error": str(e)}

