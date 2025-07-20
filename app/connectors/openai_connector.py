import time
from openai import OpenAI
from typing import Tuple, Dict, Any, Generator
# Importamos nuestro objeto de configuración centralizado
from ..config import settings
from .base_connector import BaseConnector

class OpenAIConnector(BaseConnector):
    def __init__(self):
        # Leemos la clave de API desde el objeto 'settings'
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        print("Conector de OpenAI inicializado correctamente.")

    def get_response_stream(self, prompt_package: dict, model_id: str = 'gpt-4o', temperature: float = 0.7) -> Generator[str, None, None]:
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
                temperature=temperature,
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            print(f"Error en el conector de OpenAI: {e}")
            yield "Lo siento, he tenido un problema al conectar con el servicio de OpenAI."

    def get_response_with_metrics(self, prompt_package: dict, model_id: str = 'gpt-4o', temperature: float = 0.7) -> Tuple[str, Dict[str, Any]]:
        """
        Obtiene una respuesta completa con métricas de tokens de OpenAI.
        """
        system_prompt = prompt_package.get("system_prompt", "Eres un asistente útil.")
        user_question = prompt_package.get("user_question", "")
        
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                temperature=temperature,
            )
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Extraer información de la respuesta
            response_text = response.choices[0].message.content
            usage = response.usage
            
            metrics = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "model_used": model_id,
                "response_time_ms": response_time_ms
            }
            
            return response_text, metrics
            
        except Exception as e:
            print(f"Error en el conector de OpenAI: {e}")
            # En caso de error, estimar tokens
            estimated_prompt = self.estimate_tokens(system_prompt + user_question)
            error_message = "Lo siento, he tenido un problema al conectar con el servicio de OpenAI."
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
