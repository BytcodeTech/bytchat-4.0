// bytchat-panel/src/types/index.ts

// Configuración de un modelo de IA dentro de un bot
export interface ModelConfig {
  id: number;
  provider: string;
  model_id: string;
  // Añade otros campos si los tienes en el backend, como 'api_key', etc.
}

// Representa un bot completo, tal como lo devuelve la API
export interface Bot {
  id: number;
  user_id: number;
  name: string;
  description: string;
  system_prompt: string;
  model_configs: ModelConfig[];
}