# Prompt Dialog — 2026-03-28

Session covering the full speckit workflow for the **2025 UNF CodeforAwhile Datathon — Problem Case: Resource Desert**.
Branch: `002-per-dataset-eda-notebooks`

---

## 1. Constitution Setup

**User:**
> `/speckit.constitution` — this project will be built using python and data science libraries. Adhere to the best practises for python programming as well as best practises for Data Science. follow test driven approach and have at minimum 70% test coverage.

**Assistant:**
Created `.specify/memory/constitution.md` v1.0.0 with 6 principles:
- Principle I: Python Code Quality (ruff, black, type hints, Google docstrings, pathlib)
- Principle II: DS Reproducibility (seeds(42), pathlib paths, no global state)
- Principle III: Test-First, ≥70% coverage hard block
- Principle IV: Data Integrity (`data/raw/` read-only, log every transformation)
- Principle V: YAGNI (no speculative abstractions, no silent drops)
- Principle VI: Analytical Rigour (cross-validation mandatory, IQR outliers, observational flags only)

Technology stack table, quality gates (`ruff check`, `black --check`, `pytest --cov=src --cov-fail-under=70`), and governance section added.

---

## 2. Propagate Constitution to Spec Artifacts

**User:**
> Under both specification folders, do update the specs.md, plan.md and tasks.md to reflect the guidelines from the constitution file just generated.

**Assistant:**
Updated the following files under both `specs/001-resource-desert-analysis/` and `specs/002-per-dataset-eda-notebooks/`:

- **spec.md** — Added FR-010 through FR-015 (ruff/black, type hints, pathlib, seeds, CV, 70% coverage). Added Constitution Compliance section mapping all 6 principles to specific FRs.
- **plan.md** — Replaced placeholder constitution gate check with a 12-row gate table; all 6 principles checked with Pass/N/A status and justifications.
- **tasks.md** — Added Phase 6 Quality Gates tasks (T034–T041) referencing SC-001, SC-002, FR-010, FR-012, Constitution Principles I–IV.

---

## 3. Phase 1 — Setup

**User:**
> `/speckit.implement` — all phase 1 tasks from `@specs/002-per-dataset-eda-notebooks/tasks.md`

**Assistant:**
Executed T001–T004:

- **T001** — Created `notebooks/eda/` directory.
- **T002** — Created `tests/e2e/` directory and empty `tests/e2e/__init__.py`.
- **T003** — Created `requirements.txt` with full project stack:
  ```
  pandas>=2.0, numpy>=1.26, matplotlib>=3.8, seaborn>=0.13,
  jupyter>=1.0, nbconvert, openpyxl, nbmake, nbqa, ruff, black,
  pytest, pytest-cov
  ```
- **T004** — Read `data/raw/Metadata.xlsx` via openpyxl and produced `specs/002-per-dataset-eda-notebooks/column-reference.md` (203 lines) listing all column names, types, and definitions for all 9 source CSV files. Key findings:
  - `geoid` is the integer ZIP join key across all 9 datasets
  - 8 USDA-FoodAccess columns use abbreviated names in CSV vs. full names in Metadata.xlsx
  - `Lack of Health Insurance Among Adults (2023)` duplicated in CDCPlaces and HealthCareAccess
  - Parks data vintage 2018; USDA data vintage 2019

Also created `.gitignore` (Python/Jupyter patterns) and `pytest.ini` with `e2e` marker.

---

## 4. Phase 2 — Foundational (Test Scaffold)

**User:**
> `/speckit.implement` — all tasks from phase 2 from `@specs/002-per-dataset-eda-notebooks/tasks.md`

**Assistant:**
Executed T005–T006:

- **T005** — Created `tests/e2e/test_eda_notebooks.py` with:
  - `test_eda_notebook_runs_without_errors` — parameterized over all `.ipynb` files in `notebooks/eda/`, tagged `@pytest.mark.e2e`
  - `test_eda_directory_exists` — asserts `notebooks/eda/` exists
  - `test_expected_notebooks_present` — asserts all 9 stems present; skips with message if Phase 3 not yet done
- **T006** — Verified `pytest --nbmake notebooks/eda/ -v` on empty directory returns 0 notebooks collected, no errors (Red phase of TDD confirmed).

---

## 5. Phase 3 — User Story 1 (Schema + Distributions)

**User:**
> `/speckit.implement` — all tasks under phase 3 for `@specs/002-per-dataset-eda-notebooks/tasks.md`

**Assistant:**
Created all 9 EDA notebooks (T007–T015) using the `nbformat` Python API. Each notebook has:

