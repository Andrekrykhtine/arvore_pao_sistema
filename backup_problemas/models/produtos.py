# Se ainda der erro, criar versão ultra básica
cat > app/models/produtos.py << 'PRODUTO_SIMPLES'
from sqlalchemy import Column, String, Float, Integer, Boolean
from app.models.base import BaseModel

class Produto(BaseModel):
    __tablename__ = "produtos"
    
    nome = Column(String(255), nullable=False)
    unidade_medida = Column(String(10), default="un")
    quantidade_atual = Column(Float, default=0)
    quantidade_minima = Column(Float, default=0)
    preco_venda = Column(Float, default=0)
    
    def __repr__(self):
        return f"<Produto(id={self.id}, nome='{self.nome}')>"
    
    @property
    def status_estoque(self):
        if self.quantidade_atual <= 0:
            return {"status": "esgotado", "icon": "❌"}
        elif self.quantidade_atual <= self.quantidade_minima:
            return {"status": "baixo", "icon": "⚠️"}
        else:
            return {"status": "normal", "icon": "✅"}
    
    @property
    def valor_estoque_total(self):
        return self.quantidade_atual * 0  # Placeholder
    
    @property
    def precisa_reposicao(self):
        return self.quantidade_atual <= self.quantidade_minima
    
    @property
    def categoria_nome(self):
        return "Sem categoria"
    
    @property
    def fornecedor_nome(self):
        return "Sem fornecedor"

