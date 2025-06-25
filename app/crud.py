from sqlalchemy.orm import Session
from . import models, schemas
# Importamos desde el nuevo archivo de seguridad, no desde auth.py
from .security import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    # Usamos la función importada desde security.py
    hashed_password = get_password_hash(user.password)
    # Corregido: Se eliminó el campo 'full_name' que no existe en el modelo
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_bots_by_user(db: Session, user_id: int):
    return db.query(models.Bot).filter(models.Bot.owner_id == user_id).all()

def create_user_bot(db: Session, bot: schemas.BotCreate, user_id: int):
    bot_data = bot.model_dump(exclude_unset=True)
    db_bot = models.Bot(**bot_data, owner_id=user_id)
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot

def update_bot_config(db: Session, bot: models.Bot, config: schemas.BotConfigUpdate):
    update_data = config.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(bot, key, value)
    db.add(bot)
    db.commit()
    db.refresh(bot)
    return bot

def add_model_config_to_bot(db: Session, config: schemas.BotModelConfigCreate, bot_id: int):
    db_config = models.BotModelConfig(**config.model_dump(), bot_id=bot_id)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def delete_bot(db: Session, bot_id: int):
    bot_to_delete = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if bot_to_delete:
        db.delete(bot_to_delete)
        db.commit()
    return bot_to_delete

def delete_bot_model_config(db: Session, model_config_id: int):
    model_config_to_delete = db.query(models.BotModelConfig).filter(models.BotModelConfig.id == model_config_id).first()
    if model_config_to_delete:
        db.delete(model_config_to_delete)
        db.commit()
    return model_config_to_delete