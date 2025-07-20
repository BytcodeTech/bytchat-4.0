-- Migración para sistema de gestión de precios de modelos
-- Ejecutar en la base de datos PostgreSQL

-- 1. Crear tabla model_pricing
CREATE TABLE IF NOT EXISTS model_pricing (
    id SERIAL PRIMARY KEY,
    provider VARCHAR NOT NULL,
    model_id VARCHAR NOT NULL,
    display_name VARCHAR NOT NULL,
    input_cost_per_1k FLOAT NOT NULL DEFAULT 0.001,
    output_cost_per_1k FLOAT NOT NULL DEFAULT 0.001,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_by VARCHAR
);

-- 2. Crear índice único para provider + model_id
CREATE UNIQUE INDEX IF NOT EXISTS idx_provider_model 
ON model_pricing (provider, model_id);

-- 3. Insertar precios por defecto
INSERT INTO model_pricing (provider, model_id, display_name, input_cost_per_1k, output_cost_per_1k, updated_by) VALUES
-- OpenAI
('openai', 'gpt-4o', 'GPT-4o', 0.005, 0.015, 'system_init'),
('openai', 'gpt-4o-mini', 'GPT-4o Mini', 0.00015, 0.0006, 'system_init'),
('openai', 'gpt-4-turbo', 'GPT-4 Turbo', 0.01, 0.03, 'system_init'),
('openai', 'o1-preview', 'o1-preview', 0.015, 0.06, 'system_init'),
('openai', 'o1-mini', 'o1-mini', 0.003, 0.012, 'system_init'),

-- Google Gemini
('google', 'gemini-pro', 'Gemini Pro', 0.0015, 0.0015, 'system_init'),
('google', 'gemini-flash', 'Gemini Flash', 0.00015, 0.0006, 'system_init'),
('google', 'gemini-ultra', 'Gemini Ultra', 0.003, 0.003, 'system_init'),

-- DeepSeek
('deepseek', 'deepseek-v2', 'DeepSeek V2', 0.0002, 0.0002, 'system_init'),
('deepseek', 'deepseek-reasoner', 'DeepSeek Reasoner', 0.002, 0.002, 'system_init'),

-- Default fallback
('default', 'default', 'Default Model', 0.001, 0.001, 'system_init')

ON CONFLICT (provider, model_id) DO NOTHING;

-- 4. Crear función para actualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 5. Crear trigger para actualizar timestamp automáticamente
DROP TRIGGER IF EXISTS update_model_pricing_updated_at ON model_pricing;
CREATE TRIGGER update_model_pricing_updated_at 
    BEFORE UPDATE ON model_pricing 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Verificar datos insertados
SELECT 
    provider,
    COUNT(*) as models_count,
    AVG(input_cost_per_1k) as avg_input_cost,
    AVG(output_cost_per_1k) as avg_output_cost
FROM model_pricing 
WHERE is_active = true
GROUP BY provider
ORDER BY provider; 