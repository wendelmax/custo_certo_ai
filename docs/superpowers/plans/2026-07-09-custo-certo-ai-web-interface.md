# Custo Certo AI - Local Web Interface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a user-friendly, responsive desktop-ready local web application for Custo Certo AI that supports drag-and-drop CSV uploads, input parameters, optional enrichment files (BOM, Budget, free-text/PDF), and provides interactive download buttons for generated Excel and HTML reports.

**Architecture:** A local Python web server powered by Flask. The backend handles the uploads, triggers the core analysis and Crew AI pipelines, and serves the generated files. The frontend is a single-page app utilizing HTML5 and TailwindCSS v4 to create a premium responsive dashboard.

**Tech Stack:** Python 3.10+, Flask 3.0+, TailwindCSS v4, Pandas, openpyxl, google-genai.

## Global Constraints
- Python 3.10+ compatibility (compatible up to Python 3.14).
- Maintain responsiveness across viewport sizes using TailwindCSS v4.
- Support optional enrichment files (BOM, Budget, Shift notes) and inject them into the Crew AI agents context.
- Maintain existing mathematical rules (Margens, PE, Absorção, Desperdício) intact.

---

### Task 1: Scaffolding and Dependencies

**Files:**
- Modify: `requirements.txt`

**Interfaces:**
- Consumes: None
- Produces: Installed dependencies in virtualenv

- [ ] **Step 1: Add Flask to requirements.txt**
  Append `Flask>=3.0.0` to `requirements.txt`.
  ```text
  google-genai>=0.1.1
  pandas>=2.0.0
  openpyxl>=3.1.0
  python-dotenv>=1.0.0
  pytest>=7.0.0
  tabulate>=0.9.0
  markdown>=3.0.0
  Flask>=3.0.0
  ```

- [ ] **Step 2: Run dependency installation**
  Run: `./test-venv/bin/pip install -r requirements.txt`
  Expected: Installation completes without errors.

- [ ] **Step 3: Run existing tests to verify baseline is green**
  Run: `./test-venv/bin/pytest -v`
  Expected: Existing 24 tests pass successfully.

- [ ] **Step 4: Commit changes**
  Run:
  ```bash
  git add requirements.txt
  git commit -m "chore: add Flask dependency to requirements.txt"
  ```

---

### Task 2: Adapt Crew AI Pipeline for Optional Context (`src/crew.py`)

**Files:**
- Modify: `src/crew.py`
- Test: `tests/test_crew_setup.py`

**Interfaces:**
- Consumes: `caminho_fin`, `caminho_op`, `custos_fixos`
- Produces: Modified `montar_equipe_analise(caminho_fin, caminho_op, custos_fixos, caminhos_opcionais=None)`

- [ ] **Step 1: Update montar_equipe_analise to accept optional context files**
  Open `src/crew.py` and modify the function signature and logic. Parse optional CSV/Excel or text files, convert to markdown/text, and inject into the prompt contexts.
  
  ```python
  # Modificação em src/crew.py
  def montar_equipe_analise(caminho_fin: str, caminho_op: str, custos_fixos: float, caminhos_opcionais: dict = None) -> Crew:
      # ... [existente: calcular margens, PE, absorção, desperdícios] ...
      
      contexto_enriquecimento = ""
      if caminhos_opcionais:
          if "bom" in caminhos_opcionais and caminhos_opcionais["bom"]:
              try:
                  bom_df = pd.read_csv(caminhos_opcionais["bom"]) if caminhos_opcionais["bom"].endswith(".csv") else pd.read_excel(caminhos_opcionais["bom"])
                  contexto_enriquecimento += f"\n### Ficha Técnica / Estrutura de Produtos (BOM):\n{df_to_markdown(bom_df)}\n"
              except Exception as e:
                  contexto_enriquecimento += f"\nErro ao ler Ficha Técnica (BOM): {e}\n"
                  
          if "budget" in caminhos_opcionais and caminhos_opcionais["budget"]:
              try:
                  budget_df = pd.read_csv(caminhos_opcionais["budget"]) if caminhos_opcionais["budget"].endswith(".csv") else pd.read_excel(caminhos_opcionais["budget"])
                  contexto_enriquecimento += f"\n### Orçamento e Metas Anuais (Budget vs Real):\n{df_to_markdown(budget_df)}\n"
              except Exception as e:
                  contexto_enriquecimento += f"\nErro ao ler Orçamento: {e}\n"
                  
          if "observacoes" in caminhos_opcionais and caminhos_opcionais["observacoes"]:
              try:
                  with open(caminhos_opcionais["observacoes"], "r", encoding="utf-8") as f:
                      obs_text = f.read()
                  contexto_enriquecimento += f"\n### Observações Adicionais do Chão de Fábrica:\n{obs_text}\n"
              except Exception as e:
                  contexto_enriquecimento += f"\nErro ao ler Observações: {e}\n"
                  
      # Injetar o contexto_enriquecimento nos prompts das tarefas
      # Modifique a criação das tarefas em src/crew.py para incluir contexto_enriquecimento nos textos
      # Exemplo: t1 = criar_tarefa_financeira(analista, output_financeiro + contexto_enriquecimento)
      # ...
  ```

