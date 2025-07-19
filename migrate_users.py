#!/usr/bin/env python3
"""
Script para migrar usuarios existentes y crear el primer super administrador.
Ejecutar después de actualizar el modelo de User con el campo 'role'.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

# Añadir el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models import User, UserRole
from app.database import get_db
from app.security import get_password_hash

def migrate_database():
    """Migra la base de datos para añadir el campo role"""
    
    # Configuración de la base de datos (usar las mismas variables de entorno)
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db/bytchat")
    
    engine = create_engine(DATABASE_URL)
    
    try:
        # Verificar si la columna role ya existe
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'role'
            """))
            
            if result.fetchone():
                print("✅ La columna 'role' ya existe en la tabla users")
            else:
                # Añadir la columna role
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL
                """))
                conn.commit()
                print("✅ Columna 'role' añadida exitosamente")
                
    except Exception as e:
        print(f"❌ Error al migrar la base de datos: {e}")
        return False
    
    return True

def create_super_admin():
    """Crea el primer super administrador"""
    
    # Configuración
    SUPER_ADMIN_EMAIL = os.getenv("SUPER_ADMIN_EMAIL", "admin@bytcode.tech")
    SUPER_ADMIN_PASSWORD = os.getenv("SUPER_ADMIN_PASSWORD", "admin123")
    
    print(f"🔧 Creando super administrador: {SUPER_ADMIN_EMAIL}")
    
    # Crear sesión de base de datos
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db/bytchat")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        # Verificar si ya existe un super administrador
        existing_admin = db.query(User).filter(User.role == UserRole.SUPER_ADMIN).first()
        
        if existing_admin:
            print(f"⚠️  Ya existe un super administrador: {existing_admin.email}")
            return True
        
        # Verificar si el usuario ya existe
        existing_user = db.query(User).filter(User.email == SUPER_ADMIN_EMAIL).first()
        
        if existing_user:
            # Actualizar el usuario existente a super administrador
            existing_user.role = UserRole.SUPER_ADMIN
            existing_user.is_approved = True
            existing_user.is_active = True
            existing_user.approved_at = datetime.now(timezone.utc)
            existing_user.approved_by = "system"
            print(f"✅ Usuario existente {SUPER_ADMIN_EMAIL} actualizado a super administrador")
        else:
            # Crear nuevo super administrador
            hashed_password = get_password_hash(SUPER_ADMIN_PASSWORD)
            super_admin = User(
                email=SUPER_ADMIN_EMAIL,
                hashed_password=hashed_password,
                role=UserRole.SUPER_ADMIN,
                is_approved=True,
                is_active=True,
                approved_at=datetime.now(timezone.utc),
                approved_by="system"
            )
            db.add(super_admin)
            print(f"✅ Nuevo super administrador creado: {SUPER_ADMIN_EMAIL}")
        
        db.commit()
        print(f"🔑 Credenciales del super administrador:")
        print(f"   Email: {SUPER_ADMIN_EMAIL}")
        print(f"   Password: {SUPER_ADMIN_PASSWORD}")
        print(f"   ⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear super administrador: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def update_existing_users():
    """Actualiza usuarios existentes para asignarles el rol por defecto"""
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db/bytchat")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        # Obtener usuarios sin rol asignado
        users_without_role = db.query(User).filter(User.role.is_(None)).all()
        
        if users_without_role:
            print(f"🔄 Actualizando {len(users_without_role)} usuarios existentes...")
            
            for user in users_without_role:
                user.role = UserRole.USER
                print(f"   - {user.email} -> rol: USER")
            
            db.commit()
            print("✅ Usuarios existentes actualizados")
        else:
            print("✅ Todos los usuarios ya tienen rol asignado")
            
        return True
        
    except Exception as e:
        print(f"❌ Error al actualizar usuarios existentes: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Función principal del script"""
    print("🚀 Iniciando migración de usuarios y creación de super administrador...")
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    # Paso 1: Migrar la base de datos
    if not migrate_database():
        print("❌ Falló la migración de la base de datos")
        return
    
    # Paso 2: Actualizar usuarios existentes
    if not update_existing_users():
        print("❌ Falló la actualización de usuarios existentes")
        return
    
    # Paso 3: Crear super administrador
    if not create_super_admin():
        print("❌ Falló la creación del super administrador")
        return
    
    print("\n🎉 ¡Migración completada exitosamente!")
    print("\n📋 Resumen de cambios:")
    print("   ✅ Campo 'role' añadido a la tabla users")
    print("   ✅ Usuarios existentes actualizados con rol 'USER'")
    print("   ✅ Super administrador creado")
    print("\n🔐 Ahora solo los usuarios con rol ADMIN o SUPER_ADMIN pueden acceder al panel de administración")

if __name__ == "__main__":
    main() 