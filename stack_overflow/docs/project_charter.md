Project Charter — Stack Overflow para ML
Nome do Grupo
Gabriel de Oliveira &
Raniel Lima de Lira 
Nome do projeto
Coleta e preparação de dados do Stack Overflow para Machine Learning
Versão do documento
1.4
Data
26/03/2026



1. Sumário executivo
Este projeto define a coleta automatizada de perguntas do Stack Overflow via Stack Exchange API, o armazenamento em banco relacional, a transformação em features e a exportação de um dataset tabular pronto para treino de modelos. O foco principal é suportar classificação binária para prever se uma pergunta será respondida (pelo menos uma resposta), representada por is_answered, com possibilidade de extensão a outros alvos (ex.: has_accepted_answer, score, view_count).


2. Propósito e justificativa
Propósito: Disponibilizar um pipeline reprodutível (coleta → persistência → ETL → CSV) que respeite limites da API e garanta dados limpos e documentados para experimentação em ML.

Justificativa: Perguntas em comunidades técnicas exibem padrões temporais e de engajamento (visualizações, votos, tags) que podem ser estudados com modelos supervisionados. Uma base consistente reduz retrabalho e permite comparar modelos de forma justa.


3. Objetivos
Tipo
Objetivo
Principal
Coletar e preparar dados temporais da Stack Exchange API para prever, via ML, se uma pergunta será respondida (is_answered), em tecnologias populares (tags definidas).
Secundários
Documentar o dataset (docs/dataset.md); manter scripts executáveis (collector, transform); permitir janela temporal configurável (MONTHS).


Resultados mensuráveis sugeridos:

Dataset exportado (data/questions_for_ml.csv) com schema documentado e sem duplicatas lógicas por question_id.
Pipeline executável conforme README.md (ambiente Python 3.12+).


4. Escopo
4.1 Dentro do escopo
Coleta via endpoint /questions (API v2.3, site stackoverflow) para as tags: python, reactjs, docker, vue.js, etc.
Filtro temporal dos últimos 6 a 12 meses (Será alterado conforme desempenho).
Armazenamento estruturado em SQLite (data/stackoverflow.db), com tabelas: questions, tags, question_tags e questions_for_ml.
Tratamento: timestamps, remoção de duplicidade por question_id na ingestão (upsert), feature engineering (hour_of_day, day_of_week, title_length, num_tags).
Exportação do arquivo data/questions_for_ml.csv para treino.
4.2 Fora do escopo
Análise de sentimento do corpo das perguntas ou de comentários.
Coleta sistemática de perfis de usuários individuais.
Implementação obrigatória de modelos de deep learning (o escopo atual é dados e preparação; modelagem pode ser etapa futura).
Hospedagem em produção, API REST do próprio projeto ou dashboard de monitoramento contínuo.


5. Partes interessadas e papéis
Integrantes: Raniel Lira e Gabriel de Oliveira — ambos atuam de forma integrada em todas as frentes do projeto (as funções abaixo são compartilhadas).

Papel
Responsabilidade típica
Responsável pelo projeto
Definir prioridades, validar entregáveis e critérios de sucesso.
Executor técnico
Desenvolver e manter coletor, schema, transformação e documentação.
Usuário do dataset
Consumir questions_for_ml.csv / tabela homônima para treino e avaliação de modelos.



6. Entregáveis
Entregável
Descrição
Repositório com código
Scripts src/collector.py, src/transform.py, src/db.py, src/config.py; schema/init.sql; scripts/init_db.py.
Banco SQLite
data/stackoverflow.db (gerado localmente; pode não versionar o binário).
Dataset para ML
data/questions_for_ml.csv e tabela questions_for_ml.
Documentação
README.md (uso e configuração), docs/dataset.md (variáveis e limpeza), este project charter.



7. Critérios de sucesso
É possível, a partir de um ambiente limpo, seguir o README e obter o CSV com o schema descrito em docs/dataset.md.
A coleta respeita a cota e backoff da API.
O escopo de tags e janela temporal está explícito e alinhado à implementação.


