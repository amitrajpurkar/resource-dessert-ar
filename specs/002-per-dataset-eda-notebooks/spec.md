# Feature Specification: Per-Dataset EDA Notebooks

**Feature Branch**: `002-per-dataset-eda-notebooks`
**Created**: 2026-03-28
**Status**: Draft
**Input**: User description: "before the User Scenarios section in @specs/001-resource-desert-analysis/spec.md add a section to produce one Jupyter notebook each for each data file and have snippets in these notebooks to analyze all aspects for each data file"

## Dataset Coverage

This feature produces one standalone exploratory analysis notebook per raw data file. The 9 notebooks correspond to the files in `data/raw/`:

| Notebook | Source File | Domain |
|---|---|---|
| `eda_cdc_places.ipynb` | `CDCPlaces.csv` | Chronic disease & health behavior prevalence by ZIP |
| `eda_census_demographics.ipynb` | `Census-Demographics.csv` | Population, age, race composition |
| `eda_census_housing_poverty.ipynb` | `Census-Housing&Poverty.csv` | Housing cost burden, poverty rates |
| `eda_fema.ipynb` | `FEMA.csv` | Disaster risk and vulnerability indicators |
| `eda_healthcare_access.ipynb` | `HealthCareAccess.csv` | Insurance coverage and access barriers |
| `eda_healthcare_workers.ipynb` | `HealthCareWorkers.csv` | Provider counts and specialties |
| `eda_parks.ipynb` | `Parks.csv` | Park presence and access |
| `eda_social_vulnerability.ipynb` | `SocialVulnerabilityIndex.csv` | Composite vulnerability scores |
| `eda_usda_food_access.ipynb` | `USDA-FoodAccess.csv` | Food desert classification and grocery access |

The `Metadata.xlsx` file is consulted as a reference for column definitions — it does not receive its own EDA notebook.

---

## Clarifications

### Session 2026-03-28

- Q: Should the domain analysis section include choropleth maps for ZIP-coded datasets? → A: No maps in EDA notebooks. Domain analysis uses ranked bar charts (top/bottom ZIPs by key metric) only. Maps are reserved for the main analysis spec (001).
- Q: Which outlier detection method should the data quality section use? → A: IQR method — flag values below Q1 − 1.5×IQR or above Q3 + 1.5×IQR. More robust than std-dev for the skewed socioeconomic and health distributions in this project.
- Q: What should the Data Quality Flag communicate about high-null columns (>30%)? → A: Warn only — label the column "too sparse" as an observation. No drop recommendation. Pipeline drop decisions belong in src/cleaning.py, not in exploration notebooks.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Understand a Single Dataset End-to-End (Priority: P1)

A data analyst opens any one of the EDA notebooks and can immediately understand the shape, quality, and key distributions of that dataset without reading any other file. All sections needed to assess data readiness are present and pre-executed.

**Why this priority**: Every downstream analysis (scoring, correlation, visualization) depends on understanding each source dataset first. A single reliable notebook delivers standalone value for its dataset.

**Independent Test**: Open `eda_cdc_places.ipynb`, run all cells top-to-bottom, and verify that the output covers schema, null counts, distributions, and at least one domain-relevant insight — with no errors.

**Acceptance Scenarios**:

1. **Given** the raw `CDCPlaces.csv` file, **When** the corresponding EDA notebook is run, **Then** it displays row/column counts, dtype summary, and null percentage per column without errors.
2. **Given** the notebook has run, **When** a reviewer scrolls to the distributions section, **Then** histograms or bar charts are shown for all numeric columns, each with a labelled axis and title.
3. **Given** the notebook has run, **When** a reviewer views the data quality section, **Then** duplicate row count and any constant/near-constant columns are identified and flagged.

---

### User Story 2 - Identify Data Quality Issues Before Pipeline Integration (Priority: P2)

A developer building the main analysis pipeline opens an EDA notebook to understand which columns are safe to use, which need cleaning, and which have too many nulls to be reliable — before writing any pipeline code.

**Why this priority**: Prevents silent data quality issues from propagating into the Desert Score computation. Notebooks act as a contract between raw data and pipeline assumptions.

