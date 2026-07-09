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

def test_calcular_margem_contribuicao_missing_values(tmp_path):
    from tools import calcular_margem_contribuicao
    
    csv_file = tmp_path / "missing_values.csv"
    df_missing = pd.DataFrame({
        "produto_id": ["PROD-001", "PROD-002"],
        "nome_produto": ["Prod A", "Prod B"],
        "preco_venda_unitario": [100.0, None],
        "custo_variavel_unitario": [50.0, 30.0],
        "despesas_variaveis_unit": [None, 10.0],
        "volume_vendas_mensal": [10, None]
    })
    df_missing.to_csv(csv_file, index=False)
    
    with pytest.warns(UserWarning, match="Missing/empty values detected. Pre-filling with 0."):
        df_result = calcular_margem_contribuicao(str(csv_file))
        
    # Check that NaN values were filled with 0 / 0.0
    assert df_result.loc[1, "preco_venda_unitario"] == 0.0
    assert df_result.loc[0, "despesas_variaveis_unit"] == 0.0
    assert df_result.loc[1, "volume_vendas_mensal"] == 0

def test_calcular_margem_contribuicao_zero_price(tmp_path):
    from tools import calcular_margem_contribuicao
    
    csv_file = tmp_path / "zero_price.csv"
    df_zero_price = pd.DataFrame({
        "produto_id": ["PROD-001", "PROD-002"],
        "nome_produto": ["Prod A", "Prod B"],
        "preco_venda_unitario": [0.0, 100.0],
        "custo_variavel_unitario": [50.0, 30.0],
        "despesas_variaveis_unit": [10.0, 10.0],
        "volume_vendas_mensal": [10, 5]
    })
    df_zero_price.to_csv(csv_file, index=False)
    
    # It should not crash, and for PROD-001 the percentual margin should be 0.0
    df_result = calcular_margem_contribuicao(str(csv_file))
    
    prod_1 = df_result[df_result["produto_id"] == "PROD-001"].iloc[0]
    prod_2 = df_result[df_result["produto_id"] == "PROD-002"].iloc[0]
    
    assert prod_1["margem_contribuição_percentual"] == 0.0
    assert prod_2["margem_contribuição_percentual"] == (60.0 / 100.0)


