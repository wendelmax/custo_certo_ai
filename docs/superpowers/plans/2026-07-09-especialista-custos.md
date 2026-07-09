# Especialista em Custos Industriais - Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir um sistema de agentes autônomos baseados em CrewAI que consome planilhas financeiras e operacionais de uma fábrica, calcula margens, ponto de equilíbrio, custeio por absorção (3 critérios) e perdas operacionais, gerando um diagnóstico estratégico em Markdown.

**Architecture:** O sistema é estruturado de forma desacoplada: um motor matemático e de dados puro (`src/tools.py`) que usa Pandas para ler planilhas e efetuar cálculos exatos, e uma equipe CrewAI sequencial composta por 3 agentes (`src/agents.py` e `src/tasks.py`) que consomem os outputs dessas ferramentas para gerar insights e o relatório executivo final.

**Tech Stack:** Python 3.10+, CrewAI, Pandas, Openpyxl, Pytest (para testes de unidade e integração), Git.

## Global Constraints
- Nenhuma fórmula financeira ou de rateio deve ser calculada diretamente pela LLM (evitar alucinações). Todas devem ser executadas em Python puro via `src/tools.py`.
- O código deve lidar com dados ausentes ou vazios preenchendo-os com zero ou emitindo avisos sem quebrar o fluxo.
- Todo código de cálculo e lógica deve possuir testes unitários correspondentes no diretório `tests/`.

---

### Task 1: Scaffolding e Configuração de Ambiente

**Files:**
- Create: `requirements.txt`
- Create: `data/custos_financeiros.csv`
- Create: `data/logs_operacionais.csv`
- Create: `tests/test_scaffolding.py`

**Interfaces:**
- Consumes: Nenhuma.
- Produces: Planilhas estruturadas na pasta `data/` prontas para leitura e ambiente Python pronto com dependências instaladas.

- [ ] **Step 1: Criar o arquivo `requirements.txt`**
  Escrever as dependências necessárias no arquivo.
  ```text
  crewai>=0.28.0
  pandas>=2.0.0
  openpyxl>=3.1.0
  python-dotenv>=1.0.0
  pytest>=7.0.0
  ```

- [ ] **Step 2: Criar as planilhas de dados fictícios para teste**
  Criar `data/custos_financeiros.csv` com dados base de produtos.
  ```csv
  produto_id,nome_produto,preco_venda_unitario,custo_variavel_unitario,despesas_variaveis_unit,volume_vendas_mensal
  PROD-001,Eixo de Aco 50mm,150.00,70.00,15.00,1000
  PROD-002,Flange de Ferro,80.00,45.00,8.00,1500
  PROD-003,Suporte Especial,200.00,120.00,20.00,500
  ```
  Criar `data/logs_operacionais.csv` com dados operacionais básicos.
  ```csv
  lote_id,produto_id,quantidade_produzida,quantidade_refugada,horas_maquina_parada,custo_hora_maquina
  LOTE-101,PROD-001,1000,50,4.0,150.00
  LOTE-102,PROD-002,1500,20,2.5,100.00
  LOTE-103,PROD-003,500,80,6.0,200.00
  ```

- [ ] **Step 3: Escrever o teste unitário de scaffold**
  Escrever em `tests/test_scaffolding.py` a verificação de existência e integridade dos arquivos de entrada.
  ```python
  import os
  import pandas as pd

  def test_files_exist():
      assert os.path.exists("data/custos_financeiros.csv")
      assert os.path.exists("data/logs_operacionais.csv")

  def test_load_csv_files():
      cf_df = pd.read_csv("data/custos_financeiros.csv")
      lo_df = pd.read_csv("data/logs_operacionais.csv")
      
      assert "produto_id" in cf_df.columns
      assert "produto_id" in lo_df.columns
      assert len(cf_df) == 3
      assert len(lo_df) == 3
  ```

- [ ] **Step 4: Executar o teste e certificar-se que falha**
  Executar: `pytest tests/test_scaffolding.py`
  Expected: Falha (se as dependências ainda não estiverem instaladas ou se os arquivos não forem localizados).

