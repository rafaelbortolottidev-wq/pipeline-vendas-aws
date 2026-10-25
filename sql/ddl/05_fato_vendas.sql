-- O QUE: Definir a tabela fato de vendas do Data Warehouse.
-- POR QUÊ: Analisar valores dos itens por cliente, produto, vendedor e data.

CREATE TABLE IF NOT EXISTS dw.fato_vendas (
    order_id          VARCHAR(32)    NOT NULL,
    order_item_id     INTEGER        NOT NULL,
    cliente_sk        BIGINT         NOT NULL,
    produto_sk        BIGINT         NOT NULL,
    vendedor_sk       BIGINT         NOT NULL,
    data_compra_sk    INTEGER        NOT NULL,
    status_pedido     VARCHAR(20)    NOT NULL,
    quantidade        INTEGER        NOT NULL,
    valor_item        DECIMAL(12,2)  NOT NULL,
    valor_frete       DECIMAL(12,2)  NOT NULL
);