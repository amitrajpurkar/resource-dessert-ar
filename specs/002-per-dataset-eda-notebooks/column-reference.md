# Column Reference: Raw Data Files

**Source**: `data/raw/Metadata.xlsx` cross-referenced against actual CSV headers.
**Generated**: 2026-03-28 (T004 — Phase 1 setup)

---

## Shared Columns (All 9 Datasets)

| Column | Type | Description |
|---|---|---|
| `feature id` | string | Internal MySideWalk feature identifier |
| `feature label` | string | Human-readable label (e.g., "ZIP Code 32202") |
| `shid` | string | Hierarchical spatial identifier (e.g., `country:us/state:fl/zip:32202`) |
| `geoid` | int | **ZIP code — primary join key across all datasets** (5-digit, e.g., 32202) |

> **ZIP key**: `geoid` is the join key. Format is integer (no leading zero issues for FL ZIPs starting with 3). Verify dtype consistency across datasets in Section 1 of each notebook.

---

## CDCPlaces.csv — 18 columns (14 domain + 4 shared)

**Source**: CDC PLACES Local Data for Better Health + CDC NCHS + CDC ATSDR
**Primary ranking metric**: Highest chronic disease prevalence rate

| Column | Source | Notes |
|---|---|---|
| `Life Expectancy at Birth (2010-2015)` | CDC NCHS | Years; older vintage (2010–2015) |
| `Fair or Poor General Health Among Adults (2023)` | CDC PLACES | % of adults |
| `Diagnosed Depression Among Adults (2023)` | CDC PLACES | % |
| `Any Disability Among Adults (2023)` | CDC PLACES | % |
| `Poor Physical Health Among Adults (2023)` | CDC PLACES | % |
| `Regular Smoking Among Adults (2023)` | CDC PLACES | % |
| `Obesity Among Adults (2023)` | CDC PLACES | % |
| `No Leisure-Time Physical Activity Among Adults (2023)` | CDC PLACES | % |
| `Poor Mental Health Among Adults (2023)` | CDC PLACES | **Key outcome metric** for Resource Desert analysis |
| `Doctor Checkup in Past Year Among Adults (2023)` | CDC PLACES | % |
| `Lack of Health Insurance Among Adults (2023)` | CDC PLACES | % (duplicated in HealthCareAccess) |
| `High Blood Pressure Among Adults (2023)` | CDC PLACES | % |
| `High Cholesterol Among Adults (2023)` | CDC PLACES | % |
| `Daytime Population (2022)` | CDC ATSDR SVI | Count |

---

## Census-Demographics.csv — 28 columns (24 domain + 4 shared)

**Source**: U.S. Census Bureau (2020–2024 ACS 5-year estimates)
**Primary ranking metric**: Population density (total population as proxy — no area column present)

| Column | Notes |
|---|---|
| `Total Population (2020-2024)` | Count; use as denominator for per-capita rates |
| `Income Less than $25,000 (2020-2024)` | Count; income bracket |
| `Income $25,000 to $49,999 (2020-2024)` | Count |
| `Income $50,000 to $74,999 (2020-2024)` | Count |
| `Income $75,000 to $99,999 (2020-2024)` | Count |
| `Income $100,000 to $124,999 (2020-2024)` | Count |
| `Income $125,000 to $149,999 (2020-2024)` | Count |
| `Income $150,000 to $199,999 (2020-2024)` | Count |
| `Income $200,000 or More (2020-2024)` | Count |
| `Black (Not Hispanic or Latino) (2020-2024)` | Count; race/ethnicity breakdown |
| `Asian (Not Hispanic or Latino) (2020-2024)` | Count |
| `Native Hawaiian and Other Pacific Islander (Not Hispanic or Latino) (2020-2024)` | Count |
| `White (Not Hispanic or Latino) (2020-2024)` | Count |
| `Hispanic or Latino (2020-2024)` | Count |
| `American Indian (Not Hispanic or Latino) (2020-2024)` | Count |
| `Single Race Other (Not Hispanic or Latino) (2020-2024)` | Count |
| `Two or More Races Other (Not Hispanic or Latino) (2020-2024)` | Count |
| `Education Less than 9th Grade (2020-2024)` | Count; education attainment |
| `Education 9th to 12th Grade, No Diploma (2020-2024)` | Count |
| `Education High School Degree (2020-2024)` | Count |
| `Education Some College No Degree (2020-2024)` | Count |
| `Education Associate Degree (2020-2024)` | Count |
| `Education Bachelor's Degree (2020-2024)` | Count |
| `Education Graduate Degree (2020-2024)` | Count |

