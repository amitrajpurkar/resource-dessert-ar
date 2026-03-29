# Data Model: Resource Desert Analysis & Optimization

**Branch**: `001-resource-desert-analysis` | **Date**: 2026-03-28

---

## Entities

### 1. ZipCodeArea

Primary unit of analysis. One row per Jacksonville ZIP code in the merged dataset.

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `zip_code` | `str` (5-char, zero-padded) | All datasets | Join key; Duval County only |
| `population` | `int` | Census-Demographics | Used to exclude commercial-only ZIPs (pop=0); demand weighting |
| `poverty_rate` | `float` (0.0–1.0) | Census-Housing&Poverty | Core demand factor component |
| `median_household_income` | `float` | Census-Housing&Poverty | Co-variable |
| `housing_cost_burden_rate` | `float` (0.0–1.0) | Census-Housing&Poverty | Co-variable |
| `urban_rural_flag` | `str` ("urban"/"rural") | Derived from population density | Prevents distance-only penalization |
| `population_density` | `float` | Derived: `population / geographic_area` | Used for urban/rural classification |

**Validation rules**:
- `zip_code` must match `^\d{5}$`
- `population` ≥ 0; ZIPs with `population == 0` are excluded from scoring (logged)
- `poverty_rate` in [0.0, 1.0]

---

### 2. PreventativeAsset

Supply-side metrics operationalizing access to preventative care resources. Stored as columns on `ZipCodeArea` after merge.

| Field | Type | Source Dataset | Notes |
|-------|------|----------------|-------|
| `provider_count` | `int` | HealthCareWorkers | Primary care providers in ZIP |
| `provider_density` | `float` | Derived: `provider_count / population * 10000` | Per 10k residents |
| `food_access_score` | `float` (0.0–1.0) | USDA-FoodAccess | Higher = better access |
| `low_access_flag` | `bool` | USDA-FoodAccess | USDA food desert classification |
| `nearest_grocery_distance_mi` | `float` | USDA-FoodAccess | Miles to nearest grocery |
| `park_access_score` | `float` (0.0–1.0) | Parks | NaNDA park presence/access metric |
| `has_park` | `bool` | Parks | Binary park presence flag |
| `insurance_coverage_rate` | `float` (0.0–1.0) | HealthCareAccess | Fraction of population with insurance |

**Validation rules**:
- `provider_count` ≥ 0
- `food_access_score`, `park_access_score`, `insurance_coverage_rate` in [0.0, 1.0]
- `nearest_grocery_distance_mi` ≥ 0.0

**Null handling**: Missing supply metrics imputed with ZIP-level median across Duval County; logged with count and reason.

---

### 3. HealthOutcomeMetric

Demand-side and outcome metrics from CDC PLACES. Stored as columns on `ZipCodeArea`.

| Field | Type | Source Dataset | Notes |
|-------|------|----------------|-------|
| `mental_health_distress_rate` | `float` (0.0–1.0) | CDCPlaces | % adults reporting frequent mental distress |
| `diabetes_prevalence_rate` | `float` (0.0–1.0) | CDCPlaces | Primary chronic disease outcome |
| `obesity_prevalence_rate` | `float` (0.0–1.0) | CDCPlaces | Secondary chronic disease outcome |
| `physical_inactivity_rate` | `float` (0.0–1.0) | CDCPlaces | Mediator variable |
| `svi_composite_score` | `float` (0.0–1.0) | SocialVulnerabilityIndex | CDC SVI overall vulnerability |
| `fema_risk_score` | `float` | FEMA | Disaster risk co-variable |

**Validation rules**:
- All rate fields in [0.0, 1.0]

---

### 4. ResourceDesertScore

Computed entity. One row per ZIP. Written to `reports/outputs/desert_scores.csv`.

| Field | Type | Notes |
|-------|------|-------|
| `zip_code` | `str` | Foreign key to ZipCodeArea |
| `desert_score` | `float` (0.0–100.0) | Final demand-weighted composite; higher = more underserved |
| `desert_rank` | `int` | 1 = most underserved; ties broken by `poverty_rate` desc |
| `demand_factor` | `float` (0.0–1.0) | Normalized (poverty_rate × disease_burden_composite) |
| `supply_gap_healthcare` | `float` (0.0–1.0) | Normalized gap in provider density |
| `supply_gap_food` | `float` (0.0–1.0) | Normalized gap in food access |
| `supply_gap_parks` | `float` (0.0–1.0) | Normalized gap in park access |
| `supply_gap_insurance` | `float` (0.0–1.0) | Normalized gap in insurance coverage |
| `top_gap_category` | `str` | Name of the largest supply gap component |

**State transitions**: Computed once from merged `ZipCodeArea` data; no updates (static analysis).

---

### 5. InterventionProposal

Output of gap-closure simulation. Written to `reports/outputs/intervention_recommendations.json`.

| Field | Type | Notes |
|-------|------|-------|
| `zip_code` | `str` | Target ZIP |
| `resource_type` | `str` | One of: "primary_care", "food_access", "parks", "insurance_outreach" |
| `current_desert_score` | `float` | Desert score before simulation |
| `simulated_desert_score` | `float` | Desert score after setting supply metric to 75th percentile |
| `score_improvement` | `float` | `current - simulated` (positive = improvement) |
| `pct_improvement` | `float` | `score_improvement / current_desert_score × 100` |
| `population_impacted` | `int` | ZIP population |
| `is_highest_impact` | `bool` | True for the single best intervention across all top-5 ZIPs |

---

## Relationships

```
ZipCodeArea (1) ──── (1) ResourceDesertScore
ZipCodeArea (1) ──── (N) InterventionProposal  [up to 4 per ZIP × top-5 ZIPs = 20 rows]
ZipCodeArea contains PreventativeAsset fields (embedded columns)
ZipCodeArea contains HealthOutcomeMetric fields (embedded columns)
```

---

## Merged DataFrame Schema (post-clean)

All entities above are stored as a single wide DataFrame (`data/processed/merged_jacksonville.csv`) after the cleaning stage. Columns are the union of all fields defined above, with `zip_code` as the index.

**Post-clean invariants**:
- No duplicate `zip_code` values
- `population > 0` for all retained rows
- All rate/score fields in [0.0, 1.0] or NaN (imputed before feature construction)
- `zip_code` matches `^\d{5}$` for all rows
