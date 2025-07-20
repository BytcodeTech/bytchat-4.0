from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import DocumentStatus, UserRole, PlanType, EventType # Importar el Enum


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
    is_active: bool 
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

class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_approved: Optional[bool] = None
    role: Optional[UserRole] = None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class User(UserBase):
    id: int
    is_active: bool
    is_approved: bool
    role: UserRole
    created_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    bots: List[Bot] = []
    class Config:
        from_attributes = True

class UserAdmin(User):
    """Schema para administradores que pueden ver todos los campos"""
    pass

# --- Schemas de Token y Chat ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ChatQuery(BaseModel):
    query: str

# === NUEVOS SCHEMAS PARA MÉTRICAS Y ANALÍTICAS ===

# --- Schemas de UserPlan ---
class UserPlanBase(BaseModel):
    plan_type: PlanType = PlanType.FREE
    tokens_included: int = 100000  # DEPRECATED
    monthly_price: int = 0
    overage_rate: int = 10
    bytokens_included: int = 2000  # Nuevo sistema

class UserPlanCreate(UserPlanBase):
    user_id: int

class UserPlanUpdate(BaseModel):
    plan_type: Optional[PlanType] = None
    tokens_included: Optional[int] = None  # DEPRECATED
    bytokens_included: Optional[int] = None
    monthly_price: Optional[int] = None
    overage_rate: Optional[int] = None
    current_period_end: Optional[datetime] = None

class UserPlan(UserPlanBase):
    id: int
    user_id: int
    tokens_remaining: int  # DEPRECATED
    bytokens_remaining: int  # Nuevo sistema
    tokens_overage: int  # Ahora representa BytTokens de overage
    overage_cost: int
    started_at: datetime
    current_period_start: datetime
    current_period_end: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# --- Schemas de TokenUsage ---
class TokenUsageBase(BaseModel):
    user_anon_id: Optional[str] = None
    query: str
    provider: str
    model_id: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class TokenUsageCreate(TokenUsageBase):
    user_id: int
    bot_id: int
    prompt_cost: int = 0
    completion_cost: int = 0
    total_cost: int = 0
    bytokens_cost: int = 0  # Nuevo campo
    response_time_ms: Optional[int] = None

class TokenUsage(TokenUsageBase):
    id: int
    user_id: int
    bot_id: int
    prompt_cost: int
    completion_cost: int
    total_cost: int
    bytokens_cost: int  # Nuevo campo
    response_time_ms: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Schemas de BillingRecord ---
class BillingRecordBase(BaseModel):
    period_start: datetime
    period_end: datetime
    plan_cost: int = 0
    overage_cost: int = 0
    total_cost: int = 0

class BillingRecordCreate(BillingRecordBase):
    user_id: int
    tokens_included: int = 0  # DEPRECATED
    tokens_used: int = 0  # DEPRECATED
    tokens_overage: int = 0  # DEPRECATED
    bytokens_included: int = 0  # Nuevo sistema
    bytokens_used: int = 0  # Nuevo sistema
    bytokens_overage: int = 0  # Nuevo sistema

class BillingRecord(BillingRecordBase):
    id: int
    user_id: int
    tokens_included: int  # DEPRECATED
    tokens_used: int  # DEPRECATED
    tokens_overage: int  # DEPRECATED
    bytokens_included: int  # Nuevo sistema
    bytokens_used: int  # Nuevo sistema
    bytokens_overage: int  # Nuevo sistema
    is_paid: bool
    payment_id: Optional[str] = None
    payment_provider: Optional[str] = None
    created_at: datetime
    paid_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# --- Schemas de AnalyticsEvent ---
class AnalyticsEventBase(BaseModel):
    event_type: EventType
    event_data: Optional[str] = None
    user_anon_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AnalyticsEventCreate(AnalyticsEventBase):
    user_id: Optional[int] = None
    bot_id: Optional[int] = None

class AnalyticsEvent(AnalyticsEventBase):
    id: int
    user_id: Optional[int] = None
    bot_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Schemas para Dashboard de Analíticas ---
class UserAnalytics(BaseModel):
    """Dashboard de analíticas para el usuario"""
    # Información del plan
    current_plan: UserPlan
    
    # Métricas de tokens
    tokens_remaining: int
    tokens_used_this_month: int
    tokens_overage: int
    estimated_overage_cost: int  # En centavos
    
    # Uso por IA
    usage_by_provider: dict  # {"openai": 5000, "google": 3000}
    
    # Temas más preguntados (top 5)
    top_topics: List[dict]  # [{"topic": "programación", "count": 15}]
    
    # Actividad diaria últimos 30 días
    daily_usage: List[dict]  # [{"date": "2025-01-01", "tokens": 500}]

class AdminAnalytics(BaseModel):
    """Dashboard de analíticas para administradores"""
    # Métricas generales
    total_users: int
    active_users_last_30_days: int
    total_revenue_this_month: int  # En centavos
    
    # Uso por plan
    users_by_plan: dict  # {"free": 100, "pro": 50, "enterprise": 10}
    
    # Top bots más usados
    top_bots: List[dict]  # [{"bot_name": "Asistente", "usage_count": 1000}]
    
    # Métricas de costos
    total_ai_costs: int  # En centavos
    revenue_by_plan: dict  # {"pro": 50000, "enterprise": 100000}

# --- Schemas para Administración de Usuarios ---
class UserWithPlan(BaseModel):
    """Usuario con información de plan para administradores"""
    id: int
    email: str
    is_active: bool
    is_approved: bool
    role: UserRole
    created_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    
    # Información del plan
    plan: Optional[UserPlan] = None
    
    # Estadísticas de uso
    total_bots: int = 0
    tokens_used_last_30_days: int = 0
    last_activity: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AdminPlanChangeRequest(BaseModel):
    """Solicitud para cambiar plan de usuario"""
    new_plan_type: PlanType
    tokens_to_add: Optional[int] = None  # Tokens adicionales si es necesario
    reset_usage: bool = False  # Si resetear el uso actual

class AdminTokenModification(BaseModel):
    """Solicitud para modificar tokens de usuario"""
    tokens_to_add: int  # Puede ser negativo para quitar tokens
    reason: Optional[str] = None  # Motivo del cambio
    reset_overage: bool = False  # Si resetear el overage actual

class AdminUserPlanResponse(BaseModel):
    """Respuesta después de modificar plan/tokens"""
    success: bool
    message: str
    updated_plan: UserPlan
    previous_values: dict  # Para tracking de cambios

# --- Schemas para ModelPricing ---
class ModelPricingBase(BaseModel):
    provider: str
    model_id: str
    display_name: str
    input_cost_per_1k: float
    output_cost_per_1k: float
    is_active: bool = True

class ModelPricingCreate(ModelPricingBase):
    updated_by: Optional[str] = None

class ModelPricingUpdate(BaseModel):
    display_name: Optional[str] = None
    input_cost_per_1k: Optional[float] = None
    output_cost_per_1k: Optional[float] = None
    is_active: Optional[bool] = None
    updated_by: Optional[str] = None

class ModelPricing(ModelPricingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[str] = None
    
    class Config:
        from_attributes = True

# --- Schemas para gestión de precios en bulk ---
class ModelPricingBulkUpdate(BaseModel):
    """Para actualizar múltiples precios a la vez"""
    pricing_updates: List[Dict[str, Any]]
    updated_by: str

