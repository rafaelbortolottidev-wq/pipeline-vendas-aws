"""
O QUE: Carregar os vendedores do Olist na dimensão de vendedores.
POR QUÊ: Analisar vendas por vendedor e localização, preservando as chaves.
"""

from pathlib import Path

import duckdb
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "raw" / "olist_sellers_dataset.csv"
DB_PATH = BASE_DIR / "data" / "warehouse" / "vendas.duckdb"


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError("Execute primeiro o script 10_create_dw.py.")

    vendedores = pd.read_csv(CSV_PATH, dtype="string")

    if vendedores["seller_id"].isna().any():
        raise ValueError("Existem seller_id ausentes.")

    if vendedores["seller_id"].duplicated().any():
        raise ValueError("Existem seller_id duplicados.")

    vendedores["seller_zip_code_prefix"] = (
        vendedores["seller_zip_code_prefix"].str.zfill(5)
    )

    conexao = duckdb.connect(str(DB_PATH))

    try:
        conexao.register("vendedores_origem", vendedores)
        conexao.execute("BEGIN TRANSACTION")

        antes = conexao.execute(
            "SELECT COUNT(*) FROM dw.dim_vendedor"
        ).fetchone()[0]

        conexao.execute("""
            INSERT INTO dw.dim_vendedor (
                vendedor_sk,
                seller_id,
                cep_prefixo,
                cidade,
                estado
            )
            SELECT
                (SELECT COALESCE(MAX(vendedor_sk), 0)
                 FROM dw.dim_vendedor)
                    + ROW_NUMBER() OVER (ORDER BY v.seller_id),
                v.seller_id,
                v.seller_zip_code_prefix,
                v.seller_city,
                v.seller_state
            FROM vendedores_origem AS v
            WHERE NOT EXISTS (
                SELECT 1
                FROM dw.dim_vendedor AS d
                WHERE d.seller_id = v.seller_id
            )
        """)

        depois = conexao.execute(
            "SELECT COUNT(*) FROM dw.dim_vendedor"
        ).fetchone()[0]

        conexao.execute("COMMIT")

        print(f"Vendedores na origem: {len(vendedores):,}")
        print(f"Vendedores inseridos: {depois - antes:,}")
        print(f"Total na dimensão: {depois:,}")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()