import os
import shutil
from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# --- Imports de nuestra aplicación ---
from . import auth, crud, models, schemas
from .database import engine, get_db
from .core.orchestrator import Orchestrator
from .worker import celery_app

# Crea las tablas en la base de datos si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bytchat SaaS API",
    description="API para la plataforma multi-tenant de Bytchat.",
    version="1.4.0"
)

# --- CONFIGURACIÓN DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Endpoints de Autenticación y Usuarios ===
@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# --- Función auxiliar para obtener un bot de un usuario específico ---
def get_bot(db: Session, bot_id: int, user_id: int):
    return db.query(models.Bot).filter(models.Bot.id == bot_id, models.Bot.owner_id == user_id).first()

# === Endpoints para la Gestión de Bots (Protegidos) ===
@app.post("/bots/", response_model=schemas.Bot, tags=["Bots"])
def create_bot_for_user(bot: schemas.BotCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_user_bot(db=db, bot=bot, user_id=current_user.id)

@app.get("/bots/", response_model=List[schemas.Bot], tags=["Bots"])
def read_user_bots(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    bots = crud.get_bots_by_user(db, user_id=current_user.id)
    return bots

@app.delete("/bots/{bot_id}", response_model=schemas.Bot, tags=["Bots"])
def delete_bot(bot_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Elimina un bot específico del usuario actual.
    """
    db_bot = get_bot(db=db, bot_id=bot_id, user_id=current_user.id)
    if db_bot is None:
        raise HTTPException(status_code=404, detail="Bot no encontrado o no tienes permiso")
    
    return crud.delete_bot(db=db, bot_id=bot_id)

@app.put("/bots/{bot_id}", response_model=schemas.Bot, tags=["Bots"])
def configure_bot(
    bot_id: int,
    config: schemas.BotConfigUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Actualiza la configuración general de un bot (como su system_prompt).
    """
    bot = get_bot(db=db, bot_id=bot_id, user_id=current_user.id)
    if not bot:
        raise HTTPException(status_code=403, detail="Bot no encontrado o no tienes permiso")
    return crud.update_bot_config(db=db, bot=bot, config=config)

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
    bot = get_bot(db=db, bot_id=bot_id, user_id=current_user.id)
    if not bot:
        raise HTTPException(status_code=403, detail="Bot no encontrado o no tienes permiso")
    return crud.add_model_config_to_bot(db=db, config=model_config, bot_id=bot_id)

# Pega este nuevo endpoint en la sección de Bots de tu archivo app/main.py

@app.delete("/bots/{bot_id}/models/{model_config_id}", response_model=schemas.BotModelConfig, tags=["Bots"])
def remove_model_from_bot(
    bot_id: int,
    model_config_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Elimina una configuración de modelo específica (una 'herramienta') de la caja de un bot.
    """
    # 1. Verificar que el bot pertenece al usuario actual
    bot = get_bot(db=db, bot_id=bot_id, user_id=current_user.id)
    if not bot:
        raise HTTPException(status_code=403, detail="Bot no encontrado o no tienes permiso")

    # 2. Verificar que la configuración del modelo pertenece al bot correcto
    model_config = db.query(models.BotModelConfig).filter(
        models.BotModelConfig.id == model_config_id,
        models.BotModelConfig.bot_id == bot_id
    ).first()

    if not model_config:
        raise HTTPException(status_code=404, detail="Configuración de modelo no encontrada para este bot")

    # 3. Si todo está bien, eliminar la configuración
    deleted_config = crud.delete_bot_model_config(db=db, model_config_id=model_config_id)
    return deleted_config

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
    bot = get_bot(db=db, bot_id=bot_id, user_id=current_user.id)
    if not bot:
        raise HTTPException(status_code=403, detail="Bot no encontrado o no tienes permiso")

    upload_folder = "temp_uploads"
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, f"{bot_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    task = celery_app.send_task('process_and_index_documents_task', args=[bot_id, file_path])
    
    return {"message": f"Archivo '{file.filename}' recibido para el bot {bot_id}. El entrenamiento ha comenzado.", "task_id": task.id}

# === Endpoint de Chat (CORREGIDO) ===
@app.post("/chat/{bot_id}", tags=["Chat"])
def handle_chat(
    bot_id: int, 
    chat_query: schemas.ChatQuery,
    db: Session = Depends(get_db),
    # Aquí estaba el otro typo, ya corregido:
    current_user: models.User = Depends(auth.get_current_user)
):
    bot = get_bot(db=db, bot_id=bot_id, user_id=current_user.id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot no encontrado o no tienes permiso")

    bot_config_dict = schemas.Bot.from_orm(bot).model_dump()
    orchestrator = Orchestrator(bot_config=bot_config_dict, bot_id=bot_id)
    
    text_stream_generator = orchestrator.handle_query(
        user_id=str(current_user.id), 
        query=chat_query.query
    )
    
    return StreamingResponse(text_stream_generator, media_type="text/plain; charset=utf-8")

# === Endpoint de Bienvenida ===
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a la API de Bytchat SaaS v1.4.0. Ve a /docs para ver la documentación interactiva."}
