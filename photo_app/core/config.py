from typing import List
import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "Photo Management System"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"
    DOCS_URL: str = "/api/docs"
    REDOC_URL: str = "/api/redoc"
    
    # Security
    SECRET_KEY: str
    ALLOWED_HOSTS: List[str] = ["*"]
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str
    DB_TYPE: str = "sqlite"  # or "oracle"
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = ""
    DB_PORT: str = ""
    DB_SERVICE: str = ""
    DB_PATH: str = "./data/photos.db"  # for SQLite
    
    # User Management
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = True
    
    @field_validator("DB_PATH")
    @classmethod
    def validate_db_path(cls, v: str, values) -> str:
        if values.data.get("DB_TYPE") == "sqlite" and not v:
            raise ValueError("DB_PATH is required for SQLite")
        return v
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Storage
    STORAGE_PATH: str = "/data/photos"
    TEMP_PATH: str = "/data/temp"
    CACHE_PATH: str = "/data/cache"
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    JAEGER_ENABLED: bool = False
    JAEGER_AGENT_HOST: str = ""
    JAEGER_AGENT_PORT: int = 6831
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
