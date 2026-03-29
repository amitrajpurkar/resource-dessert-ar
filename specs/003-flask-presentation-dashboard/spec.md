# Feature Specification: Flask Presentation Dashboard

**Feature Branch**: `003-flask-presentation-dashboard`
**Created**: 2026-03-28
**Status**: Draft
**Input**: User description: "Run the resource desert analysis notebook and save its output files and images. Create a simple web application using Flask with elegant stylesheets. Using the output files from the notebook, create a web app for presentation to judges and audience — showing the problem statement, how the analysis was done, observations from the data, and suggested recommendations."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Problem Statement Presentation (Priority: P1)

A judge or audience member opens the web app and immediately understands the problem being solved: what a Resource Desert is, why it matters to Jacksonville, and what the three key questions are. The landing page sets the stage before any data is shown.

**Why this priority**: Without context, the data and charts are meaningless. The narrative must lead. This is independently usable — a presenter can walk through just the problem statement and deliver value.

**Independent Test**: Navigate to the root URL. Confirm the page displays the Resource Desert problem statement, the three key questions, and the inequity cycle explanation without external material.

**Acceptance Scenarios**:

1. **Given** a visitor lands on the app, **When** the page loads, **Then** they see a headline with "Resource Desert", the three key questions numbered clearly, and the inequity cycle (Preventative Assets → Poor Outcomes).
2. **Given** the landing page is displayed, **When** a judge reads it, **Then** they can understand the problem without any prior context.

---

### User Story 2 — Data Analysis Walkthrough (Priority: P1)

A presenter walks the audience through how the analysis was conducted: the data sources, how the Desert Score is calculated, and which ZIP codes rank as most underserved — backed by the top-10 bar chart and an embedded interactive choropleth map.

**Why this priority**: Establishes credibility and method transparency. Core MVP — the data story cannot be told without this section.

**Independent Test**: Navigate to the Analysis section. Confirm the top-10 Desert Scores bar chart is displayed, the choropleth map is embedded and interactive, and the Desert Score formula is explained in plain language.

**Acceptance Scenarios**:

1. **Given** the Analysis section is displayed, **When** a presenter shows it, **Then** the bar chart of top-10 ZIP codes is visible with labelled scores.
2. **Given** the Analysis section is displayed, **When** a user interacts with the choropleth map, **Then** hovering over ZIP codes reveals their score.
3. **Given** the Analysis section is displayed, **When** the data sources table is read, **Then** all source datasets are listed with their origin agency.
4. **Given** the Analysis section is displayed, **When** the top-10 table is shown, **Then** it lists ZIP code, rank, Desert Score, top gap category, and poverty rate.

---

### User Story 3 — Health Outcome Observations (Priority: P2)

The audience sees how Resource Deserts translate to real health consequences — a scatter plot showing the correlation between preventative assets and poor health outcomes, with a plain-English interpretation of the strongest relationship found.

**Why this priority**: Answers Key Question 2 and makes the analysis emotionally resonant. Requires Analysis section (US2) complete for narrative flow.

**Independent Test**: Navigate to the Observations section. Confirm the health scatter plot is shown, the strongest correlation is called out in a highlighted stat block, and the direction of the relationship is described in plain English.

**Acceptance Scenarios**:

1. **Given** the Observations section is displayed, **When** shown, **Then** the scatter plot image is visible with a written summary of the strongest asset–outcome relationship.
2. **Given** the Observations section is displayed, **When** a judge reads it, **Then** they can identify which preventative asset has the strongest link to poor health outcomes without interpreting the chart.

---

### User Story 4 — AI Recommendations (Priority: P2)

The audience sees the single highest-impact intervention identified by the gap-closure simulation — which ZIP code, which resource type, and how much improvement is projected — alongside the full heatmap and a sortable table of all 20 simulated interventions.

**Why this priority**: Answers Key Question 3 and is the analytical payoff. Depends on Desert Score computation (US2) for context.

**Independent Test**: Navigate to the Recommendations section. Confirm a highlighted call-out card shows the top intervention, the heatmap image is displayed, and the full 20-row intervention table is visible.

**Acceptance Scenarios**:

1. **Given** the Recommendations section is displayed, **When** shown, **Then** the highest-impact intervention (ZIP, resource type, score improvement, population) appears in a visually prominent card.
2. **Given** the Recommendations section is displayed, **When** the heatmap is shown, **Then** the highest-impact cell is marked with a star visible in the image.
3. **Given** the Recommendations section is displayed, **When** the full table is read, **Then** all 20 intervention rows are shown sorted by impact descending.

---

### User Story 5 — Per-Category Drill-Down (Priority: P3)

A judge asks about a specific service category (e.g., food access). The presenter navigates to a drill-down section showing the category-specific supply gap chart across all Jacksonville ZIP codes.

**Why this priority**: Supports Q&A depth. Nice to have for interactive sessions — the core story is complete without it.

**Independent Test**: Navigate to the Category section. Confirm all four category bar charts (healthcare, food access, parks, insurance) are displayed with labels.

**Acceptance Scenarios**:

1. **Given** the Category section is displayed, **When** shown, **Then** all four category view charts are visible with category names as headers.
2. **Given** a category chart is displayed, **When** viewed, **Then** ZIP codes and supply gap scores are legible.

---

### Edge Cases

