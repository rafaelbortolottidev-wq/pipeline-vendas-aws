-- Projeto 03 - Data Warehouse Olist AWS
-- O QUE: Validar contagens e relacionamentos das tabelas.
-- POR QUE: Garantir a integridade dos dados carregados no Redshift.

-- 1. Contagem das seis tabelas
SELECT 'dim_cliente' AS tabela, COUNT(*) AS registros FROM dw.dim_cliente
UNION ALL
SELECT 'dim_produto', COUNT(*) FROM dw.dim_produto
UNION ALL
SELECT 'dim_vendedor', COUNT(*) FROM dw.dim_vendedor
UNION ALL
SELECT 'dim_tempo', COUNT(*) FROM dw.dim_tempo
UNION ALL
SELECT 'fato_vendas', COUNT(*) FROM dw.fato_vendas
UNION ALL
SELECT 'fato_pagamentos', COUNT(*) FROM dw.fato_pagamentos;


-- 2. Integridade referencial das vendas
SELECT
    COUNT(*) AS total_vendas,
    SUM(CASE WHEN c.cliente_sk IS NULL THEN 1 ELSE 0 END) AS clientes_invalidos,
    SUM(CASE WHEN p.produto_sk IS NULL THEN 1 ELSE 0 END) AS produtos_invalidos,
    SUM(CASE WHEN v.vendedor_sk IS NULL THEN 1 ELSE 0 END) AS vendedores_invalidos,
    SUM(CASE WHEN t.tempo_sk IS NULL THEN 1 ELSE 0 END) AS datas_invalidas
FROM dw.fato_vendas f
LEFT JOIN dw.dim_cliente c ON f.cliente_sk = c.cliente_sk
LEFT JOIN dw.dim_produto p ON f.produto_sk = p.produto_sk
LEFT JOIN dw.dim_vendedor v ON f.vendedor_sk = v.vendedor_sk
LEFT JOIN dw.dim_tempo t ON f.data_compra_sk = t.tempo_sk;


-- 3. Integridade referencial dos pagamentos
SELECT
    COUNT(*) AS total_pagamentos,
    SUM(CASE WHEN c.cliente_sk IS NULL THEN 1 ELSE 0 END) AS clientes_invalidos,
    SUM(CASE WHEN t.tempo_sk IS NULL THEN 1 ELSE 0 END) AS datas_invalidas
FROM dw.fato_pagamentos p
LEFT JOIN dw.dim_cliente c ON p.cliente_sk = c.cliente_sk
LEFT JOIN dw.dim_tempo t ON p.data_compra_sk = t.tempo_sk;