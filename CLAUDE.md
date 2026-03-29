# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Problem Context

This repository is for **Problem Case: Resource Desert — Optimizing Services Reach** from the **2025 UNF CodeforAwhile Datathon**.

**Goal:** Identify Jacksonville neighborhoods that qualify as "Resource Deserts" — where essential services are physically or financially out of reach — and propose a data-driven AI solution to bridge the gap between supply of care and community demand.

**Three key questions to answer:**
1. What is the biggest mismatch between residents and available essential services (by neighborhood/ZIP)?
2. How do resource deserts directly affect long-term health outcomes? (Show relationship between lack of preventative assets and poor outcomes.)
3. Propose an AI solution to put the right resources in the right places for a specific Jacksonville community.

**Deliverable:** A functional prototype (mapping tool or data dashboard) highlighting service gaps or proposing optimized delivery strategies.

---

## Data Sources (`data/raw/` — read-only)

| File | Source | Contents |
|---|---|---|
| `Census-Demographics.csv` | U.S. Census Bureau | Population, age, race by area |
| `Census-Housing&Poverty.csv` | U.S. Census Bureau | Housing cost burden, poverty rates |
| `CDCPlaces.csv` | CDC | Chronic disease prevalence, health behaviors by ZIP |
| `FEMA.csv` | FEMA | Disaster risk, vulnerability indicators |
| `HealthCareAccess.csv` | NPPES / EPA EJScreen | Insurance coverage, access barriers |
| `HealthCareWorkers.csv` | NPPES | Provider counts and specialties by area |
| `Parks.csv` | NaNDA | Park presence and access by neighborhood |
| `SocialVulnerabilityIndex.csv` | CDC SVI | Composite vulnerability scores |
| `USDA-FoodAccess.csv` | USDA FARA | Food desert classification, grocery access |
| `Metadata.xlsx` | — | Column definitions and data dictionary |

**Key analytical concept:** "Preventative Assets" (parks, primary care, healthy food) → absence leads to "Poor Outcomes" (poor mental health, low life expectancy). The analysis should operationalize this causal chain.

---

## Project Structure

```
prob1-resource-desert/
├── data/
│   ├── raw/          ← Original source files — never modify
│   ├── processed/    ← Cleaned/merged datasets
│   └── outputs/      ← Model outputs, scores, predictions
├── notebooks/        ← Exploratory analysis only
├── src/              ← Importable modules (ingestion, cleaning, features, models, viz)
├── tests/            ← pytest unit and e2e tests
└── reports/
    ├── figures/      ← All saved plots (descriptive filenames, ≥150 DPI)
    └── outputs/      ← Metric summaries, written findings
```

---


## Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run only unit tests (no real data)
pytest tests/ -v -m "not e2e"

# Run a single test file
pytest tests/test_cleaning.py -v

