# Resource Desert — Optimizing Services Reach
### UNF CodeforAwhile Datathon 2026

Jacksonville is a city of vast geography and diverse neighborhoods. However, essential services are physically or financially out of reach for those who need them most.

**The Inequity Cycle:** A lack of *Preventative Assets* (parks, primary care, healthy food) leads directly to *Poor Outcomes* (mental health struggles, lower life expectancy).

**The Mission:** Use data and AI to bridge the gap between the *supply* of care and the *demand* of the community — putting the right resources in the right places.

---

## Key Questions

1. What is the biggest mismatch between residents and the essential services available to them (by neighborhood/ZIP)?
2. How do Resource Deserts directly affect long-term health outcomes? *(Show the relationship between lack of preventative assets and poor outcomes.)*
3. How would you use AI to "put the right resources in the right places"? Propose a data-driven solution that bridges the gap for a specific Jacksonville community.

---

## Data Sources (`data/raw/` — read-only)

| File | Source | Contents |
|---|---|---|
| `Census-Demographics.csv` | U.S. Census Bureau | Population, age, race by ZIP |
| `Census-Housing&Poverty.csv` | U.S. Census Bureau | Housing cost burden, poverty rates |
| `CDCPlaces.csv` | CDC | Chronic disease prevalence, health behaviors by ZIP |
| `FEMA.csv` | FEMA | Disaster risk and community vulnerability indicators |
| `HealthCareAccess.csv` | NPPES / EPA EJScreen | Insurance coverage and access barriers |
| `HealthCareWorkers.csv` | NPPES | Provider counts and specialties by area |
| `Parks.csv` | NaNDA | Park presence and access by neighborhood |
| `SocialVulnerabilityIndex.csv` | CDC SVI | Composite social vulnerability scores |
| `USDA-FoodAccess.csv` | USDA FARA | Food desert classification and grocery access |
| `Metadata.xlsx` | — | Column definitions and data dictionary |
| `jacksonville_zctas.geojson` | Census TIGER/Line 2022 | ZCTA boundaries for choropleth map |

---

## Project Structure

```
prob1-resource-desert/
├── data/
│   ├── raw/               ← Original source files — never modify
│   ├── processed/         ← Cleaned/merged datasets
│   └── outputs/           ← Model outputs (scores, predictions)
├── notebooks/
│   └── resource_desert_analysis.ipynb  ← End-to-end narrative notebook
├── src/
│   ├── config.py          ← All path constants and logging helper
│   ├── ingestion.py       ← Stage 1: load raw CSVs
│   ├── cleaning.py        ← Stage 2: standardise ZIPs, fix types, clip rates
│   ├── features.py        ← Stage 3: merge, Desert Score, correlations
│   ├── models.py          ← Stage 4: gap-closure simulation, intervention ranking
│   └── visualization.py   ← Stage 5: bar chart, choropleth map, scatter, heatmap
├── tests/
│   ├── conftest.py        ← Synthetic fixture DataFrames
│   ├── test_ingestion.py
│   ├── test_cleaning.py
│   ├── test_features.py
│   ├── test_models.py
│   ├── test_visualization.py
│   └── e2e/
│       └── test_pipeline_e2e.py  ← Full pipeline on real data (@pytest.mark.e2e)
├── reports/
│   ├── figures/           ← All saved plots (≥150 DPI)
│   └── outputs/           ← desert_scores.csv, intervention_recommendations.json
├── specs/                 ← Feature spec, plan, tasks, contracts
├── requirements.txt
└── pytest.ini
```

---

## How to Run

### 1. Set up the environment

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. (One-time) Download the Jacksonville ZCTA boundary file

Required for the choropleth map. Downloads the Census TIGER/Line ZCTA5 shapefile,
filters to Jacksonville-area ZIPs, and writes `data/raw/jacksonville_zctas.geojson`.

```bash
python - <<'EOF'
import geopandas as gpd
from pathlib import Path

url = "https://www2.census.gov/geo/tiger/TIGER2022/ZCTA520/tl_2022_us_zcta520.zip"
gdf = gpd.read_file(url)
jax = gdf[gdf["ZCTA5CE20"].str.startswith(("320", "322"))]
out = Path("data/raw/jacksonville_zctas.geojson")
out.parent.mkdir(parents=True, exist_ok=True)
jax.to_file(str(out), driver="GeoJSON")
print(f"Saved {len(jax)} ZCTAs → {out}")
EOF
```

### 3. Run the full pipeline via the notebook

```bash
jupyter lab notebooks/resource_desert_analysis.ipynb
```

The notebook runs all five pipeline stages in order and produces:

| Output | Path |
|---|---|
| Merged dataset | `data/processed/merged_jacksonville.csv` |
| Desert scores | `reports/outputs/desert_scores.csv` |
| Intervention recommendations | `reports/outputs/intervention_recommendations.json` |
| Choropleth map (interactive HTML) | `reports/outputs/resource_desert_map.html` |
| Bar chart (top-10 ZIPs) | `reports/figures/desert_scores_bar_chart.png` |
| Health outcome scatter | `reports/figures/preventative_asset_vs_health_outcome.png` |
| Intervention heatmap | `reports/figures/intervention_impact_heatmap.png` |
| Category views (×4) | `reports/figures/category_{name}_view.png` |


### 3.5 Run a flask presentation
run this command
```
source .venv/bin/activate && python app.py →              
  http://127.0.0.1:5000
```



### 4. Run unit tests

```bash
# All unit tests (no real data required)
pytest tests/ -v -m "not e2e"

# With coverage report
pytest tests/ -m "not e2e" --cov=src --cov-report=term-missing
```

### 5. Run end-to-end tests (requires `data/raw/` populated)

```bash
pytest tests/ -v -m e2e
```

### 6. Lint and format

```bash
ruff check src/ tests/          # lint
black src/ tests/               # auto-format
```

### 7. Clear notebook outputs before committing

```bash
jupyter nbconvert --clear-output --inplace notebooks/*.ipynb
```

---

## Pipeline Overview

```
load_raw_datasets()          # ingestion.py  — 9 CSV/XLSX files → raw DataFrames
        ↓
clean_datasets()             # cleaning.py   — standardise ZIPs, fix dtypes, clip rates
        ↓
merge_datasets()             # features.py   — outer-join on zip_code, impute nulls
        ↓
compute_desert_score()       # features.py   — demand-weighted Desert Score (0–100)
        ↓
run_gap_closure_simulation() # models.py     — simulate interventions for top-5 ZIPs
rank_interventions()         # models.py     — flag highest-impact action
        ↓
plot_*() / create_*()        # visualization.py — all charts and choropleth map
```
