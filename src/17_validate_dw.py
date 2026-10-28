"""
O QUE: Validar contagens, chaves, relacionamentos e totais do DW.
POR QUÊ: Detectar perdas, duplicações e diferenças de valores após a carga.
"""

from pathlib import Path

import duckdb
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "warehouse" / "vendas.duckdb"
RAW_DIR = BASE_DIR / "data" / "raw"

# Contagens esperadas para a versão do dataset que inspecionamos.
TABELAS = {
    "dim_cliente": (99441, ["cliente_sk"], ["customer_id"]),
    "dim_produto": (32951, ["produto_sk"], ["product_id"]),
    "dim_vendedor": (3095, ["vendedor_sk"], ["seller_id"]),
    "dim_tempo": (1096, ["tempo_sk"], ["data"]),
    "fato_vendas": (112650, ["order_id", "order_item_id"], None),
    "fato_pagamentos": (103886, ["order_id", "payment_sequential"], None),
}

RELACIONAMENTOS = [
    ("fato_vendas", "cliente_sk", "dim_cliente", "cliente_sk"),
    ("fato_vendas", "produto_sk", "dim_produto", "produto_sk"),
    ("fato_vendas", "vendedor_sk", "dim_vendedor", "vendedor_sk"),
    ("fato_vendas", "data_compra_sk", "dim_tempo", "tempo_sk"),
    ("fato_pagamentos", "cliente_sk", "dim_cliente", "cliente_sk"),
    ("fato_pagamentos", "data_compra_sk", "dim_tempo", "tempo_sk"),
]


def main():
    falhas = []

    def verificar(nome, obtido, esperado):
        passou = obtido == esperado
        print(f"{'OK' if passou else 'FALHA'} | {nome}")
        if not passou:
            falhas.append(nome)
            print(f"  Obtido: {obtido} | Esperado: {esperado}")

    conexao = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        for tabela, (esperado, chave, alternativa) in TABELAS.items():
            total = conexao.execute(
                f"SELECT COUNT(*) FROM dw.{tabela}"
            ).fetchall()[0][0]

            verificar(f"{tabela}: {total:,} registros", total, esperado)

            for colunas in [chave, alternativa]:
                if colunas is None:
                    continue

                campos = ", ".join(colunas)
                nulos = " OR ".join(f"{c} IS NULL" for c in colunas)

                problemas = conexao.execute(f"""
                    SELECT COUNT(*) FROM (
                        SELECT {campos}
                        FROM dw.{tabela}
                        GROUP BY {campos}
                        HAVING COUNT(*) > 1 OR {nulos}
                    ) AS erros
                """).fetchall()[0][0]

                verificar(f"{tabela}: chave {campos}", problemas, 0)

        for fato, fk, dimensao, pk in RELACIONAMENTOS:
            orfaos = conexao.execute(f"""
                SELECT COUNT(*)
                FROM dw.{fato} AS f
                LEFT JOIN dw.{dimensao} AS d ON f.{fk} = d.{pk}
                WHERE d.{pk} IS NULL
            """).fetchall()[0][0]

            verificar(f"{fato}.{fk}: relacionamento", orfaos, 0)

        itens = pd.read_csv(
            RAW_DIR / "olist_order_items_dataset.csv", dtype="string"
        )
        pagamentos = pd.read_csv(
            RAW_DIR / "olist_order_payments_dataset.csv", dtype="string"
        )

        conexao.register("itens_origem", itens)
        conexao.register("pagamentos_origem", pagamentos)

        medidas = [
            ("valor_item", "fato_vendas", "price", "itens_origem"),
            ("valor_frete", "fato_vendas", "freight_value", "itens_origem"),
            (
                "valor_pagamento", "fato_pagamentos",
                "payment_value", "pagamentos_origem"
            ),
        ]

        for destino, tabela, origem, fonte in medidas:
            total_dw = conexao.execute(
                f"SELECT SUM({destino}) FROM dw.{tabela}"
            ).fetchall()[0][0]

            total_csv = conexao.execute(
                f"SELECT SUM(CAST({origem} AS DECIMAL(12,2))) FROM {fonte}"
            ).fetchall()[0][0]

            verificar(
                f"{tabela}.{destino}: total {total_dw}",
                total_dw,
                total_csv,
            )

        quantidade_invalida = conexao.execute("""
            SELECT COUNT(*) FROM dw.fato_vendas
            WHERE quantidade IS NULL OR quantidade <> 1
        """).fetchall()[0][0]

        verificar("Quantidade igual a 1 por item", quantidade_invalida, 0)

    finally:
        conexao.close()

    if falhas:
        raise RuntimeError(f"Validação reprovada: {len(falhas)} falhas.")

    print("\nTodas as verificações executadas foram aprovadas.")


if __name__ == "__main__":
    main()