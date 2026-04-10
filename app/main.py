import streamlit as st
import duckdb
import pandas as pd


con = duckdb.connect("db/cnpj.duckdb")

st.title("Consulta CNPJ")

st.write("Busca de empresas do cadastro CNPJ")

# =========================
# INPUTS
# =========================
col1, col2 = st.columns(2)

with col1:
    busca_nome = st.text_input("Razão social")

with col2:
    busca_cnpj = st.text_input("CNPJ")

ufs = con.execute("""
SELECT DISTINCT uf_sigla
FROM estabelecimentos
WHERE uf_sigla IS NOT NULL
ORDER BY uf_sigla
""").fetchdf()["uf_sigla"].tolist()

uf_escolhido = st.selectbox("UF", [""] + ufs)

# =========================
# BUSCA
# =========================
if st.button("Buscar"):

    query = """
    SELECT DISTINCT
        e.cnpj_basico,
        e.razao_social
    FROM empresas e
    LEFT JOIN estabelecimentos est
        ON e.cnpj_basico = est.cnpj_basico
    WHERE 1=1
    """

    if busca_nome:
        query += f" AND e.razao_social ILIKE '%{busca_nome}%'"

    if busca_cnpj:
        query += f" AND e.cnpj_basico LIKE '%{busca_cnpj}%'"

    if uf_escolhido:
        query += f" AND est.uf_sigla = '{uf_escolhido}'"

    try:
        df = con.execute(query + " LIMIT 50").fetchdf()

        if df.empty:
            st.warning("Nenhuma empresa encontrada.")
        else:
            st.subheader("Resultados")

            opcoes = df["cnpj_basico"].astype(str) + " - " + df["razao_social"]

            escolha = st.selectbox("Selecione uma empresa", opcoes)

            cnpj = escolha.split(" - ")[0]

            empresa = df[df["cnpj_basico"] == cnpj].iloc[0]

            cnpj = empresa["cnpj_basico"]

            # =========================
            # DETALHES EMPRESA
            # =========================
            st.subheader("Dados da Empresa")

            dados = con.execute(f"""
            SELECT *
            FROM empresas
            WHERE cnpj_basico = '{cnpj}'
            LIMIT 1
            """).fetchdf()

            st.dataframe(dados)

            # =========================
            # ESTABELECIMENTOS
            # =========================
            st.subheader("Estabelecimentos")

            estabs = con.execute(f"""
SELECT cnpj_ordem, uf_sigla, municipio
FROM estabelecimentos
WHERE cnpj_basico = '{cnpj}'
LIMIT 20
""").fetchdf()

            st.dataframe(estabs)

            # =========================
            # SÓCIOS (REQUISITO OBRIGATÓRIO)
            # =========================
            st.subheader("Sócios")

            try:
                socios = con.execute(f"""
                SELECT *
                FROM socios
                WHERE cnpj_basico = '{cnpj}'
                LIMIT 20
                """).fetchdf()

                if socios.empty:
                    st.info("Nenhum sócio encontrado.")
                else:
                    st.dataframe(socios)

            except Exception:
                st.info("Tabela de sócios não disponível.")

            # =========================
            # CNAE (EXTRA VALIOSO)
            # =========================
            st.subheader("CNAE da Empresa")

            try:
                cnae_empresa = con.execute(f"""
                SELECT *
                FROM cnaes
                WHERE codigo = (
                    SELECT cnae_fiscal
                    FROM estabelecimentos
                    WHERE cnpj_basico = '{cnpj}'
                    LIMIT 1
                )
                """).fetchdf()

                if cnae_empresa.empty:
                    st.info("CNAE não encontrado.")
                else:
                    st.dataframe(cnae_empresa)

            except Exception:
                st.info("CNAEs não disponíveis.")

    except Exception as e:
        st.error(f"Erro na consulta: {e}")