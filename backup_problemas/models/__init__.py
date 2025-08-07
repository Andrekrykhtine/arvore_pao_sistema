# Criar __init__.py simples para os modelos
"""
Modelos do Sistema Árvore Pão
"""

# Importar modelo base primeiro
from .base import BaseModel

# Importar modelos principais
from .produtos import Produto

# Lista de todos os modelos
__all__ = [
    "BaseModel",
    "Produto"
]
