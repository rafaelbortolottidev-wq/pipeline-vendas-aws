-- O QUE: Definir a dimensão de vendedores do Data Warehouse.
-- POR QUÊ: Permitir analisar vendas por vendedor e localização.

CREATE TABLE IF NOT EXISTS dw.dim_vendedor (
    vendedor_sk     BIGINT        NOT NULL,
    seller_id       VARCHAR(32)   NOT NULL,
    cep_prefixo     VARCHAR(5),
    cidade          VARCHAR(256),
    estado          VARCHAR(2)
);