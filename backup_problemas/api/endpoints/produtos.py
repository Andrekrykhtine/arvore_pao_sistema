# Criar endpoints para produtos
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.services.produtos import ProdutoService
from app.schemas.produtos import (
    ProdutoCreate, ProdutoUpdate, ProdutoResponse, 
    ProdutoList, ProdutoFiltros, ProdutosPaginados
)
import math

router = APIRouter(prefix="/produtos", tags=["Produtos"])

def get_produto_service(db: Session = Depends(get_db)) -> ProdutoService:
    """Dependency injection para ProdutoService"""
    return ProdutoService(db)

@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(
    produto_data: ProdutoCreate,
    service: ProdutoService = Depends(get_produto_service)
):
    """
    🆕 Criar novo produto
    
    Cria um novo produto no sistema com validações:
    - Nome obrigatório e único
    - Códigos interno e de barras únicos (se informados)
    - Unidade de medida válida
    """
    try:
        produto = service.criar_produto(produto_data)
        return _produto_para_response(produto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar produto: {str(e)}"
        )

@router.get("/", response_model=ProdutosPaginados)
def listar_produtos(
    pagina: int = Query(1, ge=1, description="Número da página"),
    por_pagina: int = Query(20, ge=1, le=100, description="Itens por página"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoria"),
    fornecedor_id: Optional[int] = Query(None, description="Filtrar por fornecedor"),
    ativo: Optional[bool] = Query(True, description="Filtrar por status ativo"),
    busca: Optional[str] = Query(None, description="Buscar por nome ou código"),
    estoque_baixo: Optional[bool] = Query(None, description="Apenas produtos com estoque baixo"),
    service: ProdutoService = Depends(get_produto_service)
):
    """
    📋 Listar produtos com filtros e paginação
    
    Parâmetros de filtro:
    - **categoria_id**: Filtrar por categoria específica
    - **fornecedor_id**: Filtrar por fornecedor específico  
    - **ativo**: true/false para produtos ativos/inativos
    - **busca**: Busca por nome, código interno ou código de barras
    - **estoque_baixo**: true para produtos que precisam reposição
    """
    try:
        filtros = ProdutoFiltros(
            categoria_id=categoria_id,
            fornecedor_id=fornecedor_id,
            ativo=ativo,
            busca=busca,
            estoque_baixo=estoque_baixo
        )
        
        produtos, total = service.listar_produtos(filtros, pagina, por_pagina)
        
        produtos_list = [_produto_para_list(produto) for produto in produtos]
        total_paginas = math.ceil(total / por_pagina)
        
        return ProdutosPaginados(
            produtos=produtos_list,
            total=total,
            pagina=pagina,
            por_pagina=por_pagina,
            total_paginas=total_paginas
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar produtos: {str(e)}"
        )

@router.get("/{produto_id}", response_model=ProdutoResponse)
def obter_produto(
    produto_id: int,
    service: ProdutoService = Depends(get_produto_service)
):
    """
    🔍 Obter produto específico por ID
    
    Retorna detalhes completos do produto incluindo:
    - Informações básicas
    - Status do estoque
    - Categoria e fornecedor
    - Propriedades calculadas
    """
    produto = service.obter_produto(produto_id)
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {produto_id} não encontrado"
        )
    
    return _produto_para_response(produto)

@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: int,
    produto_data: ProdutoUpdate,
    service: ProdutoService = Depends(get_produto_service)
):
    """
    ✏️ Atualizar produto existente
    
    Permite atualização parcial de qualquer campo do produto.
    Mantém validações de unicidade para códigos.
    """
    try:
        produto = service.atualizar_produto(produto_id, produto_data)
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto com ID {produto_id} não encontrado"
            )
        
        return _produto_para_response(produto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_produto(
    produto_id: int,
    service: ProdutoService = Depends(get_produto_service)
):
    """
    🗑️ Deletar produto (soft delete)
    
    Remove produto do sistema (soft delete).
    O produto fica inativo mas permanece no banco para auditoria.
    """
    sucesso = service.deletar_produto(produto_id)
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {produto_id} não encontrado"
        )

@router.get("/codigo/{codigo}", response_model=ProdutoResponse)
def buscar_por_codigo(
    codigo: str,
    service: ProdutoService = Depends(get_produto_service)
):
    """
    🔍 Buscar produto por código
    
    Busca por código interno ou código de barras.
    Útil para leitores de código de barras.
    """
    produto = service.buscar_por_codigo(codigo)
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com código '{codigo}' não encontrado"
        )
    
    return _produto_para_response(produto)

@router.get("/estoque/baixo", response_model=List[ProdutoList])
def produtos_estoque_baixo(
    service: ProdutoService = Depends(get_produto_service)
):
    """
    ⚠️ Produtos com estoque baixo
    
    Lista produtos que estão com quantidade atual
    menor ou igual à quantidade mínima.
    """
    produtos = service.obter_produtos_estoque_baixo()
    return [_produto_para_list(produto) for produto in produtos]

# Funções auxiliares para conversão
def _produto_para_response(produto) -> ProdutoResponse:
    """Converter modelo Produto para schema Response"""
    return ProdutoResponse(
        id=produto.id,
        nome=produto.nome,
        descricao=produto.descricao,
        codigo_interno=produto.codigo_interno,
        codigo_barras=produto.codigo_barras,
        categoria_id=produto.categoria_id,
        fornecedor_principal_id=produto.fornecedor_principal_id,
        unidade_medida=produto.unidade_medida,
        quantidade_atual=produto.quantidade_atual,
        quantidade_minima=produto.quantidade_minima,
        preco_venda=produto.preco_venda,
        ativo=produto.is_active,
        created_at=produto.created_at,
        updated_at=produto.updated_at,
        categoria_nome=produto.categoria_obj.nome if produto.categoria_obj else None,
        fornecedor_nome=produto.fornecedor_obj.nome if produto.fornecedor_obj else None,
        status_estoque=produto.status_estoque,
        valor_estoque_total=produto.valor_estoque_total,
        precisa_reposicao=produto.precisa_reposicao
    )

def _produto_para_list(produto) -> ProdutoList:
    """Converter modelo Produto para schema List"""
    return ProdutoList(
        id=produto.id,
        nome=produto.nome,
        codigo_interno=produto.codigo_interno,
        categoria_nome=produto.categoria_obj.nome if produto.categoria_obj else None,
        quantidade_atual=produto.quantidade_atual,
        quantidade_minima=produto.quantidade_minima,
        preco_venda=produto.preco_venda,
        status_estoque=produto.status_estoque,
        ativo=produto.is_active
    )

