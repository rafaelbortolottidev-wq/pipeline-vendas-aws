"""
O QUE: Inspecionar status, validade e período das datas dos pedidos.
POR QUÊ: Entender datas ausentes antes de definir regras de negócio.
"""

from pathlib import Path

import pandas as pd


def main():
    arquivo = (
        Path(__file__).resolve().parent.parent
        / "data" / "raw" / "olist_orders_dataset.csv"
    )
    df = pd.read_csv(arquivo, dtype="string")

    print("PEDIDOS POR STATUS")
    print(df["order_status"].value_counts(dropna=False).to_string())

    colunas = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    print("\nVALIDADE DAS DATAS")
    for coluna in colunas:
        datas = pd.to_datetime(
            df[coluna],
            format="%Y-%m-%d %H:%M:%S",
            errors="coerce",
        )
        invalidas = (df[coluna].notna() & datas.isna()).sum()
        print(
            f"{coluna}: {df[coluna].isna().sum()} ausentes"
            f" | {invalidas} invalidas"
        )
        if coluna == "order_purchase_timestamp":
            print(f"Periodo de compras: {datas.min()} ate {datas.max()}")

    print("\nDATAS AUSENTES POR STATUS")
    ausentes = df[colunas].isna()
    print(ausentes.groupby(df["order_status"]).sum().to_string())


if __name__ == "__main__":
    main()