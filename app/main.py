import streamlit as st
import duckdb
import pandas as pd

# =========================
# CONEXÃO
# =========================
con = duckdb.connect("db/cnpj.duckdb")

# =========================
# SESSION STATE
# =========================
if "resultados" not in st.session_state:
    st.session_state.resultados = None

# =========================
# UI
# =========================
st.title("Consulta CNPJ")
st.write("Busca de empresas do cadastro CNPJ")

# =========================
# FORM DE BUSCA (ENTER FUNCIONA)
# =========================
with st.sidebar.form("form_busca"):

    st.header("Filtros")

    busca_nome = st.text_input("Razão social")
    busca_cnpj = st.text_input("CNPJ")

    uf = st.text_input("UF (ex: SC)")
    municipio = st.text_input("Município")
    cnae = st.text_input("CNAE principal")

    limite = st.slider("Limite de resultados", 10, 200, 50)

    buscar = st.form_submit_button("Buscar")

# =========================
# QUERY
# =========================
if buscar:

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

    if municipio:
        query += f" AND est.municipio ILIKE '%{municipio}%'"

    if uf:
        query += f" AND est.uf ILIKE '%{uf}%'"

    if cnae:
        query += f"""
        AND EXISTS (
            SELECT 1 FROM estabelecimentos e2
            WHERE e2.cnpj_basico = e.cnpj_basico
            AND e2.cnae_fiscal LIKE '%{cnae}%'
        )
        """

    try:
        st.session_state.resultados = con.execute(query + f" LIMIT {limite}").fetchdf()
    except Exception as e:
        st.error(f"Erro na consulta: {e}")

# =========================
# RESULTADOS (FORA DO BOTÃO)
# =========================
df = st.session_state.resultados

if df is not None:

    if df.empty:
        st.warning("Nenhuma empresa encontrada.")
    else:
        st.subheader("Resultados")

        opcoes = df["cnpj_basico"].astype(str) + " - " + df["razao_social"]

        escolha = st.selectbox(
            "Selecione uma empresa",
            opcoes,
            key="empresa_select"
        )

        cnpj = escolha.split(" - ")[0]

        # =========================
        # DADOS DA EMPRESA
        # =========================
        st.subheader("Dados da Empresa")

        dados = con.execute(f"""
        SELECT *
        FROM empresas
        WHERE cnpj_basico = '{cnpj}'
        LIMIT 1
        """).fetchdf()

        st.dataframe(dados, width="stretch")

        # =========================
        # ESTABELECIMENTOS
        # =========================
        st.subheader("Estabelecimentos")

        estabs = con.execute(f"""
        SELECT 
            est.cnpj_ordem,
            m.descricao AS municipio,
            est.uf
        FROM estabelecimentos est
        LEFT JOIN municipios m
            ON est.municipio = m.codigo
        WHERE est.cnpj_basico = '{cnpj}'
        LIMIT 20
        """).fetchdf()

        if estabs.empty:
            st.info("Nenhum estabelecimento encontrado.")
        else:
            st.dataframe(estabs, width="stretch")

        # =========================
        # SÓCIOS
        # =========================
        st.subheader("Sócios")

        try:
            socios = con.execute(f"""
            SELECT nome_socio, identificador_socio
            FROM socios
            WHERE cnpj_basico = '{cnpj}'
            LIMIT 20
            """).fetchdf()

            if socios.empty:
                st.info("Nenhum sócio encontrado.")
            else:
                st.dataframe(socios, width="stretch")

        except Exception:
            st.info("Tabela de sócios não disponível.")

        # =========================
        # CNAE
        # =========================
        st.subheader("CNAE")

        try:
            cnae_empresa = con.execute(f"""
            SELECT c.codigo, c.descricao
            FROM cnaes c
            WHERE c.codigo = (
                SELECT cnae_fiscal
                FROM estabelecimentos
                WHERE cnpj_basico = '{cnpj}'
                LIMIT 1
            )
            """).fetchdf()

            if cnae_empresa.empty:
                st.info("CNAE não encontrado.")
            else:
                st.dataframe(cnae_empresa, width="stretch")

        except Exception:
            st.info("CNAEs não disponíveis.")