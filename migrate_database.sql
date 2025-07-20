-- Migración para agregar sistema de BytTokens
-- Ejecutar en la base de datos PostgreSQL

-- 1. Agregar columnas de BytTokens a user_plans
ALTER TABLE user_plans 
ADD COLUMN IF NOT EXISTS bytokens_included INTEGER DEFAULT 2000,
ADD COLUMN IF NOT EXISTS bytokens_remaining INTEGER DEFAULT 2000;

-- 2. Agregar columna de BytTokens a token_usage  
ALTER TABLE token_usage 
ADD COLUMN IF NOT EXISTS bytokens_cost INTEGER DEFAULT 0;

-- 3. Actualizar planes existentes con valores por defecto según su tipo
UPDATE user_plans 
SET bytokens_included = CASE 
    WHEN plan_type = 'FREE' THEN 2000
    WHEN plan_type = 'PRO' THEN 13000
    WHEN plan_type = 'ENTERPRISE' THEN 80000
    ELSE 2000
END
WHERE bytokens_included = 2000;

-- 4. Mantener el porcentaje de uso actual para bytokens_remaining
UPDATE user_plans 
SET bytokens_remaining = CASE 
    WHEN tokens_included > 0 THEN 
        CAST(bytokens_included * (tokens_remaining::FLOAT / tokens_included::FLOAT) AS INTEGER)
    ELSE bytokens_included
END
WHERE bytokens_remaining = 2000;

-- 5. Calcular BytTokens para registros existentes de token_usage (estimación básica)
UPDATE token_usage 
SET bytokens_cost = GREATEST(1, total_tokens / 1000)
WHERE bytokens_cost = 0;

-- Verificar cambios
SELECT 
    'user_plans' as table_name,
    plan_type,
    COUNT(*) as count,
    AVG(bytokens_included) as avg_bytokens_included,
    AVG(bytokens_remaining) as avg_bytokens_remaining
FROM user_plans 
GROUP BY plan_type
UNION ALL
SELECT 
    'token_usage' as table_name,
    'all' as plan_type,
    COUNT(*) as count,
    AVG(bytokens_cost) as avg_bytokens_included,
    SUM(bytokens_cost) as avg_bytokens_remaining
FROM token_usage 
WHERE bytokens_cost > 0; 