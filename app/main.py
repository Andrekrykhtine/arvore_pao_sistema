"""
Aplicação Principal - Sistema Árvore Pão
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import engine, Base, test_connection, get_db_info, health_check
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# === CRIAR TABELAS ===
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tabelas criadas/verificadas com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao criar tabelas: {e}")

# === CRIAR APLICAÇÃO ===
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None
)

# === MIDDLEWARE CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === ROUTES PRINCIPAIS ===
@app.get("/")
def read_root():
    """Endpoint raiz - informações básicas"""
    return {
        "message": f"{settings.PROJECT_NAME} está funcionando!",
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "debug": settings.DEBUG
    }

@app.get("/health")
def health_check_endpoint():
    """Health check completo do sistema"""
    db_health = health_check()
    
    return {
        "status": "healthy" if db_health["database"] == "healthy" else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "environment": settings.ENVIRONMENT,
        "version": settings.PROJECT_VERSION,
        "database": db_health,
        "services": {
            "api": "running",
            "database": db_health["database"]
        }
    }

@app.get("/config")
def get_config():
    """Informações de configuração (apenas development)"""
    if settings.ENVIRONMENT != "development":
        return JSONResponse(
            status_code=403,
            content={"error": "Endpoint disponível apenas em development"}
        )
    
    return {
        "project": {
            "name": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION,
            "environment": settings.ENVIRONMENT
        },
        "database": {
            "host": settings.DB_HOST,
            "port": settings.DB_PORT,
            "name": settings.DB_NAME,
            "user": settings.DB_USER
        },
        "api": {
            "host": settings.API_HOST,
            "port": settings.API_PORT,
            "debug": settings.DEBUG
        },
        "directories": {
            "upload": settings.UPLOAD_DIR,
            "temp": settings.TEMP_DIR,
            "log": settings.LOG_FILE
        }
    }

# === ERROR HANDLERS ===
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erro global: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Erro interno do servidor", "detail": str(exc) if settings.DEBUG else None}
    )

# === STARTUP EVENTS ===
@app.on_event("startup")
async def startup_event():
    """Eventos de inicialização"""
    logger.info(f"🚀 Iniciando {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
    logger.info(f"🔧 Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"🔍 Debug: {settings.DEBUG}")
    
    # Testar conexão com banco
    if test_connection():
        logger.info("✅ Conexão com banco estabelecida")
    else:
        logger.error("❌ Falha na conexão com banco")

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos de finalização"""
    logger.info("🛑 Finalizando aplicação...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG
    )
EOF