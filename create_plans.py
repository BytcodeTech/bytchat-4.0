#!/usr/bin/env python3
"""
Script para crear los planes de suscripción iniciales
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import crud, schemas, models

def create_initial_plans():
    """Crea los planes iniciales de la plataforma"""
    db = SessionLocal()
    
    try:
        # Verificar si ya existen planes
        existing_plans = crud.get_plans(db)
        if existing_plans:
            print("Los planes ya existen. Saltando creación...")
            return
        
        # Plan Gratuito
        free_plan = schemas.PlanCreate(
            name="Free",
            price=0.0,
            currency="PEN",
            interval="month",
            max_bots=1,
            max_documents=5,
            max_messages_per_month=100,
            features={
                "chat_widget": True,
                "basic_analytics": False,
                "priority_support": False,
                "api_access": False,
                "white_label": False
            }
        )
        
        # Plan Pro
        pro_plan = schemas.PlanCreate(
            name="Pro",
            price=29.90,
            currency="PEN",
            interval="month",
            max_bots=5,
            max_documents=50,
            max_messages_per_month=5000,
            features={
                "chat_widget": True,
                "basic_analytics": True,
                "priority_support": True,
                "api_access": True,
                "white_label": False
            }
        )
        
        # Plan Enterprise
        enterprise_plan = schemas.PlanCreate(
            name="Enterprise",
            price=99.90,
            currency="PEN",
            interval="month",
            max_bots=20,
            max_documents=200,
            max_messages_per_month=25000,
            features={
                "chat_widget": True,
                "basic_analytics": True,
                "priority_support": True,
                "api_access": True,
                "white_label": True
            }
        )
        
        # Crear planes en la base de datos
        crud.create_plan(db, free_plan)
        crud.create_plan(db, pro_plan)
        crud.create_plan(db, enterprise_plan)
        
        print("✅ Planes creados exitosamente:")
        print("   - Free: S/ 0.00/mes")
        print("   - Pro: S/ 29.90/mes")
        print("   - Enterprise: S/ 99.90/mes")
        
    except Exception as e:
        print(f"❌ Error al crear planes: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_plans() 