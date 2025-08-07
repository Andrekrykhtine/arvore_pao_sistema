from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import QueuePool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# ✅ Engine simples e robusto
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5,
    max_overflow=10,
    echo=False
)

# ✅ SessionLocal simples
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

Base = declarative_base()

# ✅ get_db() SIMPLIFICADO - sem testes que podem falhar
def get_db():
    """Dependency simplificada para database"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def test_connection():
    """Testar conexão"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return result.fetchone()[0] == 1
    except Exception as e:
        logger.error(f"❌ Erro de conexão: {e}")
        return False
