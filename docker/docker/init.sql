-- docker/init.sql
-- Script de inicialização do banco de dados

-- Criar extensões se necessário
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criar schema de auditoria
CREATE SCHEMA IF NOT EXISTS audit;

-- Função para timestamps automáticos
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Log inicial
INSERT INTO pg_stat_statements_reset();
