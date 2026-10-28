"""
O QUE: Criar as tabelas do Data Warehouse no DuckDB.
POR QUÊ: Executar e validar a estrutura SQL localmente antes da etapa AWS.
"""

from pathlib import Path

import duckdb


BASE_DIR = Path(__file__).resolve().parent
DDL_DIR = BASE_DIR / "sql" / "ddl"
DB_PATH = BASE_DIR / "data" / "warehouse" / "vendas.duckdb"

DDL_FILES = [
    "01_dim_cliente.sql",
    "02_dim_produto.sql",
    "03_dim_vendedor.sql",
    "04_dim_tempo.sql",
    "05_fato_vendas.sql",
    "06_fato_pagamentos.sql",
]


def main():
    # Confere todos os arquivos antes de alterar o banco.
    scripts = []
    for nome in DDL_FILES:
        caminho = DDL_DIR / nome
        scripts.append((nome, caminho.read_text(encoding="utf-8-sig")))

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conexao = duckdb.connect(str(DB_PATH))

    try:
        conexao.execute("BEGIN TRANSACTION")

        for nome, sql in scripts:
            conexao.execute(sql)
            print(f"SQL executado: {nome}")

        conexao.execute("COMMIT")

        tabelas = conexao.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'dw'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """).fetchall()

        print(f"\nBanco: {DB_PATH}")
        print(f"Tabelas no schema dw: {len(tabelas)}")

        for (nome,) in tabelas:
            print(f"  - {nome}")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()
    