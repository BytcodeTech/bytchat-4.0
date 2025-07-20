import os
import shutil
from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, File, Response, Path, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
import json
import logging

# --- Imports de nuestra aplicación ---
from . import auth, crud, models, schemas
from .database import engine, get_db
from .core.orchestrator import Orchestrator
from .worker import celery_app
from .services.metrics_service import MetricsService


# Crea las tablas en la base de datos si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bytchat SaaS API",
    description="API para la plataforma multi-tenant de Bytchat.",
    version="1.4.0"
)

# Montar la carpeta de archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- CONFIGURACIÓN DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Endpoints de Autenticación y Usuarios ===
@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User, tags=["Users"])
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.put("/users/me/password/", response_model=schemas.User, tags=["Users"])
def change_user_password(
    password_update: schemas.PasswordUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Cambia la contraseña del usuario actual"""
    return crud.change_user_password(db=db, user_id=current_user.id, password_update=password_update)

# === Endpoints de Administración de Usuarios ===
@app.get("/admin/users/", response_model=List[schemas.UserAdmin], tags=["Admin"])
def get_all_users_admin(db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin_role)):
    """Obtiene todos los usuarios (solo para administradores)"""
    return crud.get_all_users(db)

@app.get("/admin/users/pending/", response_model=List[schemas.UserAdmin], tags=["Admin"])
def get_pending_users_admin(db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin_role)):
    """Obtiene usuarios pendientes de aprobación"""
    return crud.get_pending_users(db)

@app.post("/admin/users/{user_id}/approve/", response_model=schemas.UserAdmin, tags=["Admin"])
def approve_user_admin(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.require_admin_role)
):
    """Aprueba un usuario manualmente"""
    return crud.approve_user(db, user_id=user_id, approved_by=current_user.email)

@app.post("/admin/users/{user_id}/reject/", response_model=schemas.UserAdmin, tags=["Admin"])
def reject_user_admin(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.require_admin_role)
):
    """Rechaza un usuario"""
    return crud.reject_user(db, user_id=user_id)

@app.put("/admin/users/{user_id}/status/", response_model=schemas.UserAdmin, tags=["Admin"])
def update_user_status_admin(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin_role)
):
    """Actualiza el estado de un usuario"""
    return crud.update_user_status(db, user_id=user_id, user_update=user_update)

# === Endpoints de Super Administración ===
@app.post("/admin/users/{user_id}/role/", response_model=schemas.UserAdmin, tags=["Super Admin"])
def update_user_role_admin(
    user_id: int,
    role_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_super_admin_role)
):
    """Actualiza el rol de un usuario (solo super administradores)"""
    return crud.update_user_role(db, user_id=user_id, role_update=role_update)

@app.post("/admin/users/{user_id}/toggle-approval/", response_model=schemas.UserAdmin, tags=["Super Admin"])
def toggle_user_approval_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_super_admin_role)
):
    """Cambia el estado de aprobación de un usuario (solo super administradores)"""
    return crud.toggle_user_approval(db, user_id=user_id, toggled_by=current_user.email)

# === Endpoints de Gestión de Planes y Tokens ===
@app.get("/admin/users/with-plans/", response_model=List[schemas.UserWithPlan], tags=["Super Admin"])
def get_all_users_with_plans_admin(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_super_admin_role)
):
    """Obtiene todos los usuarios con información de planes y tokens (solo super administradores)"""
    return crud.get_all_users_with_plans(db, skip=skip, limit=limit)

@app.get("/admin/users/{user_id}/plan-details/", tags=["Super Admin"])
def get_user_plan_details_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_super_admin_role)
):
    """Obtiene detalles completos del plan de un usuario (solo super administradores)"""
    details = crud.get_user_plan_details(db, user_id=user_id)
    if not details:
        raise HTTPException(status_code=404, detail="Usuario o plan no encontrado")
    return details

@app.post("/admin/users/{user_id}/change-plan/", response_model=schemas.AdminUserPlanResponse, tags=["Super Admin"])
def change_user_plan_admin(
    user_id: int,
    plan_request: schemas.AdminPlanChangeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_super_admin_role)
):
    """Cambia el plan de un usuario (solo super administradores)"""
    # Verificar que el usuario existe
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Cambiar plan
    result = crud.admin_change_user_plan(
        db=db,
        user_id=user_id,
        new_plan_type=plan_request.new_plan_type,
        tokens_to_add=plan_request.tokens_to_add,
        reset_usage=plan_request.reset_usage
    )
    
    if not result:
        raise HTTPException(status_code=400, detail="No se pudo cambiar el plan")
    
    # Registrar evento
    event = models.AnalyticsEvent(
        user_id=user_id,
        event_type=models.EventType.PLAN_UPGRADE,
        event_data=f"Plan changed by admin {current_user.email} to {plan_request.new_plan_type.value}"
    )
    db.add(event)
    db.commit()
    
    return schemas.AdminUserPlanResponse(
        success=True,
        message=f"Plan cambiado exitosamente a {plan_request.new_plan_type.value}",
        updated_plan=result["updated_plan"],
        previous_values=result["previous_values"]
    )

@app.post("/admin/users/{user_id}/modify-tokens/", response_model=schemas.AdminUserPlanResponse, tags=["Super Admin"])
def modify_user_tokens_admin(
    user_id: int,
    token_request: schemas.AdminTokenModification,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_super_admin_role)
):
    """Modifica los tokens de un usuario (solo super administradores)"""
    # Verificar que el usuario existe
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Modificar tokens
    result = crud.admin_modify_user_tokens(
        db=db,
        user_id=user_id,
        tokens_to_add=token_request.tokens_to_add,
        reason=token_request.reason,
        reset_overage=token_request.reset_overage
    )
    
    if not result:
        raise HTTPException(status_code=400, detail="No se pudieron modificar los tokens")
    
    # Registrar evento
    action = "agregados" if token_request.tokens_to_add > 0 else "removidos"
    event = models.AnalyticsEvent(
        user_id=user_id,
        event_type=models.EventType.TOKEN_LIMIT_WARNING,
        event_data=f"Tokens {action} por admin {current_user.email}: {token_request.tokens_to_add}. Razón: {token_request.reason or 'No especificada'}"
    )
    db.add(event)
    db.commit()
    
    return schemas.AdminUserPlanResponse(
        success=True,
        message=f"Tokens modificados exitosamente: {token_request.tokens_to_add}",
        updated_plan=result["updated_plan"],
        previous_values=result["previous_values"]
    )


# --- Función auxiliar para obtener un bot de un usuario específico ---
def get_bot(db: Session, bot_id: int, user_id: int):
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id, models.Bot.owner_id == user_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot no encontrado o no tienes permiso")
    return bot

# === Endpoints para la Gestión de Bots (Protegidos) ===
@app.post("/bots/", response_model=schemas.Bot, tags=["Bots"])
def create_bot_for_user(bot: schemas.BotCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_user_bot(db=db, bot=bot, user_id=current_user.id)

@app.get("/bots/", response_model=List[schemas.Bot], tags=["Bots"])
def read_user_bots(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    bots = crud.get_bots_by_user(db, user_id=current_user.id)
    return bots

# El endpoint de PUT ahora usa la función de autenticación correcta
@app.put("/bots/{bot_id}", response_model=schemas.Bot, tags=["Bots"])
def update_bot_details(
    bot_id: int,
    bot_update: schemas.BotUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    db_bot = get_bot(db, bot_id=bot_id, user_id=current_user.id)
    return crud.update_bot(db=db, bot=db_bot, bot_update=bot_update)

@app.delete("/bots/{bot_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Bots"])
def delete_bot(bot_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_bot = get_bot(db=db, bot_id=bot_id, user_id=current_user.id)
    crud.delete_bot(db=db, bot_id=db_bot.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/bots/{bot_id}/models/", response_model=schemas.BotModelConfig, tags=["Bots"])
def add_model_to_bot(
    bot_id: int,
    model_config: schemas.BotModelConfigCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    bot = get_bot(db=db, bot_id=bot_id, user_id=current_user.id)
    return crud.add_model_config_to_bot(db=db, config=model_config, bot_id=bot_id)

@app.delete("/bots/{bot_id}/models/{model_config_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Bots"])
def remove_model_from_bot(
    bot_id: int,
    model_config_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    bot = get_bot(db=db, bot_id=bot_id, user_id=current_user.id)
    model_config = db.query(models.BotModelConfig).filter(
        models.BotModelConfig.id == model_config_id,
        models.BotModelConfig.bot_id == bot_id
    ).first()

    if not model_config:
        raise HTTPException(status_code=404, detail="Configuración de modelo no encontrada para este bot")

    crud.delete_bot_model_config(db=db, model_config_id=model_config_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/bots/{bot_id}/train", tags=["Bots"])
def train_bot_with_document(
    bot_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verificar que el bot pertenece al usuario
    bot = get_bot(db=db, bot_id=bot_id, user_id=current_user.id)
    
    # Guardar archivo temporal
    temp_dir = f"temp_uploads/{current_user.id}"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = f"{temp_dir}/{file.filename}"
    
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Crear registro del documento
    doc_data = schemas.DocumentCreate(
        filename=file.filename,
        file_type=file.content_type,
        file_size=os.path.getsize(temp_file_path),
        bot_id=bot_id
    )
    document = crud.create_document(db=db, doc=doc_data)
    
    # Enviar tarea a Celery
    task = celery_app.send_task(
        'app.worker.process_document',
        args=[document.id, temp_file_path]
    )
    
    return {"message": "Documento enviado para procesamiento", "document_id": document.id, "task_id": task.id}

@app.get("/bots/{bot_id}/documents", response_model=List[schemas.Document], tags=["Bots"])
def get_bot_documents(
    bot_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verificar que el bot pertenece al usuario
    bot = get_bot(db=db, bot_id=bot_id, user_id=current_user.id)
    return bot.documents

# === Endpoint para Chat Autenticado ===
@app.post("/bots/{bot_id}/chat", tags=["Bots"])
def chat_with_bot(
    bot_id: int,
    chat_query: schemas.ChatQuery,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Endpoint de chat para usuarios autenticados con tracking de métricas.
    """
    # Verificar que el bot pertenece al usuario
    bot = get_bot(db=db, bot_id=bot_id, user_id=current_user.id)
    
    # Convertir el bot a diccionario para el orquestador
    bot_config_dict = schemas.Bot.from_orm(bot).model_dump()
    
    # Crear orquestador con user_id para métricas
    orchestrator = Orchestrator(db=db, bot_config=bot_config_dict, bot_id=bot_id, user_id=current_user.id)
    
    # Procesar la consulta con métricas habilitadas
    text_stream_generator = orchestrator.handle_query(
        user_id=str(current_user.id),
        query=chat_query.query,
        track_metrics=True
    )
    
    return StreamingResponse(text_stream_generator, media_type="text/plain; charset=utf-8")

# === NUEVOS ENDPOINTS PARA MÉTRICAS Y ANALÍTICAS ===

@app.get("/users/me/plan", response_model=schemas.UserPlan, tags=["User Analytics"])
def get_user_plan(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Obtiene el plan actual del usuario"""
    metrics_service = MetricsService(db)
    user_plan = metrics_service.get_or_create_user_plan(current_user.id)
    return user_plan

@app.get("/users/me/analytics", tags=["User Analytics"])
def get_user_analytics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Obtiene analíticas completas del usuario para el dashboard"""
    metrics_service = MetricsService(db)
    analytics = metrics_service.get_user_analytics(current_user.id)
    return analytics

@app.get("/users/me/token-usage", response_model=List[schemas.TokenUsage], tags=["User Analytics"])
def get_user_token_usage(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Obtiene el historial de uso de tokens del usuario"""
    return crud.get_token_usage_by_user(db, user_id=current_user.id, skip=skip, limit=limit)

@app.get("/users/me/billing", response_model=List[schemas.BillingRecord], tags=["User Analytics"])
def get_user_billing_records(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Obtiene los registros de facturación del usuario"""
    return crud.get_billing_records_by_user(db, user_id=current_user.id)

@app.post("/users/me/plan/upgrade", response_model=schemas.UserPlan, tags=["User Analytics"])
def upgrade_user_plan(
    new_plan: schemas.UserPlanUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Actualiza el plan del usuario"""
    if not new_plan.plan_type:
        raise HTTPException(status_code=400, detail="Se requiere especificar plan_type")
    
    metrics_service = MetricsService(db)
    updated_plan = metrics_service.upgrade_user_plan(current_user.id, new_plan.plan_type)
    return updated_plan

@app.get("/users/me/usage-summary", tags=["User Analytics"])
def get_usage_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Obtiene un resumen rápido del uso actual"""
    metrics_service = MetricsService(db)
    user_plan = metrics_service.get_or_create_user_plan(current_user.id)
    
    return {
        "tokens_remaining": user_plan.bytokens_remaining,
        "tokens_included": user_plan.bytokens_included,
        "usage_percentage": ((user_plan.bytokens_included - user_plan.bytokens_remaining) / user_plan.bytokens_included) * 100,
        "overage_tokens": user_plan.tokens_overage,
        "overage_cost_cents": user_plan.overage_cost,
        "plan_type": user_plan.plan_type.value,
        "current_period_end": user_plan.current_period_end
    }

# === ENDPOINTS PARA ADMINISTRADORES ===

@app.get("/admin/analytics/overview", tags=["Admin Analytics"])
def get_admin_analytics_overview(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin_role)
):
    """Dashboard de analíticas para administradores"""
    
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Métricas generales
    total_users = db.query(func.count(models.User.id)).scalar()
    active_users_last_30_days = db.query(func.count(models.User.id)).filter(
        models.User.approved_at >= now - timedelta(days=30)
    ).scalar()
    
    # Revenue este mes (en centavos)
    total_revenue = db.query(func.sum(models.BillingRecord.total_cost)).filter(
        and_(
            models.BillingRecord.is_paid == True,
            models.BillingRecord.period_start >= month_start
        )
    ).scalar() or 0
    
    # Usuarios por plan
    users_by_plan = {}
    plan_stats = db.query(
        models.UserPlan.plan_type,
        func.count(models.UserPlan.id).label('count')
    ).group_by(models.UserPlan.plan_type).all()
    
    for plan_type, count in plan_stats:
        users_by_plan[plan_type.value] = count
    
    # Top 5 bots más usados
    top_bots = db.query(
        models.Bot.name,
        func.count(models.TokenUsage.id).label('usage_count')
    ).join(models.TokenUsage).filter(
        models.TokenUsage.created_at >= month_start
    ).group_by(models.Bot.id, models.Bot.name).order_by(
        func.count(models.TokenUsage.id).desc()
    ).limit(5).all()
    
    return {
        "total_users": total_users,
        "active_users_last_30_days": active_users_last_30_days,
        "total_revenue_this_month_cents": total_revenue,
        "users_by_plan": users_by_plan,
        "top_bots": [{"bot_name": name, "usage_count": count} for name, count in top_bots]
    }

@app.get("/admin/analytics/revenue", tags=["Admin Analytics"])
def get_revenue_analytics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin_role)
):
    """Analíticas de revenue por período"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Revenue por día
    daily_revenue = db.query(
        func.date(models.BillingRecord.paid_at).label('date'),
        func.sum(models.BillingRecord.total_cost).label('revenue')
    ).filter(
        and_(
            models.BillingRecord.is_paid == True,
            models.BillingRecord.paid_at >= start_date,
            models.BillingRecord.paid_at <= end_date
        )
    ).group_by(func.date(models.BillingRecord.paid_at)).all()
    
    # Revenue por plan
    revenue_by_plan = db.query(
        models.UserPlan.plan_type,
        func.sum(models.BillingRecord.total_cost).label('revenue')
    ).join(models.BillingRecord).filter(
        and_(
            models.BillingRecord.is_paid == True,
            models.BillingRecord.period_start >= start_date
        )
    ).group_by(models.UserPlan.plan_type).all()
    
    return {
        "daily_revenue": [
            {"date": date.isoformat(), "revenue_cents": revenue}
            for date, revenue in daily_revenue
        ],
        "revenue_by_plan": {
            plan_type.value: revenue for plan_type, revenue in revenue_by_plan
        }
    }

# === Endpoints de Analytics para Usuarios ===
@app.get("/bots/{bot_id}/analytics", tags=["Analytics"])
def get_bot_analytics(
    bot_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Obtener analytics del bot para el usuario actual"""
    # Verificar que el bot pertenece al usuario
    bot = db.query(models.Bot).filter(
        models.Bot.id == bot_id,
        models.Bot.owner_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="Bot no encontrado o no tienes permisos")
    
    # Calcular fecha de inicio
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Obtener eventos de chat
    chat_events = db.query(models.AnalyticsEvent).filter(
        models.AnalyticsEvent.bot_id == bot_id,
        models.AnalyticsEvent.event_type == models.EventType.CHAT_MESSAGE,
        models.AnalyticsEvent.created_at >= start_date
    ).order_by(models.AnalyticsEvent.created_at.desc()).all()
    
    # Contar mensajes por día
    from collections import defaultdict
    daily_usage = defaultdict(int)
    
    for event in chat_events:
        date_key = event.created_at.date().isoformat()
        daily_usage[date_key] += 1
    
    # Obtener uso de tokens si existe
    token_usage = db.query(models.TokenUsage).filter(
        models.TokenUsage.bot_id == bot_id,
        models.TokenUsage.created_at >= start_date
    ).all()
    
    total_tokens = sum(usage.total_tokens for usage in token_usage)
    total_cost = sum(usage.total_cost for usage in token_usage)
    
    return {
        "bot_id": bot_id,
        "bot_name": bot.name,
        "period_days": days,
        "total_messages": len(chat_events),
        "total_tokens": total_tokens,
        "total_cost_cents": total_cost,
        "daily_usage": dict(daily_usage),
        "recent_messages": [
            {
                "timestamp": event.created_at.isoformat(),
                "data": json.loads(event.event_data) if event.event_data else {}
            }
            for event in chat_events[:10]
        ]
    }

@app.get("/user/analytics/summary", tags=["Analytics"])
def get_user_analytics_summary(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Resumen de analytics para todos los bots del usuario"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Obtener todos los bots del usuario
    user_bots = db.query(models.Bot).filter(models.Bot.owner_id == current_user.id).all()
    
    # Obtener eventos totales
    total_events = db.query(models.AnalyticsEvent).filter(
        models.AnalyticsEvent.user_id == current_user.id,
        models.AnalyticsEvent.event_type == models.EventType.CHAT_MESSAGE,
        models.AnalyticsEvent.created_at >= start_date
    ).count()
    
    # Obtener uso de tokens total
    total_tokens = db.query(func.sum(models.TokenUsage.total_tokens)).filter(
        models.TokenUsage.user_id == current_user.id,
        models.TokenUsage.created_at >= start_date
    ).scalar() or 0
    
    total_cost = db.query(func.sum(models.TokenUsage.total_cost)).filter(
        models.TokenUsage.user_id == current_user.id,
        models.TokenUsage.created_at >= start_date
    ).scalar() or 0
    
    return {
        "user_id": current_user.id,
        "period_days": days,
        "total_bots": len(user_bots),
        "total_messages": total_events,
        "total_tokens": total_tokens,
        "total_cost_cents": total_cost,
        "bots": [
            {
                "id": bot.id,
                "name": bot.name,
                "created_at": bot.created_at.isoformat()
            }
            for bot in user_bots
        ]
    }

# === Endpoint público para el widget con consumo de tokens para bots de usuarios de pago ===
@app.post("/chat/widget/{bot_id}", tags=["Public Chat"])
def widget_chat(bot_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    """
    Endpoint público para el widget de chat. Recibe userAnonId y mensaje.
    
    LÓGICA DE TOKENS:
    - Si el bot pertenece a un usuario de pago: SÍ consume tokens del propietario
    - Si el bot no tiene propietario o es demo: NO consume tokens
    """
    user_anon_id = data.get('userAnonId')
    query = data.get('query')
    if not user_anon_id or not query:
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios")
    
    # Guardar la métrica básica
    with open('chat_metrics.log', 'a') as f:
        f.write(f"{datetime.utcnow().isoformat()} | bot_id={bot_id} | userAnonId={user_anon_id} | mensaje={query}\n")
    
    # Obtener el bot (sin autenticación)
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot no encontrado")
    
    # Verificar si el bot tiene propietario con plan de pago
    bot_owner = None
    should_track_metrics = False
    orchestrator_user_id = None
    
    if bot.owner_id:
        bot_owner = db.query(models.User).filter(models.User.id == bot.owner_id).first()
        if bot_owner:
            # Verificar si el usuario tiene plan de pago (no FREE)
            user_plan = db.query(models.UserPlan).filter(models.UserPlan.user_id == bot_owner.id).first()
            if user_plan and user_plan.plan_type != models.PlanType.FREE:
                should_track_metrics = True
                orchestrator_user_id = bot_owner.id
                with open('chat_metrics.log', 'a') as f:
                    f.write(f"  -> CONSUMIRÁ TOKENS del usuario {bot_owner.email} (plan: {user_plan.plan_type})\n")
            else:
                with open('chat_metrics.log', 'a') as f:
                    f.write(f"  -> NO consumirá tokens (usuario {bot_owner.email} tiene plan FREE)\n")
    else:
        with open('chat_metrics.log', 'a') as f:
            f.write(f"  -> NO consumirá tokens (bot sin propietario)\n")
    
    bot_config_dict = schemas.Bot.from_orm(bot).model_dump()
    
    # Crear orquestador con o sin métricas según el plan del propietario
    orchestrator = Orchestrator(
        db=db, 
        bot_config=bot_config_dict, 
        bot_id=bot_id, 
        user_id=orchestrator_user_id
    )
    
    # Procesar la consulta con o sin métricas según el plan
    text_stream_generator = orchestrator.handle_query(
        user_id=str(user_anon_id),
        query=query,
        track_metrics=should_track_metrics
    )
    
    return StreamingResponse(text_stream_generator, media_type="text/plain; charset=utf-8")

# === Endpoint autenticado para chat con métricas completas ===
@app.post("/chat/{bot_id}", tags=["Chat"])
def authenticated_chat(
    bot_id: int,
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Endpoint autenticado para chat que registra métricas completas
    """
    query = data.get('query')
    if not query:
        raise HTTPException(status_code=400, detail="La consulta es obligatoria")
    
    # Verificar que el bot pertenece al usuario o es público
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot no encontrado")
    
    # Verificar permisos: el bot debe pertenecer al usuario actual
    if bot.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para usar este bot")
    
    bot_config_dict = schemas.Bot.from_orm(bot).model_dump()
    
    # Crear orquestador CON métricas completas
    orchestrator = Orchestrator(db=db, bot_config=bot_config_dict, bot_id=bot_id, user_id=current_user.id)
    
    # Procesar la consulta CON métricas (track_metrics=True)
    text_stream_generator = orchestrator.handle_query(
        user_id=str(current_user.id),
        query=query,
        track_metrics=True
    )
    
    # Registrar evento de análisis
    try:
        analytics_event = models.AnalyticsEvent(
            user_id=current_user.id,
            bot_id=bot_id,
            event_type=models.EventType.CHAT_MESSAGE,
            event_data=json.dumps({"query_length": len(query), "query_preview": query[:50]}),
            created_at=datetime.utcnow()
        )
        db.add(analytics_event)
        db.commit()
    except Exception as e:
        logging.warning(f"Error registrando evento de analytics: {e}")
        db.rollback()
    
    return StreamingResponse(text_stream_generator, media_type="text/plain; charset=utf-8")

# === Endpoints para gestión de precios de modelos ===

@app.get("/admin/model-pricing/", response_model=List[schemas.ModelPricing], tags=["Super Admin"])
def get_all_model_pricing_admin(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_super_admin_role)
):
    """Obtiene todos los precios de modelos (solo super administradores)"""
    return crud.get_all_model_pricing(db)

@app.get("/admin/model-pricing/{provider}/", response_model=List[schemas.ModelPricing], tags=["Super Admin"])
def get_model_pricing_by_provider_admin(
    provider: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_super_admin_role)
):
    """Obtiene precios de modelos por proveedor (solo super administradores)"""
    return crud.get_model_pricing_by_provider(db, provider)

@app.put("/admin/model-pricing/{pricing_id}/", response_model=schemas.ModelPricing, tags=["Super Admin"])
def update_model_pricing_admin(
    pricing_id: int,
    pricing_update: schemas.ModelPricingUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_super_admin_role)
):
    """Actualiza el precio de un modelo (solo super administradores)"""
    # Agregar quién hizo el cambio
    pricing_update.updated_by = current_user.email
    
    updated_pricing = crud.update_model_pricing(db, pricing_id, pricing_update)
    if not updated_pricing:
        raise HTTPException(status_code=404, detail="Precio de modelo no encontrado")
    
    return updated_pricing

@app.post("/admin/model-pricing/bulk-update/", tags=["Super Admin"])
def bulk_update_model_pricing_admin(
    bulk_update: schemas.ModelPricingBulkUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_super_admin_role)
):
    """Actualiza múltiples precios a la vez (solo super administradores)"""
    # Asegurar que se registre quién hizo el cambio
    bulk_update.updated_by = current_user.email
    
    result = crud.bulk_update_model_pricing(db, bulk_update.pricing_updates, bulk_update.updated_by)
    
    return {
        "success": True,
        "message": f"Se actualizaron {result['updated_count']} precios",
        "updated_by": bulk_update.updated_by,
        "updated_at": datetime.utcnow().isoformat()
    }

@app.post("/admin/model-pricing/initialize/", tags=["Super Admin"])
def initialize_model_pricing_admin(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_super_admin_role)
):
    """Inicializa los precios por defecto si no existen (solo super administradores)"""
    initialized = crud.initialize_default_model_pricing(db)
    
    if initialized:
        return {
            "success": True,
            "message": "Precios inicializados correctamente",
            "initialized_by": current_user.email
        }
    else:
        return {
            "success": False,
            "message": "Los precios ya están inicializados"
        }