**Section 1 — Data Loading & Schema Summary:**
- Loads CSV from `data/raw/` using a 4-candidate `Path.cwd()` project root detection
- Displays: shape, dtype table, null percentage per column, ZIP (`geoid`) key check

**Section 3 — Univariate Distributions:**
- Histograms for all numeric columns (KDE overlay)
- Frequency bar charts for categorical columns with ≤20 unique values
- All charts titled and axis-labelled

Common imports pattern across all notebooks:
```python
import warnings
from pathlib import Path
import matplotlib, matplotlib.pyplot as plt
import pandas as pd, seaborn as sns
from IPython.display import display
warnings.filterwarnings("ignore")
matplotlib.rcParams["figure.dpi"] = 100
sns.set_theme(style="whitegrid", palette="muted")
%matplotlib inline
_here = Path.cwd()
_candidates = [_here, _here.parent, _here.parents[1], _here.parents[2]]
PROJECT_ROOT = next((p for p in _candidates if (p / "data" / "raw").exists()), None)
assert PROJECT_ROOT is not None
RAW_DATA = PROJECT_ROOT / "data" / "raw"
```

Checkpoint: `pytest --nbmake notebooks/eda/ -v` → 9 passed.

---

## 6. Phase 4 — User Story 2 (Data Quality Assessment)

**User:**
> `/speckit.implement` — all tasks under phase 4 of `@specs/002-per-dataset-eda-notebooks/tasks.md`

**Assistant:**
Added Section 2 to all 9 notebooks (T016–T024). Each Section 2 contains:

1. **Duplicate row count** cell
2. **Quality flag table** — `[column_name, null_pct, dtype, quality_flag]`
   - `usable`: numeric, <30% null, not admin col
   - `needs_cleaning`: `object` dtype
   - `too_sparse`: >30% null
   - Admin columns (`feature id`, `feature label`, `shid`, `geoid`) always flagged `usable`
3. **IQR outlier table** for all numeric columns — `[column, Q1, Q3, IQR, lower_fence, upper_fence, outlier_count, outlier_zips]`

Flag assignment function:
```python
ADMIN_COLS = {"feature id", "feature label", "shid", "geoid"}

def assign_flag(null_pct: float, col_dtype: str, col_name: str) -> str:
    if col_name in ADMIN_COLS: return "usable"
    if null_pct > 30.0: return "too_sparse"
    if col_dtype == "object": return "needs_cleaning"
    return "usable"
```

Note for `eda_census_housing_poverty`: flags ZIP column if integer vs. string format inconsistency detected.

---

## 7. Phase 5 — User Story 3 (Domain-Relevant Analysis)

**User:**
> `/speckit.implement` — proceed with phase 5 for `@specs/002-per-dataset-eda-notebooks/tasks.md`

**Assistant:**
Added Section 4 to all 9 notebooks (T025–T033). Each Section 4 has at least one ranked horizontal bar chart (top/bottom 10 ZIPs) with labelled axes, units, and a one-sentence Resource Desert relevance note.

| Notebook | Primary Metric | Extra Chart |
|---|---|---|
| `eda_cdc_places` | Highest chronic disease prevalence rate | — |
| `eda_census_demographics` | Total Population (density proxy) | — |
| `eda_census_housing_poverty` | People Below Poverty Level | Housing cost burden distribution |
| `eda_fema` | Environmental Hazard Community Resilience Score | — |
| `eda_healthcare_access` | Computed uninsured rate % | — |
| `eda_healthcare_workers` | Primary Care Physician Ratio | Provider type median ratio comparison |
| `eda_parks` | Percent Area Covered by Parks (2018) | — |
| `eda_social_vulnerability` | Social Vulnerability Index (top-quartile highlighted) | Quartile color coding + Q75 threshold line |
| `eda_usda_food_access` | Low Income People (USDA) (2019) | Food desert proportion bar chart |

Standard chart pattern:
```python
METRIC_COL = "..."
METRIC_LABEL = "..."
RELEVANCE_NOTE = "..."
N = 10
ranked = df[["geoid", METRIC_COL]].dropna().sort_values(METRIC_COL, ascending=False)
top_n = ranked.head(N)
bottom_n = ranked.tail(N).sort_values(METRIC_COL)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
# horizontal bar charts with invert_yaxis(), labelled axes
fig.suptitle(f"Top & Bottom {N} ZIPs — {DATASET_TITLE}", fontsize=13, fontweight="bold")
```

---

