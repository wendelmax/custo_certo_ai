import pandas as pd
from custom_crew import Crew
from tools import calcular_margem_contribuicao, calcular_custeio_absorcao, analisar_desperdicios_eficiencia, calcular_ponto_equilibrio
from agents import criar_analista_financeiro, criar_auditor_processos, criar_diretor_controladoria
from tasks import criar_tarefa_financeira, criar_tarefa_operacional, criar_tarefa_diretoria

def df_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    headers = list(df.columns)
    markdown_lines = []
    markdown_lines.append("| " + " | ".join(headers) + " |")
    markdown_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in df.iterrows():
        formatted_vals = []
        for val in row:
            if pd.api.types.is_number(val) and not isinstance(val, bool):
                if pd.isna(val):
                    formatted_vals.append("")
                elif pd.api.types.is_integer(val):
                    formatted_vals.append(str(int(val)))
                else:
                    formatted_vals.append(f"{val:.2f}")
            else:
                formatted_vals.append(str(val) if not pd.isna(val) else "")
        markdown_lines.append("| " + " | ".join(formatted_vals) + " |")
    return "\n".join(markdown_lines) + "\n"

def montar_equipe_analise(caminho_fin: str, caminho_op: str, custos_fixos: float, caminhos_opcionais: dict = None) -> Crew:
    # 1. Executar os calculos do motor matematico (Tools)
    margens_df = calcular_margem_contribuicao(caminho_fin)
    pe_dict = calcular_ponto_equilibrio(caminho_fin, custos_fixos)
    
    # Calcular absorcao sob os 3 criterios
    abs_vol = calcular_custeio_absorcao(caminho_fin, caminho_op, custos_fixos, "volume")
    abs_horas = calcular_custeio_absorcao(caminho_fin, caminho_op, custos_fixos, "horas_maquina")
    abs_custo_direto = calcular_custeio_absorcao(caminho_fin, caminho_op, custos_fixos, "custo_direto")
    
    # Analisar desperdicios operacionais
    desperdicios_df = analisar_desperdicios_eficiencia(caminho_op, caminho_fin)
    
    # 2. Formatar os dados em strings estruturadas em Markdown para a LLM
    output_financeiro = "## Resumo de Margens de Contribuicao:\n"
    output_financeiro += df_to_markdown(margens_df[["produto_id", "nome_produto", "margem_contribuição_unitaria", "margem_contribuição_percentual", "margem_contribuição_total"]])
    output_financeiro += f"\n\n**Ponto de Equilibrio Geral da Fábrica:** Faturamento Minimo de R$ {pe_dict['faturamento_equilibrio_geral']:,.2f}\n"
    
    output_financeiro += "\n## Comparativo Custeio por Absorcao (3 Rateios):\n"
    output_financeiro += "### 1. Rateio por Volume:\n"
    output_financeiro += df_to_markdown(abs_vol[["produto_id", "custo_absorcao_unitario", "lucro_unitario_absorcao"]])
    output_financeiro += "\n### 2. Rateio por Horas Maquina:\n"
    output_financeiro += df_to_markdown(abs_horas[["produto_id", "horas_maquina_ativas", "custo_absorcao_unitario", "lucro_unitario_absorcao"]])
    output_financeiro += "\n### 3. Rateio por Custo Direto:\n"
    output_financeiro += df_to_markdown(abs_custo_direto[["produto_id", "custo_absorcao_unitario", "lucro_unitario_absorcao"]])
    
    output_operacional = df_to_markdown(desperdicios_df[["lote_id", "produto_id", "quantidade_produzida", "quantidade_refugada", "taxa_refugo_percentual", "horas_maquina_parada", "custo_refugo", "custo_parada_maquina", "perda_ineficiencia_total"]])
    
    # 2b. Processar arquivos opcionais de enriquecimento
    contexto_enriquecimento = ""
    if caminhos_opcionais:
        if "bom" in caminhos_opcionais and caminhos_opcionais["bom"]:
            try:
                bom_df = pd.read_csv(caminhos_opcionais["bom"]) if caminhos_opcionais["bom"].lower().endswith(".csv") else pd.read_excel(caminhos_opcionais["bom"])
                contexto_enriquecimento += f"\n### Ficha Técnica / Estrutura de Produtos (BOM):\n{df_to_markdown(bom_df)}\n"
            except Exception as e:
                contexto_enriquecimento += f"\nErro ao ler Ficha Técnica (BOM): {e}\n"

        if "budget" in caminhos_opcionais and caminhos_opcionais["budget"]:
            try:
                budget_df = pd.read_csv(caminhos_opcionais["budget"]) if caminhos_opcionais["budget"].lower().endswith(".csv") else pd.read_excel(caminhos_opcionais["budget"])
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

    # 3. Instanciar agentes
    analista = criar_analista_financeiro()
    auditor = criar_auditor_processos()
    diretor = criar_diretor_controladoria()
    
    # 4. Instanciar tarefas com contexto enriquecido
    t1 = criar_tarefa_financeira(analista, output_financeiro + contexto_enriquecimento)
    t2 = criar_tarefa_operacional(auditor, output_operacional + contexto_enriquecimento)
    t3 = criar_tarefa_diretoria(diretor)
    
    # 5. Montar a Crew
    return Crew(
        agents=[analista, auditor, diretor],
        tasks=[t1, t2, t3]
    )
