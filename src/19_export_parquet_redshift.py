"""
O QUE: Exportar as seis tabelas do Data Warehouse para Parquet.
POR QUÊ: Preparar os dados para carga no Amazon Redshift via S3.
"""

from pathlib import Path
import duckdb

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "warehouse" / "vendas.duckdb"
EXPORT_DIR = BASE_DIR / "data" / "redshift_export"

TABELAS = {
    "dim_cliente": 99441,
    "dim_produto": 32951,
    "dim_vendedor": 3095,
    "dim_tempo": 1096,
    "fato_vendas": 112650,
    "fato_pagamentos": 103886,
}


def main():
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        for tabela, esperado in TABELAS.items():
            schemas = con.execute(
                """
                SELECT table_schema
                FROM information_schema.tables
                WHERE table_name = ?
                  AND table_type = 'BASE TABLE'
                """,
                [tabela],
            ).fetchall()

            if len(schemas) != 1:
                raise ValueError(
                    f"Tabela {tabela}: esperado um único schema, "
                    f"encontrados {len(schemas)}"
                )

            origem = f'"{schemas[0][0]}"."{tabela}"'
            total = con.execute(
                f"SELECT COUNT(*) FROM {origem}"
            ).fetchone()[0]

            if total != esperado:
                raise ValueError(
                    f"{tabela}: esperado {esperado}, encontrado {total}"
                )

            destino = EXPORT_DIR / f"{tabela}.parquet"
            caminho = destino.as_posix().replace("'", "''")

            con.execute(
                f"COPY (SELECT * FROM {origem}) "
                f"TO '{caminho}' "
                "(FORMAT PARQUET, COMPRESSION SNAPPY)"
            )

            print(f"OK | {tabela}: {total:,} registros")


if __name__ == "__main__":
    main()