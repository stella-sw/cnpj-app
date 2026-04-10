import os
import subprocess
import sys

DB_PATH = "db/cnpj.duckdb"

# =========================
# PASSO 1 — garantir banco
# =========================
if not os.path.exists(DB_PATH):
    print("Banco não encontrado. Executando pipeline...")
    subprocess.run([sys.executable, "scripts/pipeline.py"])
else:
    print("Banco já existe. Pulando pipeline.")

# =========================
# PASSO 2 — rodar Streamlit
# =========================
print("Iniciando aplicação Streamlit...")

subprocess.run([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    "app/main.py"
])
