from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .models import DocumentStatus # Importar el Enum


# --- Schemas de BotModelConfig ---
class BotModelConfigBase(BaseModel):
    provider: str = Field(..., example="google")
    model_id: str = Field(..., example="gemini-1.5-pro-latest")
    task_type: str = "general" # Campo añadido para la lógica del frontend

class BotModelConfigCreate(BotModelConfigBase):
    pass

class BotModelConfig(BotModelConfigBase):
    id: int
    bot_id: int
    class Config:
        from_attributes = True 

class DocumentBase(BaseModel):
    filename: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None

class DocumentCreate(DocumentBase):
    bot_id: int

class DocumentUpdate(BaseModel):
    status: Optional[DocumentStatus] = None
    vector_index_path: Optional[str] = None
    chunks_map_path: Optional[str] = None

class Document(DocumentBase):
    id: int
    bot_id: int
    status: DocumentStatus
    uploaded_at: datetime
    vector_index_path: Optional[str] = None
    chunks_map_path: Optional[str] = None

    class Config:
        from_attributes = True # Cambiado de orm_mode


# --- Schemas de Bot ---
class BotBase(BaseModel):
    name: str = Field(..., example="Asistente de Ventas")
    description: Optional[str] = Field(None, example="Un bot para ayudar con las ventas")
    system_prompt: Optional[str] = Field("Eres un asistente de IA muy servicial.", example="Eres un experto en ventas de coches.")

class BotCreate(BotBase):
    pass

class BotUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None

class Bot(BotBase):
    id: int
    owner_id: int
    system_prompt: str
    model_configs: List[BotModelConfig] = [] 
    documents: List[Document] = [] 
    class Config:
        from_attributes = True  # Cambiado de orm_mode

# --- Schemas de User ---
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    bots: List[Bot] = []
    class Config:
        from_attributes = True

# --- Schemas de Token y Chat ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ChatQuery(BaseModel):
    query: str