- [ ] **Step 5: Instalar dependências e validar se os testes passam**
  Executar instalação: `pip install -r requirements.txt` (pode ser executado pelo ambiente).
  Executar teste: `pytest tests/test_scaffolding.py -v`
  Expected: PASS

- [ ] **Step 6: Realizar commit**
  ```bash
  git add requirements.txt data/ tests/test_scaffolding.py
  git commit -m "chore: setup dependencies and sample datasets"
  ```

---

### Task 2: Motor de Cálculo - Margens e Ponto de Equilíbrio (`src/tools.py`)

**Files:**
- Create: `src/tools.py`
- Create: `tests/test_tools.py`

**Interfaces:**
- Consumes: Dados de `data/custos_financeiros.csv`.
- Produces: Função `calcular_margem_contribuicao(caminho_csv: str) -> pd.DataFrame` e `calcular_ponto_equilibrio(caminho_csv: str, custos_fixos: float) -> dict`.

- [ ] **Step 1: Escrever teste de falha em `tests/test_tools.py`**
  Escrever testes para o cálculo de margem e ponto de equilíbrio.
  ```python
  import pytest
  import pandas as pd
  import sys
  import os

  # Adiciona src ao path
  sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

  def test_calcular_margem_contribuicao():
      from tools import calcular_margem_contribuicao
      df = calcular_margem_contribuicao("data/custos_financeiros.csv")
      
      # Verificações de dados de teste para PROD-001
      # Preço: 150, Custo Var: 70, Desp Var: 15. MC_u = 150 - 70 - 15 = 65.
      prod_1 = df[df["produto_id"] == "PROD-001"].iloc[0]
      assert prod_1["margem_contribuição_unitaria"] == 65.0
      assert prod_1["margem_contribuição_percentual"] == (65.0 / 150.0)

  def test_calcular_ponto_equilibrio():
      from tools import calcular_ponto_equilibrio
      # Custos fixos totais de teste = 50000.00
      pe = calcular_ponto_equilibrio("data/custos_financeiros.csv", 50000.00)
      assert pe["faturamento_equilibrio_geral"] > 0
  ```

- [ ] **Step 2: Executar teste e validar que falha**
  Executar: `pytest tests/test_tools.py::test_calcular_margem_contribuicao`
  Expected: FAIL (ModuleNotFoundError ou NameError)

- [ ] **Step 3: Escrever implementação mínima no arquivo `src/tools.py`**
  Implementar a função de cálculo de margem e ponto de equilíbrio.
  ```python
  import pandas as pd

  def calcular_margem_contribuicao(caminho_csv: str) -> pd.DataFrame:
      df = pd.read_csv(caminho_csv)
      df["preco_venda_unitario"] = df["preco_venda_unitario"].astype(float)
      df["custo_variavel_unitario"] = df["custo_variavel_unitario"].astype(float)
      df["despesas_variaveis_unit"] = df["despesas_variaveis_unit"].astype(float)
      df["volume_vendas_mensal"] = df["volume_vendas_mensal"].astype(int)
      
      df["margem_contribuição_unitaria"] = df["preco_venda_unitario"] - (df["custo_variavel_unitario"] + df["despesas_variaveis_unit"])
      df["margem_contribuição_percentual"] = df["margem_contribuição_unitaria"] / df["preco_venda_unitario"]
      df["margem_contribuição_total"] = df["margem_contribuição_unitaria"] * df["volume_vendas_mensal"]
      return df

  def calcular_ponto_equilibrio(caminho_csv: str, custos_fixos: float) -> dict:
      df = calcular_margem_contribuicao(caminho_csv)
      
      # Ponto de equilíbrio usando margem de contribuição média ponderada baseada no faturamento
      df["faturamento_total"] = df["preco_venda_unitario"] * df["volume_vendas_mensal"]
      faturamento_total_carteira = df["faturamento_total"].sum()
      
      if faturamento_total_carteira == 0:
          return {"faturamento_equilibrio_geral": 0.0, "mensagem": "Volume de faturamento zerado."}
          
      df["peso_faturamento"] = df["faturamento_total"] / faturamento_total_carteira
      margem_ponderada = (df["margem_contribuição_percentual"] * df["peso_faturamento"]).sum()
      
      faturamento_equilibrio = custos_fixos / margem_ponderada if margem_ponderada > 0 else 0.0
      
      return {
          "faturamento_equilibrio_geral": faturamento_equilibrio,
          "margem_contribuição_media_ponderada": margem_ponderada,
          "faturamento_atual_total": faturamento_total_carteira
      }
  ```

