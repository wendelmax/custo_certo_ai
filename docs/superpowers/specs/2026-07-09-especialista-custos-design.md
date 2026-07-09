# Especificação de Design - Agente Especialista em Custos Industriais (Custo Certo)

- **Status**: Em Revisão (Pendente Aprovação do Usuário)
- **Data**: 2026-07-09
- **Autor**: Antigravity
- **Tecnologias**: Python, CrewAI, Pandas, Openpyxl

---

## 1. Introdução e Objetivos

Este documento especifica o design de um sistema de agentes autônomos especialista em custos fabris. O sistema foi projetado para ler planilhas de dados financeiros e operacionais de uma fábrica, calcular a rentabilidade dos produtos e cruzar esses números com os desvios de processo (refugos e paradas de máquina), gerando um parecer de controladoria estratégico.

### Objetivos Principais:
1. **Calcular Margens de Contribuição e Ponto de Equilíbrio** por produto.
2. **Executar Custeio por Absorção** distribuindo custos indiretos e fixos através de 3 critérios de rateio (Volume, Horas de Máquina e Custos Diretos).
3. **Avaliar Riscos e Falhas Operacionais** monetizando o impacto de refugos e paradas de máquina.
4. **Gerar Relatórios de Diagnóstico** recomendando planos de ação para otimização de margens e mitigação de riscos operacionais.

---

## 2. Arquitetura do Sistema e Estrutura de Arquivos

O projeto será implementado em Python com a seguinte estrutura de arquivos dentro da pasta do projeto:

```text
custo_certo/
│
├── data/                             # Arquivos de dados de entrada
│   ├── custos_financeiros.csv        # Cadastro de produtos e dados de custos/vendas
│   └── logs_operacionais.csv         # Logs de produção, refugos e paradas
│
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-07-09-especialista-custos-design.md  # Este arquivo
│
├── src/                              # Código-fonte da aplicação
│   ├── __init__.py
│   ├── agents.py                     # Definição dos agentes CrewAI (papéis, metas, LLM)
│   ├── tasks.py                      # Definição das tarefas executadas por cada agente
│   ├── tools.py                      # Ferramentas de cálculo matemático e leitura de dados (Pandas)
│   └── crew.py                       # Orquestração da equipe e execução do fluxo sequencial
│
├── main.py                           # Arquivo de entrada principal
├── requirements.txt                  # Dependências de bibliotecas
└── .env                              # Configuração de chaves de API (ex: GEMINI_API_KEY)
```

---

## 3. Modelagem de Dados (Schemas)

O sistema consumirá dois arquivos no formato CSV como entrada.

### 3.1. `data/custos_financeiros.csv`
Armazena a estrutura de preços, volumes esperados e custos variáveis atribuídos diretamente aos produtos.

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `produto_id` | Texto (Chave) | Identificador exclusivo do produto | `PROD-001` |
| `nome_produto` | Texto | Nome de identificação comercial do item | `Eixo de Aço 50mm` |
| `preco_venda_unitario` | Decimal | Preço de venda líquido unitário praticado | `150.00` |
| `custo_variavel_unitario`| Decimal | Custo de matéria-prima e insumos diretos unitários | `70.00` |
| `despesas_variaveis_unit`| Decimal | Impostos incidentes e comissões por unidade | `15.00` |
| `volume_vendas_mensal` | Inteiro | Quantidade física vendida/planejada no mês | `1000` |

### 3.2. `data/logs_operacionais.csv`
Armazena o registro de ocorrências das ordens de produção ou lotes fabricados no mês.

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `lote_id` | Texto (Chave) | Identificador exclusivo do lote de produção | `LOTE-101` |
| `produto_id` | Texto | Link com o código do produto correspondente | `PROD-001` |
| `quantidade_produzida` | Inteiro | Unidades boas produzidas e aprovadas no lote | `1050` |
| `quantidade_refugada` | Inteiro | Unidades descartadas por defeito ou perda no processo | `50` |
| `horas_maquina_parada` | Decimal | Horas em que a linha de produção ficou inativa por quebras | `3.5` |
| `custo_hora_maquina` | Decimal | Custo de ociosidade/operação por hora de parada da máquina | `200.00` |

---

## 4. Motor de Cálculo (`src/tools.py`)

Para assegurar exatidão matemática absoluta (evitando alucinações numéricas das LLMs), todas as contas estruturadas serão realizadas programaticamente via Pandas nas ferramentas do agente.

### 4.1. Fórmulas de Margem e Ponto de Equilíbrio
*   **Margem de Contribuição Unitária ($MC_u$):**
    $$MC_u = \text{preco\_venda\_unitario} - (\text{custo\_variavel\_unitario} + \text{despesas\_variaveis\_unit})$$
*   **Margem de Contribuição Percentual ($MC_\%$):**
    $$MC_\% = \frac{MC_u}{\text{preco\_venda\_unitario}}$$
*   **Ponto de Equilíbrio Geral ($PE$):**
    Dado que os Custos Fixos totais da empresa (aluguel + salários fixos administrativos + manutenção) são calculados sob a soma da base, o volume de vendas de equilíbrio para cobrir a estrutura é determinado por:
    $$PE \text{ (Faturamento)} = \frac{\text{Custos Fixos Totais}}{\text{Margem de Contribuição Média Ponderada}}$$

