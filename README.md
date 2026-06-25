# N3 - Séries Temporais do Stack Overflow

**Alunos:** Gabriel de Oliveira e Raniela Lima de Lira

Projeto de modelagem preditiva, avaliação e rastreio de experimentos para prever o volume diário de perguntas do Stack Overflow a partir do dataset já coletado e tratado na etapa N2.

O trabalho transforma registros em nível de pergunta em uma série temporal diária, audita a qualidade dos dados, cria atributos temporais, compara baselines e modelos de famílias diferentes, diagnostica resíduos, registra experimentos no Weights & Biases e gera uma previsão final de 30 dias.

## Case

A base original vem da Stack Exchange API e contém perguntas do Stack Overflow sobre tecnologias monitoradas, como `python`, `reactjs`, `docker` e `vue.js`.

Para esta etapa, a unidade de análise deixa de ser a pergunta individual e passa a ser a série:

```text
daily_questions = quantidade diária de perguntas criadas no Stack Overflow
```

No notebook executado, a série possui 181 dias, de 2025-09-27 a 2026-03-26, e usa como fonte:

```text
stack_overflow_n2/data/questions_for_ml.csv
```

## Objetivos

- Revisar e auditar a série temporal: nulos, duplicatas, gaps, outliers e frequência.
- Criar features temporais com lags, médias móveis, calendário cíclico, fim de semana e tendência.
- Construir baselines de persistência e média móvel.
- Avaliar estacionariedade com ADF/KPSS, ACF/PACF e decomposição da série.
- Treinar modelos SARIMAX, Holt-Winters e ML tabular sequencial.
- Comparar modelos por MAE, RMSE e MAPE.
- Diagnosticar resíduos do modelo campeão com ACF, histograma, Q-Q plot e Ljung-Box.
- Validar a robustez com walk-forward.
- Registrar experimentos no `wandb`.
- Produzir previsão futura de 30 dias com intervalo de confiança.

## Estrutura

```text
stack_for_ml/
|-- README.md
|-- checklist.md
|-- doc.md
|-- requirements.txt
|-- notebooks/
|   `-- 01_n3_stackoverflow_timeseries.ipynb
`-- src/
    |-- __init__.py
    `-- timeseries_utils.py
```

Arquivos principais:

- `notebooks/01_n3_stackoverflow_timeseries.ipynb`: notebook principal da entrega N3.
- `src/timeseries_utils.py`: funções reutilizáveis de carga, agregação, features, métricas, modelos, validação e logs no `wandb`.
- `requirements.txt`: dependências para reproduzir a execução.
- `checklist.md`: checklist dos requisitos da tarefa.
- `doc.md`: enunciado/base de requisitos da atividade.

## Pré-requisitos

- Python 3.12 ou compatível.
- Dataset gerado pela etapa N2 em `stack_overflow_n2/data/questions_for_ml.csv`.
- Ambiente local com Jupyter Notebook.

## Como executar

Na raiz do workspace, crie e ative um ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r stack_for_ml/requirements.txt
```

Abra o notebook:

```bash
jupyter notebook stack_for_ml/notebooks/01_n3_stackoverflow_timeseries.ipynb
```

Execute as células em ordem. O notebook procura automaticamente o arquivo `stack_overflow_n2/data/questions_for_ml.csv` subindo a partir do diretório atual.

## Modelos avaliados

O projeto compara baselines e modelos de famílias diferentes:

| Tipo | Modelo |
| --- | --- |
| Baseline | Persistência, usando o último valor observado |
| Baseline | Média móvel de 7 dias |
| Estatístico | SARIMAX com grid curto e escolha por AIC |
| Suavização | Holt-Winters aditivo com sazonalidade semanal |
| ML tabular | Gradient Boosting com features temporais |
| Checagem de overfitting | Árvore de decisão complexa |

No notebook executado, o modelo campeão pelo menor RMSE de teste foi `gradient_boosting`.

## Métricas principais

As métricas usadas para comparação são:

- `mae_teste`: erro absoluto médio.
- `rmse_teste`: raiz do erro quadrático médio.
- `mape_teste`: erro percentual absoluto médio, quando aplicável.

Leaderboard registrado no notebook:

| Modelo | Família | MAE teste | RMSE teste | MAPE teste |
| --- | --- | ---: | ---: | ---: |
| gradient_boosting | ML | 4.748 | 5.776 | 28.143 |
| baseline_media_movel_7 | baseline | 4.769 | 6.068 | 35.507 |
| decision_tree_complexa | ML_overfitting_check | 5.147 | 6.290 | 33.296 |
| baseline_persistencia | baseline | 5.588 | 7.404 | 37.729 |
| holtwinters_add_weekly | suavização | 6.888 | 8.583 | 35.570 |
| sarimax_(1, 1, 1)_(0, 1, 1, 7) | SARIMAX | 7.406 | 9.011 | 36.954 |

## Weights & Biases

O notebook usa o projeto:

```text
stack-overflow-timeseries-n3
```

Por padrão, a execução define `WANDB_MODE=offline`, permitindo rodar sem credenciais e sem internet. Cada baseline/modelo registra:

- nome do run;
- hiperparâmetros principais;
- métricas de teste;
- tabela de valores reais versus previstos no teste.

Em ambientes em que o serviço interno do `wandb` é bloqueado, o helper salva os dados em:

```text
wandb/offline-fallback-runs/*.json
```

Para sincronizar runs offline em uma máquina configurada:

```bash
wandb login
wandb sync wandb/offline-run-*
```

## Conteúdo do notebook

- Auditoria estrutural da série temporal.
- Diagnóstico de qualidade dos dados.
- Análise exploratória, decomposição e perfil semanal.
- Engenharia de atributos temporais.
- Separação temporal treino/teste sem embaralhamento.
- Baselines e régua de desempenho.
- Testes ADF/KPSS, ACF/PACF e evidências para modelagem.
- SARIMAX com comparação por AIC.
- Holt-Winters.
- Gradient Boosting e checagem de overfitting.
- Leaderboard final por RMSE de teste.
- Diagnóstico dos resíduos do modelo campeão.
- Validação walk-forward com janela inicial e passo semanal.
- Previsão futura de 30 dias com intervalo de confiança.
- Storytelling executivo, conclusões e recomendações.

## Resultados e recomendações

A previsão diária de perguntas ajuda a estimar demanda de moderação, suporte técnico, curadoria de conteúdo e monitoramento de interesse por tecnologias. A série apresenta variação semanal e flutuações naturais de volume, o que justifica o uso de atributos defasados, médias móveis e sazonalidade curta.

Como próximos passos, recomenda-se atualizar a coleta periodicamente, reexecutar o notebook com novas janelas, comparar novamente o leaderboard antes de trocar o modelo campeão e investigar dias extremos antes de remover ou suavizar observações.
