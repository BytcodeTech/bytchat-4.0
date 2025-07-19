from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import crud, models
from .security import verify_password
from .database import get_db
from .models import UserRole

SECRET_KEY = "un_secreto_muy_secreto_para_el_token"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    
    # Verificar que el usuario esté aprobado y activo
    if not user.is_approved or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta está pendiente de aprobación o ha sido desactivada. Contacta al administrador.",
        )
    
    return user

def get_current_user_or_none(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[models.User]:
    try:
        return get_current_user(token, db)
    except HTTPException:
        return None

# === Funciones de Verificación de Permisos ===
def require_admin_role(current_user: models.User = Depends(get_current_user)):
    """Verifica que el usuario tenga rol de administrador o superior"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren permisos de administrador.",
        )
    return current_user

def require_super_admin_role(current_user: models.User = Depends(get_current_user)):
    """Verifica que el usuario tenga rol de super administrador"""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren permisos de super administrador.",
        )
    return current_user

def is_admin(user: models.User) -> bool:
    """Verifica si un usuario es administrador"""
    return user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

def is_super_admin(user: models.User) -> bool:
    """Verifica si un usuario es super administrador"""
    return user.role == UserRole.SUPER_ADMIN