## 8. Phase 6 — Quality Gates & Polish

**User:**
> `/speckit.implement` — remaining tasks from Phase 6 and beyond for `@specs/002-per-dataset-eda-notebooks/tasks.md`

**Assistant:**
Executed all 8 Phase 6 quality gate tasks:

- **T034** ✅ — `pytest --nbmake notebooks/eda/ -v` → 9 notebooks collected, 9 passed, 0 errors.
- **T035** ✅ — Verified headings. Found all 9 notebooks had numbered headings (`1. Data Loading & Schema Summary` etc.) that didn't match the spec. Stripped numbers from all markdown heading cells; re-verified all 9 match exactly:
  1. `Data Loading & Schema Summary`
  2. `Data Quality Assessment`
  3. `Univariate Distributions`
  4. `Domain-Relevant Analysis`
- **T036** ✅ — `nbqa ruff notebooks/eda/` — initially found 9 F401 errors (unused `import numpy as np`). Auto-fixed with `nbqa ruff notebooks/eda/ --fix`. Re-run → "All checks passed!"
- **T037** ✅ — `nbqa black notebooks/eda/` — 9 formatting violations auto-fixed. Re-run `--check` → "9 files would be left unchanged."
- **T038** ✅ — `jupyter nbconvert --clear-output notebooks/eda/*.ipynb` — all 9 notebooks cleared.
- **T039** ✅ — Loaded all 9 CSVs and compared actual column names against `column-reference.md`. Zero discrepancies found across all 9 datasets.
- **T040** ✅ — `git diff --name-only -- data/raw/` → empty. Raw data unmodified.
- **T041** ✅ — `pytest tests/ -v -m "not e2e"` → 11 deselected (correct — no non-e2e tests for notebooks-only feature).

Post-polish re-run: `pytest --nbmake notebooks/eda/ -v` → 9 passed in 15.18s ✓

---

## 9. Documentation

**User:**
> Under the root folder of this project, create a sub-folder named "docs" inside that create a markdown file named prompt-dialog.md and save all prompt conversation from today into this file.

**Assistant:**
Created `docs/prompt-dialog.md` (this file).

---

## Summary of All Artifacts Produced (Session 1 — Feature 002)

| Artifact | Description |
|---|---|
| `.specify/memory/constitution.md` | Project constitution v1.0.0 — 6 principles, quality gates, governance |
| `requirements.txt` | Full Python stack: pandas, numpy, matplotlib, seaborn, jupyter, nbmake, nbqa, ruff, black, pytest |
| `.gitignore` | Python/Jupyter ignore patterns |
| `pytest.ini` | e2e marker registration |
| `tests/e2e/__init__.py` | Empty init for e2e test package |
| `tests/e2e/test_eda_notebooks.py` | Parameterized nbmake-based e2e test suite |
| `specs/002-per-dataset-eda-notebooks/column-reference.md` | Column names and definitions for all 9 raw CSVs |
| `notebooks/eda/eda_cdc_places.ipynb` | CDC PLACES — 4 sections |
| `notebooks/eda/eda_census_demographics.ipynb` | Census Demographics — 4 sections |
| `notebooks/eda/eda_census_housing_poverty.ipynb` | Census Housing & Poverty — 4 sections + extra chart |
| `notebooks/eda/eda_fema.ipynb` | FEMA Risk & Resilience — 4 sections |
| `notebooks/eda/eda_healthcare_access.ipynb` | Healthcare Access — 4 sections |
| `notebooks/eda/eda_healthcare_workers.ipynb` | Healthcare Workers — 4 sections + provider type chart |
| `notebooks/eda/eda_parks.ipynb` | Parks Access — 4 sections |
| `notebooks/eda/eda_social_vulnerability.ipynb` | Social Vulnerability Index — 4 sections + quartile coloring |
| `notebooks/eda/eda_usda_food_access.ipynb` | USDA Food Access — 4 sections + food desert proportion chart |
| `docs/prompt-dialog.md` | This file |

---

---

# Session 2 — 2026-03-28

Branch: `001-resource-desert-analysis` (Phase 7 completion) → `003-flask-presentation-dashboard` (full lifecycle)

---

## 10. Feature 001 — Phase 7: Visualization Tests, Notebook, E2E, Quality Gates

**User:**
> `/speckit.implement complete all remaining tasks from @specs/001-resource-desert-analysis/tasks.md`

**Assistant:**
Executed T027–T034 across visualization tests, Jupyter notebook, e2e tests, linting, and coverage gate.

