from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from . import models, schemas
from .security import get_password_hash
from typing import List, Optional, Dict
from datetime import datetime, timezone 

# --- User CRUD ---
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene todos los usuarios para administración"""
    return db.query(models.User).offset(skip).limit(limit).all()

def get_pending_users(db: Session):
    """Obtiene usuarios pendientes de aprobación"""
    return db.query(models.User).filter(models.User.is_approved == False).all()

def approve_user(db: Session, user_id: int, approved_by: str):
    """Aprueba un usuario manualmente"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_approved = True
        user.is_active = True
        user.approved_at = datetime.now(timezone.utc)
        user.approved_by = approved_by
        db.commit()
        db.refresh(user)
    return user

def reject_user(db: Session, user_id: int):
    """Rechaza un usuario (lo mantiene inactivo)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_approved = False
        user.is_active = False
        db.commit()
        db.refresh(user)
    return user

def update_user_status(db: Session, user_id: int, user_update: schemas.UserUpdate):
    """Actualiza el estado de un usuario"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        update_data = user_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
    return user

def update_user_role(db: Session, user_id: int, role_update: schemas.UserUpdate):
    """Actualiza el rol de un usuario (solo para super administradores)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user and role_update.role:
        user.role = role_update.role
        db.commit()
        db.refresh(user)
    return user

def change_user_password(db: Session, user_id: int, password_update: schemas.PasswordUpdate):
    """Cambia la contraseña de un usuario"""
    from .security import verify_password, get_password_hash
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar contraseña actual
    if not verify_password(password_update.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    
    # Cambiar a nueva contraseña
    user.hashed_password = get_password_hash(password_update.new_password)
    db.commit()
    db.refresh(user)
    
    return user

def toggle_user_approval(db: Session, user_id: int, toggled_by: str):
    """Cambia el estado de aprobación de un usuario"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Cambiar el estado de aprobación
    user.is_approved = not user.is_approved
    
    # Si se aprueba, activar también
    if user.is_approved:
        user.is_active = True
        user.approved_at = datetime.now(timezone.utc)
        user.approved_by = toggled_by
    else:
        user.is_active = False
        user.approved_at = None
        user.approved_by = None
    
    db.commit()
    db.refresh(user)
    return user

# --- Bot CRUD ---
def get_bots_by_user(db: Session, user_id: int):
    return db.query(models.Bot).filter(models.Bot.owner_id == user_id).all()

def create_user_bot(db: Session, bot: schemas.BotCreate, user_id: int):
    db_bot = models.Bot(**bot.dict(), owner_id=user_id)
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot

def update_bot(db: Session, bot: models.Bot, bot_update: schemas.BotUpdate):
    update_data = bot_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(bot, key, value)
    db.commit()
    db.refresh(bot)
    return bot

def delete_bot(db: Session, bot_id: int):
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if bot:
        db.delete(bot)
        db.commit()
    return bot

# --- BotModelConfig CRUD ---
def add_model_config_to_bot(db: Session, config: schemas.BotModelConfigCreate, bot_id: int):
    db_config = models.BotModelConfig(**config.dict(), bot_id=bot_id)
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def delete_bot_model_config(db: Session, model_config_id: int):
    config = db.query(models.BotModelConfig).filter(models.BotModelConfig.id == model_config_id).first()
    if config:
        db.delete(config)
        db.commit()
    return config

