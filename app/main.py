import os
import shutil
from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, File, Response, Path, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime

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

# Montar la carpeta de archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

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

@app.get("/users/me/", response_model=schemas.User, tags=["Users"])
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.put("/users/me/password/", response_model=schemas.User, tags=["Users"])
def change_user_password(
    password_update: schemas.PasswordUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Cambia la contraseña del usuario actual"""
    return crud.change_user_password(db=db, user_id=current_user.id, password_update=password_update)

# === Endpoints de Administración de Usuarios ===
@app.get("/admin/users/", response_model=List[schemas.UserAdmin], tags=["Admin"])
def get_all_users_admin(db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin_role)):
    """Obtiene todos los usuarios (solo para administradores)"""
    return crud.get_all_users(db)

@app.get("/admin/users/pending/", response_model=List[schemas.UserAdmin], tags=["Admin"])
def get_pending_users_admin(db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin_role)):
    """Obtiene usuarios pendientes de aprobación"""
    return crud.get_pending_users(db)

@app.post("/admin/users/{user_id}/approve/", response_model=schemas.UserAdmin, tags=["Admin"])
def approve_user_admin(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.require_admin_role)
):
    """Aprueba un usuario manualmente"""
    return crud.approve_user(db, user_id=user_id, approved_by=current_user.email)

@app.post("/admin/users/{user_id}/reject/", response_model=schemas.UserAdmin, tags=["Admin"])
def reject_user_admin(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.require_admin_role)
):
    """Rechaza un usuario"""
    return crud.reject_user(db, user_id=user_id)

@app.put("/admin/users/{user_id}/status/", response_model=schemas.UserAdmin, tags=["Admin"])
def update_user_status_admin(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin_role)
):
    """Actualiza el estado de un usuario"""
    return crud.update_user_status(db, user_id=user_id, user_update=user_update)

# === Endpoints de Super Administración ===
@app.post("/admin/users/{user_id}/role/", response_model=schemas.UserAdmin, tags=["Super Admin"])
def update_user_role_admin(
    user_id: int,
    role_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_super_admin_role)
):
    """Actualiza el rol de un usuario (solo super administradores)"""
    return crud.update_user_role(db, user_id=user_id, role_update=role_update)

@app.post("/admin/users/{user_id}/toggle-approval/", response_model=schemas.UserAdmin, tags=["Super Admin"])
def toggle_user_approval_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_super_admin_role)
):
    """Cambia el estado de aprobación de un usuario (solo super administradores)"""
    return crud.toggle_user_approval(db, user_id=user_id, toggled_by=current_user.email)


# --- Función auxiliar para obtener un bot de un usuario específico ---
def get_bot(db: Session, bot_id: int, user_id: int):
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id, models.Bot.owner_id == user_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot no encontrado o no tienes permiso")
    return bot

# === Endpoints para la Gestión de Bots (Protegidos) ===
@app.post("/bots/", response_model=schemas.Bot, tags=["Bots"])
def create_bot_for_user(bot: schemas.BotCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_user_bot(db=db, bot=bot, user_id=current_user.id)

@app.get("/bots/", response_model=List[schemas.Bot], tags=["Bots"])
def read_user_bots(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    bots = crud.get_bots_by_user(db, user_id=current_user.id)
    return bots

# El endpoint de PUT ahora usa la función de autenticación correcta
@app.put("/bots/{bot_id}", response_model=schemas.Bot, tags=["Bots"])
def update_bot_details(
    bot_id: int,
    bot_update: schemas.BotUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    db_bot = get_bot(db, bot_id=bot_id, user_id=current_user.id)
    return crud.update_bot(db=db, bot=db_bot, bot_update=bot_update)

@app.delete("/bots/{bot_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Bots"])
def delete_bot(bot_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_bot = get_bot(db=db, bot_id=bot_id, user_id=current_user.id)
    crud.delete_bot(db=db, bot_id=db_bot.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/bots/{bot_id}/models/", response_model=schemas.BotModelConfig, tags=["Bots"])
def add_model_to_bot(
    bot_id: int,
    model_config: schemas.BotModelConfigCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    bot = get_bot(db=db, bot_id=bot_id, user_id=current_user.id)
    return crud.add_model_config_to_bot(db=db, config=model_config, bot_id=bot_id)

@app.delete("/bots/{bot_id}/models/{model_config_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Bots"])
def remove_model_from_bot(
    bot_id: int,
    model_config_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    bot = get_bot(db=db, bot_id=bot_id, user_id=current_user.id)
    model_config = db.query(models.BotModelConfig).filter(
        models.BotModelConfig.id == model_config_id,
        models.BotModelConfig.bot_id == bot_id
    ).first()

    if not model_config:
        raise HTTPException(status_code=404, detail="Configuración de modelo no encontrada para este bot")

    crud.delete_bot_model_config(db=db, model_config_id=model_config_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/bots/{bot_id}/train", tags=["Bots"])
def train_bot_with_document(
    bot_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    bot = get_bot(db=db, bot_id=bot_id, user_id=current_user.id)

    upload_folder = "temp_uploads"
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, f"{bot_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    task = celery_app.send_task('process_and_index_documents_task', args=[bot_id, file_path])
    
    return {"message": f"Archivo '{file.filename}' recibido para el bot {bot_id}. El entrenamiento ha comenzado.", "task_id": task.id}

# === Endpoint de Chat (CORREGIDO) ===

@app.post("/chat/{bot_id}", tags=["Chat"])
async def handle_chat(
    bot_id: int, 
    chat_query: schemas.ChatQuery,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    bot = crud.get_bot(db=db, bot_id=bot_id, user_id=current_user.id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot no encontrado o no tienes permiso.")

    # Usamos model_dump() para convertir el objeto a un diccionario de forma segura
    bot_config_dict = schemas.Bot.from_orm(bot).model_dump()

    # Le pasamos la sesión 'db' al crear el orquestador
    orchestrator = Orchestrator(db=db, bot_config=bot_config_dict, bot_id=bot_id)

    text_stream_generator = orchestrator.handle_query(
        user_id=str(current_user.id), 
        query=chat_query.query
    )

    return StreamingResponse(text_stream_generator, media_type="text/plain; charset=utf-8")
    

# === Endpoints para Gestión de Documentos (Entrenamiento) ===

@app.get("/bots/{bot_id}/documents/", response_model=List[schemas.Document], tags=["Bots"])
def read_bot_documents(
    bot_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Obtiene la lista de documentos de un bot específico.
    """
    bot = get_bot(db, bot_id=bot_id, user_id=current_user.id)
    return crud.get_documents_by_bot(db=db, bot_id=bot.id)


# Este endpoint reemplaza y mejora el endpoint de /train que tenías
@app.post("/bots/{bot_id}/documents/upload", response_model=schemas.Document, tags=["Bots"])
def upload_document_for_training(
    bot_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Sube un archivo, crea el registro del documento y lanza la tarea de entrenamiento.
    """
    bot = get_bot(db, bot_id=bot_id, user_id=current_user.id)
    
    # 1. Crear el registro del documento en la BD
    doc_in = schemas.DocumentCreate(
        filename=file.filename,
        file_type=file.content_type,
        file_size=file.size,
        bot_id=bot_id
    )
    db_document = crud.create_bot_document(db=db, doc=doc_in)

    # 2. Guardar el archivo físicamente
    upload_folder = f"temp_uploads/{bot_id}"
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, f"doc_{db_document.id}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Lanzar la tarea de Celery
    task = celery_app.send_task('process_document_task', args=[bot_id, file_path, db_document.id])
    
    return db_document

@app.delete("/bots/{bot_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Bots"])
def delete_bot_document(
    bot_id: int,
    document_id: int = Path(..., description="ID del documento a eliminar"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    bot = get_bot(db, bot_id=bot_id, user_id=current_user.id)
    doc = db.query(models.Document).filter(models.Document.id == document_id, models.Document.bot_id == bot_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado para este bot")
    # Eliminar archivo físico e índice si existen
    if doc.vector_index_path and os.path.exists(doc.vector_index_path):
        if os.path.isdir(doc.vector_index_path):
            shutil.rmtree(doc.vector_index_path)
        else:
            os.remove(doc.vector_index_path)
    # Si en el futuro se agrega file_path al modelo Document, este bloque lo manejará
    if hasattr(doc, 'file_path') and doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    db.delete(doc)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post("/chat-public/{bot_id}", tags=["Chat"])
def handle_public_chat(
    bot_id: int,
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint público para el widget de chat. Recibe userAnonId y mensaje.
    Guarda la métrica y responde usando el bot.
    """
    user_anon_id = data.get('userAnonId')
    query = data.get('query')
    if not user_anon_id or not query:
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios")
    # Guardar la métrica básica (puedes expandir esto según tus necesidades)
    with open('chat_metrics.log', 'a') as f:
        f.write(f"{datetime.utcnow().isoformat()} | bot_id={bot_id} | userAnonId={user_anon_id} | mensaje={query}\n")
    # Obtener el bot (sin autenticación)
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot no encontrado")
    bot_config_dict = schemas.Bot.from_orm(bot).model_dump()
    orchestrator = Orchestrator(db=db, bot_config=bot_config_dict, bot_id=bot_id)
    # Procesar la consulta
    text_stream_generator = orchestrator.handle_query(
        user_id=str(user_anon_id),
        query=query
    )
    return StreamingResponse(text_stream_generator, media_type="text/plain; charset=utf-8")

