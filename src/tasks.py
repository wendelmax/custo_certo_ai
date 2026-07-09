from custom_crew import Task, Agent

def criar_tarefa_financeira(agente: Agent, output_financeiro_str: str) -> Task:
    return Task(
        description=(
            f"Analise o seguinte resumo matematico de margens e custeio por absorcao:\n"
            f"{output_financeiro_str}\n\n"
            f"Organize as informacoes em tabelas organizadas. Identifique os produtos com menores margens e compare como o custo "
            f"por absorcao unitario varia de acordo com cada um dos 3 criterios de rateio (Volume, Horas Maquina, Custo Direto)."
        ),
        expected_output="Relatorio com tabelas de margens e comparativo detalhado dos 3 metodos de rateio de custos fixos.",
        agent=agente
    )

def criar_tarefa_operacional(agente: Agent, output_operacional_str: str) -> Task:
    return Task(
        description=(
            f"Analise a seguinte planilha consolidada de ineficiencias de fabrica:\n"
            f"{output_operacional_str}\n\n"
            f"Mapeie onde estao as maiores perdas monetarias (custo de refugo vs. custo de parada de maquina). "
            f"Aponte quais produtos ou lotes tem maior risco operacional por falhas de processo."
        ),
        expected_output="Mapeamento e diagnostico detalhado das perdas operacionais por refugo e horas paradas de maquina.",
        agent=agente
    )

def criar_tarefa_diretoria(agente: Agent) -> Task:
    return Task(
        description=(
            "Cruze as analises financeira e operacional geradas anteriormente. Crie um relatorio de controladoria industrial.\n"
            "O relatorio deve:\n"
            "1. Explicar como as falhas de producao (refugos, paradas) estao diretamente prejudicando as margens de produtos especificos.\n"
            "2. Demonstrar o impacto de se escolher diferentes criterios de rateio de custos (Volume vs. Horas vs. Custos Diretos).\n"
            "3. Propor 3 recomendacoes praticas e acionaveis para a diretoria aumentar a margem ou mitigar os riscos operacionais identificados.\n\n"
            "Use formatacao elegante em markdown com titulos claros."
        ),
        expected_output="Relatorio Executivo final consolidado em Markdown com analise de sensibilidade de rateio e plano de acao.",
        agent=agente
    )