---

## Census-Housing&Poverty.csv — 12 columns (8 domain + 4 shared)

**Source**: U.S. Census Bureau (2020–2024 ACS 5-year estimates)
**Primary ranking metric**: Poverty rate (`People Below Poverty Level` / `Total Population` from Demographics)

| Column | Notes |
|---|---|
| `Median Household Income (2020-2024)` | Dollars; key demand-side indicator |
| `Owner Occupied Household Median Income (2020-2024)` | Dollars |
| `Renter Occupied Household Median Income (2020-2024)` | Dollars |
| `Excessive Housing Costs (Housing Costs 30 Percent or More of Income) (2020-2024)` | % of households; housing cost burden indicator |
| `Renter Excessive Housing Costs (2020-2024)` | % of renters |
| `Home Owner Excessive Housing Costs (2020-2024)` | % of home owners |
| `People Below Poverty Level (2020-2024)` | Count; **primary poverty indicator** |
| `Low Income Population (Income is 200% or Under the Poverty Level) (2020-2024)` | Count; broader low-income threshold |

---

## FEMA.csv — 9 columns (5 domain + 4 shared)

**Source**: FEMA National Risk Index (2025), HVRI Univ SC, EPA EJScreen
**Primary ranking metric**: `Environmental Hazard Community Resilience Score (2025)` (lower = less resilient)

| Column | Notes |
|---|---|
| `Environmental Hazard Community Resilience Score (2025)` | Score; higher = more resilient to hazards |
| `Environmental Hazard Expected Annual Loss Total (2025)` | Dollars; annualized expected loss |
| `Social Vulnerability to Environmental Hazards (2024)` | Index; HVRI composite |
| `Air Toxics Cancer Risk Environmental Justice Index (2023)` | EJ index; percentile |
| `Traffic Proximity and Volume Environmental Justice Index (2024)` | EJ index; percentile |

---

## HealthCareAccess.csv — 13 columns (9 domain + 4 shared)

**Source**: NPPES (2025), U.S. Census (2020–2024), CDC PLACES (2023)
**Primary ranking metric**: Uninsured rate (`People without Health Insurance` / total population)

| Column | Notes |
|---|---|
| `Mental Health Providers (2025)` | Count; supply-side indicator |
| `Total Health Care Workers (2025)` | Count; aggregate supply |
| `People with Health Insurance (2020-2024)` | Count |
| `People without Health Insurance (2020-2024)` | Count; **key access barrier** |
| `Age 18 and Under with Health Insurance (2020-2024)` | Count |
| `Age 18 and Under without Health Insurance (2020-2024)` | Count |
| `Lack of Health Insurance Among Adults (2023)` | % (CDC PLACES); **duplicated from CDCPlaces** |
| `People with Private Health Insurance (2020-2024)` | Count |
| `People with Public Health Insurance (2020-2024)` | Count |

---

## HealthCareWorkers.csv — 8 columns (4 domain + 4 shared)

**Source**: NPPES (2025), County Business Patterns (2023)
**Primary ranking metric**: `Primary Care Physician Ratio (2025)` (population per physician; lower ratio = more underserved)

| Column | Notes |
|---|---|
| `Pediatrician Ratio (2025)` | Population per pediatrician |
| `Primary Care Physician Ratio (2025)` | Population per PCP; **key supply metric** |
| `Primary Care Nurse Practitioner Ratio (2025)` | Population per NP |
| `Child Care Centers (2023)` | Count |

---

## Parks.csv — 7 columns (3 domain + 4 shared)

**Source**: NaNDA openICPSR (2018)
**Primary ranking metric**: `Number of Parks (2018)` or `Percent Area Covered by Parks (2018)`

