# Column Reference: Jacksonville Resource Desert Datasets

**Branch**: `001-resource-desert-analysis` | **Date**: 2026-03-28
**Source**: Inspected from `data/raw/Metadata.xlsx` + CSV headers

All datasets exported from the mySidewalk platform. Each file shares the same first 4 columns:
- `feature id` — internal platform ID
- `feature label` — human-readable label, e.g. "ZIP Code 32202" → extract ZIP with `str.extract(r'(\d{5})')`
- `shid` — platform shape ID
- `geoid` — geographic ID (GEOID format varies; use `feature label` for ZIP extraction)

**37 rows** in each dataset = 37 Jacksonville (Duval County) ZIP codes.

---

## CDCPlaces.csv — 18 columns

| Column | Type | Notes |
|--------|------|-------|
| `Life Expectancy at Birth (2010-2015)` | float | Years |
| `Fair or Poor General Health Among Adults (2023)` | float | % of adults |
| `Diagnosed Depression Among Adults (2023)` | float | % of adults |
| `Any Disability Among Adults (2023)` | float | % of adults |
| `Poor Physical Health Among Adults (2023)` | float | % of adults |
| `Regular Smoking Among Adults (2023)` | float | % of adults |
| `Obesity Among Adults (2023)` | float | % of adults — used in disease_burden |
| `No Leisure-Time Physical Activity Among Adults (2023)` | float | % of adults |
| **`Poor Mental Health Among Adults (2023)`** | float | % of adults — **primary outcome metric** |
| `Doctor Checkup in Past Year Among Adults (2023)` | float | % of adults |
| `Lack of Health Insurance Among Adults (2023)` | float | % of adults |
| `High Blood Pressure Among Adults (2023)` | float | % of adults |
| `High Cholesterol Among Adults (2023)` | float | % of adults |
| `Daytime Population (2022)` | int | Count |

---

## Census-Demographics.csv — 28 columns

| Column | Type | Notes |
|--------|------|-------|
| **`Total Population (2020-2024)`** | int | **Denominator for all rate calculations** |
| `Less than $25,000 Income (2020-2024)` … `$200,000+ Income (2020-2024)` | int | 8 income bracket counts |
| Race/Ethnicity columns (White, Black, Hispanic, Asian, etc.) | int | 7 columns |
| Education columns (Less than 9th Grade … Graduate Degree) | int | 8 columns |

---

## Census-Housing&Poverty.csv — 12 columns

| Column | Type | Notes |
|--------|------|-------|
| **`Median Household Income (2020-2024)`** | float | USD |
| `Owner Occupied Household Median Income (2020-2024)` | float | USD |
| `Renter Occupied Household Median Income (2020-2024)` | float | USD |
| **`Excessive Housing Costs (30%+ of Income) (2020-2024)`** | int | Count of households |
| `Renter Excessive Housing Costs (2020-2024)` | int | Count |
| `Home Owner Excessive Housing Costs (2020-2024)` | int | Count |
| **`People Below Poverty Level (2020-2024)`** | int | Count — used to compute `poverty_rate` |
| `Low Income Population (200%+ Poverty Level) (2020-2024)` | int | Count |

---

## FEMA.csv — 9 columns

| Column | Type | Notes |
|--------|------|-------|
| `Environmental Hazard Community Resilience Score (2025)` | float | 0–100; higher = more resilient |
| `Environmental Hazard Expected Annual Loss Total (2025)` | float | USD |
| `Social Vulnerability to Environmental Hazards (2024)` | float | 0–1; higher = more vulnerable |
| `Air Toxics Cancer Risk Environmental Justice Index (2023)` | float | |
| `Traffic Proximity and Volume Environmental Justice Index (2024)` | float | |

---

## HealthCareAccess.csv — 13 columns

| Column | Type | Notes |
|--------|------|-------|
| `Mental Health Providers (2025)` | int | Count in ZIP |
| `Total Health Care Workers (2025)` | int | Count in ZIP |
| **`People with Health Insurance (2020-2024)`** | int | Count |
| **`People without Health Insurance (2020-2024)`** | int | Count — used for `uninsured_rate` |
| `Age 18 and Under with Health Insurance (2020-2024)` | int | Count |
| `Age 18 and Under without Health Insurance (2020-2024)` | int | Count |
| `Lack of Health Insurance Among Adults (2023)` | float | % |
| `People with Private Health Insurance (2020-2024)` | int | Count |
| `People with Public Health Insurance (2020-2024)` | int | Count |

---

## HealthCareWorkers.csv — 8 columns

| Column | Type | Notes |
|--------|------|-------|
| `Pediatrician Ratio (2025)` | float | Per 100k; some NaN values present |
| **`Primary Care Physician Ratio (2025)`** | float | Per 100k population — **supply metric; higher = better** |
| **`Primary Care Nurse Practitioner Ratio (2025)`** | float | Per 100k |
| `Child Care Centers (2023)` | int | Count in ZIP |

---

## Parks.csv — 7 columns

| Column | Type | Notes |
|--------|------|-------|
| `Number of Parks (2018)` | int | Count |
| **`Percent Area Covered by Parks (2018)`** | float | 0–100 scale — **supply metric; higher = better** |
| `Park Area (acres) (2018)` | float | Acres |

---

## SocialVulnerabilityIndex.csv — 6 columns

| Column | Type | Notes |
|--------|------|-------|
| **`Social Vulnerability Index Within the State (2022)`** | float | 0–1; higher = more vulnerable |
| `Social Vulnerability Index Highly Vulnerable Factors Within the State (2022)` | int | Count of highly vulnerable factors |

---

## USDA-FoodAccess.csv — 16 columns

| Column | Type | Notes |
|--------|------|-------|
| **`People 1/2 Mile Urban/10 Miles Rural with Low Access to Healthy Food (2019)`** | int | Count |
| `People 1 Miles Urban/10 Miles Rural with Low Access to Healthy Food (2019)` | int | Count |
| **`People 1 Mile Urban/20 Miles Rural with Low Access to Healthy Food (2019)`** | int | Count — **used for food gap (widest threshold)** |
| **`Low Income People (USDA) (2019)`** | int | Count |
| `Children Age 17 and Under (USDA) (2019)` | int | Count |
| `Seniors Age 65 and Over (USDA) (2019)` | int | Count |
| Race/population breakdown columns (White, Black, Asian, etc.) | int | 6 columns |

---

## Desert Score Column Mapping

| Score Component | Source Column | Direction |
|----------------|---------------|-----------|
| `supply_gap_healthcare` | `Primary Care Physician Ratio (2025)` | Higher ratio = better = lower gap; gap = `1 - normalize(ratio)` |
| `supply_gap_food` | `People 1 Mile Urban/20 Miles Rural... / Total Population` | Higher % = worse = higher gap |
| `supply_gap_parks` | `Percent Area Covered by Parks (2018)` | Higher % = better = lower gap; gap = `1 - normalize(pct)` |
| `supply_gap_insurance` | `People without Health Insurance / Total Population` | Higher rate = worse = higher gap |
| `poverty_rate` | `People Below Poverty Level / Total Population` | Demand component |
| `disease_burden` | avg(`Poor Mental Health %`, `Obesity %`) / 100 | Demand component |
| `demand_factor` | `normalize(poverty_rate × disease_burden)` | Multiplier |
