"""
O QUE: Baixar o dataset Olist e copiar seus CSVs para data/raw.
POR QUÊ: Manter os dados originais organizados para o profiling.
"""

from pathlib import Path
import shutil

import kagglehub


def main():
    origem = Path(
        kagglehub.dataset_download("olistbr/brazilian-ecommerce")
    )
    destino = Path(__file__).resolve().parent.parent / "data" / "raw"
    destino.mkdir(parents=True, exist_ok=True)

    arquivos = sorted(origem.rglob("*.csv"))
    if not arquivos:
        raise RuntimeError("Nenhum CSV encontrado no download.")

    for arquivo in arquivos:
        shutil.copy2(arquivo, destino / arquivo.name)
        print(f"Copiado: {arquivo.name}")

    print(f"\nTotal: {len(arquivos)} CSVs")
    print(f"Destino: {destino}")


if __name__ == "__main__":
    main()