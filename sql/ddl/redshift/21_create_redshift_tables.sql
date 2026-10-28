-- Projeto 03 - Data Warehouse Olist AWS
-- O QUE: Criar o schema e as seis tabelas dimensionais.
-- POR QUE: Estruturar o Data Warehouse no Amazon Redshift.

CREATE SCHEMA IF NOT EXISTS dw;

CREATE TABLE IF NOT EXISTS dw.dim_cliente (
    cliente_sk BIGINT NOT NULL,
    customer_id VARCHAR(32) NOT NULL,
    customer_unique_id VARCHAR(32) NOT NULL,
    cep_prefixo VARCHAR(5),
    cidade VARCHAR(256),
    estado VARCHAR(2)
);

CREATE TABLE IF NOT EXISTS dw.dim_produto (
    produto_sk BIGINT NOT NULL,
    product_id VARCHAR(32) NOT NULL,
    categoria VARCHAR(256),
    peso_g DECIMAL(12,2),
    comprimento_cm DECIMAL(12,2),
    altura_cm DECIMAL(12,2),
    largura_cm DECIMAL(12,2)
);

CREATE TABLE IF NOT EXISTS dw.dim_vendedor (
    vendedor_sk BIGINT NOT NULL,
    seller_id VARCHAR(32) NOT NULL,
    cep_prefixo VARCHAR(5),
    cidade VARCHAR(256),
    estado VARCHAR(2)
);

CREATE TABLE IF NOT EXISTS dw.dim_tempo (
    tempo_sk INTEGER NOT NULL,
    data DATE NOT NULL,
    ano SMALLINT NOT NULL,
    trimestre SMALLINT NOT NULL,
    mes SMALLINT NOT NULL,
    dia SMALLINT NOT NULL,
    dia_semana SMALLINT NOT NULL,
    fim_de_semana BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dw.fato_vendas (
    order_id VARCHAR(32) NOT NULL,
    order_item_id INTEGER NOT NULL,
    cliente_sk BIGINT NOT NULL,
    produto_sk BIGINT NOT NULL,
    vendedor_sk BIGINT NOT NULL,
    data_compra_sk INTEGER NOT NULL,
    status_pedido VARCHAR(20) NOT NULL,
    quantidade INTEGER NOT NULL,
    valor_item DECIMAL(12,2) NOT NULL,
    valor_frete DECIMAL(12,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS dw.fato_pagamentos (
    order_id VARCHAR(32) NOT NULL,
    payment_sequential INTEGER NOT NULL,
    cliente_sk BIGINT NOT NULL,
    data_compra_sk INTEGER NOT NULL,
    tipo_pagamento VARCHAR(30) NOT NULL,
    numero_parcelas INTEGER NOT NULL,
    valor_pagamento DECIMAL(12,2) NOT NULL
);