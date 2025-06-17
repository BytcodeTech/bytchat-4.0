class ModelRouter:
    def __init__(self):
        print("ModelRouter inicializado (MODO DE PRUEBA: FORZANDO DEEPSEEK-CHAT).")

    def select_model(self, query: str) -> dict:
        """
        Para esta prueba, esta función siempre elegirá el modelo deepseek-chat.
        """
        print("Router: Forzando el uso de DeepSeek-Chat para la prueba de contexto RAG.")
        return {
            "connector_type": "deepseek",
            "model_id": "deepseek-chat"
        }