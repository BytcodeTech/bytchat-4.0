# --- Importaciones corregidas para la nueva estructura ---

# Un punto (.) para importar módulos de la misma carpeta (core).
from .rag_retriever import RAGRetriever
from .model_router import ModelRouter

# Dos puntos (..) para subir un nivel (a 'app') y luego entrar a 'connectors'.
from ..connectors.google_connector import GoogleConnector
from ..connectors.openai_connector import OpenAIConnector
from ..connectors.deepseek_connector import DeepSeekConnector
from ..config import settings # Importamos la configuración para las API keys

class Orchestrator:
    def __init__(self, bot_config: dict):
        print(f"Orquestador (Streaming) inicializado para la configuración: {bot_config}")
        
        self.bot_config = bot_config
        
        # Por ahora, dejamos la lógica del RAG y el router comentada.
        # La activaremos en un siguiente paso.
        # self.retriever = RAGRetriever(bot_config['rag_index_path']) 
        # self.router = ModelRouter()
        
        # Inicializamos los conectores. Las claves de API se cargan
        # automáticamente dentro de cada conector desde la configuración.
        self.connectors = {
            "google": GoogleConnector(),
            "openai": OpenAIConnector(),
            "deepseek": DeepSeekConnector()
        }
        print("Sistema listo para recibir peticiones.")

    def handle_query(self, user_id: str, query: str):
        print(f"\n--- Nueva Petición Recibida --- \nProcesando pregunta: '{query}'")

        prompt_package = {
            "system_prompt": "Eres un asistente de IA llamado Bytchat, creado por Bytcode. Eres servicial, inteligente y un poco creativo.",
            "user_question": query
        }

        # En el futuro, esta configuración vendrá de la base de datos para cada bot.
        selected_connector_type = "google"
        selected_model_id = "gemini-1.5-pro-latest"
        
        connector = self.connectors[selected_connector_type]
        
        # Devolvemos el stream del conector.
        return connector.get_response_stream(prompt_package=prompt_package, model_id=selected_model_id)
