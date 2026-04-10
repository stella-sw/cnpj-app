import streamlit as st
import duckdb
import pandas as pd

# conexão com banco de dados (vamos criar depois se não existir)
con = duckdb.connect("db/cnpj.duckdb")

st.title("Consulta CNPJ")

st.write("Busque emprezas por razão social ou CNPJ")

#inputs
col1, col2 = st.columns(2)

with col1:
    busca_nome = st.text_input("Razão social")

with col2:
    busca_cnpj = st.text_input("CNPJ")

ufs = con.execute("SELECT DISTINCT uf FROM estabelecimentos").fetchdf()["uf"].dropna().tolist()
uf = st.selectbox("UF", [""] + ufs)

#botão
if st.button("Buscar"):
    query = """
    SELECT 
        e.cnpj_basico,
        e.razao_social,
        est.uf,
        est.municipio
    FROM empresas e
    LEFT JOIN estabelecimentos est
    ON e.cnpj_basico = est.cnpj_basico
    WHERE 1=1
    """

    if busca_nome:
        query += f" AND e.razao_social ILIKE '%{busca_nome}%'"

    if busca_cnpj:
        query += f" AND e.cnpj_basico LIKE '%{busca_cnpj}%'"
    
    if uf:
        query += f" AND est.uf = '{uf}'"
    
    try:
        df = con.execute(query + " LIMIT 50").fetchdf()
        if not df.empty:
            st.write("Resultados:")

            # cria uma lista com identificador
            opcoes = df["razao_social"] + " (" + df["cnpj_basico"] + ")"

            escolha = st.selectbox("Selecione uma empresa", opcoes)

            empresa = df[opcoes == escolha].iloc[0]

            st.subheader("Detalhes da Empresa")

            st.write(f"**CNPJ:** {empresa['cnpj_basico']}")
            st.write(f"**Razão Social:** {empresa['razao_social']}")
            st.write(f"**UF:** {empresa['uf']}")
            st.write(f"**Município:** {empresa['municipio']}")
    except Exception as e:
        st.error(f"Erro: {e}")
