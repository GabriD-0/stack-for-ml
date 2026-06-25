# Coleta e preparação de dados do Stack Overflow para ML

Projeto prático de coleta, armazenamento, tratamento e preparação de dados temporais do Stack Overflow (via Stack Exchange API) para uso em aprendizado de máquina.

**Tema:** Coleta e preparação de dados temporais do Stack Overflow para prever a resolução de perguntas sobre tecnologias populares.

## Pré-requisitos

- Python 3.12.10+
- Acesso à API Stack Exchange

## Instalação

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuração

- Crie um arquivo `.env` na raiz do projeto para `SQLITE_DB_PATH`, `MONTHS` e `STACK_API_KEY`.
- **Banco:** por padrão o SQLite usa `data/stackoverflow.db`. Defina `SQLITE_DB_PATH` no `.env` para alterar.
- **Janela temporal:** variável `MONTHS` (padrão 6). Ex.: `MONTHS=12` para 12 meses.
- **API:** sem chave são 10.000 requisições/dia. Para cota maior, cadastre em [Stack Apps](https://stackapps.com/) e defina `STACK_API_KEY` no `.env`.

## Uso

### 1. Criar o banco e o esquema

O esquema é aplicado automaticamente na primeira coleta. Para apenas criar as tabelas sem coletar:

```bash
python scripts/init_db.py
```

### 2. Coletar dados

```bash
python -m src.collector
```

Coleta perguntas das tags `python`, `reactjs`, `docker`, `vue.js` na janela configurada (padrão últimos 6 meses) e persiste em SQLite. Respeita backoff e limites da API.

### 3. Tratamento e dataset para ML

```bash
python -m src.transform
```

- Preenche a tabela `questions_for_ml` com limpeza e features derivadas.
- Exporta `data/questions_for_ml.csv` para uso na etapa de treinamento.

### 4. Documentação do dataset

Ver [docs/dataset.md](docs/dataset.md) para descrição das variáveis, fontes e etapas de limpeza.

## Estrutura do repositório

```
├── README.md
├── requirements.txt
├── Definição de case e coleta de dados.md
├── docs/
│   └── dataset.md
├── schema/
│   └── init.sql
├── scripts/
│   └── init_db.py    # Aplica o schema no SQLite
├── src/
│   ├── config.py      # Parâmetros (tags, datas, caminho do BD)
│   ├── collector.py   # Coleta via API e persistência
│   ├── db.py          # Conexão SQLite e upsert
│   └── transform.py   # Limpeza, features e export CSV
└── data/
    ├── stackoverflow.db      # Banco SQLite (gerado)
    └── questions_for_ml.csv  # Dataset para ML (gerado)
```

## Fontes dos dados

- **API:** [Stack Exchange API 2.3](https://api.stackexchange.com/docs), endpoint `/questions`, site `stackoverflow`.
- **Tags:** python, reactjs, docker, vue.js (coleta por tag para maior volume).
- **Limites:** 10.000 requisições/dia sem chave; a aplicação respeita o campo `backoff` da resposta.

## Desafios

- **Cota da API:** coleta por tag e paginação com pausas para não exceder o limite.
- **Backoff:** quando a API retorna `backoff`, o coletor aguarda o número de segundos indicado antes da próxima requisição.
- **Duplicados:** uma mesma pergunta pode aparecer em mais de uma tag; o upsert por `question_id` evita duplicação na tabela `questions`.