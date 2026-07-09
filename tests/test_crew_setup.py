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

