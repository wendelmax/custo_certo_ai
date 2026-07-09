# Especificação de Design - Agente Especialista em Custos Industriais (Custo Certo)

- **Status**: Em Revisão (Pendente Aprovação do Usuário)
- **Data**: 2026-07-09
- **Autor**: Antigravity
- **Tecnologias**: Python, CrewAI (custom_crew), Pandas, Openpyxl, Markdown, Tabulate

---

## 1. Introdução e Objetivos

Este documento especifica o design de um sistema de agentes autônomos especialista em custos fabris. O sistema foi projetado para ler planilhas de dados financeiros e operacionais de uma fábrica, calcular a rentabilidade dos produtos e cruzar esses números com os desvios de processo (refugos e paradas de máquina), gerando um parecer de controladoria estratégico.

### Objetivos Principais:
1. **Calcular Margens de Contribuição e Ponto de Equilíbrio** por produto.
2. **Executar Custeio por Absorção** distribuindo custos indiretos e fixos através de 3 critérios de rateio (Volume, Horas de Máquina Ativas e Custos Diretos).
3. **Avaliar Riscos e Falhas Operacionais** monetizando o impacto de refugos e paradas de máquina.
4. **Gerar Relatórios de Diagnóstico C-Level** recomendando planos de ação para otimização de margens e mitigação de riscos operacionais em formato Markdown e HTML Premium.
5. **Exportar Planilhas Excel Multitab Estilizadas** contendo o Dashboard C-Level, as margens, os comparativos de rateio por absorção e o diagnóstico operacional.

---

## 2. Arquitetura do Sistema e Estrutura de Arquivos

O projeto será implementado em Python com a seguinte estrutura de arquivos dentro da pasta do projeto:

