# Criar arquivo de schemas básicos
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProdutoBase(BaseModel):
    """Schema base para produtos"""
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do produto")
    unidade_medida: str = Field("un", max_length=10, description="Unidade de medida")
    quantidade_atual: float = Field(0, ge=0, description="Quantidade em estoque")
    quantidade_minima: float = Field(0, ge=0, description="Estoque mínimo")
    preco_venda: float = Field(0, ge=0, description="Preço de venda")

class ProdutoCreate(ProdutoBase):
    """Schema para criação de produtos"""
    pass

class ProdutoUpdate(BaseModel):
    """Schema para atualização de produtos (campos opcionais)"""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    unidade_medida: Optional[str] = Field(None, max_length=10)
    quantidade_atual: Optional[float] = Field(None, ge=0)
    quantidade_minima: Optional[float] = Field(None, ge=0)
    preco_venda: Optional[float] = Field(None, ge=0)

class ProdutoResponse(ProdutoBase):
    """Schema para resposta de produtos"""
    id: int
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProdutoSimple(BaseModel):
    """Schema simples para listagens"""
    id: int
    nome: str
    quantidade_atual: float
    preco_venda: float
    
    class Config:
        from_attributes = True
