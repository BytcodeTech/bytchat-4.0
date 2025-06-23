import json
import os
import faiss
import numpy as np
import logging
from langchain_community.embeddings import SentenceTransformerEmbeddings

logging.basicConfig(level=logging.INFO)

class RAGRetriever:
    def __init__(self, bot_id: int):
        self.bot_id = bot_id
        self.vector_db_path = f"data/vector_db/{self.bot_id}"
        self.index_file = os.path.join(self.vector_db_path, "index.faiss")
        self.map_file = os.path.join(self.vector_db_path, "chunks_map.json")
        
        self.index = None
        self.chunks_map = None
        
        if os.path.exists(self.index_file):
            logging.info(f"Cargando índice FAISS para el bot {self.bot_id} desde {self.index_file}")
            self.index = faiss.read_index(self.index_file)
            
            logging.info(f"Cargando mapa de chunks para el bot {self.bot_id} desde {self.map_file}")
            with open(self.map_file, 'r', encoding='utf-8') as f:
                self.chunks_map = {int(k): v for k, v in json.load(f).items()}
        else:
            logging.warning(f"ADVERTENCIA: No se encontró un índice de entrenamiento para el bot {self.bot_id}")

    def search(self, query: str, k: int = 3):
        if self.index is None or self.chunks_map is None:
            return []

        embeddings_generator = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        query_embedding = embeddings_generator.embed_query(query)
        
        query_vector = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_vector, k)
        
        relevant_chunks = [
            self.chunks_map[i] for i in indices[0] if i != -1
        ]
        
        logging.info(f"Chunks relevantes encontrados: {relevant_chunks}")
        return relevant_chunks

