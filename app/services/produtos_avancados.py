# app/schemas/produtos_avancados.py
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.types import condecimal
from typing import Optional, List, Dict, Any, Annotated
from datetime import datetime
from decimal import Decimal
from enum import Enum


class UnidadeMedida(str, Enum):
    """Enum para unidades de medida padronizadas"""
    QUILOGRAMA = "kg"
    GRAMA = "g"
    LITRO = "l"
    MILILITRO = "ml"
    UNIDADE = "un"
    CAIXA = "cx"
    PACOTE = "pct"
    METRO = "m"
    CENTIMETRO = "cm"


class StatusProduto(str, Enum):
    """Status do produto no sistema"""
    ATIVO = "ativo"
    INATIVO = "inativo"
    DESCONTINUADO = "descontinuado"
    EM_DESENVOLVIMENTO = "em_desenvolvimento"


class CategoriaProduto(str, Enum):
    """Categorias de produtos da padaria"""
    PAES = "paes"
    DOCES = "doces"
    SALGADOS = "salgados"
    BEBIDAS = "bebidas"
    INGREDIENTES = "ingredientes"
    EMBALAGENS = "embalagens"
    OUTROS = "outros"


# Definir tipos customizados para Decimal
PrecoDecimal = Annotated[Decimal, condecimal(max_digits=10, decimal_places=2, gt=0)]
CustoDecimal = Annotated[Decimal, condecimal(max_digits=10, decimal_places=2, ge=0)]
QuantidadeDecimal = Annotated[Decimal, condecimal(max_digits=12, decimal_places=3, ge=0)]


