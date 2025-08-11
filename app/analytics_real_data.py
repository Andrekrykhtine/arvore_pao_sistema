# ========================
# ANALYTICS COM DADOS REAIS - POSTGRESQL
# ========================

import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal
from datetime import datetime

def get_db_connection():
    """Obter conexão com PostgreSQL"""
    return psycopg2.connect(
        dbname="arvore_pao",
        user="postgres", 
        password="123456",
        host="db",  # Nome do container
        port=5432
    )

@app.get("/api/v1/analytics/resumo-real", response_model=ResumoAnalytics)
def analytics_resumo_real():
    """📊 Resumo geral com dados reais do PostgreSQL"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                
                # Estatísticas gerais
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_produtos,
                        COUNT(*) FILTER (WHERE is_active = true) as produtos_ativos,
                        COUNT(*) FILTER (WHERE quantidade_atual <= 0 AND is_active = true) as produtos_sem_estoque,
                        COUNT(*) FILTER (WHERE quantidade_atual <= quantidade_minima AND quantidade_atual > 0 AND is_active = true) as produtos_estoque_baixo,
                        SUM(quantidade_atual * preco_venda) FILTER (WHERE is_active = true) as valor_total_estoque,
                        AVG(
                            CASE 
                                WHEN preco_custo > 0 AND preco_venda > 0 
                                THEN ((preco_venda - preco_custo) / preco_venda * 100)
                                ELSE NULL 
                            END
                        ) as margem_media
                    FROM produtos
                """)
                stats = cursor.fetchone()
                
                # Produto com maior valor em estoque
                cursor.execute("""
                    SELECT nome, categoria, (quantidade_atual * preco_venda) as valor
                    FROM produtos 
                    WHERE is_active = true AND quantidade_atual > 0
                    ORDER BY (quantidade_atual * preco_venda) DESC 
                    LIMIT 1
                """)
                produto_maior_valor = cursor.fetchone()
                
                # Produto com maior margem
                cursor.execute("""
                    SELECT nome, categoria, 
                           ((preco_venda - preco_custo) / preco_venda * 100) as margem
                    FROM produtos 
                    WHERE is_active = true AND preco_custo > 0 AND preco_venda > preco_custo
                    ORDER BY ((preco_venda - preco_custo) / preco_venda * 100) DESC 
                    LIMIT 1
                """)
                produto_maior_margem = cursor.fetchone()
                
                # Categoria dominante
                cursor.execute("""
                    SELECT categoria, COUNT(*) as quantidade,
                           (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM produtos WHERE is_active = true)) as percentual
                    FROM produtos 
                    WHERE is_active = true
                    GROUP BY categoria 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 1
                """)
                categoria_dominante = cursor.fetchone()
        
        return ResumoAnalytics(
            total_produtos=stats['total_produtos'],
            produtos_ativos=stats['produtos_ativos'], 
            produtos_estoque_baixo=stats['produtos_estoque_baixo'],
            produtos_sem_estoque=stats['produtos_sem_estoque'],
            valor_total_estoque=Decimal(str(stats['valor_total_estoque'] or 0)),
            margem_media=float(stats['margem_media'] or 0),
            produto_maior_valor={
                "nome": produto_maior_valor['nome'] if produto_maior_valor else "N/A",
                "valor": float(produto_maior_valor['valor']) if produto_maior_valor else 0,
                "categoria": produto_maior_valor['categoria'] if produto_maior_valor else "N/A"
            } if produto_maior_valor else None,
            produto_maior_margem={
                "nome": produto_maior_margem['nome'] if produto_maior_margem else "N/A", 
                "margem": float(produto_maior_margem['margem']) if produto_maior_margem else 0,
                "categoria": produto_maior_margem['categoria'] if produto_maior_margem else "N/A"
            } if produto_maior_margem else None,
            categoria_dominante={
                "categoria": categoria_dominante['categoria'] if categoria_dominante else "N/A",
                "quantidade": categoria_dominante['quantidade'] if categoria_dominante else 0,
                "percentual": float(categoria_dominante['percentual']) if categoria_dominante else 0
            } if categoria_dominante else None
        )
        
    except Exception as e:
        logger.error(f"Erro no resumo analytics real: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados reais: {str(e)}")

