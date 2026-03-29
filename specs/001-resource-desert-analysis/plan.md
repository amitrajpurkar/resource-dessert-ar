# Implementation Plan: Resource Desert Analysis & Optimization

**Branch**: `001-resource-desert-analysis` | **Date**: 2026-03-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-resource-desert-analysis/spec.md`

## Summary

Build a demand-weighted Resource Desert Score per Jacksonville ZIP code by merging 9 raw datasets (census, CDC PLACES, USDA food access, healthcare workers, parks, SVI, FEMA), quantify the preventative-asset → health-outcome causal chain, and deliver a gap-closure simulation identifying the single highest-impact intervention. Output: Jupyter notebook + standalone Folium choropleth HTML + CSV/JSON reports.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: pandas ≥2.0, numpy ≥1.26, scikit-learn ≥1.4, matplotlib ≥3.8, seaborn ≥0.13, folium ≥0.15, geopandas ≥0.14, jupyter ≥1.0, openpyxl ≥3.1, pytest ≥8.0, pytest-cov ≥4.1, ruff ≥0.4, black ≥24.0
**Storage**: Local files only — reads from `data/raw/` (read-only); writes to `data/processed/`, `reports/outputs/`, `reports/figures/`
**Testing**: pytest + pytest-cov; ≥70% line coverage hard gate; unit tests use synthetic fixture DataFrames only; e2e tests tagged `@pytest.mark.e2e`
**Target Platform**: Local workstation — Jupyter notebook + HTML file export; no server required
**Project Type**: Data science analysis pipeline (notebook-first, src/ modules back it)
**Performance Goals**: End-to-end pipeline completes in <5 minutes on a laptop; static analysis (no real-time data)
**Constraints**: Offline-capable (local files only); figures at ≥150 DPI; ≥70% test coverage; no `print()` in `src/`; no hardcoded paths outside `src/config.py`
**Scale/Scope**: ~30–50 Jacksonville (Duval County) ZIP codes; 9 raw CSV datasets + 1 XLSX metadata file

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| # | Gate | Status | Notes |
|---|------|--------|-------|
| G1 | `ruff check src/ tests/` — zero errors | PENDING | No src/ code yet |
| G2 | `black --check src/ tests/` — zero formatting violations | PENDING | No src/ code yet |
| G3 | `pytest tests/ -v -m "not e2e"` — all unit tests pass | PENDING | No tests yet |
| G4 | `pytest tests/ --cov=src --cov-fail-under=70` — coverage ≥ 70% | PENDING | No src/ code yet |
| G5 | No files under `data/raw/` appear in the git diff | PASS | `data/raw/` is read-only |
| G6 | All public functions have type hints + Google-style docstrings | PENDING | Implementation phase |
| G7 | All file paths use `pathlib.Path`; no hardcoded strings outside `src/config.py` | PENDING | Implementation phase |
| G8 | Random seeds set (`np.random.seed(42)`, `random.seed(42)`) | PENDING | Implementation phase |

**Complexity Tracking**: None required — single project, no speculative abstractions.

## Project Structure

### Documentation (this feature)

```text
specs/001-resource-desert-analysis/
├── plan.md              ← This file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/           ← Phase 1 output (pipeline I/O contracts)
├── column-reference.md  ← Existing column definitions from Metadata.xlsx
├── checklists/
│   └── requirements.md
└── tasks.md             ← Phase 2 output (/speckit.tasks — NOT created here)
```

### Source Code (repository root)

```text
src/
├── config.py            ← All Path constants; no hardcoded strings elsewhere
├── ingestion.py         ← Load raw CSVs/XLSX; validate shape/dtypes/nulls; return raw DataFrames
├── cleaning.py          ← Fix types, nulls, duplicates, outliers; post-clean assertions
├── features.py          ← Composite Desert Score; demand factor; normalization
├── models.py            ← Gap-closure simulation; intervention ranking; cross-validation (if model added)
└── visualization.py     ← All plot functions; Folium choropleth; save to reports/figures/

notebooks/
└── resource_desert_analysis.ipynb   ← End-to-end prototype notebook

reports/
├── figures/             ← All saved plots (≥150 DPI, descriptive filenames)
└── outputs/
    ├── desert_scores.csv
    ├── intervention_recommendations.json
    └── resource_desert_map.html

tests/
├── __init__.py
├── conftest.py          ← Synthetic fixture DataFrames
├── test_ingestion.py
├── test_cleaning.py
├── test_features.py
├── test_models.py
├── test_visualization.py
└── e2e/
    ├── __init__.py
    └── test_pipeline_e2e.py   ← @pytest.mark.e2e — uses real data/raw/

data/
├── raw/                 ← Read-only source files (Census, CDC, USDA, etc.)
├── processed/           ← Merged/cleaned datasets written by pipeline
└── outputs/             ← Model outputs (also referenced from reports/outputs/)
```

**Structure Decision**: Single Python project. Five-module `src/` pipeline (ingestion → cleaning → features → models → visualization) as required by the project constitution. Notebook in `notebooks/` orchestrates the pipeline for the prototype deliverable.

## Complexity Tracking

No violations to justify. Pipeline follows the minimum viable 5-stage architecture mandated by the project constitution. No abstractions added beyond what the feature requires.