- [ ] **Step 2: Add test for optional context parsing**
  Open `tests/test_crew_setup.py` and write a test case verifying the new function argument.
  
  ```python
  def test_montar_equipe_com_arquivos_opcionais():
      # Criar arquivos dummy e passar no dicionário caminhos_opcionais
      # Chamar montar_equipe_analise
      # Assert que a equipe é montada com sucesso
      pass
  ```

- [ ] **Step 3: Run the test to verify**
  Run: `./test-venv/bin/pytest tests/test_crew_setup.py -v`
  Expected: PASS

- [ ] **Step 4: Commit changes**
  Run:
  ```bash
  git add src/crew.py tests/test_crew_setup.py
  git commit -m "feat: support optional enrichment files in crew orchestration"
  ```

---

### Task 3: Implement Flask Server Backend (`app.py`)

**Files:**
- Create: `app.py`
- Test: `tests/test_app.py`

**Interfaces:**
- Consumes: Flask requests containing files and parameters.
- Produces: API response JSON with calculation results, generating `analise_de_custos.xlsx` and `relatorio_controladoria.html`.

- [ ] **Step 1: Create app.py**
  Implement Flask endpoints for homepage, analysis run, and file download.
  
  ```python
  import os
  import sys
  from flask import Flask, request, jsonify, render_template, send_from_directory
  from werkzeug.utils import secure_filename
  from dotenv import load_dotenv

  sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
  from crew import montar_equipe_analise
  from tools import (
      calcular_margem_contribuicao, 
      calcular_custeio_absorcao, 
      analisar_desperdicios_eficiencia, 
      calcular_ponto_equilibrio
  )
  from exportador import exportar_analise_excel
  from converter_relatorio import converter_markdown_para_html_premium

  load_dotenv()
  app = Flask(__name__)
  app.config['UPLOAD_FOLDER'] = 'uploads'
  os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

  @app.route('/')
  def index():
      return render_template('index.html')

  @app.route('/analisar', methods=['POST'])
  def analisar():
      # 1. Recuperar parâmetros e arquivos
      custos_fixos = float(request.form.get('custos_fixos', 30000.00))
      
      file_fin = request.files.get('file_financeiro')
      file_op = request.files.get('file_operacional')
      
      if not file_fin or not file_op:
          return jsonify({'error': 'Arquivos obrigatórios ausentes'}), 400
          
      caminho_fin = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file_fin.filename))
      caminho_op = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file_op.filename))
      file_fin.save(caminho_fin)
      file_op.save(caminho_op)
      
      # 2. Arquivos opcionais
      caminhos_opcionais = {}
      for key in ['bom', 'budget', 'observacoes']:
          f = request.files.get(key)
          if f and f.filename:
              path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
              f.save(path)
              caminhos_opcionais[key] = path
              
      # 3. Executar equipe e cálculos
      equipe = montar_equipe_analise(caminho_fin, caminho_op, custos_fixos, caminhos_opcionais)
      resultado = equipe.kickoff()
      
      # Salvar relatório MD
      with open("relatorio_controladoria.md", "w", encoding="utf-8") as f:
          f.write(resultado)
          
      # Geração Excel
      import pandas as pd
      margens_df = calcular_margem_contribuicao(caminho_fin)
      pe_dict = calcular_ponto_equilibrio(caminho_fin, custos_fixos)
      abs_vol = calcular_custeio_absorcao(caminho_fin, caminho_op, custos_fixos, "volume")
      abs_horas = calcular_custeio_absorcao(caminho_fin, caminho_op, custos_fixos, "horas_maquina")
      abs_custo_direto = calcular_custeio_absorcao(caminho_fin, caminho_op, custos_fixos, "custo_direto")
      desperdicios_df = analisar_desperdicios_eficiencia(caminho_op, caminho_fin)
      
      exportar_analise_excel(
          "analise_de_custos.xlsx",
          margens_df, abs_vol, abs_horas, abs_custo_direto, desperdicios_df,
          pe_dict, custos_fixos
      )
      
      # Geração HTML
      converter_markdown_para_html_premium("relatorio_controladoria.md", "relatorio_controladoria.html")
      
      # Renderizar o Markdown como HTML parcial para retornar ao frontend
      import markdown
      html_resultado = markdown.markdown(resultado, extensions=['tables'])
      
      # Extrair alguns KPIs para retorno rápido
      kpis = {
          'ponto_equilibrio': pe_dict['faturamento_equilibrio_geral'],
          'margem_media': margens_df['margem_contribuição_unitaria'].mean(),
          'custo_refugo': desperdicios_df['custo_refugo'].sum() if not desperdicios_df.empty else 0.0
      }
      
      return jsonify({
          'success': True,
          'kpis': kpis,
          'relatorio_html': html_resultado
      })

  @app.route('/download/<arquivo>')
  def download(arquivo):
      if arquivo == 'excel':
          return send_from_directory('.', 'analise_de_custos.xlsx', as_attachment=True)
      elif arquivo == 'html':
          return send_from_directory('.', 'relatorio_controladoria.html')
      return jsonify({'error': 'Arquivo inválido'}), 404

  if __name__ == '__main__':
      app.run(debug=True, port=5000)
  ```

