"""
O QUE: Carregar os pagamentos dos pedidos no Data Warehouse.
POR QUÊ: Analisar pagamentos separadamente dos itens, evitando
multiplicar valores ao relacionar as duas tabelas.
"""

from pathlib import Path

import duckdb
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
DB_PATH = BASE_DIR / "data" / "warehouse" / "vendas.duckdb"


def validar_chave(dados, colunas):
    if dados[colunas].isna().any().any():
        raise ValueError(f"Chave ausente: {colunas}")

    if dados.duplicated(subset=colunas).any():
        raise ValueError(f"Chave duplicada: {colunas}")


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError("Execute primeiro o script 10_create_dw.py.")

    pagamentos = pd.read_csv(
        RAW_DIR / "olist_order_payments_dataset.csv", dtype="string"
    )
    pedidos = pd.read_csv(
        RAW_DIR / "olist_orders_dataset.csv", dtype="string"
    )

    for coluna in ["payment_sequential", "payment_installments"]:
        pagamentos[coluna] = pd.to_numeric(
            pagamentos[coluna], errors="raise"
        ).astype("Int64")

    validar_chave(pagamentos, ["order_id", "payment_sequential"])
    validar_chave(pedidos, ["order_id"])

    datas = pd.to_datetime(
        pedidos["order_purchase_timestamp"],
        format="%Y-%m-%d %H:%M:%S",
        errors="raise",
    )

    if datas.isna().any():
        raise ValueError("Existem datas de compra ausentes.")

    pedidos["data_compra_sk"] = datas.dt.strftime("%Y%m%d").astype("int64")

    conexao = duckdb.connect(str(DB_PATH))

    try:
        conexao.register("pagamentos_origem", pagamentos)
        conexao.register("pedidos_origem", pedidos)
        conexao.execute("BEGIN TRANSACTION")

        conexao.execute("""
            CREATE TEMP TABLE pagamentos_preparados AS
            SELECT
                p.order_id,
                p.payment_sequential,
                c.cliente_sk,
                t.tempo_sk AS data_compra_sk,
                p.payment_type AS tipo_pagamento,
                p.payment_installments AS numero_parcelas,
                CAST(p.payment_value AS DECIMAL(12,2)) AS valor_pagamento
            FROM pagamentos_origem AS p
            LEFT JOIN pedidos_origem AS o
                ON p.order_id = o.order_id
            LEFT JOIN dw.dim_cliente AS c
                ON o.customer_id = c.customer_id
            LEFT JOIN dw.dim_tempo AS t
                ON o.data_compra_sk = t.tempo_sk
        """)

        quantidade = conexao.execute(
            "SELECT COUNT(*) FROM pagamentos_preparados"
        ).fetchone()[0][0]

        if quantidade != len(pagamentos):
            raise ValueError("Os relacionamentos multiplicaram os pagamentos.")

        invalidos = conexao.execute("""
            SELECT COUNT(*)
            FROM pagamentos_preparados
            WHERE cliente_sk IS NULL
               OR data_compra_sk IS NULL
               OR tipo_pagamento IS NULL
               OR numero_parcelas IS NULL
               OR numero_parcelas < 0
               OR valor_pagamento IS NULL
               OR valor_pagamento < 0
               OR payment_sequential < 1
        """).fetchone()[0][0]

        if invalidos:
            raise ValueError(
                f"{invalidos} pagamentos com dimensão ausente ou valores inválidos."
            )

        antes = conexao.execute(
            "SELECT COUNT(*) FROM dw.fato_pagamentos"
        ).fetchone()[0][0]

        conexao.execute("""
            INSERT INTO dw.fato_pagamentos (
                order_id, payment_sequential, cliente_sk,
                data_compra_sk, tipo_pagamento,
                numero_parcelas, valor_pagamento
            )
            SELECT
                p.order_id, p.payment_sequential, p.cliente_sk,
                p.data_compra_sk, p.tipo_pagamento,
                p.numero_parcelas, p.valor_pagamento
            FROM pagamentos_preparados AS p
            WHERE NOT EXISTS (
                SELECT 1
                FROM dw.fato_pagamentos AS f
                WHERE f.order_id = p.order_id
                  AND f.payment_sequential = p.payment_sequential
            )
        """)

        depois = conexao.execute(
            "SELECT COUNT(*) FROM dw.fato_pagamentos"
        ).fetchone()[0][0]

        conexao.execute("COMMIT")

        print(f"Pagamentos na origem: {len(pagamentos):,}")
        print(f"Pagamentos inseridos: {depois - antes:,}")
        print(f"Total na fato: {depois:,}")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()