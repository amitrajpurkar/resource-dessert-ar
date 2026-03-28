# Tasks: Resource Desert Analysis & Optimization

**Input**: Design documents from `/specs/001-resource-desert-analysis/`
**Branch**: `001-resource-desert-analysis`
**Prerequisites**: plan.md ✓ spec.md ✓ research.md ✓ data-model.md ✓ contracts/ ✓ quickstart.md ✓

**Tests**: Included — FR-015 mandates ≥70% line coverage as a hard completion gate.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1–US4)
- All file paths are relative to the repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the project skeleton, pin dependencies, and establish path/logging conventions before any pipeline code is written.

- [x] T001 Create output directories: `reports/figures/`, `reports/outputs/`, `data/processed/`, `notebooks/` (use `mkdir -p`)
- [x] T002 Create `requirements.txt` pinning: pandas≥2.0, numpy≥1.26, scikit-learn≥1.4, matplotlib≥3.8, seaborn≥0.13, folium≥0.15, geopandas≥0.14, jupyter≥1.0, openpyxl≥3.1, pytest≥8.0, pytest-cov≥4.1, ruff≥0.4, black≥24.0
- [x] T003 [P] Create `pytest.ini` registering the `e2e` marker: `markers = e2e: end-to-end tests that require data/raw/ to be populated`
- [x] T004 [P] Create `src/config.py` with `pathlib.Path` constants for every directory and raw data file path referenced in `contracts/pipeline-io-contracts.md`; add `get_logger(name: str) -> logging.Logger` helper
- [x] T005 Create `tests/conftest.py` with synthetic fixture DataFrames covering all 5 pipeline entities: `sample_census_df`, `sample_cdc_df`, `sample_usda_df`, `sample_healthcare_df`, `sample_parks_df`, `sample_merged_df`, `sample_desert_scores_df`
- [x] T006 [P] Inspect `data/raw/Metadata.xlsx` and populate `specs/001-resource-desert-analysis/column-reference.md` with the exact column names needed from each of the 9 raw datasets (ZIP column name, demand metrics, supply metrics)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create typed module stubs and test scaffolding. No user story can start until `src/config.py` and all stubs exist.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T007 Create stub files `src/ingestion.py`, `src/cleaning.py`, `src/features.py`, `src/models.py`, `src/visualization.py` — each with all public function signatures, full type hints, Google-style docstrings, and `raise NotImplementedError` bodies. Use exact signatures from `contracts/pipeline-io-contracts.md`.
- [x] T008 [P] Create `tests/__init__.py`, `tests/e2e/__init__.py` (empty); verify `pytest tests/ -v -m "not e2e"` collects tests without errors (0 passed, 0 errors is acceptable at this stage)

**Checkpoint**: Foundation ready — user story implementation can begin.

---

## Phase 3: User Story 1 — Identify Resource Desert Neighborhoods (Priority: P1) 🎯 MVP

**Goal**: Every Jacksonville ZIP receives a Desert Score; top-10 most underserved ZIPs appear on a choropleth map and bar chart.

**Independent Test**: Load `reports/outputs/desert_scores.csv` — confirm it has ≥1 row, a `desert_score` column in [0,100], and a `desert_rank` column starting at 1. Open `reports/outputs/resource_desert_map.html` in a browser and confirm the map renders with a coloured legend.

### Tests for User Story 1 ⚠️ Write first — confirm they FAIL before implementing

- [x] T009 [P] [US1] Write failing unit tests for `load_raw_datasets()` in `tests/test_ingestion.py`: assert correct dict keys returned, each value is a DataFrame with ≥1 row, `FileNotFoundError` raised when a path is missing (use tmp_path fixture)
- [x] T010 [P] [US1] Write failing unit tests for `clean_datasets()` in `tests/test_cleaning.py`: assert `zip_code` is str 5-char zero-padded, no duplicate zip_codes per dataset, rate columns clipped to [0,1], row-drop count is logged
- [x] T011 [P] [US1] Write failing unit tests for `merge_datasets()` and `compute_desert_score()` in `tests/test_features.py`: assert merged df has no duplicate zip_codes, `desert_score` in [0,100], `desert_rank` starts at 1, ZIPs with population=0 absent