- [ ] **Step 4: Executar testes para verificar que passam**
  Executar: `pytest tests/test_tools.py -v`
  Expected: PASS

- [ ] **Step 5: Realizar commit**
  ```bash
  git add src/tools.py tests/test_tools.py
  git commit -m "feat: implement margin and breakeven functions in tools.py"
  ```

---

### Task 3: Motor de Cálculo - Absorção e Perdas (`src/tools.py`)

**Files:**
- Modify: `src/tools.py`
- Modify: `tests/test_tools.py`

**Interfaces:**
- Consumes: Arquivos `data/custos_financeiros.csv` e `data/logs_operacionais.csv`.
- Produces: Funções em `src/tools.py`:
  - `calcular_custeio_absorcao(caminho_fin: str, caminho_op: str, custos_fixos: float, criterio: str) -> pd.DataFrame`
  - `analisar_desperdicios_eficiencia(caminho_op: str, caminho_fin: str) -> pd.DataFrame`

- [ ] **Step 1: Escrever testes unitários em `tests/test_tools.py`**
  Adicionar testes para absorção e análise de perdas operacionais no final do arquivo de testes existente.
  ```python
  def test_calcular_custeio_absorcao():
      from tools import calcular_custeio_absorcao
      # Custo fixo = 12000.00
      # Critério volume
      df_vol = calcular_custeio_absorcao(
          "data/custos_financeiros.csv", 
          "data/logs_operacionais.csv", 
          12000.00, 
          "volume"
      )
      assert "custo_absorcao_unitario" in df_vol.columns
      assert len(df_vol) == 3

  def test_analisar_desperdicios_eficiencia():
      from tools import analisar_desperdicios_eficiencia
      df = analisar_desperdicios_eficiencia(
          "data/logs_operacionais.csv",
          "data/custos_financeiros.csv"
      )
      # Lote 101 produziu 1000, refugou 50. Custo MP/Unit = 70.
      # Custo Refugo = 50 * 70 = 3500.
      # Horas paradas = 4.0, custo hora = 150. Custo parada = 4.0 * 150 = 600.
      # Custo ineficiencia total = 4100.
      lote_101 = df[df["lote_id"] == "LOTE-101"].iloc[0]
      assert lote_101["custo_refugo"] == 3500.0
      assert lote_101["custo_parada_maquina"] == 600.0
      assert lote_101["perda_ineficiencia_total"] == 4100.0
  ```

- [ ] **Step 2: Executar testes e verificar que falham**
  Executar: `pytest tests/test_tools.py::test_calcular_custeio_absorcao -v`
  Expected: FAIL (ImportError ou NameError)

