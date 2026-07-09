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
        
    # Criar dados dummies adequados
    df_margens = pd.DataFrame([{
        "produto_id": "P01",
        "nome_produto": "Produto A",
        "preco_venda_unitario": 100.00,
        "custo_variavel_unitario": 50.00,
        "despesas_variaveis_unit": 10.00,
        "margem_contribuição_unitaria": 40.00,
        "margem_contribuição_percentual": 0.40,
        "margem_contribuição_total": 4000.00,
        "volume_vendas_mensal": 100
    }])
    
    df_absorcao_vol = pd.DataFrame([{
        "produto_id": "P01",
        "nome_produto": "Produto A",
        "preco_venda_unitario": 100.00,
        "custo_absorcao_unitario": 80.00,
        "lucro_unitario_absorcao": 20.00
    }])
    
    df_absorcao_horas = pd.DataFrame([{
        "produto_id": "P01",
        "nome_produto": "Produto A",
        "preco_venda_unitario": 100.00,
        "custo_absorcao_unitario": 85.00,
        "lucro_unitario_absorcao": 15.00
    }])
    
    df_absorcao_custo = pd.DataFrame([{
        "produto_id": "P01",
        "nome_produto": "Produto A",
        "preco_venda_unitario": 100.00,
        "custo_absorcao_unitario": 75.00,
        "lucro_unitario_absorcao": 25.00
    }])
    
    df_ineficiencias = pd.DataFrame([{
        "produto_id": "P01",
        "quantidade_produzida": 100,
        "quantidade_refugada": 5,
        "taxa_refugo_percentual": 0.05,
        "horas_maquina_parada": 2.5,
        "custo_refugo": 250.00,
        "custo_parada_maquina": 500.00,
        "perda_ineficiencia_total": 750.00
    }])
    
    pe_dummy = {
        "faturamento_atual_total": 10000.00,
        "faturamento_equilibrio_geral": 50000.00,
        "margem_contribuição_media_ponderada": 0.45
    }
    
    exportar_analise_excel(
        caminho_teste,
        df_margens, df_absorcao_vol, df_absorcao_horas, df_absorcao_custo, df_ineficiencias,
        pe_dummy, 12000.00
    )
    
    assert os.path.exists(caminho_teste)
    # Validar se as planilhas corretas foram criadas
    xl = pd.ExcelFile(caminho_teste)
    assert "Dashboard C-Level" in xl.sheet_names
    assert "Margens e PE" in xl.sheet_names
    assert "Rateios por Absorção" in xl.sheet_names
    assert "Ineficiências Fabris" in xl.sheet_names
    
    # Limpeza
    if os.path.exists(caminho_teste):
        os.remove(caminho_teste)

def test_exportar_analise_excel_empty_data():
    from exportador import exportar_analise_excel
    
    caminho_teste = "tests/test_analise_exportada_vazia.xlsx"
    if os.path.exists(caminho_teste):
        os.remove(caminho_teste)
        
    df_margens = pd.DataFrame(columns=[
        "produto_id", "nome_produto", "preco_venda_unitario", "custo_variavel_unitario",
        "despesas_variaveis_unit", "margem_contribuição_unitaria", "margem_contribuição_percentual",
        "margem_contribuição_total", "volume_vendas_mensal"
    ])
    
    df_absorcao_vol = pd.DataFrame(columns=[
        "produto_id", "nome_produto", "preco_venda_unitario", "custo_absorcao_unitario", "lucro_unitario_absorcao"
    ])
    
    df_absorcao_horas = pd.DataFrame(columns=[
        "produto_id", "nome_produto", "preco_venda_unitario", "custo_absorcao_unitario", "lucro_unitario_absorcao"
    ])
    
    df_absorcao_custo = pd.DataFrame(columns=[
        "produto_id", "nome_produto", "preco_venda_unitario", "custo_absorcao_unitario", "lucro_unitario_absorcao"
    ])
    
    df_ineficiencias = pd.DataFrame(columns=[
        "produto_id", "quantidade_produzida", "quantidade_refugada", "taxa_refugo_percentual",
        "horas_maquina_parada", "custo_refugo", "custo_parada_maquina", "perda_ineficiencia_total"
    ])
    
    pe_dummy = {}
    
    exportar_analise_excel(
        caminho_teste,
        df_margens, df_absorcao_vol, df_absorcao_horas, df_absorcao_custo, df_ineficiencias,
        pe_dummy, 0.0
    )
    
    assert os.path.exists(caminho_teste)
    # Validar se as planilhas corretas foram criadas
    xl = pd.ExcelFile(caminho_teste)
    assert "Dashboard C-Level" in xl.sheet_names
    assert "Margens e PE" in xl.sheet_names
    assert "Rateios por Absorção" in xl.sheet_names
    assert "Ineficiências Fabris" in xl.sheet_names
    
    # Limpeza
    if os.path.exists(caminho_teste):
        os.remove(caminho_teste)