class ProdutoBase(BaseModel):
    """Modelo base para produtos com validações avançadas"""
    
    nome: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nome do produto",
        examples=["Pão Francês", "Bolo de Chocolate"]
    )
    
    descricao: Optional[str] = Field(
        None,
        max_length=500,
        description="Descrição detalhada do produto",
        examples=["Pão tradicional francês crocante por fora e macio por dentro"]
    )
    
    categoria: CategoriaProduto = Field(
        ...,
        description="Categoria do produto",
        examples=[CategoriaProduto.PAES]
    )
    
    unidade_medida: UnidadeMedida = Field(
        ...,
        description="Unidade de medida do produto",
        examples=[UnidadeMedida.UNIDADE]
    )
    
    preco_venda: PrecoDecimal = Field(
        ...,
        description="Preço de venda unitário",
        examples=[2.50]
    )
    
    preco_custo: Optional[CustoDecimal] = Field(
        None,
        description="Preço de custo do produto",
        examples=[1.20]
    )
    
    margem_lucro: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Margem de lucro em porcentagem",
        examples=[45.5]
    )
    
    codigo_barras: Optional[str] = Field(
        None, 
        pattern=r"^\d{8,14}$", 
        description="Código de barras do produto"
    )
    
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Tags para categorização adicional",
        examples=[["artesanal", "sem glúten", "vegano"]]
    )
    
    @field_validator('nome')
    @classmethod
    def validate_nome(cls, v):
        """Validar e normalizar nome do produto"""
        if not v or not v.strip():
            raise ValueError('Nome não pode estar vazio')
        
        # Normalizar nome (primeira letra maiúscula)
        return v.strip().title()
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validar tags"""
        if v:
            # Remover duplicatas e normalizar
            return list(set(tag.lower().strip() for tag in v if tag.strip()))
        return v
    
    @model_validator(mode='after')
    def validate_precos(self):
        """Validar consistência entre preços"""
        if self.preco_custo and self.preco_venda and self.preco_custo >= self.preco_venda:
            raise ValueError('Preço de custo deve ser menor que preço de venda')
        
        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nome": "Pão Francês",
                    "descricao": "Pão tradicional francês, crocante e saboroso",
                    "categoria": "paes",
                    "unidade_medida": "un",
                    "preco_venda": 0.80,
                    "preco_custo": 0.35,
                    "margem_lucro": 56.25,
                    "codigo_barras": "7891234567890",
                    "tags": ["artesanal", "tradicional"]
                }
            ]
        }
    }


class ProdutoCreate(ProdutoBase):
    """Modelo para criação de produtos"""

    quantidade_inicial: QuantidadeDecimal = Field(
        default=Decimal('0'),
        description="Quantidade inicial em estoque",
        examples=[100.0]
    )

    quantidade_minima: QuantidadeDecimal = Field(
        ...,
        description="Quantidade mínima para alerta de estoque",
        examples=[10.0]
    )
    
    quantidade_maxima: Optional[QuantidadeDecimal] = Field(
        None,
        description="Quantidade máxima em estoque",
        examples=[500.0]
    )
    
    fornecedor_principal: Optional[str] = Field(
        None,
        max_length=100,
        description="Nome do fornecedor principal",
        examples=["Fornecedor ABC"]
    )
    
    observacoes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Observações adicionais sobre o produto",
        examples=["Produto sazonal, disponível apenas no inverno"]
    )
    
    @model_validator(mode='after')
    def validate_quantidades(self):
        """Validar consistência das quantidades"""
        qtd_inicial = self.quantidade_inicial or Decimal('0')
        qtd_minima = self.quantidade_minima or Decimal('0')
        qtd_maxima = self.quantidade_maxima
        
        if qtd_inicial < qtd_minima:
            raise ValueError('Quantidade inicial não pode ser menor que quantidade mínima')
        
        if qtd_maxima and qtd_inicial > qtd_maxima:
            raise ValueError('Quantidade inicial não pode ser maior que quantidade máxima')
            
        if qtd_maxima and qtd_minima > qtd_maxima:
            raise ValueError('Quantidade mínima não pode ser maior que quantidade máxima')
        
        return self


class ProdutoUpdate(BaseModel):
    """Modelo para atualização de produtos (campos opcionais)"""
    
    nome: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Nome do produto"
    )
    
    descricao: Optional[str] = Field(
        None,
        max_length=500,
        description="Descrição do produto"
    )
    
    categoria: Optional[CategoriaProduto] = Field(
        None,
        description="Categoria do produto"
    )
    
    unidade_medida: Optional[UnidadeMedida] = Field(
        None,
        description="Unidade de medida"
    )
    
    preco_venda: Optional[PrecoDecimal] = Field(
        None,
        description="Preço de venda"
    )
    
    preco_custo: Optional[CustoDecimal] = Field(
        None,
        description="Preço de custo"
    )
    
    quantidade_atual: Optional[QuantidadeDecimal] = Field(
        None,
        description="Quantidade atual em estoque"
    )
    
    quantidade_minima: Optional[QuantidadeDecimal] = Field(
        None,
        description="Quantidade mínima para alerta"
    )
    
    quantidade_maxima: Optional[QuantidadeDecimal] = Field(
        None,
        description="Quantidade máxima em estoque"
    )
    
    status: Optional[StatusProduto] = Field(
        None,
        description="Status do produto"
    )
    
    tags: Optional[List[str]] = Field(
        None,
        description="Tags do produto"
    )
    
    observacoes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Observações"
    )
    
    @field_validator('nome')
    @classmethod
    def validate_nome(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Nome não pode estar vazio')
            return v.strip().title()
        return v


class StatusEstoque(BaseModel):
    """Modelo para status de estoque"""
    status: str = Field(..., description="Status: normal, baixo, esgotado")
    cor: str = Field(..., description="Cor para exibição")
    icone: str = Field(..., description="Ícone para exibição")
    urgencia: int = Field(..., ge=1, le=5, description="Nível de urgência (1-5)")


class ProdutoResponse(ProdutoBase):
    """Modelo para resposta completa de produtos"""
    
    id: int = Field(..., description="ID único do produto")
    
    quantidade_atual: QuantidadeDecimal = Field(
        ...,
        description="Quantidade atual em estoque"
    )
    
    quantidade_minima: QuantidadeDecimal = Field(
        ...,
        description="Quantidade mínima para alerta"
    )
    
    quantidade_maxima: Optional[QuantidadeDecimal] = Field(
        None,
        description="Quantidade máxima em estoque"
    )
    
    status: StatusProduto = Field(
        ...,
        description="Status do produto"
    )
    
    status_estoque: StatusEstoque = Field(
        ...,
        description="Status atual do estoque"
    )
    
    valor_estoque_total: PrecoDecimal = Field(
        ...,
        description="Valor total do estoque (quantidade * preço)"
    )
    
    margem_lucro_calculada: Optional[float] = Field(
        None,
        description="Margem de lucro calculada (%)"
    )
    
    giro_estoque: Optional[float] = Field(
        None,
        description="Giro de estoque (últimos 30 dias)"
    )
    
    dias_sem_venda: Optional[int] = Field(
        None,
        description="Dias sem movimentação de venda"
    )
    
    fornecedor_principal: Optional[str] = Field(
        None,
        description="Fornecedor principal"
    )
    
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data da última atualização")
    
    # Campos calculados
    precisa_reposicao: bool = Field(..., description="Se precisa de reposição")
    percentual_estoque: float = Field(..., description="Percentual do estoque (atual/máximo)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "nome": "Pão Francês",
                    "descricao": "Pão tradicional francês",
                    "categoria": "paes",
                    "unidade_medida": "un",
                    "preco_venda": 0.80,
                    "preco_custo": 0.35,
                    "quantidade_atual": 150.0,
                    "quantidade_minima": 50.0,
                    "quantidade_maxima": 500.0,
                    "status": "ativo",
                    "status_estoque": {
                        "status": "normal",
                        "cor": "#27ae60",
                        "icone": "✅",
                        "urgencia": 1
                    },
                    "valor_estoque_total": 120.00,
                    "margem_lucro_calculada": 56.25,
                    "precisa_reposicao": False,
                    "percentual_estoque": 30.0
                }
            ]
        }
    }


class ProdutoSimple(BaseModel):
    """Modelo simplificado para listagens"""
    id: int
    nome: str
    categoria: CategoriaProduto
    preco_venda: PrecoDecimal
    quantidade_atual: QuantidadeDecimal
    status_estoque: StatusEstoque
    

class ProdutoSummary(BaseModel):
    """Modelo para resumos e estatísticas"""
    id: int
    nome: str
    categoria: CategoriaProduto
    valor_estoque: PrecoDecimal
    giro_mensal: Optional[float]
    margem_lucro: Optional[float]
    ranking_vendas: Optional[int]
