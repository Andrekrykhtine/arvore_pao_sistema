from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

from app.core.database import get_db

from app.schemas.analytics_produtos import (
    MetricaProduto, ResumoAnalytics, RelatorioAnalytics, 
    AlertaInteligente, DashboardKPIs, AnalyticsPorCategoria
)

app = FastAPI(title="🍞 Sistema Árvore Pão - Básico Funcional")

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "message": "API funcionando corretamente",
        "version": "1.0.0"
    }

@app.get("/")
def root():
    return {
        "message": "🍞 Sistema Árvore Pão",
        "status": "funcionando",
        "endpoints": ["/health", "/produtos"]
    }

@app.get("/produtos")
def listar_produtos():
    return {
        "produtos": [],
        "total": 0,
        "message": "Endpoint básico funcionando - ready para implementar CRUD"
    }

@app.get("/test")
def test_endpoint():
    return {
        "test": "success",
        "database": "pending",
        "schemas": "basic",
        "message": "API básica funcionando perfeitamente"
    }

# ========================
# ENDPOINTS DE ANALYTICS
# ========================

# ========================
# ENDPOINTS DE ANALYTICS
# ========================
from app.schemas.analytics_produtos import (
    MetricaProduto, ResumoAnalytics, RelatorioAnalytics, 
    AlertaInteligente, DashboardKPIs, AnalyticsPorCategoria
)

@app.get("/api/v1/analytics/resumo", response_model=ResumoAnalytics)
def analytics_resumo_geral(db: Session = Depends(get_db)):
    """📊 Resumo geral de analytics dos produtos"""
    try:
        # Simular conexão com banco para buscar dados reais
        # Por enquanto, vamos usar dados mock baseados na estrutura real
        
        return ResumoAnalytics(
            total_produtos=10,  # Seus produtos cadastrados
            produtos_ativos=9,
            produtos_estoque_baixo=2,
            produtos_sem_estoque=0,
            valor_total_estoque=Decimal('2500.00'),
            margem_media=45.5,
            produto_maior_valor={
                "nome": "Bolo de Chocolate Premium",
                "valor": 450.00,
                "categoria": "doces"
            },
            produto_maior_margem={
                "nome": "Pão Francês",
                "margem": 56.25,
                "categoria": "paes"
            },
            categoria_dominante={
                "categoria": "paes",
                "quantidade": 4,
                "percentual": 40.0
            }
        )
        
    except Exception as e:
        logger.error(f"Erro no resumo analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/produtos", response_model=List[MetricaProduto])
def analytics_por_produto(db: Session = Depends(get_db)):
    """📈 Métricas detalhadas por produto"""
    try:
        # Exemplo com dados simulados baseados na estrutura real
        metricas = []
        
        # Simular alguns produtos com métricas
        produtos_exemplo = [
            {"id": 1, "nome": "Pão Francês", "categoria": "paes", "preco": 0.80, "estoque": 150},
            {"id": 2, "nome": "Bolo de Chocolate", "categoria": "doces", "preco": 15.00, "estoque": 25},
            {"id": 3, "nome": "Croissant", "categoria": "doces", "preco": 4.50, "estoque": 45}
        ]
        
        for produto in produtos_exemplo:
            metrica = MetricaProduto(
                produto_id=produto["id"],
                nome=produto["nome"],
                categoria=produto["categoria"],
                quantidade_atual=Decimal(str(produto["estoque"])),
                quantidade_minima=Decimal('20'),
                percentual_estoque=75.0,
                dias_estoque_restante=15,
                preco_venda=Decimal(str(produto["preco"])),
                preco_custo=Decimal(str(produto["preco"] * 0.6)),
                margem_bruta=Decimal(str(produto["preco"] * 0.4)),
                margem_percentual=40.0,
                valor_estoque_total=Decimal(str(produto["estoque"] * produto["preco"])),
                status_estoque="normal" if produto["estoque"] > 20 else "baixo",
                precisa_reposicao=produto["estoque"] <= 20,
                nivel_urgencia=2 if produto["estoque"] > 20 else 4
            )
            metricas.append(metrica)
            
        return metricas
        
    except Exception as e:
        logger.error(f"Erro nas métricas por produto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/categorias", response_model=List[AnalyticsPorCategoria])
