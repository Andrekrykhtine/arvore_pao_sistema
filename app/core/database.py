from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Engine com configurações otimizadas
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,
    max_overflow=10,
    echo=settings.DEBUG
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para todos os modelos
Base = declarative_base()

def get_db():
    """Dependency para FastAPI - fornece sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão do banco: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def test_connection() -> bool:
    """Testar conexão com o banco"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            if row[0] == 1:
                logger.info("✅ Conexão com banco funcionando")
                return True
    except Exception as e:
        logger.error(f"❌ Erro de conexão: {e}")
        return False
    
    return False

def create_tables():
    """Criar todas as tabelas definidas nos modelos"""
    try:
        # Importar todos os modelos para registrá-los
        from app.models import produtos  # noqa
        
        # Criar tabelas
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tabelas criadas com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        return False

def get_table_info():
    """Obter informações das tabelas"""
    try:
        with engine.connect() as connection:
            # Listar tabelas
            tables_result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in tables_result.fetchall()]
            
            # Contar registros em cada tabela
            table_counts = {}
            for table in tables:
                count_result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                table_counts[table] = count_result.fetchone()[0]
            
            return {
                "tables": tables,
                "counts": table_counts,
                "total_tables": len(tables)
            }
    except Exception as e:
        logger.error(f"Erro ao obter info das tabelas: {e}")
        return {"error": str(e)}