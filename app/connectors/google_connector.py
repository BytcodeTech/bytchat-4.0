import google.generativeai as genai
# Importamos nuestro objeto de configuración centralizado
from ..config import settings
from app.connectors.base_connector import BaseConnector

class GoogleConnector:
    def __init__(self):
        # Leemos la clave de API desde el objeto 'settings'
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("La clave GOOGLE_API_KEY no está configurada en el archivo .env")
        
        genai.configure(api_key=api_key)
        print("Conector de Google inicializado correctamente.")

    def get_response_stream(self, prompt_package, model_id='gemini-1.5-pro-latest', temperature=None):
        """
        Obtiene una respuesta en streaming del modelo de Google.
        """
        system_prompt = prompt_package.get("system_prompt", "Eres un asistente útil.")
        user_question = prompt_package.get("user_question", "")
        
        try:
            model = genai.GenerativeModel(
                model_name=model_id,
                system_instruction=system_prompt
            )
            
            response_stream = model.generate_content(user_question, stream=True)
            
            for chunk in response_stream:
                # Usamos 'yield' para devolver cada trozo de texto a medida que llega
                yield chunk.text
        except Exception as e:
            print(f"Error en el conector de Google: {e}")
            yield "Lo siento, he tenido un problema al conectar con el servicio de Google."

