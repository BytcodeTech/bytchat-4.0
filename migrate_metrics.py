#!/usr/bin/env python3
"""
Script de migración para implementar el sistema de métricas y analíticas en Bytchat 4.0
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app import models, schemas
from sqlalchemy import text
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_metrics_tables():
    """Crea las nuevas tablas de métricas en la base de datos"""
    logger.info("🔄 Creando tablas de métricas...")
    
    try:
        # Esto creará todas las tablas definidas en models.py que no existan
        models.Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas de métricas creadas exitosamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {e}")
        return False

def create_default_plans_for_existing_users():
    """Crea planes por defecto para usuarios existentes"""
    logger.info("🔄 Creando planes por defecto para usuarios existentes...")
    
    db = SessionLocal()
    try:
        # Obtener todos los usuarios que no tienen plan
        users_without_plan = db.query(models.User).outerjoin(models.UserPlan).filter(
            models.UserPlan.id == None
        ).all()
        
        plans_created = 0
        for user in users_without_plan:
            # Crear plan gratuito por defecto
            user_plan = models.UserPlan(
                user_id=user.id,
                plan_type=models.PlanType.FREE,
                tokens_included=100000,
                tokens_remaining=100000,
                monthly_price=0,
                overage_rate=15,  # $0.15 per 1K tokens en centavos/100
                current_period_end=datetime.utcnow() + timedelta(days=30)
            )
            db.add(user_plan)
            plans_created += 1
        
        db.commit()
        logger.info(f"✅ Planes creados para {plans_created} usuarios existentes")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creando planes por defecto: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def migrate_existing_chat_logs():
    """Migra los logs existentes de chat_metrics.log a la nueva tabla de analíticas"""
    logger.info("🔄 Migrando logs existentes de chat...")
    
    db = SessionLocal()
    try:
        # Verificar si existe el archivo de logs
        if not os.path.exists('chat_metrics.log'):
            logger.info("📝 No se encontró chat_metrics.log, saltando migración de logs")
            return True
        
        events_migrated = 0
        with open('chat_metrics.log', 'r') as f:
            for line in f:
                try:
                    # Parsear línea: "2025-07-03T04:12:58.634693 | bot_id=6 | userAnonId=2qty4kyiw3x1751515978494 | mensaje=hola"
                    parts = line.strip().split(' | ')
                    if len(parts) >= 4:
                        timestamp_str = parts[0]
                        bot_id_str = parts[1].split('=')[1]
                        user_anon_id = parts[2].split('=')[1]
                        mensaje = parts[3].split('=', 1)[1]
                        
                        # Convertir timestamp
                        timestamp = datetime.fromisoformat(timestamp_str)
                        
                        # Crear evento analítico
                        event = models.AnalyticsEvent(
                            bot_id=int(bot_id_str),
                            event_type=models.EventType.CHAT_MESSAGE,
                            event_data=f'{{"query": "{mensaje}", "migrated_from_log": true}}',
                            user_anon_id=user_anon_id,
                            created_at=timestamp
                        )
                        db.add(event)
                        events_migrated += 1
                        
                except Exception as e:
                    logger.warning(f"⚠️  Error procesando línea de log: {e}")
                    continue
        
        db.commit()
        logger.info(f"✅ {events_migrated} eventos migrados desde chat_metrics.log")
        
        # Crear backup del archivo original
        backup_name = f'chat_metrics_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        os.rename('chat_metrics.log', backup_name)
        logger.info(f"📦 Backup creado: {backup_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error migrando logs: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def verify_migration():
    """Verifica que la migración se haya completado correctamente"""
    logger.info("🔍 Verificando migración...")
    
    db = SessionLocal()
    try:
        # Verificar tablas creadas
        table_checks = {
            "user_plans": models.UserPlan,
            "token_usage": models.TokenUsage,
            "billing_records": models.BillingRecord,
            "analytics_events": models.AnalyticsEvent
        }
        
        for table_name, model_class in table_checks.items():
            count = db.query(model_class).count()
            logger.info(f"📊 Tabla {table_name}: {count} registros")
        
        # Verificar usuarios con planes
        users_with_plans = db.query(models.UserPlan).count()
        total_users = db.query(models.User).count()
        logger.info(f"👥 {users_with_plans}/{total_users} usuarios tienen planes asignados")
        
        # Verificar eventos migrados
        migrated_events = db.query(models.AnalyticsEvent).filter(
            models.AnalyticsEvent.event_data.like('%migrated_from_log%')
        ).count()
        if migrated_events > 0:
            logger.info(f"📈 {migrated_events} eventos migrados desde logs")
        
        logger.info("✅ Verificación completada")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en verificación: {e}")
        return False
    finally:
        db.close()

def show_next_steps():
    """Muestra los próximos pasos después de la migración"""
    logger.info("\n" + "="*60)
    logger.info("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
    logger.info("="*60)
    logger.info("\n📋 PRÓXIMOS PASOS:")
    logger.info("1. Reiniciar la aplicación para cargar los nuevos modelos")
    logger.info("2. Los usuarios existentes tienen plan GRATUITO por defecto")
    logger.info("3. Las nuevas consultas de usuarios autenticados tendrán tracking")
    logger.info("4. El widget público sigue funcionando sin cambios")
    logger.info("\n🔧 ENDPOINTS DISPONIBLES:")
    logger.info("• GET /users/me/analytics - Dashboard del usuario")
    logger.info("• GET /users/me/plan - Plan actual")
    logger.info("• GET /admin/analytics/overview - Dashboard admin")
    logger.info("\n💡 RECOMENDACIONES:")
    logger.info("• Probar el endpoint /users/me/analytics después del reinicio")
    logger.info("• Verificar que el tracking de tokens funcione en /bots/{id}/chat")
    logger.info("• Los logs antiguos están respaldados automáticamente")

def main():
    """Función principal de migración"""
    logger.info("🚀 Iniciando migración del sistema de métricas...")
    logger.info("="*60)
    
    # Paso 1: Crear tablas
    if not create_metrics_tables():
        logger.error("💥 Falló la creación de tablas. Abortando migración.")
        return False
    
    # Paso 2: Crear planes por defecto
    if not create_default_plans_for_existing_users():
        logger.error("💥 Falló la creación de planes por defecto. Abortando migración.")
        return False
    
    # Paso 3: Migrar logs existentes
    if not migrate_existing_chat_logs():
        logger.error("💥 Falló la migración de logs. Continuando...")
        # No abortamos aquí porque no es crítico
    
    # Paso 4: Verificar migración
    if not verify_migration():
        logger.error("💥 Falló la verificación. Revisar manualmente.")
        return False
    
    # Mostrar próximos pasos
    show_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            logger.info("\n✅ Migración completada exitosamente")
            sys.exit(0)
        else:
            logger.error("\n❌ Migración falló")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Migración cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n💥 Error inesperado: {e}")
        sys.exit(1) 