- [ ] **Step 3: Implementar métodos de absorção e perdas no `src/tools.py`**
  Adicionar as implementações abaixo ao arquivo `src/tools.py`.
  ```python
  def calcular_custeio_absorcao(caminho_fin: str, caminho_op: str, custos_fixos: float, criterio: str) -> pd.DataFrame:
      fin_df = pd.read_csv(caminho_fin)
      op_df = pd.read_csv(caminho_op)
      
      # Consolidar produções por produto
      producao_total = op_df.groupby("produto_id")["quantidade_produzida"].sum().reset_index()
      horas_maquina = op_df.groupby("produto_id")["horas_maquina_parada"].sum().reset_index() # para horas de máquina
      
      df = pd.merge(fin_df, producao_total, on="produto_id", how="left").fillna(0)
      df = pd.merge(df, horas_maquina, on="produto_id", how="left").fillna(0)
      
      total_produzido_todos = df["quantidade_produzida"].sum()
      total_custo_direto_carteira = (df["custo_variavel_unitario"] * df["quantidade_produzida"]).sum()
      total_horas_maquina = df["horas_maquina_parada"].sum()
      
      # Cálculo do fator de rateio
      if criterio == "volume":
          if total_produzido_todos == 0:
              df["rateio_custo_fixo"] = 0.0
          else:
              df["rateio_custo_fixo"] = (df["quantidade_produzida"] / total_produzido_todos) * custos_fixos
      elif criterio == "horas_maquina":
          if total_horas_maquina == 0:
              df["rateio_custo_fixo"] = 0.0
          else:
              df["rateio_custo_fixo"] = (df["horas_maquina_parada"] / total_horas_maquina) * custos_fixos
      elif criterio == "custo_direto":
          df["custo_direto_total"] = df["custo_variavel_unitario"] * df["quantidade_produzida"]
          if total_custo_direto_carteira == 0:
              df["rateio_custo_fixo"] = 0.0
          else:
              df["rateio_custo_fixo"] = (df["custo_direto_total"] / total_custo_direto_carteira) * custos_fixos
      else:
          raise ValueError(f"Criterio de rateio invalido: {criterio}")
          
      # Evitar divisão por zero se quantidade produzida for 0
      df["custo_fixo_unitario"] = df.apply(
          lambda row: row["rateio_custo_fixo"] / row["quantidade_produzida"] if row["quantidade_produzida"] > 0 else 0.0,
          axis=1
      )
      
      df["custo_absorcao_unitario"] = df["custo_variavel_unitario"] + df["despesas_variaveis_unit"] + df["custo_fixo_unitario"]
      df["lucro_unitario_absorcao"] = df["preco_venda_unitario"] - df["custo_absorcao_unitario"]
      df["lucro_total_absorcao"] = df["lucro_unitario_absorcao"] * df["quantidade_produzida"]
      
      return df

  def analisar_desperdicios_eficiencia(caminho_op: str, caminho_fin: str) -> pd.DataFrame:
      op_df = pd.read_csv(caminho_op)
      fin_df = pd.read_csv(caminho_fin)
      
      df = pd.merge(op_df, fin_df[["produto_id", "custo_variavel_unitario"]], on="produto_id", how="left").fillna(0)
      
      # Custo financeiro do refugo = quantidade_refugada * custo_variavel_unitario (matéria prima perdida)
      df["custo_refugo"] = df["quantidade_refugada"] * df["custo_variavel_unitario"]
      
      # Custo parada de máquina = horas_maquina_parada * custo_hora_maquina
      df["custo_parada_maquina"] = df["horas_maquina_parada"] * df["custo_hora_maquina"]
      
      # Perda de ineficiência total
      df["perda_ineficiencia_total"] = df["custo_refugo"] + df["custo_parada_maquina"]
      
      # Taxa de refugo (%)
      df["taxa_refugo_percentual"] = df.apply(
          lambda row: row["quantidade_refugada"] / (row["quantidade_produzida"] + row["quantidade_refugada"]) 
          if (row["quantidade_produzida"] + row["quantidade_refugada"]) > 0 else 0.0,
          axis=1
      )
      
      return df
  ```

- [ ] **Step 4: Executar os testes para certificar-se que passam**
  Executar: `pytest tests/test_tools.py -v`
  Expected: PASS

- [ ] **Step 5: Realizar commit**
  ```bash
  git add src/tools.py tests/test_tools.py
  git commit -m "feat: add absorption costing and waste calculations to tools.py"
  ```

---

### Task 4: Definição de Agentes e Tarefas CrewAI (`src/agents.py` & `src/tasks.py`)

**Files:**
- Create: `src/agents.py`
- Create: `src/tasks.py`
- Create: `tests/test_crew_setup.py`

**Interfaces:**
- Consumes: Arquivos e funções matemáticas de `src/tools.py`.
- Produces: Arquivo `src/agents.py` exportando os agentes e `src/tasks.py` exportando as tarefas configuradas.

- [ ] **Step 1: Criar o teste unitário de setup em `tests/test_crew_setup.py`**
  Validar a criação dos agentes e tarefas sem depender da execução do LLM real (usando mocks do LLM ou testando instanciação).
  ```python
  import pytest
  from crewai import Agent, Task
  import sys
  import os

  sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

  def test_agents_instantiation():
      from agents import criar_analista_financeiro, criar_auditor_processos, criar_diretor_controladoria
      # Testar instanciação básica definindo dummy LLM ou usando mock
      analista = criar_analista_financeiro()
      auditor = criar_auditor_processos()
      diretor = criar_diretor_controladoria()
      
      assert isinstance(analista, Agent)
      assert isinstance(auditor, Agent)
      assert isinstance(diretor, Agent)
      assert analista.role == "Especialista em Controladoria Industrial"

  def test_tasks_instantiation():
      from agents import criar_analista_financeiro
      from tasks import criar_tarefa_financeira
      analista = criar_analista_financeiro()
      tarefa = criar_tarefa_financeira(analista, "dummy_data.md")
      
      assert isinstance(tarefa, Task)
      assert tarefa.agent == analista
  ```

- [ ] **Step 2: Executar testes de setup e garantir que falham**
  Executar: `pytest tests/test_crew_setup.py -v`
  Expected: FAIL

- [ ] **Step 3: Implementar `src/agents.py`**
  ```python
  from crewai import Agent
  import os

  def criar_analista_financeiro() -> Agent:
      return Agent(
          role="Especialista em Controladoria Industrial",
          goal="Analisar margem de contribuicao, ponto de equilibrio e custo por absorcao sob os 3 criterios de rateio.",
          backstory="Auditor senior de custos focado em modelagem matematica de margens industriais. Sua premissa e garantir que os dados numericos de custos estejam precisos.",
          verbose=True,
          allow_delegation=False
      )

  def criar_auditor_processos() -> Agent:
      return Agent(
          role="Engenheiro de Producao e Gestor de Riscos",
          goal="Identificar falhas operacionais e quantificar financeiramente perdas por refugo e parada de maquina.",
          backstory="Especialista em Lean Manufacturing e auditoria de processos produtivos, focado em reduzir desperdicios no chao de fabrica.",
          verbose=True,
          allow_delegation=False
      )

  def criar_diretor_controladoria() -> Agent:
      return Agent(
          role="Diretor Financeiro e de Operacoes (CFO)",
          goal="Consolidar visoes financeiras e de riscos, emitir recomendacoes corporativas claras para melhoria de margem.",
          backstory="Diretor experiente em reestruturacao fabril. Ele cruza problemas fisicos (operacionais) com resultados de rentabilidade e define planos de acao acionaveis.",
          verbose=True,
          allow_delegation=False
      )
  ```

- [ ] **Step 4: Implementar `src/tasks.py`**
  ```python
  from crewai import Task
  from crewai import Agent

  def criar_tarefa_financeira(agente: Agent, output_financeiro_str: str) -> Task:
      return Task(
          description=(
              f"Analise o seguinte resumo matematico de margens e custeio por absorcao:\n"
              f"{output_financeiro_str}\n\n"
              f"Organize as informacoes em tabelas organizadas. Identifique os produtos com menores margens e compare como o custo "
              f"por absorcao unitario varia de acordo com cada um dos 3 criterios de rateio (Volume, Horas Maquina, Custo Direto)."
          ),
          expected_output="Relatorio com tabelas de margens e comparativo detalhado dos 3 metodos de rateio de custos fixos.",
          agent=agente
      )

  def criar_tarefa_operacional(agente: Agent, output_operacional_str: str) -> Task:
      return Task(
          description=(
              f"Analise a seguinte planilha consolidada de ineficiencias de fabrica:\n"
              f"{output_operacional_str}\n\n"
              f"Mapeie onde estao as maiores perdas monetarias (custo de refugo vs. custo de parada de maquina). "
              f"Aponte quais produtos ou lotes tem maior risco operacional por falhas de processo."
          ),
          expected_output="Mapeamento e diagnostico detalhado das perdas operacionais por refugo e horas paradas de maquina.",
          agent=agente
      )

  def criar_tarefa_diretoria(agente: Agent) -> Task:
      return Task(
          description=(
              "Cruze as analises financeira e operacional geradas anteriormente. Crie um relatorio de controladoria industrial.\n"
              "O relatorio deve:\n"
              "1. Explicar como as falhas de producao (refugos, paradas) estao diretamente prejudicando as margens de produtos especificos.\n"
              "2. Demonstrar o impacto de se escolher diferentes criterios de rateio de custos (Volume vs. Horas vs. Custos Diretos).\n"
              "3. Propor 3 recomendacoes praticas e acionaveis para a diretoria aumentar a margem ou mitigar os riscos operacionais identificados.\n\n"
              "Use formatacao elegante em markdown com titulos claros."
          ),
          expected_output="Relatorio Executivo final consolidado em Markdown com analise de sensibilidade de rateio e plano de acao.",
          agent=agente
      )
  ```

