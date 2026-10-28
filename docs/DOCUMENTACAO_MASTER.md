# Documentação Técnica — Data Warehouse Olist AWS

**Projeto:** P03 — pipeline-vendas-aws  
**Versão:** 1.0  
**Status:** implementação validada; encerramento documental e operacional em andamento.

## 1. Objetivo e arquitetura

Construir um Data Warehouse dimensional para análise de vendas e pagamentos do Olist, com desenvolvimento local e implantação no Amazon Redshift Serverless.

**Kaggle → Python + DuckDB → Parquet → Amazon S3 → Redshift Serverless → SQL**

O ambiente local permite desenvolver as transformações e validar os dados antes da carga na AWS.

## 2. Fonte e processamento local

**Fonte:** [Olist Brazilian E-Commerce Public Dataset — Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

O download foi realizado com `kagglehub`. Os nove arquivos CSV foram inspecionados com Python para verificar estrutura, volumes, duplicidades, valores ausentes e relacionamentos.

**Ambiente:**

- Python 3.11.9.
- Pandas para leitura e preparação dos dados.
- DuckDB para armazenamento e consultas SQL locais.
- Banco local: `data/warehouse/vendas.duckdb`.

**Decisões de tratamento:**

- Preservar categorias e medidas ausentes dos produtos como `NULL`.
- Armazenar prefixos de CEP como texto com cinco dígitos.
- Preservar pagamentos de valor zero identificados na origem.
- Manter os status dos pedidos para aplicação de filtros nas análises.
- Não preencher artificialmente datas de entrega ausentes.

Avaliações e geolocalização foram inspecionadas, mas não integram o modelo dimensional desta versão.

## 3. Modelo dimensional

| Tabela | Granularidade | Registros |
|---|---|---:|
| dim_cliente | Um cadastro por customer_id | 99.441 |
| dim_produto | Um produto | 32.951 |
| dim_vendedor | Um vendedor | 3.095 |
| dim_tempo | Um dia do calendário | 1.096 |
| fato_vendas | Um item de um pedido | 112.650 |
| fato_pagamentos | Um registro de pagamento de um pedido | 103.886 |

### Chaves e relacionamentos

As dimensões de clientes, produtos e vendedores possuem chaves internas:
`cliente_sk`, `produto_sk` e `vendedor_sk`.

Os identificadores originais são preservados para rastreabilidade e relacionamento durante a carga.

- `fato_vendas`: identificada por `order_id` + `order_item_id`.
- `fato_pagamentos`: identificada por `order_id` + `payment_sequential`.
- `dim_tempo`: chave `tempo_sk` no formato `AAAAMMDD`.

A dimensão de clientes mantém dois identificadores:

- `customer_id`: cadastro associado ao pedido.
- `customer_unique_id`: identificação do mesmo cliente em diferentes compras.

Não foi feita deduplicação por `customer_unique_id`, preservando a localização associada a cada cadastro.

### Tempo e medidas

A dimensão tempo contém todos os dias de **01/01/2016 a 31/12/2018**.
O dia da semana segue o padrão de 1 para segunda-feira até 7 para domingo.

Na fato de vendas:

- Cada linha representa uma unidade, com `quantidade = 1`.
- Valor do item e frete são armazenados separadamente.
- O status do pedido é preservado.

Na fato de pagamentos:

- Um pedido pode possuir vários registros de pagamento.
- O número de parcelas é um atributo; não existe uma linha por parcela.
- A data associada é a data da compra, pois a origem não fornece uma data específica do pagamento.

Os valores monetários usam `DECIMAL(12,2)`.

**Vendas e pagamentos não devem ser unidos diretamente por pedido para somar valores.**
Essa junção pode multiplicar registros. Para comparações, agregue cada fato por pedido antes de relacioná-las.

## 4. Organização dos arquivos

| Arquivos | Responsabilidade |
|---|---|
| Scripts 01 a 09 | Download, inspeção, profiling e verificações da origem |
| 10_create_dw.py | Criação das tabelas locais |
| Scripts 11 a 14 | Carga das quatro dimensões |
| 15_load_fato_vendas.py | Carga dos itens dos pedidos |
| 16_load_fato_pagamentos.py | Carga dos pagamentos |
| 17_validate_dw.py | Validação do DW local |
| 18_query_vendas_mensais.py | Consulta analítica mensal |
| 19_export_parquet_redshift.py | Exportação das tabelas para Parquet |
| 20_check_parquet_schema.py | Conferência dos esquemas Parquet |
| sql/ddl/ | Definições SQL das tabelas locais |
| sql/ddl/redshift/ | Criação, carga e validação no Redshift |
| docs/imagens/ | Imagem da arquitetura |
| docs/DOCUMENTACAO_MASTER.md | Documentação técnica |

No PowerShell, execute os scripts a partir da raiz do projeto utilizando o Python do ambiente virtual. Exemplo:

    .\.venv\Scripts\python.exe src\17_validate_dw.py

Com os CSVs disponíveis em `data/raw/`, a construção e a carga local seguem a ordem dos scripts 10 a 16. Depois são executadas a validação, a consulta e a exportação.

### Reprocessamento local

As cargas inserem apenas identificadores ainda ausentes, preservando as chaves existentes.

A repetição da carga de clientes manteve 99.441 registros, com zero novas inserções. A carga de vendedores também manteve 3.095 registros nas execuções repetidas.

Essa proteção não representa uma implementação completa de carga incremental: atualizações cadastrais e mudanças de status dos pedidos não são aplicadas automaticamente.

## 5. Amazon S3 e Redshift Serverless

### Armazenamento no S3

- **Bucket:** `rafael-portfolio-olist-aws`.
- **Região:** `us-east-1`.
- **Prefixo:** `gold/olist/`.
- **Conteúdo:** seis arquivos Parquet, aproximadamente 17,2 MB no total.

O upload foi concluído sem falhas.

### Configuração do Redshift

| Configuração | Valor |
|---|---|
| Região | us-east-1 |
| Namespace | olist-dw-namespace |
| Workgroup | olist-dw-workgroup |
| Banco | dev |
| Schema | dw |
| Capacidade básica | 4 RPUs |
| Limite diário configurado | 4 RPU-horas |

### Sequência de carga

Os scripts estão em `sql/ddl/redshift/` e foram executados pelo Query Editor v2:

1. `21_create_redshift_tables.sql`: criação do schema e das tabelas.
2. `22_load_redshift.sql`: carga dos arquivos Parquet com `COPY`.
3. `23_validate_redshift.sql`: verificação das contagens e dos relacionamentos.

**O COPY utilizado não é idempotente.**
Reexecutá-lo sobre tabelas preenchidas pode duplicar registros. A versão 1.0 não implementa `MERGE` nem recarga automatizada.

## 6. Segurança e IAM

| Identidade ou configuração | Finalidade |
|---|---|
| portfolio-admin | Identidade humana no IAM Identity Center |
| OlistDevAccess | Permission Set utilizado para operar o projeto |
| OlistRedshiftS3Role | Role utilizada pelo Redshift para leitura dos arquivos no S3 |

O acesso humano foi validado pelo portal AWS.

A Role `OlistRedshiftS3Role` possui permissão de leitura dos arquivos do projeto, confiança configurada para Redshift e Redshift Serverless e foi definida como Role padrão do namespace.

O acesso humano e o acesso entre serviços são gerenciados separadamente.

Credenciais, dados brutos, arquivos Parquet e banco DuckDB não são versionados.

## 7. Validações realizadas

### Ambiente local

O script `17_validate_dw.py` aprovou:

- Contagens das seis tabelas.
- Ausência de valores nulos e duplicidades nas chaves verificadas.
- Integridade dos seis relacionamentos entre fatos e dimensões.
- Quantidade igual a 1 em cada item.
- Reconciliação das somas monetárias com os respectivos CSVs.

| Medida — todos os status carregados | Total validado |
|---|---:|
| Valor dos itens | R$ 13.591.643,70 |
| Frete | R$ 2.251.909,54 |
| Pagamentos | R$ 16.008.872,12 |

Cada medida foi comparada com sua própria origem. Não foi adotada como regra a igualdade entre pagamentos e a soma de itens com frete.

### Redshift

As verificações executadas no Query Editor v2 confirmaram:

- Contagens das seis tabelas compatíveis com o ambiente local.
- 112.650 itens sem referências inválidas para clientes, produtos, vendedores e tempo.
- 103.886 pagamentos sem referências inválidas para clientes e tempo.

A reconciliação monetária descrita acima foi executada no ambiente local.

## 8. Consulta analítica

O script `18_query_vendas_mensais.py` foi desenvolvido para analisar pedidos entregues por mês de compra.

| Indicador | Regra |
|---|---|
| Pedidos | Contagem distinta de order_id |
| Itens | Soma de quantidade |
| Valor dos itens | Soma de valor_item, sem frete |
| Ticket médio | Valor dos itens dividido pela quantidade de pedidos |

O filtro utilizado é `status_pedido = 'delivered'`.

O agrupamento considera a data da compra, não a data da entrega. A consulta retorna meses com registros e não preenche automaticamente meses sem vendas.

O valor dos itens não representa lucro nem receita líquida da plataforma.

## 9. Versionamento e limites da versão

O código foi desenvolvido na branch `feature/dw-local` e integrado à `main` pela PR #1.

A revisão documental está na branch `feature/documentacao-final`.

A documentação oficial contém dois arquivos:

- `README.md`: apresentação resumida.
- `docs/DOCUMENTACAO_MASTER.md`: detalhes técnicos.

**Limites da v1.0:**

- Dataset histórico e estático.
- Carga manual no Redshift.
- Sem ingestão incremental automatizada.
- Sem histórico de alterações cadastrais por SCD.
- Sem atualização automática das fatos.
- Power BI fora do escopo.
- Sem testes de desempenho em grande escala.

## 10. Custos e encerramento

Foi configurado um limite diário de 4 RPU-horas com ação de desativar consultas de usuários ao atingir o consumo definido.

**Esse limite não representa um teto absoluto de gastos AWS.**

A implementação e as validações técnicas estão concluídas. Para o encerramento operacional, permanecem:

- Integração da documentação revisada à main.
- Revisão dos custos e dos recursos AWS.
- Registro da decisão de manter ou remover os recursos.
- Consolidação das evidências para apresentação do projeto.

A remoção dos recursos AWS ainda não está confirmada nesta documentação.