# Exportadores e Relatórios C-Level - Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar o módulo de exportação profissional para Excel (`src/exportador.py`) e o conversor HTML Premium C-Level (`converter_relatorio.py`), integrando-os ao ponto de entrada `main.py` da aplicação.

**Architecture:** O exportador Excel usará a biblioteca `openpyxl` para formatar e estilizar quatro abas com cabeçalhos coloridos, formatação monetária e auto-ajuste de colunas. O conversor HTML lerá o markdown gerado pelo agente Diretor de Controladoria e aplicará estilos CSS elegantes (fontes modernas, boxes de riscos destacados e tabelas estilizadas).

**Tech Stack:** Python 3.10+, Pandas, Openpyxl, Markdown, Pytest, Git.

## Global Constraints
- Toda estilização do Excel deve seguir a paleta corporativa padrão (cabeçalhos em azul escuro `#1F497D` com texto em branco, linhas alternadas em cinza claro e formatação monetária `R$ #,##0.00`).
- O conversor de relatório HTML deve utilizar apenas CSS embutido (`style` tags) para garantir portabilidade completa no envio de e-mails corporativos.
- Todos os novos arquivos e lógicas devem possuir testes unitários correspondentes no diretório `tests/`.

---

### Task 1: Módulo de Exportação para Excel (`src/exportador.py`)

**Files:**
- Create: `src/exportador.py`
- Create: `tests/test_exportador.py`

**Interfaces:**
- Consumes: DataFrames consolidados das ferramentas de cálculo (`tools.py`).
- Produces: Função `exportar_analise_excel(caminho_saida: str, df_margens: pd.DataFrame, df_absorcao_vol: pd.DataFrame, df_absorcao_horas: pd.DataFrame, df_absorcao_custo: pd.DataFrame, df_ineficiencias: pd.DataFrame, pe_dict: dict, custos_fixos: float) -> None`.

- [ ] **Step 1: Escrever teste de falha em `tests/test_exportador.py`**
  Escrever um teste que gera DataFrames fictícios e tenta chamar o exportador.
  ```python
  import pytest
  import os
  import pandas as pd
  import sys

  sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

  def test_exportar_analise_excel():
      from exportador import exportar_analise_excel
      
      caminho_teste = "tests/test_analise_exportada.xlsx"
      if os.path.exists(caminho_teste):
          os.remove(caminho_teste)
          
      # Criar dados dummies
      df_dummy = pd.DataFrame([{"produto_id": "P01", "valor": 100.00}])
      pe_dummy = {"faturamento_equilibrio_geral": 50000.00, "margem_contribuição_media_ponderada": 0.45}
      
      exportar_analise_excel(
          caminho_teste,
          df_dummy, df_dummy, df_dummy, df_dummy, df_dummy,
          pe_dummy, 12000.00
      )
      
      assert os.path.exists(caminho_teste)
      # Validar se as planilhas corretas foram criadas
      xl = pd.ExcelFile(caminho_teste)
      assert "Dashboard C-Level" in xl.sheet_names
      assert "Margens e PE" in xl.sheet_names
      
      # Limpeza
      if os.path.exists(caminho_teste):
          os.remove(caminho_teste)
  ```

- [ ] **Step 2: Executar o teste e certificar-se que falha**
  Executar: `pytest tests/test_exportador.py -v`
  Expected: FAIL (ModuleNotFoundError: No module named 'exportador')