**T027 — Visualization tests** (`tests/test_visualization.py`, 24 tests):

Discovered a Python descriptor protocol subtlety when mocking `Figure.savefig` via `patch.object`:
- Callable class instances (non-functions) do **not** implement `__get__`, so Python does not bind `self` (the Figure) when the mock is called. The mock receives `(out_path, dpi=150)` directly.
- For tests that only need to capture the output path and DPI, used a `_CaptureSavefig` callable class with `__call__(self, fname, *args, **kwargs)`.
- For tests that need to inspect axis properties (title, labels), used `patch.object(..., autospec=True)` which forces binding; the Figure instance is retrieved as `mock_sf.call_args[0][0]`.

Key helper patterns:
```python
class _CaptureSavefig:
    def __call__(self, fname, *args, **kwargs):
        self.path = str(fname)
        self.dpi = kwargs.get("dpi")

# For axis inspection:
with patch.object(matplotlib.figure.Figure, "savefig", autospec=True) as mock_sf:
    plot_desert_scores_bar_chart(df)
fig_instance = mock_sf.call_args[0][0]
ax = fig_instance.axes[0]
assert ax.get_title() != ""
```

A `minimal_geojson` fixture was created for choropleth tests — writes a temp GeoJSON with a `ZCTA5CE20` property matching the Folium `key_on` configuration.

**T028 — Jupyter notebook** (`notebooks/resource_desert_analysis.ipynb`):
- Created full orchestration notebook running all 5 pipeline stages.
- Cell 1: `matplotlib.use('Agg')` for headless execution; `repo_root = Path().resolve().parent`; imports all pipeline modules.
- Cell 17 (health correlation): required pivoting the long-format DataFrame before applying `.style.format('{:.3f}')`:
  ```python
  corr_matrix = corr_df.pivot(index="asset", columns="outcome", values="pearson_r")
  corr_matrix.style.background_gradient(cmap="RdYlGn", vmin=-1, vmax=1).format("{:.3f}")
  ```
- Choropleth cell guarded with `if cfg.GEOJSON_PATH.exists():` to allow graceful skip.

**T029 — E2E tests** (`tests/e2e/test_pipeline_e2e.py`):
- Class-scoped `pipeline_outputs` fixture runs the full pipeline once per session.
- 14 assertions: 9 datasets loaded, 5-char ZIPs, no duplicates, `desert_scores.csv` columns/range/rank, intervention JSON 20 rows, one `is_highest_impact`, non-negative improvements, 5 visualization PNG files exist.

**T030 — Ruff fix** (`src/visualization.py`):
- Removed unused `score_lookup` variable (F841) — a 4-line dict computed for the choropleth tooltip but never used.

**T031–T033 — Quality gates**: All passed — `ruff check`, `black --check`, `pytest --cov=src --cov-fail-under=70` (95.6% achieved), notebook outputs cleared.

**T034 — requirements.txt cleanup**:
- Removed duplicate entries (ruff, black, pytest, pytest-cov appeared twice).
- Added `ipykernel>=6.0` for venv kernel registration.

---

## 11. Feature 001 — GeoJSON Download (T035)

**User:**
> Append the previous step as an additional task under `@specs/001-resource-desert-analysis/tasks.md`

**Assistant:**
Added T035 to tasks.md and executed it: downloaded Census TIGER/Line 2022 ZCTA5 shapefile, filtered to Jacksonville-area ZCTAs (prefix `320` or `322`), and saved as `data/raw/jacksonville_zctas.geojson` (2.8 MB, 83 ZCTAs). Verified the `ZCTA5CE20` property matches the `key_on` parameter in the Folium choropleth configuration — no placeholders remain.

---

## 12. Feature 001 — GeoJSON Integration Verification

**User:**
> Can you now verify if the GeoJSON for Jacksonville and surrounds is being invoked correctly by code and there is no placeholder left.

**Assistant:**
Traced all references to `cfg.GEOJSON_PATH` through `src/visualization.py`, the notebook, and tests. Confirmed:
- `create_choropleth_map()` uses `key_on="feature.properties.ZCTA5CE20"`.
- The downloaded GeoJSON file contains `ZCTA5CE20` as the ZIP code property — exact match.
- No placeholder strings (`"REPLACE_ME"`, `"TODO"`, `"..."`) found anywhere in pipeline code.
- E2E choropleth test correctly skips with `pytest.skip(...)` when the GeoJSON is absent rather than failing.

---

## 13. README Rewrite