```text
custo_certo/
│
├── data/                             # Arquivos de dados de entrada
│   ├── custos_financeiros.csv        # Cadastro de produtos e dados de custos/vendas
│   └── logs_operacionais.csv         # Logs de produção, refugos e paradas de máquina
│
├── docs/
│   └── superpowers/
│       ├── specs/
│       │   └── 2026-07-09-especialista-custos-design.md  # Este arquivo
│       └── plans/
│           └── 2026-07-09-especialista-custos.md         # Plano de implementação
│
├── src/                              # Código-fonte da aplicação
│   ├── __init__.py
│   ├── agents.py                     # Definição dos agentes CrewAI (papéis, metas)
│   ├── tasks.py                      # Definição das tarefas executadas por cada agente
│   ├── tools.py                      # Ferramentas de cálculo matemático e leitura de dados (Pandas)
│   ├── custom_crew.py                # Orquestrador leve customizado compatível com Python 3.14+
│   ├── exportador.py                 # Módulo de exportação de dados estruturados para Excel (openpyxl)
│   └── crew.py                       # Orquestração da equipe e execução do fluxo sequencial
│
├── main.py                           # Ponto de entrada do script principal
├── converter_relatorio.py            # Conversor do parecer executivo Markdown para HTML Premium
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
| `horas_maquina_ativas` | Decimal | Horas em que a linha de produção esteve rodando ativamente | `20.0` |

---

## 4. Motor de Cálculo (`src/tools.py`)

Para assegurar exatidão matemática absoluta (evitando alucinações numéricas das LLMs), todas as contas estruturadas serão realizadas programaticamente via Pandas nas ferramentas do agente.

### 4.1. Fórmulas de Margem e Ponto de Equilíbrio
*   **Margem de Contribuição Unitária ($MC_u$):**
    $$MC_u = \text{preco\_venda\_unitario} - (\text{custo\_variavel\_unitario} + \text{despesas\_variaveis\_unit})$$
*   **Margem de Contribuição Percentual ($MC_\%$):**
    Se Preço de Venda for maior que zero:
    $$MC_\% = \frac{MC_u}{\text{preco\_venda\_unitario}}$$
*   **Ponto de Equilíbrio Geral ($PE$):**
    Dado que os Custos Fixos totais da empresa são calculados sob a soma da base, o faturamento mínimo de equilíbrio para cobrir a estrutura é determinado por:
    $$PE \text{ (Faturamento)} = \frac{\text{Custos Fixos Totais}}{\text{Margem de Contribuição Média Ponderada}}$$

### 4.2. Fórmulas de Custeio por Absorção (Três Critérios de Rateio)
O sistema consolidará todas as despesas indiretas/fixas adicionais e aplicará as três formas de rateio:
1.  **Rateio por Volume de Produção**:
    $$\text{Custo Indireto Unitário} = \frac{\text{Custos Fixos Totais}}{\text{Quantidade Total Produzida de Todos os Produtos}} \times \text{Participação do Produto}$$
2.  **Rateio por Horas de Máquina Ativas**:
    Calculado com base no tempo de máquina consumido em funcionamento (`horas_maquina_ativas`).
    $$\text{Fator de Rateio} = \frac{\text{Horas Máquina Ativas do Produto}}{\text{Total de Horas Máquina Ativas Consumidas}}$$
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
    *   *Goal*: Consolidar os pareceres financeiro e operacional, comparar as margens sob os 3 critérios de rateio por absorção e propor planos de ação executivos estruturados para C-Level.
    *   *Backstory*: Executivo estratégico focado em tomada de decisão corporativa de alto nível. Conecta causas operacionais com resultados financeiros de forma clara e assertiva.

### 5.2. Tarefas

1.  **Tarefa 1: Análise Matemática de Margens e Rateios**
    *   *Executor*: `Cost Analyst Agent`
    *   *Entregável*: Tabela markdown detalhando Margem de Contribuição (Unitária, % e Total), Ponto de Equilíbrio de cada produto, e Custo Unitário por Absorção sob os 3 métodos de rateio.
2.  **Tarefa 2: Diagnóstico de Eficiência e Desperdiço**
    *   *Executor*: `Process & Risk Auditor Agent`
    *   *Entregável*: Relatório markdown apontando os maiores gargalos de ineficiência, taxas de refugo por lote e custo financeiro absoluto da ineficiência operacional por produto.
3.  **Tarefa 3: Relatório de Diagnóstico Estratégico C-Level**
    *   *Executor*: `Controller Agent`
    *   *Entregável*: Parecer executivo estruturado em Markdown contendo: Resumo Executivo, Destaques Financeiros, Principais Gargalos Operacionais, Análise de Sensibilidade de Rateio de Custos Fixos e 3 Recomendações Críticas para a Diretoria.

---

## 6. Módulos de Exportação e Relatório C-Level

### 6.1. Exportador Excel (`src/exportador.py`)
Gera a planilha `analise_de_custos.xlsx` estruturada em quatro abas usando `openpyxl`:
-   **Dashboard C-Level**: Resumo executivo com fórmulas de soma e média dos principais KPIs financeiros e de desperdício fabril.
-   **Margens e PE**: Tabela formatada contendo preço de venda, custo variável unitário, despesas variáveis unitárias, margem de contribuição (R$ e %) e volume de equilíbrio.
-   **Rateios por Absorção**: Comparação lado a lado dos custos e lucros unitários calculados sob as três opções de rateio.
-   **Ineficiências Chão de Fábrica**: Mapeamento dos lotes operacionais, taxa de refugo e perdas monetárias geradas por desperdício de matéria-prima e paradas de máquina.

### 6.2. Conversor HTML Premium (`converter_relatorio.py`)
Conversor do relatório `relatorio_controladoria.md` em `relatorio_controladoria.html` aplicando estilização moderna e limpa:
-   Layout centralizado responsivo com fontes sans-serif corporativas (`Inter` ou similar).
-   Tabelas de dados com bordas finas, cabeçalhos em azul escuro e linhas com coloração zebra.
-   Resumos de riscos e recomendações destacados com boxes coloridos para leitura executiva rápida (C-Level).

---

## 7. Tratamento de Erros e Validação de Entrada

*   **Validador de Colunas**: Antes de iniciar os cálculos matemáticos, a função `validar_colunas_csv` em `tools.py` verificará se as colunas obrigatórias estão presentes nas planilhas. Caso falte alguma, um `ValueError` amigável listará as colunas ausentes para o usuário.
*   **Dados Ausentes**: Dados de entrada em branco (`NaN`) serão preenchidos defensivamente com `0` e o sistema emitirá um aviso em tempo de execução via módulo `warnings`.
*   **Segurança contra Divisão por Zero**: Todos os divisores em funções matemáticas são validados antes da operação para garantir que o script nunca seja abortado.
