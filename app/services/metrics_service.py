"""
Servicio central para métricas, tracking de tokens y facturación
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from .. import models, schemas
from ..models import PlanType, EventType

# Configuración de precios reales de modelos (USD por 1K tokens)
MODEL_PRICING = {
    # OpenAI
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "o1-preview": {"input": 0.015, "output": 0.06},
    "o1-mini": {"input": 0.003, "output": 0.012},
    
    # Google Gemini
    "gemini-pro": {"input": 0.0015, "output": 0.0015},
    "gemini-flash": {"input": 0.00015, "output": 0.0006},
    "gemini-ultra": {"input": 0.003, "output": 0.003},
    
    # DeepSeek
    "deepseek-v2": {"input": 0.0002, "output": 0.0002},
    "deepseek-reasoner": {"input": 0.002, "output": 0.002},
    
    # Valores por defecto para modelos no listados
    "default": {"input": 0.001, "output": 0.001}
}

# Configuración de planes con BytTokens
PLAN_CONFIGS_BYTETOKENS = {
    PlanType.FREE: {
        "bytokens_included": 2000,      # $2 USD valor real
        "monthly_price": 0,
        "overage_rate": 0.001,          # $1 por 1000 BytTokens adicionales
        "max_overage": 1000             # Máximo 1000 BytTokens de overage
    },
    PlanType.PRO: {
        "bytokens_included": 13000,     # $13 USD valor real ($20 con 35% margen)
        "monthly_price": 2000,          # En centavos (20 USD)
        "overage_rate": 0.0012,         # $1.20 por 1000 BytTokens adicionales  
        "max_overage": 10000            # Máximo 10000 BytTokens de overage
    },
    PlanType.ENTERPRISE: {
        "bytokens_included": 80000,     # $80 USD valor real ($100 con 20% margen)
        "monthly_price": 10000,         # En centavos (100 USD)
        "overage_rate": 0.0011,         # $1.10 por 1000 BytTokens adicionales
        "max_overage": 50000            # Máximo 50000 BytTokens de overage
    }
}

class MetricsService:
    """Servicio central para manejo de métricas y facturación"""
    
    # Precios por token en centavos (actualizables desde configuración)
    TOKEN_COSTS = {
        "openai": {
            "gpt-4": {"prompt": 0.003, "completion": 0.006},  # $0.03/$0.06 per 1K tokens
            "gpt-4o": {"prompt": 0.0025, "completion": 0.01},  # $0.025/$0.10 per 1K tokens
            "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},  # $0.0005/$0.0015 per 1K tokens
        },
        "google": {
            "gemini-1.5-pro": {"prompt": 0.00125, "completion": 0.005},  # $0.00125/$0.005 per 1K tokens
            "gemini-1.5-flash": {"prompt": 0.000075, "completion": 0.0003},  # $0.000075/$0.0003 per 1K tokens
            "gemini-1.5-flash-latest": {"prompt": 0.000075, "completion": 0.0003},  # $0.000075/$0.0003 per 1K tokens
            "gemini-1.5-pro-latest": {"prompt": 0.00125, "completion": 0.005},  # $0.00125/$0.005 per 1K tokens
        },
        "deepseek": {
            "deepseek-chat": {"prompt": 0.00014, "completion": 0.00028},  # $0.00014/$0.00028 per 1K tokens
        }
    }
    


    def __init__(self, db: Session):
        self.db = db

    def get_or_create_user_plan(self, user_id: int) -> models.UserPlan:
        """Obtiene o crea el plan de un usuario"""
        user_plan = self.db.query(models.UserPlan).filter(
            models.UserPlan.user_id == user_id
        ).first()
        
        if not user_plan:
            # Crear plan gratuito por defecto
            config = PLAN_CONFIGS_BYTETOKENS[PlanType.FREE]
            user_plan = models.UserPlan(
                user_id=user_id,
                plan_type=PlanType.FREE,
                bytokens_included=config["bytokens_included"],
                bytokens_remaining=config["bytokens_included"],
                monthly_price=config["monthly_price"],
                overage_rate=int(config["overage_rate"] * 1000),  # Convertir a entero
                current_period_end=datetime.utcnow() + timedelta(days=30)
            )
            self.db.add(user_plan)
            self.db.commit()
            self.db.refresh(user_plan)
        
        return user_plan

    def calculate_token_cost(self, provider: str, model_id: str, 
                           prompt_tokens: int, completion_tokens: int) -> Tuple[int, int, int]:
        """
        Calcula el costo de tokens en centavos
        Returns: (prompt_cost, completion_cost, total_cost)
        """
        try:
            costs = self.TOKEN_COSTS.get(provider, {}).get(model_id, {})
            if not costs:
                logging.warning(f"No hay costos definidos para {provider}:{model_id}")
                return 0, 0, 0
            
            # Calcular costos (los precios están por 1K tokens, convertir a centavos)
            prompt_cost = int((prompt_tokens / 1000) * costs["prompt"] * 100)
            completion_cost = int((completion_tokens / 1000) * costs["completion"] * 100)
            total_cost = prompt_cost + completion_cost
            
            return prompt_cost, completion_cost, total_cost
        
        except Exception as e:
            logging.error(f"Error calculando costo de tokens: {e}")
            return 0, 0, 0

    def calculate_bytetoken_cost(self, provider: str, model_id: str, prompt_tokens: int, completion_tokens: int) -> int:
        """
        Calcula el costo en BytTokens basado en precios reales de modelos desde la BD
        1000 BytTokens = $1 USD
        """
        # Intentar obtener precios desde la base de datos
        model_pricing_db = self.db.query(models.ModelPricing).filter(
            models.ModelPricing.provider == provider.lower(),
            models.ModelPricing.model_id == model_id.lower(),
            models.ModelPricing.is_active == True
        ).first()
        
        if model_pricing_db:
            # Usar precios de la base de datos
            input_cost_per_1k = model_pricing_db.input_cost_per_1k
            output_cost_per_1k = model_pricing_db.output_cost_per_1k
        else:
            # Fallback a precios hardcodeados
            model_key = model_id.lower()
            model_pricing = MODEL_PRICING.get(model_key, MODEL_PRICING["default"])
            input_cost_per_1k = model_pricing["input"]
            output_cost_per_1k = model_pricing["output"]
        
        # Calcular costo en USD
        prompt_cost_usd = (prompt_tokens / 1000.0) * input_cost_per_1k
        completion_cost_usd = (completion_tokens / 1000.0) * output_cost_per_1k
        total_cost_usd = prompt_cost_usd + completion_cost_usd
        
        # Convertir a BytTokens (1000 BytTokens = $1 USD)
        bytokens_cost = int(total_cost_usd * 1000)
        
        # Mínimo 1 BytToken para evitar uso "gratis"
        return max(1, bytokens_cost)

    def get_model_info(self, model_id: str) -> dict:
        """
        Obtiene información del modelo incluyendo costos estimados
        """
        model_key = model_id.lower()
        pricing = MODEL_PRICING.get(model_key, MODEL_PRICING["default"])
        
        # Calcular costo promedio por pregunta (estimación: 150 tokens input, 100 tokens output)
        estimated_input = 150
        estimated_output = 100
        estimated_cost_usd = (estimated_input / 1000.0) * pricing["input"] + (estimated_output / 1000.0) * pricing["output"]
        estimated_bytokens = int(estimated_cost_usd * 1000)
        
        return {
            "model_id": model_id,
            "input_cost_per_1k": pricing["input"],
            "output_cost_per_1k": pricing["output"],
            "estimated_cost_per_query_usd": round(estimated_cost_usd, 4),
            "estimated_cost_per_query_bytokens": max(1, estimated_bytokens)
        }

    def check_token_limit(self, user_id: int, tokens_needed: int) -> Dict[str, Any]:
        """
        Verifica si el usuario puede usar los tokens solicitados
        Returns: {"allowed": bool, "remaining": int, "will_overage": bool, "overage_cost": int}
        """
        user_plan = self.get_or_create_user_plan(user_id)
        
        allowed = True
        will_overage = False
        overage_cost = 0
        
        if user_plan.bytokens_remaining >= tokens_needed:
            # Suficientes tokens en el plan
            remaining = user_plan.bytokens_remaining - tokens_needed
        else:
            # Necesitará usar overage
            will_overage = True
            overage_tokens = tokens_needed - user_plan.bytokens_remaining
            overage_cost = int((overage_tokens / 1000) * user_plan.overage_rate)
            remaining = 0
            
            # Para plan gratuito, no permitir overage
            if user_plan.plan_type == PlanType.FREE:
                allowed = False
        
        return {
            "allowed": allowed,
            "remaining": remaining,
            "will_overage": will_overage,
            "overage_cost": overage_cost,
            "overage_tokens": overage_tokens if will_overage else 0
        }

    def record_token_usage(self, 
                          user_id: int, 
                          bot_id: int,
                          user_anon_id: Optional[str],
                          query: str,
                          provider: str,
                          model_id: str,
                          prompt_tokens: int,
                          completion_tokens: int,
                          response_time_ms: Optional[int] = None) -> models.TokenUsage:
        """
        Registra el uso de tokens y actualiza el plan del usuario usando BytTokens
        """
        total_tokens = prompt_tokens + completion_tokens
        
        # Calcular costos en el sistema tradicional (para compatibilidad)
        prompt_cost, completion_cost, total_cost = self.calculate_token_cost(
            provider, model_id, prompt_tokens, completion_tokens
        )
        
        # Calcular costo en BytTokens (nuevo sistema)
        bytokens_cost = self.calculate_bytetoken_cost(
            provider, model_id, prompt_tokens, completion_tokens
        )
        
        # Crear registro de uso
        token_usage = models.TokenUsage(
            user_id=user_id,
            bot_id=bot_id,
            user_anon_id=user_anon_id,
            query=query,
            provider=provider,
            model_id=model_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            prompt_cost=prompt_cost,
            completion_cost=completion_cost,
            total_cost=total_cost,
            bytokens_cost=bytokens_cost,  # Nuevo campo
            response_time_ms=response_time_ms
        )
        
        self.db.add(token_usage)
        
        # Actualizar plan del usuario usando BytTokens
        user_plan = self.get_or_create_user_plan(user_id)
        
        if user_plan.bytokens_remaining >= bytokens_cost:
            # Descontar del plan base
            user_plan.bytokens_remaining -= bytokens_cost
        else:
            # Usar overage
            overage_bytokens = bytokens_cost - user_plan.bytokens_remaining
            user_plan.bytokens_remaining = 0
            user_plan.tokens_overage += overage_bytokens
            user_plan.overage_cost += int((overage_bytokens / 1000) * user_plan.overage_rate)
        
        self.db.commit()
        self.db.refresh(token_usage)
        
        # Registrar evento analítico
        self.record_analytics_event(
            user_id=user_id,
            bot_id=bot_id,
            event_type=EventType.CHAT_MESSAGE,
            event_data=json.dumps({
                "provider": provider,
                "model_id": model_id,
                "total_tokens": total_tokens,
                "total_cost": total_cost
            }),
            user_anon_id=user_anon_id
        )
        
        return token_usage

    def record_analytics_event(self,
                              event_type: EventType,
                              user_id: Optional[int] = None,
                              bot_id: Optional[int] = None,
                              event_data: Optional[str] = None,
                              user_anon_id: Optional[str] = None,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None):
        """Registra un evento analítico"""
        event = models.AnalyticsEvent(
            user_id=user_id,
            bot_id=bot_id,
            event_type=event_type,
            event_data=event_data,
            user_anon_id=user_anon_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(event)
        self.db.commit()

    def get_user_analytics(self, user_id: int) -> Dict[str, Any]:
        """Obtiene analíticas del dashboard para un usuario"""
        user_plan = self.get_or_create_user_plan(user_id)
        
        # Calcular período actual
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Uso de BytTokens este mes (corregido para usar bytokens_cost)
        monthly_usage = self.db.query(func.sum(models.TokenUsage.bytokens_cost)).filter(
            and_(
                models.TokenUsage.user_id == user_id,
                models.TokenUsage.created_at >= month_start
            )
        ).scalar() or 0
        
        # Uso por proveedor (corregido para usar bytokens_cost)
        usage_by_provider = {}
        provider_usage = self.db.query(
            models.TokenUsage.provider,
            func.sum(models.TokenUsage.bytokens_cost).label('total')
        ).filter(
            and_(
                models.TokenUsage.user_id == user_id,
                models.TokenUsage.created_at >= month_start
            )
        ).group_by(models.TokenUsage.provider).all()
        
        for provider, total in provider_usage:
            usage_by_provider[provider] = total
        
        # Actividad diaria últimos 30 días (corregido para usar bytokens_cost)
        thirty_days_ago = now - timedelta(days=30)
        daily_usage = self.db.query(
            func.date(models.TokenUsage.created_at).label('date'),
            func.sum(models.TokenUsage.bytokens_cost).label('bytokens')
        ).filter(
            and_(
                models.TokenUsage.user_id == user_id,
                models.TokenUsage.created_at >= thirty_days_ago
            )
        ).group_by(func.date(models.TokenUsage.created_at)).all()
        
        daily_usage_list = [
            {"date": date.isoformat(), "tokens": bytokens}  # tokens por compatibilidad con frontend
            for date, bytokens in daily_usage
        ]
        
        return {
            "current_plan": {
                "plan_type": user_plan.plan_type.value,
                "monthly_price": user_plan.monthly_price,
                "overage_rate": user_plan.overage_rate,
                "current_period_end": user_plan.current_period_end.isoformat() if user_plan.current_period_end else None,
                # Campos nuevos (BytTokens)
                "bytokens_included": user_plan.bytokens_included,
                "bytokens_remaining": user_plan.bytokens_remaining,
                # Campos deprecated (para compatibilidad con frontend)
                "tokens_included": user_plan.bytokens_included,  # Mapear BytTokens → tokens para compatibilidad
                "tokens_remaining": user_plan.bytokens_remaining,  # Mapear BytTokens → tokens para compatibilidad
            },
            # Campos de nivel superior para compatibilidad
            "tokens_remaining": user_plan.bytokens_remaining,  # Frontend espera esto en nivel superior
            "tokens_included": user_plan.bytokens_included,  # Para compatibilidad completa
            "tokens_used_this_month": monthly_usage,
            "tokens_overage": user_plan.tokens_overage,
            "estimated_overage_cost": user_plan.overage_cost,
            "usage_by_provider": usage_by_provider,
            "daily_usage": daily_usage_list,
            "top_topics": self._get_top_topics(user_id)  # Implementar después
        }

    def _get_top_topics(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Analiza los temas más preguntados por el usuario"""
        # Por ahora devolver datos simulados
        # TODO: Implementar análisis de contenido con NLP
        return [
            {"topic": "programación", "count": 15},
            {"topic": "marketing", "count": 10},
            {"topic": "diseño", "count": 8},
            {"topic": "negocios", "count": 5},
            {"topic": "tecnología", "count": 3}
        ]

    def upgrade_user_plan(self, user_id: int, new_plan_type: PlanType) -> models.UserPlan:
        """Actualiza el plan de un usuario"""
        user_plan = self.get_or_create_user_plan(user_id)
        old_plan = user_plan.plan_type
        
        # Obtener configuración del nuevo plan
        config = PLAN_CONFIGS_BYTETOKENS[new_plan_type]
        
        # Actualizar plan
        user_plan.plan_type = new_plan_type
        user_plan.bytokens_included = config["bytokens_included"]
        user_plan.bytokens_remaining = config["bytokens_included"]
        user_plan.monthly_price = config["monthly_price"]
        user_plan.overage_rate = int(config["overage_rate"] * 1000)
        user_plan.current_period_start = datetime.utcnow()
        user_plan.current_period_end = datetime.utcnow() + timedelta(days=30)
        
        # Reset overage del período anterior
        user_plan.tokens_overage = 0
        user_plan.overage_cost = 0
        
        self.db.commit()
        
        # Registrar evento de upgrade
        self.record_analytics_event(
            user_id=user_id,
            event_type=EventType.PLAN_UPGRADE,
            event_data=json.dumps({
                "old_plan": old_plan.value,
                "new_plan": new_plan_type.value,
                "new_price": config["monthly_price"]
            })
        )
        
        return user_plan 