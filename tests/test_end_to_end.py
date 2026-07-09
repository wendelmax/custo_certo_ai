import pytest
import os
import sys
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

def test_end_to_end_flow(monkeypatch):
    # Set dummy API keys just in case
    monkeypatch.setenv("OPENAI_API_KEY", "mock-key")
    monkeypatch.setenv("GEMINI_API_KEY", "mock-key")
    
    # Mock Agent.execute to avoid API calls
    from custom_crew import Agent
    calls = []
    def mock_execute(self, task_description, context=""):
        calls.append((self.role, task_description, context))
        return f"Mock output for {self.role}"
    
    monkeypatch.setattr(Agent, "execute", mock_execute)
    
    # Import crew orchestrator
    from crew import montar_equipe_analise
    
    caminho_fin = os.path.join(os.path.dirname(__file__), "../data/custos_financeiros.csv")
    caminho_op = os.path.join(os.path.dirname(__file__), "../data/logs_operacionais.csv")
    custos_fixos = 30000.0
    
    crew_instance = montar_equipe_analise(caminho_fin, caminho_op, custos_fixos)
    
    assert len(crew_instance.agents) == 3
    assert len(crew_instance.tasks) == 3
    
    # Kickoff the crew execution and check result
    resultado = crew_instance.kickoff()
    assert resultado == "Mock output for Diretor Financeiro e de Operacoes (CFO)"
    assert len(calls) == 3
    
    # Verify execution order and content passing
    assert calls[0][0] == "Especialista em Controladoria Industrial"
    assert "Resumo de Margens de Contribuicao" in calls[0][1]
    assert calls[1][0] == "Engenheiro de Producao e Gestor de Riscos"
    assert calls[2][0] == "Diretor Financeiro e de Operacoes (CFO)"

def test_main_execution(monkeypatch, tmp_path):
    # Set dummy API keys
    monkeypatch.setenv("OPENAI_API_KEY", "mock-key")
    monkeypatch.setenv("GEMINI_API_KEY", "mock-key")
    
    # Mock Agent.execute
    from custom_crew import Agent
    def mock_execute(self, task_description, context=""):
        return f"Mock report content for {self.role}"
    monkeypatch.setattr(Agent, "execute", mock_execute)
    
    # Set up directory context
    original_cwd = os.getcwd()
    try:
        # Copy data files to temp directory
        shutil.copytree(os.path.join(original_cwd, "data"), os.path.join(tmp_path, "data"))
        os.chdir(tmp_path)
        
        # Add original cwd to sys.path so python can find main and src modules
        sys.path.insert(0, original_cwd)
        sys.path.insert(0, os.path.join(original_cwd, "src"))
        
        from main import main as run_main
        run_main()
        
        # Check that the report was created
        report_path = os.path.join(tmp_path, "relatorio_controladoria.md")
        assert os.path.exists(report_path)
        with open(report_path, "r") as f:
            content = f.read()
        assert "Mock report content for Diretor Financeiro e de Operacoes (CFO)" in content
        
        # Verificar se os arquivos de relatorios foram gerados com sucesso
        assert os.path.exists("relatorio_controladoria.md")
        assert os.path.exists("relatorio_controladoria.html")
        assert os.path.exists("analise_de_custos.xlsx")
        
    finally:
        os.chdir(original_cwd)
        # Clean sys.path if necessary
        if original_cwd in sys.path:
            sys.path.remove(original_cwd)
        src_path = os.path.join(original_cwd, "src")
        if src_path in sys.path:
            sys.path.remove(src_path)
