from sqlalchemy.orm import Session
# Importamos nuestros módulos.
from . import models, schemas, auth 

def get_user_by_email(db: Session, email: str):
    """
    Busca y devuelve un usuario por su email.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Crea un nuevo usuario en la base de datos con contraseña encriptada.
    """
    # --- ¡ESTA ES LA LÍNEA CORREGIDA! ---
    # En lugar de añadir "_hashed", ahora llamamos a la función
    # de encriptación real desde nuestro módulo de auth.
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
    """
    Obtiene todos los bots que pertenecen a un usuario específico.
    """
    return db.query(models.Bot).filter(models.Bot.owner_id == user_id).all()

def create_user_bot(db: Session, bot: schemas.BotCreate, user_id: int):
    """
    Crea un nuevo bot para un usuario específico.
    """
    db_bot = models.Bot(**bot.model_dump(), owner_id=user_id)
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot
