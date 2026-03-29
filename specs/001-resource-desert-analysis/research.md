# Research: Resource Desert Analysis & Optimization

**Branch**: `001-resource-desert-analysis` | **Date**: 2026-03-28

---

## 1. Jacksonville ZIP Code GeoJSON for Choropleth Map

**Decision**: Obtain a ZCTA (ZIP Code Tabulation Area) GeoJSON for Florida/Duval County from the U.S. Census Bureau TIGER/Line shapefiles, convert to GeoJSON, and filter to Jacksonville ZIPs present in the datasets.

**Rationale**: Folium choropleth requires a GeoJSON where each feature's `id` or a named property matches the DataFrame's ZIP column. Census TIGER/Line is the authoritative source; it is freely downloadable. Since we are offline at a conference, the GeoJSON must be pre-downloaded and stored locally (suggested: `data/raw/jacksonville_zctas.geojson` or `data/processed/`).

**Alternatives considered**:
- `geopandas` + Census shapefile (TIGER ZIP5 shapefile): viable but requires conversion step; TIGER/Line is the source either way.
- Third-party GeoJSON APIs: rejected — requires internet; violates offline constraint.

**Action required**: Before pipeline runs, place `jacksonville_zctas.geojson` in `data/raw/`. The ingestion module must validate its presence and raise `FileNotFoundError` with a clear message if missing.

---

## 2. Demand-Weighted Desert Score Formula

**Decision**:

```
supply_gap_i = 1 - normalize(raw_supply_metric_i)     # higher gap = lower supply
demand_factor = normalize(poverty_rate × disease_burden_composite)
component_score_i = supply_gap_i × demand_factor
desert_score = normalize(Σ component_score_i) × 100   # final range 0–100
```

Where:
- **Supply gap metrics** (4 components): healthcare provider density (`HealthCareWorkers`), food access score (`USDA-FoodAccess`), park presence binary or score (`Parks`), insurance coverage rate (`HealthCareAccess`)
- **Disease burden composite**: average of CDC PLACES mental health distress rate + at least one chronic disease prevalence (e.g., diabetes rate)
- **normalize()**: min-max normalization across all Jacksonville ZIPs in scope

**Rationale**: Demand-weighting ensures that a missing resource in a high-poverty, high-disease-burden ZIP scores higher than the same gap in a wealthier ZIP. This directly implements FR-001 and the clarification from the spec session (2026-03-28).

**Tie-breaking**: ZIPs with identical Desert Scores are ranked by descending poverty rate (spec edge case).

**Alternatives considered**:
- Equal-weight composite (no demand factor): simpler but does not capture community need; rejected per spec clarification.
- PCA-based composite: more sophisticated but less interpretable for non-technical judges; rejected per YAGNI principle.

---

## 3. Gap-Closure Simulation Approach

**Decision**: For each of the top-5 underserved ZIPs, simulate setting each supply gap metric to its 75th-percentile value (i.e., "what if this ZIP had adequate supply for this resource?"). Recompute the Desert Score with the simulated value. Report: ZIP, resource type, current score, simulated score, Δ score, % improvement, estimated population impacted.

**Rationale**: The 75th-percentile target is defensible (achievable benchmark, not utopian) and interpretable. Simulating each resource independently isolates the marginal impact of each intervention type. This directly implements FR-004.

**Alternatives considered**:
- Setting supply metric to max observed: maximalist; unrealistic for a judge audience.
- Trained ML model predicting score: FR-014 requires CV if used as a reported deliverable; adds complexity without improving interpretability for the prototype; spec assumptions note a trained model is not required.

---

## 4. Multi-Dataset Merge Strategy

**Decision**: Use ZIP code as the sole join key. Merge strategy:

1. Load each dataset independently via `ingestion.py`.
2. Standardize the ZIP column name to `zip_code` (string, zero-padded to 5 chars) in `cleaning.py` for each dataset.
3. Filter each dataset to Duval County ZIPs only (cross-reference with Census-Demographics ZIPs as the authoritative ZIP list).
4. Outer-join all datasets on `zip_code`, then flag and log ZIPs with missing values per source.
5. Drop ZIPs with no population data (commercial-only); log count and reason.
6. Impute remaining nulls conservatively: numeric supply metrics → median of non-null ZIPs; binary flags → 0 (assume absent if unknown).

**Rationale**: ZIP code is confirmed as the primary granularity (spec assumption). Outer join preserves all ZIPs for audit; inner join could silently exclude underserved ZIPs that are absent from one dataset.

**Alternatives considered**:
- Inner join across all datasets: fast but silent data loss; violates FR-005 (no silent drops).
- Census tract granularity: not consistent across all source datasets; rejected per spec assumption.

---

## 5. Folium Choropleth Implementation

**Decision**:

```python
import folium
choropleth = folium.Choropleth(
    geo_data=geojson_path,
    data=desert_scores_df,
    columns=["zip_code", "desert_score"],
    key_on="feature.properties.ZCTA5CE10",  # Census TIGER ZCTA property name
    fill_color="RdYlGn_r",   # red = high deprivation, green = low
    fill_opacity=0.75,
    line_opacity=0.3,
    legend_name="Resource Desert Score (0–100)",
    highlight=True,
)
# Add tooltip with ZIP, score, top supply gap
```

Export: `map.save("reports/outputs/resource_desert_map.html")` (FR-009).

**Rationale**: Folium produces standalone HTML with no server needed; `RdYlGn_r` is intuitive (red = bad) for non-technical audiences (SC-005). `ZCTA5CE10` is the standard Census TIGER property name for ZIP codes.

**Alternatives considered**:
- Plotly Choropleth: richer interactivity but heavier dependency; folium is already sufficient for a standalone HTML file.
- Static matplotlib map with geopandas: no interactivity; harder for judges to explore in 2 minutes (SC-002, SC-005).

---

## 6. Test Coverage Strategy

**Decision**: Synthetic fixture DataFrames in `tests/conftest.py` covering all 5 modules. Each public function gets at least one unit test. E2E test (`tests/e2e/test_pipeline_e2e.py`) runs full pipeline on real data and is tagged `@pytest.mark.e2e`. Target: ≥70% line coverage (FR-015 hard gate).

**Key fixtures needed**:
- `sample_census_df`: 5 rows, required Census columns
- `sample_cdc_df`: 5 rows, required CDC PLACES columns
- `sample_merged_df`: 5 rows, all supply/demand columns after merge
- `sample_desert_scores_df`: 5 rows with `zip_code` + `desert_score`

---

## 7. Open Item: Raw Data Files

**Status**: `data/raw/` is currently empty. All 9 CSV files and `Metadata.xlsx` must be placed there before the pipeline can run. The ingestion module will validate their presence at startup.

**Files expected**:
- `Census-Demographics.csv`
- `Census-Housing&Poverty.csv`
- `CDCPlaces.csv`
- `FEMA.csv`
- `HealthCareAccess.csv`
- `HealthCareWorkers.csv`
- `Parks.csv`
- `SocialVulnerabilityIndex.csv`
- `USDA-FoodAccess.csv`
- `Metadata.xlsx`
- `jacksonville_zctas.geojson` (to be sourced from Census TIGER/Line)
