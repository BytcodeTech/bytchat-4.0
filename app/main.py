from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
from fastapi import UploadFile, File

from . import auth, crud, models, schemas
from .database import engine, get_db
from .core.orchestrator import Orchestrator
from .worker import celery_app

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bytchat SaaS API",
    description="API para la plataforma multi-tenant de Bytchat.",
    version="1.2.1" # Subimos la versión!
)

# === Endpoints de Autenticación y Usuarios ===
@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# === Endpoints para la Gestión de Bots (Protegidos) ===
@app.post("/bots/", response_model=schemas.Bot, tags=["Bots"])
def create_bot_for_user(bot: schemas.BotCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_user_bot(db=db, bot=bot, user_id=current_user.id)

@app.get("/bots/", response_model=List[schemas.Bot], tags=["Bots"])
def read_user_bots(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    bots = crud.get_bots_by_user(db, user_id=current_user.id)
    return bots

# --- ENDPOINT PARA CONFIGURAR EL PROMPT (RESTAURADO) ---
@app.put("/bots/{bot_id}", response_model=schemas.Bot, tags=["Bots"])
def configure_bot_prompt(
    bot_id: int,
    config: schemas.BotConfigUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Actualiza la configuración general de un bot (como su system_prompt).
    """
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if not bot or bot.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bot no encontrado o no tienes permiso")
    
    return crud.update_bot_config(db=db, bot=bot, config=config)

# --- ENDPOINT PARA AÑADIR UN MODELO A LA CAJA DE HERRAMIENTAS ---
@app.post("/bots/{bot_id}/models/", response_model=schemas.BotModelConfig, tags=["Bots"])
def add_model_to_bot(
    bot_id: int,
    model_config: schemas.BotModelConfigCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Añade una nueva configuración de modelo (una 'herramienta') a la caja de un bot.
    """
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if not bot or bot.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bot no encontrado o no tienes permiso")
    
    return crud.add_model_config_to_bot(db=db, config=model_config, bot_id=bot_id)

# --- Endpoint de Entrenamiento (Protegido) ---
@app.post("/bots/{bot_id}/train", tags=["Bots"])
def train_bot_with_document(
    bot_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Permite subir un documento de texto (.txt) para entrenar a un bot.
    """
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if not bot or bot.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bot no encontrado o no tienes permiso")

    upload_folder = "temp_uploads"
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, f"{bot_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    task = celery_app.send_task('process_and_index_documents_task', args=[bot_id, file_path])
    
    return {"message": f"Archivo '{file.filename}' recibido para el bot {bot_id}. El entrenamiento ha comenzado.", "task_id": task.id}


# === Endpoint de Chat (Aún no actualizado a la nueva lógica) ===
@app.post("/chat/{bot_id}", tags=["Chat"])
def handle_chat(
    bot_id: int, 
    query: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot no encontrado")
    if bot.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso")

    return {"message": f"La lógica de chat para el bot {bot.name} aún no está implementada con la 'caja de herramientas'."}

# === Endpoint de Bienvenida ===
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a la API de Bytchat SaaS v1.2.1. Ve a /docs para ver la documentación interactiva."}
