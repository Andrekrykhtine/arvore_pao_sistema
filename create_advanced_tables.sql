-- Tabela de Fornecedores
CREATE TABLE IF NOT EXISTS fornecedores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    razao_social VARCHAR(150),
    cnpj VARCHAR(14) UNIQUE,
    tipo VARCHAR(20) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100),
    contato_responsavel VARCHAR(100),
    endereco VARCHAR(200),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    cep VARCHAR(8),
    prazo_entrega_dias INTEGER,
    condicoes_pagamento VARCHAR(200),
    status VARCHAR(20) DEFAULT 'ativo',
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Ingredientes
CREATE TABLE IF NOT EXISTS ingredientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    descricao TEXT,
    calorias_100g DECIMAL(8,2),
    proteinas_100g DECIMAL(8,2),
    carboidratos_100g DECIMAL(8,2),
    gorduras_100g DECIMAL(8,2),
    unidade_compra VARCHAR(10) NOT NULL,
    preco_medio DECIMAL(10,2),
    fornecedor_principal_id INTEGER REFERENCES fornecedores(id),
    estoque_atual DECIMAL(12,3) DEFAULT 0,
    estoque_minimo DECIMAL(12,3) DEFAULT 0,
    estoque_maximo DECIMAL(12,3),
    dias_validade_padrao INTEGER,
    contem_gluten BOOLEAN DEFAULT FALSE,
    contem_lactose BOOLEAN DEFAULT FALSE,
    vegano BOOLEAN DEFAULT TRUE,
    alergenos TEXT[], -- Array de strings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Lotes
CREATE TABLE IF NOT EXISTS lotes (
    id SERIAL PRIMARY KEY,
    numero_lote VARCHAR(50) NOT NULL,
    ingrediente_id INTEGER NOT NULL REFERENCES ingredientes(id),
    fornecedor_id INTEGER NOT NULL REFERENCES fornecedores(id),
    quantidade DECIMAL(12,3) NOT NULL,
    quantidade_disponivel DECIMAL(12,3) NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL,
    data_fabricacao DATE,
    data_validade DATE NOT NULL,
    data_recebimento DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'ativo',
    aprovado_qualidade BOOLEAN DEFAULT TRUE,
    observacoes_qualidade TEXT,
    numero_nota_fiscal VARCHAR(50),
    lote_fornecedor VARCHAR(50),
    certificacoes TEXT[], -- Array de strings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(numero_lote, fornecedor_id)
);

-- Tabela de Receitas
CREATE TABLE IF NOT EXISTS receitas (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER NOT NULL REFERENCES produtos(id),
    nome_receita VARCHAR(100) NOT NULL,
    versao VARCHAR(10) DEFAULT '1.0',
    rendimento DECIMAL(10,3) NOT NULL,
    tempo_preparo_minutos INTEGER,
    custo_total DECIMAL(10,2),
    custo_por_unidade DECIMAL(10,2),
    calorias_totais DECIMAL(10,2),
    ativa BOOLEAN DEFAULT TRUE,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Composição (Ingredientes por Receita)
CREATE TABLE IF NOT EXISTS receita_ingredientes (
    id SERIAL PRIMARY KEY,
    receita_id INTEGER NOT NULL REFERENCES receitas(id) ON DELETE CASCADE,
    ingrediente_id INTEGER NOT NULL REFERENCES ingredientes(id),
    quantidade DECIMAL(12,3) NOT NULL,
    unidade VARCHAR(10) NOT NULL,
    percentual DECIMAL(5,2),
    custo_unitario DECIMAL(10,2),
    observacoes VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_fornecedores_tipo ON fornecedores(tipo);
CREATE INDEX IF NOT EXISTS idx_fornecedores_status ON fornecedores(status);
CREATE INDEX IF NOT EXISTS idx_ingredientes_tipo ON ingredientes(tipo);
CREATE INDEX IF NOT EXISTS idx_ingredientes_fornecedor ON ingredientes(fornecedor_principal_id);
CREATE INDEX IF NOT EXISTS idx_lotes_ingrediente ON lotes(ingrediente_id);
CREATE INDEX IF NOT EXISTS idx_lotes_fornecedor ON lotes(fornecedor_id);
CREATE INDEX IF NOT EXISTS idx_lotes_validade ON lotes(data_validade);
CREATE INDEX IF NOT EXISTS idx_lotes_status ON lotes(status);
CREATE INDEX IF NOT EXISTS idx_receitas_produto ON receitas(produto_id);
CREATE INDEX IF NOT EXISTS idx_receita_ingredientes_receita ON receita_ingredientes(receita_id);
CREATE INDEX IF NOT EXISTS idx_receita_ingredientes_ingrediente ON receita_ingredientes(ingrediente_id);

-- Triggers para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_fornecedores_updated_at BEFORE UPDATE ON fornecedores FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ingredientes_updated_at BEFORE UPDATE ON ingredientes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_lotes_updated_at BEFORE UPDATE ON lotes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_receitas_updated_at BEFORE UPDATE ON receitas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
