from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings
import logging

# Configurar logging do SQLAlchemy
logging.basicConfig()
logger = logging.getLogger(__name__)

if settings.DEBUG:
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# === ENGINE CONFIGURATION ===
engine = create_engine(
    settings.database_url_sync,
    # Pool settings para produção
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
    # Echo SQL queries em development
    echo=settings.DEBUG,
    # Configurações adicionais
    connect_args={
        "options": "-c timezone=America/Sao_Paulo"
    }
)

# === SESSION CONFIGURATION ===
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# === BASE MODEL ===
Base = declarative_base()

# === DEPENDENCY INJECTION ===
def get_db():
    """
    Dependency para FastAPI - fornece sessão do banco
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão do banco: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# === DATABASE UTILITIES ===
def create_tables():
    """Criar todas as tabelas"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tabelas criadas com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        raise

def drop_tables():
    """Dropar todas as tabelas (CUIDADO!)"""
    if settings.ENVIRONMENT == "production":
        raise ValueError("❌ Não é possível dropar tabelas em produção!")
    
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("⚠️ Todas as tabelas foram removidas")
    except Exception as e:
        logger.error(f"❌ Erro ao dropar tabelas: {e}")
        raise

def test_connection() -> bool:
    """Testar conexão com o banco"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            row = result.fetchone()
            if row[0] == 1:
                logger.info("✅ Conexão com banco funcionando")
                return True
    except Exception as e:
        logger.error(f"❌ Erro de conexão com banco: {e}")
        return False
    
    return False

def get_db_info() -> dict:
    """Obter informações do banco"""
    try:
        with engine.connect() as connection:
            # Versão do PostgreSQL
            version_result = connection.execute("SELECT version()")
            version = version_result.fetchone()[0]
            
            # Nome do banco atual
            db_result = connection.execute("SELECT current_database()")
            database = db_result.fetchone()[0]
            
            # Número de conexões ativas
            conn_result = connection.execute(
                "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
            )
            connections = conn_result.fetchone()[0]
            
            return {
                "version": version.split(" ")[1],
                "database": database,
                "active_connections": connections,
                "status": "connected"
            }
    except Exception as e:
        logger.error(f"Erro ao obter info do banco: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

# === EVENT LISTENERS ===
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configurações na conexão (se necessário)"""
    if settings.DEBUG:
        logger.debug("Nova conexão estabelecida com o banco")

# === HEALTH CHECK ===
def health_check() -> dict:
    """Health check do banco para API"""
    if test_connection():
        info = get_db_info()
        return {
            "database": "healthy",
            "info": info
        }
    else:
        return {
            "database": "unhealthy",
            "error": "Não foi possível conectar ao banco"
        }
EOF