-- O QUE: Definir a dimensão de clientes do Data Warehouse.
-- POR QUÊ: Relacionar vendas ao cadastro e permitir analisar recorrência.

CREATE SCHEMA IF NOT EXISTS dw;

CREATE TABLE IF NOT EXISTS dw.dim_cliente (
    cliente_sk          BIGINT       NOT NULL,
    customer_id         VARCHAR(32)  NOT NULL,
    customer_unique_id  VARCHAR(32)  NOT NULL,
    cep_prefixo         VARCHAR(5),
    cidade              VARCHAR(256),
    estado              VARCHAR(2)
);