- [ ] **Step 3: Implementar `src/exportador.py`**
  Implementar a lógica usando `openpyxl` e formatação visual elegante.
  ```python
  import pandas as pd
  from openpyxl import Workbook
  from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
  from openpyxl.utils.dataframe import dataframe_to_rows

  def exportar_analise_excel(caminho_saida: str, df_margens: pd.DataFrame, df_absorcao_vol: pd.DataFrame, 
                             df_absorcao_horas: pd.DataFrame, df_absorcao_custo: pd.DataFrame, 
                             df_ineficiencias: pd.DataFrame, pe_dict: dict, custos_fixos: float) -> None:
      wb = Workbook()
      
      # Estilos visuais
      header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
      header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid") # Azul Escuro
      zebra_fill = PatternFill(start_color="F2F5F8", end_color="F2F5F8", fill_type="solid") # Cinza Claro
      bold_font = Font(name="Calibri", size=11, bold=True)
      thin_border = Border(
          left=Side(style='thin', color='D3D3D3'),
          right=Side(style='thin', color='D3D3D3'),
          top=Side(style='thin', color='D3D3D3'),
          bottom=Side(style='thin', color='D3D3D3')
      )
      
      # 1. ABA 1: Dashboard C-Level
      ws_dash = wb.active
      ws_dash.title = "Dashboard C-Level"
      ws_dash.views.sheetView[0].showGridLines = True
      
      ws_dash.append(["Métrica Executiva", "Valor Financeiro"])
      ws_dash.append(["Faturamento Total da Fábrica", pe_dict.get("faturamento_atual_total", 0.0)])
      ws_dash.append(["Custos Fixos Mensais Fabris", custos_fixos])
      ws_dash.append(["Ponto de Equilíbrio Geral", pe_dict.get("faturamento_equilibrio_geral", 0.0)])
      ws_dash.append(["Margem de Contribuição Média (%)", pe_dict.get("margem_contribuição_media_ponderada", 0.0)])
      ws_dash.append(["Custo Total de Ineficiências (Refugo + Paradas)", df_ineficiencias["perda_ineficiencia_total"].sum() if "perda_ineficiencia_total" in df_ineficiencias.columns else 0.0])
      
      # Estilizar Aba 1
      for col in ws_dash.iter_cols(min_row=1, max_row=6, min_col=1, max_col=2):
          for cell in col:
              cell.border = thin_border
      for cell in ws_dash[1]:
          cell.font = header_font
          cell.fill = header_fill
          cell.alignment = Alignment(horizontal="center")
      for row in range(2, 7):
          ws_dash.cell(row=row, column=2).number_format = 'R$ #,##0.00'
          if row == 5:
              ws_dash.cell(row=row, column=2).number_format = '0.0%'
      ws_dash.cell(row=6, column=2).font = Font(name="Calibri", size=11, bold=True, color="FF0000") # Custo ineficiencia em vermelho
      
      # Helper para exportar tabelas genéricas
      def exportar_planilha_tabela(nome_aba: str, df: pd.DataFrame, formats: dict):
          ws = wb.create_sheet(title=nome_aba)
          ws.views.sheetView[0].showGridLines = True
          
          # Cabeçalhos
          headers = list(df.columns)
          ws.append(headers)
          for cell in ws[1]:
              cell.font = header_font
              cell.fill = header_fill
              cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
              
          # Conteúdo
          for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=False), start=2):
              ws.append(row)
              # Estilo zebra e bordas
              fill = zebra_fill if r_idx % 2 == 0 else PatternFill(fill_type=None)
              for c_idx in range(1, len(row) + 1):
                  cell = ws.cell(row=r_idx, column=c_idx)
                  cell.border = thin_border
                  if fill.fill_type:
                      cell.fill = fill
                      
                  # Formatação específica de colunas
                  col_name = headers[c_idx - 1]
                  if col_name in formats:
                      cell.number_format = formats[col_name]
                      
      # Formatos das colunas
      formats_margem = {
          "preco_venda_unitario": 'R$ #,##0.00',
          "custo_variavel_unitario": 'R$ #,##0.00',
          "despesas_variaveis_unit": 'R$ #,##0.00',
          "margem_contribuição_unitaria": 'R$ #,##0.00',
          "margem_contribuição_percentual": '0.0%',
          "margem_contribuição_total": 'R$ #,##0.00',
          "volume_vendas_mensal": '#,##0'
      }
      formats_absorcao = {
          "preco_venda_unitario": 'R$ #,##0.00',
          "custo_variavel_unitario": 'R$ #,##0.00',
          "despesas_variaveis_unit": 'R$ #,##0.00',
          "quantidade_produzida": '#,##0',
          "horas_maquina_ativas": '#,##0.0',
          "rateio_custo_fixo": 'R$ #,##0.00',
          "custo_fixo_unitario": 'R$ #,##0.00',
          "custo_absorcao_unitario": 'R$ #,##0.00',
          "lucro_unitario_absorcao": 'R$ #,##0.00',
          "lucro_total_absorcao": 'R$ #,##0.00'
      }
      formats_ineficiencias = {
          "quantidade_produzida": '#,##0',
          "quantidade_refugada": '#,##0',
          "taxa_refugo_percentual": '0.0%',
          "horas_maquina_parada": '#,##0.0',
          "custo_refugo": 'R$ #,##0.00',
          "custo_parada_maquina": 'R$ #,##0.00',
          "perda_ineficiencia_total": 'R$ #,##0.00'
      }
      
      # 2. ABA 2: Margens
      exportar_planilha_tabela("Margens e PE", df_margens, formats_margem)
      
      # 3. ABA 3: Absorção
      # Concatenar visões de absorção para relatório side-by-side limpo
      abs_consolidado = df_absorcao_vol[["produto_id", "nome_produto", "preco_venda_unitario", "custo_absorcao_unitario", "lucro_unitario_absorcao"]].copy()
      abs_consolidado.columns = ["produto_id", "nome_produto", "Preço Venda", "Absorção Unit. (Volume)", "Lucro Unit. (Volume)"]
      
      abs_consolidado["Absorção Unit. (Horas)"] = df_absorcao_horas["custo_absorcao_unitario"]
      abs_consolidado["Lucro Unit. (Horas)"] = df_absorcao_horas["lucro_unitario_absorcao"]
      abs_consolidado["Absorção Unit. (Custo Dir)"] = df_absorcao_custo["custo_absorcao_unitario"]
      abs_consolidado["Lucro Unit. (Custo Dir)"] = df_absorcao_custo["lucro_unitario_absorcao"]
      
      formats_consolidado = {
          "Preço Venda": 'R$ #,##0.00',
          "Absorção Unit. (Volume)": 'R$ #,##0.00',
          "Lucro Unit. (Volume)": 'R$ #,##0.00',
          "Absorção Unit. (Horas)": 'R$ #,##0.00',
          "Lucro Unit. (Horas)": 'R$ #,##0.00',
          "Absorção Unit. (Custo Dir)": 'R$ #,##0.00',
          "Lucro Unit. (Custo Dir)": 'R$ #,##0.00'
      }
      exportar_planilha_tabela("Rateios por Absorção", abs_consolidado, formats_consolidado)
      
      # 4. ABA 4: Ineficiências
      exportar_planilha_tabela("Ineficiências Fabris", df_ineficiencias, formats_ineficiencias)
      
      # Auto-fit columns nas abas
      for ws in wb.worksheets:
          for col in ws.columns:
              max_len = 0
              col_letter = col[0].column_letter
              for cell in col:
                  val_str = str(cell.value or '')
                  if len(val_str) > max_len:
                      max_len = len(val_str)
              ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
              
      wb.save(caminho_saida)
  ```

