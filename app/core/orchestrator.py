import logging
from .rag_retriever import RAGRetriever
from .model_router import ModelRouter
from ..connectors.google_connector import GoogleConnector
from ..connectors.openai_connector import OpenAIConnector
from ..connectors.deepseek_connector import DeepSeekConnector

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)

class Orchestrator:
    def __init__(self, bot_config: dict, bot_id: int):
        self.bot_config = bot_config
        self.bot_id = bot_id
        self.router = ModelRouter()
        
        # self.retriever = RAGRetriever(bot_id=self.bot_id)
        
        self.connectors = {
            "google": GoogleConnector(),
            "openai": OpenAIConnector(),
            "deepseek": DeepSeekConnector()
        }
        logging.info(f"Orquestador inicializado para el bot {bot_id}.")

    def handle_query(self, user_id: str, query: str):
        logging.info(f"\n--- Petición para el Bot ID: {self.bot_id} ---")

        available_models = self.bot_config.get('model_configs', [])
        if not available_models:
            yield "Lo siento, este bot no tiene modelos de IA configurados."
            return

        chosen_model_config = self.router.select_model(query, available_models)
        
        if not chosen_model_config:
            yield "Lo siento, no tengo un modelo adecuado para responder a tu pregunta."
            return

        provider = chosen_model_config['provider']
        model_id = chosen_model_config['model_id']
        
        system_prompt = self.bot_config.get("system_prompt", "Eres un asistente de IA.")
        
        prompt_package = {
            "system_prompt": system_prompt,
            "user_question": query
        }
        
        connector = self.connectors.get(provider)
        if not connector:
            logging.error(f"Error: El proveedor de IA '{provider}' no está configurado en el sistema.")
            yield f"Error: El proveedor de IA '{provider}' no está configurado en el sistema."
            return
            
        yield from connector.get_response_stream(prompt_package=prompt_package, model_id=model_id)
