from abc import ABC, abstractmethod

class BaseConnector(ABC):
    @abstractmethod
    def get_response_stream(self, prompt_package: dict, model_id: str, temperature: float):
        """
        Método abstracto para obtener una respuesta en streaming del modelo.
        """
        pass