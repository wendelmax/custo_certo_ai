# Custo Certo - Especialista em Controladoria e Custos Industriais

O **Custo Certo** é um ecossistema de agentes autônomos baseado em IA projetado para realizar análises profundas de controladoria industrial. O sistema lê planilhas de dados financeiros e operacionais de uma fábrica, executa cálculos matemáticos de exatidão de custos (margens, ponto de equilíbrio, custeio por absorção e custos de desperdício) e orquestra uma equipe de agentes cognitivos para gerar pareceres estratégicos C-Level em formato de planilhas Excel formatadas e relatórios HTML/Markdown.

---

## 🚀 Funcionalidades Principais

1. **Análise de Margens & Ponto de Equilíbrio**: Cálculos precisos de margem de contribuição (unitária, percentual e total) por produto e cálculo do ponto de equilíbrio fabril ponderado.
2. **Custeio por Absorção Multicritério**: Distribuição automática de custos fixos e despesas indiretas utilizando três critérios de rateio:
   * Por volume de produção.
   * Por horas de máquina ativas.
   * Proporcional ao custo direto.
3. **Diagnóstico de Ineficiências**: Monetização do impacto de refugos/sucatas por lote de fabricação e custos de ociosidade por paradas de máquina.
4. **Relatório Executivo C-Level**: Parecer estratégico produzido por agentes autônomos (Analista Financeiro, Engenheiro de Produção e CFO/Controller) e exportado em HTML Premium formatado com estilos embutidos.
5. **Exportador Excel Profissional**: Planilha `.xlsx` formatada com dashboard geral interativo (fórmulas) e abas separadas para cada análise.

---

## 📋 Pré-requisitos e Instalação

O sistema roda em Python 3.10+ (compatível com Python 3.14).

### 1. Instalar as dependências
Instale as bibliotecas necessárias usando o `pip`:
```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto e configure a chave de API da IA. O sistema prioriza o **Google Gemini** e possui fallback para a **OpenAI**:

```env
# Chave da API do Google Gemini (Recomendado)
GEMINI_API_KEY=sua_chave_gemini_aqui

# Chave da API da OpenAI (Fallback)
OPENAI_API_KEY=sua_chave_openai_aqui
```

---

## 📊 Estrutura de Dados de Entrada (CSVs)

O sistema consome dois arquivos na pasta `data/`:

*   **`data/custos_financeiros.csv`**: Cadastro de preços de venda líquidos, custos variáveis de matéria-prima, despesas variáveis (comissões/impostos) e volumes de venda mensais planejados por produto.
*   **`data/logs_operacionais.csv`**: Logs de fabricação das ordens de produção, contendo quantidade de itens bons, quantidade de refugos por lote, horas de máquina parada, custo de ociosidade por hora e horas de funcionamento ativo da máquina.

---

## ⚙️ Como Executar a Aplicação

Para iniciar o diagnóstico de controladoria fabril, basta executar o ponto de entrada principal:

```bash
python3 main.py
```

### Arquivos Gerados de Saída:
Ao término da execução, três arquivos serão criados na raiz do projeto:
1.  **`analise_de_custos.xlsx`**: Planilha Excel multitab formatada com cores corporativas, auto-ajuste de colunas e dashboard de KPIs.
2.  **`relatorio_controladoria.md`**: Parecer escrito da diretoria em formato Markdown simples.
3.  **`relatorio_controladoria.html`**: Relatório executivo C-Level em HTML Premium com folha de estilo moderna, pronto para apresentação ou envio por e-mail.

---

## 🧪 Executando os Testes Automatizados

O projeto possui uma suíte completa de **24 testes unitários e de integração** para garantir a segurança dos cálculos e das exportações.

Para rodar todos os testes:
```bash
pytest -v
```

---

## 🛠️ Detalhes da Arquitetura

O sistema é construído de forma modular para evitar alucinações matemáticas da IA:
*   **`src/tools.py`**: Todo o motor de cálculo matemático (Margens, PE, Absorção e Desperdício) é executado aqui em Python puro e Pandas, com validações proativas de colunas e tratamento contra divisão por zero.
*   **`src/custom_crew.py`**: Orquestrador leve compatível com as versões mais recentes do Python (3.14+), evitando os conflitos de dependência do `crewai` nativo.
*   **`src/exportador.py`**: Geração de planilhas usando `openpyxl` aplicando estilos personalizados de cores corporativas e formatação de números.
*   **`converter_relatorio.py`**: Conversor Markdown para HTML estruturado para e-mail corporativo (CSS inline).
