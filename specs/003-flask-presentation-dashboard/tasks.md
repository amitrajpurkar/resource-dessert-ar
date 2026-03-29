# Tasks: Flask Presentation Dashboard

**Input**: Design documents from `/specs/003-flask-presentation-dashboard/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Organization**: Tasks are grouped by user story. US1 and US2 are P1 (MVP). US3 and US4 are P2. US5 is P3.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story this task belongs to (US1–US5)

---

## Phase 1: Setup

**Purpose**: Directory structure, dependencies, and path constant verification.

- [X] T001 Verify `REPORTS_FIGURES_DIR` and `REPORTS_OUTPUTS_DIR` exist in `src/config.py`; add both if missing, using `pathlib.Path` and the existing path-definition pattern
- [X] T002 [P] Create `webapp/` directory tree: `webapp/templates/`, `webapp/static/css/`, `webapp/static/js/`
- [X] T003 [P] Add `flask>=3.0` to `requirements.txt`; run `pip install flask` to verify it resolves

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Flask app wiring, data loaders, background runner, file-serving routes, CSS/JS base, and route tests. Must be complete before any section content is added.

**⚠️ CRITICAL**: No user story section work can begin until this phase is complete.

- [X] T004 Create `app.py`: Flask instance, `logging` setup, import `cfg` from `src/config.py`, module-level `_run_state = {"status": "idle", "message": ""}` dict and `_lock = threading.Lock()`
- [X] T005 Add `_run_notebook_thread()` function to `app.py` — runs `subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", "--ExecutePreprocessor.kernel_name=prob1-resource-desert", "--ExecutePreprocessor.timeout=600", "notebooks/resource_desert_analysis.ipynb"], ...)` and updates `_run_state` under `_lock` on completion or error
- [X] T006 Add `load_desert_scores()`, `load_interventions()`, and `build_chart_list()` helper functions to `app.py` — each returns an empty list/None gracefully when its source file is missing; `load_desert_scores` reads top-10 rows from `cfg.REPORTS_OUTPUTS_DIR / "desert_scores.csv"`; `load_interventions` reads all 20 rows from `cfg.REPORTS_OUTPUTS_DIR / "intervention_recommendations.json"` sorted by `score_improvement` descending; `build_chart_list` returns the 7 known `ChartImage` dicts with `missing` flags checked against `cfg.REPORTS_FIGURES_DIR`
- [X] T007 Add `GET /figures/<filename>` route (returns `send_from_directory(cfg.REPORTS_FIGURES_DIR, filename)`) and `GET /map` route (returns `send_from_directory(cfg.REPORTS_OUTPUTS_DIR, "resource_desert_map.html")`) to `app.py`
- [X] T008 Add `POST /api/regenerate` route (spawns thread if `status != "running"`, returns 202 or 409 JSON) and `GET /api/regenerate/status` route (returns lock-protected `_run_state` as JSON) to `app.py`
- [X] T009 [P] Create `webapp/static/css/style.css` with CSS custom properties (`--color-navy: #0d1b2a`, `--color-accent-red: #d73027`, `--color-accent-green: #1a9850`, `--color-highlight: #ffe066`), CSS reset, sticky top nav bar layout, and five-section scroll scaffold
- [X] T010 [P] Create `webapp/static/js/app.js` with `pollStatus()` function using `fetch('/api/regenerate/status')` and recursive `setTimeout(pollStatus, 2000)` — updates a `#run-status` element; stops polling when status is `complete` or `error`
- [X] T011 Create `tests/test_app.py` with a `client` pytest fixture (`app.config["TESTING"] = True; yield app.test_client()`) and tests for: `GET /figures/<missing>` returns 404, `GET /map` returns 200 or 404, `POST /api/regenerate` returns 202 JSON with `{"status":"running"}`, duplicate `POST /api/regenerate` while running returns 409, `GET /api/regenerate/status` returns JSON with `status` key

**Checkpoint**: Flask app starts with `python app.py`; all API routes respond correctly; unit tests pass.

---

## Phase 3: User Story 1 — Problem Statement (Priority: P1) 🎯 MVP

**Goal**: Landing page delivers the Resource Desert problem context — definition, three key questions, inequity cycle — before any data is shown.

**Independent Test**: `GET /` returns 200 with "Resource Desert" heading, three numbered key questions, and inequity cycle text. No generated files required.

