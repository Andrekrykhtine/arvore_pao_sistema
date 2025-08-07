# Criar modelo de usuários
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Index
from sqlalchemy.sql import func
from app.models.base import BaseModel

class Usuario(BaseModel):
    """Usuários do sistema"""
    __tablename__ = "usuarios"
    
    # Informações básicas
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    
    # Autenticação
    senha_hash = Column(String(255), nullable=False)
    salt = Column(String(50))
    
    # Perfil
    perfil = Column(String(50), default="operador")  # admin, gerente, operador, visualizador
    departamento = Column(String(100))
    cargo = Column(String(100))
    
    # Contato
    telefone = Column(String(20))
    celular = Column(String(20))
    
    # Status
    ativo = Column(Boolean, default=True)
    email_verificado = Column(Boolean, default=False)
    primeiro_acesso = Column(Boolean, default=True)
    
    # Controle de sessão
    ultimo_login = Column(DateTime(timezone=True))
    tentativas_login = Column(Integer, default=0)
    bloqueado_ate = Column(DateTime(timezone=True))
    
    # Configurações pessoais
    configuracoes = Column(JSON)  # Preferências do usuário
    
    # Permissões específicas
    permissoes = Column(JSON)  # Permissões customizadas
    
    __table_args__ = (
        Index('idx_usuario_email', 'email'),
        Index('idx_usuario_username', 'username'),
        Index('idx_usuario_perfil_ativo', 'perfil', 'ativo'),
    )
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, username='{self.username}', perfil='{self.perfil}')>"
    
    @property
    def nome_display(self):
        """Nome para exibição"""
        return self.nome.split()[0] if self.nome else self.username
    
    def pode_acessar(self, recurso):
        """Verificar se usuário pode acessar recurso"""
        if self.perfil == "admin":
            return True
        
        # Lógica de permissões baseada no perfil
        permissoes_perfil = {
            "gerente": ["produtos", "estoque", "fornecedores", "relatorios", "inventarios"],
            "operador": ["produtos", "estoque", "movimentacoes"],
            "visualizador": ["produtos", "relatorios"]
        }
        
        return recurso in permissoes_perfil.get(self.perfil, [])


