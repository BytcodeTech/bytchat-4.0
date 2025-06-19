from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# --- Configuración de Seguridad ---
# Le decimos a la librería qué algoritmo de encriptación usar
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Clave secreta para "firmar" los tokens. ¡Debería ser más compleja y guardarse en .env!
SECRET_KEY = "un_secreto_muy_secreto_para_el_token"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # El token será válido por 30 minutos

# --- Funciones de Contraseña ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Comprueba si una contraseña en texto plano coincide con una encriptada."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Devuelve el hash encriptado de una contraseña."""
    return pwd_context.hash(password)

# --- Funciones de Token (JWT) ---
def create_access_token(data: dict) -> str:
    """Crea un nuevo token de acceso."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt