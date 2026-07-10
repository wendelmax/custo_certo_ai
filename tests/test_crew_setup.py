import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from custom_crew import Agent, Task

def test_agents_instantiation():
    from agents import criar_analista_financeiro, criar_auditor_processos, criar_diretor_controladoria
    analista = criar_analista_financeiro()
    auditor = criar_auditor_processos()
    diretor = criar_diretor_controladoria()
    
    assert isinstance(analista, Agent)
    assert isinstance(auditor, Agent)
    assert isinstance(diretor, Agent)
    assert analista.role == "Especialista em Controladoria Industrial"
    assert auditor.role == "Engenheiro de Producao e Gestor de Riscos"
    assert diretor.role == "Diretor Financeiro e de Operacoes (CFO)"

def test_tasks_instantiation():
    from agents import criar_analista_financeiro
    from tasks import criar_tarefa_financeira, criar_tarefa_operacional, criar_tarefa_diretoria
    analista = criar_analista_financeiro()
    tarefa_fin = criar_tarefa_financeira(analista, "dummy_data.md")
    tarefa_op = criar_tarefa_operacional(analista, "dummy_data_op.md")
    tarefa_dir = criar_tarefa_diretoria(analista)
    
    assert isinstance(tarefa_fin, Task)
    assert tarefa_fin.agent == analista
    assert isinstance(tarefa_op, Task)
    assert tarefa_op.agent == analista
    assert isinstance(tarefa_dir, Task)
    assert tarefa_dir.agent == analista

def test_crew_kickoff():
    from custom_crew import Crew
    
    agent_calls = []
    
    class DummyAgent(Agent):
        def execute(self, task_description: str, context: str = "") -> str:
            agent_calls.append((self.role, task_description, context))
            return f"Result from {self.role}"
            
    analista = DummyAgent(role="Analista", goal="goal", backstory="backstory")
    auditor = DummyAgent(role="Auditor", goal="goal", backstory="backstory")
    
    task1 = Task(description="task 1 desc", expected_output="output 1", agent=analista)
    task2 = Task(description="task 2 desc", expected_output="output 2", agent=auditor)
    
    crew = Crew(agents=[analista, auditor], tasks=[task1, task2])
    
    result = crew.kickoff()
    
    assert result == "Result from Auditor"
    assert task1.output == "Result from Analista"
    assert task2.output == "Result from Auditor"
    
    assert len(agent_calls) == 2
    assert agent_calls[0] == ("Analista", "task 1 desc", "")
    assert agent_calls[1] == ("Auditor", "task 2 desc", "\n### Output from Task 1 (Analista):\nResult from Analista\n")


def test_montar_equipe_com_arquivos_opcionais(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "mock-key")
    monkeypatch.setenv("GEMINI_API_KEY", "mock-key")

    from custom_crew import Agent, Crew
    calls = []
    def mock_execute(self, task_description, context=""):
        calls.append((self.role, task_description, context))
        return f"Mock output for {self.role}"
    monkeypatch.setattr(Agent, "execute", mock_execute)

    from crew import montar_equipe_analise

    caminho_fin = os.path.join(os.path.dirname(__file__), "../data/custos_financeiros.csv")
    caminho_op = os.path.join(os.path.dirname(__file__), "../data/logs_operacionais.csv")

    bom_file = tmp_path / "bom.csv"
    bom_file.write_text("produto_id,material,quantidade\nPROD-001,Aco 50mm,2\nPROD-002,Ferro Fundido,1\n", encoding="utf-8")

    budget_file = tmp_path / "budget.csv"
    budget_file.write_text("categoria,orçado,real\nMateria Prima,50000,52000\nMao de Obra,30000,28000\n", encoding="utf-8")

    obs_file = tmp_path / "observacoes.txt"
    obs_file.write_text("Linha de producao A apresentou ruido no eixo principal.\nTurno noturno com 2 operarios ausentes.\n", encoding="utf-8")

    caminhos_opcionais = {
        "bom": str(bom_file),
        "budget": str(budget_file),
        "observacoes": str(obs_file),
    }

    crew_instance = montar_equipe_analise(caminho_fin, caminho_op, 30000.0, caminhos_opcionais=caminhos_opcionais)

    assert isinstance(crew_instance, Crew)
    assert len(crew_instance.agents) == 3
    assert len(crew_instance.tasks) == 3

    assert "Ficha Técnica / Estrutura de Produtos (BOM)" in crew_instance.tasks[0].description
    assert "Orçamento e Metas Anuais (Budget vs Real)" in crew_instance.tasks[0].description
    assert "Observações Adicionais do Chão de Fábrica" in crew_instance.tasks[0].description

    assert "Ficha Técnica / Estrutura de Produtos (BOM)" in crew_instance.tasks[1].description
    assert "Orçamento e Metas Anuais (Budget vs Real)" in crew_instance.tasks[1].description
    assert "Observações Adicionais do Chão de Fábrica" in crew_instance.tasks[1].description

    crew_instance.kickoff()
    assert len(calls) == 3

def test_detect_openai_provider(monkeypatch):
    from custom_crew import detect_openai_provider

    # Sem nenhuma chave → None
    for env in ["GROQ_API_KEY", "HYPER_API_KEY", "OPENAI_API_KEY", "OPENROUTER_API_KEY"]:
        monkeypatch.delenv(env, raising=False)
    assert detect_openai_provider() is None

    # GROQ_API_KEY → detecta base_url da Groq
    monkeypatch.setenv("GROQ_API_KEY", "grok_test")
    result = detect_openai_provider()
    assert result["api_key"] == "grok_test"
    assert "groq.com" in result["base_url"]
    monkeypatch.delenv("GROQ_API_KEY")

    # OPENAI_API_KEY sem base_url → None (usa default da lib)
    monkeypatch.setenv("OPENAI_API_KEY", "openai_test")
    result = detect_openai_provider()
    assert result["api_key"] == "openai_test"
    assert result["base_url"] is None
    monkeypatch.delenv("OPENAI_API_KEY")

    # HYPER_API_KEY com OPENAI_MODEL override
    monkeypatch.setenv("HYPER_API_KEY", "hyper_test")
    monkeypatch.setenv("OPENAI_MODEL", "hyperbee-1.0")
    result = detect_openai_provider()
    assert result["api_key"] == "hyper_test"
    assert "hyper.charm.land" in result["base_url"]
    assert result["model"] == "hyperbee-1.0"
    monkeypatch.delenv("HYPER_API_KEY")
    monkeypatch.delenv("OPENAI_MODEL")

    # OPENAI_BASE_URL explicito sobrescreve deteccao
    monkeypatch.setenv("GROQ_API_KEY", "custom_test")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://custom.api.com/v1")
    result = detect_openai_provider()
    assert result["base_url"] == "https://custom.api.com/v1"
    monkeypatch.delenv("GROQ_API_KEY")
    monkeypatch.delenv("OPENAI_BASE_URL")


def test_df_to_markdown():
    import numpy as np
    import pandas as pd
    from crew import df_to_markdown

    df = pd.DataFrame({
        "A": [1, np.int64(2), 3],
        "B": [1.5, np.float64(2.567), pd.NA],
        "C": ["text", True, False],
        "D": [None, np.nan, 4.0]
    })
    
    # We convert float columns to nullable or float types
    # B contains a float and pd.NA, pandas will treat it as object or float (if using Float64)
    # Let's ensure B uses Float64 type
    df["B"] = df["B"].astype("Float64")
    
    result = df_to_markdown(df)
    
    # Expected output:
    # | A | B | C | D |
    # | --- | --- | --- | --- |
    # | 1 | 1.50 | text |  |
    # | 2 | 2.57 | True |  |
    # | 3 |  | False | 4.00 |
    
    expected = (
        "| A | B | C | D |\n"
        "| --- | --- | --- | --- |\n"
        "| 1 | 1.50 | text |  |\n"
        "| 2 | 2.57 | True |  |\n"
        "| 3 |  | False | 4.00 |\n"
    )
    assert result == expected

