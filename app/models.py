from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    bots = relationship("Bot", back_populates="owner")


class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    
    # --- NUEVAS COLUMNAS PARA PERSONALIZACIÓN ---

    # El 'prompt' o personalidad base del bot.
    system_prompt = Column(Text, default="Eres un asistente de IA servicial.")

    # El modelo para tareas simples (ej. 'gemini-1.5-flash-latest')
    simple_model_id = Column(String, default="gemini-1.5-flash-latest")

    # El modelo para tareas complejas (ej. 'gpt-4o')
    complex_model_id = Column(String, default="gemini-1.5-pro-latest")
    
    # --- FIN DE LAS NUEVAS COLUMNAS ---
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="bots")
