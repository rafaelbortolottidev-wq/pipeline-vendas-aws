"""
O QUE: Verificar nomes e tipos das colunas dos arquivos Parquet.
POR QUÊ: Validar a estrutura antes da carga no Amazon Redshift.
"""

from pathlib import Path
import duckdb

BASE_DIR = Path(__file__).resolve().parent
EXPORT_DIR = BASE_DIR / "data" / "redshift_export"

for arquivo in sorted(EXPORT_DIR.glob("*.parquet")):
    print(f"\n--- {arquivo.name} ---")

    caminho = arquivo.as_posix().replace("'", "''")

    colunas = duckdb.sql(
        f"DESCRIBE SELECT * FROM read_parquet('{caminho}')"
    ).fetchall()

    for coluna in colunas:
        print(f"{coluna[0]:30} {coluna[1]}")