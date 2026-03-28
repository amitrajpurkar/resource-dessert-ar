# Skill: Code Review

## Purpose
Review Python data-science code for correctness, quality, readability, maintainability, and adherence to project conventions defined in `CLAUDE.md`. Produce a structured, actionable review.

## When to Use
- Before merging any code into a shared branch
- After writing a new module or pipeline script
- When refactoring existing code

---

## Review Dimensions

Apply all six dimensions below to every code review:

---

### 1. Correctness & Logic
Verify the code does what it claims to do.

**Check for:**
- Off-by-one errors in slicing or indexing
- Incorrect aggregation axis (`axis=0` vs `axis=1`)
- DataFrame mutations on views (use `.copy()` where needed)
- Silent type coercions (e.g. int/float mismatch in pandas)
- Train/test leakage — transformations fitted on test data
- Incorrect metric usage (e.g. accuracy on imbalanced classes)
- Missing `random_state` / seed on stochastic operations

**Flag with:** `[BUG]` or `[LOGIC]`

---

### 2. Code Style & PEP 8
```
[STYLE] Variable names should be snake_case
[STYLE] Line length must not exceed 88 characters (black default)
[STYLE] Imports should be grouped: stdlib → third-party → local, separated by blank lines
[STYLE] No wildcard imports: `from pandas import *` is forbidden
[STYLE] Magic numbers must be named constants: MAX_NULL_PCT = 0.60
```

Check that black and ruff pass without errors:
```bash
black --check src/ tests/
ruff check src/ tests/
```

---

### 3. Documentation
Every public function must have a docstring. Template to enforce:

```python
def clean_revenue(df: pd.DataFrame, col: str = "revenue") -> pd.DataFrame:
    """
    Remove nulls and cap outliers in the revenue column.

    Args:
        df:  Input DataFrame. Must contain `col`.
        col: Name of the revenue column. Defaults to "revenue".

    Returns:
        DataFrame with `col` cleaned in-place (copy returned).

    Raises:
        KeyError: If `col` is not present in `df`.
    """
```

**Flag with:** `[DOC]` when docstring is missing, incomplete, or inaccurate.

---

### 4. Type Hints
All function signatures must have full type hints.

```python
# BAD
def process(data, threshold):
    ...

# GOOD
def process(data: pd.DataFrame, threshold: float = 0.05) -> pd.DataFrame:
    ...
```

Use `from __future__ import annotations` at top of file for forward references.
Use `list[str]` not `List[str]` (Python 3.10+ style).

**Flag with:** `[TYPES]`

---

### 5. Data-Science Specific Anti-Patterns

| Anti-Pattern | Correct Approach | Flag |
|---|---|---|
| `df["col"].fillna(df["col"].mean())` on full dataset before split | Fit imputer on train, transform both | `[LEAKAGE]` |
| Single train/test split for model eval | `cross_val_score` or k-fold CV | `[EVAL]` |
| `accuracy_score` on imbalanced target | `f1_score`, `roc_auc_score` | `[METRIC]` |
| Hardcoded file paths (`"/home/user/data.csv"`) | `pathlib.Path` + config | `[PATH]` |
| `print()` for runtime messages | `logging.info()` | `[LOG]` |
| `df = df.append(row)` (deprecated) | `pd.concat([df, row_df])` | `[DEPRECATED]` |
| No seed on `train_test_split` or model init | Add `random_state=42` | `[REPRO]` |
| Fitting on `df` then selecting features | Select features before fitting | `[LEAKAGE]` |

---

### 6. Testability
- Functions with side effects (file I/O, network) should be isolated / injectable
- Pure transformation functions should be easily unit-testable
- No logic buried inside `if __name__ == "__main__"` blocks — extract to functions

**Flag with:** `[TEST]`

---

## Review Output Format

Produce a structured review using this template:

```markdown
## Code Review — `src/<module_name>.py`
**Reviewer:** Claude
**Date:** <date>
**Overall:** ✅ Approved / ⚠️ Approve with Changes / ❌ Needs Rework

---

### Summary
<2–3 sentence overall assessment>

### Issues

| Severity | Line(s) | Type | Description |
|---|---|---|---|
| 🔴 Critical | 42 | [BUG] | DataFrame view mutation — use `.copy()` |
| 🟡 Warning  | 15 | [LEAKAGE] | Scaler fitted before train/test split |
| 🔵 Minor    | 8  | [DOC] | Missing docstring on `encode_categories` |
| 🔵 Minor    | 67 | [STYLE] | Line exceeds 88 characters |

### Positive Observations
- ...

### Recommended Changes
1. ...
2. ...
```

Severity guide:
- 🔴 **Critical** — Incorrect results, data leakage, crashes. Must fix before proceeding.
- 🟡 **Warning** — Poor practice, risk of errors at scale. Should fix.
- 🔵 **Minor** — Style, docs, naming. Fix before final submission.

---

## Conventions
- Always run automated checks first (`black`, `ruff`) — don't manually flag style issues the linter catches.
- Be specific: cite line numbers, quote the problematic code, and provide a corrected version.
- Acknowledge good patterns alongside issues — this is a learning tool, not just a fault-finder.
