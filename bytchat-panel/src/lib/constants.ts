// bytchat-panel/src/lib/constants.ts
import { Model } from '@/components/cards/ModelCard';

export const AVAILABLE_MODELS: Model[] = [
  {
    provider: 'google',
    id: 'gemini-1.5-pro-latest',
    name: 'Gemini 1.5 Pro',
    task_type: 'complex', // <-- AÑADIDO
  },
  {
    provider: 'google',
    id: 'gemini-1.5-flash-latest',
    name: 'Gemini 1.5 Flash',
    task_type: 'simple', // <-- AÑADIDO
  },
  {
    provider: 'openai',
    id: 'gpt-4o',
    name: 'GPT-4o',
    task_type: 'complex', // <-- AÑADIDO
  },
  {
    provider: 'openai',
    id: 'gpt-3.5-turbo',
    name: 'GPT-3.5 Turbo',
    task_type: 'simple', // <-- AÑADIDO
  },
  {
    provider: 'deepseek',
    id: 'deepseek-chat',
    name: 'DeepSeek Chat',
    task_type: 'simple', // <-- AÑADIDO
  },
  {
    provider: 'deepseek',
    id: 'deepseek-coder',
    name: 'DeepSeek Coder', // Asumamos que es para tareas complejas
    task_type: 'complex', // <-- AÑADIDO
  },
  {
    provider: 'xai',
    id: 'grok-3-fast',
    name: 'Grok 3 Fast',
    task_type: 'simple',
    comingSoon: true,
  },
  {
    provider: 'xai',
    id: 'grok-4',
    name: 'Grok 4',
    task_type: 'complex',
    comingSoon: true,
  },
];