def analytics_por_categoria(db: Session = Depends(get_db)):
    """📊 Analytics agrupados por categoria"""
    try:
        categorias = [
            AnalyticsPorCategoria(
                categoria="paes",
                total_produtos=4,
                valor_total_estoque=Decimal('1200.00'),
                margem_media=48.5,
                produtos_estoque_baixo=1,
                produto_mais_vendido="Pão Francês",
                percentual_do_total=48.0
            ),
            AnalyticsPorCategoria(
                categoria="doces",
                total_produtos=3,
                valor_total_estoque=Decimal('800.00'),
                margem_media=52.0,
                produtos_estoque_baixo=0,
                produto_mais_vendido="Bolo de Chocolate",
                percentual_do_total=32.0
            ),
            AnalyticsPorCategoria(
                categoria="salgados",
                total_produtos=2,
                valor_total_estoque=Decimal('400.00'),
                margem_media=41.2,
                produtos_estoque_baixo=1,
                produto_mais_vendido="Coxinha",
                percentual_do_total=16.0
            )
        ]
        
        return categorias
        
    except Exception as e:
        logger.error(f"Erro nas métricas por categoria: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/kpis", response_model=DashboardKPIs)
def dashboard_kpis(db: Session = Depends(get_db)):
    """📊 KPIs principais para dashboard"""
    try:
        return DashboardKPIs(
            valor_total_estoque=Decimal('2500.00'),
            produtos_estoque_critico=2,
            percentual_disponibilidade=85.5,
            margem_media_geral=47.2,
            produto_maior_rentabilidade={
                "nome": "Torta de Morango",
                "margem": 65.0,
                "valor_estoque": 320.00
            },
            potencial_receita=Decimal('4150.00'),
            produtos_precisam_reposicao=2,
            categorias_balanceadas=2,
            score_saude_estoque=78.5,
            total_alertas_ativos=3,
            alertas_criticos=1
        )
        
    except Exception as e:
        logger.error(f"Erro nos KPIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/alertas", response_model=List[AlertaInteligente])
def alertas_inteligentes(urgencia_minima: Optional[int] = Query(None, ge=1, le=5)):
    """⚠️ Sistema de alertas inteligentes baseado em analytics"""
    try:
        alertas = [
            AlertaInteligente(
                tipo="CRITICO",
                categoria="estoque",
                titulo="Produto Sem Estoque",
                descricao="Pão integral está com estoque zerado há 2 dias",
                produto_id=5,
                produto_nome="Pão Integral",
                valor_metrica=Decimal('0'),
                threshold=Decimal('10'),
                urgencia=5,
                acao_sugerida="Fazer pedido urgente ao fornecedor"
            ),
            AlertaInteligente(
                tipo="ALTO",
                categoria="estoque",
                titulo="Estoque Baixo",
                descricao="Croissant está abaixo do estoque mínimo",
                produto_id=3,
                produto_nome="Croissant",
                valor_metrica=Decimal('8'),
                threshold=Decimal('15'),
                urgencia=4,
                acao_sugerida="Agendar reposição para amanhã"
            ),
            AlertaInteligente(
                tipo="MEDIO",
                categoria="margem",
                titulo="Margem Baixa",
                descricao="Sanduíche natural tem margem abaixo do esperado",
                produto_id=7,
                produto_nome="Sanduíche Natural",
                valor_metrica=Decimal('22.5'),
                threshold=Decimal('30.0'),
                urgencia=3,
                acao_sugerida="Revisar preço ou custo dos ingredientes"
            )
        ]
        
        if urgencia_minima:
            alertas = [a for a in alertas if a.urgencia >= urgencia_minima]
            
        return alertas
        
    except Exception as e:
        logger.error(f"Erro nos alertas inteligentes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/relatorio-completo")
