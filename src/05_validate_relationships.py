"""
O QUE: Verificar referências entre as tabelas principais.
POR QUÊ: Identificar registros sem correspondência antes dos joins.
"""

from pathlib import Path

import pandas as pd


def main():
    pasta = Path(__file__).resolve().parent.parent / "data" / "raw"

    nomes = {
        "clientes": "olist_customers_dataset.csv",
        "pedidos": "olist_orders_dataset.csv",
        "itens": "olist_order_items_dataset.csv",
        "produtos": "olist_products_dataset.csv",
        "vendedores": "olist_sellers_dataset.csv",
        "pagamentos": "olist_order_payments_dataset.csv",
    }

    tabelas = {
        nome: pd.read_csv(pasta / arquivo, dtype="string")
        for nome, arquivo in nomes.items()
    }

    relacoes = [
        ("pedidos", "clientes", "customer_id"),
        ("itens", "pedidos", "order_id"),
        ("itens", "produtos", "product_id"),
        ("itens", "vendedores", "seller_id"),
        ("pagamentos", "pedidos", "order_id"),
    ]

    for origem, destino, chave in relacoes:
        referencias = tabelas[origem][chave]
        existentes = tabelas[destino][chave].dropna()

        nulos = referencias.isna().sum()
        orfaos = (
            referencias.notna() & ~referencias.isin(existentes)
        ).sum()

        print(
            f"{origem} -> {destino} ({chave}): "
            f"{nulos} nulos | {orfaos} registros sem correspondencia"
        )


if __name__ == "__main__":
    main()