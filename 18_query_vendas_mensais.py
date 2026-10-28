"""
O QUE: Consultar a evolução mensal do faturamento no Data Warehouse.
POR QUÊ: Analisar receita, quantidade de itens, pedidos e ticket médio.
"""

from pathlib import Path

import duckdb


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "warehouse" / "vendas.duckdb"


def main():
    con = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        query = """
            SELECT
                t.ano,
                t.mes,
                COUNT(DISTINCT f.order_id) AS total_pedidos,
                SUM(f.quantidade) AS total_itens,
                ROUND(SUM(f.valor_item), 2) AS faturamento,
                ROUND(
                    SUM(f.valor_item)
                    / NULLIF(COUNT(DISTINCT f.order_id), 0),
                    2
                ) AS ticket_medio
            FROM dw.fato_vendas f
            INNER JOIN dw.dim_tempo t
                ON f.tempo_sk = t.tempo_sk
            WHERE f.status_pedido = 'delivered'
            GROUP BY
                t.ano,
                t.mes
            ORDER BY
                t.ano,
                t.mes
        """

        resultado = con.execute(query).df()

        print("\nEVOLUÇÃO MENSAL DE VENDAS")
        print(resultado.to_string(index=False))

    finally:
        con.close()


if __name__ == "__main__":
    main()