### Implementation for User Story 1

- [x] T012 [US1] Implement `load_raw_datasets(config: ModuleType) -> Dict[str, pd.DataFrame]` in `src/ingestion.py`: load all 9 CSVs + `Metadata.xlsx` via `pathlib.Path`; log shape/dtypes; raise `FileNotFoundError` with descriptive message for any missing file; return raw unmodified DataFrames
- [x] T013 [US1] Implement `clean_datasets(raw: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]` in `src/cleaning.py`: standardize ZIP column to `zip_code` (str, 5-char, zero-padded) across all datasets; fix dtypes; clip rate/proportion columns to [0.0, 1.0]; drop duplicates; log before/after record counts and reasons for every drop
- [x] T014 [US1] Implement `merge_datasets(cleaned: Dict[str, pd.DataFrame]) -> pd.DataFrame` in `src/features.py`: outer-join all datasets on `zip_code`; filter to Duval County ZIPs; log and exclude ZIPs with `population == 0`; impute null supply metrics with column median (log imputation count); save to `data/processed/merged_jacksonville.csv`
- [x] T015 [US1] Implement `compute_desert_score(merged_df: pd.DataFrame) -> pd.DataFrame` in `src/features.py`: compute `demand_factor = normalize(poverty_rate × disease_burden_composite)`; compute `supply_gap_*` for each of 4 asset types; compute `desert_score = normalize(Σ supply_gap_i × demand_factor) × 100`; add `desert_rank` (ties broken by `poverty_rate` desc); save to `reports/outputs/desert_scores.csv`
- [x] T016 [P] [US1] Implement `plot_desert_scores_bar_chart(desert_scores_df: pd.DataFrame, figures_dir: Path) -> None` in `src/visualization.py`: horizontal bar chart of top-10 ZIPs by Desert Score; descriptive title; labelled axes with units; saved to `reports/figures/desert_scores_bar_chart.png` at ≥150 DPI
- [x] T017 [US1] Implement `create_choropleth_map(desert_scores_df: pd.DataFrame, geojson_path: Path, outputs_dir: Path) -> None` in `src/visualization.py`: Folium choropleth keyed on `ZCTA5CE20`; `RdYlGn_r` palette; tooltip showing zip, score, top gap category; saved as standalone HTML to `reports/outputs/resource_desert_map.html`

**Checkpoint**: US1 complete — `desert_scores.csv` written, map HTML opens in browser, bar chart saved.

---

## Phase 4: User Story 2 — Impact of Resource Deserts on Health Outcomes (Priority: P2)

**Goal**: At least one quantified relationship between a preventative asset metric and a health outcome metric, visualised with effect direction stated explicitly.

**Independent Test**: Open `reports/figures/preventative_asset_vs_health_outcome.png` — confirm it shows a scatter plot with a labelled regression line, named axes with units, and at least 2 extreme ZIP codes annotated.

### Tests for User Story 2 ⚠️ Write first — confirm they FAIL before implementing

- [ ] T018 [P] [US2] Write failing unit tests for `compute_health_outcome_correlation()` in `tests/test_features.py`: assert returns a dict/DataFrame of Pearson r values, all values in [-1, 1], at least one asset-outcome pair present

### Implementation for User Story 2

- [ ] T019 [US2] Implement `compute_health_outcome_correlation(merged_df: pd.DataFrame) -> pd.DataFrame` in `src/features.py`: compute Pearson correlation between each of the 4 preventative asset metrics and each health outcome metric (mental health distress rate, diabetes prevalence); return correlation matrix; log strongest association
- [ ] T020 [US2] Implement `plot_preventative_vs_outcome(merged_df: pd.DataFrame, asset_col: str, outcome_col: str, figures_dir: Path) -> None` in `src/visualization.py`: scatter plot with seaborn `regplot`; axis labels include metric name + units; top-3 and bottom-3 ZIPs annotated by zip_code; saved to `reports/figures/preventative_asset_vs_health_outcome.png` at ≥150 DPI

**Checkpoint**: US2 complete — correlation chart saved with regression line and annotated extremes.

