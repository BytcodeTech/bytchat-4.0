from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings

# Crea el "motor" de la base de datos usando la URL de nuestra configuración
engine = create_engine(settings.DATABASE_URL_COMPUTED)

# Crea una sesión para hablar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Una clase base para nuestros modelos de la base de datos (tablas)
Base = declarative_base()

# Función para obtener una sesión de base de datos en nuestras rutas de API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
