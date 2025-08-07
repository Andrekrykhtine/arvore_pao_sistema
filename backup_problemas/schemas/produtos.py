# Criar arquivo de schemas para produtos
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

# Schema base comum
class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do produto")
    descricao: Optional[str] = Field(None, max_length=1000, description="Descrição do produto")
    codigo_interno: Optional[str] = Field(None, max_length=50, description="Código interno")
    codigo_barras: Optional[str] = Field(None, max_length=50, description="Código de barras")
    categoria_id: Optional[int] = Field(None, description="ID da categoria")
    fornecedor_principal_id: Optional[int] = Field(None, description="ID do fornecedor principal")
    unidade_medida: str = Field("un", max_length=10, description="Unidade de medida")
    quantidade_atual: float = Field(0, ge=0, description="Quantidade em estoque")
    quantidade_minima: float = Field(0, ge=0, description="Estoque mínimo")
    preco_venda: float = Field(0, ge=0, description="Preço de venda")
    ativo: bool = Field(True, description="Produto ativo")

    @validator('nome')
    def nome_nao_vazio(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome não pode estar vazio')
        return v.strip()

    @validator('unidade_medida')
    def unidade_valida(cls, v):
        unidades_validas = ['un', 'kg', 'g', 'l', 'ml', 'm', 'cm', 'pc', 'cx']
        if v not in unidades_validas:
            raise ValueError(f'Unidade deve ser uma de: {", ".join(unidades_validas)}')
        return v

# Schema para criação
class ProdutoCreate(ProdutoBase):
    pass

# Schema para atualização (todos os campos opcionais)
class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = Field(None, max_length=1000)
    codigo_interno: Optional[str] = Field(None, max_length=50)
    codigo_barras: Optional[str] = Field(None, max_length=50)
    categoria_id: Optional[int] = None
    fornecedor_principal_id: Optional[int] = None
    unidade_medida: Optional[str] = Field(None, max_length=10)
    quantidade_atual: Optional[float] = Field(None, ge=0)
    quantidade_minima: Optional[float] = Field(None, ge=0)
    preco_venda: Optional[float] = Field(None, ge=0)
    ativo: Optional[bool] = None

# Schema para resposta (inclui campos calculados)
class ProdutoResponse(ProdutoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    categoria_nome: Optional[str] = None
    fornecedor_nome: Optional[str] = None
    status_estoque: dict
    valor_estoque_total: float
    precisa_reposicao: bool

    class Config:
        from_attributes = True

# Schema para listagem (mais enxuto)
class ProdutoList(BaseModel):
    id: int
    nome: str
    codigo_interno: Optional[str]
    categoria_nome: Optional[str]
    quantidade_atual: float
    quantidade_minima: float
    preco_venda: float
    status_estoque: dict
    ativo: bool

    class Config:
        from_attributes = True

# Schema para filtros
class ProdutoFiltros(BaseModel):
    categoria_id: Optional[int] = None
    fornecedor_id: Optional[int] = None
    ativo: Optional[bool] = True
    busca: Optional[str] = None  # Busca por nome ou código
    estoque_baixo: Optional[bool] = None
    
# Schema para resposta paginada
class ProdutosPaginados(BaseModel):
    produtos: List[ProdutoList]
    total: int
    pagina: int
    por_pagina: int
    total_paginas: int

