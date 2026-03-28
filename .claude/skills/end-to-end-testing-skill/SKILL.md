# Skill: End-to-End Testing

## Purpose
Validate that the entire data pipeline — from raw file ingestion through cleaning, feature engineering, modelling, and reporting — produces correct, reproducible outputs when run as a whole.

## When to Use
- Before finalising a problem-case solution
- After any significant refactor of pipeline code
- As a smoke test to confirm the pipeline runs in a clean environment
- To validate that outputs match expected benchmarks

## Distinction from Unit Tests
| | Unit Tests | End-to-End Tests |
|---|---|---|
| Scope | Single function | Full pipeline |
| Data | Synthetic fixtures | Real (or realistic) data |
| Speed | < 1s each | Minutes acceptable |
| Location | `tests/` | `tests/e2e/` |
| Tag | *(default)* | `@pytest.mark.e2e` |

---

## Setup

```bash
# Install dependencies
pip install pytest pytest-cov

# Run only e2e tests
pytest tests/e2e/ -v -m e2e

# Run everything (unit + e2e)
pytest tests/ -v

# Skip e2e in fast CI runs
pytest tests/ -v -m "not e2e"
```

Register the custom marker in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
markers = [
    "e2e: end-to-end pipeline tests using real or near-real data",
    "slow: tests expected to run longer than 10 seconds",
]
```

---

## Fixtures for E2E Tests

```python
# tests/e2e/conftest.py
import pytest
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

@pytest.fixture(scope="session")
def raw_data_path() -> dict[str, Path]:
    """Return paths to all raw data files, asserting they exist."""
    paths = {
        "case1": RAW_DIR / "Duval_StJohns.csv",
        "case2_reg":  RAW_DIR / "VoterRegistrationComp",
        "case2_hist": RAW_DIR / "VotingHistoryComp",
        "case3": RAW_DIR / "Police_involved.xlsx",
    }
    for name, path in paths.items():
        assert path.exists(), f"Raw data missing for {name}: {path}"
    return paths

@pytest.fixture(scope="session")
def processed_case1(raw_data_path) -> pd.DataFrame:
    """Run the Case 1 cleaning pipeline and return the result."""
    from src.case1.pipeline import run_cleaning_pipeline
    return run_cleaning_pipeline(raw_data_path["case1"])
```

---

## E2E Test Templates

### Template 1 — Pipeline Smoke Test
Verifies the pipeline runs without errors and returns a non-empty DataFrame.

```python
# tests/e2e/test_case1_pipeline.py
import pytest
import pandas as pd
from pathlib import Path

pytestmark = pytest.mark.e2e


def test_case1_pipeline_runs_without_error(raw_data_path):
    """Full Case 1 pipeline should complete without exceptions."""
    from src.case1.pipeline import run_full_pipeline
    result = run_full_pipeline(raw_data_path["case1"])
    assert result is not None


def test_case1_pipeline_returns_dataframe(raw_data_path):
    from src.case1.pipeline import run_full_pipeline
    result = run_full_pipeline(raw_data_path["case1"])
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0, "Pipeline output must not be empty"
```

### Template 2 — Schema Contract
Verifies the output has the expected columns and types.

```python
EXPECTED_OUTPUT_COLUMNS = {
    "org_name":       "object",
    "fiscal_year":    "int64",
    "revenue":        "float64",
    "expenses":       "float64",
    "profit_margin":  "float64",
    "stability_flag": "bool",
}

def test_case1_output_schema(processed_case1):
    """Pipeline output must have the required columns and types."""
    for col, expected_dtype in EXPECTED_OUTPUT_COLUMNS.items():
        assert col in processed_case1.columns, f"Missing column: {col}"
        actual_dtype = str(processed_case1[col].dtype)
        assert actual_dtype == expected_dtype, \
            f"Column '{col}': expected {expected_dtype}, got {actual_dtype}"