def relatorio_analytics_completo(db: Session = Depends(get_db)):
    """📊 Relatório completo de analytics"""
    try:
        # Buscar dados de outros endpoints para compor relatório completo
        resumo = ResumoAnalytics(
            total_produtos=10,
            produtos_ativos=9,
            produtos_estoque_baixo=2,
            produtos_sem_estoque=0,
            valor_total_estoque=Decimal('2500.00'),
            margem_media=45.5
        )
        
        # Simular métricas por produto
        metricas_produtos = [
            MetricaProduto(
                produto_id=1,
                nome="Pão Francês",
                categoria="paes",
                quantidade_atual=Decimal('150'),
                quantidade_minima=Decimal('50'),
                percentual_estoque=75.0,
                dias_estoque_restante=0,
                preco_venda=Decimal('0.80'),
                preco_custo=Decimal('0.35'),
                margem_bruta=Decimal('0.45'),
                margem_percentual=56.25,
                valor_estoque_total=Decimal('120.00'),
                status_estoque="normal",
                precisa_reposicao=False,
                nivel_urgencia=1
            )
        ]
        
        relatorio_data = RelatorioAnalytics(
            resumo_geral=resumo,
            metricas_produtos=metricas_produtos,
            analytics_categorias=[],
            top_produtos_valor=[
                {"nome": "Bolo de Chocolate Premium", "valor": 450.00},
                {"nome": "Torta de Morango", "valor": 320.00}
            ],
            top_produtos_margem=[
                {"nome": "Pão Francês", "margem": 56.25},
                {"nome": "Croissant", "margem": 52.0}
            ],
            produtos_atencao=[
                {"nome": "Pão Integral", "motivo": "Sem estoque"},
                {"nome": "Croissant", "motivo": "Estoque baixo"}
            ],
            recomendacoes=[
                "Reabastecer produtos com estoque crítico",
                "Revisar preços de produtos com baixa margem",
                "Considerar promoções para produtos parados"
            ]
        )
        return {"relatorio-completo": relatorio_data}
        
    except Exception as e:
        logger.error(f"Erro no relatório completo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================
# ANALYTICS COM DADOS REAIS POSTGRESQL
# ========================
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
            margem_media=float(stats['margem_media'] or 0.0),
            produto_maior_valor={
                "nome": produto_maior_valor['nome'] if produto_maior_valor else "N/A",
                "valor": float(produto_maior_valor['valor'] or 0.0) if produto_maior_valor else 0.0,
                "categoria": produto_maior_valor['categoria'] if produto_maior_valor else "N/A"
            } if produto_maior_valor else None,
            produto_maior_margem={
                "nome": produto_maior_margem['nome'] if produto_maior_margem else "N/A", 
                "margem": float(produto_maior_margem['margem'] or 0.0) if produto_maior_margem else 0.0,
                "categoria": produto_maior_margem['categoria'] if produto_maior_margem else "N/A"
            } if produto_maior_margem else None,
            categoria_dominante={
                "categoria": categoria_dominante['categoria'] if categoria_dominante else "N/A",
                "quantidade": categoria_dominante['quantidade'] if categoria_dominante else 0,
                "percentual": float(categoria_dominante['percentual'] or 0.0) if categoria_dominante else 0.0
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
                        categoria=produto['categoria'] or "N/A",
                        quantidade_atual=Decimal(str(produto['quantidade_atual'] or 0)),
                        quantidade_minima=Decimal(str(produto['quantidade_minima'] or 0)),
                        percentual_estoque=float(produto['percentual_estoque'] or 0.0),
                        dias_estoque_restante=int(produto['dias_estoque_restante'] or 0),
                        preco_venda=Decimal(str(produto['preco_venda'] or 0)),
                        preco_custo=Decimal(str(produto['preco_custo'] or 0)),
                        margem_bruta=Decimal(str(produto['margem_bruta'] or 0)),
                        margem_percentual=float(produto['margem_percentual'] or 0.0),
                        valor_estoque_total=Decimal(str(produto['valor_estoque_total'] or 0)),
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
                        categoria=cat['categoria'] or "N/A",
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


# ========================
# DASHBOARD WEB INTERFACE
# ========================
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    """🎨 Dashboard visual para analytics"""
    try:
        with open("templates/dashboard.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dashboard não encontrado")

@app.get("/", response_class=HTMLResponse)
def dashboard_redirect():
    """🏠 Redirecionar página inicial para dashboard"""
    return """
    <html>
        <head>
            <meta http-equiv="refresh" content="0; url=/dashboard">
            <title>Redirecionando...</title>
        </head>
        <body>
            <p>Redirecionando para o <a href="/dashboard">Dashboard</a>...</p>
        </body>
    </html>
    """

# ========================
# ENDPOINTS PARA INTEGRAÇÃO N8N
# ========================
from fastapi import BackgroundTasks
import requests
from typing import Dict, Any

# Configurações N8N
N8N_WEBHOOK_BASE = "http://localhost:5678/webhook"  # URL base do N8N
N8N_ENABLED = True  # Flag para habilitar/desabilitar N8N

async def send_to_n8n(webhook_path: str, data: Dict[Any, Any]):
    """Enviar dados para N8N via webhook"""
    if not N8N_ENABLED:
        return False
        
    try:
        webhook_url = f"{N8N_WEBHOOK_BASE}/{webhook_path}"
        response = requests.post(webhook_url, json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Erro ao enviar para N8N: {e}")
        return False

@app.get("/api/v1/n8n/alertas-criticos")
async def n8n_alertas_criticos():
    """🚨 Endpoint específico para N8N - apenas alertas críticos"""
    try:
        # Buscar apenas alertas críticos e altos
        alertas = []
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                
                # Produtos sem estoque (crítico)
                cursor.execute("""
                    SELECT id, nome, categoria, quantidade_atual, quantidade_minima,
                           'CRITICO' as tipo_alerta,
                           'Produto sem estoque' as descricao_alerta,
                           'Fazer pedido urgente' as acao_sugerida
                    FROM produtos 
                    WHERE is_active = true AND quantidade_atual <= 0
                    ORDER BY nome
                """)
                sem_estoque = cursor.fetchall()
                
                for produto in sem_estoque:
                    alertas.append({
                        "tipo": "CRITICO",
                        "categoria": "estoque",
                        "produto_id": produto['id'],
                        "produto_nome": produto['nome'],
                        "produto_categoria": produto['categoria'],
                        "quantidade_atual": float(produto['quantidade_atual']),
                        "quantidade_minima": float(produto['quantidade_minima']),
                        "titulo": produto['descricao_alerta'],
                        "acao": produto['acao_sugerida'],
                        "urgencia": 5,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Produtos com estoque muito baixo (alto)
                cursor.execute("""
                    SELECT id, nome, categoria, quantidade_atual, quantidade_minima,
                           'ALTO' as tipo_alerta,
                           'Estoque muito baixo' as descricao_alerta,
                           'Agendar reposição hoje' as acao_sugerida
                    FROM produtos 
                    WHERE is_active = true 
                      AND quantidade_atual > 0 
                      AND quantidade_atual <= (quantidade_minima * 0.5)
                    ORDER BY (quantidade_atual / NULLIF(quantidade_minima, 0))
                """)
                estoque_baixo = cursor.fetchall()
                
                for produto in estoque_baixo:
                    alertas.append({
                        "tipo": "ALTO", 
                        "categoria": "estoque",
                        "produto_id": produto['id'],
                        "produto_nome": produto['nome'],
                        "produto_categoria": produto['categoria'],
                        "quantidade_atual": float(produto['quantidade_atual']),
                        "quantidade_minima": float(produto['quantidade_minima']),
                        "titulo": produto['descricao_alerta'],
                        "acao": produto['acao_sugerida'],
                        "urgencia": 4,
                        "timestamp": datetime.now().isoformat()
                    })
        
        alertas_data = {
            "sistema": "Árvore Pão",
            "total_alertas": len(alertas),
            "alertas_criticos": len([a for a in alertas if a["tipo"] == "CRITICO"]),
            "alertas_altos": len([a for a in alertas if a["tipo"] == "ALTO"]),
            "alertas": alertas,
            "gerado_em": datetime.now().isoformat(),
            "webhook_ready": True
        }
        return {"alertas-criticos": alertas_data}
        
    except Exception as e:
        logger.error(f"Erro no endpoint N8N alertas críticos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/n8n/resumo-diario")
async def n8n_resumo_diario():
    """📊 Resumo diário para N8N - relatório automático"""
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
                        AVG(((preco_venda - preco_custo) / preco_venda * 100)) FILTER (WHERE is_active = true AND preco_custo > 0) as margem_media
                    FROM produtos
                """)
                stats = cursor.fetchone()
                
                # Top 3 produtos por valor
                cursor.execute("""
                    SELECT nome, (quantidade_atual * preco_venda) as valor
                    FROM produtos 
                    WHERE is_active = true AND quantidade_atual > 0
                    ORDER BY (quantidade_atual * preco_venda) DESC 
                    LIMIT 3
                """)
                top_produtos = cursor.fetchall()
                
                # Resumo por categoria
                cursor.execute("""
                    SELECT categoria, COUNT(*) as quantidade,
                           SUM(quantidade_atual * preco_venda) as valor_categoria
                    FROM produtos 
                    WHERE is_active = true
                    GROUP BY categoria 
                    ORDER BY valor_categoria DESC
                """)
                categorias = cursor.fetchall()
        
        resumo_diario_data = {
            "sistema": "Árvore Pão",
            "tipo_relatorio": "resumo_diario",
            "data": datetime.now().date().isoformat(),
            "estatisticas": {
                "total_produtos": stats['total_produtos'],
                "produtos_ativos": stats['produtos_ativos'],
                "produtos_sem_estoque": stats['produtos_sem_estoque'],
                "produtos_estoque_baixo": stats['produtos_estoque_baixo'],
                "valor_total_estoque": float(stats['valor_total_estoque'] or 0),
                "margem_media": float(stats['margem_media'] or 0)
            },
            "top_produtos": [
                {"nome": p['nome'], "valor": float(p['valor'] or 0)}
                for p in top_produtos
            ],
            "resumo_categorias": [
                {
                    "categoria": c['categoria'],
                    "quantidade": c['quantidade'],
                    "valor": float(c['valor_categoria'] or 0)
                }
                for c in categorias
            ],
            "gerado_em": datetime.now().isoformat(),
            "n8n_ready": True
        }
        return {"resumo-diario": resumo_diario_data}
        
    except Exception as e:
        logger.error(f"Erro no resumo diário N8N: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/n8n/trigger-alert")
async def n8n_trigger_alert(background_tasks: BackgroundTasks):
    """🔔 Endpoint para disparar alertas via N8N"""
    try:
        # Buscar alertas críticos
        response = await n8n_alertas_criticos()
        alertas_criticos = [a for a in response["alertas"] if a["tipo"] == "CRITICO"]
        
        if alertas_criticos:
            # Enviar para N8N em background
            background_tasks.add_task(
                send_to_n8n, 
                "alertas-urgentes", 
                {
                    "sistema": "Árvore Pão",
                    "alertas": alertas_criticos,
                    "total": len(alertas_criticos),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return {
                "success": True,
                "message": f"{len(alertas_criticos)} alertas críticos enviados para N8N",
                "alertas_enviados": len(alertas_criticos)
            }
        else:
            return {
                "success": True,
                "message": "Nenhum alerta crítico encontrado",
                "alertas_enviados": 0
            }
        
    except Exception as e:
        logger.error(f"Erro ao disparar alertas N8N: {e}")
        raise HTTPException(status_code=500, detail=str(e))

