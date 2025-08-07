# Criar base.py com imports corretos
from sqlalchemy import Column, Integer, DateTime, String, Boolean
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from app.core.database import Base

class BaseModel(Base):
    """Modelo base com campos de auditoria comum a todas as tabelas"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    @declared_attr
    def created_by(cls):
        return Column(String(100), nullable=True)
    
    @declared_attr  
    def updated_by(cls):
        return Column(String(100), nullable=True)
    
    # Soft delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def soft_delete(self):
        """Soft delete - marcar como deletado sem remover do banco"""
        self.deleted_at = func.now()
        self.is_active = False
    
    def activate(self):
        """Reativar registro"""
        self.deleted_at = None
        self.is_active = True

