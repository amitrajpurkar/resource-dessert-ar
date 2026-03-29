# Quickstart: Flask Presentation Dashboard

**Feature**: 003-flask-presentation-dashboard
**Date**: 2026-03-28

---

## Prerequisites

The following must be true before the dashboard is usable:

1. The virtual environment is set up and activated:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. The Jupyter kernel is registered (one-time, already done if notebook was previously run):
   ```bash
   python -m ipykernel install --user --name prob1-resource-desert
   ```

3. The GeoJSON file is present (one-time download):
   ```bash
   python -c "
   import geopandas as gpd
   gdf = gpd.read_file('https://www2.census.gov/geo/tiger/TIGER2022/ZCTA520/tl_2022_us_zcta520.zip')
   jax = gdf[gdf['ZCTA5CE20'].str.startswith(('320', '322'))]
   jax.to_file('data/raw/jacksonville_zctas.geojson', driver='GeoJSON')
   "
   ```

---

## Step 1: Generate Analysis Outputs

Run the notebook to produce all required output files:

```bash
jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.kernel_name=prob1-resource-desert \
  --ExecutePreprocessor.timeout=600 \
  notebooks/resource_desert_analysis.ipynb
```

This produces:
- `reports/outputs/desert_scores.csv`
- `reports/outputs/intervention_recommendations.json`
- `reports/outputs/resource_desert_map.html`
- `reports/figures/desert_scores_bar_chart.png`
- `reports/figures/preventative_asset_vs_health_outcome.png`
- `reports/figures/intervention_impact_heatmap.png`
- `reports/figures/category_healthcare_view.png`
- `reports/figures/category_food_access_view.png`
- `reports/figures/category_parks_view.png`
- `reports/figures/category_insurance_view.png`

---

## Step 2: Start the Dashboard

```bash
python app.py
```

The app starts on `http://127.0.0.1:5000` by default.

Alternatively via Flask CLI:
```bash
flask --app app run
```

---

## Step 3: Open in Browser

Navigate to `http://127.0.0.1:5000` in a browser. The page loads all five sections:
- **Problem Statement** — what a Resource Desert is and why Jacksonville
- **Analysis** — Desert Score methodology, top-10 ZIP table, choropleth map
- **Observations** — health outcome correlation chart and narrative
- **Recommendations** — highest-impact intervention card, heatmap, full table
- **Category Drill-Down** — per-category supply gap charts

---

## Regenerating Data During Presentation

If you need to re-run the analysis without leaving the browser:

1. Click **"Regenerate Data"** in the navigation bar.
2. A spinner appears while the notebook executes (~30–60 seconds).
3. On completion, **reload the page** to see updated outputs.
4. If the run fails, an error banner shows the last 500 characters of notebook stderr.

---

## Running Tests

Unit tests (fast, no real data):
```bash
pytest tests/test_app.py -v
```

Full test suite including e2e (requires notebook outputs):
```bash
pytest tests/ -v
```

---

## Project Layout

```
app.py                          ← Flask entry point, routes, notebook runner
webapp/
├── templates/
│   └── index.html              ← Single Jinja2 template (five sections)
└── static/
    ├── css/
    │   └── style.css           ← Hand-written CSS, no framework
    └── js/
        └── app.js              ← Polling JS for notebook regeneration status
tests/
└── test_app.py                 ← Flask route tests via app.test_client()
src/
└── config.py                   ← Path constants (REPORTS_FIGURES_DIR, etc.)
reports/
├── figures/                    ← Pre-generated PNG charts (served at /figures/<filename>)
└── outputs/                    ← CSV, JSON, HTML map (desert_scores.csv, etc.)
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| "Data not yet generated" on all sections | Notebook not run | Run Step 1 |
| Choropleth map iframe blank | `resource_desert_map.html` missing | Run Step 1 |
| Spinner never stops | Kernel not registered | `python -m ipykernel install --user --name prob1-resource-desert` |
| Error banner on regenerate | Notebook cell raised an exception | Check the error message; re-run notebook in Jupyter to debug |
| `ModuleNotFoundError: folium` | Wrong Python kernel | Verify kernel registration; check venv is activated |
