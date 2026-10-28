"""
O QUE: Inspecionar o volume e as colunas dos CSVs do Olist.
POR QUÊ: Conhecer a estrutura da fonte antes de definir o modelo.
"""

from pathlib import Path

import pandas as pd


def main():
    pasta = Path(__file__).resolve().parent.parent / "data" / "raw"
    arquivos = sorted(pasta.glob("*.csv"))

    if not arquivos:
        raise FileNotFoundError(f"Nenhum CSV encontrado em {pasta}")

    for arquivo in arquivos:
        # Ler como texto preserva IDs e zeros à esquerda dos CEPs.
        df = pd.read_csv(arquivo, dtype="string")

        print(f"\nArquivo: {arquivo.name}")
        print(f"Linhas: {len(df):,} | Colunas: {len(df.columns)}")
        print(f"Campos: {', '.join(df.columns)}")


if __name__ == "__main__":
    main()