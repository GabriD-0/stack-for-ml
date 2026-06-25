# Dicionário de Dados — Stack Overflow para ML

**Projeto:** Coleta e preparação de dados do Stack Overflow para Machine Learning  
**Versão:** 1.0  
**Data:** 09/04/2026  
**Autores:** Gabriel de Oliveira & Raniel Lima de Lira

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Fonte dos Dados](#2-fonte-dos-dados)
3. [Modelo Relacional](#3-modelo-relacional)
4. [Tabela `questions`](#4-tabela-questions)
5. [Tabela `tags`](#5-tabela-tags)
6. [Tabela `question_tags`](#6-tabela-question_tags)
7. [Tabela `questions_for_ml`](#7-tabela-questions_for_ml)
8. [Dataset de Exportação — `questions_for_ml.csv`](#8-dataset-de-exportação--questions_for_mlcsv)
9. [Índices do Banco de Dados](#9-índices-do-banco-de-dados)
10. [Variáveis Derivadas (Feature Engineering)](#10-variáveis-derivadas-feature-engineering)
11. [Transformações e Limpeza](#11-transformações-e-limpeza)
12. [Uso para Machine Learning](#12-uso-para-machine-learning)

---

## 1. Visão Geral

Este dicionário descreve todos os dados coletados, armazenados e transformados pelo pipeline do projeto. Os dados são obtidos da Stack Exchange API v2.3, persistidos em um banco SQLite (`data/stackoverflow.db`) e exportados como CSV (`data/questions_for_ml.csv`) para uso em modelos de aprendizado de máquina.

**Tecnologias monitoradas (tags):** `python`, `reactjs`, `docker`, `vue.js`  
**Janela temporal:** últimos 6 meses (configurável até 12 meses via variável `MONTHS`)  
**Volume:** ~3.815 registros (referência: coleta de 26/03/2026)  
**Banco de dados:** SQLite (`data/stackoverflow.db`)

---

## 2. Fonte dos Dados

| Atributo | Valor |
|---|---|
| Origem | Stack Exchange API v2.3 |
| Endpoint | `/questions` |
| Site | `stackoverflow` |
| Formato de resposta | JSON |
| Autenticação | Opcional — chave via `STACK_API_KEY` no `.env` |
| Cota sem chave | 10.000 requisições/dia |
| Cota com chave | Ampliada conforme plano Stack Apps |
| Paginação | 100 itens por página |
| Ordenação | Por `creation` (decrescente) |
| Campos retornados pela API | `question_id`, `title`, `creation_date`, `last_activity_date`, `score`, `view_count`, `answer_count`, `is_answered`, `accepted_answer_id`, `tags` |

---

## 3. Modelo Relacional

```
questions (1) ──< question_tags >── (N) tags
    │
    └── questions_for_ml (1:1, derivada)
```

- `questions` é a tabela principal com uma linha por pergunta única.
- `tags` é o catálogo normalizado de tags.
- `question_tags` representa a relação muitos-para-muitos entre perguntas e tags.
- `questions_for_ml` é uma visão desnormalizada da `questions`, enriquecida com features derivadas para uso em ML.

---

## 4. Tabela `questions`

**Descrição:** Tabela principal. Armazena uma linha por pergunta única coletada do Stack Overflow. Alimentada pelo script `src/collector.py` via upsert (inserção ou atualização por `question_id`).

| Campo | Tipo SQL | Nulável | Padrão | Chave | Descrição |
|---|---|---|---|---|---|
| `question_id` | `INTEGER` | Não | — | PK | Identificador único da pergunta, atribuído pela Stack Exchange API. Nunca reutilizado. |
| `title` | `TEXT` | Não | — | — | Título da pergunta, exatamente como publicado pelo usuário. Pode conter HTML escapado em casos raros. |
| `creation_date` | `TEXT` | Não | — | — | Data e hora de criação da pergunta no formato `YYYY-MM-DD HH:MM:SS` (UTC). Convertida de Unix timestamp durante a ingestão. |
| `last_activity_date` | `TEXT` | Sim | `NULL` | — | Data e hora da última atividade (edição, nova resposta, comentário) no formato `YYYY-MM-DD HH:MM:SS` (UTC). Nulo quando não há atividade registrada. |
| `score` | `INTEGER` | Não | `0` | — | Pontuação da pergunta: total de votos positivos menos votos negativos. Pode ser negativo. |
| `view_count` | `INTEGER` | Não | `0` | — | Número acumulado de visualizações da página da pergunta. Valor sempre maior ou igual a zero. |
| `answer_count` | `INTEGER` | Não | `0` | — | Número de respostas postadas. Não inclui comentários. Valor sempre maior ou igual a zero. |
| `is_answered` | `INTEGER` | Não | `0` | — | Indicador binário. `1` = a pergunta tem ao menos uma resposta; `0` = sem respostas. Calculado pela própria API. |
| `has_accepted_answer` | `INTEGER` | Não | `0` | — | Indicador binário. `1` = o autor aceitou uma resposta; `0` = sem resposta aceita. Derivado da presença do campo `accepted_answer_id` na resposta da API. **Variável-alvo secundária.** |
| `created_at` | `TEXT` | Não | `datetime('now')` | — | Timestamp de ingestão no banco local (quando o registro foi gravado ou atualizado no SQLite). Formato `YYYY-MM-DD HH:MM:SS` (horário do sistema). |

### Domínios e observações

| Campo | Valores possíveis / Domínio | Observação |
|---|---|---|
| `question_id` | Inteiro positivo (ex.: `12345678`) | Gerado pela Stack Exchange; imutável. |
| `title` | String livre | Máximo ~150 caracteres (recomendado pelo SO). |
| `creation_date` | `YYYY-MM-DD HH:MM:SS` | Sempre em UTC. |
| `last_activity_date` | `YYYY-MM-DD HH:MM:SS` ou `NULL` | NULL em registros antigos/inativos. |
| `score` | Qualquer inteiro (incluindo negativos) | Votações negativas são possíveis. |
| `view_count` | ≥ 0 | Nunca negativo. |
| `answer_count` | ≥ 0 | Uma pergunta pode ter 0 respostas. |
| `is_answered` | `0` ou `1` | `1` quando `answer_count > 0` **e** a resposta tem pontuação positiva (regra da API). |
| `has_accepted_answer` | `0` ou `1` | `1` quando `accepted_answer_id` está presente no JSON da API. |
| `created_at` | `YYYY-MM-DD HH:MM:SS` | Fuso horário local do servidor/máquina que executou a coleta. |

---

## 5. Tabela `tags`

**Descrição:** Catálogo normalizado de todas as tags encontradas nas perguntas coletadas. Alimentado automaticamente pelo coletor ao inserir novas tags.

| Campo | Tipo SQL | Nulável | Padrão | Chave | Descrição |
|---|---|---|---|---|---|
| `tag_id` | `INTEGER` | Não | AUTOINCREMENT | PK | Identificador interno gerado automaticamente pelo banco. Não corresponde a nenhum ID da API. |
| `name` | `TEXT` | Não | — | UNIQUE | Nome da tag em letras minúsculas (ex.: `python`, `reactjs`). Garante unicidade no catálogo. |

### Domínios e observações

| Campo | Valores possíveis / Domínio | Observação |
|---|---|---|
| `tag_id` | Inteiro positivo sequencial | Gerado localmente; sem significado externo. |
| `name` | String minúscula sem espaços | Exemplos principais: `python`, `reactjs`, `docker`, `vue.js`. Outras tags relacionadas também são armazenadas. |

---

## 6. Tabela `question_tags`

**Descrição:** Tabela de junção que representa a relação muitos-para-muitos entre perguntas e tags. Uma pergunta pode ter várias tags e uma tag pode estar em várias perguntas.

| Campo | Tipo SQL | Nulável | Padrão | Chave | Descrição |
|---|---|---|---|---|---|
| `question_id` | `INTEGER` | Não | — | PK (composta), FK → `questions.question_id` | Referencia a pergunta. Exclusão em cascata (`ON DELETE CASCADE`). |
| `tag_id` | `INTEGER` | Não | — | PK (composta), FK → `tags.tag_id` | Referencia a tag. Exclusão em cascata (`ON DELETE CASCADE`). |

### Domínios e observações

| Campo | Valores possíveis / Domínio | Observação |
|---|---|---|
| `question_id` | Deve existir em `questions` | Restrição de integridade referencial. |
| `tag_id` | Deve existir em `tags` | Restrição de integridade referencial. |

**Chave primária composta:** (`question_id`, `tag_id`) — impede duplicatas na associação.

---

## 7. Tabela `questions_for_ml`

**Descrição:** Tabela desnormalizada e enriquecida com features derivadas, gerada pelo script `src/transform.py`. Agrega os dados de `questions` e `question_tags` em uma única linha por pergunta, pronta para uso em modelos de ML. Espelha o conteúdo do arquivo CSV exportado.

| Campo | Tipo SQL | Nulável | Padrão | Origem | Descrição |
|---|---|---|---|---|---|
| `question_id` | `INTEGER` | Não | — | `questions.question_id` | Identificador único da pergunta. FK referenciando `questions`. |
| `title` | `TEXT` | Não | — | `questions.title` | Título da pergunta. Valores nulos substituídos por string vazia na transformação. |
| `creation_date` | `TEXT` | Não | — | `questions.creation_date` | Data/hora de criação (`YYYY-MM-DD HH:MM:SS`, UTC). |
| `last_activity_date` | `TEXT` | Sim | `NULL` | `questions.last_activity_date` | Data/hora da última atividade (`YYYY-MM-DD HH:MM:SS`, UTC). Pode ser nulo. |
| `score` | `INTEGER` | Não | `0` | `questions.score` | Pontuação da pergunta (votos positivos − negativos). |
| `view_count` | `INTEGER` | Não | `0` | `questions.view_count` | Número de visualizações acumuladas. |
| `answer_count` | `INTEGER` | Não | `0` | `questions.answer_count` | Número de respostas postadas. |
| `is_answered` | `INTEGER` | Não | `0` | `questions.is_answered` | Binário: `1` = tem ao menos uma resposta; `0` = sem resposta. **Variável-alvo principal.** |
| `has_accepted_answer` | `INTEGER` | Não | `0` | `questions.has_accepted_answer` | Binário: `1` = tem resposta aceita; `0` = sem resposta aceita. **Variável-alvo alternativa.** |
| `hour_of_day` | `INTEGER` | Não | — | Derivada de `creation_date` | Hora do dia (0–23) em que a pergunta foi criada (UTC). Feature temporal. |
| `day_of_week` | `INTEGER` | Não | — | Derivada de `creation_date` | Dia da semana (0–6, onde 0 = domingo) em que a pergunta foi criada. Feature temporal. |
| `title_length` | `INTEGER` | Não | — | Derivada de `title` | Número de caracteres do título. Feature de texto. |
| `num_tags` | `INTEGER` | Não | `0` | Derivada de `question_tags` | Quantidade de tags associadas à pergunta. Feature de engajamento/categorização. |
| `created_at` | `TEXT` | Não | `datetime('now')` | Sistema | Timestamp de ingestão desta linha na tabela (`YYYY-MM-DD HH:MM:SS`, horário local). |

---

## 8. Dataset de Exportação — `questions_for_ml.csv`

**Localização:** `data/questions_for_ml.csv`  
**Formato:** CSV, separado por vírgula, codificação UTF-8, com cabeçalho  
**Gerado por:** `src/transform.py`  
**Conteúdo:** espelho exato da tabela `questions_for_ml` (sem a coluna `created_at`)

### Colunas e ordem no CSV

| Posição | Nome da coluna | Tipo Python | Exemplo | Descrição resumida |
|---|---|---|---|---|
| 1 | `question_id` | `int` | `78432156` | ID da pergunta |
| 2 | `title` | `str` | `"How to use asyncio in Python?"` | Título da pergunta |
| 3 | `creation_date` | `str` | `"2025-10-14 13:45:02"` | Data/hora de criação (UTC) |
| 4 | `last_activity_date` | `str` / `None` | `"2025-10-15 09:22:11"` | Última atividade (UTC) |
| 5 | `score` | `int` | `7` | Pontuação |
| 6 | `view_count` | `int` | `1243` | Visualizações |
| 7 | `answer_count` | `int` | `2` | Número de respostas |
| 8 | `is_answered` | `int` (0/1) | `1` | Tem resposta? |
| 9 | `has_accepted_answer` | `int` (0/1) | `1` | Tem resposta aceita? |
| 10 | `hour_of_day` | `int` | `13` | Hora de criação (0–23) |
| 11 | `day_of_week` | `int` | `1` | Dia da semana (0=dom, 6=sáb) |
| 12 | `title_length` | `int` | `35` | Comprimento do título (chars) |
| 13 | `num_tags` | `int` | `4` | Número de tags |

---

## 9. Índices do Banco de Dados

| Nome do índice | Tabela | Campo(s) | Finalidade |
|---|---|---|---|
| `idx_questions_creation_date` | `questions` | `creation_date` | Acelera consultas com filtro por intervalo de datas. |
| `idx_questions_has_accepted_answer` | `questions` | `has_accepted_answer` | Acelera análises de distribuição da variável-alvo. |
| `idx_question_tags_question_id` | `question_tags` | `question_id` | Acelera JOINs ao buscar tags de uma pergunta. |
| `idx_question_tags_tag_id` | `question_tags` | `tag_id` | Acelera JOINs ao buscar perguntas de uma tag. |

---

## 10. Variáveis Derivadas (Feature Engineering)

As features abaixo são calculadas pelo script `src/transform.py` durante o processo de ETL e armazenadas tanto na tabela `questions_for_ml` quanto no CSV exportado.

| Feature | Fórmula / Origem | Tipo | Domínio | Justificativa |
|---|---|---|---|---|
| `hour_of_day` | `strftime('%H', creation_date)` convertido para inteiro | `INTEGER` | 0 – 23 | Captura padrões de postagem por horário (ex.: horário comercial vs. madrugada) que podem influenciar engajamento e probabilidade de resposta. |
| `day_of_week` | `strftime('%w', creation_date)` convertido para inteiro | `INTEGER` | 0 (dom) – 6 (sáb) | Captura padrões semanais de atividade da comunidade (dias úteis tendem a ter mais engajamento). |
| `title_length` | `LENGTH(title)` | `INTEGER` | ≥ 0 | Títulos mais descritivos (nem muito curtos nem excessivamente longos) podem correlacionar com maior chance de resposta. |
| `num_tags` | `COUNT(tag_id)` via LEFT JOIN com `question_tags` | `INTEGER` | ≥ 0 | Quantidade de tags associadas; perguntas bem categorizadas alcançam mais especialistas. |

---

## 11. Transformações e Limpeza

| Etapa | Descrição | Campo(s) afetado(s) |
|---|---|---|
| **Deduplicação** | O coletor usa upsert por `question_id`; uma pergunta que aparece em múltiplas tags (ex.: `python` e `docker`) é armazenada uma única vez. | `question_id` |
| **Conversão de timestamp** | A API retorna timestamps como Unix epoch (segundos desde 1970-01-01). O pipeline converte para `YYYY-MM-DD HH:MM:SS` (UTC) via `datetime.utcfromtimestamp()`. | `creation_date`, `last_activity_date` |
| **Tratamento de nulos — has_accepted_answer** | O campo `accepted_answer_id` é ausente no JSON quando não há resposta aceita. O pipeline define `has_accepted_answer = 1` quando presente, `0` caso contrário. | `has_accepted_answer` |
| **Tratamento de nulos — title** | Títulos nulos são substituídos por string vazia (`""`) na tabela `questions_for_ml`. | `title` |
| **Normalização de tags** | Tags são convertidas para letras minúsculas antes do armazenamento. | `tags.name` |
| **Backoff da API** | Quando a resposta da API contém o campo `backoff`, o coletor aguarda o número de segundos indicado antes da próxima requisição. Não afeta dados, apenas a cadência de coleta. | — |

---

## 12. Uso para Machine Learning

### Variáveis-alvo

| Variável | Tipo | Descrição | Quando usar |
|---|---|---|---|
| `is_answered` | Binário (0/1) | Pergunta tem ao menos uma resposta | **Alvo principal** — maior volume de positivos, mais fácil de balancear |
| `has_accepted_answer` | Binário (0/1) | Pergunta tem resposta aceita pelo autor | Alvo mais exigente; pode ser menos balanceado |

### Features recomendadas para modelos tabulares

| Feature | Tipo | Observação |
|---|---|---|
| `score` | Numérica contínua | Pode ser negativa |
| `view_count` | Numérica contínua | Distribuição assimétrica; considerar log-transform |
| `answer_count` | Numérica discreta | Cuidado com vazamento de dados (leakage) se o alvo for `is_answered` |
| `hour_of_day` | Numérica discreta / cíclica | Encoding cíclico (seno/cosseno) pode melhorar modelos lineares |
| `day_of_week` | Numérica discreta / cíclica | Idem ao anterior |
| `title_length` | Numérica discreta | Simples proxy de qualidade do título |
| `num_tags` | Numérica discreta | Range típico: 1 a 5 (limite do Stack Overflow) |
| `title` | Texto livre | Usar somente em modelos que suportem NLP (TF-IDF, embeddings) |

> **Atenção — vazamento de dados (data leakage):** `answer_count` e `is_answered` são informações capturadas no momento da coleta (não no momento da criação da pergunta). Se o objetivo for prever o desfecho futuro de perguntas novas, essas variáveis devem ser excluídas do conjunto de features, pois já revelam o resultado.

### Balanceamento

Verifique a distribuição do alvo antes de treinar:

```python
import pandas as pd
df = pd.read_csv("data/questions_for_ml.csv")
print(df["has_accepted_answer"].value_counts(normalize=True))
print(df["is_answered"].value_counts(normalize=True))
```

Se desbalanceada, considere:
- Oversampling (SMOTE) ou undersampling
- Pesos de classe (`class_weight='balanced'`)
- Métricas adequadas: F1-score, AUC-ROC (evitar apenas acurácia)
