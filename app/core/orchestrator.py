import logging
from sqlalchemy.orm import Session
from app.core.rag_retriever import RAGRetriever
from app.core.model_router import ModelRouter
from app.connectors.google_connector import GoogleConnector
from app.connectors.openai_connector import OpenAIConnector
from app.connectors.deepseek_connector import DeepSeekConnector
from app import schemas

class Orchestrator:
    def __init__(self, db: Session, bot_config: dict, bot_id: int):
        self.db = db
        self.bot_config = bot_config
        self.bot_id = bot_id
        self.router = ModelRouter()
        self.retriever = RAGRetriever()
        
        self.connectors = {
            "google": GoogleConnector(),
            "openai": OpenAIConnector(),
            "deepseek": DeepSeekConnector()
        }
        logging.info(f"Orquestador inicializado para el bot {bot_id}.")

    def handle_query(self, user_id: str, query: str):
        logging.info(f"\n--- Petición para el Bot ID: {self.bot_id} ---")

        relevant_chunks = self.retriever.search(db=self.db, bot_id=self.bot_id, query=query)
        
        # Construir el prompt según si hay contexto o no
        if relevant_chunks:
            context = "\n".join(relevant_chunks)
            logging.info(f"Contexto recuperado para la pregunta: {len(relevant_chunks)} chunks")
            prompt_package = {
                "system_prompt": self.bot_config.get("system_prompt", "Eres un asistente de IA."),
                "user_question": f"Usando el siguiente contexto, responde la pregunta.\n\nCONTEXTO:\n{context}\n\nPREGUNTA:\n{query}"
            }
        else:
            logging.info("No se encontró contexto relevante, el modelo usará su conocimiento base")
            prompt_package = {
                "system_prompt": self.bot_config.get("system_prompt", "Eres un asistente de IA. Si no hay contexto relevante, responde usando tu conocimiento general."),
                "user_question": (
                    "No se encontró información relevante en los documentos proporcionados. "
                    "Responde la siguiente pregunta usando únicamente tu conocimiento general, sin limitarte a los documentos:\n\n"
                    f"{query}"
                )
            }

        available_models = self.bot_config.get("model_configs", [])
        chosen_model_config = self.router.select_model(query, available_models)

        if not chosen_model_config:
            yield "No tengo un modelo de IA configurado para responder."
            return

        provider_name = chosen_model_config.get("provider")
        model_id_name = chosen_model_config.get("model_id")
        connector = self.connectors.get(provider_name)
        
        if not connector:
            yield f"Error: Conector para '{provider_name}' no encontrado."
            return
        
        logging.info(f"Modelo seleccionado: {model_id_name} via {provider_name}")

        stream = connector.get_response_stream(
            prompt_package=prompt_package, 
            model_id=model_id_name,
            temperature=self.bot_config.get("temperature", 0.7)
        )
        
        for chunk in stream:
            yield chunk