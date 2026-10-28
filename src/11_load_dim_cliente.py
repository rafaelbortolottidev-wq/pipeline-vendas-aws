"""
O QUE: Carregar os clientes do Olist na dimensão de clientes.
POR QUÊ: Relacionar as vendas aos clientes com uma chave interna estável.
"""

from pathlib import Path

import duckdb
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "raw" / "olist_customers_dataset.csv"
DB_PATH = BASE_DIR / "data" / "warehouse" / "vendas.duckdb"


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError("Execute primeiro o script 10_create_dw.py.")

    clientes = pd.read_csv(CSV_PATH, dtype="string")

    chaves = ["customer_id", "customer_unique_id"]
    if clientes[chaves].isna().any().any():
        raise ValueError("Existem identificadores de cliente ausentes.")

    if clientes["customer_id"].duplicated().any():
        raise ValueError("Existem customer_id duplicados.")

    clientes["customer_zip_code_prefix"] = (
        clientes["customer_zip_code_prefix"].str.zfill(5)
    )

    conexao = duckdb.connect(str(DB_PATH))

    try:
        conexao.register("clientes_origem", clientes)
        conexao.execute("BEGIN TRANSACTION")

        antes = conexao.execute(
            "SELECT COUNT(*) FROM dw.dim_cliente"
        ).fetchone()[0]

        conexao.execute("""
            INSERT INTO dw.dim_cliente (
                cliente_sk,
                customer_id,
                customer_unique_id,
                cep_prefixo,
                cidade,
                estado
            )
            SELECT
                (SELECT COALESCE(MAX(cliente_sk), 0)
                 FROM dw.dim_cliente)
                    + ROW_NUMBER() OVER (ORDER BY c.customer_id),
                c.customer_id,
                c.customer_unique_id,
                c.customer_zip_code_prefix,
                c.customer_city,
                c.customer_state
            FROM clientes_origem AS c
            WHERE NOT EXISTS (
                SELECT 1
                FROM dw.dim_cliente AS d
                WHERE d.customer_id = c.customer_id
            )
        """)

        depois = conexao.execute(
            "SELECT COUNT(*) FROM dw.dim_cliente"
        ).fetchone()[0]

        conexao.execute("COMMIT")

        print(f"Clientes na origem: {len(clientes):,}")
        print(f"Clientes inseridos: {depois - antes:,}")
        print(f"Total na dimensão: {depois:,}")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()