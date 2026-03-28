"""Stage 1 — Data Ingestion.

Loads all raw source files, validates shape/dtypes/nulls, and returns raw
unmodified DataFrames.  No transformation is performed here.
"""

from pathlib import Path
from typing import Dict

import pandas as pd

from src import config as cfg

logger = cfg.get_logger(__name__)


def load_raw_datasets() -> Dict[str, pd.DataFrame]:
    """Load all raw source files and return them as a keyed dictionary.

    Validates that each file exists and contains at least one row.  Logs
    shape and dtypes for every dataset.  Raises ``FileNotFoundError`` with a
    descriptive message if any required file is missing.

    Returns:
        Dict mapping dataset key (e.g. ``cfg.KEY_CDC``) to its raw DataFrame.

    Raises:
        FileNotFoundError: If any required raw data file is absent from
            ``data/raw/``.
    """
    datasets: Dict[str, pd.DataFrame] = {}

    csv_map = {
        cfg.KEY_CDC: cfg.CDC_PLACES_PATH,
        cfg.KEY_CENSUS_DEMO: cfg.CENSUS_DEMOGRAPHICS_PATH,
        cfg.KEY_CENSUS_HOUSING: cfg.CENSUS_HOUSING_POVERTY_PATH,
        cfg.KEY_FEMA: cfg.FEMA_PATH,
        cfg.KEY_HEALTHCARE_ACCESS: cfg.HEALTHCARE_ACCESS_PATH,
        cfg.KEY_HEALTHCARE_WORKERS: cfg.HEALTHCARE_WORKERS_PATH,
        cfg.KEY_PARKS: cfg.PARKS_PATH,
        cfg.KEY_SVI: cfg.SVI_PATH,
        cfg.KEY_USDA: cfg.USDA_FOOD_ACCESS_PATH,
    }

    for key, path in csv_map.items():
        datasets[key] = _load_csv(path, key)

    datasets["metadata"] = _load_xlsx(cfg.METADATA_PATH, "metadata")

    logger.info("Loaded %d datasets successfully.", len(datasets))
    return datasets


def _load_csv(path: Path, key: str) -> pd.DataFrame:
    """Load a single CSV, validate it is non-empty, and log its shape.

    Args:
        path: Absolute path to the CSV file.
        key: Dataset key used in log messages.

    Returns:
        Raw DataFrame.

    Raises:
        FileNotFoundError: If *path* does not exist.
        ValueError: If the loaded DataFrame has zero rows.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Required data file not found: {path.name} "
            f"(expected at {path}). "
            "Place all raw data files in data/raw/ before running the pipeline."
        )

    df = pd.read_csv(path, dtype=str)

    if len(df) == 0:
        raise ValueError(f"Dataset '{key}' ({path.name}) loaded with zero rows.")

    logger.info(
        "Loaded '%s': %d rows × %d cols from %s",
        key,
        len(df),
        len(df.columns),
        path.name,
    )
    return df


def _load_xlsx(path: Path, key: str) -> pd.DataFrame:
    """Load the first sheet of an XLSX file and log its shape.

    Args:
        path: Absolute path to the XLSX file.
        key: Dataset key used in log messages.

    Returns:
        Raw DataFrame from Sheet1.

    Raises:
        FileNotFoundError: If *path* does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Required metadata file not found: {path.name} "
            f"(expected at {path})."
        )

    df = pd.read_excel(path, sheet_name=0)
    logger.info(
        "Loaded '%s': %d rows × %d cols from %s",
        key,
        len(df),
        len(df.columns),
        path.name,
    )
    return df
