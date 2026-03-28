# Tasks: Per-Dataset EDA Notebooks

**Input**: Design documents from `/specs/002-per-dataset-eda-notebooks/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Organization**: Tasks are grouped by user story. Each story maps to a distinct notebook section added across all 9 notebooks, so stories can be implemented and validated independently.

**Story → Section mapping**:
- US1 (P1): Section 1 (Schema Summary) + Section 3 (Univariate Distributions) — establishes runnable baseline
- US2 (P2): Section 2 (Data Quality Assessment — IQR outliers + quality flags)
- US3 (P3): Section 4 (Domain-Relevant Ranked Bar Charts)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (separate notebook files, no inter-file dependencies)
- **[Story]**: User story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup

**Purpose**: Directory structure, test scaffold, and metadata reference — must complete before any notebook is written.

- [x] T001 Create `notebooks/eda/` directory (mkdir -p notebooks/eda)
- [x] T002 Create `tests/e2e/` directory and empty `tests/e2e/__init__.py`
- [x] T003 Add `nbmake` to `requirements.txt` for notebook e2e testing
- [x] T004 [P] Read `data/raw/Metadata.xlsx` and produce `specs/002-per-dataset-eda-notebooks/column-reference.md` listing column names and definitions for all 9 source files — used as reference when writing schema section headers

**Checkpoint**: Directory structure ready; column reference available for notebook authors.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared e2e test runner that validates all 9 notebooks — written once, extended as notebooks are added.

⚠️ **CRITICAL**: The test file scaffold MUST exist before user story phases begin (Constitution Principle III — Test-First). Tests MUST be written first and verified to fail (no notebooks yet) before implementation starts.

- [x] T005 Create `tests/e2e/test_eda_notebooks.py` with a parameterized e2e test using `nbmake` that discovers and executes all `.ipynb` files in `notebooks/eda/`, tagged `@pytest.mark.e2e`
- [x] T006 Verify `pytest --nbmake notebooks/eda/ -v` command works on an empty directory (returns 0 notebooks collected, no errors) — confirms test runner is functional before notebooks exist (Red phase of TDD)

**Checkpoint**: Test runner ready. Each notebook added in Phases 3–5 is immediately testable via `pytest --nbmake notebooks/eda/<name>.ipynb`.

---

## Phase 3: User Story 1 — Understand a Single Dataset End-to-End (Priority: P1) 🎯 MVP

**Goal**: All 9 notebooks exist, run top-to-bottom without errors, and display schema + univariate distributions (Sections 1 and 3). A reviewer can open any notebook and immediately understand the shape, dtypes, and key distributions of that dataset.

**Independent Test**: `pytest --nbmake notebooks/eda/eda_cdc_places.ipynb -v` passes; the executed notebook shows row count, dtype table, null percentages, and histograms for all numeric columns.

### Implementation for User Story 1

- [x] T007 [P] [US1] Create `notebooks/eda/eda_cdc_places.ipynb` with Section 1 (load `data/raw/CDCPlaces.csv`, display shape, dtype table, null % per column, ZIP key check) and Section 3 (histogram per numeric column, frequency table per categorical ≤20 unique values; all charts titled and axis-labelled)
- [x] T008 [P] [US1] Create `notebooks/eda/eda_census_demographics.ipynb` with Section 1 (load `data/raw/Census-Demographics.csv`, same schema profiling) and Section 3 (distributions for all numeric/categorical columns)
- [x] T009 [P] [US1] Create `notebooks/eda/eda_census_housing_poverty.ipynb` with Section 1 (load `data/raw/Census-Housing&Poverty.csv`) and Section 3 (distributions)
- [x] T010 [P] [US1] Create `notebooks/eda/eda_fema.ipynb` with Section 1 (load `data/raw/FEMA.csv`) and Section 3 (distributions)
- [x] T011 [P] [US1] Create `notebooks/eda/eda_healthcare_access.ipynb` with Section 1 (load `data/raw/HealthCareAccess.csv`) and Section 3 (distributions)
- [x] T012 [P] [US1] Create `notebooks/eda/eda_healthcare_workers.ipynb` with Section 1 (load `data/raw/HealthCareWorkers.csv`) and Section 3 (distributions)
- [x] T013 [P] [US1] Create `notebooks/eda/eda_parks.ipynb` with Section 1 (load `data/raw/Parks.csv`) and Section 3 (distributions)
- [x] T014 [P] [US1] Create `notebooks/eda/eda_social_vulnerability.ipynb` with Section 1 (load `data/raw/SocialVulnerabilityIndex.csv`) and Section 3 (distributions)
- [x] T015 [P] [US1] Create `notebooks/eda/eda_usda_food_access.ipynb` with Section 1 (load `data/raw/USDA-FoodAccess.csv`) and Section 3 (distributions)

**Checkpoint**: All 9 notebooks exist and pass `pytest --nbmake notebooks/eda/ -v`. User Story 1 is independently complete.

---

## Phase 4: User Story 2 — Identify Data Quality Issues Before Pipeline Integration (Priority: P2)

**Goal**: Add Section 2 (Data Quality Assessment) to all 9 notebooks. Section 2 must show: duplicate row count, per-column Data Quality Flag (usable / needs_cleaning / too_sparse for >30% null), IQR outlier table per numeric column (Q1, Q3, IQR, fences, outlier count, outlier ZIPs). Flags are observational only — no drop recommendations.

**Independent Test**: Open `notebooks/eda/eda_census_housing_poverty.ipynb`, run Section 2 cells; verify the output includes a quality flag table with columns [column_name, null_pct, dtype, quality_flag] and an outlier summary table using IQR fences.

### Implementation for User Story 2

- [x] T016 [P] [US2] Add Section 2 to `notebooks/eda/eda_cdc_places.ipynb`: duplicate count cell, quality flag table (null_pct, dtype, flag: usable/needs_cleaning/too_sparse), IQR outlier table for all numeric columns (Q1, Q3, IQR, lower_fence, upper_fence, outlier_count, outlier_zips)
- [x] T017 [P] [US2] Add Section 2 to `notebooks/eda/eda_census_demographics.ipynb` (same structure as T016)
- [x] T018 [P] [US2] Add Section 2 to `notebooks/eda/eda_census_housing_poverty.ipynb` — note: flag ZIP code column if integer vs. string format inconsistency is detected
- [x] T019 [P] [US2] Add Section 2 to `notebooks/eda/eda_fema.ipynb`
- [x] T020 [P] [US2] Add Section 2 to `notebooks/eda/eda_healthcare_access.ipynb`
- [x] T021 [P] [US2] Add Section 2 to `notebooks/eda/eda_healthcare_workers.ipynb`
- [x] T022 [P] [US2] Add Section 2 to `notebooks/eda/eda_parks.ipynb`
- [x] T023 [P] [US2] Add Section 2 to `notebooks/eda/eda_social_vulnerability.ipynb`
- [x] T024 [P] [US2] Add Section 2 to `notebooks/eda/eda_usda_food_access.ipynb`

**Checkpoint**: All 9 notebooks pass `pytest --nbmake notebooks/eda/ -v` with Section 2 in place. A developer can determine column usability within 60 seconds. User Story 2 independently complete.

---

## Phase 5: User Story 3 — Discover Domain-Relevant Patterns per Dataset (Priority: P3)

**Goal**: Add Section 4 (Domain-Relevant Analysis) to all 9 notebooks. Each Section 4 must include at least one ranked horizontal bar chart showing top/bottom 10 ZIPs by the dataset's primary metric (per data-model.md mapping). No maps — bar charts only. Chart must have descriptive title, labelled axes with units, and a one-sentence note connecting the finding to the Resource Desert narrative.

**Independent Test**: Open `notebooks/eda/eda_healthcare_workers.ipynb`, run Section 4 cells; verify a ranked bar chart is displayed showing top and bottom ZIPs by provider-to-population ratio, with labelled axes and a Resource Desert relevance note.

### Implementation for User Story 3

- [x] T025 [P] [US3] Add Section 4 to `notebooks/eda/eda_cdc_places.ipynb`: ranked bar chart of top/bottom 10 ZIPs by highest chronic disease prevalence rate; include Resource Desert relevance note
- [x] T026 [P] [US3] Add Section 4 to `notebooks/eda/eda_census_demographics.ipynb`: ranked bar chart by population density (pop per sq mile); include Resource Desert relevance note
- [x] T027 [P] [US3] Add Section 4 to `notebooks/eda/eda_census_housing_poverty.ipynb`: ranked bar chart by poverty rate (%); also show housing cost burden distribution; include Resource Desert relevance note
- [x] T028 [P] [US3] Add Section 4 to `notebooks/eda/eda_fema.ipynb`: ranked bar chart by composite disaster risk score; include Resource Desert relevance note
- [x] T029 [P] [US3] Add Section 4 to `notebooks/eda/eda_healthcare_access.ipynb`: ranked bar chart by uninsured rate (%); include Resource Desert relevance note
- [x] T030 [P] [US3] Add Section 4 to `notebooks/eda/eda_healthcare_workers.ipynb`: ranked bar chart by provider-to-population ratio (top and bottom 10 ZIPs); also show provider type breakdown bar chart; include Resource Desert relevance note
- [x] T031 [P] [US3] Add Section 4 to `notebooks/eda/eda_parks.ipynb`: ranked bar chart by park access score or park count per ZIP; include Resource Desert relevance note
- [x] T032 [P] [US3] Add Section 4 to `notebooks/eda/eda_social_vulnerability.ipynb`: ranked bar chart by composite SVI percentile; highlight top-quartile ZIPs; include Resource Desert relevance note
- [x] T033 [P] [US3] Add Section 4 to `notebooks/eda/eda_usda_food_access.ipynb`: ranked bar chart of most food-insecure ZIPs by low-income + low-access population share; show proportion of ZIPs classified as food deserts; include Resource Desert relevance note

**Checkpoint**: All 9 notebooks have all 4 sections and pass `pytest --nbmake notebooks/eda/ -v`. All user stories complete.

---

## Phase 6: Quality Gates & Polish (Constitution Compliance)

**Purpose**: Final validation, quality gate enforcement, and output clearing per constitution v1.0.0.

**⚠️ ALL gates below MUST pass before the branch is considered complete.**

- [ ] T034 Run `pytest --nbmake notebooks/eda/ -v` against all 9 notebooks; confirm 9 notebooks collected, 0 errors (SC-001, Constitution Principle III)
- [x] T035 Verify all 9 notebooks have exactly 4 section headings matching the required order: "Data Loading & Schema Summary", "Data Quality Assessment", "Univariate Distributions", "Domain-Relevant Analysis" (SC-002)
- [x] T036 [P] Run `nbqa ruff notebooks/eda/` — zero linting errors in all notebook code cells (FR-010, Constitution Principle I)
- [x] T037 [P] Run `nbqa black notebooks/eda/ --check` — zero formatting violations; apply `nbqa black notebooks/eda/` to auto-fix if needed (FR-010, Constitution Principle I)
- [x] T038 [P] Clear all notebook outputs before final commit: `jupyter nbconvert --clear-output notebooks/eda/*.ipynb` (FR-012, git convention)
- [x] T039 Verify `specs/002-per-dataset-eda-notebooks/column-reference.md` (T004) matches column names actually found in each notebook's Section 1 schema output — update any discrepancies found
- [x] T040 [P] Confirm no files under `data/raw/` appear in `git diff` — raw data MUST remain unmodified (Constitution Principle II)
- [x] T041 Run `pytest tests/ -v -m "not e2e"` — confirm zero regressions in existing unit tests outside this feature

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS user story phases
- **US1 (Phase 3)**: Depends on Phase 2; all 9 notebook tasks [P] run in parallel
- **US2 (Phase 4)**: Depends on Phase 3 (notebooks must exist); all 9 [P] run in parallel
- **US3 (Phase 5)**: Depends on Phase 3 (ZIP column needed for ranking); all 9 [P] run in parallel
- **Polish (Phase 6)**: Depends on Phases 3, 4, 5 all complete

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2 — no dependency on other stories
- **US2 (P2)**: Starts after US1 (Section 1 must exist for Section 2 to reference column list)
- **US3 (P3)**: Can start after US1 in parallel with US2 (Section 4 only needs ZIP column from Section 1)

### Parallel Opportunities

- T007–T015 (US1): All 9 notebooks are independent files — fully parallel
- T016–T024 (US2): All 9 Section 2 additions are independent — fully parallel
- T025–T033 (US3): All 9 Section 4 additions are independent — fully parallel
- US2 and US3 phases can overlap once US1 is complete

---

## Parallel Example: User Story 1

```bash
# All 9 notebooks can be created simultaneously:
Task T007: eda_cdc_places.ipynb           (Section 1 + 3)
Task T008: eda_census_demographics.ipynb  (Section 1 + 3)
Task T009: eda_census_housing_poverty.ipynb
Task T010: eda_fema.ipynb
Task T011: eda_healthcare_access.ipynb
Task T012: eda_healthcare_workers.ipynb
Task T013: eda_parks.ipynb
Task T014: eda_social_vulnerability.ipynb
Task T015: eda_usda_food_access.ipynb

# Validate immediately after any single notebook:
pytest --nbmake notebooks/eda/eda_cdc_places.ipynb -v
```

---

## Implementation Strategy

### MVP First (User Story 1 Only — 13 tasks)

1. Complete Phase 1: Setup (T001–T004)
2. Complete Phase 2: Foundational (T005–T006)
3. Complete Phase 3: US1 notebooks (T007–T015)
4. **STOP and VALIDATE**: `pytest --nbmake notebooks/eda/ -v` — 9 notebooks pass
5. Any reviewer can inspect schema + distributions for any dataset

### Incremental Delivery

1. Setup + Foundational → test runner ready
2. US1 (T007–T015) → 9 runnable notebooks with schema + distributions
3. US2 (T016–T024) → quality flags + outlier tables added to all notebooks
4. US3 (T025–T033) → domain analysis charts added; all notebooks fully complete
5. Polish (T034–T038) → outputs cleared, linting clean, ready to present

---

## Notes

- All 9 notebook files in each story phase are tagged [P] — they are completely independent
- Section 2 tasks (T016–T024) depend on Section 1 existing but do NOT depend on each other
- Section 4 tasks (T025–T033) depend on Section 1 (for ZIP column) but NOT on Section 2
- US2 and US3 can therefore proceed in parallel once US1 is complete
- Data Quality Flags are observational only — do not add any `df.drop()` or pipeline prescription in notebook cells
- No Folium maps anywhere in EDA notebooks — bar charts only for geographic ranking
- Clear notebook outputs before every commit: `jupyter nbconvert --clear-output notebooks/eda/*.ipynb`
