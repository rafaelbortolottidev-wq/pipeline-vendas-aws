"""
O QUE: Verificar valores numéricos de itens e pagamentos.
POR QUÊ: Identificar valores inválidos, negativos ou zerados.
"""

from pathlib import Path

import pandas as pd


def main():
    pasta = Path(__file__).resolve().parent.parent / "data" / "raw"

    campos = {
        "olist_order_items_dataset.csv": ["price", "freight_value"],
        "olist_order_payments_dataset.csv": ["payment_value"],
    }

    for arquivo, colunas in campos.items():
        df = pd.read_csv(pasta / arquivo, dtype="string")
        print(f"\nArquivo: {arquivo}")

        for coluna in colunas:
            valores = pd.to_numeric(df[coluna], errors="coerce")
            invalidos = (df[coluna].notna() & valores.isna()).sum()

            print(
                f"{coluna}: "
                f"ausentes={df[coluna].isna().sum()} | "
                f"invalidos={invalidos} | "
                f"negativos={(valores < 0).sum()} | "
                f"zeros={(valores == 0).sum()}"
            )
            print(
                f"Minimo: {valores.min():.2f} | "
                f"Maximo: {valores.max():.2f}"
            )


if __name__ == "__main__":
    main()