@app.get("/api/v1/analytics/produtos-real", response_model=List[MetricaProduto])
def analytics_produtos_real():
    """📈 Métricas detalhadas por produto - dados reais"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        id,
                        nome,
                        categoria,
                        quantidade_atual,
                        quantidade_minima,
                        preco_venda,
                        preco_custo,
                        (quantidade_atual * preco_venda) as valor_estoque_total,
                        CASE 
                            WHEN preco_custo > 0 AND preco_venda > preco_custo 
                            THEN (preco_venda - preco_custo)
                            ELSE NULL 
                        END as margem_bruta,
                        CASE 
                            WHEN preco_custo > 0 AND preco_venda > preco_custo 
                            THEN ((preco_venda - preco_custo) / preco_venda * 100)
                            ELSE NULL 
                        END as margem_percentual,
                        CASE 
                            WHEN quantidade_atual <= 0 THEN 'sem_estoque'
                            WHEN quantidade_atual <= quantidade_minima THEN 'baixo'
                            WHEN quantidade_atual <= (quantidade_minima * 2) THEN 'atencao'
                            ELSE 'normal'
                        END as status_estoque,
                        CASE 
                            WHEN quantidade_atual <= quantidade_minima THEN true
                            ELSE false
                        END as precisa_reposicao,
                        CASE 
                            WHEN quantidade_atual <= 0 THEN 5
                            WHEN quantidade_atual <= quantidade_minima THEN 4  
                            WHEN quantidade_atual <= (quantidade_minima * 1.5) THEN 3
                            ELSE 1
                        END as nivel_urgencia,
                        -- Estimativa simples de dias restantes
                        CASE 
                            WHEN quantidade_atual > 0 THEN GREATEST(1, quantidade_atual / GREATEST(1, quantidade_minima) * 30)
                            ELSE 0
                        END as dias_estoque_restante,
                        (quantidade_atual * 100.0 / GREATEST(quantidade_minima * 3, 1)) as percentual_estoque
                    FROM produtos 
                    WHERE is_active = true
                    ORDER BY 
                        CASE 
                            WHEN quantidade_atual <= 0 THEN 1
                            WHEN quantidade_atual <= quantidade_minima THEN 2
                            ELSE 3
                        END,
                        nome
                """)
                
                produtos_data = cursor.fetchall()
                
                metricas = []
                for produto in produtos_data:
                    metrica = MetricaProduto(
                        produto_id=produto['id'],
                        nome=produto['nome'],
                        categoria=produto['categoria'],
                        quantidade_atual=Decimal(str(produto['quantidade_atual'])),
                        quantidade_minima=Decimal(str(produto['quantidade_minima'])),
                        percentual_estoque=float(produto['percentual_estoque']),
                        dias_estoque_restante=int(produto['dias_estoque_restante']),
                        preco_venda=Decimal(str(produto['preco_venda'])),
                        preco_custo=Decimal(str(produto['preco_custo'] or 0)),
                        margem_bruta=Decimal(str(produto['margem_bruta'] or 0)),
                        margem_percentual=float(produto['margem_percentual'] or 0),
                        valor_estoque_total=Decimal(str(produto['valor_estoque_total'])),
                        status_estoque=produto['status_estoque'],
                        precisa_reposicao=produto['precisa_reposicao'],
                        nivel_urgencia=produto['nivel_urgencia']
                    )
                    metricas.append(metrica)
                    
                return metricas
                
    except Exception as e:
        logger.error(f"Erro nas métricas por produto real: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar produtos reais: {str(e)}")

@app.get("/api/v1/analytics/categorias-real", response_model=List[AnalyticsPorCategoria])
def analytics_categorias_real():
    """🏷️ Analytics por categoria - dados reais"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    WITH categoria_stats AS (
                        SELECT 
                            categoria,
                            COUNT(*) as total_produtos,
                            SUM(quantidade_atual * preco_venda) as valor_total_estoque,
                            AVG(
                                CASE 
                                    WHEN preco_custo > 0 AND preco_venda > preco_custo 
                                    THEN ((preco_venda - preco_custo) / preco_venda * 100)
                                    ELSE NULL 
                                END
                            ) as margem_media,
                            COUNT(*) FILTER (WHERE quantidade_atual <= quantidade_minima) as produtos_estoque_baixo
                        FROM produtos 
                        WHERE is_active = true
                        GROUP BY categoria
                    ),
                    total_estoque AS (
                        SELECT SUM(quantidade_atual * preco_venda) as total_geral
                        FROM produtos 
                        WHERE is_active = true
                    )
                    SELECT 
                        cs.*,
                        (cs.valor_total_estoque * 100.0 / te.total_geral) as percentual_do_total
                    FROM categoria_stats cs
                    CROSS JOIN total_estoque te
                    ORDER BY cs.valor_total_estoque DESC
                """)
                
                categorias_data = cursor.fetchall()
                
                categorias = []
                for cat in categorias_data:
                    categoria = AnalyticsPorCategoria(
                        categoria=cat['categoria'],
                        total_produtos=cat['total_produtos'],
                        valor_total_estoque=Decimal(str(cat['valor_total_estoque'] or 0)),
                        margem_media=float(cat['margem_media'] or 0),
                        produtos_estoque_baixo=cat['produtos_estoque_baixo'],
                        produto_mais_vendido="N/A",  # Implementar com dados de vendas futuramente
                        percentual_do_total=float(cat['percentual_do_total'] or 0)
                    )
                    categorias.append(categoria)
                    
                return categorias
                
    except Exception as e:
        logger.error(f"Erro nas métricas por categoria real: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar categorias reais: {str(e)}")

