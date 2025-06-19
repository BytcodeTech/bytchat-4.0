from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

# Importamos la clase Base desde nuestro archivo de base de datos
# Todos nuestros modelos heredarán de esta clase
from .database import Base

class User(Base):
    __tablename__ = "users" # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # Esta es la relación: Un usuario puede tener muchos bots.
    # 'back_populates' le dice a SQLAlchemy cómo conectar esta relación
    # con la relación en el modelo Bot.
    bots = relationship("Bot", back_populates="owner")


class Bot(Base):
    __tablename__ = "bots" # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)

    # Clave foránea: Esta columna conecta cada bot con un usuario.
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Esta es la otra parte de la relación: Un bot pertenece a un 'owner' (dueño).
    owner = relationship("User", back_populates="bots")
