"""
O QUE: Analisar identificadores de clientes e pedidos por cliente.
POR QUÊ: Definir como medir recorrência no modelo dimensional.
"""

from pathlib import Path

import pandas as pd


def main():
    pasta = Path(__file__).resolve().parent.parent / "data" / "raw"

    clientes = pd.read_csv(
        pasta / "olist_customers_dataset.csv", dtype="string"
    )
    pedidos = pd.read_csv(
        pasta / "olist_orders_dataset.csv", dtype="string"
    )

    base = pedidos.merge(
        clientes[["customer_id", "customer_unique_id"]],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    print(f"customer_id distintos: {clientes['customer_id'].nunique()}")
    print(
        "customer_unique_id distintos: "
        f"{clientes['customer_unique_id'].nunique()}"
    )

    for nome, dados in [
        ("Todos os pedidos", base),
        ("Somente entregues", base[base["order_status"].eq("delivered")]),
    ]:
        contagem = dados.groupby("customer_unique_id")["order_id"].nunique()

        print(f"\n{nome}")
        print(f"Clientes: {len(contagem)}")
        print(f"Clientes com mais de um pedido: {(contagem > 1).sum()}")
        print(f"Maior quantidade de pedidos por cliente: {contagem.max()}")


if __name__ == "__main__":
    main()