from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    APP_NAME: str = "E-Commerce API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/ecommerce_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # PhonePe
    PHONEPE_MERCHANT_ID: str = ""
    PHONEPE_SALT_KEY: str = ""
    PHONEPE_SALT_INDEX: int = 1
    PHONEPE_BASE_URL: str = "https://api-preprod.phonepe.com/apis/pg-sandbox"
    PHONEPE_REDIRECT_URL: str = "http://localhost:8000/api/v1/payments/callback"
    PHONEPE_CALLBACK_URL: str = "http://localhost:8000/api/v1/payments/webhook"

    # Email
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
