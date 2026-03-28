# Quickstart: Per-Dataset EDA Notebooks

**Branch**: `002-per-dataset-eda-notebooks`

---

## Prerequisites

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Ensure data/raw/ contains all 9 CSV source files
```

---

## Run a Single EDA Notebook

```bash
jupyter notebook notebooks/eda/eda_cdc_places.ipynb
# Then: Kernel → Restart & Run All
```

Or execute headlessly:

```bash
jupyter nbconvert --to notebook --execute notebooks/eda/eda_cdc_places.ipynb \
  --output notebooks/eda/eda_cdc_places_executed.ipynb
```

---

## Run All EDA Notebooks (e2e tests)

```bash
# Using nbmake (install: pip install nbmake)
pytest --nbmake notebooks/eda/ -v

# Or the tagged e2e suite
pytest tests/e2e/test_eda_notebooks.py -v -m e2e
```

---

## Notebook Section Structure

Every EDA notebook follows this 4-section layout:

| # | Section Heading | What It Covers |
|---|---|---|
| 1 | Data Loading & Schema Summary | Load raw CSV, display shape, dtypes, null rates per column, ZIP key check |
| 2 | Data Quality Assessment | Null flags (usable/needs_cleaning/too_sparse), duplicate count, IQR outlier table |
| 3 | Univariate Distributions | Histogram per numeric column, frequency table per categorical (≤20 unique values) |
| 4 | Domain-Relevant Analysis | Ranked bar chart: top/bottom 10 ZIPs by dataset's primary metric |

---

## Adding a New Notebook

If a new raw data file is added to `data/raw/`:

1. Copy any existing EDA notebook as a template.
2. Rename to `eda_<new_file_stem>.ipynb` and place in `notebooks/eda/`.
3. Update Section 1 to point to the new file path.
4. Update Section 4's primary metric to match the new dataset's domain.
5. Add to the dataset coverage table in `specs/002-per-dataset-eda-notebooks/spec.md`.
6. Confirm `pytest --nbmake notebooks/eda/eda_<new_file_stem>.ipynb` passes.

---

## Key Conventions

- **No maps**: Domain analysis uses ranked bar charts only (no Folium/choropleth).
- **No transformation logic**: Cleaning code belongs in `src/cleaning.py`, not notebook cells.
- **Clear outputs before committing**: `jupyter nbconvert --clear-output notebooks/eda/*.ipynb`
- **Data Quality Flags are warnings**: "too_sparse" does not mean "drop this column" — that decision belongs in the pipeline.