**User:**
> We are only addressing one problem 'Resource Desert'; the other you mentioned are from last year's hackathon. Remove them from reference. Now update the `@README.md` to refer to the problem statement as mentioned in `@raw_specs.md`; also list down a sequence of steps on how to run this project step by step.

**Assistant:**
Rewrote `README.md` from scratch based solely on `raw_specs.md`. Removed all references to Case 2 (voter turnout) and Case 3 (police shootings) which were from the previous year's hackathon.

New README contents:
- Problem statement: Resource Desert definition, three key analytical questions, deliverable description.
- 7-step run guide: env setup → GeoJSON download (one-time) → notebook execution → unit tests → e2e tests → lint/format check → clear notebook outputs.
- Pipeline overview flowchart (text diagram).
- Data sources table listing all 10 files with their source agency.

---

## 14. Notebook Execution Fix

**User:**
> Can you please execute the Jupyter notebook `@notebooks/resource_desert_analysis.ipynb`; this is giving error on one of the snippets; it complains of a missing module 'folium'; if you find additional Python libraries are needed, do add them to `@requirements.txt` as well.

**Assistant:**
Diagnosed two issues:

**Issue 1 — `ModuleNotFoundError: No module named 'folium'`:**
- Root cause: Notebook was running against the system Python kernel, not the `.venv` where `folium 0.20.0` is installed.
- Fix: Registered the venv as a named Jupyter kernel:
  ```bash
  python -m ipykernel install --user --name prob1-resource-desert
  ```
  Added `ipykernel>=6.0` to `requirements.txt`. Executed notebook with `--ExecutePreprocessor.kernel_name=prob1-resource-desert`.

**Issue 2 — `ValueError: Unknown format code 'f' for object of type 'str'` (Cell 17):**
- Root cause: `compute_health_outcome_correlation()` returns a long-format DataFrame with string `asset` and `outcome` columns. Applying `.format('{:.3f}')` on all columns fails on strings.
- Fix: Pivot to wide matrix before styling:
  ```python
  corr_matrix = corr_df.pivot(index="asset", columns="outcome", values="pearson_r")
  corr_matrix.style.background_gradient(cmap="RdYlGn", vmin=-1, vmax=1).format("{:.3f}")
  ```

Notebook executed successfully end-to-end. All 7 output files produced.

---

## 15. Feature 003 — Specification

**User:**
> `/speckit.specify` run `@notebooks/resource_desert_analysis.ipynb` and save its output files and images. Create a simple web application in Python using a suitable framework like Flask; use elegant and simple stylesheets. Using the output files from the notebook, create this web application that can serve the purpose of presentation to judges and audience to first show the problem statement and how the analysis was done and finally what was the observation from the data and the suggested recommendations.

**Assistant:**
Created branch `003-flask-presentation-dashboard` and wrote `specs/003-flask-presentation-dashboard/spec.md`.

Five user stories defined (P1/P1/P2/P2/P3):
1. **US1 (P1)** — Problem Statement: Resource Desert definition, 3 key questions, inequity cycle.
2. **US2 (P1)** — Data Analysis Walkthrough: Desert Score formula, data sources table, top-10 ZIP table, bar chart, choropleth iframe.
3. **US3 (P2)** — Health Outcome Observations: scatter plot, strongest-correlation stat block.
4. **US4 (P2)** — AI Recommendations: highest-impact call-out card, heatmap, 20-row intervention table.
5. **US5 (P3)** — Per-Category Drill-Down: 4 category supply gap charts.

Functional requirements include FR-007/007a/007b/007c (Regenerate Data button, background execution, duplicate-run blocking, error display) and FR-010 (sticky nav bar).

---

## 16. Feature 003 — Clarification

**User:**
> `/speckit.clarify`

**Assistant:**
Asked 3 targeted questions:

- **Q1 (Layout)**: Single-page scrollable vs multi-page vs tabbed?
  - User answered **A** (single-page scrollable). Applied to FR-001 and FR-010.
- **Q2 (Notebook trigger)**: Display-only vs automatic on load vs Regenerate button?
  - User answered **C** (Regenerate Data button). Applied to FR-007a/b/c.
- **Q3 (Charts)**: Static PNGs vs in-browser rendering vs hybrid?
  - User answered **A** (static PNGs only; Folium iframe is the sole interactive element). Applied to FR-002.

Clarifications written into `spec.md` under `## Clarifications / ### Session 2026-03-28`.

---

## 17. Feature 003 — Planning (Phase 0 & 1)

**User:**
> `/speckit.plan`

**Assistant:**
Ran the full plan workflow. Generated four artefacts:

**`specs/003-flask-presentation-dashboard/research.md`** — 6 research decisions:
1. Background execution: `threading.Thread` + `subprocess.run` + `threading.Lock`-protected `_run_state` dict. No Celery/RQ — datathon demo needs no external infrastructure.
2. File serving: `send_from_directory(cfg.REPORTS_FIGURES_DIR, filename)` — handles MIME types, prevents path traversal.
3. Choropleth embed: `/map` route + `<iframe src="/map">` — file is ~5 MB, too large to inline.
4. JS polling: Recursive `setTimeout` + `fetch` (not `setInterval`) — waits for each response before scheduling the next.
5. Testing: Flask `app.test_client()` fixture — no pytest-flask dependency needed.
6. CSS: Hand-written ~200 lines, CSS custom properties for palette (navy `#0d1b2a`, red `#d73027`, green `#1a9850`, highlight `#ffe066`).

**`specs/003-flask-presentation-dashboard/data-model.md`** — 5 entities:
- `DesertScore` (11 fields from `desert_scores.csv`)
- `Intervention` (8 fields from `intervention_recommendations.json`)
- `ChartImage` (4 fields, 7 known instances)
- `ChoroplethMap` (4 fields, served at `/map`)
- `NotebookRunStatus` (2 fields, in-memory with Lock, lifecycle diagram)

**`specs/003-flask-presentation-dashboard/plan.md`** — Technical context (Python 3.11+, Flask ≥ 3.0, stdlib threading/subprocess), Constitution Check (all 6 gates pass), Project Structure (`app.py` + `webapp/` + `tests/test_app.py`), summary.

**`specs/003-flask-presentation-dashboard/contracts/routes.md`** — 5 route contracts with request/response schemas, error behaviour, and security notes.

**`specs/003-flask-presentation-dashboard/contracts/templates.md`** — Jinja2 template variable contracts for all 7 injected variables with field-level types, examples, and missing-file behaviour.

**`specs/003-flask-presentation-dashboard/quickstart.md`** — Developer quickstart: install, kernel registration, notebook execution, `python app.py`, browser URL, regenerate flow, troubleshooting table.

`CLAUDE.md` updated with Flask ≥ 3.0 under Active Technologies via `update-agent-context.sh`.

---

## 18. Feature 003 — Task Generation

**User:**
> `/speckit.tasks`

**Assistant:**
Generated `specs/003-flask-presentation-dashboard/tasks.md` with 30 tasks across 8 phases:

| Phase | Tasks | Description |
|---|---|---|
| Phase 1: Setup | T001–T003 | Verify config.py constants, create webapp/ dirs, add Flask to requirements.txt |
| Phase 2: Foundational | T004–T011 | `app.py` skeleton, data loaders, notebook runner, file-serving routes, API routes, CSS base, JS polling, route tests |
| Phase 3: US1 (P1) | T012–T015 | `index()` route, `index.html` skeleton + problem statement section, CSS, GET / tests |
| Phase 4: US2 (P1) | T016–T018 | Analysis section (table, bar chart, choropleth iframe), CSS, tests |
| Phase 5: US3 (P2) | T019–T020 | Observations section (scatter plot, stat block), CSS |
| Phase 6: US4 (P2) | T021–T023 | Recommendations section (call-out card, heatmap, 20-row table), CSS, tests |
| Phase 7: US5 (P3) | T024–T025 | Category drill-down section (4 charts), CSS |
| Phase 8: Polish | T026–T030 | Missing-file fallbacks, error/spinner CSS, Regenerate button JS wiring, ruff/black, final test run |

12 of 30 tasks marked `[P]` (parallelizable). MVP defined as Phases 1–4 (T001–T018).

---

## 19. Feature 003 — Implementation

**User:**
> `/speckit.implement`

**Assistant:**
Executed all 30 tasks. All phases completed without errors.

**Phase 1 — Setup (T001–T003)**:
- `REPORTS_FIGURES_DIR` and `REPORTS_OUTPUTS_DIR` already present in `src/config.py`. ✓
- Created `webapp/templates/`, `webapp/static/css/`, `webapp/static/js/`.
- Added `flask>=3.0` to `requirements.txt`; installed Flask 3.1.3.

**Phase 2 — Foundational (T004–T011)**:

