# app/core/database.py - VERSÃO CORRIGIDA
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings
import logging

# Configurar logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO if settings.DEBUG else logging.WARNING)

# Engine do SQLAlchemy com configurações otimizadas
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Dependency para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para testar conexão
def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"Erro de conexão com banco: {e}")
        return False
