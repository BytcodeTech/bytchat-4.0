import os
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import json

# --- Configuración (sin cambios) ---
DOCS_PATH = "data/raw_docs"
INDEX_PATH = "data/vector_db/bytcode_index.faiss"
CHUNKS_MAP_PATH = "data/vector_db/chunks_map.json"
MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'

def create_index():
    print("Iniciando el proceso de indexación...")
    model = SentenceTransformer(MODEL_NAME)
    print("Modelo cargado.")

    all_chunks = []
    print(f"Leyendo documentos desde la carpeta: {DOCS_PATH}...")
    if not os.path.exists(DOCS_PATH):
        print(f"¡Error! La carpeta '{DOCS_PATH}' no existe.")
        return

    for filename in os.listdir(DOCS_PATH):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_PATH, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                
                # ¡NUEVA LÓGICA DE CHUNKING MEJORADA!
                # Primero dividimos por párrafos (doble salto de línea)
                paragraphs = text.split('\n\n')
                for paragraph in paragraphs:
                    # Luego, dividimos cada párrafo por líneas individuales
                    lines = paragraph.split('\n')
                    # Añadimos cada línea como un chunk si tiene suficiente texto
                    chunks = [line.strip() for line in lines if len(line.strip()) > 10]
                    all_chunks.extend(chunks)
    
    if not all_chunks:
        print("¡Error! No se encontraron fragmentos de texto válidos.")
        return

    print(f"Se encontraron y procesaron {len(all_chunks)} fragmentos de texto (chunks).")

    print("Generando y normalizando vectores...")
    embeddings = model.encode(all_chunks, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')
    faiss.normalize_L2(embeddings)

    print(f"Embeddings generados. Dimensión del vector: {embeddings.shape[1]}")

    print("Creando y construyendo el índice FAISS...")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    print(f"Índice creado. Contiene {index.ntotal} vectores.")

    os.makedirs("data/vector_db", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(CHUNKS_MAP_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=4)

    print("\n¡Proceso de indexación completado con éxito!")

if __name__ == "__main__":
    create_index()