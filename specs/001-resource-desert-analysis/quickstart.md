# Quickstart: Resource Desert Analysis & Optimization

**Branch**: `001-resource-desert-analysis` | **Date**: 2026-03-28

---

## Prerequisites

- Python 3.11+
- All raw data files placed in `data/raw/` (see list below)
- `jacksonville_zctas.geojson` placed in `data/raw/` (Census TIGER/Line ZCTA shapefile converted to GeoJSON)

---

## Setup

```bash
# From repo root
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Required Raw Data Files

Place these files in `data/raw/` before running (read-only; never modify):

```
data/raw/
├── Census-Demographics.csv
├── Census-Housing&Poverty.csv
├── CDCPlaces.csv
├── FEMA.csv
├── HealthCareAccess.csv
├── HealthCareWorkers.csv
├── Parks.csv
├── SocialVulnerabilityIndex.csv
├── USDA-FoodAccess.csv
├── Metadata.xlsx
└── jacksonville_zctas.geojson   ← from Census TIGER/Line ZCTA5 shapefile
```

---

## Run the Full Pipeline (Single Command)

```bash
jupyter nbconvert --to notebook --execute notebooks/resource_desert_analysis.ipynb \
  --output notebooks/resource_desert_analysis_executed.ipynb
```

This produces:
- `reports/outputs/desert_scores.csv` — Desert Score per ZIP
- `reports/outputs/intervention_recommendations.json` — Gap-closure simulation results
- `reports/outputs/resource_desert_map.html` — Standalone choropleth map
- `reports/figures/*.png` — All saved charts

---

## Run Tests

```bash
# Unit tests only (no raw data needed)
pytest tests/ -v -m "not e2e"

# All tests including e2e (requires data/raw/ populated)
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov-fail-under=70 --cov-report=term-missing
```

---

## Run Linting & Formatting

```bash
ruff check src/ tests/
black --check src/ tests/
black src/ tests/    # auto-format
```

---

## View the Prototype

Open `reports/outputs/resource_desert_map.html` in any web browser to see the interactive choropleth map. The top-10 most underserved ZIP codes are highlighted in red.

Open `notebooks/resource_desert_analysis.ipynb` in Jupyter for the full annotated analysis:

```bash
jupyter lab notebooks/resource_desert_analysis.ipynb
```

---

## Key Output Files

| File | Description |
|------|-------------|
| `reports/outputs/desert_scores.csv` | Desert Score + rank for every Jacksonville ZIP |
| `reports/outputs/intervention_recommendations.json` | 20 simulated interventions (top-5 ZIPs × 4 resource types); `is_highest_impact` flags the winner |
| `reports/outputs/resource_desert_map.html` | Folium choropleth — open in browser |
| `reports/figures/desert_scores_bar_chart.png` | Top-10 most underserved ZIPs |
| `reports/figures/preventative_asset_vs_health_outcome.png` | Causal chain evidence chart |
| `reports/figures/intervention_impact_heatmap.png` | Gap-closure simulation results |
