# Un gestor de caché muy simple basado en un diccionario de Python.
class CacheManager:
    def __init__(self):
        self.cache = {}
        print("CacheManager inicializado (memoria a corto plazo lista).")

    def get(self, query: str):
        """Busca una respuesta en el caché para una pregunta dada."""
        # .get(query, None) intenta buscar la 'query'. Si no la encuentra, devuelve None.
        return self.cache.get(query, None)

    def set(self, query: str, response: dict):
        """Guarda una nueva respuesta en el caché."""
        print(f"Guardando en caché la respuesta para: '{query}'")
        self.cache[query] = response