- [ ] **Step 4: Executar os testes para certificar-se que passam**
  Executar: `pytest tests/test_exportador.py -v`
  Expected: PASS

- [ ] **Step 5: Realizar commit**
  ```bash
  git add src/exportador.py tests/test_exportador.py
  git commit -m "feat: implement structured Excel exporter module"
  ```

---

### Task 2: Conversor de Relatório C-Level HTML (`converter_relatorio.py`)

**Files:**
- Create: `converter_relatorio.py`
- Create: `tests/test_converter.py`

**Interfaces:**
- Consumes: Arquivo Markdown `relatorio_controladoria.md`.
- Produces: Arquivo HTML estilizado `relatorio_controladoria.html` via função `converter_markdown_para_html_premium(caminho_md: str, caminho_html: str) -> None`.

- [ ] **Step 1: Escrever teste de falha em `tests/test_converter.py`**
  ```python
  import pytest
  import os
  import sys

  def test_converter_markdown_para_html():
      from converter_relatorio import converter_markdown_para_html_premium
      
      caminho_md = "tests/test_report.md"
      caminho_html = "tests/test_report.html"
      
      with open(caminho_md, "w") as f:
          f.write("# Relatório Executivo\n\nEste é um teste de **controladoria**.")
          
      converter_markdown_para_html_premium(caminho_md, caminho_html)
      
      assert os.path.exists(caminho_html)
      with open(caminho_html, "r") as f:
          content = f.read()
          assert "<title>Relatório de Controladoria Industrial</title>" in content
          assert "Este é um teste de <strong>controladoria</strong>." in content
          
      if os.path.exists(caminho_md):
          os.remove(caminho_md)
      if os.path.exists(caminho_html):
          os.remove(caminho_html)
  ```

