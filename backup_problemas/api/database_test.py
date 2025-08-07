from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.models.produtos import Produto
from datetime import datetime

router = APIRouter(prefix="/database-test", tags=["Database Tests"])

@router.get("/connection")
def test_sqlalchemy_connection(db: Session = Depends(get_db)):
    """🔗 Testar conexão SQLAlchemy"""
    try:
        # Teste básico
        result = db.execute(text("SELECT 1 as test")).fetchone()
        
        # Teste de consulta
        produto_count = db.query(Produto).count()
        
        return {
            "status": "✅ Conexão SQLAlchemy OK",
            "test_query": result[0],
            "total_produtos": produto_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "❌ Erro na conexão",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/produtos")
def list_produtos(db: Session = Depends(get_db)):
    """📦 Listar produtos via SQLAlchemy"""
    try:
        produtos = db.query(Produto).limit(5).all()
        
        return {
            "status": "✅ Consulta OK",
            "total_encontrados": len(produtos),
            "produtos": [
                {
                    "id": p.id,
                    "nome": p.nome,
                    "categoria": p.categoria,
                    "quantidade": p.quantidade_atual
                } for p in produtos
            ]
        }
    except Exception as e:
        return {
            "status": "❌ Erro na consulta",
            "error": str(e)
        }

@router.post("/produtos/test")
def create_test_produto(db: Session = Depends(get_db)):
    """✏️ Criar produto de teste via SQLAlchemy"""
    try:
        produto = Produto(
            nome=f"Produto Teste {datetime.now().strftime('%H%M%S')}",
            categoria="Teste SQLAlchemy",
            unidade_medida="un",
            quantidade_atual=10.0,
            ativo=True
        )
        
        db.add(produto)
        db.commit()
        db.refresh(produto)
        
        return {
            "status": "✅ Produto criado",
            "produto_id": produto.id,
            "produto_nome": produto.nome,
            "created_at": produto.created_at.isoformat()
        }
    except Exception as e:
        db.rollback()
        return {
            "status": "❌ Erro ao criar produto",
            "error": str(e)
        }
