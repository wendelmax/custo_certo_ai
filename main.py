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
    with open("relatorio_controladoria.md", "w") as f:
        f.write(resultado)
    print("\nRelatorio salvo em 'relatorio_controladoria.md'")

if __name__ == "__main__":
    main()
