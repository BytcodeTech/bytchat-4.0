from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Enum, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base
import enum

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # La relación se mantiene igual aquí
    bots = relationship("Bot", back_populates="owner", cascade="all, delete-orphan")

class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    system_prompt = Column(Text, default="Eres un asistente de IA servicial.")
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="bots")

    # --- LÍNEA CORREGIDA ---
    # Cambiamos 'back_pop_ulates' a 'back_populates'
    model_configs = relationship("BotModelConfig", back_populates="bot", cascade="all, delete-orphan")

    documents = relationship("Document", back_populates="bot", cascade="all, delete-orphan")

class BotModelConfig(Base):
    __tablename__ = "bot_model_configs"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String, default="general") 
    provider = Column(String, nullable=False)
    model_id = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    bot_id = Column(Integer, ForeignKey("bots.id"))
    
    # --- LÍNEA CORREGIDA ---
    # Cambiamos 'back_pop_ulates' a 'back_populates'
    bot = relationship("Bot", back_populates="model_configs")

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, nullable=False)
    file_type = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    
    vector_index_path = Column(String, nullable=True)
    chunks_map_path = Column(String, nullable=True)

    bot_id = Column(Integer, ForeignKey('bots.id'), nullable=False)
    bot = relationship("Bot", back_populates="documents")

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())