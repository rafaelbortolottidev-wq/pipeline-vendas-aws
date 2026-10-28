"""
O QUE: Carregar os itens dos pedidos na fato de vendas.
POR QUÊ: Relacionar valores, clientes, produtos, vendedores e datas
sem duplicar itens nem perder registros por falta de dimensão.
"""

from pathlib import Path

import duckdb
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
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

    itens = pd.read_csv(
        RAW_DIR / "olist_order_items_dataset.csv", dtype="string"
    )
    pedidos = pd.read_csv(
        RAW_DIR / "olist_orders_dataset.csv", dtype="string"
    )

    itens["order_item_id"] = pd.to_numeric(
        itens["order_item_id"], errors="raise"
    ).astype("Int64")

    validar_chave(itens, ["order_id", "order_item_id"])
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
        conexao.register("itens_origem", itens)
        conexao.register("pedidos_origem", pedidos)
        conexao.execute("BEGIN TRANSACTION")

        conexao.execute("""
            CREATE TEMP TABLE vendas_preparadas AS
            SELECT
                i.order_id,
                i.order_item_id,
                c.cliente_sk,
                p.produto_sk,
                v.vendedor_sk,
                t.tempo_sk AS data_compra_sk,
                o.order_status AS status_pedido,
                1 AS quantidade,
                CAST(i.price AS DECIMAL(12,2)) AS valor_item,
                CAST(i.freight_value AS DECIMAL(12,2)) AS valor_frete
            FROM itens_origem AS i
            LEFT JOIN pedidos_origem AS o
                ON i.order_id = o.order_id
            LEFT JOIN dw.dim_cliente AS c
                ON o.customer_id = c.customer_id
            LEFT JOIN dw.dim_produto AS p
                ON i.product_id = p.product_id
            LEFT JOIN dw.dim_vendedor AS v
                ON i.seller_id = v.seller_id
            LEFT JOIN dw.dim_tempo AS t
                ON o.data_compra_sk = t.tempo_sk
        """)

        quantidade = conexao.execute(
            "SELECT COUNT(*) FROM vendas_preparadas"
        ).fetchone()[0]

        if quantidade != len(itens):
            raise ValueError("Os relacionamentos multiplicaram os itens.")

        invalidos = conexao.execute("""
            SELECT COUNT(*)
            FROM vendas_preparadas
            WHERE cliente_sk IS NULL
               OR produto_sk IS NULL
               OR vendedor_sk IS NULL
               OR data_compra_sk IS NULL
               OR status_pedido IS NULL
               OR valor_item IS NULL
               OR valor_frete IS NULL
               OR valor_item < 0
               OR valor_frete < 0
        """).fetchone()[0]

        if invalidos:
            raise ValueError(
                f"{invalidos} itens com dimensão ausente ou valores inválidos."
            )

        antes = conexao.execute(
            "SELECT COUNT(*) FROM dw.fato_vendas"
        ).fetchone()[0]

        conexao.execute("""
            INSERT INTO dw.fato_vendas (
                order_id, order_item_id, cliente_sk, produto_sk,
                vendedor_sk, data_compra_sk, status_pedido,
                quantidade, valor_item, valor_frete
            )
            SELECT
                s.order_id, s.order_item_id, s.cliente_sk, s.produto_sk,
                s.vendedor_sk, s.data_compra_sk, s.status_pedido,
                s.quantidade, s.valor_item, s.valor_frete
            FROM vendas_preparadas AS s
            WHERE NOT EXISTS (
                SELECT 1
                FROM dw.fato_vendas AS f
                WHERE f.order_id = s.order_id
                  AND f.order_item_id = s.order_item_id
            )
        """)

        depois = conexao.execute(
            "SELECT COUNT(*) FROM dw.fato_vendas"
        ).fetchone()[0]

        conexao.execute("COMMIT")

        print(f"Itens na origem: {len(itens):,}")
        print(f"Itens inseridos: {depois - antes:,}")
        print(f"Total na fato: {depois:,}")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()