def test_calcular_custeio_absorcao():
    from tools import calcular_custeio_absorcao
    # Custo fixo = 12000.00
    
    # 1. Critério: volume
    df_vol = calcular_custeio_absorcao(
        "data/custos_financeiros.csv", 
        "data/logs_operacionais.csv", 
        12000.00, 
        "volume"
    )
    assert "custo_absorcao_unitario" in df_vol.columns
    assert len(df_vol) == 3
    
    prod_1 = df_vol[df_vol["produto_id"] == "PROD-001"].iloc[0]
    assert prod_1["rateio_custo_fixo"] == pytest.approx(4000.00)
    assert prod_1["custo_fixo_unitario"] == pytest.approx(4.00)
    assert prod_1["custo_absorcao_unitario"] == pytest.approx(89.00)
    assert prod_1["lucro_unitario_absorcao"] == pytest.approx(61.00)
    assert prod_1["lucro_total_absorcao"] == pytest.approx(61000.00)

    prod_2 = df_vol[df_vol["produto_id"] == "PROD-002"].iloc[0]
    assert prod_2["rateio_custo_fixo"] == pytest.approx(6000.00)
    assert prod_2["custo_fixo_unitario"] == pytest.approx(4.00)
    assert prod_2["custo_absorcao_unitario"] == pytest.approx(57.00)
    assert prod_2["lucro_unitario_absorcao"] == pytest.approx(23.00)
    assert prod_2["lucro_total_absorcao"] == pytest.approx(34500.00)

    prod_3 = df_vol[df_vol["produto_id"] == "PROD-003"].iloc[0]
    assert prod_3["rateio_custo_fixo"] == pytest.approx(2000.00)
    assert prod_3["custo_fixo_unitario"] == pytest.approx(4.00)
    assert prod_3["custo_absorcao_unitario"] == pytest.approx(144.00)
    assert prod_3["lucro_unitario_absorcao"] == pytest.approx(56.00)
    assert prod_3["lucro_total_absorcao"] == pytest.approx(28000.00)

    # 2. Critério: horas_maquina
    df_hm = calcular_custeio_absorcao(
        "data/custos_financeiros.csv", 
        "data/logs_operacionais.csv", 
        12000.00, 
        "horas_maquina"
    )
    prod_1_hm = df_hm[df_hm["produto_id"] == "PROD-001"].iloc[0]
    assert prod_1_hm["rateio_custo_fixo"] == pytest.approx(3840.00)
    assert prod_1_hm["custo_fixo_unitario"] == pytest.approx(3.84)
    assert prod_1_hm["custo_absorcao_unitario"] == pytest.approx(88.84)
    assert prod_1_hm["lucro_unitario_absorcao"] == pytest.approx(61.16)
    assert prod_1_hm["lucro_total_absorcao"] == pytest.approx(61160.00)

    prod_2_hm = df_hm[df_hm["produto_id"] == "PROD-002"].iloc[0]
    assert prod_2_hm["rateio_custo_fixo"] == pytest.approx(2400.00)
    assert prod_2_hm["custo_fixo_unitario"] == pytest.approx(1.60)
    assert prod_2_hm["custo_absorcao_unitario"] == pytest.approx(54.60)
    assert prod_2_hm["lucro_unitario_absorcao"] == pytest.approx(25.40)
    assert prod_2_hm["lucro_total_absorcao"] == pytest.approx(38100.00)

    prod_3_hm = df_hm[df_hm["produto_id"] == "PROD-003"].iloc[0]
    assert prod_3_hm["rateio_custo_fixo"] == pytest.approx(5760.00)
    assert prod_3_hm["custo_fixo_unitario"] == pytest.approx(11.52)
    assert prod_3_hm["custo_absorcao_unitario"] == pytest.approx(151.52)
    assert prod_3_hm["lucro_unitario_absorcao"] == pytest.approx(48.48)
    assert prod_3_hm["lucro_total_absorcao"] == pytest.approx(24240.00)

    # 3. Critério: custo_direto
    df_cd = calcular_custeio_absorcao(
        "data/custos_financeiros.csv", 
        "data/logs_operacionais.csv", 
        12000.00, 
        "custo_direto"
    )
    prod_1_cd = df_cd[df_cd["produto_id"] == "PROD-001"].iloc[0]
    assert prod_1_cd["rateio_custo_fixo"] == pytest.approx(4253.164556962025)
    assert prod_1_cd["custo_fixo_unitario"] == pytest.approx(4.253164556962025)
    assert prod_1_cd["custo_absorcao_unitario"] == pytest.approx(89.25316455696202)
    assert prod_1_cd["lucro_unitario_absorcao"] == pytest.approx(60.74683544303798)
    assert prod_1_cd["lucro_total_absorcao"] == pytest.approx(60746.83544303798)

    prod_2_cd = df_cd[df_cd["produto_id"] == "PROD-002"].iloc[0]
    assert prod_2_cd["rateio_custo_fixo"] == pytest.approx(4101.26582278481)
    assert prod_2_cd["custo_fixo_unitario"] == pytest.approx(2.7341772151898733)
    assert prod_2_cd["custo_absorcao_unitario"] == pytest.approx(55.734177215189873)
    assert prod_2_cd["lucro_unitario_absorcao"] == pytest.approx(24.265822784810127)
    assert prod_2_cd["lucro_total_absorcao"] == pytest.approx(36398.73417721519)

    prod_3_cd = df_cd[df_cd["produto_id"] == "PROD-003"].iloc[0]
    assert prod_3_cd["rateio_custo_fixo"] == pytest.approx(3645.5696202531645)
    assert prod_3_cd["custo_fixo_unitario"] == pytest.approx(7.291139240506329)
    assert prod_3_cd["custo_absorcao_unitario"] == pytest.approx(147.29113924050633)
    assert prod_3_cd["lucro_unitario_absorcao"] == pytest.approx(52.70886075949367)
    assert prod_3_cd["lucro_total_absorcao"] == pytest.approx(26354.430379746836)

    # Check that it doesn't crash on invalid criterion
    with pytest.raises(ValueError):
        calcular_custeio_absorcao(
            "data/custos_financeiros.csv", 
            "data/logs_operacionais.csv", 
            12000.00, 
            "criterio_invalido"
        )


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
    assert lote_101["taxa_refugo_percentual"] == pytest.approx(50 / (1000 + 50))

    lote_102 = df[df["lote_id"] == "LOTE-102"].iloc[0]
    assert lote_102["taxa_refugo_percentual"] == pytest.approx(20 / (1500 + 20))

    lote_103 = df[df["lote_id"] == "LOTE-103"].iloc[0]
    assert lote_103["taxa_refugo_percentual"] == pytest.approx(80 / (500 + 80))
