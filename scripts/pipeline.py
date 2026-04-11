import os
import zipfile
import duckdb
import re
import pandas as pd


# =========================
# CONFIG
# =========================
DATA_DIR = "data"
DB_PATH = "db/cnpj.duckdb"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs("db", exist_ok=True)

if len(os.listdir(DATA_DIR)) == 0:
    raise Exception("A pasta data/ está vazia. Adicione os arquivos do CNPJ.")

# =========================
# EXTRAÇÃO
# =========================

def extract_and_rename():
    print("Processando arquivos ZIP...")

    for file in os.listdir(DATA_DIR):
        if not file.endswith(".zip"):
            continue

        zip_path = os.path.join(DATA_DIR, file)

        if not zipfile.is_zipfile(zip_path):
            print(f"Pulando (não é zip válido): {file}")
            continue

        print(f"Extraindo: {file}")

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(DATA_DIR)

    # =========================
    # RENOMEAR AUTOMATICAMENTE
    # =========================

    for f in os.listdir(DATA_DIR):
        name = f.lower()

        if f.endswith(".zip"):
            continue

        old_path = os.path.join(DATA_DIR, f)

        # detectar tipo
        if "empre" in name:
            new_name = "empresas.csv"

        elif "estabele" in name:
            new_name = "estabelecimentos.csv"

        elif "socio" in name:
            new_name = "socios.csv"

        elif "cnae" in name:
            new_name = "cnaes.csv"

        elif "natureza" in name or "natju" in name:
            new_name = "naturezas.csv"

        elif "munic" in name:
            new_name = "municipios.csv"

        else:
            continue

        new_path = os.path.join(DATA_DIR, new_name)

        # evita sobrescrever sem necessidade
        if old_path != new_path:
            print(f"Renomeado: {f} → {new_name}")

extract_and_rename()

# =========================
# AJUSTAR NOMES
# =========================

def find_file(tipo):
    for f in os.listdir(DATA_DIR):
        name = f.lower()

        if f.endswith(".zip"):
            continue

        if tipo == "empresas" and "empre" in name:
            return os.path.join(DATA_DIR, f)

        if tipo == "estabelecimentos" and "estabele" in name:
            return os.path.join(DATA_DIR, f)

        if tipo == "socios" and "socio" in name:
            return os.path.join(DATA_DIR, f)

        if tipo == "cnaes" and "cnae" in name:
            return os.path.join(DATA_DIR, f)

        if tipo == "naturezas" and ("natureza" in name or "natju" in name):
            return os.path.join(DATA_DIR, f)

        if tipo == "municipios" and "munic" in name:
            return os.path.join(DATA_DIR, f)

    return None

empresas_file = find_file("empresas")
estabs_file = find_file("estabelecimentos")
socios_file = find_file("socios")
cnaes_file = find_file("cnaes")
nat_file = find_file("naturezas")
municipios_file = find_file("municipios")

print("Arquivos encontrados:")
print("Empresas:", empresas_file)
print("Estabelecimentos:", estabs_file)
print("Socios:", socios_file)
print("CNAEs:", cnaes_file)
print("Naturezas:", nat_file)
print("Municipios:", municipios_file)

'''

if empresas_file is None:
    raise Exception("Arquivo de empresas não encontrado na pasta data/")

if estabs_file is None:
    raise Exception("Arquivo de estabelecimentos não encontrado na pasta data/")
'''

# =========================
# LOAD DUCKDB
# =========================

con = duckdb.connect(DB_PATH)

# =========================
# FUNÇÃO PARA RENOMEAR AS COLUNAS
# =========================

def rename_by_index(con, table, mapping):
    cols = con.execute(f"DESCRIBE {table}").fetchdf()["column_name"].tolist()
    for i, name in mapping.items():
        if i < len(cols):
            con.execute(f"ALTER TABLE {table} RENAME COLUMN {cols[i]} TO {name}")

# =========================
# EMPRESAS
# =========================
con.execute(f"""
CREATE OR REPLACE TABLE empresas AS
SELECT *
FROM read_csv_auto(
    '{DATA_DIR}/empresas*.csv',
    delim=';',
    header=False,
    ignore_errors=true,
    all_varchar=true
);
""")

cols = con.execute("DESCRIBE empresas").fetchdf()["column_name"].tolist()

con.execute(f"ALTER TABLE empresas RENAME COLUMN {cols[0]} TO cnpj_basico;")
con.execute(f"ALTER TABLE empresas RENAME COLUMN {cols[1]} TO razao_social;")
con.execute(f"ALTER TABLE empresas RENAME COLUMN {cols[2]} TO natureza_juridica;")
con.execute(f"ALTER TABLE empresas RENAME COLUMN {cols[3]} TO qualificacao_responsavel;")
con.execute(f"ALTER TABLE empresas RENAME COLUMN {cols[4]} TO capital_social;")
con.execute(f"ALTER TABLE empresas RENAME COLUMN {cols[5]} TO porte_empresa;")
con.execute(f"ALTER TABLE empresas RENAME COLUMN {cols[6]} TO ente_federativo;")

print("Empresas carregadas!")

# =========================
# ESTABELECIMENTOS
# =========================
con.execute(f"""
    CREATE OR REPLACE TABLE estabelecimentos AS
    SELECT *
    FROM read_csv_auto(
        '{DATA_DIR}/estabelecimentos*.csv',
        delim=';',
        header=False,
        ignore_errors=true,
        all_varchar=true
    );
    """)

rename_by_index(con, "estabelecimentos", {
    0: "cnpj_basico",
    1: "cnpj_ordem",
    2: "cnpj_dv",
    5: "situacao_cadastral",
    11: "cnae_fiscal",
    19: "uf",
    20: "municipio"
})

print("Estabelecimentos carregados!")

# =========================
# SOCIOS
# =========================

con.execute(f"""
CREATE OR REPLACE TABLE socios AS
SELECT *
FROM read_csv_auto(
    '{DATA_DIR}/socios*.csv',
    delim=';',
    header=False,
    ignore_errors=true,
    all_varchar=true
);
""")

rename_by_index(con, "socios", {
    0: "cnpj_basico",
    1: "identificador_socio",
    2: "nome_socio"
})

print("Sócios carregados!")


# =========================
# CNAES
# =========================

con.execute(f"""
CREATE OR REPLACE TABLE cnaes AS
SELECT *
FROM read_csv_auto(
    '{DATA_DIR}/cnae*.csv',
    delim=';',
    header=False,
    ignore_errors=true,
    all_varchar=true
);
""")

rename_by_index(con, "cnaes", {
    0: "codigo",
    1: "descricao"
})

print("CNAEs carregados!")

# =========================
# NATUREZAS JURIDICAS
# =========================

con.execute(f"""
CREATE OR REPLACE TABLE naturezas_juridicas AS
SELECT *
FROM read_csv_auto(
    '{DATA_DIR}/natureza*.csv',
    delim=';',
    header=False,
    ignore_errors=true,
    all_varchar=true
);
""")

rename_by_index(con, "naturezas_juridicas", {
    0: "codigo",
    1: "descricao"
})

print("Naturezas jurídicas carregadas!")

# =========================
# MUNICIPIOS
# =========================

con.execute(f"""
CREATE OR REPLACE TABLE municipios AS
SELECT *
FROM read_csv_auto(
    '{DATA_DIR}/*munic*.csv',
    delim=';',
    header=False,
    ignore_errors=true,
    all_varchar=true
);
""")

rename_by_index(con, "municipios", {
    0: "codigo",
    1: "descricao"
})

print("Municípios carregados!")


print("Pipeline concluído com sucesso!")