`app.py` written as a single file (~260 lines) containing:
- Flask instance with `template_folder` and `static_folder` pointing to `webapp/`.
- Module-level `_run_state` dict and `_lock = threading.Lock()`.
- `_run_notebook_thread()` — subprocess runner that updates `_run_state` under lock.
- `load_desert_scores()` — reads `desert_scores.csv`, renames `Total Population (2020-2024)` → `total_population`, returns top-10 rows; empty list on missing/corrupt file.
- `load_interventions()` — reads `intervention_recommendations.json`, sorted by `score_improvement` desc; empty list on failure.
- `build_chart_list()` — returns 7 chart descriptors with `missing: bool` flags checked against `REPORTS_FIGURES_DIR`.
- `GET /figures/<filename>` and `GET /map` routes via `send_from_directory`.
- `POST /api/regenerate` and `GET /api/regenerate/status` routes.

`webapp/static/css/style.css` (~300 lines):
- CSS custom properties for the full palette.
- CSS reset, sticky nav, five-section scroll scaffold.
- All section-specific styles: problem hero, formula block, data tables, map iframe container, stat block, highlight card, category grid, placeholder, error banner, spinner animation.

`webapp/static/js/app.js`:
- `pollStatus()` using recursive `setTimeout` + `fetch`.
- Regenerate button click handler: disables button, shows spinner, POSTs to `/api/regenerate`, starts polling, reloads on `complete`, shows error banner on `error`.
- On page load: if `body.dataset.runStatus == "running"` (SSR state), starts polling immediately.

`tests/test_app.py` (33 tests in 7 classes):
- `TestServeFigure` — 404 on missing, 200 on existing PNG.
- `TestServeMap` — 404 on missing, 200 on existing HTML.
- `TestApiRegenerate` — 202 with thread spawn, 409 when already running, no thread on duplicate.
- `TestApiRegenerateStatus` — JSON shape, idle/error/complete states.
- `TestIndexProblemStatement` — 200, "Resource Desert" heading, 3 list items, inequity cycle text.
- `TestIndexAnalysis` — bar chart img, choropleth iframe, desert scores table rows.
- `TestIndexRecommendations` — highlight card ZIP, resource type, `best-row` CSS class, heatmap img.
- Additional classes for data loaders and `_run_notebook_thread` (success + error paths).

**Phase 3–7 — All sections built into `webapp/templates/index.html`**:
- Single Jinja2 template, all 5 sections in sequence.
- Sticky nav with 5 anchor links + Regenerate button wired to `run_status` SSR state.
- Each section has `{% if data %}...{% else %}<div class="placeholder">...{% endif %}` fallback.
- `{% set ... | selectattr | first %}` used to look up chart descriptors by filename.
- Best-intervention call-out card guarded by `{% if best_intervention %}`.
- 20-row interventions table with `{% if row.is_highest_impact %} class="best-row"{% endif %}`.
- Category grid uses a Jinja2 `{% set cat_charts = [...] %}` loop.

**Phase 8 — Polish (T026–T030)**:
- All missing-file placeholders already in template from phases above.
- `ruff check app.py` + `black --check app.py` → zero issues.
- Final test run: **33/33 pass, 98% coverage** on `app.py`.

**Bug fix during smoke test**: `Total Population (2020-2024)` column not in the `display_cols` list — added a `df.rename(columns={cfg.COL_TOTAL_POPULATION: "total_population"})` step in `load_desert_scores()` before the column selection. Also added Jinja2 `is defined` guard in the template for robustness.

All 30 tasks marked `[X]` in `tasks.md`.

---

## 20. Feature 003 — Static Standalone Presentation

**User:**
> The Flask app looks good. Can you create a static single-HTML file with same/similar styles which can be opened standalone. Save this file in "docs" folder and name it `project_presentation.html`; this HTML should not have the Regenerate button and should open without the need of running Flask app.

**Assistant:**
Generated `docs/project_presentation.html` using a Python script that:
1. Reads `reports/outputs/desert_scores.csv` and `intervention_recommendations.json`.
2. Base64-encodes all 7 PNG charts from `reports/figures/` and inlines them as `data:image/png;base64,...` `src` attributes.
3. Inlines the full CSS in a `<style>` block (no external stylesheet reference).
4. Embeds all data as static HTML tables (no JavaScript, no server calls).
5. Replaces the Regenerate button with a `nav__badge` span ("2026 UNF Datathon").
6. Replaces the choropleth iframe with a `map-note` callout explaining how to access it via the Flask app.

Result: **613 KB** fully self-contained HTML that opens directly from the filesystem.

Validation: 14/14 checks passed — Resource Desert heading present, 3 key questions, inequity cycle, 10 desert score rows, 20 intervention rows, 7 base64 images, highlight card, no Regenerate button, no external CSS link.