@app.get("/api/v1/analytics/alertas-real", response_model=List[AlertaInteligente])
def alertas_reais():
    """⚠️ Alertas baseados em dados reais"""
    try:
        alertas = []
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                
                # Produtos sem estoque
                cursor.execute("""
                    SELECT id, nome FROM produtos 
                    WHERE is_active = true AND quantidade_atual <= 0
                    ORDER BY nome
                """)
                sem_estoque = cursor.fetchall()
                
                for produto in sem_estoque:
                    alertas.append(AlertaInteligente(
                        tipo="CRITICO",
                        categoria="estoque", 
                        titulo="Produto Sem Estoque",
                        descricao=f"{produto['nome']} está com estoque zerado",
                        produto_id=produto['id'],
                        produto_nome=produto['nome'],
                        valor_metrica=Decimal('0'),
                        threshold=Decimal('1'),
                        urgencia=5,
                        acao_sugerida="Fazer reposição urgente"
                    ))
                
                # Produtos com estoque baixo
                cursor.execute("""
                    SELECT id, nome, quantidade_atual, quantidade_minima
                    FROM produtos 
                    WHERE is_active = true 
                      AND quantidade_atual > 0 
                      AND quantidade_atual <= quantidade_minima
                    ORDER BY (quantidade_atual / NULLIF(quantidade_minima, 0))
                """)
                estoque_baixo = cursor.fetchall()
                
                for produto in estoque_baixo:
                    alertas.append(AlertaInteligente(
                        tipo="ALTO",
                        categoria="estoque",
                        titulo="Estoque Baixo", 
                        descricao=f"{produto['nome']}: {produto['quantidade_atual']} unidades (mín: {produto['quantidade_minima']})",
                        produto_id=produto['id'],
                        produto_nome=produto['nome'],
                        valor_metrica=Decimal(str(produto['quantidade_atual'])),
                        threshold=Decimal(str(produto['quantidade_minima'])),
                        urgencia=4,
                        acao_sugerida="Agendar reposição em 1-2 dias"
                    ))
                
                # Produtos com margem baixa (< 20%)
                cursor.execute("""
                    SELECT id, nome, preco_venda, preco_custo,
                           ((preco_venda - preco_custo) / preco_venda * 100) as margem
                    FROM produtos 
                    WHERE is_active = true 
                      AND preco_custo > 0 
                      AND preco_venda > preco_custo
                      AND ((preco_venda - preco_custo) / preco_venda * 100) < 20
                    ORDER BY ((preco_venda - preco_custo) / preco_venda * 100)
                """)
                margem_baixa = cursor.fetchall()
                
                for produto in margem_baixa:
                    alertas.append(AlertaInteligente(
                        tipo="MEDIO",
                        categoria="margem",
                        titulo="Margem Baixa",
                        descricao=f"{produto['nome']} tem margem de apenas {produto['margem']:.1f}%",
                        produto_id=produto['id'],
                        produto_nome=produto['nome'],
                        valor_metrica=Decimal(str(produto['margem'])),
                        threshold=Decimal('20'),
                        urgencia=2,
                        acao_sugerida="Revisar preço de venda ou negociar custo"
                    ))
        
        # Ordenar por urgência
        alertas.sort(key=lambda x: x.urgencia, reverse=True)
        return alertas
        
    except Exception as e:
        logger.error(f"Erro nos alertas reais: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar alertas reais: {str(e)}")