- What happens when a required output file (e.g., `desert_scores.csv`) is missing? The app MUST display a clear "Data not yet generated — please run the notebook first" message rather than an unhandled error page.
- What if the choropleth HTML file is too large to embed inline? It MUST be served via a direct `<iframe>` pointing to the static-served file, not inlined.
- What if the app is opened before the notebook has been run? Every section dependent on generated files must show a graceful fallback rather than a blank or broken page.
- What if a category PNG is missing? The category tile must show a placeholder with a descriptive label and the "Regenerate Data" button rather than a broken image.
- What if the user clicks "Regenerate Data" while a run is already in progress? The button MUST be disabled and show a spinner — a second concurrent execution must be blocked.
- What if notebook execution takes longer than 5 minutes? The status indicator must remain active; the app must not time out the background process.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The app MUST serve a single-page scrollable presentation divided into five clearly labelled sections: Problem Statement, Analysis, Observations, Recommendations, and Category Drill-Down.
- **FR-002**: The app MUST display all pre-generated PNG chart images from `reports/figures/` as static `<img>` elements — no in-browser chart rendering. The Folium choropleth HTML remains the sole interactive element.
- **FR-003**: The app MUST embed the choropleth HTML map (`reports/outputs/resource_desert_map.html`) as an interactive `<iframe>`.
- **FR-004**: The app MUST read `reports/outputs/desert_scores.csv` and display the top-10 most underserved ZIP codes in a styled HTML table.
- **FR-005**: The app MUST read `reports/outputs/intervention_recommendations.json` and display all 20 intervention rows in a table sorted by score improvement descending, with the highest-impact row visually highlighted.
- **FR-006**: The app MUST display a prominent call-out card showing the single highest-impact intervention (ZIP, resource type, score improvement percentage, population impacted).
- **FR-007**: The app MUST handle missing output files gracefully — showing a "Regenerate Data" button in place of each missing asset section.
- **FR-007a**: The app MUST provide a "Regenerate Data" button (visible in the nav bar or on the landing section) that triggers full notebook execution as a background process and displays a progress indicator while running.
- **FR-007b**: While notebook execution is in progress, the app MUST show a running status indicator and prevent duplicate runs. Once complete, all sections MUST refresh to display the newly generated outputs.
- **FR-007c**: If notebook execution fails, the app MUST display the error message returned by the notebook process so the presenter can diagnose and retry.
- **FR-008**: The app MUST use a consistent, elegant visual design with a dark navy and white base palette, accent colors drawn from the red-yellow-green Desert Score theme, and readable typography.
- **FR-009**: The app MUST be launchable with a single command (`python app.py` or `flask run`) from within the activated virtual environment.
- **FR-010**: A sticky top navigation bar with anchor links MUST allow jumping to any of the five sections within one click from anywhere on the page. The single page scrolls continuously — there are no separate URLs per section.

### Key Entities

- **DesertScore**: Represents one ZIP code's deprivation assessment — attributes: zip_code, desert_rank, desert_score (0–100), top_gap_category, total_population, poverty_rate.
- **Intervention**: Represents one simulated resource addition — attributes: zip_code, resource_type, current_desert_score, simulated_desert_score, score_improvement, pct_improvement, population_impacted, is_highest_impact.
- **ChartImage**: A static pre-rendered PNG — attributes: file_path, section, caption.
- **ChoroplethMap**: A standalone interactive HTML file served as an iframe — too large to inline; served from the static directory.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All five presentation sections load and display fully within 3 seconds on a local machine.
- **SC-002**: A first-time viewer can navigate the complete presentation narrative in under 5 minutes without instruction.
- **SC-003**: The highest-impact intervention is identifiable within 5 seconds of reaching the Recommendations section.
- **SC-004**: All 7 output assets (1 CSV, 1 JSON, 1 HTML map, 5 PNG charts) are surfaced in the app with zero manual configuration after the notebook has been run.
- **SC-005**: The app starts and serves all pages without error after a fresh `pip install -r requirements.txt` followed by notebook execution on a clean machine.
- **SC-006**: The presentation layout is readable on a 1280×800 laptop screen in full-screen browser mode without horizontal scrolling.

---

## Clarifications

### Session 2026-03-28

- Q: What is the presentation layout style — single-page scroll, multi-page routes, or tabbed? → A: Single scrollable page with a sticky top navigation bar and anchor links to each section. No separate URLs per section.
- Q: Should the app trigger notebook execution, or be display-only? → A: App provides a "Regenerate Data" button that triggers full notebook execution on demand, shows a progress indicator while running, prevents duplicate runs, and displays errors on failure.
- Q: Should charts be static PNGs or interactive in-browser renders? → A: All charts are static PNGs served from `reports/figures/`. The choropleth map remains the sole interactive element (via its Folium HTML iframe). No in-browser chart rendering.

---

## Assumptions

- The analysis notebook has been executed before the app is started — all files in `reports/outputs/` and `reports/figures/` are assumed present.
- The app runs on localhost for live presentation purposes — no internet deployment, user authentication, or multi-user access is required.
- The target display is a standard 1280×800 or larger presentation laptop in full-screen browser mode.
- Four category PNG charts are present: `category_healthcare_view.png`, `category_food_access_view.png`, `category_parks_view.png`, `category_insurance_view.png`.
- The app is read-only — no user input, form submission, or data modification is in scope.
- The Flask development server is acceptable for a datathon demo — production-grade deployment is out of scope.
- `flask` is added to `requirements.txt`; no separate installation step is needed beyond the existing setup instructions.
