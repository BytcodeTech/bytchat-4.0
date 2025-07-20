import time
import google.generativeai as genai
from typing import Tuple, Dict, Any, Generator
# Importamos nuestro objeto de configuración centralizado
from ..config import settings
from .base_connector import BaseConnector

class GoogleConnector(BaseConnector):
    def __init__(self):
        # Leemos la clave de API desde el objeto 'settings'
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("La clave GOOGLE_API_KEY no está configurada en el archivo .env")
        
        genai.configure(api_key=api_key)
        print("Conector de Google inicializado correctamente.")

    def get_response_stream(self, prompt_package: dict, model_id: str = 'gemini-1.5-pro-latest', temperature: float = 0.7) -> Generator[str, None, None]:
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
            
            generation_config = genai.types.GenerationConfig(temperature=temperature)
            response_stream = model.generate_content(user_question, stream=True, generation_config=generation_config)
            
            for chunk in response_stream:
                # Usamos 'yield' para devolver cada trozo de texto a medida que llega
                yield chunk.text
        except Exception as e:
            print(f"Error en el conector de Google: {e}")
            yield "Lo siento, he tenido un problema al conectar con el servicio de Google."

    def get_response_with_metrics(self, prompt_package: dict, model_id: str = 'gemini-1.5-pro-latest', temperature: float = 0.7) -> Tuple[str, Dict[str, Any]]:
        """
        Obtiene una respuesta completa con métricas de tokens de Google.
        """
        system_prompt = prompt_package.get("system_prompt", "Eres un asistente útil.")
        user_question = prompt_package.get("user_question", "")
        
        start_time = time.time()
        
        try:
            model = genai.GenerativeModel(
                model_name=model_id,
                system_instruction=system_prompt
            )
            
            generation_config = genai.types.GenerationConfig(temperature=temperature)
            response = model.generate_content(user_question, generation_config=generation_config)
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Extraer información de la respuesta
            response_text = response.text
            
            # Google Gemini incluye información de tokens en la respuesta
            usage_metadata = response.usage_metadata
            
            metrics = {
                "prompt_tokens": usage_metadata.prompt_token_count,
                "completion_tokens": usage_metadata.candidates_token_count,
                "total_tokens": usage_metadata.total_token_count,
                "model_used": model_id,
                "response_time_ms": response_time_ms
            }
            
            return response_text, metrics
            
        except Exception as e:
            print(f"Error en el conector de Google: {e}")
            # En caso de error, estimar tokens
            estimated_prompt = self.estimate_tokens(system_prompt + user_question)
            error_message = "Lo siento, he tenido un problema al conectar con el servicio de Google."
            estimated_completion = self.estimate_tokens(error_message)
            
            metrics = {
                "prompt_tokens": estimated_prompt,
                "completion_tokens": estimated_completion,
                "total_tokens": estimated_prompt + estimated_completion,
                "model_used": model_id,
                "response_time_ms": 0,
                "error": str(e)
            }
            
            return error_message, metrics

