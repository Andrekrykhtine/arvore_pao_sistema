from sqlalchemy import Column, String, Text, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Categoria(BaseModel):
    """Categorias de produtos"""
    __tablename__ = "categorias"
    
    nome = Column(String(100), nullable=False, unique=True, index=True)
    descricao = Column(Text)
    codigo = Column(String(20), unique=True, index=True)
    cor_hex = Column(String(7), default="#3498db")  # Cor para interface
    icone = Column(String(50), default="box")  # Ícone para interface
    
    # Hierarquia de categorias (categoria pai)
    categoria_pai_id = Column(Integer, nullable=True, index=True)
    
    # Configurações específicas
    perecivel_por_padrao = Column(Boolean, default=False)
    controlado_por_padrao = Column(Boolean, default=False)
    margem_padrao = Column(Float, default=30.0)  # Margem de lucro padrão (%)
    
    # Relacionamentos
    produtos = relationship("Produto", back_populates="categoria_obj")
    subcategorias = relationship("Categoria", backref="categoria_pai", remote_side="Categoria.id")
    
    # Índices para performance
    __table_args__ = (
        Index('idx_categoria_nome_ativo', 'nome', 'is_active'),
        Index('idx_categoria_codigo', 'codigo'),
    )
    
    def __repr__(self):
        return f"<Categoria(id={self.id}, nome='{self.nome}')>"
    
    @property
    def nome_completo(self):
        """Nome completo incluindo categoria pai"""
        if self.categoria_pai:
            return f"{self.categoria_pai.nome} > {self.nome}"
        return self.nome
    
    @property
    def total_produtos(self):
        """Total de produtos nesta categoria"""
        return len([p for p in self.produtos if p.is_active])
