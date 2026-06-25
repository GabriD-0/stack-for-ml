# N3 - Series Temporais do Stack Overflow

Entrega de modelagem preditiva, avaliacao e rastreio de experimentos usando o case ja tratado no projeto `stack_overflow`.

## Case

A base original contem perguntas coletadas da Stack Exchange API para tecnologias monitoradas, com registros em nivel de pergunta. Para a tarefa N3, o dataset e agregado por `creation_date` e a serie temporal alvo passa a ser:

`daily_questions` = quantidade diaria de perguntas criadas no Stack Overflow dentro da janela coletada.

Com a base atual, a serie cobre 181 dias, de 2025-09-27 a 2026-03-26, e usa `stack_overflow/data/questions_for_ml.csv` como fonte.

## Estrutura

```text
stack_for_ml/
├── doc.md
├── README.md
├── requirements.txt
├── checklist.md
├── notebooks/
│   └── 01_n3_stackoverflow_timeseries.ipynb
└── src/
    ├── __init__.py
    └── timeseries_utils.py
```

## Como executar

Na raiz do workspace:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r stack_for_ml/requirements.txt
jupyter notebook stack_for_ml/notebooks/01_n3_stackoverflow_timeseries.ipynb
```

Execute as celulas em ordem. O notebook localiza automaticamente `stack_overflow/data/questions_for_ml.csv` subindo a partir do diretorio atual.

## wandb

O notebook define `WANDB_MODE=offline` por padrao para rodar sem credenciais e sem internet. Cada baseline/modelo abre um run com nome descritivo, hiperparametros, metricas e uma tabela de previsao no teste.

Em ambientes Windows/sandbox que bloqueiam o servico interno do wandb, o helper preserva os mesmos dados em `wandb/offline-fallback-runs/*.json`. Em uma maquina sem essa restricao, os mesmos blocos usam `wandb.init` e `run.log` normalmente.

Para enviar os runs depois:

```bash
wandb login
wandb sync wandb/offline-run-*
```

O projeto usado e `stack-overflow-timeseries-n3`. O leaderboard local aparece no notebook ordenado por RMSE de teste; apos o sync, a mesma comparacao pode ser vista na interface do wandb.

## Conteudo do notebook

- Auditoria estrutural da serie, nulos, duplicatas, gaps e outliers.
- EDA com serie temporal, decomposicao e perfil semanal.
- Engenharia de atributos com lags, medias moveis, calendario ciclico, fim de semana e tendencia.
- Baselines de persistencia e media movel.
- ADF/KPSS, ACF/PACF e tabela de evidencias.
- SARIMAX com grid de AIC, suavizacao exponencial e ML tabular sequencial.
- Checagem simples de overfitting.
- Tabela de metricas, leaderboard e diagnostico de residuos.
- Validacao temporal walk-forward.
- Previsao final de 30 dias com intervalo de confianca.
- Storytelling executivo, conclusoes e recomendacoes.
