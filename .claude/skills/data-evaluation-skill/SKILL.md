# Skill: Data Evaluation

## Purpose
Perform a thorough first-pass evaluation of a dataset — profiling its structure, quality, and suitability for analysis. This skill is the mandatory first step before any cleaning or modelling work begins.

## When to Use
- When a new dataset is introduced to the project
- To produce a dataset quality report before cleaning
- To detect issues early: nulls, cardinality, distributions, suspicious values

---

## Procedure

### Step 1 — Load & Structural Inspection
```python
import pandas as pd
import numpy as np

df = pd.read_csv("data/raw/<file>")  # or read_excel, read_json, etc.

print("Shape:", df.shape)
print("\nDtypes:\n", df.dtypes)
print("\nFirst 5 rows:\n", df.head())
print("\nLast 5 rows:\n", df.tail())
print("\nColumn names:", df.columns.tolist())
```

### Step 2 — Null / Missing Value Analysis
```python
null_summary = pd.DataFrame({
    "null_count": df.isnull().sum(),
    "null_pct":   (df.isnull().sum() / len(df) * 100).round(2)
}).sort_values("null_pct", ascending=False)

print(null_summary[null_summary["null_count"] > 0])
```
**Flag columns with >20% nulls for special treatment decisions.**

### Step 3 — Descriptive Statistics
```python
# Numeric columns
print(df.describe(include=[np.number]).T)

# Categorical / object columns
print(df.describe(include=["object", "category"]).T)
```

### Step 4 — Cardinality & Uniqueness
```python
for col in df.columns:
    n_unique = df[col].nunique()
    pct_unique = n_unique / len(df) * 100
    print(f"{col:40s}  unique={n_unique:6d}  ({pct_unique:.1f}%)")
```
**High-cardinality strings (e.g. IDs, free text) vs. low-cardinality categoricals require different treatment.**

### Step 5 — Duplicate Detection
```python
n_dupes = df.duplicated().sum()
print(f"Full-row duplicates: {n_dupes} ({n_dupes/len(df)*100:.2f}%)")

# Key-based duplicates (adjust key columns)
# key_cols = ["id", "date"]
# print("Key duplicates:", df.duplicated(subset=key_cols).sum())
```

### Step 6 — Distribution Spot-Check (Numeric)
```python
import matplotlib.pyplot as plt
import seaborn as sns

numeric_cols = df.select_dtypes(include=[np.number]).columns
fig, axes = plt.subplots(nrows=(len(numeric_cols) + 2) // 3, ncols=3, figsize=(14, 4 * ((len(numeric_cols) + 2) // 3)))
axes = axes.flatten()

for i, col in enumerate(numeric_cols):
    df[col].dropna().hist(ax=axes[i], bins=30, edgecolor="black")
    axes[i].set_title(col)
    axes[i].set_xlabel("")

for j in range(i + 1, len(axes)):
    axes[j].set_visible(False)

plt.suptitle("Numeric Column Distributions", y=1.01, fontsize=13)
plt.tight_layout()
plt.savefig("reports/figures/data_evaluation_distributions.png", dpi=150)
plt.show()
```

### Step 7 — Outlier Screening (IQR method)
```python
def flag_outliers_iqr(series: pd.Series, multiplier: float = 1.5) -> pd.Series:
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    return (series < q1 - multiplier * iqr) | (series > q3 + multiplier * iqr)

for col in df.select_dtypes(include=[np.number]).columns:
    n_out = flag_outliers_iqr(df[col].dropna()).sum()
    if n_out > 0:
        print(f"{col}: {n_out} outliers ({n_out/df[col].notna().sum()*100:.1f}%)")
```

### Step 8 — Correlation Matrix
```python
corr = df.select_dtypes(include=[np.number]).corr()
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax, square=True)
ax.set_title("Correlation Matrix")
plt.tight_layout()
plt.savefig("reports/figures/data_evaluation_correlation.png", dpi=150)
plt.show()
```

---

## Output Checklist
After completing evaluation, produce a short written summary covering:

- [ ] Dataset dimensions and file source
- [ ] Columns with significant nulls (>5%) and recommended action
- [ ] Columns that appear to be IDs / should be excluded from modelling
- [ ] Suspected data-type mismatches (e.g. numeric stored as string)
- [ ] Columns with extreme outliers
- [ ] Key correlations to note for feature engineering
- [ ] Overall data quality rating: **Good / Needs Cleaning / Poor**

Save summary to `reports/outputs/<problem_case>_data_evaluation.md`.

---

## Conventions
- Always print shape before and after any operation.
- Do not modify `data/raw/` — this step is read-only.
- Log findings with `logging.info(...)`, not `print()`, in production scripts.