```

### Template 3 — Data Quality Post-Pipeline
Verifies business-level invariants hold after the full pipeline.

```python
def test_case1_no_nulls_in_output(processed_case1):
    null_counts = processed_case1.isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0]
    assert len(cols_with_nulls) == 0, \
        f"Nulls found in output columns: {cols_with_nulls.to_dict()}"


def test_case1_revenue_is_non_negative(processed_case1):
    assert (processed_case1["revenue"] >= 0).all(), \
        "Revenue must be non-negative after cleaning"


def test_case1_profit_margin_in_valid_range(processed_case1):
    margins = processed_case1["profit_margin"]
    assert margins.between(-1.0, 1.0).all(), \
        "Profit margin must be between -1.0 and 1.0"


def test_case1_row_count_within_expected_range(processed_case1):
    # Adjust lower/upper based on known data characteristics
    assert 50 <= len(processed_case1) <= 10_000, \
        f"Unexpected row count: {len(processed_case1)}"
```

### Template 4 — Reproducibility
Verifies that running the pipeline twice gives identical results.

```python
def test_case1_pipeline_is_reproducible(raw_data_path):
    """Two runs of the pipeline must produce identical outputs."""
    from src.case1.pipeline import run_full_pipeline
    result_1 = run_full_pipeline(raw_data_path["case1"])
    result_2 = run_full_pipeline(raw_data_path["case1"])
    pd.testing.assert_frame_equal(
        result_1.reset_index(drop=True),
        result_2.reset_index(drop=True),
        check_like=False,
    )
```

### Template 5 — Model Performance Regression Guard
Verifies that model metrics don't degrade below an accepted baseline.

```python
MINIMUM_ACCEPTABLE_METRICS = {
    "accuracy": 0.70,
    "f1":       0.65,
    "roc_auc":  0.75,
}

def test_case2_model_metrics_above_baseline(raw_data_path):
    from src.case2.pipeline import run_model_pipeline
    metrics = run_model_pipeline(raw_data_path["case2_reg"], raw_data_path["case2_hist"])

    for metric, min_val in MINIMUM_ACCEPTABLE_METRICS.items():
        assert metric in metrics, f"Missing metric: {metric}"
        assert metrics[metric] >= min_val, \
            f"Metric '{metric}' regressed: {metrics[metric]:.4f} < {min_val}"
```

### Template 6 — Output Files Written
Verifies that all expected output files are created by the pipeline.

```python
def test_case1_pipeline_writes_output_files(tmp_path, raw_data_path):
    """Pipeline should write processed data and report files."""
    from src.case1.pipeline import run_full_pipeline
    run_full_pipeline(raw_data_path["case1"], output_dir=tmp_path)

    expected_files = [
        "case1_cleaned.parquet",
        "case1_evaluation.md",
    ]
    for filename in expected_files:
        output_path = tmp_path / filename
        assert output_path.exists(), f"Expected output file not created: {filename}"
        assert output_path.stat().st_size > 0, f"Output file is empty: {filename}"
```

---

## E2E Test Checklist

Before marking a problem case as complete, verify:

- [ ] Smoke test: pipeline runs end-to-end without exceptions
- [ ] Schema test: output columns and dtypes match contract
- [ ] Null test: no unexpected nulls in output
- [ ] Business invariants: domain-specific value range checks pass
- [ ] Reproducibility: two identical runs produce identical results
- [ ] Output files: all required output files are created and non-empty
- [ ] Model metrics: performance meets or exceeds baseline thresholds (if applicable)

---

## Conventions
- Use `tmp_path` (pytest built-in) for file output tests — never write to `data/` in tests.
- All e2e tests must be tagged `@pytest.mark.e2e` so they can be excluded from fast runs.
- E2E tests may be slow — document expected runtime in the test module docstring.
- Do not assert on exact numeric values from ML models — use `>=` thresholds.
- If a pipeline step is non-deterministic, fix the seed and assert on a deterministic output property (e.g. row count, column presence) rather than exact values.
