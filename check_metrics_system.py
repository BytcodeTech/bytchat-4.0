#!/usr/bin/env python3
"""
Script para verificar el estado del sistema de métricas de Bytchat 4.0
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import models
from app.services.metrics_service import MetricsService
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_tables():
    """Verifica que todas las tablas de métricas existan"""
    logger.info("🔍 Verificando tablas de base de datos...")
    
    db = SessionLocal()
    try:
        tables_status = {}
        
        # Verificar cada tabla
        table_models = {
            "users": models.User,
            "user_plans": models.UserPlan,
            "token_usage": models.TokenUsage,
            "billing_records": models.BillingRecord,
            "analytics_events": models.AnalyticsEvent,
            "bots": models.Bot,
            "bot_model_configs": models.BotModelConfig
        }
        
        for table_name, model_class in table_models.items():
            try:
                count = db.query(model_class).count()
                tables_status[table_name] = {"exists": True, "count": count}
                logger.info(f"✅ {table_name}: {count} registros")
            except Exception as e:
                tables_status[table_name] = {"exists": False, "error": str(e)}
                logger.error(f"❌ {table_name}: ERROR - {e}")
        
        return tables_status
        
    except Exception as e:
        logger.error(f"❌ Error verificando tablas: {e}")
        return {}
    finally:
        db.close()

def check_user_plans():
    """Verifica el estado de los planes de usuarios"""
    logger.info("\n👥 Verificando planes de usuarios...")
    
    db = SessionLocal()
    try:
        total_users = db.query(models.User).count()
        users_with_plans = db.query(models.UserPlan).count()
        
        logger.info(f"📊 Total usuarios: {total_users}")
        logger.info(f"📊 Usuarios con planes: {users_with_plans}")
        
        if users_with_plans < total_users:
            logger.warning(f"⚠️  {total_users - users_with_plans} usuarios sin plan")
        
        # Distribución por tipo de plan
        plan_distribution = db.query(
            models.UserPlan.plan_type,
            db.func.count(models.UserPlan.id).label('count')
        ).group_by(models.UserPlan.plan_type).all()
        
        logger.info("📈 Distribución de planes:")
        for plan_type, count in plan_distribution:
            logger.info(f"   • {plan_type.value}: {count} usuarios")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando planes: {e}")
        return False
    finally:
        db.close()

def check_metrics_service():
    """Verifica que el servicio de métricas funcione correctamente"""
    logger.info("\n🔧 Verificando servicio de métricas...")
    
    db = SessionLocal()
    try:
        metrics_service = MetricsService(db)
        
        # Verificar precios de tokens
        test_costs = metrics_service.calculate_token_cost("openai", "gpt-4", 1000, 500)
        if test_costs[2] > 0:  # total_cost > 0
            logger.info(f"✅ Cálculo de costos funciona: ${test_costs[2]/100:.4f}")
        else:
            logger.warning("⚠️  Cálculo de costos devuelve 0")
        
        # Verificar configuración de planes
        for plan_type in models.PlanType:
            config = metrics_service.PLAN_CONFIGS.get(plan_type)
            if config:
                logger.info(f"✅ Plan {plan_type.value}: {config['bytokens_included']} BytTokens, ${config['monthly_price']/100:.2f}/mes")
            else:
                logger.error(f"❌ Configuración faltante para plan {plan_type.value}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando servicio de métricas: {e}")
        return False
    finally:
        db.close()

def test_plan_creation():
    """Prueba la creación de planes para un usuario de test"""
    logger.info("\n🧪 Probando creación de plan de test...")
    
    db = SessionLocal()
    try:
        # Buscar un usuario existente para test
        test_user = db.query(models.User).first()
        if not test_user:
            logger.warning("⚠️  No hay usuarios para probar")
            return True
        
        metrics_service = MetricsService(db)
        
        # Verificar o crear plan
        user_plan = metrics_service.get_or_create_user_plan(test_user.id)
        
        if user_plan:
            logger.info(f"✅ Plan creado/obtenido para usuario {test_user.email}")
            logger.info(f"   • Tipo: {user_plan.plan_type.value}")
            logger.info(f"   • BytTokens restantes: {user_plan.bytokens_remaining:,}")
            logger.info(f"   • Período actual hasta: {user_plan.current_period_end}")
        else:
            logger.error("❌ No se pudo crear/obtener plan")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de creación de plan: {e}")
        return False
    finally:
        db.close()

def check_analytics_data():
    """Verifica datos de analíticas existentes"""
    logger.info("\n📈 Verificando datos de analíticas...")
    
    db = SessionLocal()
    try:
        # Verificar eventos recientes
        recent_events = db.query(models.AnalyticsEvent).filter(
            models.AnalyticsEvent.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        total_events = db.query(models.AnalyticsEvent).count()
        
        logger.info(f"📊 Total eventos analíticos: {total_events}")
        logger.info(f"📊 Eventos últimos 7 días: {recent_events}")
        
        # Verificar tipos de eventos
        event_types = db.query(
            models.AnalyticsEvent.event_type,
            db.func.count(models.AnalyticsEvent.id).label('count')
        ).group_by(models.AnalyticsEvent.event_type).all()
        
        if event_types:
            logger.info("📋 Tipos de eventos:")
            for event_type, count in event_types:
                logger.info(f"   • {event_type.value}: {count}")
        
        # Verificar uso de tokens
        token_usage_count = db.query(models.TokenUsage).count()
        if token_usage_count > 0:
            logger.info(f"🎯 Registros de uso de tokens: {token_usage_count}")
            
            # Mostrar uso por proveedor
            usage_by_provider = db.query(
                models.TokenUsage.provider,
                db.func.sum(models.TokenUsage.total_tokens).label('total'),
                db.func.count(models.TokenUsage.id).label('requests')
            ).group_by(models.TokenUsage.provider).all()
            
            logger.info("🤖 Uso por proveedor:")
            for provider, tokens, requests in usage_by_provider:
                logger.info(f"   • {provider}: {tokens:,} tokens en {requests} requests")
        else:
            logger.info("📝 Sin registros de uso de tokens (normal en instalación nueva)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando analíticas: {e}")
        return False
    finally:
        db.close()

def show_system_summary():
    """Muestra un resumen del estado del sistema"""
    logger.info("\n" + "="*60)
    logger.info("📋 RESUMEN DEL SISTEMA DE MÉTRICAS")
    logger.info("="*60)
    
    db = SessionLocal()
    try:
        # Estadísticas generales
        total_users = db.query(models.User).count()
        total_bots = db.query(models.Bot).count()
        users_with_plans = db.query(models.UserPlan).count()
        total_usage_records = db.query(models.TokenUsage).count()
        
        logger.info(f"👥 Usuarios totales: {total_users}")
        logger.info(f"🤖 Bots totales: {total_bots}")
        logger.info(f"📋 Usuarios con planes: {users_with_plans}")
        logger.info(f"📊 Registros de uso: {total_usage_records}")
        
        # Estado del sistema
        if users_with_plans == total_users and total_users > 0:
            logger.info("✅ Sistema completamente configurado")
        elif users_with_plans > 0:
            logger.info("⚠️  Sistema parcialmente configurado")
        else:
            logger.info("❌ Sistema necesita configuración")
        
        # Próximos pasos recomendados
        logger.info("\n💡 PRÓXIMOS PASOS RECOMENDADOS:")
        
        if total_usage_records == 0:
            logger.info("• Probar el endpoint /bots/{id}/chat para generar datos de uso")
            logger.info("• Verificar que los conectores de IA funcionen correctamente")
        
        logger.info("• Consultar /users/me/analytics para ver el dashboard")
        logger.info("• Probar upgrade de plan con /users/me/plan/upgrade")
        
        if total_users > 0:
            logger.info("• Los administradores pueden ver /admin/analytics/overview")
        
    except Exception as e:
        logger.error(f"❌ Error generando resumen: {e}")
    finally:
        db.close()

def main():
    """Función principal de verificación"""
    logger.info("🔍 VERIFICANDO SISTEMA DE MÉTRICAS DE BYTCHAT 4.0")
    logger.info("="*60)
    
    all_checks_passed = True
    
    # Verificación 1: Tablas de base de datos
    tables_status = check_database_tables()
    if not tables_status:
        all_checks_passed = False
    
    # Verificación 2: Planes de usuarios
    if not check_user_plans():
        all_checks_passed = False
    
    # Verificación 3: Servicio de métricas
    if not check_metrics_service():
        all_checks_passed = False
    
    # Verificación 4: Test de creación de plan
    if not test_plan_creation():
        all_checks_passed = False
    
    # Verificación 5: Datos de analíticas
    if not check_analytics_data():
        all_checks_passed = False
    
    # Resumen final
    show_system_summary()
    
    if all_checks_passed:
        logger.info("\n✅ TODAS LAS VERIFICACIONES PASARON")
        logger.info("🚀 El sistema de métricas está listo para usar")
    else:
        logger.info("\n⚠️  ALGUNAS VERIFICACIONES FALLARON")
        logger.info("🔧 Revisar los errores anteriores y ejecutar migrate_metrics.py si es necesario")
    
    return all_checks_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Verificación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n💥 Error inesperado: {e}")
        sys.exit(1) 