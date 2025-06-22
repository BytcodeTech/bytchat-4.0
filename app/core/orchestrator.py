from .rag_retriever import RAGRetriever
from .model_router import ModelRouter
from ..connectors.google_connector import GoogleConnector
from ..connectors.openai_connector import OpenAIConnector
from ..connectors.deepseek_connector import DeepSeekConnector
from ..config import settings

class Orchestrator:
    def __init__(self, bot_config: dict):
        print(f"Orquestador inicializado para la configuración: {bot_config}")
        
        self.bot_config = bot_config
        # Inicializamos nuestro nuevo enrutador
        self.router = ModelRouter()
        
        # self.retriever = RAGRetriever(...) # Lógica RAG para el futuro
        
        self.connectors = {
            "google": GoogleConnector(),
            "openai": OpenAIConnector(),
            "deepseek": DeepSeekConnector()
        }
        print("Sistema listo para recibir peticiones.")

    def handle_query(self, user_id: str, query: str):
        print(f"\n--- Nueva Petición Recibida --- \nProcesando pregunta: '{query}'")

        # --- Lógica de Enrutamiento ---
        # 1. El enrutador decide la complejidad
        task_complexity = self.router.select_model(query)

        # 2. Elegimos el modelo basado en la decisión del enrutador y la config del bot
        if task_complexity == "complex":
            model_full_id = self.bot_config.get("complex_model_id", "gemini-1.5-pro-latest")
            print(f"Usando modelo complejo: {model_full_id}")
        else:
            model_full_id = self.bot_config.get("simple_model_id", "gemini-1.5-flash-latest")
            print(f"Usando modelo simple: {model_full_id}")

        # Suponemos un formato 'proveedor:id_del_modelo', ej: "google:gemini-1.5-pro-latest"
        # Esto es un ejemplo, lo haremos más robusto después.
        try:
            # Asumimos por ahora que los modelos de google no llevan prefijo
            if ":" not in model_full_id:
                selected_connector_type = "google"
                selected_model_id = model_full_id
            else:
                selected_connector_type, selected_model_id = model_full_id.split(":", 1)
        except Exception:
             # Si falla, usamos un default seguro
            selected_connector_type = "google"
            selected_model_id = "gemini-1.5-flash-latest"


        # --- Creación del Prompt y Llamada al Conector ---
        prompt_package = {
            "system_prompt": self.bot_config.get("system_prompt", "Eres un asistente de IA."),
            "user_question": query
        }
        
        connector = self.connectors.get(selected_connector_type)
        if not connector:
             # Si el conector no existe, usamos un default
            print(f"ADVERTENCIA: Conector '{selected_connector_type}' no encontrado. Usando 'google'.")
            connector = self.connectors["google"]

        return connector.get_response_stream(prompt_package=prompt_package, model_id=selected_model_id)