---

## Phase 5: User Story 3 — AI-Driven Gap-Closure Optimization (Priority: P3)

**Goal**: Gap-closure simulation identifies the single highest-impact intervention across top-5 underserved ZIPs; result is human-readable.

**Independent Test**: Load `reports/outputs/intervention_recommendations.json` — confirm 20 rows (5 ZIPs × 4 resource types), exactly one row has `is_highest_impact == true`, all `score_improvement` values ≥ 0.

### Tests for User Story 3 ⚠️ Write first — confirm they FAIL before implementing

- [ ] T021 [P] [US3] Write failing unit tests for `run_gap_closure_simulation()` and `rank_interventions()` in `tests/test_models.py`: assert output has `top_n × 4` rows, exactly 1 row with `is_highest_impact=True`, `score_improvement` ≥ 0 for all rows, `pct_improvement` in [0, 100]

### Implementation for User Story 3

- [ ] T022 [US3] Implement `run_gap_closure_simulation(desert_scores_df: pd.DataFrame, merged_df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame` in `src/models.py`: for each of the top-N ZIPs × 4 resource types, set the supply metric to the 75th percentile of that column, recompute the desert score, return interventions_df with `current_desert_score`, `simulated_desert_score`, `score_improvement`, `pct_improvement`, `population_impacted`
- [ ] T023 [US3] Implement `rank_interventions(interventions_df: pd.DataFrame) -> pd.DataFrame` in `src/models.py`: sort by `score_improvement` descending; set `is_highest_impact = True` on the single top row; write to `reports/outputs/intervention_recommendations.json`
- [ ] T024 [US3] Implement `plot_intervention_impact_heatmap(interventions_df: pd.DataFrame, figures_dir: Path) -> None` in `src/visualization.py`: seaborn heatmap with ZIPs on y-axis, resource types on x-axis, `pct_improvement` as values; highest-impact cell annotated with star; saved to `reports/figures/intervention_impact_heatmap.png` at ≥150 DPI

**Checkpoint**: US3 complete — simulation JSON written, heatmap saved, highest-impact intervention identifiable in <2 minutes.

---

## Phase 6: User Story 4 — Explore Data by Service Category (Priority: P4)

**Goal**: Any single service category (healthcare, food, parks, insurance) can be isolated and visualised independently.

**Independent Test**: Call `filter_by_service_category(desert_scores_df, "food_access")` — confirm the returned DataFrame contains only food-access supply gap columns and a re-ranked `desert_rank`. Confirm a category bar chart PNG is saved to `reports/figures/`.

### Implementation for User Story 4

- [ ] T025 [P] [US4] Implement `filter_by_service_category(desert_scores_df: pd.DataFrame, category: str) -> pd.DataFrame` in `src/features.py`: accepts `"healthcare"`, `"food_access"`, `"parks"`, `"insurance"`; returns df filtered to relevant supply gap column + demand columns; re-ranks ZIPs by that single gap column
- [ ] T026 [US4] Implement `plot_category_view(category_df: pd.DataFrame, category: str, figures_dir: Path) -> None` in `src/visualization.py`: horizontal bar chart showing supply gap + poverty rate for all ZIPs in the category view; saved to `reports/figures/category_{category}_view.png` at ≥150 DPI

**Checkpoint**: All 4 user stories independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end notebook, e2e test, coverage gate, linting pass, notebook cleanup.

