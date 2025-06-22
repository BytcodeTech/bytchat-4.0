import json

class ModelRouter:
    def __init__(self):
        # Palabras clave que indican una consulta compleja
        self.complex_keywords = [
            "analiza", "resume", "traduce", "explica", "código", 
            "tabla", "lista", "optimiza", "compara", "crea"
        ]
        print("ModelRouter inicializado.")

    def select_model(self, query: str) -> str:
        """
        Analiza la pregunta y decide si es 'simple' o 'compleja'.
        """
        # Convertimos la pregunta a minúsculas para una comparación más fácil
        lower_query = query.lower()
        
        # Verificamos si alguna de nuestras palabras clave complejas está en la pregunta
        for keyword in self.complex_keywords:
            if keyword in lower_query:
                print(f"ModelRouter: Consulta clasificada como 'compleja' por la palabra clave: '{keyword}'")
                return "complex"
        
        print("ModelRouter: Consulta clasificada como 'simple'.")
        return "simple"

