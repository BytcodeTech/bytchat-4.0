import os
from openai import OpenAI
from dotenv import load_dotenv

class OpenAIConnector:
    def __init__(self):
        print("Inicializando OpenAIConnector...")
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("¡Error Crítico! OPENAI_API_KEY no fue encontrada.")
        self.client = OpenAI(api_key=api_key)
        print("OpenAIConnector configurado y listo.")

    def get_response_stream(self, prompt_package: dict, model_id: str = "gpt-3.5-turbo"):
        try:
            print(f"Iniciando STREAM con OpenAI (modelo: {model_id})...")
            stream = self.client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": prompt_package['system_prompt']},
                    {"role": "user", "content": prompt_package['user_question']}
                ],
                stream=True
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content is not None:
                    yield content
        except Exception as e:
            print(f"Ocurrió un error al contactar la API de OpenAI: {e}")
            yield "Lo siento, tuve un problema para contactar a mi cerebro de IA (OpenAI)."