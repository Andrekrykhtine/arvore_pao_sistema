# Dockerfile - VERSÃO MELHORADA
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (cache layer)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Criar diretórios necessários
RUN mkdir -p /uploads /temp /logs

# Copiar código da aplicação
COPY ./app /app

# Criar script de health check
RUN echo '#!/bin/bash\ncurl -f http://localhost:8000/health || exit 1' > /healthcheck.sh && \
    chmod +x /healthcheck.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD ["/healthcheck.sh"]

# Criar usuário não-root
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app /uploads /temp /logs

# Trocar para usuário não-root
USER appuser

# Expor porta
EXPOSE 8000

# Comando padrão
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
