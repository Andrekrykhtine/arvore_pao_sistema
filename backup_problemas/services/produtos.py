# Criar serviços para produtos
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from app.models.produtos import Produto
from app.models.categorias import Categoria
from app.models.fornecedores import Fornecedor
from app.schemas.produtos import ProdutoCreate, ProdutoUpdate, ProdutoFiltros
import math

class ProdutoService:
    """Serviços para gerenciamento de produtos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def criar_produto(self, produto_data: ProdutoCreate) -> Produto:
        """Criar novo produto"""
        # Verificar se código interno já existe
        if produto_data.codigo_interno:
            produto_existente = self.db.query(Produto).filter(
                Produto.codigo_interno == produto_data.codigo_interno,
                Produto.is_active == True
            ).first()
            if produto_existente:
                raise ValueError(f"Produto com código interno '{produto_data.codigo_interno}' já existe")
        
        # Verificar se código de barras já existe
        if produto_data.codigo_barras:
            produto_existente = self.db.query(Produto).filter(
                Produto.codigo_barras == produto_data.codigo_barras,
                Produto.is_active == True
            ).first()
            if produto_existente:
                raise ValueError(f"Produto com código de barras '{produto_data.codigo_barras}' já existe")
        
        # Criar produto
        produto = Produto(**produto_data.dict())
        self.db.add(produto)
        self.db.commit()
        self.db.refresh(produto)
        
        return produto
    
    def listar_produtos(self, 
                       filtros: ProdutoFiltros,
                       pagina: int = 1, 
                       por_pagina: int = 20) -> tuple[List[Produto], int]:
        """Listar produtos com filtros e paginação"""
        query = self.db.query(Produto)
        
        # Aplicar filtros
        if filtros.ativo is not None:
            query = query.filter(Produto.is_active == filtros.ativo)
        
        if filtros.categoria_id:
            query = query.filter(Produto.categoria_id == filtros.categoria_id)
        
        if filtros.fornecedor_id:
            query = query.filter(Produto.fornecedor_principal_id == filtros.fornecedor_id)
        
        if filtros.busca:
            busca = f"%{filtros.busca}%"
            query = query.filter(
                or_(
                    Produto.nome.ilike(busca),
                    Produto.codigo_interno.ilike(busca),
                    Produto.codigo_barras.ilike(busca)
                )
            )
        
        if filtros.estoque_baixo:
            query = query.filter(Produto.quantidade_atual <= Produto.quantidade_minima)
        
        # Contar total
        total = query.count()
        
        # Aplicar paginação
        offset = (pagina - 1) * por_pagina
        produtos = query.offset(offset).limit(por_pagina).all()
        
        return produtos, total
    
    def obter_produto(self, produto_id: int) -> Optional[Produto]:
        """Obter produto por ID"""
        return self.db.query(Produto).filter(
            Produto.id == produto_id,
            Produto.is_active == True
        ).first()
    
    def atualizar_produto(self, produto_id: int, produto_data: ProdutoUpdate) -> Optional[Produto]:
        """Atualizar produto"""
        produto = self.obter_produto(produto_id)
        if not produto:
            return None
        
        # Verificar códigos únicos se foram alterados
        if produto_data.codigo_interno and produto_data.codigo_interno != produto.codigo_interno:
            produto_existente = self.db.query(Produto).filter(
                Produto.codigo_interno == produto_data.codigo_interno,
                Produto.id != produto_id,
                Produto.is_active == True
            ).first()
            if produto_existente:
                raise ValueError(f"Código interno '{produto_data.codigo_interno}' já existe")
        
        # Aplicar atualizações
        for campo, valor in produto_data.dict(exclude_unset=True).items():
            if valor is not None:
                setattr(produto, campo, valor)
        
        self.db.commit()
        self.db.refresh(produto)
        return produto
    
    def deletar_produto(self, produto_id: int) -> bool:
        """Soft delete de produto"""
        produto = self.obter_produto(produto_id)
        if not produto:
            return False
        
        produto.soft_delete()
        self.db.commit()
        return True
    
    def obter_produtos_estoque_baixo(self) -> List[Produto]:
        """Obter produtos com estoque baixo"""
        return self.db.query(Produto).filter(
            Produto.quantidade_atual <= Produto.quantidade_minima,
            Produto.is_active == True
        ).all()
    
    def buscar_por_codigo(self, codigo: str) -> Optional[Produto]:
        """Buscar produto por código interno ou de barras"""
        return self.db.query(Produto).filter(
            or_(
                Produto.codigo_interno == codigo,
                Produto.codigo_barras == codigo
            ),
            Produto.is_active == True
        ).first()


