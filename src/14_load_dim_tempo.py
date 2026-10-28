"""
O QUE: Gerar e carregar o calendário na dimensão tempo.
POR QUÊ: Analisar vendas por dia, mês, trimestre e ano, sem lacunas no calendário.
"""

from pathlib import Path

import duckdb
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "raw" / "olist_orders_dataset.csv"
DB_PATH = BASE_DIR / "data" / "warehouse" / "vendas.duckdb"


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError("Execute primeiro o script 10_create_dw.py.")

    pedidos = pd.read_csv(
        CSV_PATH,
        usecols=["order_purchase_timestamp"],
        dtype="string",
    )

    datas = pd.to_datetime(
        pedidos["order_purchase_timestamp"],
        format="%Y-%m-%d %H:%M:%S",
        errors="raise",
    )

    if datas.empty or datas.isna().any():
        raise ValueError("Datas de compra ausentes ou origem vazia.")

    inicio = pd.Timestamp(year=datas.min().year, month=1, day=1)
    fim = pd.Timestamp(year=datas.max().year, month=12, day=31)

    calendario = pd.DataFrame({
        "data": pd.date_range(inicio, fim, freq="D")
    })

    calendario["tempo_sk"] = calendario["data"].dt.strftime(
        "%Y%m%d"
    ).astype("int64")
    calendario["ano"] = calendario["data"].dt.year
    calendario["trimestre"] = calendario["data"].dt.quarter
    calendario["mes"] = calendario["data"].dt.month
    calendario["dia"] = calendario["data"].dt.day
    calendario["dia_semana"] = calendario["data"].dt.dayofweek + 1
    calendario["fim_de_semana"] = calendario["dia_semana"] >= 6

    conexao = duckdb.connect(str(DB_PATH))

    try:
        conexao.register("calendario_origem", calendario)
        conexao.execute("BEGIN TRANSACTION")

        antes = conexao.execute(
            "SELECT COUNT(*) FROM dw.dim_tempo"
        ).fetchone()[0]

        conexao.execute("""
            INSERT INTO dw.dim_tempo (
                tempo_sk, data, ano, trimestre,
                mes, dia, dia_semana, fim_de_semana
            )
            SELECT
                c.tempo_sk,
                CAST(c.data AS DATE),
                c.ano,
                c.trimestre,
                c.mes,
                c.dia,
                c.dia_semana,
                c.fim_de_semana
            FROM calendario_origem AS c
            WHERE NOT EXISTS (
                SELECT 1
                FROM dw.dim_tempo AS d
                WHERE d.tempo_sk = c.tempo_sk
            )
        """)

        depois = conexao.execute(
            "SELECT COUNT(*) FROM dw.dim_tempo"
        ).fetchone()[0]

        conexao.execute("COMMIT")

        print(f"Calendário gerado: {inicio:%d/%m/%Y} a {fim:%d/%m/%Y}")
        print(f"Dias inseridos: {depois - antes:,}")
        print(f"Total na dimensão: {depois:,}")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()