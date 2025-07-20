#!/usr/bin/env python3

import sys
import os
sys.path.append('/app')

from app.database import get_db, SessionLocal
from app import crud, models
from app.security import get_password_hash
from app.models import UserRole

# Configuración del super admin desde variables de entorno
SUPER_ADMIN_EMAIL = "admin@bytcode.tech"
SUPER_ADMIN_PASSWORD = "superagente123"

def create_super_admin():
    """Crea el usuario super administrador si no existe"""
    db = SessionLocal()
    try:
        # Verificar si el usuario ya existe
        existing_user = crud.get_user_by_email(db, email=SUPER_ADMIN_EMAIL)
        
        if existing_user:
            print(f"El usuario {SUPER_ADMIN_EMAIL} ya existe")
            print(f"- Activo: {existing_user.is_active}")
            print(f"- Aprobado: {existing_user.is_approved}")
            print(f"- Rol: {existing_user.role}")
            return existing_user
        
        # Crear el usuario super administrador
        hashed_password = get_password_hash(SUPER_ADMIN_PASSWORD)
        super_admin = models.User(
            email=SUPER_ADMIN_EMAIL,
            hashed_password=hashed_password,
            is_active=True,
            is_approved=True,
            role=UserRole.SUPER_ADMIN
        )
        
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        
        print(f"Usuario super administrador creado exitosamente: {SUPER_ADMIN_EMAIL}")
        print(f"Contraseña: {SUPER_ADMIN_PASSWORD}")
        
        return super_admin
        
    except Exception as e:
        print(f"Error al crear el usuario super administrador: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def list_all_users():
    """Lista todos los usuarios en la base de datos"""
    db = SessionLocal()
    try:
        users = db.query(models.User).all()
        print("\n=== USUARIOS EN LA BASE DE DATOS ===")
        for user in users:
            print(f"Email: {user.email}")
            print(f"  - Activo: {user.is_active}")
            print(f"  - Aprobado: {user.is_approved}")
            print(f"  - Rol: {user.role}")
            print("---")
    except Exception as e:
        print(f"Error al listar usuarios: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=== VERIFICACIÓN Y CREACIÓN DE USUARIO ADMINISTRADOR ===")
    
    # Listar usuarios existentes
    list_all_users()
    
    # Crear super admin si no existe
    create_super_admin()
    
    # Listar usuarios después de la creación
    print("\n=== DESPUÉS DE LA VERIFICACIÓN ===")
    list_all_users() 