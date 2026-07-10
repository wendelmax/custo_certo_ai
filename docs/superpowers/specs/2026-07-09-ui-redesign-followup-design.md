# UI/UX Follow-up Redesign — Custo Certo AI

## Contexto

O commit `54e9115` já implementou a maior parte de um redesign "premium SaaS" (hero, stepper, cards arredondados, gradientes, tooltips) em `templates/index.html`. Uma análise externa colada pelo usuário listou 17 pontos de melhoria; a maioria já está resolvida. Este spec cobre os 4 pontos que ainda faltam ou estão inconsistentes, decididos em sessão de brainstorming:

1. Unificar bordas e espaçamento entre seções
2. Indicador de tendência (real vs. orçado) nos KPIs de Margem e Refugo
3. Sidebar de navegação por âncoras
4. Tokens `@theme` do Tailwind v4 nas seções tocadas

Fora de escopo (adiado por decisão do usuário): sidebar como app-shell multi-view, migração `@theme` do arquivo inteiro, tendência no KPI de Ponto de Equilíbrio.

## 1. Bordas e espaçamento

**Arquivo:** `templates/index.html`

- Trocar a classe `card-border` por `card-ring` nos seguintes elementos (mantendo `rounded-2xl`/`rounded-3xl` como já está):
  - `.card` do stepper (linha ~242)
  - `<section id="form-section">` (linha ~291)
- As dropzones individuais (`#drop-financeiro`, `#drop-operacional`, `#drop-bom`, `#drop-budget`, `#drop-observacoes`) **mantêm** `card-border` + `border-style: dashed` — é a affordance de drop-target, não deve virar `card-ring`.
- Padding padronizado (Tailwind utilities, sem mudar a CSS custom property `--shadow`/`--border` em si):
  - Cards primários (form section, card do relatório): `p-8 sm:p-10` (form section já está correto; relatório em `p-6 sm:p-8` → sobe para `p-8 sm:p-10`)
  - Cards secundários (KPI cards, chart cards): `p-6 sm:p-7` → `p-7 sm:p-8`
  - Stepper: mantém `p-5` (é uma barra de status, não um card de conteúdo)

## 2. Tendência nos KPIs (real vs. orçado)

### Backend — `app.py`

- `caminhos_opcionais.get('budget')` (já existe, linha ~64) precisa ser lido dentro do bloco de cálculo de KPIs (linhas 72-105), não só repassado pro `montar_equipe_analise`.
- Nova função em `src/tools.py`: `calcular_tendencia_budget(caminho_budget, margem_media, custo_refugo_total)`:
  - Lê o arquivo com `pd.read_csv`/`pd.read_excel` conforme extensão (mesmo padrão usado em `src/crew.py:67-72`).
  - Espera colunas `categoria`, `orçado`, `real` (schema já usado no fixture de teste `tests/test_crew_setup.py:85-86`).
  - Normaliza `categoria` (`strip().lower()`, remove acentos) e casa contra dois conjuntos de aliases:
    - Margem: `{"margem", "margem de contribuição", "margem de contribuicao"}`
    - Refugo: `{"refugo", "custo de refugo", "perdas"}`
  - Para cada match, calcula `pct = (real - orçado) / orçado * 100` (proteger divisão por zero → retorna `None` para aquela chave).
  - Retorna `{'margem': {'pct': float, 'direcao': 'up'|'down'} | None, 'refugo': {...} | None}`.
  - Se o arquivo de budget não existe/não foi enviado, ou não há nenhum match de categoria, retorna `{'margem': None, 'refugo': None}` — sem lançar exceção (feature é best-effort, não pode quebrar a análise principal).
- Em `app.py`, após montar o dict `kpis` (linha ~105), se `caminhos_opcionais.get('budget')` existir, chamar `calcular_tendencia_budget(...)` e anexar:
  ```python
  kpis['trend_margem'] = tendencia['margem']
  kpis['trend_refugo'] = tendencia['refugo']
  ```
  Se não houver budget, esses campos ficam ausentes do dict (o frontend trata a ausência como "sem tendência").
- **Ponto de Equilíbrio não recebe tendência** — é um limiar calculado (faturamento mínimo), não um valor realizado comparável a orçamento.

### Frontend — `templates/index.html`