- [ ] **Step 2: Executar testes de setup e garantir que falham**
  Executar: `pytest tests/test_converter.py -v`
  Expected: FAIL

- [ ] **Step 3: Instalar biblioteca `markdown` se necessário**
  Instalar: `~/.local/bin/pip3 install --user --break-system-packages markdown` (adicionar no setup do script).

- [ ] **Step 4: Implementar `converter_relatorio.py`**
  Escrever a função de parse com template HTML Premium.
  ```python
  import markdown
  import os

  def converter_markdown_para_html_premium(caminho_md: str, caminho_html: str) -> None:
      if not os.path.exists(caminho_md):
          raise FileNotFoundError(f"Arquivo markdown nao encontrado: {caminho_md}")
          
      with open(caminho_md, "r", encoding="utf-8") as f:
          text_md = f.read()
          
      body_html = markdown.markdown(text_md, extensions=['tables'])
      
      html_completo = f"""<!DOCTYPE html>
  <html lang="pt-BR">
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Relatório de Controladoria Industrial</title>
      <style>
          body {{
              font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
              color: #333333;
              line-height: 1.6;
              background-color: #F8F9FA;
              margin: 0;
              padding: 40px 20px;
          }}
          .container {{
              max-width: 900px;
              background-color: #FFFFFF;
              padding: 40px;
              margin: 0 auto;
              border-radius: 8px;
              box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
              border-top: 6px solid #1F497D;
          }}
          h1 {{
              color: #1F497D;
              border-bottom: 2px solid #E9ECEF;
              padding-bottom: 10px;
              font-size: 28px;
              margin-top: 0;
          }}
          h2 {{
              color: #2C3E50;
              margin-top: 30px;
              border-bottom: 1px solid #E9ECEF;
              padding-bottom: 6px;
              font-size: 22px;
          }}
          h3 {{
              color: #34495E;
              font-size: 18px;
          }}
          p, li {{
              font-size: 15px;
              color: #555555;
          }}
          table {{
              width: 100%;
              border-collapse: collapse;
              margin: 20px 0;
              font-size: 14px;
          }}
          th {{
              background-color: #1F497D;
              color: #FFFFFF;
              font-weight: bold;
              padding: 10px;
              text-align: left;
              border: 1px solid #D3D3D3;
          }}
          td {{
              padding: 8px 10px;
              border: 1px solid #E9ECEF;
          }}
          tr:nth-child(even) {{
              background-color: #F8F9FA;
          }}
          .warning, blockquote {{
              background-color: #FFF3CD;
              border-left: 5px solid #FFC107;
              padding: 15px;
              margin: 20px 0;
              border-radius: 4px;
          }}
          .warning p, blockquote p {{
              margin: 0;
              color: #856404;
              font-weight: 500;
          }}
          .footer {{
              margin-top: 40px;
              font-size: 12px;
              color: #999999;
              text-align: center;
              border-top: 1px solid #E9ECEF;
              padding-top: 20px;
          }}
      </style>
  </head>
  <body>
      <div class="container">
          {body_html}
          <div class="footer">
              Relatório gerado automaticamente pelo Agente Especialista Custo Certo.
          </div>
      </div>
  </body>
  </html>
  """
      with open(caminho_html, "w", encoding="utf-8") as f:
          f.write(html_completo)
  ```

