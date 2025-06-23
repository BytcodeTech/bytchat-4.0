from sqlalchemy.orm import Session
from . import models, schemas, auth 

def get_user_by_email(db: Session, email: str):
    """Busca y devuelve un usuario por su email."""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Crea un nuevo usuario en la base de datos con contraseña encriptada."""
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_bots_by_user(db: Session, user_id: int):
    """Obtiene todos los bots que pertenecen a un usuario específico."""
    return db.query(models.Bot).filter(models.Bot.owner_id == user_id).all()

def create_user_bot(db: Session, bot: schemas.BotCreate, user_id: int):
    """
    Crea un nuevo bot.
    """
    bot_data = bot.model_dump(exclude_unset=True)
    db_bot = models.Bot(**bot_data, owner_id=user_id)
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot

# --- FUNCIÓN QUE FALTABA ---
def update_bot_config(db: Session, bot: models.Bot, config: schemas.BotConfigUpdate):
    """
    Actualiza la configuración de un bot existente en la base de datos.
    """
    # Convierte el schema a un diccionario, excluyendo los campos que no se enviaron
    update_data = config.model_dump(exclude_unset=True)
    
    # Itera sobre los datos enviados y actualiza el objeto 'bot' de la base de datos
    for key, value in update_data.items():
        setattr(bot, key, value)
        
    db.add(bot)
    db.commit()
    db.refresh(bot)
    return bot

def add_model_config_to_bot(db: Session, config: schemas.BotModelConfigCreate, bot_id: int):
    """
    Añade una nueva configuración de modelo a un bot existente (una nueva 'herramienta').
    """
    db_config = models.BotModelConfig(**config.model_dump(), bot_id=bot_id)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config
