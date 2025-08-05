from fastapi import FastAPI, Depends
from app.core.config import settings
from app.core.database import test_connection, create_tables, get_table_info
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION
)

@app.get("/")
def read_root():
    return {
        "message": f"{settings.PROJECT_NAME} está funcionando!",
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
def health_check():
    db_connected = test_connection()
    table_info = get_table_info()
    
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "database": "connected" if db_connected else "disconnected",
        "tables": table_info,
        "timestamp": datetime.now().isoformat(),
        "version": settings.PROJECT_VERSION
    }

@app.get("/database/info")
def database_info():
    """Informações detalhadas do banco de dados"""
    return {
        "database_url": settings.DATABASE_URL.replace(settings.DB_PASSWORD, "***"),
        "connection_status": "connected" if test_connection() else "disconnected",
        "table_info": get_table_info(),
        "environment": settings.ENVIRONMENT
    }

@app.post("/database/create-tables")
def create_database_tables():
    """Criar tabelas do banco de dados"""
    success = create_tables()
    
    return {
        "success": success,
        "message": "Tabelas criadas com sucesso" if success else "Erro ao criar tabelas",
        "table_info": get_table_info()
    }

@app.on_event("startup")
async def startup_event():
    """Eventos de inicialização"""
    logger.info(f"🚀 Iniciando {settings.PROJECT_NAME}")
    
    # Testar conexão
    if test_connection():
        logger.info("✅ Conexão com banco estabelecida")
        
        # Criar tabelas automaticamente
        if create_tables():
            logger.info("✅ Tabelas verificadas/criadas")
        else:
            logger.error("❌ Erro ao criar tabelas")
    else:
        logger.error("❌ Falha na conexão com banco")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)