import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_converter_markdown_para_html():
    from converter_relatorio import converter_markdown_para_html_premium
    
    caminho_md = "tests/test_report.md"
    caminho_html = "tests/test_report.html"
    
    with open(caminho_md, "w", encoding="utf-8") as f:
        f.write("# Relatório Executivo\n\nEste é um teste de **controladoria**.")
        
    converter_markdown_para_html_premium(caminho_md, caminho_html)
    
    assert os.path.exists(caminho_html)
    with open(caminho_html, "r", encoding="utf-8") as f:
        content = f.read()
        assert "<title>Relatório de Controladoria Industrial</title>" in content
        assert "Este é um teste de <strong>controladoria</strong>." in content
        
    if os.path.exists(caminho_md):
        os.remove(caminho_md)
    if os.path.exists(caminho_html):
        os.remove(caminho_html)

def test_converter_markdown_file_not_found():
    from converter_relatorio import converter_markdown_para_html_premium
    with pytest.raises(FileNotFoundError):
        converter_markdown_para_html_premium("tests/non_existent.md", "tests/output.html")

def test_converter_markdown_with_tables():
    from converter_relatorio import converter_markdown_para_html_premium
    
    caminho_md = "tests/test_table.md"
    caminho_html = "tests/test_table.html"
    
    table_content = """# Relatório com Tabelas

| Produto | Preço |
| --- | --- |
| Produto A | 100.00 |
| Produto B | 150.00 |
"""
    with open(caminho_md, "w", encoding="utf-8") as f:
        f.write(table_content)
        
    converter_markdown_para_html_premium(caminho_md, caminho_html)
    
    assert os.path.exists(caminho_html)
    with open(caminho_html, "r", encoding="utf-8") as f:
        content = f.read()
        assert "<table>" in content
        assert "<th>Produto</th>" in content
        assert "<td>Produto A</td>" in content
        
    if os.path.exists(caminho_md):
        os.remove(caminho_md)
    if os.path.exists(caminho_html):
        os.remove(caminho_html)
