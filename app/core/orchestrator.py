from .rag_retriever import RAGRetriever
from .model_router import ModelRouter
from connectors.google_connector import GoogleConnector
from connectors.openai_connector import OpenAIConnector
from connectors.deepseek_connector import DeepSeekConnector

class Orchestrator:
    def __init__(self):
        print("Orchestrator (Streaming) inicializado.")
        self.retriever = RAGRetriever()
        self.router = ModelRouter()
        self.connectors = {
            "google": GoogleConnector(),
            "openai": OpenAIConnector(),
            "deepseek": DeepSeekConnector()
        }
        print("Sistema listo para recibir peticiones.")

    def handle_query(self, user_id: str, query: str):
        print(f"\n--- Nueva Petición Recibida --- \nProcesando pregunta: '{query}'")

        context, score = self.retriever.search(query)
        
        prompt_package = {}
        if score < 1.5:
            prompt_package = {
                "system_prompt": f"Basándote estrictamente en el siguiente CONTEXTO, responde a la PREGUNTA del usuario de forma amable y directa. No añadas información que no esté en el contexto. CONTEXTO: --- {context} ---",
                "user_question": query
            }
        else:
            prompt_package = {
                "system_prompt": "Eres un asistente servicial.",
                "user_question": f"Responde a la siguiente pregunta del usuario de la mejor manera que puedas. PREGUNTA: {query}"
            }

        model_decision = self.router.select_model(query)
        selected_connector_type = model_decision["connector_type"]
        selected_model_id = model_decision["model_id"]
        
        connector = self.connectors[selected_connector_type]
        
        return connector.get_response_stream(prompt_package=prompt_package, model_id=selected_model_id)