- [ ] T027 [P] Write failing unit tests for visualization functions in `tests/test_visualization.py`: mock `matplotlib.pyplot.savefig` and `folium.Map.save`; assert each plot function calls save with a path in `reports/figures/` or `reports/outputs/`; assert figures have titles and axis labels
- [ ] T028 Create `notebooks/resource_desert_analysis.ipynb`: end-to-end notebook with markdown narrative cells; orchestrate all 5 pipeline stages in order; display top-10 Desert Scores table, embedded choropleth map, correlation chart, intervention recommendations summary
- [ ] T029 Write `tests/e2e/test_pipeline_e2e.py` tagged `@pytest.mark.e2e`: run full pipeline on `data/raw/`; assert `reports/outputs/desert_scores.csv` exists with expected columns; assert `reports/outputs/intervention_recommendations.json` exists with 20 rows; assert `reports/outputs/resource_desert_map.html` is a non-empty file
- [ ] T030 [P] Run `ruff check src/ tests/` and fix all violations — zero errors required (FR-010)
- [ ] T031 [P] Run `black src/ tests/` to auto-format — zero formatting violations required (FR-010)
- [ ] T032 Run `pytest tests/ -v -m "not e2e"` and confirm all unit tests pass (FR-015 gate 3)
- [ ] T033 Run `pytest tests/ --cov=src --cov-fail-under=70 --cov-report=term-missing` and confirm coverage ≥ 70% (FR-015 hard gate)
- [ ] T034 Clear all cell outputs in `notebooks/resource_desert_analysis.ipynb` before final commit (`jupyter nbconvert --ClearOutputPreprocessor.enabled=True`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Requires Phase 1 — BLOCKS all user stories
- **US1 (Phase 3)**: Requires Phase 2 — core blocking story; US2/US3/US4 depend on its merged_df
- **US2 (Phase 4)**: Requires Phase 2 + T014 (merged_df) from US1
- **US3 (Phase 5)**: Requires Phase 2 + T015 (desert_scores_df) from US1
- **US4 (Phase 6)**: Requires Phase 2 + T015 (desert_scores_df) from US1
- **Polish (Phase 7)**: Requires all desired user stories complete

### User Story Dependencies

- **US1 (P1)**: Independent after Phase 2 — no dependency on other stories
- **US2 (P2)**: Depends on `merged_df` from US1 T014 (merge step only, not full US1)
- **US3 (P3)**: Depends on `desert_scores_df` from US1 T015
- **US4 (P4)**: Depends on `desert_scores_df` from US1 T015

### Within Each User Story

- Unit tests MUST be written first and confirmed to FAIL before implementation starts
- Module stubs (T007) before any implementation tasks
- `src/config.py` (T004) before any module that imports paths
- `merge_datasets()` (T014) before `compute_desert_score()` (T015)
- `compute_desert_score()` (T015) before `create_choropleth_map()` (T017)

### Parallel Opportunities

- T003, T004, T006 — all Phase 1 setup can run in parallel
- T009, T010, T011 — all US1 test files can be written in parallel
- T016, T017 — visualization functions use different output paths
- T018, T021 — tests for US2 and US3 can be written in parallel after T014/T015
- T030, T031 — ruff and black are independent

---

## Parallel Example: User Story 1

```bash
# Write all US1 test files together (after T007, T008):
Task T009: "Write failing unit tests for load_raw_datasets() in tests/test_ingestion.py"
Task T010: "Write failing unit tests for clean_datasets() in tests/test_cleaning.py"
Task T011: "Write failing unit tests for merge_datasets() and compute_desert_score() in tests/test_features.py"

# After T013 and T014 complete, these visualization tasks can run in parallel:
Task T016: "Implement plot_desert_scores_bar_chart() in src/visualization.py"
Task T017: "Implement create_choropleth_map() in src/visualization.py"
```

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T006)
2. Complete Phase 2: Foundational (T007–T008) — **blocks everything**
3. Write tests T009–T011, confirm FAIL
4. Implement T012–T017
5. **STOP and VALIDATE**: `desert_scores.csv` written + map HTML renders
6. Demo to judges — this alone answers Key Question #1

### Incremental Delivery

1. Setup + Foundational → skeleton ready
2. US1 → scores + map → MVP demo
3. US2 → correlation chart → answers Key Question #2
4. US3 → simulation + recommendations → answers Key Question #3
5. US4 → per-category drill-down → Q&A support
6. Polish → coverage gate + linting + notebook

---

## Notes

- `[P]` tasks operate on different files with no incomplete dependencies
- `[USn]` label maps each task to a specific user story for traceability
- `data/raw/` files are read-only — never appear in git diff (Gate G5)
- `jacksonville_zctas.geojson` still needed in `data/raw/` before T017 and T029 can run
- Each story is independently completable and testable — demo after each phase
- Commit after each logical group using prefix `[case1]`
