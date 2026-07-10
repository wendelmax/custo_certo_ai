# UI/UX Follow-up Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the 4 remaining gaps from the premium SaaS redesign audit of `templates/index.html`: unify card borders/spacing, add a real budget-vs-actual trend indicator to two KPI cards, add an anchor-based sidebar, and introduce scoped Tailwind v4 `@theme` tokens.

**Architecture:** Single Flask app (`app.py`) rendering one Jinja template (`templates/index.html`) with vanilla JS (no build step, no JS framework, no JS test runner). Tailwind is the self-hosted v4.3.2 browser build (`static/tailwind.browser.js`), which supports `<style type="text/tailwindcss">` blocks for `@theme`. Business logic for the new budget-trend calculation goes in `src/tools.py` (pure functions, pytest-covered, same pattern as the existing `calcular_*` functions); wiring lives in `app.py`'s `/analisar` route. All other tasks are template/CSS/JS-only and are verified manually (there is no frontend test harness in this repo — `tests/` is Python/pytest only).

**Tech Stack:** Flask, pandas, pytest, Tailwind CSS v4 (browser build), Chart.js, vanilla JS.

## Global Constraints

- Spec source of truth: `docs/superpowers/specs/2026-07-09-ui-redesign-followup-design.md`.
- Dropzones keep their dashed `card-border` — never converted to `card-ring` (they are drop-targets, not content cards).
- The budget-vs-actual comparison uses the app's own computed values (`margem_media`, `custo_refugo_total`) as the "real" side — the `real` column inside the uploaded budget CSV is never read.
- Ponto de Equilíbrio never gets a trend badge (it's a calculated threshold, not a realized value).
- `@theme` tokens must reference the existing `--bg-card`/`--text`/etc. CSS custom properties (not new hard-coded colors) so the `.dark` class toggle keeps working with zero `@custom-variant` changes.
- `@theme` utilities are applied only in: header, hero, form section, KPI cards, new sidebar. Report content, error toast, and file-chip stay on CSS vars.
- Run `pytest` from the repo root (existing tests use paths like `"data/custos_financeiros.csv"` relative to cwd).

---

## Task 1: `@theme` token block (Tailwind v4)

**Files:**
- Modify: `templates/index.html` (inside `<head>`)

**Interfaces:**
- Produces: Tailwind utilities `bg-card`, `bg-card-hover`, `bg-surface`, `text-ink`, `text-ink-secondary`, `text-ink-muted`, `bg-primary`, `text-primary`, `bg-primary-light`, `rounded-card`, `shadow-card` — available to every later task in this plan.

- [ ] **Step 1: Insert the `@theme` block**

Find this exact block in `templates/index.html` (inside `<head>`, right before the existing `<style>` tag):

```html
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
```

Replace it with:

```html
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
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
  <style>
```

Note: the existing `--bg-card`, `--text`, etc. custom properties are defined further down in the same `<style>` tag on `:root` / `html.dark` (unchanged) — `@theme` just re-exposes them as Tailwind tokens. This does **not** replace the existing `:root`/`html.dark` block; both `<style>` tags coexist.

- [ ] **Step 2: Manually verify Tailwind compiles the new utilities**

Run the app and confirm no console errors:

```bash
python app.py &
sleep 2
curl -s http://127.0.0.1:5000/ | grep -o '@theme' | head -1
kill %1
```

Expected: prints `@theme` (confirms the block is present in the served HTML — Tailwind's browser build parses it client-side, so there's no server-side compile error to catch here; the real check is opening the page in a browser and confirming no JS console errors from `tailwind.browser.js`).

Open `http://127.0.0.1:5000/` in a browser, open devtools console, confirm no errors mentioning `@theme` or `text/tailwindcss`.

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat: add Tailwind v4 @theme token block mapped to existing CSS vars"
```

---

## Task 2: Unify borders and spacing

**Files:**
- Modify: `templates/index.html`

**Interfaces:**
- Consumes: nothing new (pure class-attribute edits on existing markup).

- [ ] **Step 1: Stepper card — border to ring, bump padding slightly**

Find:

```html
    <div class="card card-border p-5 mb-10 slide-in">
```

Replace with:

```html
    <div class="card card-ring p-5 sm:p-6 mb-10 slide-in">
```

- [ ] **Step 2: Form section — border to ring**

Find:

```html
    <section id="form-section" class="card card-border p-8 sm:p-10 mb-10 slide-in">
```

Replace with:

```html
    <section id="form-section" class="card card-ring p-8 sm:p-10 mb-10 slide-in">
```

Do **not** touch the 5 dropzone `div`s inside this section (`#drop-financeiro`, `#drop-operacional`, `#drop-bom`, `#drop-budget`, `#drop-observacoes`) — they keep `card-border` + `border-style: dashed`.

- [ ] **Step 3: KPI cards — bump padding**

Find (appears 3 times, identical string, once per KPI card):

```html
class="card card-ring card-hover p-6 sm:p-7 slide-in"
```

Replace all 3 occurrences with:

```html
class="card card-ring card-hover p-7 sm:p-8 slide-in"
```

- [ ] **Step 4: Chart cards — bump padding**

Find (appears 2 times, identical string, once per chart card):

```html
<div class="card card-ring card-hover p-6 sm:p-7">
```

Replace both occurrences with:

```html
<div class="card card-ring card-hover p-7 sm:p-8">
```

- [ ] **Step 5: Report content — bump padding to match primary cards**

Find:

```html
        <div class="p-6 sm:p-8" id="relatorio-conteudo">
```

Replace with:

```html
        <div class="p-8 sm:p-10" id="relatorio-conteudo">
```

- [ ] **Step 6: Manual verification**

```bash
grep -n "card-border" templates/index.html
```

Expected output: only the 5 dropzone divs and nothing else (no `form-section`, no stepper `div`).

```bash
grep -c "p-7 sm:p-8" templates/index.html
```

Expected: `5` (3 KPI cards + 2 chart cards).

Run the app and visually confirm in browser: stepper/form-section have no visible hard border (soft ring/shadow only), dropzones still show a dashed border, all cards have generous padding, both light and dark mode look correct.

- [ ] **Step 7: Commit**

```bash
git add templates/index.html
git commit -m "feat: unify card borders (ring over solid border) and padding scale"
```

---

## Task 3: Backend — `calcular_tendencia_budget`

**Files:**
- Modify: `src/tools.py`
- Test: `tests/test_tools.py`

**Interfaces:**
- Produces: `calcular_tendencia_budget(caminho_budget: str | None, margem_media: float, custo_refugo_total: float) -> dict` returning `{"margem": {"pct": float, "direcao": "up"|"down", "favoravel": bool} | None, "refugo": {...} | None}`. Consumed by Task 4 (`app.py`).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_tools.py`:

```python
def test_calcular_tendencia_budget_match_margem_e_refugo(tmp_path):
    from tools import calcular_tendencia_budget
    budget_file = tmp_path / "budget.csv"
    budget_file.write_text(
        "categoria,orçado,real\nMargem,60.0,65.0\nCusto de Refugo,1000.0,900.0\n",
        encoding="utf-8"
    )
    resultado = calcular_tendencia_budget(str(budget_file), margem_media=65.0, custo_refugo_total=900.0)

    assert resultado["margem"]["pct"] == pytest.approx(8.333333, rel=1e-4)
    assert resultado["margem"]["direcao"] == "up"
    assert resultado["margem"]["favoravel"] is True

    assert resultado["refugo"]["pct"] == pytest.approx(-10.0, rel=1e-4)
    assert resultado["refugo"]["direcao"] == "down"
    assert resultado["refugo"]["favoravel"] is True

def test_calcular_tendencia_budget_desfavoravel(tmp_path):
    from tools import calcular_tendencia_budget
    budget_file = tmp_path / "budget.csv"
    budget_file.write_text(
        "categoria,orçado,real\nMargem,60.0,50.0\nCusto de Refugo,1000.0,1200.0\n",
        encoding="utf-8"
    )
    resultado = calcular_tendencia_budget(str(budget_file), margem_media=50.0, custo_refugo_total=1200.0)

    assert resultado["margem"]["direcao"] == "down"
    assert resultado["margem"]["favoravel"] is False

    assert resultado["refugo"]["direcao"] == "up"
    assert resultado["refugo"]["favoravel"] is False

def test_calcular_tendencia_budget_sem_match(tmp_path):
    from tools import calcular_tendencia_budget
    budget_file = tmp_path / "budget.csv"
    budget_file.write_text("categoria,orçado,real\nMateria Prima,50000,52000\n", encoding="utf-8")
    resultado = calcular_tendencia_budget(str(budget_file), margem_media=65.0, custo_refugo_total=900.0)
    assert resultado == {"margem": None, "refugo": None}

def test_calcular_tendencia_budget_sem_arquivo():
    from tools import calcular_tendencia_budget
    resultado = calcular_tendencia_budget(None, margem_media=65.0, custo_refugo_total=900.0)
    assert resultado == {"margem": None, "refugo": None}

def test_calcular_tendencia_budget_orcado_zero(tmp_path):
    from tools import calcular_tendencia_budget
    budget_file = tmp_path / "budget.csv"
    budget_file.write_text("categoria,orçado,real\nMargem,0,65.0\n", encoding="utf-8")
    resultado = calcular_tendencia_budget(str(budget_file), margem_media=65.0, custo_refugo_total=900.0)
    assert resultado["margem"] is None

def test_calcular_tendencia_budget_alias_case_e_acento(tmp_path):
    from tools import calcular_tendencia_budget
    budget_file = tmp_path / "budget.csv"
    budget_file.write_text("categoria,orçado,real\nMARGEM DE CONTRIBUIÇÃO,60.0,65.0\n", encoding="utf-8")
    resultado = calcular_tendencia_budget(str(budget_file), margem_media=65.0, custo_refugo_total=900.0)
    assert resultado["margem"]["direcao"] == "up"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_tools.py -k tendencia_budget -v
```

Expected: all 6 tests FAIL with `ImportError: cannot import name 'calcular_tendencia_budget'`.

- [ ] **Step 3: Implement `calcular_tendencia_budget`**

Add to the top of `src/tools.py` (after `import warnings`):

```python
import unicodedata
```

Append to the end of `src/tools.py`:

```python
_ALIASES_MARGEM = {"margem", "margem de contribuicao"}
_ALIASES_REFUGO = {"refugo", "custo de refugo", "perdas"}


def _normalizar_categoria(texto) -> str:
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return texto


def calcular_tendencia_budget(caminho_budget, margem_media: float, custo_refugo_total: float) -> dict:
    resultado = {"margem": None, "refugo": None}
    if not caminho_budget:
        return resultado

    df = pd.read_csv(caminho_budget) if caminho_budget.lower().endswith(".csv") else pd.read_excel(caminho_budget)

    if "categoria" not in df.columns or "orçado" not in df.columns:
        return resultado

    df["_categoria_norm"] = df["categoria"].apply(_normalizar_categoria)

    def _match(aliases, valor_real, maior_e_melhor):
        linhas = df[df["_categoria_norm"].isin(aliases)]
        if linhas.empty:
            return None
        orcado = float(linhas.iloc[0]["orçado"])
        if orcado == 0:
            return None
        pct = (valor_real - orcado) / orcado * 100
        direcao = "up" if pct >= 0 else "down"
        favoravel = pct >= 0 if maior_e_melhor else pct <= 0
        return {"pct": pct, "direcao": direcao, "favoravel": favoravel}

    resultado["margem"] = _match(_ALIASES_MARGEM, margem_media, maior_e_melhor=True)
    resultado["refugo"] = _match(_ALIASES_REFUGO, custo_refugo_total, maior_e_melhor=False)
    return resultado
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_tools.py -k tendencia_budget -v
```

Expected: all 6 tests PASS.

- [ ] **Step 5: Run the full existing test_tools.py suite to check for regressions**

```bash
pytest tests/test_tools.py -v
```

Expected: all tests PASS (no existing test touches `calcular_tendencia_budget` or `unicodedata`, so nothing should break).

- [ ] **Step 6: Commit**

```bash
git add src/tools.py tests/test_tools.py
git commit -m "feat: add calcular_tendencia_budget for real-vs-orçado KPI trend"
```

---

## Task 4: Wire budget trend into `/analisar`

**Files:**
- Modify: `app.py`
- Test: `tests/test_app.py`

**Interfaces:**
- Consumes: `calcular_tendencia_budget(caminho_budget, margem_media, custo_refugo_total) -> dict` from Task 3.
- Produces: `/analisar` JSON response now includes `kpis.trend_margem` and `kpis.trend_refugo` keys whenever a `budget` file was uploaded (each either the trend dict or `None`). Consumed by Task 5 (frontend rendering).

- [ ] **Step 1: Write the failing test**

Append to `tests/test_app.py`:

```python
def test_analisar_com_budget_inclui_tendencia(client, monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "mock-key")
    monkeypatch.setenv("GEMINI_API_KEY", "mock-key")

    from custom_crew import Agent
    def mock_execute(self, task_description, context=""):
        return f"Mock output for {self.role}"
    monkeypatch.setattr(Agent, "execute", mock_execute)

    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    budget_file = tmp_path / "budget.csv"
    budget_file.write_text(
        "categoria,orçado,real\nMargem,10.0,10.0\nCusto de Refugo,100.0,100.0\n",
        encoding="utf-8"
    )

    with open(os.path.join(data_dir, "custos_financeiros.csv"), "rb") as fin, \
         open(os.path.join(data_dir, "logs_operacionais.csv"), "rb") as fop, \
         open(budget_file, "rb") as fbudget:
        res = client.post('/analisar', data={
            'custos_fixos': '30000.00',
            'file_financeiro': (fin, 'custos_financeiros.csv'),
            'file_operacional': (fop, 'logs_operacionais.csv'),
            'budget': (fbudget, 'budget.csv'),
        }, content_type='multipart/form-data')

    assert res.status_code == 200
    payload = res.get_json()
    assert payload['success'] is True
    assert 'trend_margem' in payload['kpis']
    assert 'trend_refugo' in payload['kpis']
    for trend in (payload['kpis']['trend_margem'], payload['kpis']['trend_refugo']):
        assert trend is None or ('pct' in trend and 'direcao' in trend and 'favoravel' in trend)


def test_analisar_sem_budget_nao_inclui_tendencia(client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "mock-key")
    monkeypatch.setenv("GEMINI_API_KEY", "mock-key")

    from custom_crew import Agent
    def mock_execute(self, task_description, context=""):
        return f"Mock output for {self.role}"
    monkeypatch.setattr(Agent, "execute", mock_execute)

    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    with open(os.path.join(data_dir, "custos_financeiros.csv"), "rb") as fin, \
         open(os.path.join(data_dir, "logs_operacionais.csv"), "rb") as fop:
        res = client.post('/analisar', data={
            'custos_fixos': '30000.00',
            'file_financeiro': (fin, 'custos_financeiros.csv'),
            'file_operacional': (fop, 'logs_operacionais.csv'),
        }, content_type='multipart/form-data')

    assert res.status_code == 200
    payload = res.get_json()
    assert 'trend_margem' not in payload['kpis']
    assert 'trend_refugo' not in payload['kpis']
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_app.py -k tendencia -v
```

Expected: `test_analisar_com_budget_inclui_tendencia` FAILS on `assert 'trend_margem' in payload['kpis']` (KeyError/AssertionError — key doesn't exist yet). `test_analisar_sem_budget_nao_inclui_tendencia` PASSES already (nothing to add yet) — that's fine, it becomes a real regression guard once Step 3 lands.

- [ ] **Step 3: Wire the function into the route**

In `app.py`, find the import block:

```python
from tools import (
    calcular_margem_contribuicao,
    calcular_custeio_absorcao,
    analisar_desperdicios_eficiencia,
    calcular_ponto_equilibrio
)
```

Replace with:

```python
from tools import (
    calcular_margem_contribuicao,
    calcular_custeio_absorcao,
    analisar_desperdicios_eficiencia,
    calcular_ponto_equilibrio,
    calcular_tendencia_budget
)
```

Then find:

```python
        kpis = {
            'ponto_equilibrio': pe_dict.get('faturamento_equilibrio_geral', 0.0),
            'margem_media': float(margens_df['margem_contribuição_unitaria'].mean()),
            'custo_refugo': custo_refugo_total,
            'top_produtos': top_produtos,
            'custo_variavel_total': custo_variavel_total,
            'custos_fixos': custos_fixos
        }

        return jsonify({
            'success': True,
            'kpis': kpis,
            'relatorio_html': html_resultado
        })
```

Replace with:

```python
        kpis = {
            'ponto_equilibrio': pe_dict.get('faturamento_equilibrio_geral', 0.0),
            'margem_media': float(margens_df['margem_contribuição_unitaria'].mean()),
            'custo_refugo': custo_refugo_total,
            'top_produtos': top_produtos,
            'custo_variavel_total': custo_variavel_total,
            'custos_fixos': custos_fixos
        }

        caminho_budget = caminhos_opcionais.get('budget')
        if caminho_budget:
            tendencia = calcular_tendencia_budget(caminho_budget, kpis['margem_media'], custo_refugo_total)
            kpis['trend_margem'] = tendencia['margem']
            kpis['trend_refugo'] = tendencia['refugo']

        return jsonify({
            'success': True,
            'kpis': kpis,
            'relatorio_html': html_resultado
        })
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_app.py -v
```

Expected: all tests in the file PASS, including the 2 new ones.

- [ ] **Step 5: Run the full test suite to check for regressions**

```bash
pytest -v
```

Expected: all tests PASS (this exercises `test_crew_setup.py`, `test_end_to_end.py`, `test_exportador.py`, `test_converter.py` too — none of them touch the `kpis` dict, so no regressions expected).

- [ ] **Step 6: Commit**

```bash
git add app.py tests/test_app.py
git commit -m "feat: attach budget trend to /analisar kpis when budget file is uploaded"
```

---

## Task 5: Frontend — KPI trend badges

**Files:**
- Modify: `templates/index.html`

**Interfaces:**
- Consumes: `kpis.trend_margem` / `kpis.trend_refugo` (`{pct, direcao, favoravel} | null | undefined`) from Task 4's `/analisar` response.

- [ ] **Step 1: Add the trend `<span>` to the Margem Média KPI card**

Find:

```html
          <p class="text-3xl sm:text-4xl font-extrabold tracking-tight" style="color: var(--text);" id="kpi-margem">—</p>
          <div class="mt-3 flex items-center gap-2">
            <span class="text-xs px-2 py-0.5 rounded-full" style="background: var(--success-bg); color: var(--success);">margem</span>
            <span class="text-xs" style="color: var(--text-muted);">contribuição média</span>
          </div>
```

Replace with:

```html
          <p class="text-3xl sm:text-4xl font-extrabold tracking-tight" style="color: var(--text);" id="kpi-margem">—</p>
          <div class="mt-3 flex items-center gap-2 flex-wrap">
            <span class="text-xs px-2 py-0.5 rounded-full" style="background: var(--success-bg); color: var(--success);">margem</span>
            <span class="text-xs" style="color: var(--text-muted);">contribuição média</span>
            <span class="text-xs font-semibold hidden" id="kpi-margem-trend"></span>
          </div>
```

- [ ] **Step 2: Add the trend `<span>` to the Custo de Refugo KPI card**

Find:

```html
          <p class="text-3xl sm:text-4xl font-extrabold tracking-tight" style="color: var(--text);" id="kpi-refugo">—</p>
          <div class="mt-3 flex items-center gap-2">
            <span class="text-xs px-2 py-0.5 rounded-full" style="background: var(--warning-bg); color: var(--warning);">desperdício</span>
            <span class="text-xs" style="color: var(--text-muted);">custo total</span>
          </div>
```

Replace with:

```html
          <p class="text-3xl sm:text-4xl font-extrabold tracking-tight" style="color: var(--text);" id="kpi-refugo">—</p>
          <div class="mt-3 flex items-center gap-2 flex-wrap">
            <span class="text-xs px-2 py-0.5 rounded-full" style="background: var(--warning-bg); color: var(--warning);">desperdício</span>
            <span class="text-xs" style="color: var(--text-muted);">custo total</span>
            <span class="text-xs font-semibold hidden" id="kpi-refugo-trend"></span>
          </div>
```

Do not add a trend span to the Ponto de Equilíbrio card.

- [ ] **Step 3: Render the trend in JS**

Find (inside the `<script>` IIFE):

```js
      function renderKPIs(kpis) {
        var equilibrio = document.getElementById('kpi-equilibrio');
        var margem = document.getElementById('kpi-margem');
        var refugo = document.getElementById('kpi-refugo');

        equilibrio.textContent = 'R$ ' + (kpis.ponto_equilibrio || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        margem.textContent = (kpis.margem_media || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '%';
        refugo.textContent = 'R$ ' + (kpis.custo_refugo || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

        renderCharts(kpis);
      }
```

Replace with:

```js
      function renderTrend(elId, trend) {
        var el = document.getElementById(elId);
        if (!trend) {
          el.classList.add('hidden');
          el.textContent = '';
          return;
        }
        var arrow = trend.direcao === 'up' ? '↑' : '↓';
        el.style.color = trend.favoravel ? 'var(--success)' : 'var(--danger)';
        el.textContent = arrow + ' ' + Math.abs(trend.pct).toFixed(1) + '% vs. orçado';
        el.classList.remove('hidden');
      }

      function renderKPIs(kpis) {
        var equilibrio = document.getElementById('kpi-equilibrio');
        var margem = document.getElementById('kpi-margem');
        var refugo = document.getElementById('kpi-refugo');

        equilibrio.textContent = 'R$ ' + (kpis.ponto_equilibrio || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        margem.textContent = (kpis.margem_media || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + '%';
        refugo.textContent = 'R$ ' + (kpis.custo_refugo || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

        renderTrend('kpi-margem-trend', kpis.trend_margem);
        renderTrend('kpi-refugo-trend', kpis.trend_refugo);

        renderCharts(kpis);
      }
```

- [ ] **Step 4: Manual verification**

Start the app and run a real analysis through the browser twice:

```bash
python app.py
```

1. Upload `data/custos_financeiros.csv` + `data/logs_operacionais.csv` + a budget CSV containing `categoria,orçado,real` rows `Margem,60,x` and `Custo de Refugo,1000,x` (values of `real` are irrelevant, ignored by design) → confirm both "Margem Média" and "Custo de Refugo" cards show a colored `↑`/`↓` badge with a percentage and "vs. orçado", and "Ponto de Equilíbrio" shows no badge.
2. Upload the same two required files **without** a budget file → confirm all 3 KPI cards render exactly as before (no badges, no layout shift, no JS console errors).

- [ ] **Step 5: Commit**

```bash
git add templates/index.html
git commit -m "feat: render budget-vs-actual trend badges on Margem and Refugo KPI cards"
```

---

## Task 6: Sidebar anchor navigation

**Files:**
- Modify: `templates/index.html`

**Interfaces:**
- Consumes: section ids `form-section`, `kpi-grid`, `relatorio-conteudo` (already exist) plus a new `charts` id added in this task; the `@theme` utilities (`bg-card`, `rounded-card`, `shadow-card`, `text-ink-muted`, `bg-primary-light`, `text-primary`) from Task 1.

- [ ] **Step 1: Add an id to the charts grid**

Find:

```html
      <!-- Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
```

Replace with:

```html
      <!-- Charts -->
      <div id="charts" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
```

- [ ] **Step 2: Add scroll-margin so the sticky header doesn't cover anchor targets**

Find (in the `<style>` block, near the `.tooltip` rules at the end):

```css
    .tooltip { position: relative; cursor: help; }
```

Replace with:

```css
    #form-section, #kpi-grid, #charts, #relatorio-conteudo { scroll-margin-top: 5rem; }

    .tooltip { position: relative; cursor: help; }
```

- [ ] **Step 3: Restructure `<main>` to add the sidebar, using the `@theme` utilities from Task 1**

This is new markup (not part of the ~63 existing inline-style occurrences elsewhere in the file), so it uses the `bg-card`/`rounded-card`/`shadow-card`/`text-ink-muted` utilities from Task 1 directly instead of the `.card`/`card-ring` component classes or inline `style="..."` — this is the concrete deliverable of the "scoped `@theme` application" part of the spec.

Find:

```html
  <main class="max-w-5xl mx-auto px-6 lg:px-8 pb-20">

    <!-- Progress Stepper -->
```

Replace with:

```html
  <main class="max-w-7xl mx-auto px-6 lg:px-8 pb-20 flex gap-10 items-start">

    <!-- Sidebar -->
    <aside class="hidden lg:block w-56 shrink-0 sticky top-24">
      <nav class="bg-card rounded-card shadow-card p-4 flex flex-col gap-1" id="sidebar-nav">
        <a href="#form-section" data-target="form-section" class="sidebar-link block px-3 py-2 rounded-lg text-[13px] font-semibold text-ink-muted hover:bg-card-hover transition-all">Upload</a>
        <a href="#kpi-grid" data-target="kpi-grid" class="sidebar-link block px-3 py-2 rounded-lg text-[13px] font-semibold text-ink-muted hover:bg-card-hover transition-all">KPIs</a>
        <a href="#charts" data-target="charts" class="sidebar-link block px-3 py-2 rounded-lg text-[13px] font-semibold text-ink-muted hover:bg-card-hover transition-all">Gráficos</a>
        <a href="#relatorio-conteudo" data-target="relatorio-conteudo" class="sidebar-link block px-3 py-2 rounded-lg text-[13px] font-semibold text-ink-muted hover:bg-card-hover transition-all">Relatório</a>
      </nav>
    </aside>

    <div class="flex-1 min-w-0 max-w-5xl mx-auto w-full">

    <!-- Progress Stepper -->
```

Then find the closing of `<main>`:

```html
    </section>

  </main>
```

Replace with:

```html
    </section>

    </div>

  </main>
```

- [ ] **Step 4: Add sidebar JS (scroll + active-state highlighting via utility-class toggling)**

Find (inside the `<script>` IIFE, right before the `FORM SUBMISSION` section comment):

```js
      // ========================
      // FORM SUBMISSION
      // ========================
```

Insert immediately before it:

```js
      // ========================
      // SIDEBAR NAV
      // ========================
      var sidebarLinks = document.querySelectorAll('#sidebar-nav .sidebar-link');

      function setActiveLink(link, active) {
        if (active) {
          link.classList.add('bg-primary-light', 'text-primary');
          link.classList.remove('text-ink-muted');
        } else {
          link.classList.remove('bg-primary-light', 'text-primary');
          link.classList.add('text-ink-muted');
        }
      }

      sidebarLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
          e.preventDefault();
          var target = document.getElementById(link.dataset.target);
          if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
      });

      if (sidebarLinks.length && 'IntersectionObserver' in window) {
        var sidebarTargets = Array.prototype.map.call(sidebarLinks, function(link) {
          return document.getElementById(link.dataset.target);
        }).filter(Boolean);

        var sidebarObserver = new IntersectionObserver(function(entries) {
          entries.forEach(function(entry) {
            if (!entry.isIntersecting) return;
            sidebarLinks.forEach(function(link) { setActiveLink(link, false); });
            var activeLink = document.querySelector('#sidebar-nav .sidebar-link[data-target="' + entry.target.id + '"]');
            if (activeLink) setActiveLink(activeLink, true);
          });
        }, { rootMargin: '-40% 0px -50% 0px', threshold: 0 });

        sidebarTargets.forEach(function(t) { sidebarObserver.observe(t); });
      }

      // ========================
      // FORM SUBMISSION
      // ========================
```

- [ ] **Step 5: Manual verification**

```bash
python app.py
```

In the browser (desktop viewport, e.g. 1280px wide):
1. Confirm the sidebar is visible to the left with 4 links, and the header/hero above are unaffected (still full-width, centered).
2. Click "Upload" → smooth-scrolls to the form section, header does not overlap the section title.
3. Run an analysis (upload financeiro + operacional), then click "KPIs" and "Gráficos" → confirm they scroll to the KPI grid and chart grid respectively.
4. Scroll manually through the page and confirm the sidebar highlights the correct link as each section enters view.
5. Resize to a mobile viewport (e.g. 375px wide) → confirm the sidebar disappears entirely and the page behaves exactly as it did before this task (single column, no leftover gap).
6. Toggle dark mode → confirm the sidebar background/ring/link colors adapt correctly.

- [ ] **Step 6: Run the full pytest suite one more time (this task only touches HTML/CSS/JS, but confirms no accidental server-side breakage)**

```bash
pytest -v
```

Expected: all tests PASS.

- [ ] **Step 7: Commit**

```bash
git add templates/index.html
git commit -m "feat: add anchor-based sidebar navigation with active-section highlighting"
```

---

## Post-implementation checklist

- [ ] All 6 tasks committed as separate commits (per-task, not squashed).
- [ ] `pytest -v` passes from repo root.
- [ ] Manual browser pass in both light and dark mode, desktop and mobile viewport, with and without a budget file uploaded.
- [ ] Re-read `docs/superpowers/specs/2026-07-09-ui-redesign-followup-design.md` and confirm every section (1-4) has a corresponding completed task above.
