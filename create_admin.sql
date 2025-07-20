-- Verificar usuarios existentes
SELECT email, is_active, is_approved, role FROM users;

-- Insertar usuario administrador si no existe
INSERT INTO users (email, hashed_password, is_active, is_approved, role, created_at)
SELECT 
    'admin@bytcode.tech',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- hash de 'superagente123'
    true,
    true,
    'SUPER_ADMIN',
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE email = 'admin@bytcode.tech'
);

-- Verificar que se creó correctamente
SELECT email, is_active, is_approved, role FROM users WHERE email = 'admin@bytcode.tech'; 