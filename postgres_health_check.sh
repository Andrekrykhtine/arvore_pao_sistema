#!/bin/bash

echo "=== 🏥 POSTGRESQL HEALTH CHECK COMPLETO ==="

# 1. Verificar uptime do PostgreSQL
echo "1. 📅 Uptime do PostgreSQL:"
docker exec arvore_pao_db psql -h localhost -p 5432 -U postgres -d arvore_pao -c "SELECT current_timestamp - pg_postmaster_start_time() as uptime;"

# 2. Verificar versão
echo -e "\n2. 📋 Versão PostgreSQL:"
docker exec arvore_pao_db psql -h localhost -p 5432 -U postgres -d arvore_pao -c "SELECT version();" | head -3

# 3. Verificar tamanho do database
echo -e "\n3. 💾 Tamanho Database:"
docker exec arvore_pao_db psql -h localhost -p 5432 -U postgres -d arvore_pao -c "SELECT pg_size_pretty(pg_database_size('arvore_pao'));"

# 4. Verificar estatísticas da tabela produtos
echo -e "\n4. 📊 Estatísticas Tabela Produtos:"
docker exec arvore_pao_db psql -h localhost -p 5432 -U postgres -d arvore_pao -c "SELECT schemaname, relname, n_tup_ins, n_tup_upd, n_tup_del FROM pg_stat_user_tables WHERE relname='produtos';"

# 5. Verificar configurações críticas
echo -e "\n5. ⚙️ Configurações Críticas:"
docker exec arvore_pao_db psql -h localhost -p 5432 -U postgres -d arvore_pao -c "SELECT name, setting FROM pg_settings WHERE name IN ('max_connections', 'shared_buffers', 'effective_cache_size');"

# 6. Verificar locks ativos
echo -e "\n6. 🔒 Locks Ativos:"
docker exec arvore_pao_db psql -h localhost -p 5432 -U postgres -d arvore_pao -c "SELECT count(*) as active_locks FROM pg_locks WHERE granted = true;"

echo -e "\n✅ Health Check Completo!"
