from fastapi import APIRouter
from datetime import datetime
from app.core.config import settings

router = APIRouter()

@router.get("/", tags=["Root"])
def hello_world():
    """
    🌍 Hello World - Endpoint principal da API
    
    Retorna informações básicas do sistema Árvore Pão
    """
    return {
        "message": "🍞 Bem-vindo ao Sistema Árvore Pão!",
        "version": settings.PROJECT_VERSION,
        "status": "funcionando",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "endpoints_disponiveis": {
            "documentacao": "/docs",
            "health_check": "/health",
            "database_info": "/database/info"
        }
    }

@router.get("/hello/{name}", tags=["Saudações"])
def hello_person(name: str):
    """
    👋 Saudação personalizada
    
    - **name**: Nome da pessoa para saudar
    """
    return {
        "message": f"Olá {name}! Bem-vindo à Árvore Pão! 🍞",
        "timestamp": datetime.now().isoformat(),
        "sistema": settings.PROJECT_NAME
    }

@router.get("/info", tags=["Sistema"])
def system_info():
    """
    ℹ️ Informações do sistema
    
    Retorna detalhes técnicos da aplicação
    """
    return {
        "nome": settings.PROJECT_NAME,
        "versao": settings.PROJECT_VERSION,
        "ambiente": settings.ENVIRONMENT,
        "debug_mode": settings.DEBUG,
        "database": {
            "host": settings.DB_HOST,
            "porta": settings.DB_PORT,
            "nome": settings.DB_NAME
        },
        "api": {
            "host": settings.API_HOST,
            "porta": settings.API_PORT
        }
    }