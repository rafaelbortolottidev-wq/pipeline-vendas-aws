-- O QUE: Definir a dimensão de produtos do Data Warehouse.
-- POR QUÊ: Permitir analisar vendas por produto e categoria.

CREATE TABLE IF NOT EXISTS dw.dim_produto (
    produto_sk          BIGINT        NOT NULL,
    product_id          VARCHAR(32)   NOT NULL,
    categoria           VARCHAR(256),
    peso_g              DECIMAL(12,2),
    comprimento_cm      DECIMAL(12,2),
    altura_cm           DECIMAL(12,2),
    largura_cm          DECIMAL(12,2)
);