# --- Document CRUD ---
def create_document(db: Session, doc: schemas.DocumentCreate):
    """
    Crea un nuevo documento en la base de datos.
    """
    db_doc = models.Document(
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        bot_id=doc.bot_id,
        status=models.DocumentStatus.PENDING # Estado inicial
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def update_document_status(db: Session, doc_id: int, status: models.DocumentStatus):
    """
    Actualiza el estado de un documento.
    """
    db_doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if db_doc:
        db_doc.status = status
        db.commit()
        db.refresh(db_doc)
    return db_doc

# === NUEVAS FUNCIONES CRUD PARA MÉTRICAS ===

# --- UserPlan CRUD ---
def get_user_plan(db: Session, user_id: int):
    """Obtiene el plan de un usuario"""
    return db.query(models.UserPlan).filter(models.UserPlan.user_id == user_id).first()

def create_user_plan(db: Session, plan: schemas.UserPlanCreate):
    """Crea un nuevo plan para usuario"""
    db_plan = models.UserPlan(**plan.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def update_user_plan(db: Session, user_id: int, plan_update: schemas.UserPlanUpdate):
    """Actualiza el plan de un usuario"""
    user_plan = db.query(models.UserPlan).filter(models.UserPlan.user_id == user_id).first()
    if user_plan:
        update_data = plan_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user_plan, key, value)
        db.commit()
        db.refresh(user_plan)
    return user_plan

# --- TokenUsage CRUD ---
def create_token_usage(db: Session, usage: schemas.TokenUsageCreate):
    """Registra un nuevo uso de tokens"""
    db_usage = models.TokenUsage(**usage.dict())
    db.add(db_usage)
    db.commit()
    db.refresh(db_usage)
    return db_usage

def get_token_usage_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Obtiene el historial de uso de tokens de un usuario"""
    return db.query(models.TokenUsage).filter(
        models.TokenUsage.user_id == user_id
    ).order_by(models.TokenUsage.created_at.desc()).offset(skip).limit(limit).all()

def get_token_usage_by_period(db: Session, user_id: int, start_date: datetime, end_date: datetime):
    """Obtiene uso de tokens en un período específico"""
    return db.query(models.TokenUsage).filter(
        models.TokenUsage.user_id == user_id,
        models.TokenUsage.created_at >= start_date,
        models.TokenUsage.created_at <= end_date
    ).all()

# --- BillingRecord CRUD ---
def create_billing_record(db: Session, record: schemas.BillingRecordCreate):
    """Crea un nuevo registro de facturación"""
    db_record = models.BillingRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_billing_records_by_user(db: Session, user_id: int):
    """Obtiene registros de facturación de un usuario"""
    return db.query(models.BillingRecord).filter(
        models.BillingRecord.user_id == user_id
    ).order_by(models.BillingRecord.created_at.desc()).all()

def update_billing_record_payment(db: Session, record_id: int, payment_id: str, payment_provider: str):
    """Actualiza un registro de facturación con información de pago"""
    record = db.query(models.BillingRecord).filter(models.BillingRecord.id == record_id).first()
    if record:
        record.is_paid = True
        record.payment_id = payment_id
        record.payment_provider = payment_provider
        record.paid_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(record)
    return record

# --- AnalyticsEvent CRUD ---
def create_analytics_event(db: Session, event: schemas.AnalyticsEventCreate):
    """Registra un nuevo evento analítico"""
    db_event = models.AnalyticsEvent(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_analytics_events_by_user(db: Session, user_id: int, event_type: Optional[models.EventType] = None, 
                                skip: int = 0, limit: int = 100):
    """Obtiene eventos analíticos de un usuario"""
    query = db.query(models.AnalyticsEvent).filter(models.AnalyticsEvent.user_id == user_id)
    
    if event_type:
        query = query.filter(models.AnalyticsEvent.event_type == event_type)
    
    return query.order_by(models.AnalyticsEvent.created_at.desc()).offset(skip).limit(limit).all()

def get_analytics_events_by_period(db: Session, start_date: datetime, end_date: datetime, 
                                 event_type: Optional[models.EventType] = None):
    """Obtiene eventos analíticos en un período"""
    query = db.query(models.AnalyticsEvent).filter(
        models.AnalyticsEvent.created_at >= start_date,
        models.AnalyticsEvent.created_at <= end_date
    )
    
    if event_type:
        query = query.filter(models.AnalyticsEvent.event_type == event_type)
    
    return query.all()

def get_documents_by_bot(db: Session, bot_id: int):
    """
    Obtiene todos los documentos de un bot específico.
    """
    return db.query(models.Document).filter(models.Document.bot_id == bot_id).all()

# === FUNCIONES CRUD PARA ADMINISTRACIÓN DE PLANES Y TOKENS ===

def get_all_users_with_plans(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene todos los usuarios con información de sus planes para administradores
    """
    from sqlalchemy.orm import joinedload
    from datetime import datetime, timedelta
    
    # Obtener usuarios con sus planes
    users = db.query(models.User).options(joinedload(models.User.bots)).offset(skip).limit(limit).all()
    
    result = []
    for user in users:
        # Obtener plan del usuario
        user_plan = db.query(models.UserPlan).filter(models.UserPlan.user_id == user.id).first()
        
        # Calcular estadísticas de uso (últimos 30 días) - Corregido para usar BytTokens
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        tokens_used_30_days = db.query(func.sum(models.TokenUsage.bytokens_cost)).filter(
            models.TokenUsage.user_id == user.id,
            models.TokenUsage.created_at >= thirty_days_ago
        ).scalar() or 0
        
        # Última actividad
        last_activity = db.query(func.max(models.TokenUsage.created_at)).filter(
            models.TokenUsage.user_id == user.id
        ).scalar()
        
        user_data = {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "is_approved": user.is_approved,
            "role": user.role,
            "created_at": user.created_at,
            "approved_at": user.approved_at,
            "approved_by": user.approved_by,
            "plan": user_plan,
            "total_bots": len(user.bots),
            "tokens_used_last_30_days": tokens_used_30_days,
            "last_activity": last_activity
        }
        result.append(user_data)
    
    return result

def admin_change_user_plan(db: Session, user_id: int, new_plan_type: models.PlanType, 
                          tokens_to_add: Optional[int] = None, reset_usage: bool = False):
    """
    Permite al admin cambiar el plan de cualquier usuario
    """
    from .services.metrics_service import PLAN_CONFIGS_BYTETOKENS
    
    # Obtener el usuario
    user = get_user(db, user_id)
    if not user:
        return None
        
    # Obtener plan actual
    user_plan = db.query(models.UserPlan).filter(models.UserPlan.user_id == user_id).first()
    if not user_plan:
        return None
    
    # Guardar valores anteriores para tracking
    previous_values = {
        "plan_type": user_plan.plan_type.value,
        "bytokens_included": user_plan.bytokens_included,
        "bytokens_remaining": user_plan.bytokens_remaining,
        "tokens_overage": user_plan.tokens_overage
    }
    
    # Obtener configuración del nuevo plan desde metrics_service
    config = PLAN_CONFIGS_BYTETOKENS[new_plan_type]
    
    # Actualizar plan
    user_plan.plan_type = new_plan_type
    user_plan.bytokens_included = config["bytokens_included"]
    user_plan.monthly_price = config["monthly_price"]
    user_plan.overage_rate = int(config["overage_rate"] * 1000)  # Convertir a entero
    
    # Resetear usage si se solicita
    if reset_usage:
        user_plan.bytokens_remaining = config["bytokens_included"]
        user_plan.tokens_overage = 0
        user_plan.overage_cost = 0
    else:
        # Ajustar bytokens remaining basado en el nuevo plan
        bytokens_used = user_plan.bytokens_included - user_plan.bytokens_remaining
        user_plan.bytokens_remaining = max(0, config["bytokens_included"] - bytokens_used)
    
    # Agregar bytokens adicionales si se especifica
    if tokens_to_add:
        user_plan.bytokens_remaining += tokens_to_add
        user_plan.bytokens_included += tokens_to_add
    
    db.commit()
    db.refresh(user_plan)
    
    return {
        "updated_plan": user_plan,
        "previous_values": previous_values
    }

def admin_modify_user_tokens(db: Session, user_id: int, tokens_to_add: int, 
                           reason: Optional[str] = None, reset_overage: bool = False):
    """
    Permite al admin agregar o quitar tokens de cualquier usuario
    """
    # Obtener plan del usuario
    user_plan = db.query(models.UserPlan).filter(models.UserPlan.user_id == user_id).first()
    if not user_plan:
        return None
    
    # Guardar valores anteriores
    previous_values = {
        "bytokens_included": user_plan.bytokens_included,
        "bytokens_remaining": user_plan.bytokens_remaining,
        "tokens_overage": user_plan.tokens_overage
    }
    
    # Modificar bytokens
    if tokens_to_add > 0:
        # Agregar bytokens
        user_plan.bytokens_included += tokens_to_add
        user_plan.bytokens_remaining += tokens_to_add
    else:
        # Quitar bytokens
        tokens_to_remove = abs(tokens_to_add)
        user_plan.bytokens_included = max(0, user_plan.bytokens_included - tokens_to_remove)
        user_plan.bytokens_remaining = max(0, user_plan.bytokens_remaining - tokens_to_remove)
    
    # Resetear overage si se solicita
    if reset_overage:
        user_plan.tokens_overage = 0
        user_plan.overage_cost = 0
    
    # Registrar el cambio en eventos
    if reason:
        event = models.AnalyticsEvent(
            user_id=user_id,
            event_type=models.EventType.TOKEN_LIMIT_WARNING,  # Usar como evento de modificación
            event_data=f"Admin token modification: {tokens_to_add} tokens. Reason: {reason}"
        )
        db.add(event)
    
    db.commit()
    db.refresh(user_plan)
    
    return {
        "updated_plan": user_plan,
        "previous_values": previous_values,
        "tokens_modified": tokens_to_add
    }

def get_user_plan_details(db: Session, user_id: int):
    """
    Obtiene detalles completos del plan de un usuario para administradores
    """
    from datetime import datetime, timedelta
    
    user_plan = db.query(models.UserPlan).filter(models.UserPlan.user_id == user_id).first()
    if not user_plan:
        return None
    
    # Obtener estadísticas de uso
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Uso total de tokens
    total_tokens_used = db.query(func.sum(models.TokenUsage.total_tokens)).filter(
        models.TokenUsage.user_id == user_id
    ).scalar() or 0
    
    # Uso últimos 30 días
    tokens_last_30_days = db.query(func.sum(models.TokenUsage.total_tokens)).filter(
        models.TokenUsage.user_id == user_id,
        models.TokenUsage.created_at >= thirty_days_ago
    ).scalar() or 0
    
    # Uso por proveedor (últimos 30 días)
    usage_by_provider = db.query(
        models.TokenUsage.provider,
        func.sum(models.TokenUsage.total_tokens).label('total_tokens')
    ).filter(
        models.TokenUsage.user_id == user_id,
        models.TokenUsage.created_at >= thirty_days_ago
    ).group_by(models.TokenUsage.provider).all()
    
    provider_usage = {provider: tokens for provider, tokens in usage_by_provider}
    
    # Historial de facturas
    billing_records = db.query(models.BillingRecord).filter(
        models.BillingRecord.user_id == user_id
    ).order_by(models.BillingRecord.created_at.desc()).limit(5).all()
    
    return {
        "user_plan": user_plan,
        "usage_stats": {
            "total_tokens_used": total_tokens_used,
            "tokens_last_30_days": tokens_last_30_days,
            "usage_by_provider": provider_usage
        },
        "recent_billing": billing_records
    }

# === Funciones para ModelPricing ===

def get_all_model_pricing(db: Session) -> List[models.ModelPricing]:
    """Obtiene todos los precios de modelos"""
    return db.query(models.ModelPricing).filter(
        models.ModelPricing.is_active == True
    ).order_by(models.ModelPricing.provider, models.ModelPricing.model_id).all()

def get_model_pricing_by_provider(db: Session, provider: str) -> List[models.ModelPricing]:
    """Obtiene precios de modelos por proveedor"""
    return db.query(models.ModelPricing).filter(
        models.ModelPricing.provider == provider,
        models.ModelPricing.is_active == True
    ).order_by(models.ModelPricing.model_id).all()

def get_model_pricing(db: Session, provider: str, model_id: str) -> models.ModelPricing:
    """Obtiene el precio de un modelo específico"""
    return db.query(models.ModelPricing).filter(
        models.ModelPricing.provider == provider,
        models.ModelPricing.model_id == model_id
    ).first()

def create_model_pricing(db: Session, pricing: schemas.ModelPricingCreate) -> models.ModelPricing:
    """Crea un nuevo precio de modelo"""
    db_pricing = models.ModelPricing(**pricing.dict())
    db.add(db_pricing)
    db.commit()
    db.refresh(db_pricing)
    return db_pricing

def update_model_pricing(db: Session, pricing_id: int, pricing_update: schemas.ModelPricingUpdate) -> models.ModelPricing:
    """Actualiza el precio de un modelo"""
    db_pricing = db.query(models.ModelPricing).filter(models.ModelPricing.id == pricing_id).first()
    if not db_pricing:
        return None
    
    # Actualizar solo los campos proporcionados
    update_data = pricing_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_pricing, field, value)
    
    db.commit()
    db.refresh(db_pricing)
    return db_pricing

