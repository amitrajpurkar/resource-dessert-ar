# Feature Specification: Resource Desert Analysis & Optimization for Jacksonville

**Feature Branch**: `001-resource-desert-analysis`
**Created**: 2026-03-28
**Status**: Draft
**Input**: User description: "@raw_specs.md"

## Clarifications

### Session 2026-03-28

- Q: How should the Resource Desert Score components be weighted? → A: Demand-weighted composite — supply gap metrics multiplied by a demand factor (poverty rate + disease burden), so a missing resource counts more in a community with higher need.
- Q: What is the primary prototype output format? → A: Jupyter notebook with embedded Folium choropleth map exported as a standalone HTML file.
- Q: What method should the AI/optimization component use? → A: Gap-closure simulation — for the top-N underserved ZIPs, simulate adding each resource type and show the projected Desert Score improvement per intervention.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Identify Resource Desert Neighborhoods (Priority: P1)

A datathon judge or civic stakeholder opens the prototype and can immediately see a map or dashboard showing which Jacksonville ZIP codes qualify as "Resource Deserts." They can see which specific services are most mismatched relative to community need (e.g., a high-poverty ZIP with no primary care providers or food access within reasonable distance).

**Why this priority**: This is the core deliverable. Without identifying where the deserts are, no other analysis or solution is possible.

**Independent Test**: Can be fully tested by loading the dashboard/map and verifying that at least one ZIP code is flagged as a resource desert with supporting demand vs. supply evidence.

**Acceptance Scenarios**:

1. **Given** the cleaned and merged dataset, **When** the resource desert scoring logic is applied, **Then** each Jacksonville ZIP code receives a composite "Desert Score" ranked from highest to lowest deprivation.
2. **Given** the ranked list, **When** a judge views the top 5 most underserved ZIPs, **Then** they can see both demand indicators (poverty rate, disease burden) and supply indicators (provider count, park access, food access) that explain the score.
3. **Given** a ZIP code with no grocery store within 1 mile and >30% poverty rate, **When** evaluated, **Then** it is classified as a food desert and flagged on the map.

---

### User Story 2 - Show Impact of Resource Deserts on Health Outcomes (Priority: P2)

A judge reviewing the presentation wants to understand *why* resource deserts matter — not just that they exist. The analysis shows a quantified relationship between the absence of preventative assets (parks, primary care, healthy food) and poor health outcomes (mental health burden, chronic disease rates).

**Why this priority**: Demonstrates the causal chain that motivates the intervention. Required to answer Key Question #2.

**Independent Test**: Can be fully tested by viewing a correlation chart or comparative analysis linking preventative asset scores to CDC health outcome metrics by ZIP code.

**Acceptance Scenarios**:

1. **Given** the merged CDC PLACES and resource supply data, **When** a correlation analysis is run, **Then** at least one meaningful relationship is shown between a preventative asset metric and a health outcome metric (e.g., park access vs. mental health distress rate).
2. **Given** the analysis results, **When** visualized, **Then** the chart clearly labels axes (metric name + units) and identifies the ZIP codes at the extremes.
3. **Given** ZIPs with the lowest preventative asset scores, **When** compared to ZIPs with the highest scores, **Then** the difference in poor health outcome rates is quantified (e.g., "ZIPs with no park access have 2× the rate of frequent mental distress").

---

### User Story 3 - Propose an AI-Driven Optimization Solution (Priority: P3)

A judge wants to see a concrete, data-backed proposal for how AI can be used to direct resources to the most underserved communities. The prototype demonstrates what would improve if a specific intervention (e.g., mobile clinic placement, food access point) were implemented in the highest-need ZIP code.

**Why this priority**: Answers Key Question #3 and is the "Inventor Phase" deliverable — what makes this a datathon prototype vs. just an analysis.

**Independent Test**: Can be fully tested by viewing a recommendation output that names a specific Jacksonville ZIP code, proposes a specific intervention type, and quantifies the projected improvement in one measurable metric.

**Acceptance Scenarios**:

1. **Given** the resource desert scores and health outcome data, **When** the optimization model is run, **Then** it identifies the ZIP code with the highest combined need and lowest current supply as the primary intervention target.
2. **Given** the target ZIP, **When** a proposed intervention is evaluated (e.g., adding a primary care access point), **Then** the prototype shows the estimated change in the Desert Score and at least one health outcome proxy metric.
3. **Given** the proposal output, **When** presented to a non-technical audience, **Then** a judge can understand the recommended action, the community it serves, and the projected benefit without any technical background.

---

### User Story 4 - Explore Data by Service Category (Priority: P4)

A user wants to drill into a specific service type (healthcare access, food access, parks, or social vulnerability) to understand the landscape across all Jacksonville ZIPs for that dimension independently.

**Why this priority**: Supports deeper interrogation during Q&A and informs root cause explanation.

**Independent Test**: Can be fully tested by selecting one service category and confirming that output updates to show only that dimension's supply/demand gap.

