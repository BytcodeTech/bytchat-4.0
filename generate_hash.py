#!/usr/bin/env python3

from passlib.context import CryptContext

# Crear el contexto para el hashing de contraseñas (igual que en security.py)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    """Genera el hash de una contraseña."""
    return pwd_context.hash(password)

# Generar hash para la contraseña del super admin
password = "superagente123"
hash_password = get_password_hash(password)

print(f"Contraseña: {password}")
print(f"Hash: {hash_password}") 