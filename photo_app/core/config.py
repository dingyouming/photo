from typing import List

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Photo Management System"
    DEBUG: bool = False
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
    DB_TYPE: str = "sqlite"  # or "oracle"
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = ""
    DB_PORT: str = ""
    DB_SERVICE: str = ""
    DB_PATH: str = "/data/photos.db"  # for SQLite
    
    @validator("DB_PATH")
    def validate_db_path(cls, v, values):
        if values.get("DB_TYPE") == "sqlite" and not v:
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
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