- [ ] **Step 5: Executar testes de configuração**
  Executar: `pytest tests/test_crew_setup.py -v`
  Expected: PASS

- [ ] **Step 6: Realizar commit**
  ```bash
  git add src/agents.py src/tasks.py tests/test_crew_setup.py
  git commit -m "feat: implement CrewAI agents and tasks configuration"
  ```

---

### Task 5: Orquestração da Crew, Ponto de Entrada e Testes Finais (`src/crew.py` & `main.py`)

**Files:**
- Create: `src/crew.py`
- Create: `main.py`
- Create: `tests/test_end_to_end.py`

**Interfaces:**
- Consumes: Biblioteca CrewAI, funções de `src/tools.py`, agentes e tarefas.
- Produces: Executável `main.py` que lê os dados de custos do período, executa os cálculos, alimenta os agentes e gera o relatório markdown final.

- [ ] **Step 1: Escrever teste de integração de ponta a ponta**
  Simular a orquestração do Crew e criação do output final em `tests/test_end_to_end.py`.
  ```python
  import pytest
  import os
  import sys

  sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

  def test_end_to_end_flow(monkeypatch):
      # Definir chave de API dummy no mock se necessario
      monkeypatch.setenv("OPENAI_API_KEY", "mock-key")
      monkeypatch.setenv("GEMINI_API_KEY", "mock-key")
      
      # Importar orquestrador
      from crew import montar_equipe_analise
      
      # Apenas verificamos se a funcao de montagem do Crew cria o objeto com 3 agentes e 3 tarefas corretos
      crew_instance = montar_equipe_analise("dummy_fin", "dummy_op", 12000.0)
      
      assert len(crew_instance.agents) == 3
      assert len(crew_instance.tasks) == 3
  ```

- [ ] **Step 2: Executar testes finais e garantir que falham**
  Executar: `pytest tests/test_end_to_end.py -v`
  Expected: FAIL

