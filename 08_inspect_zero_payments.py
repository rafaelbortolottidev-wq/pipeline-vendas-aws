"""
O QUE: Inspecionar pagamentos zerados e o status dos pedidos.
POR QUÊ: Entender esses casos antes de definir regras de qualidade.
"""

from pathlib import Path

import pandas as pd


def main():
    pasta = Path(__file__).resolve().parent / "data" / "raw"

    pagamentos = pd.read_csv(
        pasta / "olist_order_payments_dataset.csv", dtype="string"
    )
    pedidos = pd.read_csv(
        pasta / "olist_orders_dataset.csv", dtype="string"
    )

    valores = pd.to_numeric(pagamentos["payment_value"], errors="raise")
    zerados = pagamentos.loc[valores.eq(0)]

    resultado = zerados.merge(
        pedidos[["order_id", "order_status"]],
        on="order_id",
        how="left",
        validate="many_to_one",
    )

    print(resultado.to_string(index=False))

    pagamentos["valor"] = valores

    totais = (
        pagamentos.groupby("order_id")["valor"]
        .agg(["size", "sum"])
        .rename(columns={
            "size": "quantidade_pagamentos",
            "sum": "total_pago",
        })
    )

    ids = zerados["order_id"].unique()

    print("\nTOTAL DOS PEDIDOS COM ALGUM PAGAMENTO ZERO")
    print(totais.loc[ids].to_string())


if __name__ == "__main__":
    main()