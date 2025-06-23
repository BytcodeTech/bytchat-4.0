from pydantic import BaseModel
from typing import List, Optional

# --- Nuevos Schemas para la Configuración de Modelos ---

class BotModelConfigBase(BaseModel):
    task_type: str = "general"
    provider: str
    model_id: str
    is_active: bool = True

class BotModelConfigCreate(BotModelConfigBase):
    pass 

class BotModelConfig(BotModelConfigBase):
    id: int
    bot_id: int
    class Config:
        from_attributes = True

# --- Schema para actualizar el prompt de un bot ---
# (Lo mantendremos separado por si quieres actualizar solo el prompt)
class BotConfigUpdate(BaseModel):
    system_prompt: Optional[str] = None

# --- Schemas de Bot Actualizados ---

class BotBase(BaseModel):
    name: str
    description: Optional[str] = None

class BotCreate(BotBase):
    # Opcionalmente, podemos pasar una lista de configuraciones al crear el bot
    initial_configs: Optional[List[BotModelConfigCreate]] = None

class Bot(BotBase):
    id: int
    owner_id: int
    system_prompt: str
    # Ahora, un bot tiene una lista de configuraciones de modelos
    model_configs: List[BotModelConfig] = []

    class Config:
        from_attributes = True

# --- El resto del archivo se mantiene igual ---
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

class TokenData(BaseModel):
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
