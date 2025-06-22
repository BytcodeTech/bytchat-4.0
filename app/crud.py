from sqlalchemy.orm import Session
from . import models, schemas, auth 

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_bots_by_user(db: Session, user_id: int):
    return db.query(models.Bot).filter(models.Bot.owner_id == user_id).all()

def create_user_bot(db: Session, bot: schemas.BotCreate, user_id: int):
    db_bot = models.Bot(**bot.model_dump(), owner_id=user_id)
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot

# --- NUEVA FUNCIÓN PARA ACTUALIZAR BOTS ---
def update_bot_config(db: Session, bot: models.Bot, config: schemas.BotConfigUpdate):
    """
    Actualiza la configuración de un bot en la base de datos.
    """
    # Obtenemos los datos del schema de actualización
    update_data = config.model_dump(exclude_unset=True)
    
    # Actualizamos los campos del objeto 'bot' de la base de datos
    for key, value in update_data.items():
        setattr(bot, key, value)
        
    db.add(bot)
    db.commit()
    db.refresh(bot)
    return bot
