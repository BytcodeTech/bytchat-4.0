from openai import OpenAI
# Importamos nuestro objeto de configuración centralizado
from ..config import settings

class OpenAIConnector:
    def __init__(self):
        # Leemos la clave de API desde el objeto 'settings'
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        print("Conector de OpenAI inicializado correctamente.")

    def get_response_stream(self, prompt_package, model_id='gpt-4o'):
        """
        Obtiene una respuesta en streaming del modelo de OpenAI.
        """
        system_prompt = prompt_package.get("system_prompt", "Eres un asistente útil.")
        user_question = prompt_package.get("user_question", "")

        try:
            stream = self.client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                stream=True,
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            print(f"Error en el conector de OpenAI: {e}")
            yield "Lo siento, he tenido un problema al conectar con el servicio de OpenAI."
