#!/bin/bash

echo "=== 🔧 CONFIGURAÇÃO ADICIONAL DO N8N ==="

# Criar arquivo de configuração customizada
cat > n8n_data/config.json << 'CONFIG'
{
  "executions": {
    "mode": "regular",
    "timeout": 900,
    "maxTimeout": 3600,
    "saveDataOnError": "all",
    "saveDataOnSuccess": "all"
  },
  "security": {
    "authCookie": {
      "secure": false
    }
  },
  "endpoints": {
    "rest": "rest",
    "webhook": "webhook",
    "webhookWaiting": "webhook-waiting"
  }
}
CONFIG

echo "✅ Configurações adicionais aplicadas!"
echo "🔄 Reiniciando N8N para aplicar configurações..."

# Reiniciar para aplicar configurações
docker-compose restart n8n

echo "✅ N8N configurado e pronto para uso!"
