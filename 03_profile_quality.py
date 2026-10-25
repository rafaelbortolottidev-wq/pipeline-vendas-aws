"""
O QUE: Contar valores ausentes e linhas duplicadas nos CSVs.
POR QUÊ: Identificar pontos de atenção antes das transformações.
"""

from pathlib import Path

import pandas as pd


def main():
    pasta = Path(__file__).resolve().parent / "data" / "raw"
    arquivos = sorted(pasta.glob("*.csv"))

    if not arquivos:
        raise FileNotFoundError(f"Nenhum CSV encontrado em {pasta}")

    for arquivo in arquivos:
        df = pd.read_csv(arquivo, dtype="string")
        nulos = df.isna().sum()
        nulos = nulos[nulos > 0]

        print(f"\nArquivo: {arquivo.name}")
        print(f"Linhas: {len(df):,}")
        print(f"Duplicadas além da primeira: {df.duplicated().sum():,}")
        print("Valores ausentes por coluna:")
        print(nulos.to_string() if not nulos.empty else "Nenhum")


if __name__ == "__main__":
    main()