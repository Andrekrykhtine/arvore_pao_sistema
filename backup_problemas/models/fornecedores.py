from sqlalchemy import Column, String, Text, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Fornecedor(BaseModel):
    """Fornecedores de produtos"""
    __tablename__ = "fornecedores"
    
    # Informações básicas
    nome = Column(String(255), nullable=False, index=True)
    nome_fantasia = Column(String(255))
    razao_social = Column(String(255))
    
    # Documentos
    cnpj = Column(String(18), unique=True, index=True)
    ie = Column(String(20))  # Inscrição Estadual
    im = Column(String(20))  # Inscrição Municipal
    
    # Contato
    email = Column(String(255))
    telefone = Column(String(20))
    celular = Column(String(20))
    site = Column(String(255))
    
    # Endereço
    endereco = Column(Text)
    cep = Column(String(10))
    cidade = Column(String(100))
    estado = Column(String(2))
    pais = Column(String(50), default="Brasil")
    
    # Informações comerciais
    prazo_entrega_dias = Column(Integer, default=7)
    valor_minimo_pedido = Column(Float, default=0)
    desconto_padrao = Column(Float, default=0)  # Percentual
    forma_pagamento_padrao = Column(String(50))
    
    # Classificação e avaliação
    classificacao = Column(String(10), default="A")  # A, B, C, D
    avaliacao = Column(Float, default=5.0)  # 1-5 estrelas
    observacoes = Column(Text)
    
    # Status
    aprovado = Column(Boolean, default=True)
    bloqueado = Column(Boolean, default=False)
    
    # Dados adicionais (JSON para flexibilidade)
    dados_extras = Column(JSON)
    
    # Relacionamentos
    produtos = relationship("Produto", back_populates="fornecedor_obj")
    cotacoes = relationship("Cotacao", back_populates="fornecedor")
    
    # Índices
    __table_args__ = (
        Index('idx_fornecedor_cnpj', 'cnpj'),
        Index('idx_fornecedor_nome_ativo', 'nome', 'is_active'),
        Index('idx_fornecedor_aprovado', 'aprovado', 'is_active'),
    )
    
    def __repr__(self):
        return f"<Fornecedor(id={self.id}, nome='{self.nome}')>"
    
    @property
    def nome_display(self):
        """Nome para exibição"""
        return self.nome_fantasia if self.nome_fantasia else self.nome
    
    @property
    def total_produtos_ativos(self):
        """Total de produtos ativos deste fornecedor"""
        return len([p for p in self.produtos if p.is_active])
    
    @property
    def status_display(self):
        """Status formatado para exibição"""
        if self.bloqueado:
            return "🔴 Bloqueado"
        elif not self.aprovado:
            return "🟡 Pendente Aprovação"
        elif self.is_active:
            return "🟢 Ativo"
        else:
            return "⚪ Inativo"