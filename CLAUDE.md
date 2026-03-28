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
- Commit prefix: `[case1] <description>`
- Clear notebook outputs before committing.

---

## Available Skills

| Skill | When to Use |
|---|---|
| `/data-evaluation-skill` | First pass on a new dataset — profiling and quality assessment |
| `/data-cleaning-skill` | Nulls, type coercion, outliers, standardisation |
| `/data-visualization-skill` | EDA charts or final presentation maps/plots |
| `/code-review-skill` | Reviewing `src/` code for quality and conventions |
| `/unit-testing-skill` | Writing pytest unit tests |
| `/end-to-end-testing-skill` | Full pipeline integration tests |

---

*Last updated: 2026-03-28*

## Active Technologies
- Python 3.11+ + pandas ≥2.0, numpy ≥1.26, matplotlib ≥3.8, seaborn ≥0.13, jupyter ≥1.0, openpyxl (for Metadata.xlsx reference reads) (002-per-dataset-eda-notebooks)
- Local files only — reads from `data/raw/`, no writes (002-per-dataset-eda-notebooks)

## Recent Changes
- 002-per-dataset-eda-notebooks: Added Python 3.11+ + pandas ≥2.0, numpy ≥1.26, matplotlib ≥3.8, seaborn ≥0.13, jupyter ≥1.0, openpyxl (for Metadata.xlsx reference reads)
