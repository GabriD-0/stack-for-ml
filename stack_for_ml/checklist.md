# Checklist da Tarefa N3

Fonte dos requisitos: `stack_for_ml/doc.md`.

## Entregaveis gerais

- [x] Repositorio organizado para publicacao no GitHub.
- [x] Notebook principal em `stack_for_ml/notebooks/01_n3_stackoverflow_timeseries.ipynb`.
- [x] Codigo organizado e reutilizavel em `stack_for_ml/src/timeseries_utils.py`.
- [x] Dependencias declaradas em `stack_for_ml/requirements.txt`.
- [x] Descricao do case no README e no notebook.
- [x] Checklist preenchido.

## Etapa 1 - Revisao e auditoria da serie temporal

- [x] Conferencia estrutural.
- [x] Dimensao do dataframe bruto e da serie diaria.
- [x] Periodo da serie com data minima e maxima.
- [x] Frequencia inferida com `pd.infer_freq`.
- [x] Nulos por coluna relevante.
- [x] Datas duplicadas no indice temporal.
- [x] Gaps de datas com indice completo e exemplos.
- [x] Outliers por IQR.
- [x] Acao definida para outliers.
- [x] Tratamento de ausentes e justificativa para nao preencher indevidamente com zero.
- [x] Tabela "Diagnostico de Qualidade de Dados".
- [x] Paragrafos sobre impacto na modelagem.

## Etapa 2 - Engenharia de atributos

- [x] Lags autorregressivos: `lag1`, `lag7`, `lag14`.
- [x] Medias moveis: `rolling7`, `rolling14`.
- [x] Encoding ciclico: `dow_sin`, `dow_cos`, `month_sin`, `month_cos`.
- [x] Flag de fim de semana e tendencia temporal.
- [x] Tabela de hipoteses das features.
- [x] `dropna()` apos criacao das features.
- [x] Separacao treino/teste temporal aproximada 80/20 sem embaralhar.

## Etapa 3 - Baselines e regua de desempenho

- [x] Baseline de persistencia.
- [x] Baseline de media movel.
- [x] MAE e RMSE para baselines.
- [x] Tabela comparativa de regua de desempenho.

## Etapa 4 - Estacionariedade, ACF/PACF e evidencias

- [x] Teste ADF na serie original.
- [x] Teste KPSS quando possivel.
- [x] Diferenciacao e novo ADF quando necessario.
- [x] Graficos ACF e PACF.
- [x] Comentario para sugerir termos curtos de AR/MA e sazonalidade semanal.
- [x] Tabela de evidencias EDA/modelagem.
- [x] Grafico da serie no tempo.
- [x] Decomposicao em tendencia, sazonalidade e residuo.

## Etapa 5 - Modelagem preditiva

- [x] Modelo ARIMA/SARIMA/SARIMAX via `statsmodels`.
- [x] Modelo de suavizacao exponencial Holt-Winters ou Holt.
- [x] Modelo moderno/ML tabular sequencial com features derivadas.
- [x] Minimo de 3 familias diferentes de modelos.

## Etapa 6 - Hiperparametros, AIC e overfitting

- [x] Grid curto de ordens SARIMAX.
- [x] Tabela de AIC por especificacao.
- [x] Escolha da especificacao final pelo menor AIC valido.
- [x] Exemplo de aumento de complexidade com ML.
- [x] Comparacao treino versus teste para discutir overfitting.

## Etapa 7 - Avaliacao, comparacao e diagnostico de residuos

- [x] MAE, RMSE e MAPE para baselines e modelos.
- [x] Tabela com Baseline 1, Baseline 2, Modelo 1, Modelo 2 e Modelo 3.
- [x] Escolha automatica do modelo campeao por RMSE de teste.
- [x] Grafico dos residuos no tempo.
- [x] ACF dos residuos.
- [x] Histograma dos residuos.
- [x] Q-Q plot.
- [x] Teste Ljung-Box.
- [x] Indicacao de refinamento quando houver autocorrelacao residual.

## Etapa 8 - Validacao temporal walk-forward

- [x] Validacao walk-forward implementada.
- [x] Janela inicial de aproximadamente 120 observacoes.
- [x] Passo de 7 dias.
- [x] Comparacao por MAE/RMSE media.
- [x] Comentario sobre custo computacional versus robustez.

## Etapa 9 - Previsao final e storytelling

- [x] Horizonte futuro de 30 dias.
- [x] Intervalos de confianca de 95%.
- [x] Grafico com historico, previsao futura e bandas.
- [x] Contexto executivo.
- [x] Descobertas esperadas.
- [x] Acoes/recomendacoes para tomada de decisao.

## Etapa 10 - Weights & Biases

- [x] Projeto `stack-overflow-timeseries-n3`.
- [x] `wandb.init` via helper `log_wandb_run`.
- [x] Runs para baselines e modelos.
- [x] Hiperparametros principais registrados.
- [x] Metricas de teste registradas.
- [x] Tabela real versus previsto registrada no wandb.
- [x] Modo offline por padrao para reprodutibilidade local.
- [x] Fallback local em JSON quando o sandbox bloqueia o servico interno do wandb.
- [x] Instrucoes de `wandb sync` no README.
- [x] Leaderboard local no notebook.
- [x] Secao de rastreio de experimentos no notebook/README.

## Observacoes

- [x] O workspace local atual nao esta inicializado como repositorio Git; a estrutura foi preparada para publicacao.
- [x] A execucao completa depende da instalacao das dependencias de `stack_for_ml/requirements.txt`.