def bulk_update_model_pricing(db: Session, updates: List[Dict], updated_by: str):
    """Actualiza múltiples precios a la vez"""
    updated_count = 0
    
    for update in updates:
        pricing_id = update.get('id')
        if not pricing_id:
            continue
            
        db_pricing = db.query(models.ModelPricing).filter(models.ModelPricing.id == pricing_id).first()
        if not db_pricing:
            continue
        
        # Actualizar campos
        if 'input_cost_per_1k' in update:
            db_pricing.input_cost_per_1k = update['input_cost_per_1k']
        if 'output_cost_per_1k' in update:
            db_pricing.output_cost_per_1k = update['output_cost_per_1k']
        if 'display_name' in update:
            db_pricing.display_name = update['display_name']
        if 'is_active' in update:
            db_pricing.is_active = update['is_active']
            
        db_pricing.updated_by = updated_by
        updated_count += 1
    
    db.commit()
    return {"updated_count": updated_count}

def initialize_default_model_pricing(db: Session):
    """Inicializa los precios por defecto si no existen"""
    
    # Verificar si ya existen precios
    existing_count = db.query(models.ModelPricing).count()
    if existing_count > 0:
        return False
    
    # Precios por defecto actuales
    default_pricing = [
        # OpenAI
        {"provider": "openai", "model_id": "gpt-4o", "display_name": "GPT-4o", "input_cost_per_1k": 0.005, "output_cost_per_1k": 0.015},
        {"provider": "openai", "model_id": "gpt-4o-mini", "display_name": "GPT-4o Mini", "input_cost_per_1k": 0.00015, "output_cost_per_1k": 0.0006},
        {"provider": "openai", "model_id": "gpt-4-turbo", "display_name": "GPT-4 Turbo", "input_cost_per_1k": 0.01, "output_cost_per_1k": 0.03},
        {"provider": "openai", "model_id": "o1-preview", "display_name": "o1-preview", "input_cost_per_1k": 0.015, "output_cost_per_1k": 0.06},
        {"provider": "openai", "model_id": "o1-mini", "display_name": "o1-mini", "input_cost_per_1k": 0.003, "output_cost_per_1k": 0.012},
        
        # Google Gemini
        {"provider": "google", "model_id": "gemini-pro", "display_name": "Gemini Pro", "input_cost_per_1k": 0.0015, "output_cost_per_1k": 0.0015},
        {"provider": "google", "model_id": "gemini-flash", "display_name": "Gemini Flash", "input_cost_per_1k": 0.00015, "output_cost_per_1k": 0.0006},
        {"provider": "google", "model_id": "gemini-ultra", "display_name": "Gemini Ultra", "input_cost_per_1k": 0.003, "output_cost_per_1k": 0.003},
        
        # DeepSeek
        {"provider": "deepseek", "model_id": "deepseek-v2", "display_name": "DeepSeek V2", "input_cost_per_1k": 0.0002, "output_cost_per_1k": 0.0002},
        {"provider": "deepseek", "model_id": "deepseek-reasoner", "display_name": "DeepSeek Reasoner", "input_cost_per_1k": 0.002, "output_cost_per_1k": 0.002},
        
        # Default fallback
        {"provider": "default", "model_id": "default", "display_name": "Default Model", "input_cost_per_1k": 0.001, "output_cost_per_1k": 0.001},
    ]
    
    # Crear registros
    for pricing_data in default_pricing:
        db_pricing = models.ModelPricing(**pricing_data, updated_by="system_init")
        db.add(db_pricing)
    
    db.commit()
    return True