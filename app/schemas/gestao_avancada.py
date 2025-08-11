# app/schemas/gestao_avancada.py
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

# ========================
# ENUMS PARA GESTÃO AVANÇADA
# ========================

class TipoFornecedor(str, Enum):
    """Tipos de fornecedor"""
    INGREDIENTES = "ingredientes"
    EMBALAGENS = "embalagens"
    EQUIPAMENTOS = "equipamentos"
    SERVICOS = "servicos"
    MISTO = "misto"

class StatusFornecedor(str, Enum):
    """Status do fornecedor"""
    ATIVO = "ativo"
    INATIVO = "inativo"
    SUSPENSO = "suspenso"
    BLACKLIST = "blacklist"

class TipoIngrediente(str, Enum):
    """Categorias de ingredientes"""
    FARINHA = "farinha"
    FERMENTO = "fermento"
    ACUCAR = "acucar"
    SAL = "sal"
    GORDURA = "gordura"
    LEITE = "leite"
    OVOS = "ovos"
    FRUTAS = "frutas"
    CHOCOLATE = "chocolate"
    ESPECIARIAS = "especiarias"
    CONSERVANTES = "conservantes"
    OUTROS = "outros"

class StatusLote(str, Enum):
    """Status do lote"""
    ATIVO = "ativo"
    VENCIDO = "vencido"
    BLOQUEADO = "bloqueado"
    CONSUMIDO = "consumido"

# ========================
# MODELOS DE FORNECEDORES
# ========================

class FornecedorBase(BaseModel):
    """Modelo base para fornecedores"""
    
    nome: str = Field(..., min_length=2, max_length=100, description="Nome da empresa")
    razao_social: Optional[str] = Field(None, max_length=150, description="Razão social")
    cnpj: Optional[str] = Field(None, pattern=r"^\d{14}$", description="CNPJ (apenas números)")
    tipo: TipoFornecedor = Field(..., description="Tipo de fornecedor")
    
    # Contato
    telefone: Optional[str] = Field(None, max_length=20, description="Telefone principal")
    email: Optional[str] = Field(None, description="Email de contato")
    contato_responsavel: Optional[str] = Field(None, max_length=100, description="Nome do responsável")
    
    # Endereço
    endereco: Optional[str] = Field(None, max_length=200, description="Endereço completo")
    cidade: Optional[str] = Field(None, max_length=100, description="Cidade")
    estado: Optional[str] = Field(None, max_length=2, description="UF")
    cep: Optional[str] = Field(None, pattern=r"^\d{8}$", description="CEP (apenas números)")
    
    # Dados comerciais
    prazo_entrega_dias: Optional[int] = Field(None, ge=0, le=365, description="Prazo de entrega em dias")
    condicoes_pagamento: Optional[str] = Field(None, max_length=200, description="Condições de pagamento")
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações gerais")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Email deve ter formato válido')
        return v

class FornecedorCreate(FornecedorBase):
    """Modelo para criação de fornecedores"""
    status: StatusFornecedor = Field(default=StatusFornecedor.ATIVO, description="Status inicial")

class FornecedorResponse(FornecedorBase):
    """Modelo de resposta para fornecedores"""
    id: int = Field(..., description="ID único")
    status: StatusFornecedor = Field(..., description="Status atual")
    total_ingredientes: int = Field(default=0, description="Total de ingredientes fornecidos")
    ultimo_pedido: Optional[datetime] = Field(None, description="Data do último pedido")
    valor_total_compras: Optional[Decimal] = Field(None, description="Valor total de compras")
    created_at: datetime = Field(..., description="Data de cadastro")
    updated_at: Optional[datetime] = Field(None, description="Última atualização")

