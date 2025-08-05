import os
from typing import List, Optional
from pathlib import Path

class Settings:
    """Configurações principais do sistema"""
    
    # === INFORMAÇÕES DO PROJETO ===
    PROJECT_NAME: str = "Sistema Árvore Pão"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "Sistema integrado de gestão para Árvore Pão"
    
    # === DATABASE ===
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:123456@db:5432/arvore_pao")
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "arvore_pao")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "123456")
    
    # === API ===
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # === SECURITY ===
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 dias
    
    # === CORS ===
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://localhost:8000"
    ).split(",")
    
    # === UPLOAD ===
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "./temp")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS: List[str] = os.getenv(
        "ALLOWED_EXTENSIONS", 
        "xml,pdf,jpg,png"
    ).split(",")
    
    # === N8N INTEGRATION ===
    N8N_URL: str = os.getenv("N8N_URL", "http://n8n:5678")
    N8N_WEBHOOK_URL: str = os.getenv("N8N_WEBHOOK_URL", "http://n8n:5678/webhook")
    N8N_USERNAME: str = os.getenv("N8N_USERNAME", "admin")
    N8N_PASSWORD: str = os.getenv("N8N_PASSWORD", "password")
    
    # === LOGGING ===
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/arvore_pao.log")
    
    # === PATHS ===
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STATIC_DIR: Path = BASE_DIR / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    
    def __init__(self):
        """Inicializar e validar configurações"""
        self.create_directories()
        self.validate_settings()
    
    def create_directories(self):
        """Criar diretórios necessários"""
        directories = [
            self.UPLOAD_DIR,
            self.TEMP_DIR,
            os.path.dirname(self.LOG_FILE),
            str(self.STATIC_DIR),
            str(self.TEMPLATES_DIR)
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def validate_settings(self):
        """Validar configurações críticas"""
        if self.ENVIRONMENT == "production":
            if "development" in self.SECRET_KEY.lower():
                raise ValueError("🚨 SECRET_KEY de desenvolvimento não pode ser usada em produção!")
            
            if self.DEBUG:
                raise ValueError("🚨 DEBUG deve ser False em produção!")
    
    @property
    def database_url_sync(self) -> str:
        """URL do banco para conexões síncronas"""
        return self.DATABASE_URL.replace("postgresql://", "postgresql://")
    
    @property
    def database_url_async(self) -> str:
        """URL do banco para conexões assíncronas"""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Instância global das configurações
settings = Settings()


