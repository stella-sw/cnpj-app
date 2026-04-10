# CNPJ Data App

Aplicação para ingestão e visualização de dados públicos do CNPJ utilizando DuckDB e Streamlit.

---

## Funcionalidades

- Busca por razão social
- Busca por CNPJ
- Filtro por UF
- Visualização de dados cadastrais
- Estrutura para estabelecimentos e sócios

---

## Tecnologias

- Python
- DuckDB
- Streamlit
- Pandas

---

### Coleta de Dados

Os dados utilizados neste projeto são provenientes do portal oficial da Receita Federal:

https://arquivos.receitafederal.gov.br/index.php/s/YggdBLfdninEJX9

Devido a restrições do servidor (bloqueio de requisições automatizadas e ausência de API pública estável), o download automático completo dos arquivos não é garantido.

Assim, a solução adotada foi:

- Os arquivos são previamente baixados e armazenados na pasta `data/`
- O pipeline realiza automaticamente:
  - identificação dos arquivos
  - extração dos arquivos compactados (.zip)
  - parsing dos dados
  - carga no banco DuckDB

Essa abordagem garante:

- reprodutibilidade
- robustez
- independência de falhas externas

Atendendo ao requisito do desafio de **"baixar ou ler os dados"**.

## Como executar

### 1. Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
