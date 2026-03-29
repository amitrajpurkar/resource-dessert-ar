# Architecture & Design: Resource Desert Analysis

**Project**: 2026 UNF CodeForAwhile Datathon — Problem Case 1
**Goal**: Identify Jacksonville ZIP codes that qualify as "Resource Deserts" and propose data-driven interventions to bridge the gap between resource supply and community demand.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Repository Layout](#2-repository-layout)
3. [Data Pipeline](#3-data-pipeline)
4. [Desert Score Algorithm](#4-desert-score-algorithm)
5. [Gap-Closure Simulation](#5-gap-closure-simulation)
6. [Flask Presentation Dashboard](#6-flask-presentation-dashboard)
7. [Testing Architecture](#7-testing-architecture)
8. [Configuration Design](#8-configuration-design)
9. [Technology Stack](#9-technology-stack)
10. [Design Principles](#10-design-principles)
11. [Produced Artefacts](#11-produced-artefacts)

---

## 1. System Overview

The system has two distinct runtime modes:

```
┌─────────────────────────────────────────────────────────────┐
│                     ANALYSIS PIPELINE                        │
│  (runs once, or on demand via the dashboard)                │
│                                                             │
│  data/raw/  ──►  ingestion  ──►  cleaning  ──►  features   │
│               (9 CSVs + GeoJSON)                            │
│                                                             │
│  features  ──►  models  ──►  visualization  ──►  outputs   │
│                                    │                        │
│                    reports/figures/*.png                    │
│                    reports/outputs/*.csv, *.json, *.html    │
└─────────────────────────────────────────────────────────────┘
                              │
                  Pre-generated output files
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   PRESENTATION DASHBOARD                     │
│  (Flask web app — reads pipeline outputs, serves judges)    │
│                                                             │
│  GET /          ──►  index.html (5-section single page)    │
│  GET /figures/  ──►  serves PNG charts                      │
│  GET /map       ──►  serves Folium choropleth HTML          │
│  POST /api/regenerate  ──►  re-runs pipeline in background  │
│  GET /api/regenerate/status  ──►  polling JSON              │
└─────────────────────────────────────────────────────────────┘
```

The pipeline and the dashboard are **decoupled**: the pipeline writes files to disk; the dashboard reads them. Neither calls the other directly except through the "Regenerate Data" background-thread mechanism.

---

## 2. Repository Layout

```
prob1-resource-desert/
│
├── app.py                          # Flask entry point — routes + background runner
│
├── src/                            # Importable pipeline modules (no notebooks here)
│   ├── config.py                   # ALL path constants + column name constants
│   ├── ingestion.py                # Stage 1: load raw datasets
│   ├── cleaning.py                 # Stage 2: standardise ZIPs, coerce dtypes
│   ├── features.py                 # Stage 3: merge, Desert Score, correlations
│   ├── models.py                   # Stage 4: gap-closure simulation
│   └── visualization.py            # Stage 5: charts + choropleth map
│
├── tests/
│   ├── conftest.py                 # Synthetic fixture DataFrames (shared by all tests)
│   ├── test_ingestion.py           # 6 unit tests
│   ├── test_cleaning.py            # 13 unit tests
│   ├── test_features.py            # 18 unit tests
│   ├── test_models.py              # 13 unit tests
│   ├── test_visualization.py       # 21 unit tests
│   ├── test_app.py                 # 33 Flask route + loader tests
│   └── e2e/
│       └── test_pipeline_e2e.py    # Full pipeline integration tests (@pytest.mark.e2e)
│
├── notebooks/
│   ├── resource_desert_analysis.ipynb   # Orchestration notebook (runs full pipeline)
│   └── eda/                             # 9 per-dataset exploratory notebooks
│       ├── eda_cdc_places.ipynb
│       ├── eda_census_demographics.ipynb
│       └── ...
│
├── data/
│   ├── raw/                        # Source files — NEVER modified
│   │   ├── CDCPlaces.csv
│   │   ├── Census-Demographics.csv
│   │   ├── Census-Housing&Poverty.csv
│   │   ├── FEMA.csv
│   │   ├── HealthCareAccess.csv
│   │   ├── HealthCareWorkers.csv
│   │   ├── Parks.csv
│   │   ├── SocialVulnerabilityIndex.csv
│   │   ├── USDA-FoodAccess.csv
│   │   ├── Metadata.xlsx           # Column data dictionary
│   │   └── jacksonville_zctas.geojson   # Census TIGER/Line ZCTA boundaries
│   ├── processed/
│   │   └── merged_jacksonville.csv # Stage 3a output: 35 ZIPs × 28 cols
│   └── outputs/                    # (legacy; main outputs are in reports/)
│
├── reports/
│   ├── figures/                    # 7 PNG charts at ≥150 DPI
│   └── outputs/                    # 3 structured output files
│       ├── desert_scores.csv
│       ├── intervention_recommendations.json
│       └── resource_desert_map.html
│
├── webapp/
│   ├── templates/
│   │   └── index.html              # Single Jinja2 template (5-section layout)
│   └── static/
│       ├── css/style.css           # ~300 lines, hand-written, CSS custom properties
│       └── js/app.js               # Regenerate button + fetch/setTimeout polling
│
├── docs/
│   ├── architecture.md             # This file
│   └── project_presentation.html  # Standalone static presentation (base64 images inlined)
│
├── specs/                          # Feature specifications (speckit workflow)
│   ├── 001-resource-desert-analysis/
│   ├── 002-per-dataset-eda-notebooks/
│   └── 003-flask-presentation-dashboard/
│
├── requirements.txt
├── pytest.ini
└── CLAUDE.md                       # AI agent guidance + active technology stack
```

**Structural rules**:
- `src/` contains only importable Python modules — no scripts, no notebooks.
- `notebooks/` is for exploration and orchestration only — no production logic lives there.
- `data/raw/` is read-only; the pipeline never writes there.
- All paths are defined as `pathlib.Path` constants in `src/config.py`.

---

## 3. Data Pipeline

The pipeline follows a strict five-stage architecture. Each stage is implemented in a dedicated `src/` module and passes DataFrames explicitly — no global state, no shared mutable objects.

```
┌──────────────┐    Dict[str, DataFrame]    ┌──────────────┐
│ ingestion.py │ ──────────────────────────► │ cleaning.py  │
│              │     (9 raw datasets)        │              │
│ load_raw_    │                             │ clean_       │
│ datasets()   │                             │ datasets()   │
└──────────────┘                             └──────────────┘
                                                     │
                                         Dict[str, DataFrame]
                                          (9 cleaned datasets)
                                                     │
                                                     ▼
                                           ┌──────────────┐
                                           │ features.py  │
                                           │              │
                                           │ merge_       │
                                           │ datasets()   │──► data/processed/
                                           │              │    merged_jacksonville.csv
                                           │ compute_     │
                                           │ desert_score │──► reports/outputs/
                                           │ ()           │    desert_scores.csv
                                           └──────────────┘
                                                     │
                                                DataFrame (35 ZIPs)
                                                     │
                                      ┌──────────────┴───────────────┐
                                      │                              │
                                      ▼                              ▼
                              ┌──────────────┐             ┌──────────────────┐
                              │  models.py   │             │ visualization.py │
                              │              │             │                  │
                              │ run_gap_     │             │ plot_desert_     │
                              │ closure_     │             │ scores_bar_chart │
                              │ simulation() │             │                  │
                              │              │             │ create_choropleth│
                              │ rank_        │             │ _map()           │
                              │ interventions│             │                  │
                              │ ()           │             │ plot_preventative│
                              └──────────────┘             │ _vs_outcome()    │
                                      │                    │                  │
                               JSON output                 │ plot_intervention│
                              reports/outputs/             │ _impact_heatmap()│
                              intervention_                │                  │
                              recommendations.json         │ plot_category_   │
                                                           │ view() × 4       │
                                                           └──────────────────┘
                                                                    │
                                                            7 PNGs + 1 HTML
                                                            reports/figures/
                                                            reports/outputs/
```

### Stage 1 — Ingestion (`src/ingestion.py`)

**Entry point**: `load_raw_datasets() → Dict[str, DataFrame]`

Loads all 9 source CSV files and 1 XLSX metadata file from `data/raw/`. Validates existence and non-empty shape before returning. Raises `FileNotFoundError` immediately if any file is missing — fail-fast design prevents silent pipeline failures downstream.

Each dataset is returned under a stable string key (e.g., `"cdc_places"`, `"census_demographics"`) defined as constants in `config.py`. The returned DataFrames are **raw and unmodified** — no type coercion, no filtering.

**Data shape at exit**: 9 DataFrames, each 37 rows × varying column counts (6–28 columns), all with a `"feature label"` column that encodes the ZIP code.

---

### Stage 2 — Cleaning (`src/cleaning.py`)

**Entry point**: `clean_datasets(raw: Dict[str, DataFrame]) → Dict[str, DataFrame]`

Applies three transformations to every dataset (except the metadata dictionary):

1. **ZIP standardisation** — Extracts the 5-digit ZIP code from the `"feature label"` column using a regex (`\d{5}`), zero-pads where needed, and stores it as `"zip_code"`. The original feature label is retained.

2. **Numeric coercion** — Replaces known NA-like strings (`"N/A"`, `"-"`, `"(null)"`) with `NaN`, then attempts `pd.to_numeric(..., errors='coerce')` on every column. Columns that cannot be numeric are left as-is.

3. **Duplicate dropping** — Deduplicates on `zip_code`, keeping the first occurrence. Logs the count of dropped rows before each drop.

All transformations are transparent — before/after row counts are logged. No silent data loss.

**Data shape at exit**: Same 9 keys, each DataFrame now has a clean `zip_code` column and consistent numeric dtypes.

---

### Stage 3a — Feature Engineering: Merge (`src/features.py` → `merge_datasets`)

Outer-joins all 9 cleaned DataFrames on `zip_code`. Filters out ZIPs with zero or missing population (removes 2 non-residential records). Derives three rate columns:

| Derived Column | Formula |
|---|---|
| `poverty_rate` | `poverty_count / total_population` (clipped to [0, 1]) |
| `uninsured_rate` | `uninsured_count / total_population` (clipped to [0, 1]) |
| `food_low_access_pct` | `food_low_access_20_mile / total_population` (clipped to [0, 1]) |

Null supply metrics (e.g., `primary_care_ratio`) are imputed with the column median. The final merged DataFrame (35 rows × 28 columns) is saved to `data/processed/merged_jacksonville.csv`.

---

### Stage 3b — Feature Engineering: Desert Score (`src/features.py` → `compute_desert_score`)

See [Section 4](#4-desert-score-algorithm) for the full algorithm.

**Output**: `reports/outputs/desert_scores.csv` — 35 rows × 11 columns.

---

### Stage 3c — Health Outcome Correlation (`src/features.py` → `compute_health_outcome_correlation`)

Computes 8 Pearson correlations between 4 preventative-asset metrics and 2 health outcome metrics:

| Asset | Outcomes tested |
|---|---|
| Primary care ratio (providers per capita) | Poor mental health rate, Obesity rate |
| Food low access % | Poor mental health rate, Obesity rate |
| Park coverage % | Poor mental health rate, Obesity rate |
| Uninsured rate | Poor mental health rate, Obesity rate |

Returns a long-format DataFrame `[asset, outcome, pearson_r]`. This powers the scatter plot in the Observations section and the strongest-correlation callout.

---

### Stage 4 — Gap-Closure Simulation (`src/models.py`)

See [Section 5](#5-gap-closure-simulation) for the full algorithm.

**Output**: `reports/outputs/intervention_recommendations.json` — 20 records.

---

### Stage 5 — Visualization (`src/visualization.py`)

Generates 7 static figures and 1 interactive Folium HTML map. All figures are saved at 150 DPI via `fig.savefig(path, dpi=150)`.

| Function | Output file | Content |
|---|---|---|
| `plot_desert_scores_bar_chart()` | `reports/figures/desert_scores_bar_chart.png` | Horizontal bar chart, top-10 ZIPs by Desert Score, RdYlGn_r colour gradient |
| `create_choropleth_map()` | `reports/outputs/resource_desert_map.html` | Interactive Folium map, ZCTA5 boundaries from Jacksonville GeoJSON, ZIP hover tooltip |
| `plot_preventative_vs_outcome()` | `reports/figures/preventative_asset_vs_health_outcome.png` | Scatter + regression line (seaborn.regplot), annotates top/bottom 3 ZIPs |
| `plot_intervention_impact_heatmap()` | `reports/figures/intervention_impact_heatmap.png` | Heatmap (ZIP × resource type), % improvement values, ★ marks highest-impact cell |
| `plot_category_view()` × 4 | `reports/figures/category_{name}_view.png` | Side-by-side bars (supply gap vs poverty rate), one chart per resource category |

The choropleth map uses the Census TIGER/Line 2022 ZCTA5 GeoJSON file filtered to Jacksonville-area ZCTAs (prefix `320` or `322`). It is served by the Flask dashboard via a dedicated `/map` route and embedded as an iframe.

---

## 4. Desert Score Algorithm

The Desert Score is a demand-weighted composite deprivation index ranging from 0 (no deprivation) to 100 (maximum deprivation).

### Step 1 — Normalise Supply Gaps

Each supply gap is normalised to [0, 1] via min-max scaling. A gap of 1.0 means the ZIP is the most deprived on that dimension; 0.0 means the least.

```
supply_gap_healthcare = 1 - minmax(primary_care_ratio)
supply_gap_food       = minmax(food_low_access_pct)
supply_gap_parks      = 1 - minmax(park_coverage_pct)
supply_gap_insurance  = minmax(uninsured_rate)
```

Note: healthcare and parks are inverted because higher provider ratios / park coverage = better access.

### Step 2 — Compute Demand Factor

The demand factor amplifies the score for ZIPs where the population is both poor and unhealthy:

```
disease_burden  = (poor_mental_health_rate + obesity_rate) / 2
demand_factor   = minmax(poverty_rate × disease_burden)
```

A ZIP with both high poverty and high disease burden gets a demand factor close to 1.

### Step 3 — Aggregate and Scale

```
raw_score    = sum(supply_gap_i) × demand_factor   [weighted supply gap]
desert_score = minmax(raw_score) × 100             [scaled to 0–100]
```

The outer min-max scales all ZIP scores relative to each other. A score of 100 is the most deprived ZIP in Jacksonville; a score of 0 is the least.

### Step 4 — Rank and Categorise

ZIPs are ranked by `desert_score` descending (rank 1 = most deprived). Ties broken by `poverty_rate` descending. The `top_gap_category` attribute identifies which single supply gap is largest for that ZIP:

```
top_gap_category = argmax(supply_gap_healthcare, supply_gap_food,
                          supply_gap_parks, supply_gap_insurance)
```

### Scoring Weights Implied by the Formula

The formula applies equal weights to all four supply gap components. Demand scaling does not affect the relative ranking of resource categories within a ZIP — it scales the overall deprivation up or down based on how much that community needs the resources.

---

## 5. Gap-Closure Simulation

The simulation answers: *"If we added one type of resource to a high-need ZIP, how much would its Desert Score improve?"*

### Algorithm

1. **Select candidates**: Identify the top-5 most deprived ZIPs (desert_rank 1–5).

2. **Define targets**: For each resource type, compute the 25th-percentile gap value across all 35 ZIPs. This represents a realistic improvement target — 75% of Jacksonville ZIPs already do better than this.

3. **Simulate each intervention** (5 ZIPs × 4 resource types = 20 scenarios):
   - For the target resource type, replace the ZIP's current gap value with the 25th-percentile target (only if it improves the score — never worsens it).
   - Recompute the raw score: `simulated_raw = new_supply_gap_sum × demand_factor`
   - Project the score improvement proportionally: `simulated_score = current_score × (simulated_raw / current_raw)`
   - Compute deltas: `score_improvement = current - simulated`, `pct_improvement = improvement / current × 100`

4. **Rank interventions**: Sort all 20 rows by `score_improvement` descending. Flag the single highest-impact intervention with `is_highest_impact = True`.

### Output Format

```json
[
  {
    "zip_code": "32254",
    "resource_type": "insurance_outreach",
    "current_desert_score": 96.4,
    "simulated_desert_score": 82.6,
    "score_improvement": 13.8,
    "pct_improvement": 14.3,
    "population_impacted": 22150,
    "is_highest_impact": true
  },
  ...
]
```

---

## 6. Flask Presentation Dashboard

### Architecture

The dashboard is a single-file Flask application (`app.py`) with no database. It is stateless except for the background notebook execution tracker.

```
Browser
  │
  │  GET /
  │  ──────────────────────────────────────────────────────────►  app.py:index()
  │                                                                    │
  │                                              load_desert_scores()  │
  │                                             load_interventions()   │
  │                                              build_chart_list()    │
  │                                                                    │
  │  ◄──────────────────────────────────────────  render_template()
  │               index.html (Jinja2)
  │               ├── desert_scores (list[dict])
  │               ├── interventions (list[dict])
  │               ├── best_intervention (dict|None)
  │               ├── charts (list[dict] with .missing flags)
  │               ├── map_exists (bool)
  │               ├── run_status (str)
  │               └── run_message (str)
  │
  │  GET /figures/<filename>
  │  ──────────────────────►  send_from_directory(REPORTS_FIGURES_DIR, filename)
  │
  │  GET /map
  │  ──────────────────────►  send_from_directory(REPORTS_OUTPUTS_DIR, "resource_desert_map.html")
  │
  │  POST /api/regenerate
  │  ──────────────────────►  Spawn threading.Thread(_run_notebook_thread)  ──►  202
  │                           (409 if already running)
  │
  │  GET /api/regenerate/status
  │  ──────────────────────►  { "status": "...", "message": "..." }   (lock-protected read)
```

### Background Execution Model

The "Regenerate Data" feature executes the analysis notebook as a background subprocess. Thread safety is enforced via a module-level `threading.Lock`:

```python
_run_state = {"status": "idle", "message": ""}
_lock = threading.Lock()

def _run_notebook_thread():
    with _lock:
        _run_state.update(status="running", message="")

    result = subprocess.run([
        "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
        "--ExecutePreprocessor.kernel_name=prob1-resource-desert",
        "--ExecutePreprocessor.timeout=600",
        "notebooks/resource_desert_analysis.ipynb"
    ], capture_output=True, text=True)

    with _lock:
        if result.returncode == 0:
            _run_state.update(status="complete", message="")
        else:
            _run_state.update(status="error", message=result.stderr[-500:])
```

**State machine**:
```
idle ──[POST /api/regenerate]──► running ──[returncode == 0]──► complete
                                         └─[returncode != 0]──► error
complete/error ──[POST /api/regenerate]──► running  (retry allowed)
```

**Duplicate-run prevention**: `POST /api/regenerate` checks `status == "running"` before spawning — returns 409 if already in progress.

### Client-Side Polling

The browser polls for notebook completion using a recursive `setTimeout` pattern (not `setInterval`) to avoid request queue buildup:

```javascript
function pollStatus() {
  fetch("/api/regenerate/status")
    .then(r => r.json())
    .then(data => {
      updateUI(data);
      if (data.status === "running") setTimeout(pollStatus, 2000);
    })
    .catch(() => setTimeout(pollStatus, 2000));
}
```

On `complete`: page reloads automatically so all sections refresh with new data.
On `error`: error banner appears with the last 500 characters of notebook `stderr`.

### Template Variables

All data is injected server-side by the `index()` route. There is no client-side data fetching for page content:

| Variable | Type | Source |
|---|---|---|
| `desert_scores` | `list[dict]` | Top-10 rows from `desert_scores.csv` |
| `interventions` | `list[dict]` | All 20 rows from `intervention_recommendations.json`, sorted by impact |
| `best_intervention` | `dict \| None` | The single row with `is_highest_impact == true` |
| `charts` | `list[dict]` | 7 chart descriptors with `missing: bool` flag per PNG |
| `map_exists` | `bool` | Whether `resource_desert_map.html` exists on disk |
| `run_status` | `str` | Current notebook run state from `_run_state` (lock-protected) |
| `run_message` | `str` | Last 500 chars of `stderr` on failure; empty otherwise |

Missing files produce graceful placeholders in the template — no errors propagate to the browser. Each section independently checks its data and shows a "not yet generated" message when needed.

### CSS Design System

Hand-written CSS using custom properties (no framework):

| Token | Value | Usage |
|---|---|---|
| `--color-navy` | `#0d1b2a` | Page background, nav bar, table headers |
| `--color-accent-red` | `#d73027` | High-deprivation indicator, problem statement accent |
| `--color-accent-yellow` | `#fee090` | Mid-deprivation indicator, category titles |
| `--color-accent-green` | `#1a9850` | Low-deprivation indicator, nav links, success states |
| `--color-highlight` | `#ffe066` | Best-intervention call-out card background |

---

## 7. Testing Architecture

### Philosophy

- **Unit tests**: Use synthetic fixture DataFrames only. Never read from `data/raw/`. Fast, deterministic, run in milliseconds.
- **E2E tests**: Tagged `@pytest.mark.e2e`. Read real source files. Run the full pipeline end-to-end. Excluded from the default `pytest` invocation.
- **Coverage gate**: Minimum 70% across `src/` enforced by `pytest --cov-fail-under=70`.

### Test Distribution

| File | Tests | What It Covers |
|---|---|---|
| `test_ingestion.py` | 6 | File existence checks, shape validation, FileNotFoundError on missing files |
| `test_cleaning.py` | 13 | ZIP extraction regex, numeric coercion, NA-string handling, duplicate dropping |
| `test_features.py` | 18 | `_minmax()` edge cases, merge correctness, Desert Score range [0, 100], correlation computation |
| `test_models.py` | 13 | 25th-percentile target logic, score never worsens, `is_highest_impact` exactly one True, intervention ranking |
| `test_visualization.py` | 21 | PNG creation, DPI≥150, figure axis labels, Folium map HTML output, missing GeoJSON handling |
| `test_app.py` | 33 | All 5 Flask route contracts, data loader success/failure paths, background thread state machine |
| `e2e/test_pipeline_e2e.py` | — | Full pipeline from raw CSVs to final output files; asserts output shapes, ZIP code format, score range, intervention count |

### Fixture Strategy (`tests/conftest.py`)

All unit tests share synthetic fixtures defined in `conftest.py`. These are minimal DataFrames (5 rows) with realistic column names matching the actual raw data:

- `sample_census_demo_df` — 5 ZIP codes with population columns
- `sample_cdc_df` — 5 ZIP codes with disease prevalence columns
- `sample_merged_df` — Pre-merged DataFrame with all derived columns populated
- `sample_desert_scores_df` — 5 ZIPs with computed `desert_score`, `desert_rank`, all `supply_gap_*`
- `all_raw_datasets` — Combines all dataset fixtures into the Dict structure expected by `clean_datasets()`

This separation means unit tests have zero dependency on the availability of `data/raw/` files — they run identically on CI and locally.

### Visualisation Test Pattern

Testing matplotlib figures requires special care because `Figure.savefig` is a bound method:

```python
# To capture path and DPI only (most tests):
class _CaptureSavefig:
    def __call__(self, fname, *args, **kwargs):
        self.path = str(fname)
        self.dpi = kwargs.get("dpi")

with patch.object(matplotlib.figure.Figure, "savefig", _CaptureSavefig()):
    plot_desert_scores_bar_chart(df)

# To inspect axis properties (requires autospec=True to bind self):
with patch.object(matplotlib.figure.Figure, "savefig", autospec=True) as mock_sf:
    plot_desert_scores_bar_chart(df)
fig = mock_sf.call_args[0][0]   # self is first arg with autospec
ax = fig.axes[0]
assert ax.get_title() != ""
```

---

## 8. Configuration Design

All project-level paths and column name constants live in `src/config.py`. No file path strings and no raw CSV column names appear anywhere else in the codebase.

### Why Centralised Configuration Matters

The source CSVs use verbose column headers (e.g., `"Total Population (2020-2024)"`, `"Primary Care Physician Ratio (2025)"`). Repeating these strings across modules would make renaming or updating data sources extremely fragile. Instead, every reference goes through a constant:

```python
# config.py
COL_TOTAL_POPULATION = "Total Population (2020-2024)"
COL_PRIMARY_CARE_RATIO = "Primary Care Physician Ratio (2025)"

# features.py — uses the constant, never the string
df[cfg.COL_POVERTY_RATE] = df[cfg.COL_POVERTY_COUNT] / df[cfg.COL_TOTAL_POPULATION]
```

If a data source changes its column headers, only `config.py` needs to be updated.

### Path Resolution

All paths resolve relative to the `config.py` file location, which is `src/`:

```python
ROOT = Path(__file__).resolve().parent.parent   # → project root
DATA_RAW_DIR = ROOT / "data" / "raw"
REPORTS_FIGURES_DIR = ROOT / "reports" / "figures"
```

This makes the project relocatable — it works from any absolute path on any machine.

---

## 9. Technology Stack

| Layer | Library | Version | Purpose |
|---|---|---|---|
| Language | Python | ≥ 3.11 | All pipeline + web code |
| Data manipulation | pandas | ≥ 2.0 | DataFrames throughout the pipeline |
| Numerical | numpy | ≥ 1.26 | Min-max normalisation, array ops |
| Machine learning | scikit-learn | ≥ 1.4 | (available; not used in current pipeline) |
| Visualisation | matplotlib | ≥ 3.8 | Bar charts, scatter plots, heatmap |
| Visualisation | seaborn | ≥ 0.13 | Regression scatter plot (`regplot`) |
| Interactive map | folium | ≥ 0.15 | Choropleth HTML map from GeoJSON |
| Geospatial | geopandas | ≥ 0.14 | GeoJSON download + filtering for Jacksonville ZCTAs |
| Notebook execution | jupyter / nbconvert | ≥ 1.0 / ≥ 7.0 | Run pipeline via notebook; Flask background trigger |
| Web framework | Flask | ≥ 3.0 | Presentation dashboard |
| File serving | werkzeug (Flask dep.) | — | `send_from_directory` for PNGs and choropleth HTML |
| Testing | pytest | ≥ 8.0 | Test runner |
| Coverage | pytest-cov | ≥ 4.1 | Coverage measurement and gate |
| Linting | ruff | ≥ 0.4 | Import order, unused variables, style checks |
| Formatting | black | ≥ 24.0 | Deterministic code formatting |
| Spreadsheet reads | openpyxl | ≥ 3.1 | Load `Metadata.xlsx` data dictionary |

---

## 10. Design Principles

### I. Five-Stage Pipeline Separation

Each stage (`ingestion → cleaning → features → models → visualization`) is a separate module with a single public entry point that takes DataFrames as input and returns DataFrames as output. No stage imports from another stage's module directly. The orchestration notebook calls them in sequence.

This separation makes each stage independently testable, replaceable, and debuggable.

### II. No Global State

DataFrames and configuration are passed as explicit function arguments. The only module-level mutable state in the entire codebase is `_run_state` in `app.py`, which is guarded by a `threading.Lock` and only ever written from within `_run_notebook_thread()`.

### III. Fail Fast on Bad Data

Ingestion raises `FileNotFoundError` immediately if any source file is missing. Cleaning logs and raises on unexpected null patterns in critical columns. This prevents silent garbage-in/garbage-out scenarios.

### IV. Transparent Logging

Every transformation that changes the shape of a DataFrame logs the before and after record counts. Every row drop (deduplication, population filter) logs the count and reason. The `get_logger()` utility in `config.py` ensures a consistent log format across all modules.

### V. Raw Data Immutability

Files under `data/raw/` are never opened for writing. The `.gitignore` excludes large binary files but the directory structure is committed. All transformations write to `data/processed/` or `reports/`.

### VI. Graceful Frontend Fallbacks

The Flask dashboard never lets a missing file cause an unhandled exception or a blank page. Each data loader returns an empty list on failure; the Jinja2 template renders descriptive placeholder `<div>` elements with a "Regenerate Data" prompt wherever data is missing.

### VII. Test-First, Synthetic Fixtures

Unit tests are written before implementations. All unit tests use 5-row synthetic DataFrames that exercise the same column contracts as the real data. This keeps the test suite fast (sub-second) and independent of real data availability.

### VIII. Single Source of Truth for Configuration

No magic strings outside `config.py`. Column names, file paths, dataset keys, and output file names are all defined once. The application, tests, and notebook all import from `config.py` — never from each other.

---

## 11. Produced Artefacts

After a full pipeline run, the following files exist on disk:

### Structured Data Outputs

| File | Rows | Key Columns | Consumer |
|---|---|---|---|
| `data/processed/merged_jacksonville.csv` | 35 | zip_code + 28 cols (all raw + derived rates) | Debugging, downstream analysis |
| `reports/outputs/desert_scores.csv` | 35 | zip_code, desert_score (0–100), desert_rank, supply_gap_* (×4), top_gap_category | Flask dashboard top-10 table |
| `reports/outputs/intervention_recommendations.json` | 20 | zip_code, resource_type, score_improvement, pct_improvement, is_highest_impact | Flask dashboard recommendations section |

### Visualisation Outputs

| File | Size | Content |
|---|---|---|
| `reports/figures/desert_scores_bar_chart.png` | ~61 KB | Horizontal bars, top-10 ZIPs by Desert Score, red→green colour gradient |
| `reports/figures/preventative_asset_vs_health_outcome.png` | ~89 KB | Scatter + OLS regression line, preventative assets vs health outcomes |
| `reports/figures/intervention_impact_heatmap.png` | ~85 KB | Heatmap of projected % improvement per ZIP × resource type combination |
| `reports/figures/category_healthcare_view.png` | ~51 KB | Healthcare supply gap + poverty rate for all Jacksonville ZIPs |
| `reports/figures/category_food_access_view.png` | ~52 KB | Food access supply gap + poverty rate for all Jacksonville ZIPs |
| `reports/figures/category_parks_view.png` | ~50 KB | Parks supply gap + poverty rate for all Jacksonville ZIPs |
| `reports/figures/category_insurance_view.png` | ~51 KB | Insurance coverage gap + poverty rate for all Jacksonville ZIPs |
| `reports/outputs/resource_desert_map.html` | ~5.2 MB | Interactive Folium choropleth — hover ZIPs to see Desert Score + rank |

### Static Presentation

| File | Size | Description |
|---|---|---|
| `docs/project_presentation.html` | ~613 KB | Fully self-contained HTML — all 7 charts base64-inlined, all data embedded; opens directly from the filesystem without Flask |

---

*Generated from codebase analysis — 2026-03-28*