---

## 21. Architecture Documentation

**User:**
> Analyze this codebase fully and document the architecture and design of this application in a markdown file under "docs" folder. Name this file as `architecture.md`.

**Assistant:**
Performed full codebase analysis using an Explore subagent, then wrote `docs/architecture.md` (691 lines, 11 sections).

Sections written:
1. **System Overview** — Two-mode architecture diagram (pipeline vs dashboard), decoupling model.
2. **Repository Layout** — Full annotated directory tree with structural rules.
3. **Data Pipeline** — ASCII flow diagram; stage-by-stage breakdown (Stages 1–5) including all transformations, outputs, and row counts.
4. **Desert Score Algorithm** — Step-by-step formula: supply gap normalisation → demand factor computation → weighted aggregation → min-max scaling to [0–100] → ranking → top-gap categorisation.
5. **Gap-Closure Simulation** — 25th-percentile target logic, proportional score projection, 20-row output format with example JSON.
6. **Flask Presentation Dashboard** — Route architecture diagram, background execution state machine, client-side polling contract, template variable table, CSS design token table.
7. **Testing Architecture** — Test count per file, fixture strategy, matplotlib mock pattern (callable class vs autospec).
8. **Configuration Design** — Why centralised config matters, path resolution via `Path(__file__).resolve().parent.parent`.
9. **Technology Stack** — Full dependency table with versions and purpose.
10. **Design Principles** — Eight principles (pipeline separation, no global state, fail-fast, transparent logging, raw data immutability, graceful fallbacks, test-first, single source of truth).
11. **Produced Artefacts** — Every output file with size, row count, and consumer.

---

## Summary of All Artifacts Produced (Session 2 — Features 001 completion + 003)

| Artifact | Description |
|---|---|
| `tests/test_visualization.py` | 24 unit tests for all 5 visualization functions; callable class + autospec mock patterns |
| `tests/e2e/test_pipeline_e2e.py` | Full pipeline e2e tests, class-scoped fixture, 14 assertions |
| `notebooks/resource_desert_analysis.ipynb` | Full orchestration notebook; fixed folium kernel issue + cell 17 correlation pivot |
| `src/visualization.py` | Removed unused `score_lookup` variable (ruff F841 fix) |
| `requirements.txt` | Deduplicated; added `ipykernel>=6.0`, `flask>=3.0` |
| `README.md` | Full rewrite — Resource Desert only, 7-step run guide, pipeline flowchart, data sources table |
| `data/raw/jacksonville_zctas.geojson` | 83 Jacksonville ZCTAs filtered from Census TIGER/Line 2022 ZCTA5 shapefile |
| `specs/003-flask-presentation-dashboard/spec.md` | 5 user stories (P1/P1/P2/P2/P3), FRs, clarifications applied |
| `specs/003-flask-presentation-dashboard/research.md` | 6 research decisions (threading, file serving, choropleth iframe, JS polling, testing, CSS) |
| `specs/003-flask-presentation-dashboard/data-model.md` | 5 entities with field tables, lifecycle diagram, file dependency map |
| `specs/003-flask-presentation-dashboard/plan.md` | Technical context, constitution check, project structure, key design decisions |
| `specs/003-flask-presentation-dashboard/contracts/routes.md` | 5 Flask route contracts (request, response, side-effects, security) |
| `specs/003-flask-presentation-dashboard/contracts/templates.md` | 7 Jinja2 template variable contracts with types and missing-file behaviour |
| `specs/003-flask-presentation-dashboard/quickstart.md` | Developer quickstart with troubleshooting table |
| `specs/003-flask-presentation-dashboard/tasks.md` | 30 tasks across 8 phases; all marked [X] complete |
| `app.py` | Flask app — 5 routes, data loaders, background notebook runner, thread-safe state |
| `webapp/templates/index.html` | Single Jinja2 template — 5 sections, sticky nav, all graceful fallbacks |
| `webapp/static/css/style.css` | ~300-line hand-written CSS — navy/red/green palette, responsive |
| `webapp/static/js/app.js` | Regenerate button wiring + recursive setTimeout/fetch polling |
| `tests/test_app.py` | 33 tests — all 5 route contracts, data loaders, notebook thread; 98% coverage |
| `docs/project_presentation.html` | 613 KB standalone HTML — all 7 charts base64-inlined, all data embedded |
| `docs/architecture.md` | 691-line architecture document covering all 11 aspects of the system |
| `docs/prompt-dialog.md` | Updated with all dialogs from Session 2 (this entry) |