- [ ] **Step 5: Executar testes de validação**
  Executar: `pytest tests/test_converter.py -v`
  Expected: PASS

- [ ] **Step 6: Realizar commit**
  ```bash
  git add converter_relatorio.py tests/test_converter.py
  git commit -m "feat: implement markdown to HTML premium converter"
  ```

---

### Task 3: Integração no Script Principal (`main.py`)

**Files:**
- Modify: `main.py`
- Modify: `tests/test_end_to_end.py`

**Interfaces:**
- Consumes: Módulos `src/exportador.py` e `converter_relatorio.py`.
- Produces: Executável unificado `main.py` gerando `relatorio_controladoria.md`, `relatorio_controladoria.html` e `analise_de_custos.xlsx` ao fim do fluxo.

- [ ] **Step 1: Atualizar teste de integração em `tests/test_end_to_end.py`**
  Garantir que a simulação final gera tanto o arquivo HTML quanto a planilha Excel.
  Adicionar no teste:
  ```python
      # Verificar se os arquivos de relatorios foram gerados com sucesso
      assert os.path.exists("relatorio_controladoria.md")
      assert os.path.exists("relatorio_controladoria.html")
      assert os.path.exists("analise_de_custos.xlsx")
  ```

- [ ] **Step 2: Executar testes e verificar que falham**
  Executar: `pytest tests/test_end_to_end.py -v`
  Expected: FAIL (assertion error - arquivos não criados)

- [ ] **Step 3: Modificar `main.py`**
  Integrar as ferramentas no fluxo de encerramento do script:
  ```python
      # No final da funcao main(), após salvar o markdown:
      
      # 1. Executar os calculos novamente para passar os DataFrames ao exportador
      print("Exportando planilhas de analise para o Excel...")
      from tools import (
          calcular_margem_contribuicao, 
          calcular_custeio_absorcao, 
          analisar_desperdicios_eficiencia, 
          calcular_ponto_equilibrio
      )
      from exportador import exportar_analise_excel
      
      margens_df = calcular_margem_contribuicao(caminho_fin)
      pe_dict = calcular_ponto_equilibrio(caminho_fin, custos_fixos_mensais)
      abs_vol = calcular_custeio_absorcao(caminho_fin, caminho_op, custos_fixos_mensais, "volume")
      abs_horas = calcular_custeio_absorcao(caminho_fin, caminho_op, custos_fixos_mensais, "horas_maquina")
      abs_custo_direto = calcular_custeio_absorcao(caminho_fin, caminho_op, custos_fixos_mensais, "custo_direto")
      desperdicios_df = analisar_desperdicios_eficiencia(caminho_op, caminho_fin)
      
      exportar_analise_excel(
          "analise_de_custos.xlsx",
          margens_df, abs_vol, abs_horas, abs_custo_direto, desperdicios_df,
          pe_dict, custos_fixos_mensais
      )
      print("Planilha salva em 'analise_de_custos.xlsx'")
      
      # 2. Converter Markdown para HTML Premium
      print("Convertendo relatorio para formato C-Level (HTML)...")
      from converter_relatorio import converter_markdown_para_html_premium
      converter_markdown_para_html_premium("relatorio_controladoria.md", "relatorio_controladoria.html")
      print("Relatorio HTML Premium gerado com sucesso em 'relatorio_controladoria.html'")
  ```

- [ ] **Step 4: Executar suite de testes para verificar que passam**
  Executar: `pytest`
  Expected: PASS

- [ ] **Step 5: Realizar commit**
  ```bash
  git add main.py tests/test_end_to_end.py
  git commit -m "feat: integrate Excel export and HTML reporting in main.py"
  ```
