# Research: Per-Dataset EDA Notebooks

**Date**: 2026-03-28
**Branch**: `002-per-dataset-eda-notebooks`

No NEEDS CLARIFICATION items were present in the spec after the clarification session. This document records the key design decisions made and their rationale.

---

## Decision 1: Outlier Detection — IQR Method

**Decision**: Use IQR fence (Q1 − 1.5×IQR, Q3 + 1.5×IQR) for all per-column outlier detection in the data quality section.

**Rationale**: The datasets (poverty rates, provider counts, SVI scores, disease prevalence) are expected to have right-skewed distributions. The standard deviation method assumes normality and will produce misleading outlier counts on skewed data. IQR is distribution-agnostic and aligns with standard boxplot conventions, making it straightforward to explain to non-technical stakeholders.

**Alternatives considered**: ±3σ (rejected — unreliable on skewed data), modified Z-score (robust but less familiar to general audience).

---

## Decision 2: No Choropleth Maps in EDA Notebooks

**Decision**: Domain analysis sections use ranked horizontal bar charts only. No Folium maps or geospatial dependencies in EDA notebooks.

**Rationale**: Maps are the primary visual deliverable of the main analysis spec (001-resource-desert-analysis). Duplicating them in each EDA notebook would add Folium as a dependency, require ZIP boundary GeoJSON data, and inflate scope. Ranked bar charts deliver the same geographic insight (which ZIPs rank highest/lowest) with zero additional dependencies.

**Alternatives considered**: Folium choropleth per notebook (rejected — scope inflation, duplicate of spec 001 deliverable), static matplotlib scatter on lat/lon (rejected — requires coordinate data not guaranteed in all datasets).

---

## Decision 3: Data Quality Flags Are Observational Only

**Decision**: The "too sparse" flag (>30% null) is a warning annotation. Notebooks make no drop recommendations. Pipeline decisions are deferred to `src/cleaning.py`.

**Rationale**: EDA notebooks are exploration artifacts; their role is observation and documentation. Embedding prescriptive logic (drop this column) in notebooks would blur the boundary between exploration and production code, violate the separation of concerns principle in CLAUDE.md, and create a maintenance risk where notebook-embedded decisions diverge from pipeline decisions.

**Alternatives considered**: Prescriptive "recommend exclude" flag (rejected — mixes exploration with pipeline logic), tiered thresholds 30%/50% (rejected — unnecessary complexity for a datathon scope).

---

## Decision 4: Notebook Testing Strategy

**Decision**: Use `pytest-notebook` or `nbmake` to execute all 9 notebooks as e2e tests tagged `@pytest.mark.e2e`. No unit tests for notebook cells (notebooks have no importable functions per FR-009).

**Rationale**: The primary correctness guarantee for notebooks is that they run end-to-end without errors against the actual raw data. Cell-level unit testing of notebooks is impractical and unnecessary at this scope. A single e2e test per notebook (run all cells, assert zero exceptions) satisfies SC-001.

**Implementation note**: `nbmake` is the simpler option — `pytest --nbmake notebooks/eda/` runs all notebooks. If unavailable, `nbconvert --execute` with a shell wrapper achieves the same result.

---

## Decision 5: Standard 4-Section Notebook Structure

**Decision**: Every notebook follows the same top-level section order: (1) Data Loading & Schema Summary, (2) Data Quality Assessment, (3) Univariate Distributions, (4) Domain-Relevant Analysis.

**Rationale**: Consistent section ordering means reviewers can navigate any notebook without re-orienting. It also makes the e2e test assertion (SC-002: "verifiable by section heading presence") straightforward to implement as a text search on the executed notebook output.

**Template cell approach**: Each notebook will begin with a single markdown cell containing a standard header and section headings as anchors. The structure is enforced by convention, not by a shared module (consistent with FR-009).
