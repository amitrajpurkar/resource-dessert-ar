# Pipeline I/O Contracts

**Branch**: `001-resource-desert-analysis` | **Date**: 2026-03-28

This document defines the interface contracts between the five pipeline stages. Each stage's contract specifies its inputs, outputs, and invariants that must hold at handoff.

---

## Stage 1: Ingestion (`src/ingestion.py`)

### Input
| Source | Path | Format |
|--------|------|--------|
| Census Demographics | `data/raw/Census-Demographics.csv` | CSV |
| Census Housing & Poverty | `data/raw/Census-Housing&Poverty.csv` | CSV |
| CDC PLACES | `data/raw/CDCPlaces.csv` | CSV |
| FEMA | `data/raw/FEMA.csv` | CSV |
| Healthcare Access | `data/raw/HealthCareAccess.csv` | CSV |
| Healthcare Workers | `data/raw/HealthCareWorkers.csv` | CSV |
| Parks | `data/raw/Parks.csv` | CSV |
| Social Vulnerability Index | `data/raw/SocialVulnerabilityIndex.csv` | CSV |
| USDA Food Access | `data/raw/USDA-FoodAccess.csv` | CSV |
| Metadata | `data/raw/Metadata.xlsx` | XLSX |
| Jacksonville ZCTAs | `data/raw/jacksonville_zctas.geojson` | GeoJSON |

### Output
```python
Dict[str, pd.DataFrame]  # keyed by dataset name, e.g. "census_demographics"
```

### Invariants
- All paths exist; raises `FileNotFoundError` with descriptive message if missing.
- Returned DataFrames are unmodified copies of raw source data.
- Each DataFrame has at least one row.
- Shape and dtype are logged at INFO level.

---

## Stage 2: Cleaning (`src/cleaning.py`)

### Input
```python
raw_datasets: Dict[str, pd.DataFrame]   # from ingestion
```

### Output
```python
Dict[str, pd.DataFrame]   # same keys; cleaned versions
```

### Invariants
- ZIP column standardized to `zip_code` (str, 5-char, zero-padded) in every DataFrame.
- No duplicate rows per `zip_code` within each dataset.
- Numeric columns have correct dtypes (float64 or int64).
- Rate/proportion columns clipped to [0.0, 1.0].
- Every row drop is logged: `logger.info("Dropped %d rows: %s", n, reason)`.
- Before/after record counts logged at INFO level for every transformation.

---

## Stage 3: Feature Engineering (`src/features.py`)

### Input
```python
cleaned_datasets: Dict[str, pd.DataFrame]   # from cleaning
```

### Output
```python
merged_df: pd.DataFrame       # wide table, one row per ZIP, saved to data/processed/merged_jacksonville.csv
desert_scores_df: pd.DataFrame  # zip_code + all ResourceDesertScore fields, saved to reports/outputs/desert_scores.csv
```

### Invariants
- `merged_df` has no duplicate `zip_code` values.
- `merged_df` excludes ZIPs with `population == 0`; exclusion count logged.
- `desert_score` values in [0.0, 100.0].
- `desert_rank` is a contiguous integer sequence starting at 1.
- Null supply metrics imputed with column median before score computation; imputation count logged.

---

## Stage 4: Models / Simulation (`src/models.py`)

### Input
```python
desert_scores_df: pd.DataFrame    # from features
merged_df: pd.DataFrame           # from features (for population and supply metrics)
top_n: int = 5                    # number of underserved ZIPs to simulate
```

### Output
```python
interventions_df: pd.DataFrame   # one row per (ZIP × resource_type), saved to reports/outputs/intervention_recommendations.json
```

### Invariants
- `interventions_df` has exactly `top_n × 4` rows (4 resource types per ZIP).
- Exactly one row has `is_highest_impact == True`.
- `score_improvement` ≥ 0 for all rows (simulation cannot worsen score).
- `pct_improvement` in [0.0, 100.0].
- `np.random.seed(42)` and `random.seed(42)` set at function entry if any randomness is used.

---

## Stage 5: Visualization (`src/visualization.py`)

### Input
```python
desert_scores_df: pd.DataFrame
merged_df: pd.DataFrame
interventions_df: pd.DataFrame
geojson_path: Path
figures_dir: Path    # reports/figures/
outputs_dir: Path    # reports/outputs/
```

### Output
- `reports/figures/desert_scores_bar_chart.png` — top-10 ZIPs ranked by Desert Score
- `reports/figures/preventative_asset_vs_health_outcome.png` — scatter/correlation chart
- `reports/figures/intervention_impact_heatmap.png` — simulation results
- `reports/outputs/resource_desert_map.html` — standalone Folium choropleth

### Invariants
- All PNG figures saved at ≥150 DPI.
- Every figure has: descriptive title, labelled axes with units, legend where multi-series.
- Folium HTML is a standalone file (no external network dependencies at render time).
- All output paths are created if they do not exist (`Path.mkdir(parents=True, exist_ok=True)`).
