# Implementation Plan: Per-Dataset EDA Notebooks

**Branch**: `002-per-dataset-eda-notebooks` | **Date**: 2026-03-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-per-dataset-eda-notebooks/spec.md`

## Summary

Produce 9 standalone Jupyter notebooks (one per raw data file in `data/raw/`) covering schema profiling, IQR-based data quality assessment, univariate distributions, and a domain-relevant ranked bar chart analysis. Notebooks are exploration artifacts — no transformation logic, no maps, no external dependencies beyond the project's standard data science stack.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: pandas ≥2.0, numpy ≥1.26, matplotlib ≥3.8, seaborn ≥0.13, jupyter ≥1.0, openpyxl (for Metadata.xlsx reference reads)
**Storage**: Local files only — reads from `data/raw/`, no writes
**Testing**: pytest ≥8.0 with `nbconvert` or `nbmake` to execute notebooks in CI
**Target Platform**: Local Jupyter server (macOS/Linux)
**Project Type**: Data science / exploratory analysis notebooks
**Performance Goals**: Each notebook completes execution in under 60 seconds on a standard laptop
**Constraints**: No internet access required; no files outside `data/raw/` or `data/processed/` loaded
**Scale/Scope**: 9 notebooks × ~60–80 ZIP rows each; all datasets fit comfortably in memory

## Constitution Check

*Constitution: `.specify/memory/constitution.md` v1.0.0 — checked 2026-03-28.*

| Gate | Status | Notes |
|---|---|---|
| **I. Python Code Quality** — ruff/black on all code cells | ✅ Pass | FR-010; Phase 6 enforces `ruff check notebooks/` and `black` via nbqa |
| **I. Python Code Quality** — no `print()` in src/ | ✅ N/A | No new `src/` modules produced by this feature |
| **II. Reproducibility** — seeds for any randomness | ✅ Pass | FR-011; no ML training in this feature; if any sampling occurs, seed(42) is required |
| **II. Reproducibility** — raw data immutable | ✅ Pass | FR-008; notebooks read-only from `data/raw/` |
| **II. Reproducibility** — 5-stage pipeline architecture | ✅ N/A | EDA notebooks are pre-pipeline exploration; no `src/` pipeline stages introduced |
| **III. Test-First** — e2e tests written before notebooks | ✅ Pass | Phase 2 (T005–T006) creates test runner before Phase 3 notebooks begin |
| **III. Test-First** — ≥70% coverage on src/ | ✅ N/A | No new `src/` code in this feature; coverage gate applies to existing `src/` baseline |
| **IV. Data Integrity** — log row drops | ✅ N/A | Notebooks observe data only; no drops performed (flags are observational per FR-003) |
| **IV. Data Integrity** — figures ≥150 DPI | ✅ N/A | EDA chart outputs are inline notebook outputs, not saved to `reports/figures/` |
| **V. Simplicity** — no speculative abstractions | ✅ Pass | No shared helpers or utilities; notebooks are fully self-contained |
| **VI. Analytical Rigour** — spatial IDs explicit | ✅ Pass | ZIP code presence and format checked in Section 1 of every notebook |

**No violations.** No complexity justification required.

## Project Structure

### Documentation (this feature)

```text
specs/002-per-dataset-eda-notebooks/
├── plan.md              ← This file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/
│   └── data-quality-flag-schema.md   ← Phase 1 output
└── tasks.md             ← Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
notebooks/
└── eda/
    ├── eda_cdc_places.ipynb
    ├── eda_census_demographics.ipynb
    ├── eda_census_housing_poverty.ipynb
    ├── eda_fema.ipynb
    ├── eda_healthcare_access.ipynb
    ├── eda_healthcare_workers.ipynb
    ├── eda_parks.ipynb
    ├── eda_social_vulnerability.ipynb
    └── eda_usda_food_access.ipynb

tests/
└── e2e/
    └── test_eda_notebooks.py    ← @pytest.mark.e2e — runs each notebook end-to-end
```

**Structure Decision**: Single-project layout. No new `src/` modules — notebooks are fully self-contained per FR-009. The only new test file is an e2e suite that executes all 9 notebooks and asserts zero errors.

## Complexity Tracking

No constitution violations.
