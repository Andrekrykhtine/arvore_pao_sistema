# app/core/config.py - VERSÃO CORRIGIDA
import os
from typing import Optional

class Settings:
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:123456@db:5432/arvore_pao"
    )
    
    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "4QbeHdNgtg42fSdYcqEHEgafyn8P-80h95_ngHAYVpg" + "x" * 32  # Garante que a chave tenha 32 caracteres
    )
        # Validar se a chave é segura
    def __post_init__(self):
        if self.ENVIRONMENT == "production" and "dev_key" in self.SECRET_KEY:
            raise ValueError("🚨 SECRET_KEY padrão não pode ser usada em produção!")
    
    # Upload
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))
    ALLOWED_EXTENSIONS: str = os.getenv("ALLOWED_EXTENSIONS", "xml,pdf")
    
    # N8N (para futuro uso)
    N8N_URL: str = os.getenv("N8N_URL", "http://localhost:5678")
    N8N_WEBHOOK_URL: str = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook")

settings = Settings()