### 4.2. Fórmulas de Custeio por Absorção (Três Critérios de Rateio)
O sistema consolidará todas as despesas indiretas/fixas adicionais e aplicará as três formas de rateio:
1.  **Rateio por Volume de Produção**:
    $$\text{Custo Indireto Unitário} = \frac{\text{Custos Fixos Totais}}{\text{Quantidade Total Produzida de Todos os Produtos}} \times \text{Participação do Produto}$$
2.  **Rateio por Horas de Máquina**:
    Calculado com base no tempo de máquina consumido (soma de horas rodadas nos lotes).
    $$\text{Fator de Rateio} = \frac{\text{Horas Máquina do Produto}}{\text{Total de Horas Máquina Consumidas}}$$
3.  **Rateio Proporcional ao Custo Direto**:
    $$\text{Fator de Rateio} = \frac{\text{Custo Direto Total do Produto}}{\text{Custo Direto Total da Fábrica}}$$

### 4.3. Cálculo Financeiro de Perdas e Ineficiências
*   **Custo Financeiro do Refugo ($C_{refugo}$):**
    $$C_{refugo} = \text{quantidade\_refugada} \times \text{custo\_variavel\_unitario}$$
*   **Custo da Parada de Máquina ($C_{parada}$):**
    $$C_{parada} = \text{horas\_maquina\_parada} \times \text{custo\_hora\_maquina}$$
*   **Custo de Ineficiência Total por Produto**: Soma das perdas de refugo e paradas associadas aos lotes daquele item.

---

## 5. Configuração dos Agentes e Tarefas (CrewAI)

O sistema de inteligência artificial é composto por 3 agentes executando 3 tarefas sequenciais.

### 5.1. Agentes

1.  **Analista Financeiro de Custos (`Cost Analyst Agent`)**
    *   *Role*: Especialista em Controladoria Industrial
    *   *Goal*: Calcular com precisão a margem de contribuição e o ponto de equilíbrio de todos os produtos do portfólio.
    *   *Backstory*: Focado em modelagem matemática e auditoria financeira de margens, identifica produtos com baixa lucratividade ou margem negativa.
2.  **Auditor de Processos e Riscos (`Process & Risk Auditor Agent`)**
    *   *Role*: Engenheiro de Produção e Gestor de Riscos Operacionais
    *   *Goal*: Identificar perdas operacionais por refugo, custos de paradas de máquina e mapear gargalos no processo produtivo.
    *   *Backstory*: Especialista em Lean Manufacturing, seu foco é quantificar fisicamente e financeiramente os desperdícios que corroem a margem.
3.  **Diretor de Controladoria (`Controller Agent`)**
    *   *Role*: Diretor Financeiro e de Operações (CFO)
    *   *Goal*: Consolidar os pareceres financeiro e operacional, comparar as margens sob os 3 critérios de rateio por absorção e propor planos de ação executivos.
    *   *Backstory*: Executivo estratégico focado em tomada de decisão corporativa. Conecta causas operacionais com resultados financeiros.

### 5.2. Tarefas

1.  **Tarefa 1: Análise Matemática de Margens e Rateios**
    *   *Executor*: `Cost Analyst Agent`
    *   *Entregável*: Tabela markdown detalhando Margem de Contribuição (Unitária, % e Total), Ponto de Equilíbrio de cada produto, e Custo Unitário por Absorção sob os 3 métodos de rateio (Volume, Horas e Custo Direto).
2.  **Tarefa 2: Diagnóstico de Eficiência e Desperdiço**
    *   *Executor*: `Process & Risk Auditor Agent`
    *   *Entregável*: Relatório markdown apontando os maiores gargalos de ineficiência, taxas de refugo por lote e custo financeiro absoluto da ineficiência operacional por produto.
3.  **Tarefa 3: Relatório de Diagnóstico Estratégico (Consolidado)**
    *   *Executor*: `Controller Agent`
    *   *Entregável*: Relatório executivo final estruturado em Markdown, cruzando desvios operacionais com margens corroídas, avaliando a adequação das margens e oferecendo 3 recomendações claras de melhoria.

---

## 6. Tratamento de Erros e Casos Limite

Para garantir robustez de execução, o motor em Pandas (`tools.py`) tratará os seguintes cenários:
*   **Divisão por Zero**: Se o volume de produção ou horas de máquina forem zero em algum produto para evitar erros matemáticos (`ZeroDivisionError`), o script retornará 0 e emitirá um aviso de "Sem Produção Registrada".
*   **Dados Ausentes (NaN)**: Valores numéricos nulos serão preenchidos com zero automaticamente na importação do arquivo.
*   **Colunas Faltantes**: Antes da execução, um validador verificará se as colunas essenciais especificadas no item 3 estão presentes nas planilhas. Caso falte alguma, a execução será interrompida com um erro amigável ao usuário.

---

## 7. Próximos Passos
Após a aprovação desta especificação pelo usuário, o plano de implementação seguirá as seguintes fases:
1.  **Fase 1**: Criação do diretório de dados e das planilhas de teste (`custos_financeiros.csv` e `logs_operacionais.csv`).
2.  **Fase 2**: Implementação das funções matemáticas e lógicas no arquivo `src/tools.py`.
3.  **Fase 3**: Desenvolvimento da lógica de agentes, backstories, tarefas e orquestração da Crew em `src/agents.py`, `src/tasks.py` e `src/crew.py`.
4.  **Fase 4**: Criação do script de entrada `main.py`, configuração de testes de validação e verificação de resultados.
