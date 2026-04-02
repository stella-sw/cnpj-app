import duckdb

con = duckdb.connect("db/cnpj.duckdb")

con.execute("""
CREATE OR REPLACE TABLE empresas AS
SELECT *
FROM read_csv_auto(
    'data/empresas.csv',
    delim=';',
    header=False,
    ignore_errors=true,
    all_varchar=true
);
""")

print("Tabela carregada!")

df = con.execute("SELECT * FROM empresas LIMIT 5").fetchdf()
print(df)

desc = con.execute("DESCRIBE empresas").fetchdf()
print(desc)

con.execute("ALTER TABLE empresas RENAME COLUMN column0 TO cnpj_basico;")
con.execute("ALTER TABLE empresas RENAME COLUMN column1 TO razao_social;")
con.execute("ALTER TABLE empresas RENAME COLUMN column2 TO natureza_juridica;")
con.execute("ALTER TABLE empresas RENAME COLUMN column3 TO qualificacao_responsavel;")
con.execute("ALTER TABLE empresas RENAME COLUMN column4 TO capital_social;")
con.execute("ALTER TABLE empresas RENAME COLUMN column5 TO porte_empresa;")
con.execute("ALTER TABLE empresas RENAME COLUMN column6 TO ente_federativo;")

print("Colunas renomeadas!")