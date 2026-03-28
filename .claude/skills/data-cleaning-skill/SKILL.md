# Skill: Data Cleaning

## Purpose
Transform a raw dataset into a clean, consistent, analysis-ready form while preserving a full audit trail of every change made.

## When to Use
- After `data-evaluation-skill` has identified issues
- Before feature engineering or modelling
- When merging or joining multiple datasets

## Prerequisites
- Data evaluation has been completed and findings documented
- Raw file is untouched in `data/raw/`
- Output will be written to `data/processed/`

---

## Procedure

### Step 0 — Setup & Logging
```python
import pandas as pd
import numpy as np
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

RAW_PATH = Path("data/raw/<file>")
OUT_PATH = Path("data/processed/<file>_cleaned.parquet")

df = pd.read_csv(RAW_PATH)
log.info(f"Loaded: {df.shape[0]} rows × {df.shape[1]} cols from {RAW_PATH}")
```

### Step 1 — Column Standardisation
```python
# Standardise column names: lowercase, underscores, no special chars
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(r"[\s\-/]+", "_", regex=True)
    .str.replace(r"[^\w]", "", regex=True)
)
log.info(f"Columns after standardisation: {df.columns.tolist()}")
```

### Step 2 — Fix Data Types
```python
# Explicitly cast each column to its intended type
# Adjust this block to match your dataset

# Dates
# df["date_col"] = pd.to_datetime(df["date_col"], errors="coerce")

# Numerics stored as strings
# df["amount"] = pd.to_numeric(df["amount"].str.replace(",", ""), errors="coerce")

# Categoricals with low cardinality
# df["status"] = df["status"].astype("category")

log.info("Dtypes after casting:\n" + str(df.dtypes))
```

### Step 3 — Handle Duplicates
```python
before = len(df)
df = df.drop_duplicates()
dropped = before - len(df)
log.info(f"Dropped {dropped} full-row duplicates ({dropped/before*100:.2f}%)")

# Key-based duplicates — keep most recent / first occurrence as appropriate
# key_cols = ["id"]
# df = df.sort_values("date").drop_duplicates(subset=key_cols, keep="last")
```

### Step 4 — Handle Missing Values
```python
# Strategy must be deliberate — document each decision

# 1. Drop columns that are beyond salvageable (>60% null) — log which ones
high_null_cols = df.columns[df.isnull().mean() > 0.60].tolist()
if high_null_cols:
    log.warning(f"Dropping high-null columns (>60%): {high_null_cols}")
    df = df.drop(columns=high_null_cols)

# 2. Fill numeric nulls with median (not mean — robust to outliers)
num_cols = df.select_dtypes(include=[np.number]).columns
for col in num_cols:
    n_null = df[col].isnull().sum()
    if n_null > 0:
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        log.info(f"  {col}: filled {n_null} nulls with median={median_val:.4f}")

# 3. Fill categorical nulls with mode or explicit "Unknown"
cat_cols = df.select_dtypes(include=["object", "category"]).columns
for col in cat_cols:
    n_null = df[col].isnull().sum()
    if n_null > 0:
        fill_val = df[col].mode()[0] if df[col].notna().sum() > 0 else "Unknown"
        df[col] = df[col].fillna(fill_val)
        log.info(f"  {col}: filled {n_null} nulls with '{fill_val}'")
```

### Step 5 — Outlier Treatment
```python
def cap_outliers_iqr(
    df: pd.DataFrame,
    col: str,
    multiplier: float = 3.0  # Use 3.0 for conservative capping
) -> pd.DataFrame:
    """Cap outliers at IQR-based bounds (Winsorization)."""
    q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - multiplier * iqr, q3 + multiplier * iqr
    n_capped = ((df[col] < lower) | (df[col] > upper)).sum()
    df[col] = df[col].clip(lower=lower, upper=upper)
    log.info(f"  {col}: capped {n_capped} outliers to [{lower:.2f}, {upper:.2f}]")
    return df

# Apply to columns flagged during evaluation
# for col in ["revenue", "expenses"]:
#     df = cap_outliers_iqr(df, col)
```

### Step 6 — String Cleaning
```python
str_cols = df.select_dtypes(include="object").columns
for col in str_cols:
    df[col] = df[col].str.strip()
    # Standardise case where appropriate
    # df[col] = df[col].str.title()  # or .str.upper() / .str.lower()
```

### Step 7 — Post-Clean Assertions
```python
# These must all pass before saving
assert df.isnull().sum().sum() == 0, "Nulls remain after cleaning!"
assert df.duplicated().sum() == 0, "Duplicates remain after cleaning!"
assert len(df) > 0, "DataFrame is empty after cleaning!"

log.info(f"Post-clean shape: {df.shape[0]} rows × {df.shape[1]} cols")
log.info("All post-clean assertions passed.")
```

### Step 8 — Save
```python
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(OUT_PATH, index=False)
log.info(f"Cleaned dataset saved to {OUT_PATH}")
```

---

## Cleaning Decisions Log

For every non-trivial decision, add an entry to `reports/outputs/<case>_cleaning_log.md`:

```markdown
| Column       | Issue Found         | Action Taken             | Rows Affected |
|---|---|---|---|
| revenue      | 14% nulls           | Filled with column median | 47 rows       |
| org_type     | Mixed case strings  | Lowercased & stripped     | All rows      |
| budget_year  | 3 extreme outliers  | Capped at IQR × 3        | 3 rows        |
```

---

## Conventions
- Never modify `data/raw/`. Always write to `data/processed/`.
- Prefer Parquet over CSV for processed files (preserves dtypes, faster I/O).
- All cleaning logic in `src/` must be wrapped in functions with docstrings and type hints.
- Log every transformation with record counts — no silent changes.
