from sqlalchemy import Column, String, Float, Integer, ForeignKey, Text, Index, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class MovimentacaoEstoque(BaseModel):
    """Movimentações de estoque"""
    __tablename__ = "movimentacoes_estoque"
    
    # Relacionamento com produto
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    
    # Tipo e motivo da movimentação
    tipo = Column(String(20), nullable=False, index=True)  # entrada, saida
    motivo = Column(String(50), nullable=False, index=True)  # compra, venda, ajuste, perda, producao, devolucao
    subtipo = Column(String(50))  # detalhamento do motivo
    
    # Quantidades
    quantidade = Column(Float, nullable=False)
    quantidade_anterior = Column(Float, nullable=False)
    quantidade_atual = Column(Float, nullable=False)
    
    # Valores financeiros
    valor_unitario = Column(Float, default=0)
    valor_total = Column(Float, default=0)
    custo_medio_anterior = Column(Float, default=0)
    custo_medio_atual = Column(Float, default=0)
    
    # Documento de origem
    documento_tipo = Column(String(50))  # nf_entrada, nf_saida, ajuste_manual, requisicao
    documento_numero = Column(String(100))
    documento_serie = Column(String(10))
    documento_data = Column(DateTime(timezone=True))
    documento_valor = Column(Float)
    
    # Fornecedor/Cliente (se aplicável)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True, index=True)
    cliente_nome = Column(String(255))  # Para vendas
    cliente_documento = Column(String(20))
    
    # Localização
    localizacao_origem = Column(String(100))
    localizacao_destino = Column(String(100))
    
    # Responsável pela movimentação
    usuario_responsavel = Column(String(100))
    operador = Column(String(100))
    
    # Informações adicionais
    observacoes = Column(Text)
    justificativa = Column(Text)  # Para perdas, ajustes negativos
    numero_lote = Column(String(50))  # Controle de lote
    data_validade = Column(Date)  # Para produtos perecíveis
    
    # Status da movimentação
    status = Column(String(20), default="processada")  # pendente, processada, cancelada, erro
    processado_em = Column(DateTime(timezone=True))
    cancelado_em = Column(DateTime(timezone=True))
    motivo_cancelamento = Column(Text)
    
    # Dados adicionais flexíveis
    dados_extras = Column(JSON)
    
    # Relacionamentos
    produto = relationship("Produto", back_populates="movimentacoes")
    fornecedor = relationship("Fornecedor")
    
    # Índices para performance e relatórios
    __table_args__ = (
        Index('idx_mov_produto_data', 'produto_id', 'created_at'),
        Index('idx_mov_tipo_data', 'tipo', 'created_at'),
        Index('idx_mov_motivo_data', 'motivo', 'created_at'),
        Index('idx_mov_documento', 'documento_tipo', 'documento_numero'),
        Index('idx_mov_status', 'status'),
        Index('idx_mov_usuario', 'usuario_responsavel', 'created_at'),
    )
    
    def __repr__(self):
        return f"<MovimentacaoEstoque(id={self.id}, produto_id={self.produto_id}, tipo='{self.tipo}', qtd={self.quantidade})>"
    
    @property
    def descricao_completa(self):
        """Descrição completa da movimentação"""
        produto_nome = self.produto.nome if self.produto else f"Produto ID {self.produto_id}"
        sinal = "+" if self.tipo == "entrada" else "-"
        return f"{sinal}{self.quantidade} {produto_nome} - {self.motivo}"
    
    @property
    def impacto_financeiro(self):
        """Impacto financeiro da movimentação"""
        if self.tipo == "entrada":
            return self.valor_total
        else:
            return -self.valor_total
    
    @property
    def dias_desde_movimentacao(self):
        """Dias desde a movimentação"""
        if self.created_at:
            delta = datetime.now(self.created_at.tzinfo) - self.created_at
            return delta.days
        return 0

class Inventario(BaseModel):
    """Inventários/Contagens de estoque"""
    __tablename__ = "inventarios"
    
    # Informações do inventário
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text)
    data_inicio = Column(DateTime(timezone=True), nullable=False)
    data_fim = Column(DateTime(timezone=True))
    
    # Status
    status = Column(String(20), default="em_andamento")  # em_andamento, concluido, cancelado
    
    # Responsável
    responsavel = Column(String(100))
    equipe = Column(JSON)  # Lista de pessoas envolvidas
    
    # Configurações
    incluir_categorias = Column(JSON)  # IDs das categorias incluídas
    incluir_apenas_ativos = Column(Boolean, default=True)
    incluir_zerados = Column(Boolean, default=False)
    
    # Resultados
    total_produtos_contados = Column(Integer, default=0)
    total_divergencias = Column(Integer, default=0)
    valor_divergencia_total = Column(Float, default=0)
    
    # Observações
    observacoes = Column(Text)
    
    def __repr__(self):
        return f"<Inventario(id={self.id}, titulo='{self.titulo}', status='{self.status}')>"

class ItemInventario(BaseModel):
    """Itens de inventário"""
    __tablename__ = "itens_inventario"
    
    inventario_id = Column(Integer, ForeignKey("inventarios.id"), nullable=False, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    
    # Quantidades
    quantidade_sistema = Column(Float, nullable=False)  # Quantidade no sistema
    quantidade_contada = Column(Float)  # Quantidade contada fisicamente
    diferenca = Column(Float, default=0)  # Diferença (contada - sistema)
    
    # Valores
    custo_unitario = Column(Float, default=0)
    valor_diferenca = Column(Float, default=0)
    
    # Status da contagem
    contado = Column(Boolean, default=False)
    data_contagem = Column(DateTime(timezone=True))
    contador = Column(String(100))
    
    # Observações
    observacoes = Column(Text)
    motivo_diferenca = Column(String(100))  # perda, roubo, erro_sistema, vencimento
    
    # Relacionamentos
    inventario = relationship("Inventario")
    produto = relationship("Produto")
    
    __table_args__ = (
        Index('idx_item_inv_inventario', 'inventario_id'),
        Index('idx_item_inv_produto', 'produto_id'),
        Index('idx_item_inv_diferenca', 'diferenca'),
    )
    
    def __repr__(self):
        return f"<ItemInventario(inventario_id={self.inventario_id}, produto_id={self.produto_id}, diff={self.diferenca})>"


