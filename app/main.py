# Corrigir main.py com imports organizados no topo
from __future__ import annotations

# ✅ IMPORTS PADRÃO
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging
from datetime import datetime
from typing import List, Optional
import math

# ✅ IMPORTS DA APLICAÇÃO - MOVIDOS PARA O TOPO
from app.schemas.produtos import ProdutoCreate, ProdutoUpdate, ProdutoResponse
from app.services.produtos import ProdutoService
from app.core.database import get_db

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar config
try:
    from app.core.config import settings
    PROJECT_NAME = settings.PROJECT_NAME
    VERSION = settings.PROJECT_VERSION
    logger.info(f"✅ Config carregado: {PROJECT_NAME}")
except Exception as e:
    logger.error(f"❌ Config erro: {e}")
    PROJECT_NAME = "Sistema Árvore Pão"
    VERSION = "1.0.0"

app = FastAPI(
    title=f"🍞 {PROJECT_NAME}",
    version=VERSION,
    description="Sistema Integrado de Gestão para Árvore Pão - Imports Corrigidos"
)

@app.get("/")
def read_root():
    return {
        "message": f"🍞 {PROJECT_NAME} funcionando!",
        "version": VERSION,
        "status": "passo 4 - CRUD com imports corrigidos",
        "features": ["config", "database", "schemas", "crud-endpoints"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
def health_check():
    db_status = "unknown"
    schemas_status = "unknown"
    crud_status = "unknown"
    
    try:
        from app.core.database import test_connection
        db_connected = test_connection()
        db_status = "connected" if db_connected else "disconnected"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"
    
    # ✅ Schemas já importados no topo
    schemas_status = "loaded"
    
    # ✅ Services já importados no topo
    crud_status = "loaded"
    
    return {
        "status": "healthy",
        "database": db_status,
        "schemas": schemas_status,
        "crud_services": crud_status,
        "version": VERSION,
        "passo": "4 - CRUD com imports corrigidos",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test")
def test_endpoint():
    return {
        "test": "funcionando",
        "config": PROJECT_NAME,
        "passo": "4 - imports corrigidos",
        "timestamp": datetime.now().isoformat()
    }

# ============ ENDPOINTS CRUD CORRIGIDOS ============

@app.get("/api/v1/produtos/", response_model=dict)
def listar_produtos(
    busca: Optional[str] = Query(None, description="Buscar por nome ou unidade"),
    ativo: Optional[bool] = Query(True, description="Filtrar produtos ativos/inativos"),
    estoque_baixo: Optional[bool] = Query(None, description="Apenas produtos com estoque baixo"),
    pagina: int = Query(1, ge=1, description="Número da página"),
    por_pagina: int = Query(20, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db)
):
    """📋 Listar produtos com filtros e paginação"""
    try:
        # ✅ CORREÇÃO: ProdutoService já importado no topo
        service = ProdutoService(db)
        produtos, total = service.listar_produtos(
            busca=busca,
            ativo=ativo,
            estoque_baixo=estoque_baixo,
            pagina=pagina,
            por_pagina=por_pagina
        )
        
        total_paginas = math.ceil(total / por_pagina)
        
        return {
            "produtos": produtos,
            "paginacao": {
                "total_produtos": total,
                "pagina_atual": pagina,
                "por_pagina": por_pagina,
                "total_paginas": total_paginas,
                "tem_proxima": pagina < total_paginas,
                "tem_anterior": pagina > 1
            },
            "filtros_aplicados": {
                "busca": busca,
                "ativo": ativo,
                "estoque_baixo": estoque_baixo
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar produtos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/api/v1/produtos/", response_model=dict)
def criar_produto(
    produto_data: ProdutoCreate,
    db: Session = Depends(get_db)
):
    """🆕 Criar novo produto com tratamento robusto de erro"""
    try:
        logger.info(f"📥 Recebendo requisição POST: {produto_data}")
        
        # ✅ Validação básica
        if not produto_data.nome or len(produto_data.nome.strip()) == 0:
            logger.warning("❌ Nome vazio na requisição")
            raise HTTPException(status_code=400, detail="Nome do produto é obrigatório")
        
        # ✅ Criar service e produto
        service = ProdutoService(db)
        logger.info("🔗 Service criado, iniciando criação do produto")
        
        produto_criado = service.criar_produto(produto_data)
        logger.info(f"✅ Produto criado com sucesso: {produto_criado}")
        
        return {
            "success": True,
            "message": f"Produto '{produto_criado['nome']}' criado com sucesso",
            "produto": produto_criado,
            "timestamp": datetime.now().isoformat()
        }
        
    except ValueError as e:
        # Erro de validação de negócio
        logger.warning(f"⚠️ Erro de validação: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # ✅ Erro interno detalhado
        logger.error(f"❌ ERRO INTERNO DETALHADO: {e}")
        logger.error(f"❌ Tipo do erro: {type(e).__name__}")
        
        # Log da stack trace completa
        import traceback
        logger.error(f"❌ Stack trace: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao criar produto: {str(e)}"
        )

@app.get("/api/v1/produtos/{produto_id}", response_model=dict)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    """🔍 Obter produto específico por ID"""
    try:
        # ✅ CORREÇÃO: ProdutoService já importado no topo
        service = ProdutoService(db)
        produto = service.obter_produto(produto_id)
        
        if not produto:
            raise HTTPException(
                status_code=404, 
                detail=f"Produto com ID {produto_id} não encontrado"
            )
        
        return {
            "success": True,
            "produto": produto,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter produto {produto_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/produtos/{produto_id}", response_model=dict)
def atualizar_produto(
    produto_id: int, 
    produto_data: ProdutoUpdate,
    db: Session = Depends(get_db)
):
    """✏️ Atualizar produto existente"""
    try:
        # ✅ CORREÇÃO: ProdutoService já importado no topo
        service = ProdutoService(db)
        produto_atualizado = service.atualizar_produto(produto_id, produto_data)
        
        if not produto_atualizado:
            raise HTTPException(
                status_code=404,
                detail=f"Produto com ID {produto_id} não encontrado"
            )
        
        return {
            "success": True,
            "message": f"Produto '{produto_atualizado['nome']}' atualizado com sucesso",
            "produto": produto_atualizado,
            "timestamp": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar produto {produto_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/produtos/{produto_id}")
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    """🗑️ Deletar produto (soft delete)"""
    try:
        # ✅ CORREÇÃO: ProdutoService já importado no topo
        service = ProdutoService(db)
        deletado = service.deletar_produto(produto_id)
        
        if not deletado:
            raise HTTPException(
                status_code=404,
                detail=f"Produto com ID {produto_id} não encontrado"
            )
        
        return {
            "success": True,
            "message": f"Produto com ID {produto_id} deletado com sucesso",
            "produto_id": produto_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar produto {produto_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/produtos/busca/{nome}", response_model=List[dict])
def buscar_produtos_por_nome(nome: str, db: Session = Depends(get_db)):
    """🔍 Buscar produtos por nome"""
    try:
        # ✅ CORREÇÃO: ProdutoService já importado no topo
        service = ProdutoService(db)
        produtos = service.buscar_por_nome(nome)
        
        return produtos
        
    except Exception as e:
        logger.error(f"Erro ao buscar produtos por nome '{nome}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/produtos/stats/resumo")
def estatisticas_produtos(db: Session = Depends(get_db)):
    """📊 Estatísticas resumidas dos produtos"""
    try:
        from sqlalchemy import text
        from app.core.database import engine
        
        with engine.connect() as conn:
            stats = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_produtos,
                    COUNT(*) FILTER (WHERE is_active = true) as produtos_ativos,
                    COUNT(*) FILTER (WHERE quantidade_atual <= 0) as produtos_esgotados,
                    COUNT(*) FILTER (WHERE quantidade_atual <= quantidade_minima AND quantidade_atual > 0) as produtos_estoque_baixo,
                    SUM(quantidade_atual * preco_venda) as valor_total_estoque
                FROM produtos
            """)).fetchone()
            
            return {
                "resumo": {
                    "total_produtos": stats[0],
                    "produtos_ativos": stats[1],
                    "produtos_inativos": stats[0] - stats[1],
                    "produtos_esgotados": stats[2],
                    "produtos_estoque_baixo": stats[3],
                    "valor_total_estoque": float(stats[4] or 0)
                },
                "alertas": {
                    "precisam_reposicao": stats[2] + stats[3],
                    "percentual_ativos": round((stats[1] / stats[0]) * 100, 1) if stats[0] > 0 else 0
                },
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 Iniciando {PROJECT_NAME} - Passo 4 (CRUD com Imports Corrigidos)")
    
    try:
        from app.core.database import test_connection
        if test_connection():
            logger.info("✅ Database conectado")
        else:
            logger.warning("⚠️ Database não conectado")
    except Exception as e:
        logger.error(f"❌ Erro database: {e}")
    
    # ✅ Schemas e Services já importados no topo
    logger.info("✅ Schemas Pydantic carregados")
    logger.info("✅ Services CRUD carregados")
    logger.info("🎊 API CRUD com imports corrigidos pronta para uso!")

logger.info("Aplicação Passo 4 (CRUD com Imports Corrigidos) criada")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

