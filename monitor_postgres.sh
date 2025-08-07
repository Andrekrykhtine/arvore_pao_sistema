#!/bin/bash

echo "=== 📊 MONITOR POSTGRESQL CONTÍNUO ==="

while true; do
  echo "$(date) - Verificando PostgreSQL..."
  
  # Teste pg_isready
  if docker exec arvore_pao_db pg_isready -h localhost -p 5432 -U postgres -d arvore_pao > /dev/null 2>&1; then
    echo "✅ PostgreSQL: OK"
  else
    echo "❌ PostgreSQL: FALHA"
    # Enviar alerta aqui se necessário
  fi
  
  # Verificar número de conexões
  CONNECTIONS=$(docker exec arvore_pao_db psql -h localhost -p 5432 -U postgres -d arvore_pao -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null | tr -d ' ')
  echo "🔗 Conexões ativas: $CONNECTIONS"
  
  # Verificar uso de CPU do container PostgreSQL
  CPU_USAGE=$(docker stats arvore_pao_db --no-stream --format "{{.CPUPerc}}" 2>/dev/null)
  echo "💻 CPU PostgreSQL: $CPU_USAGE"
  
  echo "---"
  sleep 30
done
