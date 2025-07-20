import logging
from sqlalchemy.orm import Session
from app.core.rag_retriever import RAGRetriever
from app.core.model_router import ModelRouter
from app.connectors.google_connector import GoogleConnector
from app.connectors.openai_connector import OpenAIConnector
from app.connectors.deepseek_connector import DeepSeekConnector
from app.services.metrics_service import MetricsService
from app import schemas

class Orchestrator:
    def __init__(self, db: Session, bot_config: dict, bot_id: int, user_id: int = None):
        self.db = db
        self.bot_config = bot_config
        self.bot_id = bot_id
        self.user_id = user_id
        self.router = ModelRouter()
        self.retriever = RAGRetriever()
        self.metrics_service = MetricsService(db)
        
        self.connectors = {
            "google": GoogleConnector(),
            "openai": OpenAIConnector(),
            "deepseek": DeepSeekConnector()
        }
        logging.info(f"Orquestador inicializado para el bot {bot_id}.")

    def handle_query(self, user_id: str, query: str, track_metrics: bool = True):
        """
        Maneja una consulta con soporte para métricas opcionales
        
        Args:
            user_id: ID del usuario (puede ser anónimo)
            query: Consulta del usuario
            track_metrics: Si True, registra métricas (requiere user_id numérico para facturación)
        """
        logging.info(f"\n--- Petición para el Bot ID: {self.bot_id} ---")

        relevant_chunks = self.retriever.search(db=self.db, bot_id=self.bot_id, query=query)
        
        # Construir el prompt según si hay contexto o no
        if relevant_chunks:
            context = "\n".join(relevant_chunks)
            logging.info(f"Contexto recuperado para la pregunta: {len(relevant_chunks)} chunks")
            prompt_package = {
                "system_prompt": self.bot_config.get("system_prompt", "Eres un asistente de IA."),
                "user_question": f"Usando el siguiente contexto, responde la pregunta.\n\nCONTEXTO:\n{context}\n\nPREGUNTA:\n{query}"
            }
        else:
            logging.info("No se encontró contexto relevante, el modelo usará su conocimiento base")
            prompt_package = {
                "system_prompt": self.bot_config.get("system_prompt", "Eres un asistente de IA. Si no hay contexto relevante, responde usando tu conocimiento general."),
                "user_question": (
                    "No se encontró información relevante en los documentos proporcionados. "
                    "Responde la siguiente pregunta usando únicamente tu conocimiento general, sin limitarte a los documentos:\n\n"
                    f"{query}"
                )
            }

        available_models = self.bot_config.get("model_configs", [])
        chosen_model_config = self.router.select_model(query, available_models)

        if not chosen_model_config:
            yield "No tengo un modelo de IA configurado para responder."
            return

        provider_name = chosen_model_config.get("provider")
        model_id_name = chosen_model_config.get("model_id")
        connector = self.connectors.get(provider_name)
        
        if not connector:
            yield f"Error: Conector para '{provider_name}' no encontrado."
            return
        
        logging.info(f"Modelo seleccionado: {model_id_name} via {provider_name}")

        # Decidir si usar streaming o métricas
        if track_metrics and self.user_id and isinstance(self.user_id, int):
            # Verificar límites antes de procesar
            # Estimar tokens del prompt para verificación previa
            estimated_tokens = connector.estimate_tokens(
                prompt_package["system_prompt"] + prompt_package["user_question"]
            )
            
            limit_check = self.metrics_service.check_token_limit(self.user_id, estimated_tokens)
            
            if not limit_check["allowed"]:
                yield "Lo siento, has alcanzado el límite de tokens de tu plan gratuito. Por favor, actualiza tu plan para continuar."
                return
            
            # Usar método con métricas
            try:
                response_text, metrics = connector.get_response_with_metrics(
                    prompt_package=prompt_package,
                    model_id=model_id_name,
                    temperature=self.bot_config.get("temperature", 0.7)
                )
                
                # Registrar uso de tokens
                self.metrics_service.record_token_usage(
                    user_id=self.user_id,
                    bot_id=self.bot_id,
                    user_anon_id=user_id if not isinstance(self.user_id, int) else None,
                    query=query,
                    provider=provider_name,
                    model_id=model_id_name,
                    prompt_tokens=metrics["prompt_tokens"],
                    completion_tokens=metrics["completion_tokens"],
                    response_time_ms=metrics.get("response_time_ms")
                )
                
                # Entregar respuesta completa
                yield response_text
                
            except Exception as e:
                logging.error(f"Error al obtener respuesta con métricas: {e}")
                # Fallback a streaming sin métricas
                yield from self._handle_streaming_response(connector, prompt_package, model_id_name)
        else:
            # Usar streaming sin métricas (para usuarios anónimos o cuando no se requieren métricas)
            yield from self._handle_streaming_response(connector, prompt_package, model_id_name)

    def _handle_streaming_response(self, connector, prompt_package: dict, model_id: str):
        """Maneja la respuesta en streaming sin métricas"""
        try:
            stream = connector.get_response_stream(
                prompt_package=prompt_package, 
                model_id=model_id,
                temperature=self.bot_config.get("temperature", 0.7)
            )
            
            for chunk in stream:
                yield chunk
        except Exception as e:
            logging.error(f"Error en streaming: {e}")
            yield f"Error al procesar la solicitud: {str(e)}"

    def handle_query_with_full_metrics(self, user_id: str, query: str):
        """
        Versión especial que siempre retorna métricas completas
        Útil para endpoints que necesitan información detallada
        """
        if not self.user_id or not isinstance(self.user_id, int):
            raise ValueError("Se requiere user_id numérico para tracking completo de métricas")
        
        # Igual lógica que handle_query pero siempre con métricas
        relevant_chunks = self.retriever.search(db=self.db, bot_id=self.bot_id, query=query)
        
        if relevant_chunks:
            context = "\n".join(relevant_chunks)
            prompt_package = {
                "system_prompt": self.bot_config.get("system_prompt", "Eres un asistente de IA."),
                "user_question": f"Usando el siguiente contexto, responde la pregunta.\n\nCONTEXTO:\n{context}\n\nPREGUNTA:\n{query}"
            }
        else:
            prompt_package = {
                "system_prompt": self.bot_config.get("system_prompt", "Eres un asistente de IA."),
                "user_question": query
            }

        available_models = self.bot_config.get("model_configs", [])
        chosen_model_config = self.router.select_model(query, available_models)

        if not chosen_model_config:
            raise ValueError("No hay modelo configurado")

        provider_name = chosen_model_config.get("provider")
        model_id_name = chosen_model_config.get("model_id")
        connector = self.connectors.get(provider_name)
        
        if not connector:
            raise ValueError(f"Conector para '{provider_name}' no encontrado")

        # Obtener respuesta con métricas
        response_text, metrics = connector.get_response_with_metrics(
            prompt_package=prompt_package,
            model_id=model_id_name,
            temperature=self.bot_config.get("temperature", 0.7)
        )
        
        # Registrar uso de tokens
        token_usage = self.metrics_service.record_token_usage(
            user_id=self.user_id,
            bot_id=self.bot_id,
            user_anon_id=user_id if not isinstance(self.user_id, int) else None,
            query=query,
            provider=provider_name,
            model_id=model_id_name,
            prompt_tokens=metrics["prompt_tokens"],
            completion_tokens=metrics["completion_tokens"],
            response_time_ms=metrics.get("response_time_ms")
        )
        
        return {
            "response": response_text,
            "metrics": metrics,
            "token_usage": token_usage
        }