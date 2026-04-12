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

def extract_and_merge():
    # =========================
    # LIMPAR ARQUIVOS NÃO-ZIP
    # =========================
    print("Limpando arquivos antigos...")

    for f in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, f)

        # mantém apenas .zip
        if not f.lower().endswith(".zip"):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Removido (pré-limpeza): {f}")
            except Exception as e:
                print(f"Erro ao remover {f}: {e}")    
    
    print("Extraindo ZIPs...")

    for file in os.listdir(DATA_DIR):
        if not file.endswith(".zip"):
            continue

        zip_path = os.path.join(DATA_DIR, file)

        if not zipfile.is_zipfile(zip_path):
            print(f"Pulando inválido: {file}")
            continue

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(DATA_DIR)

    print("Mesclando CSVs...")

    groups = {
        "empresas": [],
        "estabelecimentos": [],
        "socios": [],
        "cnaes": [],
        "naturezas": [],
        "municipios": []
    }

    # Agrupar arquivos
    for f in os.listdir(DATA_DIR):
        if f.lower().endswith(".zip"):
            continue

        name = f.lower()

        if "empre" in name:
            groups["empresas"].append(f)
        elif "estabele" in name:
            groups["estabelecimentos"].append(f)
        elif "socio" in name:
            groups["socios"].append(f)
        elif "cnae" in name:
            groups["cnaes"].append(f)
        elif "natureza" in name or "natju" in name:
            groups["naturezas"].append(f)
        elif "munic" in name:
            groups["municipios"].append(f)

    # Merge + delete seguro
    for group_name, files in groups.items():
        if not files:
            continue

        output_path = os.path.join(DATA_DIR, f"{group_name}.csv")

        print(f"Mesclando {group_name} ({len(files)} arquivos)...")

        with open(output_path, "w", encoding="utf-8", newline="") as outfile:
            header_written = False

            for file in sorted(files):
                file_path = os.path.join(DATA_DIR, file)

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
                        for i, line in enumerate(infile):
                            if i == 0:
                                if not header_written:
                                    outfile.write(line)
                                    header_written = True
                            else:
                                outfile.write(line)

                    # delete ONLY after successful processing
                    os.remove(file_path)
                    print(f"Removido: {file}")

                except Exception as e:
                    print(f"Erro ao processar {file}: {e}")
                    print("Arquivo NÃO foi deletado")

    print("Merge concluído e arquivos limpos")

extract_and_merge()


empresas_file = os.path.join(DATA_DIR, "empresas.csv")
estabs_file = os.path.join(DATA_DIR, "estabelecimentos.csv")
socios_file = os.path.join(DATA_DIR, "socios.csv")
cnaes_file = os.path.join(DATA_DIR, "cnaes.csv")
nat_file = os.path.join(DATA_DIR, "naturezas.csv")
municipios_file = os.path.join(DATA_DIR, "municipios.csv")

for f in [empresas_file, estabs_file, socios_file, cnaes_file, nat_file, municipios_file]:
    if not os.path.exists(f):
        print(f"Arquivo faltando: {f}")

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
