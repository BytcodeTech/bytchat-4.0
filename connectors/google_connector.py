import os
import google.generativeai as genai
from dotenv import load_dotenv

class GoogleConnector:
    def __init__(self):
        print("Inicializando GoogleConnector...")
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("¡Error Crítico! GOOGLE_API_KEY no fue encontrada.")
        genai.configure(api_key=api_key)
        print("GoogleConnector configurado y listo.")

    def get_response_stream(self, prompt_package: dict, model_id: str = "gemini-1.5-pro"):
        try:
            print(f"Iniciando STREAM con Gemini (modelo: {model_id})...")
            model = genai.GenerativeModel(model_id)
            full_prompt = f"{prompt_package['system_prompt']}\n\nPREGUNTA DEL USUARIO:\n{prompt_package['user_question']}"
            response_stream = model.generate_content(full_prompt, stream=True)
            for chunk in response_stream:
                yield chunk.text
        except Exception as e:
            print(f"Ocurrió un error al contactar la API de Gemini: {e}")
            yield "Lo siento, tuve un problema para contactar a mi cerebro de IA (Gemini)."