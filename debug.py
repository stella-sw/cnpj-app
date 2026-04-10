import duckdb

con = duckdb.connect("db/cnpj.duckdb")


print(con.execute("""
SELECT uf_sigla, COUNT(*) AS total
FROM estabelecimentos
GROUP BY uf_sigla
ORDER BY total DESC
""").fetchdf())