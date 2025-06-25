from passlib.context import CryptContext

# Creamos el contexto para el hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Verifica una contraseña plana contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Genera el hash de una contraseña."""
    return pwd_context.hash(password)