- No card de KPI "Margem Média" (linha ~433-447) e "Custo de Refugo" (linha ~449-463), adicionar um `<span>` de tendência abaixo do valor, escondido por padrão (sem conteúdo até `renderKPIs` popular).
- Em `renderKPIs(kpis)` (linha ~713), se `kpis.trend_margem`/`kpis.trend_refugo` existir e não for `null`, popular o span com seta (`↑`/`↓` conforme `direcao`) + `pct` formatado + texto "vs. orçado". Se ausente/`null`, span permanece vazio (mesmo comportamento visual de hoje).

## 3. Sidebar de navegação (âncoras)

**Arquivo:** `templates/index.html`

- `<main class="max-w-5xl ...">` (linha ~239) muda para `max-w-7xl` (mesma largura do `<header>`) e vira um flex container: sidebar (largura fixa ~240px, `hidden lg:block`) + coluna de conteúdo (`flex-1`, mantém o `max-w-5xl` interno para não esticar o texto do relatório).
- Sidebar fixa (`sticky top-20`) com 4 links:
  - Upload → `#form-section`
  - KPIs → `#kpi-grid`
  - Gráficos → novo `id="charts"` no grid de charts (linha ~467, hoje sem id)
  - Relatório → `#relatorio-conteudo` (ou o card pai, para o scroll não cortar o header do card)
- Cada link faz `scrollIntoView({behavior:'smooth', block:'start'})` via JS, mesmo padrão já usado nos botões do hero (linha ~208).
- Destaque do item ativo: um `IntersectionObserver` observando as 4 seções-alvo, adicionando uma classe de destaque (ex: cor `--primary` + fundo `--primary-light`) ao link correspondente quando a seção entra em viewport.
- Mobile (`< lg`): sidebar fica `hidden`; layout de página permanece single-column exatamente como está hoje — nenhuma mudança de comportamento mobile.

## 4. Tokens `@theme` (Tailwind v4)

**Arquivo:** `templates/index.html`, dentro de `<head>`, novo bloco:

```html
<style type="text/tailwindcss">
  @theme {
    --color-card: var(--bg-card);
    --color-card-hover: var(--bg-card-hover);
    --color-surface: var(--bg);
    --color-ink: var(--text);
    --color-ink-secondary: var(--text-secondary);
    --color-ink-muted: var(--text-muted);
    --color-primary: var(--primary);
    --color-primary-light: var(--primary-light);
    --radius-card: 1.25rem;
    --shadow-card: var(--shadow);
  }
</style>
```

- Como os valores de `@theme` apontam para as CSS custom properties já existentes em `:root`/`html.dark` (linhas 16-66), o toggle de tema (`html.classList.add('dark')`, linha ~545) continua funcionando sem precisar de `@custom-variant dark` — não há variant `dark:` novo sendo introduzido.
- Utilities novas disponíveis: `bg-card`, `text-ink`, `text-ink-secondary`, `text-ink-muted`, `bg-primary`, `text-primary`, `rounded-card`, `shadow-card`.
- **Escopo de aplicação:** somente nas seções já tocadas por este spec — header, hero, form section, KPI cards, sidebar nova. Substituir os `style="color: var(--text)"` / `style="background: var(--bg-card)"` inline por essas classes **apenas nesses trechos**.
- Relatório (`#relatorio-conteudo` e seu conteúdo), toast de erro (`.error-toast`) e file-chip (`.file-chip`) **permanecem em CSS vars puro** — fora de escopo desta entrega.

## Testes / verificação

- Backend: teste unitário para `calcular_tendencia_budget` cobrindo: match de categoria (case/acento variando), nenhum match, budget ausente, divisão por zero no orçado.
- Manual (via `/verify` ou skill `run`): subir o Flask, rodar uma análise com e sem arquivo de budget, conferir:
  - Com budget: badges de tendência aparecem em Margem e Refugo, não aparecem em Ponto de Equilíbrio.
  - Sem budget: os 3 KPI cards renderizam idênticos ao comportamento atual.
  - Dark mode: toggle continua funcionando: sidebar, novas utilities `@theme` e cards refletem o tema corretamente.
  - Sidebar: scroll suave, destaque do item ativo, sidebar oculta em viewport mobile.
