import os
import sys
from dotenv import load_dotenv

# Garantir que o diretório src esteja no path para importação correta de crew
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from crew import montar_equipe_analise

def main():
    load_dotenv()
    
    # Certificar-se que a chave da API existe (ex: GEMINI_API_KEY ou OPENAI_API_KEY)
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("AVISO: GEMINI_API_KEY ou OPENAI_API_KEY nao encontradas no arquivo .env.")
    
    caminho_fin = "data/custos_financeiros.csv"
    caminho_op = "data/logs_operacionais.csv"
    custos_fixos_mensais = 30000.00 # Custos fixos totais da fabrica
    
    print("Orquestrando equipe de controle de custos...")
    equipe = montar_equipe_analise(caminho_fin, caminho_op, custos_fixos_mensais)
    
    print("Executando analise com os agentes autônomos...")
    resultado = equipe.kickoff()
    
    print("\n=== DIAGNÓSTICO ESTRATÉGICO FINAL ===\n")
    print(resultado)
    
    # Salvar resultado final em arquivo
    with open("relatorio_controladoria.md", "w", encoding="utf-8") as f:
        f.write(resultado)
    print("\nRelatorio salvo em 'relatorio_controladoria.md'")

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

if __name__ == "__main__":
    main()
