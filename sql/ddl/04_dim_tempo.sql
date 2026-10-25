-- O QUE: Definir a dimensão de tempo do Data Warehouse.
-- POR QUÊ: Permitir analisar vendas por dia, mês, trimestre e ano.

CREATE TABLE IF NOT EXISTS dw.dim_tempo (
    tempo_sk       INTEGER      NOT NULL,
    data           DATE         NOT NULL,
    ano            SMALLINT     NOT NULL,
    trimestre      SMALLINT     NOT NULL,
    mes            SMALLINT     NOT NULL,
    dia            SMALLINT     NOT NULL,
    dia_semana     SMALLINT     NOT NULL,
    fim_de_semana  BOOLEAN      NOT NULL
);
