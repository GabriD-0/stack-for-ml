Use o mesmo case de séries temporais do projeto stack_overflow, já tratado e explorado. A partir dele, siga as etapas do documento da tarefa.

Entregáveis
Repositório GitHub

Notebook(s) com:

Auditoria e EDA.

Engenharia de atributos.

Baselines.

Modelos (ARIMA/ARIMAX/SARIMAX, suavização, moderno/ML).

Diagnóstico de resíduos.

Previsão final.

Integração com wandb (init, log, etc.)

Código organizado, comentado e reprodutível

Descrição do case.

Tabela de evidências EDA/modelagem.

Tabela de métricas (baselines e modelos).

Gráficos principais (série, decomposição, previsão, resíduos).

Leaderboard do wandb.

Conclusões e recomendações.




---


N3 - Modelagem Preditiva, Avaliação e Rastreio de Experimentos
Use o mesmo case de séries temporais do projeto stack_overflow, já tratado e explorado. A partir dele, siga as etapas.
Etapa 1 – Revisão e auditoria da série temporal
    1. Conferência estrutural
    2. Dimensão do dataframe (linhas, colunas).
    • Período da série (data mínima → data máxima).
    • Frequência inferida (ex.: diária, horária, via pd.infer_freq).
    3. Qualidade do índice temporal
    • Nulos por coluna.
    • Datas duplicadas no índice.
    • Gaps de datas: crie um índice completo no intervalo, conte quantas datas faltam e mostre alguns exemplos.
    4. Outliers
    • Detecte outliers (ex.: IQR 1.5×IQR).
    • Informe quantidade por coluna e o que fará com eles (manter, tratar, suavizar).
    5. Imputação
    • Explique como lidou com valores ausentes (ex.: interpolação).
    • Justifique por que não preenche com zero quando isso distorce o fenômeno.
Entrega mínima:
Tabela “Diagnóstico de Qualidade de Dados” (nulos, duplicatas, gaps, outliers).
1–2 parágrafos sobre impacto desses problemas na modelagem.
Etapa 2 – Engenharia de atributos 
    1. Lags autorregressivos: Ex.: lag1, lag2 da variável-alvo.
    2. Médias móveis: Ex.: mm7 = média móvel de 7 dias (ou janela adequada).
    3. Encoding cíclico: Converter mês, dia da semana, hora etc. em seno/cosseno (mes_sin, mes_cos, dia_sem_sin, dia_sem_cos) para respeitar a natureza cíclica.
    4. Tabela de hipóteses das features: Ex.: lag1 – hoje depende do valor de ontem; mm7 – captura tendência de curto prazo; mes_sin/mes_cos – modelam sazonalidade anual de forma contínua.
    5. Dataset final: use dropna() para remover linhas iniciais inválidas; Separe em treino (≈80%) e teste (≈20%), sem embaralhar.
Etapa 3 – Baselines e régua de desempenho
Construa duas referências de desempenho: baseline 1 – Persistência (Naïve) e baseline 2 – Média móvel. Calcule MAE e RMSE para cada baseline e monte uma pequena tabela comparativa. Essa tabela será a sua “régua de desempenho”.
Etapa 4 – Estacionariedade, ACF/PACF e evidências
    1. Teste ADF (e, se conveniente, KPSS)
    • Aplique ADF na série (ou série transformada).
    • Interprete o p-valor e diga se a série pode ser considerada estacionária.
    • Se não for estacionária, mostre uma diferenciação e reavalie.
    2. ACF e PACF
Plote e comente os gráficos da série estacionária (original ou diferenciada).
Use os padrões para sugerir valores de p e q.
    3. Tabela de evidências no relatório
    • Gráfico da série no tempo.
    • Decomposição (tendência + sazonalidade + resíduo).
    • Resultado do ADF (p-valor + frase de interpretação).
    • Gráficos ACF/PACF.
Etapa 5 – Modelagem preditiva (mínimo 3 modelos)
Implemente no mínimo 3 modelos de famílias diferentes:
    • Modelo 1 – ARIMA/ARIMAX ou SARIMA/SARIMAX: pode ser univariado ou com exógenas (ARIMAX/SARIMAX). Ordem escolhida manualmente (ACF/PACF) ou com auto_arima, sempre com diagnóstico depois.
    • Modelo 2 – Suavização exponencial: SES, Holt ou Holt-Winters, coerente com presença/ausência de tendência e sazonalidade.
    • Modelo 3 – ML: Prophet, LSTM ou outro apresentado nos seminários. Use features derivadas (lags, encoding cíclico) quando fizer sentido.