- [ ] **Step 2: Implement tests in tests/test_app.py**
  Verify standard requests return successfully.
  
  ```python
  import pytest
  from app import app as flask_app

  @pytest.fixture
  def client():
      flask_app.config['TESTING'] = True
      with flask_app.test_client() as client:
          yield client

  def test_index_route(client):
      res = client.get('/')
      assert res.status_code == 200
  ```

- [ ] **Step 3: Run app tests**
  Run: `./test-venv/bin/pytest tests/test_app.py -v`
  Expected: PASS

- [ ] **Step 4: Commit changes**
  Run:
  ```bash
  git add app.py tests/test_app.py
  git commit -m "feat: implement Flask backend app.py and tests"
  ```

---

### Task 4: Implement TailwindCSS v4 Frontend UI (`templates/index.html`)

**Files:**
- Create: `templates/index.html`

**Interfaces:**
- Consumes: Backend Flask JSON responses from `/analisar`
- Produces: Responsive UI with form submission and file download capabilities

- [ ] **Step 1: Create templates/index.html**
  Create the `templates/` directory if needed and write the complete single-page application using TailwindCSS v4 and vanilla JavaScript.
  Ensure it features dark/light mode toggles, drag-and-drop inputs for all files, and handles progress states during execution.
  
  *(Use the responsive columns layout, KPI dashboard cards, executive markdown report viewer, and download links mapped to `/download/excel` and `/download/html`)*

- [ ] **Step 2: Verify template files existence**
  Ensure file is saved at `/mnt/c/Users/wende/Projects/custo_certo/templates/index.html`.

- [ ] **Step 3: Commit changes**
  Run:
  ```bash
  git add templates/index.html
  git commit -m "feat: implement responsive TailwindCSS v4 frontend template"
  ```

---

### Task 4: End-to-End Testing and Verification

**Files:**
- None (manual/automated E2E verification)

**Interfaces:**
- None

- [ ] **Step 1: Run all automated tests**
  Run: `./test-venv/bin/pytest -v`
  Expected: All 26+ tests pass successfully.

- [ ] **Step 2: Launch the Flask server**
  Propose command: `./test-venv/bin/python app.py` and run it in background to check endpoints.

- [ ] **Step 3: Commit and verify git status is clean**
  Run: `git status`
  Expected: Clean working tree except for files added/changed in the plan.
