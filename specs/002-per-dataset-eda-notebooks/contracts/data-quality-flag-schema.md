# Contract: Data Quality Flag Schema

**Consumer**: `src/` pipeline modules (ingestion, cleaning, feature engineering)
**Producer**: EDA notebooks (`notebooks/eda/*.ipynb`)
**Version**: 1.0 | **Date**: 2026-03-28

---

## Purpose

Each EDA notebook produces a human-readable Data Quality summary table. This contract defines the flag values and their meaning so that pipeline developers can rely on a consistent vocabulary when consulting EDA notebook outputs.

**Important**: Flags are **observational warnings only**. The pipeline (`src/cleaning.py`) is the authoritative decision-maker on whether to drop, impute, or coerce any column.

---

## Flag Values

| Flag | Trigger Condition | Pipeline Implication |
|---|---|---|
| `usable` | null_pct ≤ 30% AND dtype consistent AND no format issues | May be used directly after type casting |
| `needs_cleaning` | Type inconsistency OR mixed formats (e.g., int/string ZIP mix) | Requires standardisation step before use |
| `too_sparse` | null_pct > 30% | High missingness noted; pipeline decides whether to impute, drop, or use partial |

---

## Outlier Annotation Contract

Outliers are identified using the IQR fence method: `[Q1 − 1.5×IQR, Q3 + 1.5×IQR]`.

Outlier annotations are **informational only** — they do not prescribe removal. A value flagged as an outlier may represent a genuinely extreme ZIP code (e.g., a ZIP with zero providers) that is analytically important to the Resource Desert analysis.

---

## Null Threshold Rationale

The 30% null threshold was chosen as the boundary for `too_sparse` based on the following reasoning:
- Columns with <30% nulls can typically be imputed with mean/median/mode without distorting distributions significantly.
- Columns with >30% nulls have too many missing values for reliable imputation in a small dataset (~60–80 ZIPs); downstream conclusions would be unreliable.
- This threshold applies uniformly across all 9 notebooks for consistency.
