"""
O QUE: Verificar nulos e duplicações nas chaves candidatas.
POR QUÊ: Validar como identificar registros antes de unir tabelas.
"""

from pathlib import Path

import pandas as pd


CHAVES = {
    "olist_customers_dataset.csv": ["customer_id"],
    "olist_orders_dataset.csv": ["order_id"],
    "olist_order_items_dataset.csv": ["order_id", "order_item_id"],
    "olist_order_payments_dataset.csv": ["order_id", "payment_sequential"],
    "olist_products_dataset.csv": ["product_id"],
    "olist_sellers_dataset.csv": ["seller_id"],
    "product_category_name_translation.csv": ["product_category_name"],
}


def main():
    pasta = Path(__file__).resolve().parent / "data" / "raw"

    for nome, chave in CHAVES.items():
        df = pd.read_csv(pasta / nome, dtype="string")

        nulos = df[chave].isna().any(axis=1).sum()
        duplicadas = df.duplicated(subset=chave).sum()

        print(f"\nArquivo: {nome}")
        print(f"Chave candidata: {', '.join(chave)}")
        print(f"Linhas com chave nula: {nulos}")
        print(f"Chaves repetidas alem da primeira: {duplicadas}")


if __name__ == "__main__":
    main()