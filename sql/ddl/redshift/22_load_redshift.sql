-- Projeto 03 - Data Warehouse Olist AWS
-- O QUE: Carregar as seis tabelas no Amazon Redshift.
-- POR QUE: Transferir os dados Parquet do S3 para o Data Warehouse.

COPY dw.dim_cliente
FROM 's3://rafael-portfolio-olist-aws/gold/olist/dim_cliente.parquet'
IAM_ROLE default
FORMAT AS PARQUET;

COPY dw.dim_produto
FROM 's3://rafael-portfolio-olist-aws/gold/olist/dim_produto.parquet'
IAM_ROLE default
FORMAT AS PARQUET;

COPY dw.dim_vendedor
FROM 's3://rafael-portfolio-olist-aws/gold/olist/dim_vendedor.parquet'
IAM_ROLE default
FORMAT AS PARQUET;

COPY dw.dim_tempo
FROM 's3://rafael-portfolio-olist-aws/gold/olist/dim_tempo.parquet'
IAM_ROLE default
FORMAT AS PARQUET;

COPY dw.fato_vendas
FROM 's3://rafael-portfolio-olist-aws/gold/olist/fato_vendas.parquet'
IAM_ROLE default
FORMAT AS PARQUET;

COPY dw.fato_pagamentos
FROM 's3://rafael-portfolio-olist-aws/gold/olist/fato_pagamentos.parquet'
IAM_ROLE default
FORMAT AS PARQUET;