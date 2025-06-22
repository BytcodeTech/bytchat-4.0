from pydantic import BaseModel
from typing import List, Optional

# --- Esquema para actualizar la configuración de un bot ---
# Todos los campos son opcionales, para que el usuario pueda
# actualizar solo lo que quiera (ej. solo el prompt).
class BotConfigUpdate(BaseModel):
    system_prompt: Optional[str] = None
    simple_model_id: Optional[str] = None
    complex_model_id: Optional[str] = None

# --- Esquemas para el Bot ---
class BotBase(BaseModel):
    name: str
    description: Optional[str] = None

class BotCreate(BotBase):
    pass

class Bot(BotBase):
    id: int
    owner_id: int
    system_prompt: str
    simple_model_id: str
    complex_model_id: str

    class Config:
        from_attributes = True

# --- Esquemas para el Usuario ---
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

# --- Esquema para el Token de Login ---
class TokenData(BaseModel):
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
