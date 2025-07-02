from sqlalchemy.orm import Session
from . import models, schemas, auth
from typing import List 

# --- User CRUD ---
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Bot CRUD ---
def get_bots_by_user(db: Session, user_id: int):
    return db.query(models.Bot).filter(models.Bot.owner_id == user_id).all()

def create_user_bot(db: Session, bot: schemas.BotCreate, user_id: int):
    # Aseguramos que todos los campos del schema se pasen correctamente al modelo
    db_bot = models.Bot(
        name=bot.name,
        description=bot.description,
        system_prompt=bot.system_prompt,
        owner_id=user_id
    )
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot

def update_bot(db: Session, bot: models.Bot, bot_update: schemas.BotUpdate):
    update_data = bot_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(bot, key, value)
    db.commit()
    db.refresh(bot)
    return bot

def delete_bot(db: Session, bot_id: int):
    db_bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if db_bot:
        db.delete(db_bot)
        db.commit()
    return db_bot

def get_bot(db: Session, bot_id: int, user_id: int):
    return db.query(models.Bot).filter(models.Bot.id == bot_id, models.Bot.owner_id == user_id).first()

# --- BotModelConfig CRUD ---
def add_model_config_to_bot(db: Session, config: schemas.BotModelConfigCreate, bot_id: int):
    db_config = models.BotModelConfig(**config.dict(), bot_id=bot_id)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def delete_bot_model_config(db: Session, model_config_id: int):
    db_config = db.query(models.BotModelConfig).filter(models.BotModelConfig.id == model_config_id).first()
    if db_config:
        db.delete(db_config)
        db.commit()
    return db_config

def get_documents_by_bot(db: Session, bot_id: int, skip: int = 0, limit: int = 100) -> List[models.Document]:
    """
    Obtiene todos los documentos asociados a un bot.
    """
    return db.query(models.Document).filter(models.Document.bot_id == bot_id).offset(skip).limit(limit).all()

def create_bot_document(db: Session, doc: schemas.DocumentCreate) -> models.Document:
    """
    Crea un nuevo registro de documento para un bot.
    """
    db_doc = models.Document(
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        bot_id=doc.bot_id,
        status=models.DocumentStatus.PENDING # Estado inicial
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def update_document_status(db: Session, doc_id: int, status: models.DocumentStatus):
    """
    Actualiza el estado de un documento.
    """
    db_doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if db_doc:
        db_doc.status = status
        db.commit()
        db.refresh(db_doc)
    return db_doc