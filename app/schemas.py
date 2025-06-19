from pydantic import BaseModel
from typing import List, Optional

class BotBase(BaseModel):
    name: str
    description: Optional[str] = None

class BotCreate(BotBase):
    pass

class Bot(BotBase):
    id: int
    owner_id: int
    class Config:
        from_attributes = True

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