8. Premissas e dependências
Python 3.12 ou superior; dependências em requirements.txt.
Acesso à internet para a Stack Exchange API.
Opcional: STACK_API_KEY no .env para cota diária ampliada (sem chave: limite de requisições/dia conforme política da API).
Variáveis de ambiente: SQLITE_DB_PATH, STACK_API_KEY


9. Restrições
Limites e políticas da Stack Exchange API.
Dados públicos expostos pela API; não há garantia de cobertura completa de todas as perguntas do site.
Escopo temporal e de tags delimitam a generalização de qualquer modelo treinado neste dataset.


10. Riscos e mitigação
Risco
Impacto
Mitigação
Esgotamento da cota da API
Coleta incompleta
Coleta por tag, paginação com pausas, uso de chave quando necessário, janela MONTHS ajustável.
backoff da API
Atraso na coleta
Aguardar o tempo indicado pela API antes da próxima requisição.
Pergunta em múltiplas tags
Duplicidade lógica
Upsert por question_id na persistência.
Desvio doc × código
Expectativas incorretas
Charter e dataset.md alinhados ao repositório (ex.: SQLite, não PostgreSQL).



11. Arquitetura da solução
11.1 Visão geral (camadas e fluxo de dados)


Fluxo resumido: a API fornece JSON de perguntas; o coletor normaliza e persiste via db; o transform lê questions (+ tags), grava questions_for_ml e exporta o CSV. Configuração centralizada em config.py + variáveis de ambiente (.env).
11.2 Componentes e responsabilidades
Componente
Função
src/config.py
Tags, janela temporal (MONTHS), URLs da API, caminho do SQLite, chave opcional.
src/collector.py
Requisições paginadas por tag, tratamento de cota/backoff, chamada à camada de persistência.
src/db.py
Conexão SQLite, upsert de perguntas e relação pergunta–tag (evita duplicar question_id).
schema/init.sql
DDL: tabelas questions, tags, question_tags, questions_for_ml e índices.
scripts/init_db.py
Aplica o schema sem coletar (inicialização do banco).
src/transform.py
ETL: preenche questions_for_ml, calcula features derivadas, exporta CSV.

11.3 Modelo de dados (lógico)
Tabela
Papel
questions
Uma linha por question_id; campos da API (título, datas, scores, is_answered, has_accepted_answer, etc.).
tags
Catálogo de tags (normalizadas).
question_tags
Associação N:N entre pergunta e tag.
questions_for_ml
Visão “flat” para ML: colunas da pergunta + features (hour_of_day, day_of_week, title_length, num_tags).

11.4 Pontos de execução
python scripts/init_db.py — cria/atualiza schema.
python -m src.collector — ingestão incremental/atualização a partir da API.
python -m src.transform — materializa questions_for_ml e gera data/questions_for_ml.csv.
11.5 Tipos de dados por pergunta (domínio)
Quantitativos: view_count, score, answer_count.
Temporais: creation_date, last_activity_date (Unix na API; convertidos no pipeline).
Categóricos / binários: tags (N:N), is_answered (alvo principal sugerido), has_accepted_answer (campo auxiliar).
11.6 Modelagem de ML sugerida (fases futuras)
Classificação: prever is_answered (ao menos uma resposta).
Regressão (opcional): view_count ou score.
Classificação alternativa: has_accepted_answer, se o foco for resposta aceita.


12. Marcos e estimativa de esforço
Estimativas indicativas para o recorte do projeto:

Marco
Atividades principais
Tempo estimado
Configuração e coleta
Setup da API, scripts de requisição, limites e backoff
12–16 h
Modelagem do banco
Schema SQLite, integração com coletor
6–8 h
Tratamento e ETL
Limpeza, datas, features, export CSV
10–14 h
Análise exploratória
Tendências temporais, correlações (opcional para o curso)
8–10 h


Total indicativo: ~36–48 h (varia com familiaridade com a API e com Python).


13. Aprovação e governança
Alterações relevantes de escopo (tags, período, alvo de ML, stack de armazenamento) devem ser refletidas neste charter e em docs/dataset.md / README.md.
Versão do documento incrementada quando houver mudança de escopo ou de arquitetura acordada.


14. Referências
Stack Exchange API 2.3 — endpoint /questions, site stackoverflow.
Documentação interna: README.md, docs/dataset.md.