**Acceptance Scenarios**:

1. **Given** the dashboard or notebook, **When** a specific service category is selected (e.g., "Food Access"), **Then** a ranked list or map updates to show all ZIPs colored by food access deprivation score only.
2. **Given** the food access view, **When** a specific ZIP is highlighted, **Then** its USDA food desert classification, nearest grocery distance, and poverty rate are displayed together.

---

### Edge Cases

- What happens when a ZIP code has no population data (e.g., commercial-only zones)? → Exclude from scoring and log the exclusion with count and reason.
- How does the system handle ZIPs present in some datasets but not others? → Use the intersection of ZIPs present across all datasets; missing values documented per source.
- What if two ZIPs have identical Desert Scores? → Rank by secondary criterion: highest poverty rate breaks ties.
- How are rural vs. urban ZIPs handled given Jacksonville's large geographic footprint? → Flag population density as a co-variable; do not penalize rural ZIPs for distance alone without considering vehicle access rates.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST compute a composite "Resource Desert Score" per Jacksonville ZIP code using a demand-weighted method: each supply gap metric (healthcare provider density, food access classification, park access, insurance coverage) is multiplied by a demand factor derived from poverty rate and CDC disease burden, then summed and normalized to a 0–100 scale.
- **FR-002**: The system MUST rank all Jacksonville ZIPs by Desert Score and display the top 10 most underserved.
- **FR-003**: The system MUST produce at least one visualization showing a quantified relationship between preventative asset availability and a health outcome metric.
- **FR-004**: The system MUST simulate adding each resource type (primary care, food access, park, insurance outreach) to the top-5 underserved ZIPs and output the projected Desert Score change per intervention, identifying the single highest-impact action.
- **FR-005**: All data transformations MUST be logged with before/after record counts; no rows may be dropped silently.
- **FR-006**: The system MUST write Desert Scores and intervention recommendations to `reports/outputs/`.
- **FR-007**: All figures MUST be saved to `reports/figures/` at ≥150 DPI with descriptive filenames.
- **FR-008**: The pipeline MUST be runnable end-to-end from raw data to final outputs with a single command.
- **FR-009**: The prototype MUST be delivered as a Jupyter notebook. The choropleth map of Desert Scores MUST additionally be exported as a standalone HTML file to `reports/outputs/`.

### Key Entities

- **ZIP Code Area**: Primary unit of analysis. Attributes: ZIP code, population, geographic area, poverty rate, urban/rural classification.
- **Preventative Asset**: A service or resource that reduces long-term health risk. Types: primary care provider, park, healthy food retailer, health insurance coverage.
- **Health Outcome Metric**: A measurable population health indicator from CDC PLACES (e.g., mental health distress rate, chronic disease prevalence).
- **Resource Desert Score**: A demand-weighted composite index per ZIP. Each supply gap metric is multiplied by a demand factor (poverty rate × disease burden), summed, and normalized to 0–100. Higher score = more underserved.
- **Intervention Proposal**: Output of the gap-closure simulation. Attributes: target ZIP, resource type simulated, current Desert Score, projected Desert Score after intervention, estimated population impacted, and percentage improvement.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every Jacksonville ZIP code present in the dataset receives a Resource Desert Score; no ZIPs are unscored without documented justification.
- **SC-002**: The top 10 most underserved ZIP codes are identifiable within 30 seconds of viewing the choropleth map or notebook output.
- **SC-003**: At least one meaningful association is demonstrated between a preventative asset metric and a health outcome metric, with an effect size or direction stated explicitly.
- **SC-004**: The gap-closure simulation produces a ranked intervention table for the top-5 underserved ZIPs; the single highest-impact action shows a projected Desert Score improvement expressed as a percentage or point change.
- **SC-005**: A non-technical judge can identify the single most underserved Jacksonville community and the proposed intervention in under 2 minutes of reviewing the prototype output.
- **SC-006**: The full pipeline runs end-to-end without manual intervention and all unit tests pass.

---

## Assumptions

- Analysis is scoped to Jacksonville (Duval County) ZIP codes present in the provided datasets.
- ZIP code is the primary geographic unit (not census tract) since all provided datasets align on this granularity.
- "Preventative assets" are operationalized as: primary care provider count (HealthCareWorkers), food access score (USDA FARA), park presence (Parks), and insurance coverage rate (HealthCareAccess).
- "Poor outcomes" are operationalized using CDC PLACES metrics: mental health distress rate and at least one chronic disease prevalence rate.
- The prototype is a static analysis run at a point in time; it does not require real-time data feeds.
- The AI/optimization component is implemented as a gap-closure simulation: each resource type is hypothetically added to the top-5 underserved ZIPs and the projected Desert Score improvement is computed. A trained ML model is not required.
- Social Vulnerability Index (SVI) and FEMA data are used as demand-side co-variables, not primary outcome measures.
- The Metadata.xlsx file will be consulted to correctly interpret column names before any merging or feature construction.
