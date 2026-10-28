![Arquitetura do Data Warehouse Olist na AWS](docs/imagens/arquitetura-olist.png)

# Data Warehouse Olist — AWS Redshift

Data Warehouse de e-commerce construído com **Python, SQL e Amazon Redshift Serverless**, utilizando dados públicos do Olist.

## Arquitetura

**Kaggle → Python + DuckDB → Parquet → Amazon S3 → Redshift Serverless → SQL**

Os dados foram modelados e validados localmente, exportados em Parquet e carregados no Redshift pelo comando `COPY`.

## Resultados

- **4 dimensões:** clientes, produtos, vendedores e tempo.
- **2 fatos:** 112.650 itens de pedidos e 103.886 registros de pagamento.
- Contagens e integridade referencial validadas no Redshift, sem referências inválidas nas verificações executadas.
- Chaves e totais monetários conferidos no ambiente local.

Vendas e pagamentos ficam em tabelas separadas para evitar a multiplicação de valores nas análises.

## Tecnologias

Python · DuckDB · SQL · Parquet · Amazon S3 · Amazon Redshift Serverless · IAM Identity Center · IAM Roles · Git/GitHub.

## Organização

- Scripts `01_` a `20_`: obtenção dos dados, profiling, cargas, consultas, validação e exportação.
- `sql/ddl/`: definição das tabelas locais.
- `sql/ddl/redshift/`: criação, carga e validação na AWS.
- [Documentação técnica](docs/DOCUMENTACAO_MASTER.md): modelo dimensional, execução, segurança e custos.

Dados brutos, arquivos Parquet, banco DuckDB e credenciais ficam fora do versionamento.

## Status e escopo

**Implementação e validações técnicas concluídas.** Encerramento documental e revisão dos recursos AWS em andamento.

Esta versão utiliza um dataset histórico e carga manual. Ingestão incremental automatizada e Power BI estão fora do escopo.

**Atenção:** repetir `COPY` sobre tabelas já carregadas pode duplicar registros.

## Fonte

[Olist Brazilian E-Commerce Public Dataset — Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)