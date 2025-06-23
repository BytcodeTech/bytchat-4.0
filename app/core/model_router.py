class ModelRouter:
    def __init__(self):
        self.complex_keywords = [
            "analiza", "resume", "traduce", "explica", "código", 
            "tabla", "lista", "optimiza", "compara", "crea"
        ]
        print("ModelRouter (Toolbox) inicializado.")

    def select_model(self, query: str, available_models: list):
        """
        Analiza la pregunta y elige el mejor modelo de la LISTA DE MODELOS DISPONIBLES.
        """
        lower_query = query.lower()
        
        # Primero, buscamos un modelo explícitamente para tareas complejas
        for keyword in self.complex_keywords:
            if keyword in lower_query:
                for model_config in available_models:
                    if model_config['task_type'] == 'complex' and model_config['is_active']:
                        print(f"ModelRouter: Consulta compleja. Usando modelo 'complex': {model_config['model_id']}")
                        return model_config
        
        # Si no, buscamos el primer modelo para tareas generales o simples que esté disponible
        for model_config in available_models:
            if model_config['task_type'] in ['general', 'simple'] and model_config['is_active']:
                print(f"ModelRouter: Consulta simple/general. Usando modelo '{model_config['task_type']}': {model_config['model_id']}")
                return model_config

        # Si no se encuentra ningún modelo adecuado, devolvemos None
        print("ModelRouter: No se encontró un modelo adecuado en la configuración del bot.")
        return None