**Independent Test**: Open `eda_census_housing_poverty.ipynb`, run all cells, and confirm that a summary table lists each column with its null rate, data type, and a recommendation flag (e.g., "usable", "needs cleaning", "too sparse").

**Acceptance Scenarios**:

1. **Given** any EDA notebook, **When** it is run, **Then** columns with >30% null values are explicitly flagged as high-risk in the data quality summary.
2. **Given** a dataset with mixed ZIP code formats (e.g., integer vs. string), **When** the notebook runs, **Then** the inconsistency is detected and reported in the data quality section.
3. **Given** a dataset with outliers, **When** the notebook runs, **Then** the outlier detection section identifies values outside the IQR fence (Q1 − 1.5×IQR / Q3 + 1.5×IQR) and shows which ZIPs they belong to.

---

### User Story 3 - Discover Domain-Relevant Patterns per Dataset (Priority: P3)

A judge or teammate opens a notebook expecting to see not just raw summaries but also domain-relevant analysis — e.g., which ZIPs have the highest disease burden in the CDC notebook, or which provider specialties are most concentrated in the healthcare workers notebook.

**Why this priority**: Bridges raw data profiling and the Resource Desert narrative. Notebooks should tell a story about each dataset, not just describe it mechanically.

**Independent Test**: Open `eda_healthcare_workers.ipynb`, run all cells, and verify that at least one domain-specific chart or table is present (e.g., top 10 ZIPs by provider density, or specialty breakdown chart).

**Acceptance Scenarios**:

1. **Given** `eda_healthcare_workers.ipynb`, **When** run, **Then** it shows the distribution of provider types and identifies the top and bottom 5 ZIPs by provider-to-population ratio.
2. **Given** `eda_usda_food_access.ipynb`, **When** run, **Then** it shows the proportion of ZIP codes classified as food deserts and a ranked bar chart of the most food-insecure ZIPs.
3. **Given** `eda_social_vulnerability.ipynb`, **When** run, **Then** it shows the distribution of the composite SVI score and highlights which ZIPs fall in the top quartile of vulnerability.

---

### Edge Cases

- What if a raw file is missing or corrupted? → The notebook must fail with a clear error message at the data loading cell, not silently produce empty outputs.
- What if a dataset has no numeric columns? → Skip distribution plots and note this explicitly; proceed with categorical frequency tables.
- What if a ZIP code column is absent in a dataset? → Note the absence in the schema section; do not attempt geographic analysis for that notebook.
- What if a column name differs from the Metadata.xlsx definition? → Flag the discrepancy in the schema section and use the column name as-is.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: One notebook MUST exist per raw data file (9 notebooks total, excluding Metadata.xlsx).
- **FR-002**: Every notebook MUST include, in order: (1) data loading & schema summary, (2) data quality assessment, (3) univariate distributions, (4) domain-relevant analysis section.
- **FR-003**: The data quality section MUST report: row count, column count, null percentage per column, duplicate row count, per-numeric-column outlier counts using the IQR method (Q1 − 1.5×IQR / Q3 + 1.5×IQR), and a Data Quality Flag per column ("usable", "needs cleaning", or "too sparse" for >30% null). Flags are observational warnings only — no drop recommendations.
- **FR-004**: The univariate distributions section MUST produce a chart for every numeric column and a frequency table for every categorical column with ≤20 unique values.
- **FR-005**: The domain-relevant section MUST include at least one ranked bar chart showing top and bottom ZIPs by a key metric specific to the dataset's subject matter (e.g., top 10 ZIPs by disease burden, bottom 10 ZIPs by provider density). No choropleth maps in EDA notebooks.
- **FR-006**: Every notebook MUST run top-to-bottom without errors against the files currently in `data/raw/`.
- **FR-007**: All charts within notebooks MUST have a descriptive title and labelled axes (with units where applicable).
- **FR-008**: Notebooks MUST NOT load or depend on any file outside `data/raw/` and `data/processed/`.
- **FR-009**: Notebooks are for exploration only — no transformation logic that belongs in `src/` may be defined inline in a notebook cell.
- **FR-010**: All Python code cells in notebooks MUST pass `ruff check` with zero errors; `black` formatting conventions MUST be applied to all code cells.
- **FR-011**: If any notebook cell performs random sampling, `np.random.seed(42)` MUST be set in that cell before the sampling call.
- **FR-012**: Notebook outputs MUST be cleared (`jupyter nbconvert --clear-output`) before committing to git.
- **FR-013**: The e2e test suite (`tests/e2e/test_eda_notebooks.py`) MUST verify all 9 notebooks execute without errors; tests MUST be tagged `@pytest.mark.e2e` and excluded from the default `pytest` run.

