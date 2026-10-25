-- O QUE: Definir a tabela fato de pagamentos do Data Warehouse.
-- POR QUÊ: Analisar valores e formas de pagamento sem duplicar os itens vendidos.

CREATE TABLE IF NOT EXISTS dw.fato_pagamentos (
    order_id              VARCHAR(32)    NOT NULL,
    payment_sequential    INTEGER        NOT NULL,
    cliente_sk            BIGINT         NOT NULL,
    data_compra_sk        INTEGER        NOT NULL,
    tipo_pagamento        VARCHAR(30)    NOT NULL,
    numero_parcelas       INTEGER        NOT NULL,
    valor_pagamento       DECIMAL(12,2)  NOT NULL
);