#!/usr/bin/env python3
"""
Script de migración para implementar el sistema de BytTokens
Agrega los nuevos campos bytokens_included, bytokens_remaining y bytokens_cost
"""

import os
import sys
sys.path.append('.')

from app.database import SessionLocal, engine
from app import models
from app.services.metrics_service import MetricsService, PLAN_CONFIGS_BYTETOKENS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Migrar la base de datos para soportar BytTokens"""
    
    logger.info("🚀 Iniciando migración a sistema BytTokens...")
    
    # Crear todas las tablas con los nuevos campos
    logger.info("📊 Creando/actualizando estructura de tablas...")
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Migrar planes de usuarios existentes
        logger.info("🔄 Migrando planes de usuarios existentes...")
        
        user_plans = db.query(models.UserPlan).all()
        logger.info(f"Encontrados {len(user_plans)} planes de usuario para migrar")
        
        for user_plan in user_plans:
            # Obtener configuración del plan
            plan_config = PLAN_CONFIGS_BYTETOKENS.get(user_plan.plan_type)
            if not plan_config:
                logger.warning(f"No se encontró configuración para plan {user_plan.plan_type}")
                continue
            
            # Actualizar solo si no tiene valores de BytTokens
            if not hasattr(user_plan, 'bytokens_included') or user_plan.bytokens_included is None:
                user_plan.bytokens_included = plan_config["bytokens_included"]
                logger.info(f"✅ Usuario {user_plan.user_id}: bytokens_included = {plan_config['bytokens_included']}")
            
            if not hasattr(user_plan, 'bytokens_remaining') or user_plan.bytokens_remaining is None:
                # Mantener el porcentaje de uso actual
                if hasattr(user_plan, 'tokens_remaining') and hasattr(user_plan, 'tokens_included'):
                    if user_plan.tokens_included > 0:
                        usage_percentage = (user_plan.tokens_included - user_plan.tokens_remaining) / user_plan.tokens_included
                        bytokens_used = int(plan_config["bytokens_included"] * usage_percentage)
                        user_plan.bytokens_remaining = plan_config["bytokens_included"] - bytokens_used
                    else:
                        user_plan.bytokens_remaining = plan_config["bytokens_included"]
                else:
                    user_plan.bytokens_remaining = plan_config["bytokens_included"]
                
                logger.info(f"✅ Usuario {user_plan.user_id}: bytokens_remaining = {user_plan.bytokens_remaining}")
        
        # Migrar registros de TokenUsage existentes
        logger.info("🔄 Calculando BytTokens para registros existentes...")
        
        metrics_service = MetricsService(db)
        token_usages = db.query(models.TokenUsage).filter(
            models.TokenUsage.bytokens_cost == 0  # Solo los que no tienen BytTokens calculados
        ).limit(1000).all()  # Procesar en lotes
        
        logger.info(f"Encontrados {len(token_usages)} registros de TokenUsage para migrar")
        
        for usage in token_usages:
            try:
                # Calcular BytTokens basado en el modelo real
                bytokens_cost = metrics_service.calculate_bytetoken_cost(
                    provider=usage.provider,
                    model_id=usage.model_id,
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens
                )
                
                usage.bytokens_cost = bytokens_cost
                
                if len(token_usages) <= 10:  # Solo mostrar detalles para lotes pequeños
                    logger.info(f"✅ TokenUsage {usage.id}: {usage.total_tokens} tokens = {bytokens_cost} BytTokens")
                
            except Exception as e:
                logger.error(f"❌ Error calculando BytTokens para TokenUsage {usage.id}: {e}")
                usage.bytokens_cost = max(1, usage.total_tokens // 1000)  # Fallback
        
        # Guardar cambios
        logger.info("💾 Guardando cambios en la base de datos...")
        db.commit()
        
        # Mostrar resumen
        logger.info("📊 Resumen de migración:")
        logger.info(f"  - Planes migrados: {len(user_plans)}")
        logger.info(f"  - TokenUsage migrados: {len(token_usages)}")
        
        # Mostrar configuración actual de planes
        logger.info("📋 Configuración de planes BytTokens:")
        for plan_type, config in PLAN_CONFIGS_BYTETOKENS.items():
            dollar_value = config["bytokens_included"] / 1000
            logger.info(f"  - {plan_type.value}: {config['bytokens_included']} BytTokens (${dollar_value})")
        
        logger.info("🎉 Migración completada exitosamente!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error durante la migración: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

def verify_migration():
    """Verificar que la migración fue exitosa"""
    logger.info("🔍 Verificando migración...")
    
    db = SessionLocal()
    try:
        # Verificar que los planes tienen BytTokens
        plans_with_bytokens = db.query(models.UserPlan).filter(
            models.UserPlan.bytokens_included > 0
        ).count()
        
        total_plans = db.query(models.UserPlan).count()
        logger.info(f"✅ Planes con BytTokens: {plans_with_bytokens}/{total_plans}")
        
        # Verificar que los TokenUsage tienen BytTokens
        usages_with_bytokens = db.query(models.TokenUsage).filter(
            models.TokenUsage.bytokens_cost > 0
        ).count()
        
        total_usages = db.query(models.TokenUsage).count()
        logger.info(f"✅ TokenUsage con BytTokens: {usages_with_bytokens}/{total_usages}")
        
        return plans_with_bytokens > 0 or total_plans == 0
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🔄 Migrando BytChat a sistema BytTokens...")
    print("=" * 50)
    
    if migrate_database():
        if verify_migration():
            print("🎉 ¡Migración completada exitosamente!")
            print("💡 El sistema ahora usa BytTokens (1000 BytTokens = $1 USD)")
        else:
            print("⚠️  Migración completada pero falló la verificación")
            sys.exit(1)
    else:
        print("❌ Error durante la migración")
        sys.exit(1) 