class FornecedorUpdate(BaseModel):
    """Modelo para atualização de fornecedores"""
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    razao_social: Optional[str] = Field(None, max_length=150)
    tipo: Optional[TipoFornecedor] = None
    telefone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = None
    contato_responsavel: Optional[str] = Field(None, max_length=100)
    endereco: Optional[str] = Field(None, max_length=200)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, pattern=r"^\d{8}$")
    prazo_entrega_dias: Optional[int] = Field(None, ge=0, le=365)
    condicoes_pagamento: Optional[str] = Field(None, max_length=200)
    status: Optional[StatusFornecedor] = None
    observacoes: Optional[str] = Field(None, max_length=1000)

# ========================
# MODELOS DE INGREDIENTES
# ========================

class IngredienteBase(BaseModel):
    """Modelo base para ingredientes"""
    
    nome: str = Field(..., min_length=2, max_length=100, description="Nome do ingrediente")
    tipo: TipoIngrediente = Field(..., description="Categoria do ingrediente")
    descricao: Optional[str] = Field(None, max_length=500, description="Descrição detalhada")
    
    # Dados nutricionais (por 100g)
    calorias_100g: Optional[Decimal] = Field(None, ge=0, description="Calorias por 100g")
    proteinas_100g: Optional[Decimal] = Field(None, ge=0, description="Proteínas por 100g")
    carboidratos_100g: Optional[Decimal] = Field(None, ge=0, description="Carboidratos por 100g")
    gorduras_100g: Optional[Decimal] = Field(None, ge=0, description="Gorduras por 100g")
    
    # Dados comerciais
    unidade_compra: str = Field(..., description="Unidade de compra (kg, g, un, etc)")
    preco_medio: Optional[Decimal] = Field(None, gt=0, description="Preço médio por unidade")
    fornecedor_principal_id: Optional[int] = Field(None, description="ID do fornecedor principal")
    
    # Controle
    estoque_minimo: Decimal = Field(default=Decimal('0'), ge=0, description="Estoque mínimo")
    estoque_maximo: Optional[Decimal] = Field(None, gt=0, description="Estoque máximo")
    dias_validade_padrao: Optional[int] = Field(None, ge=1, description="Validade padrão em dias")
    
    # Alérgenos e restrições
    contém_gluten: bool = Field(default=False, description="Contém glúten")
    contém_lactose: bool = Field(default=False, description="Contém lactose")
    vegano: bool = Field(default=True, description="É vegano")
    alergenos: Optional[List[str]] = Field(default_factory=list, description="Lista de alérgenos")

class IngredienteCreate(IngredienteBase):
    """Modelo para criação de ingredientes"""
    estoque_inicial: Decimal = Field(default=Decimal('0'), ge=0, description="Estoque inicial")

class IngredienteResponse(IngredienteBase):
    """Modelo de resposta para ingredientes"""
    id: int = Field(..., description="ID único")
    estoque_atual: Decimal = Field(..., description="Estoque atual")
    valor_total_estoque: Optional[Decimal] = Field(None, description="Valor total em estoque")
    fornecedor_principal_nome: Optional[str] = Field(None, description="Nome do fornecedor principal")
    lotes_ativos: int = Field(default=0, description="Número de lotes ativos")
    proximo_vencimento: Optional[date] = Field(None, description="Data do próximo vencimento")
    created_at: datetime = Field(..., description="Data de cadastro")
    updated_at: Optional[datetime] = Field(None, description="Última atualização")

class IngredienteUpdate(BaseModel):
    """Modelo para atualização de ingredientes"""
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    tipo: Optional[TipoIngrediente] = None
    descricao: Optional[str] = Field(None, max_length=500)
    calorias_100g: Optional[Decimal] = Field(None, ge=0)
    proteinas_100g: Optional[Decimal] = Field(None, ge=0)
    carboidratos_100g: Optional[Decimal] = Field(None, ge=0)
    gorduras_100g: Optional[Decimal] = Field(None, ge=0)
    unidade_compra: Optional[str] = None
    preco_medio: Optional[Decimal] = Field(None, gt=0)
    fornecedor_principal_id: Optional[int] = None
    estoque_minimo: Optional[Decimal] = Field(None, ge=0)
    estoque_maximo: Optional[Decimal] = Field(None, gt=0)
    dias_validade_padrao: Optional[int] = Field(None, ge=1)
    contém_gluten: Optional[bool] = None
    contém_lactose: Optional[bool] = None
    vegano: Optional[bool] = None
    alergenos: Optional[List[str]] = None