- [X] T012 [US1] Implement `index()` route handler in `app.py` — calls `load_desert_scores()`, `load_interventions()`, `build_chart_list()`, reads `map_exists` flag, reads `_run_state` under lock; renders `index.html` with all 7 template variables: `desert_scores`, `interventions`, `best_intervention`, `charts`, `map_exists`, `run_status`, `run_message`
- [X] T013 [US1] Create `webapp/templates/index.html` — HTML5 boilerplate with `<link>` to `style.css` and `<script>` to `app.js`; sticky `<nav>` with anchor links to `#problem`, `#analysis`, `#observations`, `#recommendations`, `#categories` and a "Regenerate Data" `<button id="regen-btn">`; `#problem` section with Resource Desert headline, three key questions numbered list, and inequity cycle paragraph (`Preventative Assets → Poor Health Outcomes`)
- [X] T014 [US1] Add Problem Statement section styles and nav bar styles to `webapp/static/css/style.css` — navy background for nav, white text, anchor link hover state, `#problem` section hero layout with dark navy background
- [X] T015 [US1] Add `GET /` tests to `tests/test_app.py` — assert 200 status, `b"Resource Desert"` in response data, three key questions text present in HTML

**Checkpoint**: `GET /` loads and shows the complete problem statement. Story 1 passes its independent test.

---

## Phase 4: User Story 2 — Data Analysis Walkthrough (Priority: P1)

**Goal**: Analysis section shows data sources, Desert Score formula, top-10 ZIP table, bar chart, and choropleth map.

**Independent Test**: Analysis section contains a `<table>` with 10 rows (or a missing-data placeholder), a `<img src="/figures/desert_scores_bar_chart.png">` element, and an `<iframe src="/map">`.

- [X] T016 [US2] Add `#analysis` section to `webapp/templates/index.html` — data sources table (10 rows, source agency column), Desert Score formula block in plain English, `{% if desert_scores %}` top-10 ZIP table (columns: rank, ZIP, score, top gap, population, poverty rate) `{% else %}` placeholder, `<img src="/figures/desert_scores_bar_chart.png">` bar chart, `{% if map_exists %}<iframe src="/map" ...>{% else %}` map placeholder
- [X] T017 [US2] Add Analysis section CSS to `webapp/static/css/style.css` — section heading style, data table (alternating row colours, header navy background), `<img>` max-width 100%, iframe container with fixed height (500px) and full width
- [X] T018 [US2] Add Analysis section tests to `tests/test_app.py` — assert `b"desert_scores_bar_chart"` in response, assert `b"/map"` in response (iframe src), mock `load_desert_scores` to return 10 rows and assert 10 `<tr>` elements in table

**Checkpoint**: Analysis section fully renders with all four elements. Stories 1 and 2 pass independently.

---

## Phase 5: User Story 3 — Health Outcome Observations (Priority: P2)

**Goal**: Observations section shows the scatter plot and a plain-English interpretation of the strongest preventative asset–outcome correlation.

**Independent Test**: Observations section contains `<img src="/figures/preventative_asset_vs_health_outcome.png">` and a highlighted stat block naming the strongest relationship.

- [X] T019 [US3] Add `#observations` section to `webapp/templates/index.html` — section heading, `<img src="/figures/preventative_asset_vs_health_outcome.png">` (or missing placeholder), stat block naming strongest correlation (hardcoded from analysis findings: primary care access vs poor mental health), plain-English narrative paragraph
- [X] T020 [P] [US3] Add Observations section CSS to `webapp/static/css/style.css` — stat block callout style (border-left accent, padded, contrasting background), narrative paragraph typography

**Checkpoint**: Observations section renders with chart and stat block. Story 3 passes independently.

---

## Phase 6: User Story 4 — AI Recommendations (Priority: P2)

**Goal**: Recommendations section surfaces the highest-impact intervention card, heatmap, and full 20-row sorted table.

**Independent Test**: Recommendations section contains a highlighted call-out card with ZIP code and resource type from `best_intervention`, a heatmap `<img>`, and a table with 20 rows.

- [X] T021 [US4] Add `#recommendations` section to `webapp/templates/index.html` — `{% if best_intervention %}` call-out card (`<div class="highlight-card">`) showing ZIP, resource type, score improvement, pct_improvement, and population_impacted; `<img src="/figures/intervention_impact_heatmap.png">` heatmap (or placeholder); `{% if interventions %}` table (20 rows, all 8 columns, row with `is_highest_impact` gets CSS class `best-row`) sorted by score_improvement descending
- [X] T022 [P] [US4] Add Recommendations section CSS to `webapp/static/css/style.css` — `.highlight-card` background `var(--color-highlight)`, bold ZIP and resource type, `.best-row` table row highlight
- [X] T023 [US4] Add Recommendations section tests to `tests/test_app.py` — mock `load_interventions` to return 20 rows with one `is_highest_impact: true`; assert call-out card present, 20 table rows rendered, `best-row` CSS class present exactly once

