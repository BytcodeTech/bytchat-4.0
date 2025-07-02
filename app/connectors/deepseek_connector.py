# app/connectors/deepseek_connector.py
import os
import httpx
import json
from app.connectors.base_connector import BaseConnector

class DeepSeekConnector(BaseConnector):
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY no encontrada.")
        self.base_url = "https://api.deepseek.com/v1"
        print("Conector de DeepSeek inicializado.")

    def get_response_stream(self, prompt_package: dict, model_id: str, temperature: float = 0.7):
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