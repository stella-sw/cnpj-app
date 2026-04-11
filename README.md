# CNPJ Data App

Aplicação para ingestão, processamento e visualização de dados públicos do CNPJ utilizando **DuckDB** e **Streamlit**.

---

## Funcionalidades

- Busca por razão social
- Busca por CNPJ
- Filtros adicionais:
  - UF
  - Município
  - CNAE principal
- Visualização de dados cadastrais da empresa
- Listagem de estabelecimentos vinculados
- Visualização de sócios
- Exibição do CNAE principal
- Interface interativa com atualização dinâmica

---

## Tecnologias

- Python
- DuckDB (banco analítico local)
- Streamlit (interface web)
- Pandas (manipulação de dados)

---

## Uso de Inteligência Artificial

No desenvolvimento deste projeto foram utilizados assistentes de código baseados em Inteligência Artificial.

**Tecnologia utilizada**
- ChatGPT (OpenAI)

**Atividades em que a IA foi utilizada**
- Apoio na estruturação do pipeline de dados
- Sugestões para tratamento e padronização de dados
- Auxílio na identificação e correção de erros
- Melhoria na organização do código e boas práticas
- Apoio na documentação do projeto (README)

A utilização da IA teve caráter assistivo, não substituindo o entendimento e as decisões de implementação por parte do desenvolvedor.

---

## Coleta de Dados

Os dados utilizados neste projeto são provenientes do portal oficial da Receita Federal:

https://arquivos.receitafederal.gov.br/index.php/s/YggdBLfdninEJX9

Devido a limitações do servidor (como bloqueio de requisições automatizadas e ausência de API pública estável), o download automático completo não é garantido.

### Abordagem adotada

- Os arquivos são previamente baixados e armazenados na pasta `data/`
- O pipeline realiza automaticamente:
  - extração de arquivos `.zip`
  - leitura de múltiplos arquivos por entidade (ex: `Estabelecimentos0`, `Estabelecimentos1`, etc.)
  - tratamento e padronização das colunas
  - carga no banco DuckDB

### Benefícios

- Reprodutibilidade
- Robustez contra falhas externas
- Processamento eficiente de grandes volumes de dados

---

## Pipeline de Dados

O pipeline foi projetado para lidar com a estrutura distribuída dos dados do CNPJ.

### Principais características:

- Leitura de múltiplos arquivos por tabela usando padrões glob (`*`)
- Padronização de colunas por índice
- Armazenamento em banco analítico local (DuckDB)
- Suporte às seguintes entidades:
  - Empresas
  - Estabelecimentos
  - Sócios
  - CNAEs
  - Naturezas jurídicas
  - Municípios

---

## Como executar

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd <nome-do-repositorio>
```

### 2. Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Adicionar os dados

Acesse o portal da Receita Federal: https://arquivos.receitafederal.gov.br/index.php/s/YggdBLfdninEJX9

Baixe os arquivos .zip desejados (ex: Empresas, Estabelecimentos, Sócios, CNAE, etc.) e coloque-os na pasta data/

Não é necessário extrair manualmente — o pipeline faz isso automaticamente.

### 5. Executar

```bash
python run.py
```
