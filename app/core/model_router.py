import logging

logging.basicConfig(level=logging.INFO)

class ModelRouter:
    def __init__(self):
        self.complex_keywords = [
            "analiza", "resume", "traduce", "explica", "código", 
            "tabla", "lista", "optimiza", "compara", "crea"
        ]
        logging.info("ModelRouter (Toolbox) inicializado.")

    def select_model(self, query: str, available_models: list):
        lower_query = query.lower()
        # 1. Buscar modelo complejo si la consulta lo requiere
        for keyword in self.complex_keywords:
            if keyword in lower_query:
                for model_config in available_models:
                    if model_config['task_type'] == 'complex' and model_config['is_active']:
                        logging.info(f"ModelRouter: Consulta compleja. Usando modelo 'complex': {model_config['model_id']}")
                        return model_config

        # 2. Buscar modelo simple/general
        for model_config in available_models:
            if model_config['task_type'] in ['general', 'simple'] and model_config['is_active']:
                logging.info(f"ModelRouter: Consulta simple/general. Usando modelo '{model_config['task_type']}': {model_config['model_id']}")
                return model_config

        # 3. Fallback: si solo hay un modelo activo, usarlo para cualquier consulta
        modelos_activos = [m for m in available_models if m['is_active']]
        if len(modelos_activos) == 1:
            logging.info(f"ModelRouter: Solo hay un modelo activo, se usará para cualquier consulta: {modelos_activos[0]['model_id']}")
            return modelos_activos[0]

        logging.warning("ModelRouter: No se encontró un modelo adecuado en la configuración del bot.")
        return None

