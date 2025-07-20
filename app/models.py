from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Enum, DateTime, func, Float, Index
from sqlalchemy.orm import relationship
from .database import Base
import enum

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)  # Cambiado a False por defecto
    is_approved = Column(Boolean, default=False)  # Nuevo campo para autorización manual
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)  # Nuevo campo de rol
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(String, nullable=True)  # Email del admin que aprobó

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

# === NUEVOS MODELOS PARA MÉTRICAS Y ANALÍTICAS ===

class PlanType(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class UserPlan(Base):
    __tablename__ = "user_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_type = Column(Enum(PlanType), default=PlanType.FREE, nullable=False)
    tokens_included = Column(Integer, default=100000)  # Tokens incluidos en el plan (DEPRECATED)
    tokens_remaining = Column(Integer, default=100000)  # Tokens restantes (DEPRECATED)
    tokens_overage = Column(Integer, default=0)  # Tokens extras usados (ahora en BytTokens)
    overage_cost = Column(Integer, default=0)  # Costo en centavos de overage
    
    # Nuevo sistema BytTokens
    bytokens_included = Column(Integer, default=2000)  # BytTokens incluidos en el plan
    bytokens_remaining = Column(Integer, default=2000)  # BytTokens restantes
    
    # Precios y configuración
    monthly_price = Column(Integer, default=0)  # Precio mensual en centavos
    overage_rate = Column(Integer, default=10)  # Rate por token extra en centavos/100000
    
    # Fechas
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    current_period_start = Column(DateTime(timezone=True), server_default=func.now())
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    user = relationship("User")

class TokenUsage(Base):
    __tablename__ = "token_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=False)
    
    # Información del request
    user_anon_id = Column(String, nullable=True)  # Para usuarios anónimos
    query = Column(Text, nullable=False)
    
    # Información del modelo usado
    provider = Column(String, nullable=False)  # openai, google, deepseek
    model_id = Column(String, nullable=False)  # gpt-4, gemini-pro, etc.
    
    # Métricas de tokens
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Costos calculados
    prompt_cost = Column(Integer, default=0)  # En centavos
    completion_cost = Column(Integer, default=0)  # En centavos
    total_cost = Column(Integer, default=0)  # En centavos
    bytokens_cost = Column(Integer, default=0)  # En BytTokens (1000 = $1)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    response_time_ms = Column(Integer, nullable=True)  # Tiempo de respuesta
    
    # Relaciones
    user = relationship("User")
    bot = relationship("Bot")

class BillingRecord(Base):
    __tablename__ = "billing_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Período de facturación
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Costos
    plan_cost = Column(Integer, default=0)  # Costo del plan base en centavos
    overage_cost = Column(Integer, default=0)  # Costo de overage en centavos
    total_cost = Column(Integer, default=0)  # Total en centavos
    
    # Métricas del período (sistema viejo - mantenido por compatibilidad)
    tokens_included = Column(Integer, default=0)  # DEPRECATED
    tokens_used = Column(Integer, default=0)  # DEPRECATED
    tokens_overage = Column(Integer, default=0)  # DEPRECATED
    
    # Métricas del período (nuevo sistema BytTokens)
    bytokens_included = Column(Integer, default=0)  # BytTokens incluidos en el período
    bytokens_used = Column(Integer, default=0)  # BytTokens utilizados en el período
    bytokens_overage = Column(Integer, default=0)  # BytTokens de overage
    
    # Estado de pago
    is_paid = Column(Boolean, default=False)
    payment_id = Column(String, nullable=True)  # ID de Stripe/Culqi
    payment_provider = Column(String, nullable=True)  # stripe, culqi
    
    # Fechas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    user = relationship("User")

class EventType(str, enum.Enum):
    USER_REGISTRATION = "user_registration"
    USER_LOGIN = "user_login"
    BOT_CREATED = "bot_created"
    CHAT_MESSAGE = "chat_message"
    PLAN_UPGRADE = "plan_upgrade"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    TOKEN_LIMIT_WARNING = "token_limit_warning"
    TOKEN_LIMIT_EXCEEDED = "token_limit_exceeded"

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=True)
    
    # Información del evento
    event_type = Column(Enum(EventType), nullable=False)
    event_data = Column(Text, nullable=True)  # JSON con datos adicionales
    
    # Contexto
    user_anon_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    user = relationship("User")
    bot = relationship("Bot")

class ModelPricing(Base):
    __tablename__ = "model_pricing"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False)  # "openai", "google", "deepseek"
    model_id = Column(String, nullable=False)  # "gpt-4o", "gemini-pro", etc.
    display_name = Column(String, nullable=False)  # "GPT-4o", "Gemini Pro", etc.
    
    # Precios en USD por 1K tokens
    input_cost_per_1k = Column(Float, nullable=False, default=0.001)
    output_cost_per_1k = Column(Float, nullable=False, default=0.001)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(String, nullable=True)  # Usuario que hizo el último cambio
    
    # Índice único por provider + model_id
    __table_args__ = (
        Index('idx_provider_model', 'provider', 'model_id', unique=True),
    )