# ========================
# MODELOS DE LOTES
# ========================

class LoteBase(BaseModel):
    """Modelo base para lotes"""
    
    numero_lote: str = Field(..., min_length=1, max_length=50, description="Número identificador do lote")
    ingrediente_id: int = Field(..., gt=0, description="ID do ingrediente")
    fornecedor_id: int = Field(..., gt=0, description="ID do fornecedor")
    
    # Dados do lote
    quantidade: Decimal = Field(..., gt=0, description="Quantidade do lote")
    preco_unitario: Decimal = Field(..., gt=0, description="Preço unitário pago")
    data_fabricacao: Optional[date] = Field(None, description="Data de fabricação")
    data_validade: date = Field(..., description="Data de validade")
    data_recebimento: date = Field(default_factory=date.today, description="Data de recebimento")
    
    # Controle de qualidade
    aprovado_qualidade: bool = Field(default=True, description="Aprovado no controle de qualidade")
    observacoes_qualidade: Optional[str] = Field(None, max_length=500, description="Observações da qualidade")
    
    # Rastreabilidade
    numero_nota_fiscal: Optional[str] = Field(None, max_length=50, description="Número da nota fiscal")
    lote_fornecedor: Optional[str] = Field(None, max_length=50, description="Lote do fornecedor")
    certificacoes: Optional[List[str]] = Field(default_factory=list, description="Certificações do lote")

    @model_validator(mode='after')
    def validate_datas(self):
        """Validar consistência das datas"""
        hoje = date.today()
        
        if self.data_validade <= hoje:
            raise ValueError('Data de validade deve ser futura')
        
        if self.data_fabricacao and self.data_fabricacao > hoje:
            raise ValueError('Data de fabricação não pode ser futura')
        
        if self.data_fabricacao and self.data_validade <= self.data_fabricacao:
            raise ValueError('Data de validade deve ser posterior à fabricação')
        
        return self

class LoteCreate(LoteBase):
    """Modelo para criação de lotes"""
    pass

class LoteResponse(LoteBase):
    """Modelo de resposta para lotes"""
    id: int = Field(..., description="ID único")
    status: StatusLote = Field(..., description="Status atual do lote")
    quantidade_disponivel: Decimal = Field(..., description="Quantidade ainda disponível")
    quantidade_consumida: Decimal = Field(default=Decimal('0'), description="Quantidade já consumida")
    valor_total: Decimal = Field(..., description="Valor total do lote")
    dias_para_vencimento: int = Field(..., description="Dias até o vencimento")
    ingrediente_nome: str = Field(..., description="Nome do ingrediente")
    fornecedor_nome: str = Field(..., description="Nome do fornecedor")
    created_at: datetime = Field(..., description="Data de cadastro")
    updated_at: Optional[datetime] = Field(None, description="Última atualização")

class LoteUpdate(BaseModel):
    """Modelo para atualização de lotes"""
    numero_lote: Optional[str] = Field(None, min_length=1, max_length=50)
    quantidade: Optional[Decimal] = Field(None, gt=0)
    preco_unitario: Optional[Decimal] = Field(None, gt=0)
    data_fabricacao: Optional[date] = None
    data_validade: Optional[date] = None
    aprovado_qualidade: Optional[bool] = None
    observacoes_qualidade: Optional[str] = Field(None, max_length=500)
    numero_nota_fiscal: Optional[str] = Field(None, max_length=50)
    lote_fornecedor: Optional[str] = Field(None, max_length=50)
    certificacoes: Optional[List[str]] = None