Etapa 6 – Hiperparâmetros, AIC e overfitting
    1. AIC para ARIMA/ARIMAX/SARIMA: Teste algumas combinações de (p, d, q) (e P, D, Q se sazonal). Registre o AIC de cada uma em uma tabela e escolha a especificação final, justificando.
    2. Overfitting: mostre um exemplo simples em que aumentar a complexidade (ex.: muitos lags) melhora o treino e piora o teste. Escreva um parágrafo com suas conclusões sobre overfitting.
Etapa 7 – Avaliação, comparação e diagnóstico de resíduos
    1. Métricas no teste: Para baselines e modelos, calcule pelo menos: MAE, RMSE, MAPE (quando fizer sentido). Monte uma tabela com: Baseline 1, Baseline 2, Modelo 1, Modelo 2, Modelo 3.
    2. Modelo campeão: Escolha um modelo principal. Justifique pela combinação de métricas, interpretabilidade e adequação ao problema.
    3. Diagnóstico de resíduos do campeão: Gráfico dos resíduos no tempo. ACF dos resíduos. Histograma + Q-Q plot. Teste de Ljung-Box (p-valor + interpretação se é ruído branco).
    4. Refinamento (se necessário): Se houver padrão/autocorrelação nos resíduos, descreva ao menos uma tentativa de ajuste (mudar p/q, incluir sazonalidade).
Etapa 8 – Validação temporal (walk-forward)
Implemente uma validação walk-forward (janela deslizante). Defina janela de treino (em observações/dias) e passo (ex.: re-treinar a cada 7 dias). Compare RMSE/MAE do walk-forward com: baselines, ARIMA/ARIMAX/SARIMA com ajuste único e comente o trade-off entre custo computacional e robustez.
Etapa 9 – Previsão final e storytelling
    1. Previsão futura
Gere previsões para um horizonte definido (ex.: 7, 14 ou 30 passos).
Inclua intervalos de confiança (ex.: 95%).
Gráfico com:
    • Histórico (treino + teste).
    • Previsões futuras.
    • Bandas de intervalo.
    2. Storytelling executivo
    • Contexto: que problema de negócio/prático a previsão ajuda a responder?
    • Descobertas: tendência, sazonalidade, efeitos exógenos.
    • Ações: que decisões podem ser tomadas (capacidade, estoque, investimento etc.).
    • Linguagem simples, focada em quem toma decisão.
Etapa 10 – Uso do Weights & Biases (wandb)
Use wandb para rastrear os experimentos.
    1. Configuração e projeto
Crie um projeto específico no wandb para o grupo.
    2. Runs de experimentos
Para cada modelo relevante (incluindo baselines), crie um run com:
    • Nome descritivo (ex.: baseline_persistencia, arimax_2_0_2, holtwinters_add, prophet_default).
    • Hiperparâmetros principais (p, d, q, P, D, Q, sazonalidade, horizonte, etc.).
    • Métricas de teste (mae_teste, rmse_teste, mape_teste).
    3. Gráficos
Logue: Série real vs previsão no teste, ou previsão futura com intervalo de confiança.
    4. Leaderboard
Use a interface do wandb para ordenar os runs por uma métrica (ex.: RMSE de teste).
No relatório, inclua:
    • Print/tabela com os principais runs.
    • 1 parágrafo explicando qual modelo foi escolhido como campeão e por quê, com base no wandb.
    5. Seção “Rastreio de Experimentos com wandb” no relatório
    • Nome do projeto e, se possível, link.
    • Resumo de 2–3 runs principais (hiperparâmetros + métricas).
    • Comentário sobre como o wandb ajudou em organização e comparação.
Entregáveis
Repositório GitHub, notebook(s) com:
    • Auditoria e EDA.
    • Engenharia de atributos.
    • Baselines.
    • Modelos (ARIMA/ARIMAX/SARIMAX, suavização, moderno/ML).
    • Diagnóstico de resíduos.
    • Previsão final.
    • Integração com wandb (init, log, etc.)
    • Código organizado, comentado e reprodutível
    • Descrição do case.
    • Tabela de evidências EDA/modelagem.
    • Tabela de métricas (baselines e modelos).
    • Gráficos principais (série, decomposição, previsão, resíduos).
    • Leaderboard do wandb.
    • Conclusões e recomendações.

Critério	Descrição	Peso
Preparação dos dados e features	Auditoria final, lags, médias móveis, encoding cíclico, hipóteses claras	20%
EDA, estacionariedade e escolha de modelos	Decomposição, ADF, ACF/PACF e AIC bem interpretados	20%
Implementação de modelos	≥3 modelos de famílias diferentes, bem configurados	25%
Avaliação e diagnóstico de resíduos	Comparação com baselines, métricas, Ljung-Box, análise do campeão	25%
Uso do Weights & Biases	Runs nomeados, métricas e gráficos logados, leaderboard usado na decisão, seção no relatório	10%
		
