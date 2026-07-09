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
    assert "margem_contribuição_media_ponderada" in pe
    assert "faturamento_atual_total" in pe

def test_calcular_margem_contribuicao_file_not_found():
    from tools import calcular_margem_contribuicao
    with pytest.raises(FileNotFoundError):
        calcular_margem_contribuicao("data/non_existent_file.csv")

def test_calcular_ponto_equilibrio_zero_faturamento(tmp_path):
    from tools import calcular_ponto_equilibrio
    # Criar um CSV temporário onde o volume de vendas é 0
    csv_file = tmp_path / "zero_faturamento.csv"
    df_zero = pd.DataFrame({
        "produto_id": ["PROD-001"],
        "nome_produto": ["Prod Teste"],
        "preco_venda_unitario": [100.0],
        "custo_variavel_unitario": [50.0],
        "despesas_variaveis_unit": [10.0],
        "volume_vendas_mensal": [0]
    })
    df_zero.to_csv(csv_file, index=False)
    
    pe = calcular_ponto_equilibrio(str(csv_file), 10000.00)
    assert pe["faturamento_equilibrio_geral"] == 0.0
    assert pe["mensagem"] == "Volume de faturamento zerado."

def test_calcular_ponto_equilibrio_negative_margin(tmp_path):
    from tools import calcular_ponto_equilibrio
    # Criar um CSV temporário onde a margem é negativa
    csv_file = tmp_path / "negative_margin.csv"
    df_neg = pd.DataFrame({
        "produto_id": ["PROD-001"],
        "nome_produto": ["Prod Prejuízo"],
        "preco_venda_unitario": [100.0],
        "custo_variavel_unitario": [120.0],
        "despesas_variaveis_unit": [10.0],
        "volume_vendas_mensal": [10]
    })
    df_neg.to_csv(csv_file, index=False)
    
    pe = calcular_ponto_equilibrio(str(csv_file), 10000.00)
    # Margem ponderada será negativa, logo faturamento_equilibrio deve ser 0.0
    assert pe["faturamento_equilibrio_geral"] == 0.0
    assert pe["margem_contribuição_media_ponderada"] < 0
