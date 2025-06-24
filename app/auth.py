from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import crud, models
from .database import get_db

# --- Configuración de Seguridad ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "un_secreto_muy_secreto_para_el_token"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Funciones de Contraseña ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --- Funciones de Token (JWT) ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Lógica para obtener el usuario actual a partir del Token ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# --- NUEVA FUNCIÓN AÑADIDA ---
def get_current_user_or_none(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[models.User]:
    """
    Intenta obtener el usuario actual. Si el token no es válido o no existe,
    en lugar de lanzar una excepción, devuelve None.
    Esto es útil para endpoints que pueden ser accedidos por usuarios logueados y no logueados.
    """
    try:
        # Reutiliza la lógica de get_current_user
        return get_current_user(token, db)
    except HTTPException:
        # Si get_current_user lanza una excepción de credenciales, simplemente devuelve None
        return None
