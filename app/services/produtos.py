# app/services/produtos.py - Versão Completa
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any, Tuple
from app.schemas.produtos import ProdutoCreate, ProdutoUpdate
from app.schemas.analytics_produtos import RelatorioProdutos
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ProdutoService:
    """Service completo para gestão de produtos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def criar_produto(self, produto_data: ProdutoCreate) -> dict:
        """Criar produto (método já implementado)"""
        # Manter implementação existente
        pass
    
    def listar_produtos(self, **kwargs) -> Tuple[List[dict], int]:
        """Listar produtos (método já implementado)"""
        # Manter implementação existente  
        pass
    
    def obter_produto(self, produto_id: int) -> Optional[dict]:
        """Obter produto por ID (método já implementado)"""
        # Manter implementação existente
        pass
    
    # ✅ ADICIONAR: Método atualizar_produto
    def atualizar_produto(self, produto_id: int, produto_data: ProdutoUpdate) -> Optional[dict]:
        """Atualizar produto existente"""
        try:
            logger.info(f"🔄 Atualizando produto ID: {produto_id}")
            
            # Verificar se produto existe
            produto_atual = self.obter_produto(produto_id)
            if not produto_atual:
                return None
            
            # Preparar campos para atualização
            update_fields = []
            params = {"id": produto_id, "updated_at": datetime.now()}
            
            if produto_data.nome is not None:
                update_fields.append("nome = :nome")
                params["nome"] = str(produto_data.nome).strip().title()
            
            if produto_data.unidade_medida is not None:
                update_fields.append("unidade_medida = :unidade_medida")
                params["unidade_medida"] = str(produto_data.unidade_medida)
            
            if produto_data.preco_venda is not None:
                update_fields.append("preco_venda = :preco_venda")
                params["preco_venda"] = float(produto_data.preco_venda)
            
            if produto_data.quantidade_atual is not None:
                update_fields.append("quantidade_atual = :quantidade_atual")
                params["quantidade_atual"] = float(produto_data.quantidade_atual)
            
            if produto_data.quantidade_minima is not None:
                update_fields.append("quantidade_minima = :quantidade_minima")
                params["quantidade_minima"] = float(produto_data.quantidade_minima)
            
            if not update_fields:
                return produto_atual  # Nenhum campo para atualizar
            
            update_fields.append("updated_at = :updated_at")
            
            # Executar atualização
            with self.db.begin():
                update_query = f"""
                    UPDATE produtos 
                    SET {', '.join(update_fields)}
                    WHERE id = :id AND ativo = true
                    RETURNING id, nome, unidade_medida, quantidade_atual, 
                             quantidade_minima, preco_venda, ativo, created_at, updated_at
                """
                
                result = self.db.execute(text(update_query), params)
                row = result.fetchone()
                
                if not row:
                    return None
                
                logger.info(f"✅ Produto {produto_id} atualizado com sucesso")
                
                return {
                    "id": row[0],
                    "nome": row[1],
                    "unidade_medida": row[2],
                    "quantidade_atual": float(row[3] or 0),
                    "quantidade_minima": float(row[4] or 0),
                    "preco_venda": float(row[5] or 0),
                    "is_active": row[6],
                    "created_at": row[7],
                    "updated_at": row[8]
                }
                
        except Exception as e:
            try:
                self.db.rollback()
                logger.error(f"🔄 Rollback executado: {e}")
            except:
                pass
            
            error_msg = f"Erro ao atualizar produto {produto_id}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    # ✅ ADICIONAR: Método deletar_produto
    def deletar_produto(self, produto_id: int) -> bool:
        """Deletar produto (soft delete)"""
        try:
            logger.info(f"🗑️ Deletando produto ID: {produto_id}")
            
            # Usar soft delete (marcar como inativo)
            with self.db.begin():
                result = self.db.execute(text("""
                    UPDATE produtos 
                    SET ativo = false, updated_at = :updated_at
                    WHERE id = :id AND ativo = true
                    RETURNING id, nome
                """), {
                    "id": produto_id,
                    "updated_at": datetime.now()
                })
                
                row = result.fetchone()
                if row:
                    logger.info(f"✅ Produto '{row[1]}' (ID: {row[0]}) deletado com sucesso")
                    return True
                else:
                    logger.warning(f"⚠️ Produto ID {produto_id} não encontrado para deleção")
                    return False
                
        except Exception as e:
            try:
                self.db.rollback()
                logger.error(f"🔄 Rollback executado: {e}")
            except:
                pass
            
            error_msg = f"Erro ao deletar produto {produto_id}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    # ✅ ADICIONAR: Método buscar_por_nome
    def buscar_por_nome(self, nome: str) -> List[dict]:
        """Buscar produtos por nome"""
        try:
            logger.info(f"🔍 Buscando produtos por nome: '{nome}'")
            
            result = self.db.execute(text("""
                SELECT id, nome, unidade_medida, quantidade_atual, 
                       quantidade_minima, preco_venda, ativo
                FROM produtos 
                WHERE nome ILIKE :nome AND ativo = true
                ORDER BY nome
                LIMIT 20
            """), {"nome": f"%{nome}%"})
            
            produtos = []
            for row in result.fetchall():
                produtos.append({
                    "id": row[0],
                    "nome": row[1],
                    "unidade_medida": row[2],
                    "quantidade_atual": float(row[3] or 0),
                    "quantidade_minima": float(row[4] or 0),
                    "preco_venda": float(row[5] or 0),
                    "is_active": row[6]
                })
            
            logger.info(f"✅ Encontrados {len(produtos)} produtos para '{nome}'")
            return produtos
            
        except Exception as e:
            error_msg = f"Erro ao buscar produtos por nome '{nome}': {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    # ✅ ADICIONAR: Método gerar_relatorio_completo
    def gerar_relatorio_completo(self, dias: int = 30, categoria: Optional[str] = None) -> RelatorioProdutos:
        """Gerar relatório completo de produtos"""
        try:
            logger.info(f"📊 Gerando relatório completo (últimos {dias} dias)")
            
            # Resumo geral
            resumo_query = """
                SELECT 
                    COUNT(*) as total_produtos,
                    COUNT(*) FILTER (WHERE ativo = true) as produtos_ativos,
                    COUNT(*) FILTER (WHERE quantidade_atual <= 0) as produtos_esgotados,
                    COUNT(*) FILTER (WHERE quantidade_atual <= quantidade_minima) as produtos_estoque_baixo,
                    SUM(quantidade_atual * preco_venda) as valor_total_estoque
                FROM produtos
            """
            
            if categoria:
                resumo_query += " WHERE categoria = :categoria"
                params = {"categoria": categoria}
            else:
                params = {}
            
            resumo_result = self.db.execute(text(resumo_query), params).fetchone()
            
            resumo_geral = {
                "total_produtos": resumo_result[0] or 0,
                "produtos_ativos": resumo_result[1] or 0,
                "produtos_inativos": (resumo_result[0] or 0) - (resumo_result[1] or 0),
                "produtos_esgotados": resumo_result[2] or 0,
                "produtos_estoque_baixo": resumo_result[3] or 0,
                "valor_total_estoque": float(resumo_result[4] or 0)
            }
            
            # Top produtos por valor de estoque
            top_produtos_query = """
                SELECT id, nome, quantidade_atual, preco_venda,
                       (quantidade_atual * preco_venda) as valor_estoque
                FROM produtos 
                WHERE ativo = true
            """
            
            if categoria:
                top_produtos_query += " AND categoria = :categoria"
            
            top_produtos_query += " ORDER BY valor_estoque DESC LIMIT 10"
            
            top_produtos_result = self.db.execute(text(top_produtos_query), params)
            top_produtos_vendas = []
            
            for row in top_produtos_result.fetchall():
                top_produtos_vendas.append({
                    "produto_id": row[0],
                    "nome_produto": row[1],
                    "quantidade_vendida": float(row[2]),
                    "valor_total_vendido": float(row[4]),
                    "numero_transacoes": 1,
                    "ticket_medio": float(row[3])
                })
            
            # Alertas de estoque
            alertas_estoque = []
            if resumo_geral["produtos_esgotados"] > 0:
                alertas_estoque.append({
                    "tipo": "produtos_esgotados",
                    "quantidade": resumo_geral["produtos_esgotados"],
                    "urgencia": "alta"
                })
            
            if resumo_geral["produtos_estoque_baixo"] > 0:
                alertas_estoque.append({
                    "tipo": "estoque_baixo",
                    "quantidade": resumo_geral["produtos_estoque_baixo"],
                    "urgencia": "media"
                })
            
            # Sugestões de compra (produtos com estoque baixo)
            sugestoes_compra = []
            if resumo_geral["produtos_estoque_baixo"] > 0:
                sugestoes_result = self.db.execute(text("""
                    SELECT nome, quantidade_atual, quantidade_minima
                    FROM produtos 
                    WHERE ativo = true AND quantidade_atual <= quantidade_minima
                    ORDER BY (quantidade_minima - quantidade_atual) DESC
                    LIMIT 5
                """))
                
                for row in sugestoes_result.fetchall():
                    sugestoes_compra.append({
                        "produto": row[0],
                        "quantidade_sugerida": max(row[2] * 2 - row[1], row[2]),
                        "prioridade": "alta" if row[1] <= 0 else "media"
                    })
            
            # Criar relatório
            from datetime import date
            
            relatorio = RelatorioProdutos(
                resumo_geral=resumo_geral,
                top_produtos_vendas=top_produtos_vendas,
                produtos_baixo_giro=[],  # Implementar se necessário
                produtos_alta_margem=[],  # Implementar se necessário
                alertas_estoque=alertas_estoque,
                sugestoes_compra=sugestoes_compra,
                periodo={
                    "inicio": (datetime.now() - timedelta(days=dias)).date(),
                    "fim": date.today()
                },
                gerado_em=datetime.now()
            )
            
            logger.info("✅ Relatório completo gerado com sucesso")
            return relatorio
            
        except Exception as e:
            error_msg = f"Erro ao gerar relatório completo: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
