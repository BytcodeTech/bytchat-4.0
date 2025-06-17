import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import os

# --- Configuración ---
INDEX_PATH = "data/vector_db/bytcode_index.faiss"
CHUNKS_MAP_PATH = "data/vector_db/chunks_map.json"
MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'

class RAGRetriever:
    def __init__(self):
        print("Inicializando RAGRetriever...")
        if not os.path.exists(INDEX_PATH) or not os.path.exists(CHUNKS_MAP_PATH):
            raise FileNotFoundError("¡Error Crítico! El índice FAISS o el mapa de chunks no existen. Por favor, ejecuta 'indexer.py' primero.")

        self.model = SentenceTransformer(MODEL_NAME)
        self.index = faiss.read_index(INDEX_PATH)
        with open(CHUNKS_MAP_PATH, 'r', encoding='utf-8') as f:
            self.chunks_map = json.load(f)
        
        print("RAGRetriever cargado y listo para buscar.")

    def search(self, query: str, top_k: int = 3) -> tuple[str, float]:
        """
        Busca los fragmentos de texto más relevantes para una pregunta dada.
        """
        print(f"Buscando contexto para la pregunta: '{query}'")
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')

        # ¡LÍNEA CLAVE AÑADIDA! También normalizamos el vector de la pregunta.
        faiss.normalize_L2(query_embedding)

        distances, indices = self.index.search(query_embedding, top_k)
        
        best_score = distances[0][0]
        
        relevant_chunks = [self.chunks_map[i] for i in indices[0]]
        
        print(f"Se encontraron {len(relevant_chunks)} fragmentos. Mejor puntuación (distancia): {best_score}")
        
        context = "\n\n---\n\n".join(relevant_chunks)
        
        return context, best_score