# ========================
# MODELOS DE COMPOSIÇÃO (RECEITAS)
# ========================

class ComposicaoIngrediente(BaseModel):
    """Ingrediente em uma receita"""
    ingrediente_id: int = Field(..., gt=0, description="ID do ingrediente")
    quantidade: Decimal = Field(..., gt=0, description="Quantidade necessária")
    unidade: str = Field(..., description="Unidade de medida")
    percentual: Optional[Decimal] = Field(None, ge=0, le=100, description="Percentual na receita")
    custo_unitario: Optional[Decimal] = Field(None, description="Custo por unidade")
    observacoes: Optional[str] = Field(None, max_length=200, description="Observações específicas")

class ReceitaProduto(BaseModel):
    """Receita completa de um produto"""
    produto_id: int = Field(..., gt=0, description="ID do produto")
    nome_receita: str = Field(..., min_length=2, max_length=100, description="Nome da receita")
    versao: str = Field(default="1.0", description="Versão da receita")
    rendimento: Decimal = Field(..., gt=0, description="Rendimento (quantas unidades produz)")
    tempo_preparo_minutos: Optional[int] = Field(None, ge=0, description="Tempo de preparo em minutos")
    
    ingredientes: List[ComposicaoIngrediente] = Field(..., min_items=1, description="Lista de ingredientes")
    
    # Dados calculados
    custo_total: Optional[Decimal] = Field(None, description="Custo total da receita")
    custo_por_unidade: Optional[Decimal] = Field(None, description="Custo por unidade produzida")
    
    # Informações nutricionais calculadas
    calorias_totais: Optional[Decimal] = Field(None, description="Calorias totais da receita")
    informacoes_nutricionais: Optional[Dict[str, Any]] = Field(None, description="Informações nutricionais detalhadas")
    
    # Controle
    ativa: bool = Field(default=True, description="Receita ativa")
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações da receita")
    created_at: Optional[datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Última atualização")

# ========================
# MODELOS DE RELATÓRIOS
# ========================

class RelatorioRastreabilidade(BaseModel):
    """Relatório de rastreabilidade de um produto"""
    produto_id: int
    produto_nome: str
    lote_produto: Optional[str]
    data_producao: date
    
    ingredientes_utilizados: List[Dict[str, Any]] = Field(
        ..., 
        description="Lista de ingredientes com seus respectivos lotes"
    )
    
    fornecedores_envolvidos: List[Dict[str, Any]] = Field(
        ...,
        description="Lista de fornecedores dos ingredientes"
    )
    
    certificacoes_produto: List[str] = Field(
        default_factory=list,
        description="Certificações aplicáveis ao produto"
    )
    
    validade_minima: date = Field(..., description="Menor data de validade entre os ingredientes")
    custo_total_ingredientes: Decimal = Field(..., description="Custo total dos ingredientes utilizados")

class RelatorioEstoque(BaseModel):
    """Relatório de estoque de ingredientes"""
    total_ingredientes: int
    valor_total_estoque: Decimal
    ingredientes_estoque_baixo: List[Dict[str, Any]]
    ingredientes_vencimento_proximo: List[Dict[str, Any]]
    lotes_vencidos: List[Dict[str, Any]]
    fornecedores_principais: List[Dict[str, Any]]
    resumo_por_categoria: Dict[str, Any]
    gerado_em: datetime = Field(default_factory=datetime.now)

class RelatorioCusto(BaseModel):
    """Relatório de análise de custos"""
    produto_id: int
    produto_nome: str
    custo_ingredientes: Decimal
    custo_por_unidade: Decimal
    margem_atual: Decimal
    margem_percentual: float
    comparativo_fornecedores: List[Dict[str, Any]]
    oportunidades_economia: List[Dict[str, Any]]
    tendencia_precos: Optional[Dict[str, Any]]

