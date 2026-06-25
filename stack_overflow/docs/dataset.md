# Documentação do dataset: questions_for_ml

## Fonte dos dados

- **Origem:** Stack Exchange API v2.3, endpoint `/questions`, site `stackoverflow`.
- **Tags utilizadas:** `python`, `reactjs`, `docker`, `vue.js` (uma tag por requisição para maximizar volume).
- **Período:** últimos 6 meses (configurável por `MONTHS` no `.env`, até 12 meses).
- **Armazenamento:** SQLite (`data/stackoverflow.db`). Tabelas: `questions`, `tags`, `question_tags`, `questions_for_ml`.

## Etapas de limpeza e preparação

1. **Remoção de duplicados:** garantida pela chave primária `question_id` no upsert na coleta (uma pergunta pode aparecer em várias tags).
2. **Timestamps:** conversão de Unix para texto no formato `YYYY-MM-DD HH:MM:SS` na ingestão.
3. **Valores ausentes:** `accepted_answer_id` pode ser nulo; definido `has_accepted_answer = 1` quando há resposta aceita, `0` caso contrário.
4. **Normalização de tags:** tags em minúsculas e armazenadas na tabela `tags` com relação N:N em `question_tags`.
5. **Feature engineering:**
   - `hour_of_day`: hora (0–23) da criação da pergunta.
   - `day_of_week`: dia da semana (0–6, domingo=0) da criação.
   - `title_length`: número de caracteres do título.
   - `num_tags`: quantidade de tags associadas à pergunta.
   - `has_accepted_answer`: binário (0/1), alvo sugerido para classificação.

## Variáveis no dataset para ML

O arquivo `data/questions_for_ml.csv` (e a tabela `questions_for_ml`) contêm:

| Campo                  | Tipo    | Descrição                                      |
|------------------------|---------|------------------------------------------------|
| question_id            | int     | ID da pergunta (chave)                         |
| title                  | text    | Título da pergunta                              |
| creation_date          | text    | Data/hora de criação                           |
| last_activity_date     | text    | Última atividade                                |
| score                  | int     | Pontuação (votos)                               |
| view_count             | int     | Número de visualizações                         |
| answer_count           | int     | Número de respostas                             |
| is_answered            | 0/1     | Indica se tem ao menos uma resposta             |
| has_accepted_answer    | 0/1     | **Variável alvo** – indica se tem resposta aceita |
| hour_of_day            | int     | Hora (0–23)                                    |
| day_of_week            | int     | Dia da semana (0–6)                            |
| title_length           | int     | Comprimento do título                           |
| num_tags               | int     | Quantidade de tags                              |

## Uso sugerido para aprendizado de máquina

- **Classificação:** prever `has_accepted_answer` (0/1) a partir das demais variáveis (ex.: score, view_count, answer_count, hour_of_day, day_of_week, title_length, num_tags). Título pode ser usado como texto em modelos que aceitam NLP.
- **Outros alvos possíveis:** `is_answered`, ou regressão para `view_count`, `score`, `answer_count`.

## Variáveis de entrada e saída

- **Entrada:** `score`, `view_count`, `answer_count`, `hour_of_day`, `day_of_week`, `title_length`, `num_tags` (e opcionalmente `title` para modelos de texto).
- **Saída:** `has_accepted_answer` (binário).

## Requisitos para treinamento

- **Volume:** o coletor busca até dezenas de milhares de perguntas (depende da janela e da API). Verifique contagens em `questions` e `questions_for_ml` antes de treinar.
- **Rótulos:** `has_accepted_answer` já está preenchido (0 ou 1) para cada linha.
- **Dados equilibrados:** verificar distribuição de `has_accepted_answer`; se muito desbalanceada, considerar balanceamento (amostragem, pesos ou métricas como F1).