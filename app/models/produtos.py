from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Index
from sqlalchemy.sql import func
from app.core.database import Base

class Produto(Base):
    """Modelo para produtos do estoque"""
    __tablename__ = "produtos"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Informações básicas
    nome = Column(String(255), nullable=False, index=True)
    categoria = Column(String(100), index=True)
    subcategoria = Column(String(100))
    unidade_medida = Column(String(10), nullable=False)  # kg, g, un, l, ml
    codigo_barras = Column(String(50), unique=True, index=True)
    codigo_interno = Column(String(50), unique=True, index=True)
    
    # Descrição e especificações
    descricao = Column(Text)
    marca = Column(String(100))
    modelo = Column(String(100))
    
    # Estoque
    quantidade_atual = Column(Float, default=0, nullable=False)
    quantidade_minima = Column(Float, default=0)
    quantidade_maxima = Column(Float, default=1000)
    ponto_reposicao = Column(Float, default=10)
    
    # Preços e custos
    custo_medio = Column(Float, default=0)
    ultimo_custo = Column(Float, default=0)
    preco_venda = Column(Float, default=0)
    margem_lucro = Column(Float, default=0)
    
    # Fornecedor
    fornecedor_principal = Column(String(255))
    codigo_fornecedor = Column(String(100))
    
    # Status e controle
    ativo = Column(Boolean, default=True, nullable=False)
    perecivel = Column(Boolean, default=False)
    controlado = Column(Boolean, default=False)
    
    # Localização
    localizacao = Column(String(100))  # Ex: Prateleira A, Setor 1
    
    # Auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Índices para performance
    __table_args__ = (
        Index('idx_produto_nome_ativo', 'nome', 'ativo'),
        Index('idx_produto_categoria_ativo', 'categoria', 'ativo'),
        Index('idx_produto_estoque', 'quantidade_atual'),
    )
    
    def __repr__(self):
        return f"<Produto(id={self.id}, nome='{self.nome}', quantidade={self.quantidade_atual})>"
    
    @property
    def valor_total_estoque(self):
        """Valor total do produto em estoque"""
        return (self.quantidade_atual or 0) * (self.custo_medio or 0)
    
    @property
    def precisa_reposicao(self):
        """Verifica se produto precisa de reposição"""
        return (self.quantidade_atual or 0) <= (self.ponto_reposicao or 0)
    
    @property
    def status_estoque(self):
        """Status atual do estoque"""
        if self.quantidade_atual <= 0:
            return "esgotado"
        elif self.precisa_reposicao:
            return "baixo"
        elif self.quantidade_atual >= self.quantidade_maxima:
            return "alto"
        else:
            return "normal"

class MovimentacaoEstoque(Base):
    """Modelo para movimentações de estoque"""
    __tablename__ = "movimentacoes_estoque"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamento com produto
    produto_id = Column(Integer, nullable=False, index=True)
    
    # Tipo de movimentação
    tipo = Column(String(20), nullable=False, index=True)  # entrada, saida
    motivo = Column(String(50), nullable=False, index=True)  # compra, venda, ajuste, perda, producao
    
    # Quantidades
    quantidade = Column(Float, nullable=False)
    quantidade_anterior = Column(Float, nullable=False)
    quantidade_atual = Column(Float, nullable=False)
    
    # Valores
    valor_unitario = Column(Float, default=0)
    valor_total = Column(Float, default=0)
    
    # Documento de referência
    documento_tipo = Column(String(50))  # nf_entrada, nf_saida, ajuste_manual
    documento_numero = Column(String(100))
    documento_serie = Column(String(10))
    
    # Observações
    observacoes = Column(Text)
    
    # Auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100))
    
    # Índices
    __table_args__ = (
        Index('idx_movimentacao_produto_data', 'produto_id', 'created_at'),
        Index('idx_movimentacao_tipo_data', 'tipo', 'created_at'),
    )
    
    def __repr__(self):
        return f"<MovimentacaoEstoque(id={self.id}, produto_id={self.produto_id}, tipo='{self.tipo}', quantidade={self.quantidade})>"