| Column | Notes |
|---|---|
| `Number of Parks (2018)` | Count; 2018 vintage |
| `Percent Area Covered by Parks (2018)` | % of ZIP area; **preferred ranking metric** |
| `Park Area (acres) (2018)` | Acres; absolute area |

> **Note**: All Parks columns are from 2018 — older vintage than most other datasets. Flag in schema section.

---

## SocialVulnerabilityIndex.csv — 6 columns (2 domain + 4 shared)

**Source**: CDC ATSDR Social Vulnerability Index (2022)
**Primary ranking metric**: `Social Vulnerability Index Within the State (2022)` (higher = more vulnerable)

| Column | Notes |
|---|---|
| `Social Vulnerability Index Within the State (2022)` | Percentile 0–1; **composite SVI score** |
| `Social Vulnerability Index Highly Vulnerable Factors Within the State (2022)` | Count of highly vulnerable sub-themes |

---

## USDA-FoodAccess.csv — 16 columns (12 domain + 4 shared)

**Source**: USDA ERS Food Access Research Atlas (FARA, 2019)
**Primary ranking metric**: `Low Income People (USDA) (2019)` combined with low-access population share

| Column (CSV name) | Metadata.xlsx full name | Notes |
|---|---|---|
| `People 1/2 Mile Urban/10 Miles Rural with Low Access to Healthy Food (2019)` | Same | Count; strictest access threshold |
| `People 1 Miles Urban/10 Miles Rural with Low Access to Healthy Food (2019)` | Same | Count |
| `People 1 Mile Urban/20 Miles Rural with Low Access to Healthy Food (2019)` | Same | Count |
| `Low Income People (USDA) (2019)` | Same | Count; **demand indicator** |
| `Children Age 17 and Under (USDA) (2019)` | `Food Access Calculations Age Groups - Children Age 17 and Under (USDA) (2019)` | ⚠️ Abbreviated in CSV |
| `Seniors Age 65 and Over (USDA) (2019)` | `Food Access Calculations Age Groups - Seniors Age 65 and Over (USDA) (2019)` | ⚠️ Abbreviated in CSV |
| `White Population (USDA) (2019)` | `Food Access Calculations Race Categories - White Population (USDA) (2019)` | ⚠️ Abbreviated in CSV |
| `Black or African American Population (USDA) (2019)` | `Food Access Calculations Race Categories - Black or African American Population (USDA) (2019)` | ⚠️ Abbreviated in CSV |
| `Asian Population (USDA) (2019)` | `Food Access Calculations Race Categories - Asian Population (USDA) (2019)` | ⚠️ Abbreviated in CSV |
| `Native Hawaiian and Other Pacific Islander Population (USDA) (2019)` | `Food Access Calculations Race Categories - Native Hawaiian and Other Pacific Islander Population (USDA) (2019)` | ⚠️ Abbreviated in CSV |
| `American Indian and Alaska Native Population (USDA) (2019)` | `Food Access Calculations Race Categories - American Indian and Alaska Native Population (USDA) (2019)` | ⚠️ Abbreviated in CSV |
| `Other/Multiple Race Population (USDA) (2019)` | `Food Access Calculations Race Categories - Other/Multiple Race Population (USDA) (2019)` | ⚠️ Abbreviated in CSV |

> **⚠️ Column name mismatch**: 8 USDA-FoodAccess columns use abbreviated names in the CSV vs. Metadata.xlsx.
> Flag this discrepancy in the `eda_usda_food_access.ipynb` schema section per spec FR-002.

---

## Cross-Dataset Notes for Notebooks

- **`geoid`** is the ZIP code in all 9 files. Format: integer (e.g., 32202). No leading-zero issues for Florida ZIPs.
- **`Lack of Health Insurance Among Adults (2023)`** appears in both `CDCPlaces` and `HealthCareAccess` — flag as duplicate in schema sections.
- **Parks data vintage (2018)** is older than all other datasets — note this in `eda_parks.ipynb`.
- **USDA-FoodAccess data vintage (2019)** is also older — note in `eda_usda_food_access.ipynb`.
- All datasets appear to cover Jacksonville (Duval County) ZIP codes only.
