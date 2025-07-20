# app/connectors/deepseek_connector.py
import os
import time
import httpx
import json
from typing import Tuple, Dict, Any, Generator
from .base_connector import BaseConnector

class DeepSeekConnector(BaseConnector):
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY no encontrada.")
        self.base_url = "https://api.deepseek.com/v1"
        print("Conector de DeepSeek inicializado.")

    def get_response_stream(self, prompt_package: dict, model_id: str, temperature: float = 0.7) -> Generator[str, None, None]:
        headers = { "Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}" }
        data = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": prompt_package.get("system_prompt")},
                {"role": "user", "content": prompt_package.get("user_question")}
            ],
            "stream": True,
            "temperature": temperature,
            "max_tokens": 4096
        }
        try:
            with httpx.stream("POST", f"{self.base_url}/chat/completions", headers=headers, json=data, timeout=120) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line.startswith("data: "):
                        line_content = line[6:]
                        if line_content.strip() == "[DONE]": break
                        try:
                            json_data = json.loads(line_content)
                            content = json_data.get("choices", [{}])[0].get("delta", {}).get("content")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield f"Error en DeepSeek: {str(e)}"

    def get_response_with_metrics(self, prompt_package: dict, model_id: str, temperature: float = 0.7) -> Tuple[str, Dict[str, Any]]:
        """
        Obtiene una respuesta completa con métricas de tokens de DeepSeek.
        """
        headers = { "Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}" }
        data = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": prompt_package.get("system_prompt")},
                {"role": "user", "content": prompt_package.get("user_question")}
            ],
            "stream": False,  # No streaming para obtener métricas
            "temperature": temperature,
            "max_tokens": 4096
        }
        
        start_time = time.time()
        
        try:
            response = httpx.post(f"{self.base_url}/chat/completions", headers=headers, json=data, timeout=120)
            response.raise_for_status()
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            response_data = response.json()
            
            # Extraer información de la respuesta
            response_text = response_data["choices"][0]["message"]["content"]
            usage = response_data.get("usage", {})
            
            metrics = {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "model_used": model_id,
                "response_time_ms": response_time_ms
            }
            
            return response_text, metrics
            
        except Exception as e:
            print(f"Error en el conector de DeepSeek: {e}")
            # En caso de error, estimar tokens
            system_prompt = prompt_package.get("system_prompt", "")
            user_question = prompt_package.get("user_question", "")
            estimated_prompt = self.estimate_tokens(system_prompt + user_question)
            error_message = f"Error en DeepSeek: {str(e)}"
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