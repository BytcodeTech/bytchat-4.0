import os
from openai import OpenAI
from dotenv import load_dotenv

class DeepSeekConnector:
    def __init__(self):
        print("Inicializando DeepSeekConnector...")
        load_dotenv()
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("¡Error Crítico! DEEPSEEK_API_KEY no fue encontrada.")
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        print("DeepSeekConnector configurado y listo.")

    def get_response_stream(self, prompt_package: dict, model_id: str = "deepseek-chat"):
        """
        Maneja la respuesta por streaming de DeepSeek con depuración de errores.
        """
        try:
            print(f"Iniciando STREAM con DeepSeek (modelo: {model_id})...")
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
            # ¡LA CLAVE! Imprimimos el error real que nos da la API de DeepSeek.
            print("\n--- INICIO DEL ERROR DETALLADO DE DEEPSEEK ---")
            print(e)
            print("--- FIN DEL ERROR DETALLADO DE DEEPSEEK ---\n")
            yield "Lo siento, tuve un problema con la conexión a DeepSeek."