**Checkpoint**: Recommendations section fully renders. Stories 1–4 all pass independently.

---

## Phase 7: User Story 5 — Per-Category Drill-Down (Priority: P3)

**Goal**: Category section shows all four category-specific supply gap bar charts with labelled headers.

**Independent Test**: Category section contains four `<img>` elements, one per category (healthcare, food_access, parks, insurance), each preceded by a category name heading.

- [X] T024 [US5] Add `#categories` section to `webapp/templates/index.html` — four subsections each with a `<h3>` category name heading and `<img src="/figures/category_<name>_view.png">` (or missing placeholder per `chart.missing` flag); categories: Healthcare, Food Access, Parks, Insurance
- [X] T025 [P] [US5] Add Category Drill-Down CSS to `webapp/static/css/style.css` — two-column chart grid on ≥1280px, single column on smaller viewports; category heading style

**Checkpoint**: All five stories render correctly end-to-end.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Missing-file fallback UI, Regenerate button wiring, error banner, linting, and final test run.

- [X] T026 Add missing-file fallback `<div class="placeholder">` blocks to `webapp/templates/index.html` for all chart images (`{% if chart.missing %}<div class="placeholder">{{ chart.caption }} — data not yet generated</div>{% else %}<img ...>{% endif %}`); add no-data placeholders for empty `desert_scores` and `interventions` lists
- [X] T027 [P] Add `.placeholder` (dashed border, centred muted text, min-height 200px), `.error-banner` (red background, white text, `run_message` display), and `.spinner` (CSS animation) styles to `webapp/static/css/style.css`
- [X] T028 Wire Regenerate button in `webapp/static/js/app.js` — on `#regen-btn` click: disable button, add `.spinner` class, `POST /api/regenerate`, start `pollStatus()` loop; on `complete`: reload page; on `error`: show `#error-banner` with message, re-enable button
- [X] T029 [P] Run `ruff check app.py` and `black --check app.py`; fix all issues
- [X] T030 Run `pytest tests/test_app.py -v`; confirm all tests pass and report coverage

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion; **blocks all user story phases**
- **US1 (Phase 3)**: Depends on Phase 2 (index route + template scaffold)
- **US2 (Phase 4)**: Depends on Phase 3 (template must exist to extend)
- **US3 (Phase 5)**: Depends on Phase 4 (sequential section additions to template)
- **US4 (Phase 6)**: Depends on Phase 5
- **US5 (Phase 7)**: Depends on Phase 6
- **Polish (Phase 8)**: Depends on Phase 7

### Within Each Phase

- Tasks modifying the same file (`index.html`, `app.py`, `style.css`, `test_app.py`) run sequentially
- Tasks touching different files (CSS vs JS, or separate route groups) are marked `[P]`

### Parallel Opportunities

Within Phase 2: T009 (CSS) and T010 (JS) are independent of T004–T008 once T002 (dirs) is done.
Within Phase 5: T019 and T020 touch different files.
Within Phase 6: T021 and T022 touch different files.
Within Phase 7: T024 and T025 touch different files.
Within Phase 8: T027 (CSS), T029 (lint) are independent of T026/T028/T030.

---

## Parallel Example: Phase 2 Foundational

```bash
# After T001–T003 complete, these can start in parallel:
Task T009: Create webapp/static/css/style.css base
Task T010: Create webapp/static/js/app.js polling logic

# T004 → T005 → T006 → T007 → T008 are sequential (same file: app.py)
# T011 (tests) can start after T007/T008 define the routes
```

---

## Implementation Strategy

### MVP (Stories 1–2 only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational — **MUST finish before any section work**
3. Complete Phase 3: US1 (Problem Statement)
4. Complete Phase 4: US2 (Analysis)
5. **STOP and VALIDATE**: `python app.py` → browser at `http://127.0.0.1:5000`; confirm top-10 table, bar chart, and choropleth map all render
6. Demo-ready at this point

### Full Delivery

1. MVP above (Phases 1–4)
2. Phase 5: US3 (Observations)
3. Phase 6: US4 (Recommendations)
4. Phase 7: US5 (Category Drill-Down)
5. Phase 8: Polish + linting + tests

---

## Notes

- All section content is added incrementally to the **same `index.html`** — never overwrite earlier sections
- `src/config.py` path constants are **read-only** — do not change existing definitions
- The `_run_state` dict in `app.py` is the **only** module-level mutable state; all access must be inside `_lock`
- `send_from_directory` requires absolute directory paths — always use `cfg.REPORTS_FIGURES_DIR` (a `pathlib.Path`), not a relative string
- Notebook kernel name `prob1-resource-desert` is hardcoded in the subprocess call — matches the registered venv kernel