- [ ] **Step 3: Implementar `src/crew.py`**
  Montar a orquestração de dados pré-calculados.
  ```python
  from crewai import Crew, Process
  from tools import calcular_margem_contribuicao, calcular_custeio_absorcao, analisar_desperdicios_eficiencia, calcular_ponto_equilibrio
  from agents import criar_analista_financeiro, criar_auditor_processos, criar_diretor_controladoria
  from tasks import criar_tarefa_financeira, criar_tarefa_operacional, criar_tarefa_diretoria

  def montar_equipe_analise(caminho_fin: str, caminho_op: str, custos_fixos: float) -> Crew:
      # 1. Executar os calculos do motor matematico (Tools)
      margens_df = calcular_margem_contribuicao(caminho_fin)
      pe_dict = calcular_ponto_equilibrio(caminho_fin, custos_fixos)
      
      # Calcular absorcao sob os 3 criterios
      abs_vol = calcular_custeio_absorcao(caminho_fin, caminho_op, custos_fixos, "volume")
      abs_horas = calcular_custeio_absorcao(caminho_fin, caminho_op, custos_fixos, "horas_maquina")
      abs_custo_direto = calcular_custeio_absorcao(caminho_fin, caminho_op, custos_fixos, "custo_direto")
      
      # Analisar desperdicios operacionais
      desperdicios_df = analisar_desperdicios_eficiencia(caminho_op, caminho_fin)
      
      # 2. Formatar os dados em strings estruturadas em Markdown para a LLM
      output_financeiro = "## Resumo de Margens de Contribuicao:\n"
      output_financeiro += margens_df[["produto_id", "nome_produto", "margem_contribuição_unitaria", "margem_contribuição_percentual", "margem_contribuição_total"]].to_markdown(index=False)
      output_financeiro += f"\n\n**Ponto de Equilibrio Geral da Fábrica:** Faturamento Minimo de R$ {pe_dict['faturamento_equilibrio_geral']:,.2f}\n"
      
      output_financeiro += "\n## Comparativo Custeio por Absorcao (3 Rateios):\n"
      output_financeiro += "### 1. Rateio por Volume:\n"
      output_financeiro += abs_vol[["produto_id", "custo_absorcao_unitario", "lucro_unitario_absorcao"]].to_markdown(index=False)
      output_financeiro += "\n### 2. Rateio por Horas Maquina:\n"
      output_financeiro += abs_horas[["produto_id", "custo_absorcao_unitario", "lucro_unitario_absorcao"]].to_markdown(index=False)
      output_financeiro += "\n### 3. Rateio por Custo Direto:\n"
      output_financeiro += abs_custo_direto[["produto_id", "custo_absorcao_unitario", "lucro_unitario_absorcao"]].to_markdown(index=False)
      
      output_operacional = desperdicios_df[["lote_id", "produto_id", "quantidade_produzida", "quantidade_refugada", "taxa_refugo_percentual", "horas_maquina_parada", "custo_refugo", "custo_parada_maquina", "perda_ineficiencia_total"]].to_markdown(index=False)
      
      # 3. Instanciar agentes
      analista = criar_analista_financeiro()
      auditor = criar_auditor_processos()
      diretor = criar_diretor_controladoria()
      
      # 4. Instanciar tarefas
      t1 = criar_tarefa_financeira(analista, output_financeiro)
      t2 = criar_tarefa_operacional(auditor, output_operacional)
      t3 = criar_tarefa_diretoria(diretor)
      
      # 5. Montar a Crew
      return Crew(
          agents=[analista, auditor, diretor],
          tasks=[t1, t2, t3],
          process=Process.sequential
      )
  ```

- [ ] **Step 4: Implementar `main.py`**
  ```python
  import os
  from dotenv import load_dotenv
  from crew import montar_equipe_analise

  def main():
      load_dotenv()
      
      # Certificar-se que a chave da API existe (ex: GEMINI_API_KEY ou OPENAI_API_KEY)
      if not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
          print("AVISO: GEMINI_API_KEY ou OPENAI_API_KEY nao encontradas no arquivo .env.")
      
      caminho_fin = "data/custos_financeiros.csv"
      caminho_op = "data/logs_operacionais.csv"
      custos_fixos_mensais = 30000.00 # Custos fixos totais da fabrica
      
      print("Orquestrando equipe de controle de custos...")
      equipe = montar_equipe_analise(caminho_fin, caminho_op, custos_fixos_mensais)
      
      print("Executando analise com os agentes autônomos...")
      resultado = equipe.kickoff()
      
      print("\n=== DIAGNÓSTICO ESTRATÉGICO FINAL ===\n")
      print(resultado)
      
      # Salvar resultado final em arquivo
      with open("relatorio_controladoria.md", "w") as f:
          f.write(resultado)
      print("\nRelatorio salvo em 'relatorio_controladoria.md'")

  if __name__ == "__main__":
      main()
  ```

- [ ] **Step 5: Executar todos os testes da aplicação**
  Executar: `pytest`
  Expected: PASS

- [ ] **Step 6: Realizar commit**
  ```bash
  git add src/crew.py main.py tests/test_end_to_end.py
  git commit -m "feat: implement orchestration and entrypoint script main.py"
  ```
