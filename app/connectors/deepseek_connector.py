from openai import OpenAI
# Importamos nuestro objeto de configuración centralizado
from ..config import settings

class DeepSeekConnector:
    def __init__(self):
        # Leemos la clave de API desde el objeto 'settings'
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY, 
            base_url="https://api.deepseek.com/v1"
        )
        print("Conector de DeepSeek inicializado correctamente.")

    def get_response_stream(self, prompt_package, model_id='deepseek-chat'):
        """
        Obtiene una respuesta en streaming del modelo de DeepSeek.
        """
        system_prompt = prompt_package.get("system_prompt", "Eres un asistente útil.")
        user_question = prompt_package.get("user_question", "")
        
        try:
            stream = self.client.chat.completions.create(
                model=model_id,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_question}
                ],
                stream=True,
                max_tokens=4096,
                temperature=0.7,
            )

            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            print(f"Error en el conector de DeepSeek: {e}")
            yield "Lo siento, he tenido un problema al conectar con el servicio de DeepSeek."

