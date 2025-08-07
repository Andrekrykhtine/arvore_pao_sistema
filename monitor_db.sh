#!/bin/bash
echo "=== 📊 MONITORAMENTO DATABASE - $(date) ==="

echo "1. 🔗 Status da Conexão:"
curl -s http://localhost:8000/health | grep -o '"database":"[^\"]*"'

echo -e "\n2. 📈 Estatísticas do PostgreSQL:"
docker-compose exec db psql -U postgres -d arvore_pao -c "
SELECT 
    datname as database,
    numbackends as connections,
    xact_commit as commits,
    xact_rollback as rollbacks,
    blks_read as blocks_read,
    blks_hit as blocks_hit,
    tup_returned as tuples_returned,
    tup_fetched as tuples_fetched
FROM pg_stat_database 
WHERE datname = 'arvore_pao';"

echo -e "\n3. 📋 Tabelas e Tamanhos:"
docker-compose exec db psql -U postgres -d arvore_pao -c "
SELECT 
    table_name,
    pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY pg_total_relation_size(quote_ident(table_name)) DESC;"
