-- Script para actualizar los modelos activos según los que realmente usa la plataforma
-- Ejecutar en la base de datos PostgreSQL

-- Primero, desactivar TODOS los modelos
UPDATE model_pricing SET is_active = FALSE WHERE TRUE;

-- Luego, activar solo los modelos que realmente se usan
-- Basado en la interfaz mostrada por el usuario

-- ✅ ACTIVAR: OpenAI - GPT-4o (Tarea Complex)
UPDATE model_pricing 
SET is_active = TRUE, 
    updated_by = 'admin_config',
    updated_at = NOW()
WHERE model_id = 'gpt-4o' AND provider = 'openai';

-- ✅ ACTIVAR: OpenAI - GPT-3.5 Turbo (Tarea Simple) 
UPDATE model_pricing 
SET is_active = TRUE,
    display_name = 'GPT-3.5 Turbo',
    model_id = 'gpt-3.5-turbo',
    input_cost_per_1k = 0.001,
    output_cost_per_1k = 0.002,
    updated_by = 'admin_config',
    updated_at = NOW()
WHERE model_id IN ('gpt-3.5-turbo', 'gpt-4-turbo') AND provider = 'openai'
   OR (provider = 'openai' AND display_name LIKE '%Turbo%');

-- ✅ ACTIVAR: Google - Gemini 1.5 Pro (Tarea Complex)
UPDATE model_pricing 
SET is_active = TRUE,
    display_name = 'Gemini 1.5 Pro',
    model_id = 'gemini-1.5-pro', 
    input_cost_per_1k = 0.0035,
    output_cost_per_1k = 0.0105,
    updated_by = 'admin_config',
    updated_at = NOW()
WHERE model_id IN ('gemini-pro', 'gemini-1.5-pro') AND provider = 'google'
   OR (provider = 'google' AND display_name LIKE '%Pro%');

-- ✅ ACTIVAR: Google - Gemini 1.5 Flash (Tarea Simple)
UPDATE model_pricing 
SET is_active = TRUE,
    display_name = 'Gemini 1.5 Flash',
    model_id = 'gemini-1.5-flash',
    input_cost_per_1k = 0.000075,
    output_cost_per_1k = 0.0003,
    updated_by = 'admin_config',
    updated_at = NOW()
WHERE model_id IN ('gemini-flash', 'gemini-1.5-flash') AND provider = 'google'
   OR (provider = 'google' AND display_name LIKE '%Flash%');

-- ✅ ACTIVAR: DeepSeek - DeepSeek Chat (Tarea Simple)
UPDATE model_pricing 
SET is_active = TRUE,
    display_name = 'DeepSeek Chat',
    model_id = 'deepseek-chat',
    input_cost_per_1k = 0.00014,
    output_cost_per_1k = 0.00028,
    updated_by = 'admin_config',
    updated_at = NOW()
WHERE model_id IN ('deepseek-v2', 'deepseek-chat') AND provider = 'deepseek'
   OR (provider = 'deepseek' AND (display_name LIKE '%Chat%' OR display_name LIKE '%V2%'));

-- ✅ ACTIVAR: DeepSeek - DeepSeek Coder (Tarea Complex)
INSERT INTO model_pricing (provider, model_id, display_name, input_cost_per_1k, output_cost_per_1k, is_active, updated_by)
VALUES ('deepseek', 'deepseek-coder', 'DeepSeek Coder', 0.00014, 0.00028, TRUE, 'admin_config')
ON CONFLICT (provider, model_id) 
DO UPDATE SET 
    is_active = TRUE,
    display_name = 'DeepSeek Coder',
    input_cost_per_1k = 0.00014,
    output_cost_per_1k = 0.00028,
    updated_by = 'admin_config',
    updated_at = NOW();

-- Agregar GPT-3.5 Turbo si no existe
INSERT INTO model_pricing (provider, model_id, display_name, input_cost_per_1k, output_cost_per_1k, is_active, updated_by)
VALUES ('openai', 'gpt-3.5-turbo', 'GPT-3.5 Turbo', 0.001, 0.002, TRUE, 'admin_config')
ON CONFLICT (provider, model_id) 
DO UPDATE SET 
    is_active = TRUE,
    display_name = 'GPT-3.5 Turbo',
    input_cost_per_1k = 0.001,
    output_cost_per_1k = 0.002,
    updated_by = 'admin_config',
    updated_at = NOW();

-- Verificar resultado final
SELECT 
    provider,
    model_id,
    display_name,
    input_cost_per_1k,
    output_cost_per_1k,
    is_active,
    updated_by
FROM model_pricing 
ORDER BY provider, is_active DESC, display_name; 