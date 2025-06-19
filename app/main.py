# --- Imports de FastAPI y Python ---
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

# --- Imports de nuestra aplicación ---
# Traemos todos los módulos que hemos creado
from . import auth, crud, models, schemas
from .database import SessionLocal, engine, get_db

# --- Creación de la Base de Datos ---
# Si las tablas no existen, esta línea las creará al iniciar
models.Base.metadata.create_all(bind=engine)

# --- Inicialización de la Aplicación ---
app = FastAPI(
    title="Bytchat SaaS API",
    description="API para la plataforma multi-tenant de Bytchat.",
    version="2.0.0"
)

# --- Endpoints de Autenticación y Usuarios ---

@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Inicia sesión para obtener un token de acceso.
    """
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}


# --- ¡ESTA ES LA FUNCIÓN CORREGIDA! ---
@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario. Ahora espera un JSON con email y password.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/me/", response_model=schemas.User, tags=["Users"])
def read_users_me():
    """
    Endpoint protegido de ejemplo.
    """
    return {"email": "user@example.com", "id": 1, "is_active": True, "bots": []}


# --- Endpoint de Bienvenida ---
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a la API de Bytchat SaaS. Ve a /docs para ver la documentación interactiva."}