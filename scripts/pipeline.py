import os
import zipfile
import duckdb

# =========================
# CONFIG
# =========================
DATA_DIR = "data"
DB_PATH = "db/cnpj.duckdb"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs("db", exist_ok=True)

# =========================
# DOWNLOAD (AMOSTRA)
# =========================

def download_file(url, output):
    print(f"Baixando: {output}")
    os.system(f"wget -O {output} '{url}'")

# Baixando apenas 1 arquivo de cada (amostra)
empresas_url = "https://arquivos.receitafederal.gov.br/index.php/s/YggdBLfdninEJX9/download?path=%2FEmpresas&files=Empresas0.zip"
estabs_url = "https://arquivos.receitafederal.gov.br/index.php/s/YggdBLfdninEJX9/download?path=%2FEstabelecimentos&files=Estabelecimentos0.zip"

empresas_zip = f"{DATA_DIR}/empresas.zip"
estabs_zip = f"{DATA_DIR}/estabelecimentos.zip"

if not os.path.exists(empresas_zip):
    download_file(empresas_url, empresas_zip)

if not os.path.exists(estabs_zip):
    download_file(estabs_url, estabs_zip)

# =========================
# EXTRAÇÃO
# =========================

def extract(zip_path):
    print(f"Extraindo: {zip_path}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(DATA_DIR)

extract(empresas_zip)
extract(estabs_zip)

# =========================
# AJUSTAR NOMES
# =========================

def find_file(prefix):
    for f in os.listdir(DATA_DIR):
        if prefix in f and not f.endswith(".zip"):
            return os.path.join(DATA_DIR, f)
    return None

empresas_file = find_file("EMPRE")
estabs_file = find_file("ESTAB")

print("Empresas:", empresas_file)
print("Estabelecimentos:", estabs_file)

# =========================
# LOAD DUCKDB
# =========================

con = duckdb.connect(DB_PATH)

# EMPRESAS
con.execute(f"""
CREATE OR REPLACE TABLE empresas AS
SELECT *
FROM read_csv_auto(
    '{empresas_file}',
    delim=';',
    header=False,
    ignore_errors=true,
    all_varchar=true
);
""")

con.execute("ALTER TABLE empresas RENAME COLUMN column0 TO cnpj_basico;")
con.execute("ALTER TABLE empresas RENAME COLUMN column1 TO razao_social;")
con.execute("ALTER TABLE empresas RENAME COLUMN column2 TO natureza_juridica;")
con.execute("ALTER TABLE empresas RENAME COLUMN column3 TO qualificacao_responsavel;")
con.execute("ALTER TABLE empresas RENAME COLUMN column4 TO capital_social;")
con.execute("ALTER TABLE empresas RENAME COLUMN column5 TO porte_empresa;")
con.execute("ALTER TABLE empresas RENAME COLUMN column6 TO ente_federativo;")

print("Empresas carregadas!")

# ESTABELECIMENTOS
con.execute(f"""
CREATE OR REPLACE TABLE estabelecimentos AS
SELECT *
FROM read_csv_auto(
    '{estabs_file}',
    delim=';',
    header=False,
    ignore_errors=true,
    all_varchar=true
);
""")

con.execute("ALTER TABLE estabelecimentos RENAME COLUMN column0 TO cnpj_basico;")
con.execute("ALTER TABLE estabelecimentos RENAME COLUMN column1 TO cnpj_ordem;")
con.execute("ALTER TABLE estabelecimentos RENAME COLUMN column2 TO cnpj_dv;")
con.execute("ALTER TABLE estabelecimentos RENAME COLUMN column7 TO uf;")
con.execute("ALTER TABLE estabelecimentos RENAME COLUMN column8 TO municipio;")

print("Estabelecimentos carregados!")

print("Pipeline concluído com sucesso!")