# Lint and format
ruff check src/ tests/
black --check src/ tests/
black src/ tests/          # auto-format
```

---

## Code Conventions

- **Paths:** Use `pathlib.Path`. Define all paths in `src/config.py` — no hardcoded strings.
- **Logging:** Use `logging` module, not `print`. Log record counts before/after every transformation.
- **Docstrings:** Google-style with `Args`, `Returns`, `Raises` on all public functions.
- **Type hints:** Required on all function signatures.
- **Random seeds:** `np.random.seed(42)` and `random.seed(42)` wherever randomness appears.
- **Row drops:** Never silent. Log count and reason before dropping.
- **Tests:** Synthetic fixture DataFrames only in unit tests. E2E tests tagged `@pytest.mark.e2e`.
- **Figures:** Every plot needs title, labelled axes with units, legend if multi-series. Save via `fig.savefig(...)`.

---

## Pipeline Architecture

Modules in `src/` should follow this separation:

1. **`ingestion`** — load raw CSVs, validate shape/dtypes/nulls, return raw DataFrames
2. **`cleaning`** — fix types, handle nulls/duplicates/outliers, assert post-clean invariants
3. **`features`** — construct composite scores (e.g. resource desert index, vulnerability score)
4. **`models`** — baseline then advanced; always cross-validate; write metrics to `reports/outputs/`
5. **`visualization`** — all plot functions; choropleth maps for spatial analysis

No global state — pass DataFrames and config explicitly as arguments.

---

## Git Conventions

- Branch: `case1/resource-desert-<feature>`
- Clear notebook outputs before committing.
- Commit messages: `[case1] add null-handling for revenue columns`
- Do not commit notebooks with large cell outputs — clear outputs before committing.
- Do not commit raw data files if they are large (>10 MB) — add to `.gitignore` and document where to obtain them.


---


## Available Skills
Use these skills (via `.claude/skills/`) to get structured, expert assistance on specific tasks:

| Skill | When to Use |
|---|---|
| `/data-evaluation-skill` | First pass on a new dataset — profiling and quality assessment |
| `/data-cleaning-skill` | Nulls, type coercion, outliers, standardisation |
| `/data-visualization-skill` | EDA charts or final presentation maps/plots |
| `/code-review-skill` | Reviewing `src/` code for quality and conventions |
| `/unit-testing-skill` | Writing pytest unit tests |
| `/end-to-end-testing-skill` | Full pipeline integration tests |

---


**Rules:**
- Never overwrite files in `data/raw/`. Always write processed outputs to `data/processed/`.
- Notebooks in `notebooks/` are for exploration only. Production code lives in `src/`.
- All figures saved to disk go in `reports/figures/` with descriptive filenames.

---

## Design Principles

### 1. Reproducibility First
- Set random seeds explicitly wherever randomness is involved: `np.random.seed(42)`, `random.seed(42)`.
- Pin library versions in `requirements.txt` or `pyproject.toml`.
- All data transformations must be scripted — never manually edit raw data files.
- Pipelines must be runnable end-to-end from a clean environment with a single command.

### 2. Code Quality
- Follow **PEP 8** for all Python code. Use `black` for formatting, `ruff` or `flake8` for linting.
- All public functions and classes must have **Google-style docstrings** with `Args`, `Returns`, and `Raises` sections.
- Use **type hints** on all function signatures (`def clean_df(df: pd.DataFrame) -> pd.DataFrame:`).
- Keep functions small and single-purpose. If a function exceeds ~40 lines, decompose it.
- Avoid notebook-style imperative scripting in `src/` — write functions and classes.

### 3. Data Integrity
- Always validate input data at the start of every pipeline stage (shape, dtypes, null counts).
- Never silently drop rows. Log or raise when data is discarded, with counts and reasons.
- Document every transformation with a comment explaining *why*, not just *what*.
- After cleaning, run a post-clean assertion suite to confirm invariants hold.

### 4. Modularity & Separation of Concerns
- Separate data ingestion, cleaning, feature engineering, modelling, and reporting into distinct modules.
- No hardcoded file paths. Use `pathlib.Path` and define paths in a central `config.py` or via environment variables.
- Avoid global state. Pass DataFrames and configurations explicitly as function arguments.

### 5. Observability
- Use Python's built-in `logging` module (not `print`) for runtime messages.
- Log pipeline entry/exit, record counts before and after each transformation, and any anomalies found.
- All models must output a summary of evaluation metrics — do not just print them; write them to `reports/outputs/`.

### 6. Testing
- Every function in `src/` must have a corresponding unit test in `tests/`.
- Use `pytest` as the test runner. Tests must pass before any code is considered done.
- Use small, synthetic fixture DataFrames in tests — never load real raw data in unit tests.
- Integration/end-to-end tests may use real data but must be tagged `@pytest.mark.e2e` and isolated.

### 7. Visualisation Standards
- Use **matplotlib** or **seaborn** as the primary plotting libraries.
- Every plot must have: a descriptive title, labelled axes (with units), and a legend if multiple series.
- Save all figures programmatically with `fig.savefig(...)` at 150 DPI minimum. Never rely on interactive display alone.
- Use a consistent colour palette across all plots in a single problem case.

### 8. Model Development
- Always establish a **baseline model** before attempting complex approaches.
- Report metrics appropriate to the task type: classification → precision/recall/F1/AUC; regression → MAE/RMSE/R².
- Use cross-validation, not a single train/test split, unless the dataset is too small.
- Document model assumptions, hyperparameter choices, and limitations explicitly.

---


*Last updated: 2026-03-28*

## Active Technologies
- Python 3.11+ + pandas ≥2.0, numpy ≥1.26, matplotlib ≥3.8, seaborn ≥0.13, jupyter ≥1.0, openpyxl (for Metadata.xlsx reference reads) (002-per-dataset-eda-notebooks)
- Local files only — reads from `data/raw/`, no writes (002-per-dataset-eda-notebooks)

## Recent Changes
- 002-per-dataset-eda-notebooks: Added Python 3.11+ + pandas ≥2.0, numpy ≥1.26, matplotlib ≥3.8, seaborn ≥0.13, jupyter ≥1.0, openpyxl (for Metadata.xlsx reference reads)
