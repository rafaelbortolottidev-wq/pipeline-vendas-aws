"""
O QUE: Carregar os produtos do Olist na dimensão de produtos.
POR QUÊ: Permitir análises por produto e categoria, preservando as chaves.
"""

from pathlib import Path

import duckdb
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "raw" / "olist_products_dataset.csv"
DB_PATH = BASE_DIR / "data" / "warehouse" / "vendas.duckdb"


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError("Execute primeiro o script 10_create_dw.py.")

    produtos = pd.read_csv(CSV_PATH, dtype="string")

    if produtos["product_id"].isna().any():
        raise ValueError("Existem product_id ausentes.")

    if produtos["product_id"].duplicated().any():
        raise ValueError("Existem product_id duplicados.")

    conexao = duckdb.connect(str(DB_PATH))

    try:
        conexao.register("produtos_origem", produtos)
        conexao.execute("BEGIN TRANSACTION")

        antes = conexao.execute(
            "SELECT COUNT(*) FROM dw.dim_produto"
        ).fetchone()[0]

        conexao.execute("""
            INSERT INTO dw.dim_produto (
                produto_sk,
                product_id,
                categoria,
                peso_g,
                comprimento_cm,
                altura_cm,
                largura_cm
            )
            SELECT
                (SELECT COALESCE(MAX(produto_sk), 0)
                 FROM dw.dim_produto)
                    + ROW_NUMBER() OVER (ORDER BY p.product_id),
                p.product_id,
                p.product_category_name,
                CAST(p.product_weight_g AS DECIMAL(12,2)),
                CAST(p.product_length_cm AS DECIMAL(12,2)),
                CAST(p.product_height_cm AS DECIMAL(12,2)),
                CAST(p.product_width_cm AS DECIMAL(12,2))
            FROM produtos_origem AS p
            WHERE NOT EXISTS (
                SELECT 1
                FROM dw.dim_produto AS d
                WHERE d.product_id = p.product_id
            )
        """)

        depois = conexao.execute(
            "SELECT COUNT(*) FROM dw.dim_produto"
        ).fetchone()[0]

        conexao.execute("COMMIT")

        print(f"Produtos na origem: {len(produtos):,}")
        print(f"Produtos inseridos: {depois - antes:,}")
        print(f"Total na dimensão: {depois:,}")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()