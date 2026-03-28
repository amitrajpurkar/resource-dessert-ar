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

## Summary of All Artifacts Produced

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
