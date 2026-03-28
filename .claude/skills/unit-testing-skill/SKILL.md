# Skill: Unit Testing

## Purpose
Write rigorous, fast, isolated unit tests for functions in `src/` using `pytest`. Tests serve as living documentation and a safety net for refactoring.

## When to Use
- Immediately after writing any function in `src/`
- When fixing a bug — write a test that reproduces it first
- When refactoring — ensure tests pass before and after

---

## Setup

```bash
# Install
pip install pytest pytest-cov

# Run all unit tests
pytest tests/ -v --ignore=tests/e2e

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
```

Directory structure:
```
tests/
├── conftest.py              ← Shared fixtures
├── test_cleaning.py         ← Tests for src/cleaning.py
├── test_features.py         ← Tests for src/features.py
├── test_evaluation.py       ← Tests for src/evaluation.py
├── test_visualisation.py    ← Tests for src/visualisation.py
└── e2e/                     ← End-to-end tests (separate skill)
```

---

## Golden Rules

1. **One assertion concept per test.** Split complex tests into smaller ones.
2. **Tests must be deterministic.** Set seeds; never rely on random default behaviour.
3. **Never load real data files.** Use synthetic `pd.DataFrame` fixtures.
4. **Tests must be fast.** Each test should complete in < 1 second.
5. **Test the contract, not the implementation.** Test inputs → outputs, not internal logic.
6. **Name tests descriptively.** `test_clean_nulls_fills_with_median_not_mean`.

---

## conftest.py — Shared Fixtures

```python
# tests/conftest.py
import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def sample_df() -> pd.DataFrame:
    """A small generic DataFrame for general-purpose tests."""
    return pd.DataFrame({
        "id":       [1, 2, 3, 4, 5],
        "value":    [10.0, 20.0, np.nan, 40.0, 50.0],
        "category": ["A", "B", "A", None, "C"],
        "date":     pd.to_datetime(["2023-01-01", "2023-01-02",
                                    "2023-01-03", "2023-01-04", "2023-01-05"]),
    })

@pytest.fixture
def df_no_nulls() -> pd.DataFrame:
    return pd.DataFrame({
        "revenue":  [100.0, 200.0, 300.0],
        "expenses": [80.0,  150.0, 250.0],
        "org_type": ["Nonprofit", "Nonprofit", "Government"],
    })

@pytest.fixture
def df_with_duplicates() -> pd.DataFrame:
    return pd.DataFrame({
        "id":    [1, 2, 2, 3],
        "value": [10, 20, 20, 30],
    })
```

---

## Test Patterns

### Pattern 1 — Happy Path (correct inputs → correct outputs)
```python
# tests/test_cleaning.py
import pandas as pd
import numpy as np
from src.cleaning import fill_numeric_nulls_with_median


def test_fill_numeric_nulls_returns_no_nulls(sample_df):
    result = fill_numeric_nulls_with_median(sample_df, col="value")
    assert result["value"].isnull().sum() == 0, "Nulls should be filled"


def test_fill_numeric_nulls_uses_median_not_mean():
    df = pd.DataFrame({"x": [1.0, 2.0, 100.0, np.nan]})  # median=2, mean=34.3
    result = fill_numeric_nulls_with_median(df, col="x")
    assert result["x"].iloc[-1] == pytest.approx(2.0), "Should fill with median=2"


def test_fill_numeric_nulls_does_not_mutate_input(sample_df):
    original_null_count = sample_df["value"].isnull().sum()
    _ = fill_numeric_nulls_with_median(sample_df, col="value")
    assert sample_df["value"].isnull().sum() == original_null_count, \
        "Original DataFrame should not be mutated"
```

### Pattern 2 — Edge Cases
```python
def test_fill_numeric_nulls_empty_dataframe():
    df = pd.DataFrame({"x": pd.Series([], dtype=float)})
    result = fill_numeric_nulls_with_median(df, col="x")
    assert len(result) == 0

def test_fill_numeric_nulls_all_null_column():
    df = pd.DataFrame({"x": [np.nan, np.nan, np.nan]})
    # All-null median is NaN — function should handle gracefully (not raise)
    result = fill_numeric_nulls_with_median(df, col="x")
    assert isinstance(result, pd.DataFrame)
```

### Pattern 3 — Error Handling
```python
import pytest

def test_fill_numeric_nulls_raises_on_missing_column(sample_df):
    with pytest.raises(KeyError, match="nonexistent"):
        fill_numeric_nulls_with_median(sample_df, col="nonexistent")

def test_clean_df_raises_on_empty_input():
    with pytest.raises(ValueError, match="empty"):
        clean_df(pd.DataFrame())
```

### Pattern 4 — Output Shape & Schema
```python
def test_drop_duplicates_reduces_row_count(df_with_duplicates):
    from src.cleaning import drop_full_duplicates
    result = drop_full_duplicates(df_with_duplicates)
    assert len(result) < len(df_with_duplicates)
    assert len(result) == 3  # [1,2,3] unique rows

def test_feature_engineering_adds_expected_columns(df_no_nulls):
    from src.features import add_profit_margin
    result = add_profit_margin(df_no_nulls)
    assert "profit_margin" in result.columns
    assert result.shape[1] == df_no_nulls.shape[1] + 1
```

### Pattern 5 — Numeric Precision
```python
def test_profit_margin_calculation():
    df = pd.DataFrame({"revenue": [200.0], "expenses": [150.0]})
    from src.features import add_profit_margin
    result = add_profit_margin(df)
    # margin = (200 - 150) / 200 = 0.25
    assert result["profit_margin"].iloc[0] == pytest.approx(0.25, rel=1e-6)
```

### Pattern 6 — Parametrize for Multiple Cases
```python
@pytest.mark.parametrize("revenue,expenses,expected_margin", [
    (200.0, 150.0, 0.25),
    (100.0, 100.0, 0.00),
    (100.0,   0.0, 1.00),
])
def test_profit_margin_parametrized(revenue, expenses, expected_margin):
    df = pd.DataFrame({"revenue": [revenue], "expenses": [expenses]})
    from src.features import add_profit_margin
    result = add_profit_margin(df)
    assert result["profit_margin"].iloc[0] == pytest.approx(expected_margin)
```

---

## Coverage Requirements

| Module | Minimum Coverage |
|---|---|
| `src/cleaning.py` | 90% |
| `src/features.py` | 85% |
| `src/evaluation.py` | 80% |
| Overall | 80% |

Run and check:
```bash
pytest tests/ --cov=src --cov-fail-under=80
```

---

## Naming Convention

```
test_<function_name>_<scenario>_<expected_outcome>

Examples:
  test_fill_nulls_with_all_nulls_returns_unchanged_shape
  test_encode_categories_raises_on_unknown_value
  test_drop_duplicates_preserves_first_occurrence
```

---

## Conventions
- Use `pytest.approx()` for all floating-point comparisons — never `==` on floats.
- Fixtures go in `conftest.py`, not duplicated across test files.
- No test should have a `time.sleep()` or network call.
- Tag slow tests: `@pytest.mark.slow` and exclude from default run with `-m "not slow"`.
