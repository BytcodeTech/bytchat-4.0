from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Configuración de la Base de Datos leída desde .env
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # Variables para Docker Compose (PostgreSQL)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "bytchat"
    DATABASE_URL: str = "postgresql://postgres:postgres@db/bytchat"

    # Variables para el Super Administrador
    SUPER_ADMIN_EMAIL: str = "admin@bytcode.tech"
    SUPER_ADMIN_PASSWORD: str = "admin123"

    # Variables de la Aplicación
    SECRET_KEY: str = "un_secreto_muy_secreto_para_el_token"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Variables de Redis
    REDIS_URL: str = "redis://redis:6379"

    # API Keys de los Modelos leídas desde .env
    # (Asegúrate de añadirlas a tu archivo .env)
    GOOGLE_API_KEY: str
    OPENAI_API_KEY: str
    DEEPSEEK_API_KEY: str

    # URLs para los servicios de Celery y Redis
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # Construye la URL completa de la base de datos
    @property
    def DATABASE_URL_COMPUTED(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@db:5432/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

# Creamos una única instancia de la configuración para usar en toda la app
settings = Settings()
