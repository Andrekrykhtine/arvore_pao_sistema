from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List, Optional, Tuple
from app.schemas.produtos import ProdutoCreate, ProdutoUpdate
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProdutoService:
    """Service com nomes de colunas corrigidos para o banco"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def criar_produto(self, produto_data: ProdutoCreate) -> dict:
        """Criar produto com colunas corretas do banco"""
        try:
            logger.info(f"🆕 Criando produto: {produto_data.nome}")
            
            # ✅ Verificar se nome já existe
            existing_check = self.db.execute(text("""
                SELECT COUNT(*) FROM produtos 
                WHERE nome = :nome AND ativo = true
            """), {"nome": produto_data.nome}).scalar()
            
            if existing_check > 0:
                raise ValueError(f"Produto '{produto_data.nome}' já existe")
            
            # ✅ Preparar dados com NOMES CORRETOS das colunas
            insert_params = {
                "nome": str(produto_data.nome).strip(),
                "unidade_medida": getattr(produto_data, 'unidade_medida', 'un'),
                "quantidade_atual": float(getattr(produto_data, 'quantidade_atual', 0.0)),
                "quantidade_minima": float(getattr(produto_data, 'quantidade_minima', 0.0)),
                "preco_venda": float(produto_data.preco_venda),
                "ativo": True,  # ✅ CORREÇÃO: usar 'ativo' ao invés de 'is_active'
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            logger.info(f"📝 Inserindo com dados corretos: {insert_params}")
            
            # ✅ INSERT com nomes corretos das colunas
            result = self.db.execute(text("""
                INSERT INTO produtos (
                    nome, unidade_medida, quantidade_atual, 
                    quantidade_minima, preco_venda, ativo, created_at, updated_at
                )
                VALUES (
                    :nome, :unidade_medida, :quantidade_atual,
                    :quantidade_minima, :preco_venda, :ativo, :created_at, :updated_at
                )
                RETURNING id, nome, unidade_medida, quantidade_atual, 
                         quantidade_minima, preco_venda, ativo, created_at
            """), insert_params)
            
            # ✅ Commit simples
            row = result.fetchone()
            if not row:
                raise Exception("Falha na inserção")
            
            self.db.commit()
            logger.info(f"✅ Produto criado: ID {row[0]}")
            
            return {
                "id": row[0],
                "nome": row[1],
                "unidade_medida": row[2],
                "quantidade_atual": float(row[3] or 0),
                "quantidade_minima": float(row[4] or 0),
                "preco_venda": float(row[5] or 0),
                "is_active": row[6],  # ✅ Converter de 'ativo' para 'is_active' na resposta
                "created_at": row[7]
            }
                
        except ValueError as e:
            logger.warning(f"⚠️ Validação: {e}")
            raise e
        except Exception as e:
            try:
                self.db.rollback()
                logger.error(f"🔄 Rollback: {e}")
            except:
                pass
            
            error_msg = f"Erro ao criar produto: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def listar_produtos(self, 
                       busca: Optional[str] = None,
                       ativo: Optional[bool] = True,
                       estoque_baixo: Optional[bool] = None,
                       pagina: int = 1, 
                       por_pagina: int = 20) -> Tuple[List[dict], int]:
        """Listar produtos com nomes corretos das colunas"""
        try:
            where_conditions: List[str] = []
            params: Dict[str, Any] = {}
            
            if ativo is not None:
                where_conditions.append("ativo = :ativo")  # ✅ usar 'ativo' ao invés de 'is_active'
                params["ativo"] = ativo
            
            if busca:
                where_conditions.append("(nome ILIKE :busca OR unidade_medida ILIKE :busca)")
                params["busca"] = f"%{busca}%"
            
            if estoque_baixo:
                where_conditions.append("quantidade_atual <= quantidade_minima")
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Contar total
            count_query = f"SELECT COUNT(*) FROM produtos WHERE {where_clause}"
            total = self.db.execute(text(count_query), params).scalar()
            
            # Buscar produtos
            offset = (pagina - 1) * por_pagina
            params["limit"] = por_pagina
            params["offset"] = offset
            
            query = f"""
                SELECT id, nome, unidade_medida, quantidade_atual, quantidade_minima, 
                       preco_venda, ativo, created_at
                FROM produtos 
                WHERE {where_clause}
                ORDER BY nome
                LIMIT :limit OFFSET :offset
            """
            
            result = self.db.execute(text(query), params)
            
            produtos = []
            for row in result.fetchall():
                produtos.append({
                    "id": row[0],
                    "nome": row[1],
                    "unidade_medida": row[2],
                    "quantidade_atual": float(row[3] or 0),
                    "quantidade_minima": float(row[4] or 0),
                    "preco_venda": float(row[5] or 0),
                    "is_active": row[6],  # ✅ Converter 'ativo' para 'is_active'
                    "created_at": row[7],
                    "status_estoque": self._get_status_estoque(float(row[3] or 0), float(row[4] or 0))
                })
            
            return produtos, total
            
        except Exception as e:
            logger.error(f"Erro ao listar produtos: {e}")
            raise
    
    def obter_produto(self, produto_id: int) -> Optional[dict]:
        """Obter produto por ID com nomes corretos"""
        try:
            result = self.db.execute(text("""
                SELECT id, nome, unidade_medida, quantidade_atual, quantidade_minima, 
                       preco_venda, ativo, created_at
                FROM produtos 
                WHERE id = :id AND ativo = true
            """), {"id": produto_id})
            
            row = result.fetchone()
            if not row:
                return None
            
            return {
                "id": row[0],
                "nome": row[1],
                "unidade_medida": row[2],
                "quantidade_atual": float(row[3] or 0),
                "quantidade_minima": float(row[4] or 0),
                "preco_venda": float(row[5] or 0),
                "is_active": row[6],  # ✅ Converter 'ativo' para 'is_active'
                "created_at": row[7],
                "status_estoque": self._get_status_estoque(float(row[3] or 0), float(row[4] or 0)),
                "valor_estoque_total": float(row[3] or 0) * float(row[5] or 0),
                "precisa_reposicao": float(row[3] or 0) <= float(row[4] or 0)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter produto {produto_id}: {e}")
            raise
    
    def _get_status_estoque(self, quantidade_atual: float, quantidade_minima: float) -> dict:
        """Calcular status do estoque"""
        if quantidade_atual <= 0:
            return {"status": "esgotado", "cor": "#e74c3c", "icon": "❌"}
        elif quantidade_atual <= quantidade_minima:
            return {"status": "baixo", "cor": "#f39c12", "icon": "⚠️"}
        else:
            return {"status": "normal", "cor": "#27ae60", "icon": "✅"}

