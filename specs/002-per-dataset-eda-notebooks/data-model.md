# Data Model: Per-Dataset EDA Notebooks

**Date**: 2026-03-28
**Branch**: `002-per-dataset-eda-notebooks`

This document describes the logical data structures produced and consumed by the EDA notebooks.

---

## Entity: EDA Notebook

A self-contained, sequentially executable Jupyter notebook covering one raw dataset.

| Attribute | Type | Description |
|---|---|---|
| `source_file` | string | Filename in `data/raw/` (e.g., `CDCPlaces.csv`) |
| `notebook_name` | string | `eda_<source_file_stem>.ipynb` (lowercase, underscores) |
| `location` | path | `notebooks/eda/<notebook_name>` |
| `sections` | ordered list | schema_summary → data_quality → distributions → domain_analysis |
| `zip_column_present` | boolean | Whether a ZIP code join key was detected in the schema |

**Uniqueness**: One notebook per source file. The stem of the source filename is the canonical identifier.

---

## Entity: Schema Summary (per notebook, Section 1)

Produced by Section 1 of each notebook. Represents the structural profile of one dataset.

| Attribute | Type | Description |
|---|---|---|
| `row_count` | int | Total rows in the raw file |
| `column_count` | int | Total columns in the raw file |
| `columns` | list[ColumnProfile] | One entry per column (see below) |
| `zip_key_present` | boolean | Whether a ZIP code column was detected |
| `zip_key_format` | string or null | Observed format: "int", "string-5digit", "mixed", or null if absent |

### Sub-entity: ColumnProfile

| Attribute | Type | Description |
|---|---|---|
| `name` | string | Column name as read from file |
| `dtype` | string | Inferred pandas dtype |
| `null_count` | int | Count of null/NaN values |
| `null_pct` | float | Percentage of null values (0–100) |
| `unique_count` | int | Count of unique non-null values |
| `metadata_name` | string or null | Corresponding name from Metadata.xlsx, if matched |
| `metadata_mismatch` | boolean | True if column name differs from Metadata.xlsx definition |

---

## Entity: Data Quality Flag (per column, Section 2)

The observational annotation assigned to each column after quality assessment. **Flags are warnings only — no drop recommendations.**

| Flag Value | Condition | Meaning |
|---|---|---|
| `"usable"` | null_pct ≤ 30% AND no type issues | Safe to use in pipeline as-is |
| `"needs_cleaning"` | Type inconsistency detected OR mixed formats | Requires type coercion or standardisation before pipeline use |
| `"too_sparse"` | null_pct > 30% | High missing rate — observational warning only; pipeline decides whether to drop |

### Sub-entity: OutlierSummary (per numeric column, Section 2)

| Attribute | Type | Description |
|---|---|---|
| `column` | string | Column name |
| `q1` | float | First quartile |
| `q3` | float | Third quartile |
| `iqr` | float | Interquartile range |
| `lower_fence` | float | Q1 − 1.5×IQR |
| `upper_fence` | float | Q3 + 1.5×IQR |
| `outlier_count` | int | Count of values outside the fence |
| `outlier_zips` | list[string] | ZIP codes associated with outlier values (if ZIP column present) |

---

## Entity: Domain Analysis (per notebook, Section 4)

Dataset-specific ranked analysis section. Minimum one ranked bar chart per notebook.

| Attribute | Type | Description |
|---|---|---|
| `primary_metric` | string | The key metric used for ranking (dataset-specific) |
| `top_n_zips` | list[string] | Top N ZIP codes by primary metric (N=10 by default) |
| `bottom_n_zips` | list[string] | Bottom N ZIP codes by primary metric |
| `chart_title` | string | Descriptive title including metric name and units |
| `resource_desert_relevance` | string | One-sentence note connecting the finding to supply/demand gap |

---

## Dataset-to-Primary-Metric Mapping

| Notebook | Primary Ranking Metric |
|---|---|
| `eda_cdc_places` | Highest chronic disease prevalence rate |
| `eda_census_demographics` | Population density (pop per sq mile) |
| `eda_census_housing_poverty` | Poverty rate (%) |
| `eda_fema` | Composite disaster risk score |
| `eda_healthcare_access` | Uninsured rate (%) |
| `eda_healthcare_workers` | Provider-to-population ratio |
| `eda_parks` | Park access score or park count |
| `eda_social_vulnerability` | Composite SVI percentile |
| `eda_usda_food_access` | Low-income + low-access population share |