### Key Entities

- **EDA Notebook**: A self-contained, sequentially executable document covering one raw dataset. Attributes: source file name, section structure (schema → quality → distributions → domain analysis), execution status.
- **Schema Summary**: The opening section of each notebook. Captures column names, inferred data types, and null rates for every column in the dataset.
- **Data Quality Flag**: A per-column observational annotation: "usable" (≤30% null, clean type), "needs cleaning" (type issues or moderate nulls), or "too sparse" (>30% null — warning only, no drop recommendation). Pipeline drop decisions are made in `src/cleaning.py`, not in notebooks.
- **Domain Analysis**: The dataset-specific section containing at least one insight relevant to the Resource Desert problem (e.g., provider concentration, food access gaps, disease burden rankings by ZIP).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 9 EDA notebooks run without errors from top to bottom against the files in `data/raw/`.
- **SC-002**: Every notebook covers all 4 required sections (schema, quality, distributions, domain analysis) — verifiable by section heading presence.
- **SC-003**: A reviewer can determine whether any given column is safe to use in the pipeline within 60 seconds of opening the relevant notebook, using the data quality summary alone.
- **SC-004**: Every numeric column in every dataset has at least one distribution visualization produced by the notebooks.
- **SC-005**: Each notebook's domain analysis section contains at least one finding that directly relates to the Resource Desert problem framing (supply/demand mismatch or health outcome).

---

## Constitution Compliance

This feature is governed by the project constitution at `.specify/memory/constitution.md` (v1.0.0).
Principles apply as follows for a notebooks-only feature (no new `src/` modules produced):

| Principle | How It Applies Here |
|---|---|
| I. Python Code Quality | FR-010 (ruff/black on notebook code cells); no `print()` — use `display()` or direct cell output |
| II. Data Science Reproducibility | FR-011 (seeds for any sampling); FR-008 (raw data read-only, no writes); no global state in notebooks |
| III. Test-First Development | FR-013 (e2e test suite with `@pytest.mark.e2e`; written before notebooks); ≥70% coverage gate applies to `src/` — no new `src/` code in this feature, so gate is satisfied by the e2e suite itself |
| IV. Data Integrity & Observability | FR-007 (titled, labelled charts); FR-003 (null rates and outlier counts explicitly reported) |
| V. Simplicity & YAGNI | No helper utilities in notebooks; no imports of custom modules not already in requirements.txt |
| VI. Analytical Rigour | FR-005 (domain analysis must name the metric and units); ZIP code as explicit geographic identifier checked in schema section per FR-002 |

**Quality Gates** (all must pass before this feature is merged):

1. `ruff check notebooks/` — zero errors in notebook code cells (via `nbqa ruff`)
2. `pytest tests/ -v -m "not e2e"` — no regressions in existing unit tests
3. `pytest --nbmake notebooks/eda/ -v` — all 9 notebooks execute without errors (`@pytest.mark.e2e`)
4. `jupyter nbconvert --clear-output notebooks/eda/*.ipynb` — outputs cleared before commit
5. No files under `data/raw/` appear in the git diff

---

## Assumptions

- Notebooks are placed in `notebooks/eda/` subdirectory within the existing `notebooks/` folder.
- Each notebook is named using the pattern `eda_<source_file_stem>.ipynb` (lowercase, underscores).
- The Metadata.xlsx column definitions are consulted when naming or interpreting columns, but the notebook reads each source file directly from `data/raw/`.
- "All aspects" of each dataset means: schema, nulls, duplicates, univariate distributions, and one domain-relevant multi-column or ranked analysis — not exhaustive multivariate modelling (that belongs in the main analysis pipeline).
- Notebooks are exploration artifacts; they will have outputs cleared before committing to git per project convention.
- ZIP code is the expected join key across datasets; its presence and format are explicitly checked in each notebook's schema section.
