# app/core/rag_retriever.py

import os
import faiss
import numpy as np
import logging
from sqlalchemy.orm import Session
from typing import List

# Importaciones de tu proyecto y de LangChain
from app import crud, models
from app.config import settings # Corregido para apuntar a la ruta correcta
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

logging.basicConfig(level=logging.INFO)

# Inicializamos el modelo de embeddings una sola vez
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


class RAGRetriever:
    def __init__(self):
        """
        El Retriever ahora es dinámico: no carga un solo índice,
        sino que los busca y carga bajo demanda para cada bot.
        """
        logging.info("RAGRetriever (dinámico) inicializado.")

    def search(self, db: Session, bot_id: int, query: str, k: int = 5) -> List[str]:
        """
        Busca en todos los documentos de un bot para encontrar los chunks más relevantes.
        """
        # 1. Obtener todos los documentos con estado 'completed' para el bot
        bot_docs = crud.get_documents_by_bot(db, bot_id=bot_id)
        completed_docs = [doc for doc in bot_docs if doc.status == models.DocumentStatus.COMPLETED and doc.vector_index_path]

        if not completed_docs:
            logging.warning(f"No se encontraron documentos procesados para el bot {bot_id}.")
            # Devolver lista vacía para permitir que el modelo use su conocimiento base
            return []

        all_chunks = []
        logging.info(f"Buscando en {len(completed_docs)} documento(s) para el bot {bot_id}.")

        # 2. Cargar cada índice y buscar los chunks relevantes
        for doc in completed_docs:
            index_path = doc.vector_index_path
            if os.path.exists(index_path):
                try:
                    # Cargar el vector store de FAISS, permitiendo la deserialización
                    vector_store = FAISS.load_local(
                        index_path, 
                        embeddings_model, 
                        allow_dangerous_deserialization=True # <-- ESTA ES LA LÍNEA CLAVE
                    )
                    
                    # Buscar documentos similares y añadir los resultados
                    results = vector_store.similarity_search_with_score(query, k=k)
                    all_chunks.extend(results)
                except Exception as e:
                    logging.error(f"Error al cargar o buscar en el índice {index_path}: {e}")
            else:
                logging.warning(f"La ruta del índice no existe: {index_path}")
        
        if not all_chunks:
            logging.info(f"No se encontraron chunks relevantes para la consulta: {query}")
            # Devolver lista vacía para permitir que el modelo use su conocimiento base
            return []

        # 3. Ordenar todos los chunks por relevancia (menor puntuación es mejor)
        all_chunks.sort(key=lambda x: x[1])
        
        # Devolver el contenido de los 'k' mejores chunks
        top_k_chunks = [chunk[0].page_content for chunk in all_chunks[:k]]
        logging.info(f"Chunks más relevantes encontrados: {len(top_k_chunks)} chunks")
        
        return top_k_chunks