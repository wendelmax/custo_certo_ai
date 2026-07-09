import pandas as pd
import warnings

def validar_colunas_csv(caminho_csv: str, colunas_esperadas: list):
    df = pd.read_csv(caminho_csv, nrows=0)
    colunas_presentes = set(df.columns)
    colunas_faltantes = [col for col in colunas_esperadas if col not in colunas_presentes]
    if colunas_faltantes:
        raise ValueError(f"O arquivo '{caminho_csv}' esta incompleto. Colunas ausentes: {colunas_faltantes}")

def calcular_margem_contribuicao(caminho_csv: str) -> pd.DataFrame:
    validar_colunas_csv(caminho_csv, ["produto_id", "preco_venda_unitario", "custo_variavel_unitario", "despesas_variaveis_unit", "volume_vendas_mensal"])
    
    df = pd.read_csv(caminho_csv)
    
    cols = ["preco_venda_unitario", "custo_variavel_unitario", "despesas_variaveis_unit", "volume_vendas_mensal"]
    has_nans = False
    for col in cols:
        if col in df.columns and df[col].isna().any():
            has_nans = True
            df[col] = df[col].fillna(0)
            
    if has_nans:
        warnings.warn("Missing/empty values detected. Pre-filling with 0.", UserWarning)
        
    df["preco_venda_unitario"] = df["preco_venda_unitario"].astype(float)
    df["custo_variavel_unitario"] = df["custo_variavel_unitario"].astype(float)
    df["despesas_variaveis_unit"] = df["despesas_variaveis_unit"].astype(float)
    df["volume_vendas_mensal"] = df["volume_vendas_mensal"].astype(int)
    
    df["margem_contribuição_unitaria"] = df["preco_venda_unitario"] - (df["custo_variavel_unitario"] + df["despesas_variaveis_unit"])
    df["margem_contribuição_percentual"] = 0.0
    non_zero_mask = df["preco_venda_unitario"] != 0
    df.loc[non_zero_mask, "margem_contribuição_percentual"] = df.loc[non_zero_mask, "margem_contribuição_unitaria"] / df.loc[non_zero_mask, "preco_venda_unitario"]
    df["margem_contribuição_total"] = df["margem_contribuição_unitaria"] * df["volume_vendas_mensal"]
    return df


def calcular_ponto_equilibrio(caminho_csv: str, custos_fixos: float) -> dict:
    validar_colunas_csv(caminho_csv, ["produto_id", "preco_venda_unitario", "custo_variavel_unitario", "despesas_variaveis_unit", "volume_vendas_mensal"])
    
    df = calcular_margem_contribuicao(caminho_csv)
    
    # Ponto de equilíbrio usando margem de contribução média ponderada baseada no faturamento
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


def calcular_custeio_absorcao(caminho_fin: str, caminho_op: str, custos_fixos: float, criterio: str) -> pd.DataFrame:
    validar_colunas_csv(caminho_fin, ["produto_id", "preco_venda_unitario", "custo_variavel_unitario", "despesas_variaveis_unit"])
    validar_colunas_csv(caminho_op, ["produto_id", "quantidade_produzida", "horas_maquina_ativas"])
    
    fin_df = pd.read_csv(caminho_fin)
    op_df = pd.read_csv(caminho_op)
    
    # Consolidar produções por produto
    producao_total = op_df.groupby("produto_id")["quantidade_produzida"].sum().reset_index()
    horas_maquina = op_df.groupby("produto_id")["horas_maquina_ativas"].sum().reset_index() # para horas de máquina
    
    df = pd.merge(fin_df, producao_total, on="produto_id", how="left").fillna(0)
    df = pd.merge(df, horas_maquina, on="produto_id", how="left").fillna(0)
    
    total_produzido_todos = df["quantidade_produzida"].sum()
    total_custo_direto_carteira = (df["custo_variavel_unitario"] * df["quantidade_produzida"]).sum()
    total_horas_maquina = df["horas_maquina_ativas"].sum()
    
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
            df["rateio_custo_fixo"] = (df["horas_maquina_ativas"] / total_horas_maquina) * custos_fixos
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
    validar_colunas_csv(caminho_op, ["lote_id", "produto_id", "quantidade_produzida", "quantidade_refugada", "horas_maquina_parada", "custo_hora_maquina"])
    validar_colunas_csv(caminho_fin, ["produto_id", "custo_variavel_unitario"])
    
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
