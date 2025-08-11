# Arquivo temporário - será implementado gradualmente


from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from decimal import Decimal

class MetricaProduto(BaseModel):
    produto_id: int
    nome: str
    categoria: str
    quantidade_atual: Decimal
    quantidade_minima: Decimal
    percentual_estoque: float
    dias_estoque_restante: int
    preco_venda: Decimal
    preco_custo: Decimal
    margem_bruta: Decimal
    margem_percentual: float
    valor_estoque_total: Decimal
    status_estoque: str
    precisa_reposicao: bool
    nivel_urgencia: int

class ResumoAnalytics(BaseModel):
    total_produtos: int
    produtos_ativos: int
    produtos_estoque_baixo: int
    produtos_sem_estoque: int
    valor_total_estoque: Decimal
    margem_media: float
    produto_maior_valor: Optional[Dict] = None
    produto_maior_margem: Optional[Dict] = None
    categoria_dominante: Optional[Dict] = None

class RelatorioAnalytics(BaseModel):
    resumo_geral: ResumoAnalytics
    metricas_produtos: List[MetricaProduto]
    analytics_categorias: List[dict] # Temporário
    top_produtos_valor: List[Dict]
    top_produtos_margem: List[Dict]
    produtos_atencao: List[Dict]
    recomendacoes: List[str]

class AlertaInteligente(BaseModel):
    tipo: str = Field(..., description="Tipo de alerta (ex: CRITICO, ALTO, MEDIO)")
    categoria: str = Field(..., description="Categoria do alerta (ex: estoque, margem)")
    titulo: str
    descricao: str
    produto_id: Optional[int] = None
    produto_nome: Optional[str] = None
    valor_metrica: Optional[Decimal] = None
    threshold: Optional[Decimal] = None
    urgencia: int = Field(..., ge=1, le=5, description="Nível de urgência de 1 a 5")
    acao_sugerida: str

class DashboardKPIs(BaseModel):
    valor_total_estoque: Decimal
    produtos_estoque_critico: int
    percentual_disponibilidade: float
    margem_media_geral: float
    produto_maior_rentabilidade: Dict
    potencial_receita: Decimal
    produtos_precisam_reposicao: int
    categorias_balanceadas: int
    score_saude_estoque: float
    total_alertas_ativos: int
    alertas_criticos: int

class AnalyticsPorCategoria(BaseModel):
    categoria: str
    total_produtos: int
    valor_total_estoque: Decimal
    margem_media: float
    produtos_estoque_baixo: int
    produto_mais_vendido: str
    percentual_do_total: float