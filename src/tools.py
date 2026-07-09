import pandas as pd
import warnings

def calcular_margem_contribuicao(caminho_csv: str) -> pd.DataFrame:
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
    df["margem_contribuição_percentual"] = df["margem_contribuição_unitaria"] / df["preco_venda_unitario"]
    df.loc[df["preco_venda_unitario"] == 0, "margem_contribuição_percentual"] = 0.0
    df["margem_contribuição_total"] = df["margem_contribuição_unitaria"] * df["volume_vendas_mensal"]
    return df


def calcular_ponto_equilibrio(caminho_csv: str, custos_fixos: float) -> dict:
    df = calcular_margem_contribuicao(caminho_csv)
    
    # Ponto de equilíbrio usando margem de contribuição média ponderada baseada no faturamento
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
