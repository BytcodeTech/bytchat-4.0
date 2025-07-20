from abc import ABC, abstractmethod
from typing import Generator, Dict, Any, Tuple

class BaseConnector(ABC):
    @abstractmethod
    def get_response_stream(self, prompt_package: dict, model_id: str, temperature: float = 0.7) -> Generator[str, None, None]:
        """
        Método abstracto para obtener una respuesta en streaming del modelo.
        """
        pass

    @abstractmethod
    def get_response_with_metrics(self, prompt_package: dict, model_id: str, temperature: float = 0.7) -> Tuple[str, Dict[str, Any]]:
        """
        Método abstracto para obtener una respuesta completa con métricas de tokens.
        Returns: (response_text, metrics_dict)
        
        metrics_dict debe contener:
        {
            "prompt_tokens": int,
            "completion_tokens": int,
            "total_tokens": int,
            "model_used": str,
            "response_time_ms": int (opcional)
        }
        """
        pass

    def estimate_tokens(self, text: str) -> int:
        """
        Estimación básica de tokens basada en palabras.
        Los conectores específicos pueden sobrescribir este método para mayor precisión.
        """
        # Estimación básica: ~0.75 tokens por palabra
        words = len(text.split())
        return int(words * 0.75)