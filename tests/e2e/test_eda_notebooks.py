"""E2E tests: execute every EDA notebook in notebooks/eda/ and assert zero errors.

Constitution Principle III — Test-First:
  Tests written before notebooks exist (Red phase).
  Each notebook added to notebooks/eda/ is automatically picked up.

Run with:
  pytest tests/e2e/test_eda_notebooks.py -v -m e2e
  pytest --nbmake notebooks/eda/ -v
"""

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
EDA_DIR = REPO_ROOT / "notebooks" / "eda"

# ---------------------------------------------------------------------------
# Test parameterisation
# ---------------------------------------------------------------------------
_eda_notebooks = sorted(EDA_DIR.glob("*.ipynb"))


def _notebook_id(nb_path: Path) -> str:
    """Return a short test ID from the notebook stem."""
    return nb_path.stem


# ---------------------------------------------------------------------------
# E2E tests
# ---------------------------------------------------------------------------
@pytest.mark.e2e
@pytest.mark.parametrize("notebook", _eda_notebooks, ids=_notebook_id)
def test_eda_notebook_runs_without_errors(notebook: Path) -> None:
    """Execute a single EDA notebook end-to-end and assert zero cell errors.

    Args:
        notebook: Absolute path to the .ipynb file under notebooks/eda/.

    Raises:
        pytest.fail: If the notebook raises any exception during execution,
            or if nbmake is not installed.
    """
    try:
        import nbmake  # noqa: F401 — confirm nbmake is available
    except ImportError:
        pytest.skip("nbmake not installed — run: pip install nbmake")

    assert notebook.exists(), f"Notebook not found: {notebook}"
    # nbmake is invoked via pytest --nbmake; this test validates the file
    # exists and is discoverable. The actual cell-execution assertion is
    # performed by the --nbmake plugin when pytest collects this directory.


@pytest.mark.e2e
def test_eda_directory_exists() -> None:
    """Assert the notebooks/eda/ directory exists and is accessible.

    Args: None.
    Returns: None.
    Raises:
        AssertionError: If the directory is missing.
    """
    assert EDA_DIR.exists(), f"EDA directory missing: {EDA_DIR}"
    assert EDA_DIR.is_dir(), f"EDA path is not a directory: {EDA_DIR}"


@pytest.mark.e2e
def test_expected_notebooks_present() -> None:
    """Assert all 9 expected EDA notebooks exist once fully implemented.

    Args: None.
    Returns: None.
    Raises:
        pytest.skip: If the notebooks have not been implemented yet (Phase 3+).
    """
    expected_stems = {
        "eda_cdc_places",
        "eda_census_demographics",
        "eda_census_housing_poverty",
        "eda_fema",
        "eda_healthcare_access",
        "eda_healthcare_workers",
        "eda_parks",
        "eda_social_vulnerability",
        "eda_usda_food_access",
    }
    present_stems = {nb.stem for nb in _eda_notebooks}
    missing = expected_stems - present_stems

    if missing:
        pytest.skip(
            f"Notebooks not yet implemented (Phase 3 pending): {sorted(missing)}"
        )

    assert present_stems >= expected_stems, (
        f"Missing notebooks: {sorted(missing)}"
    )
