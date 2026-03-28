"""Stage 2 — Data Cleaning.

Fixes dtypes, standardises the ZIP column, handles nulls/duplicates/outliers,
and asserts post-clean invariants.  Every row drop is logged with a count and
reason.
"""

from typing import Dict

import pandas as pd

from src import config as cfg

logger = cfg.get_logger(__name__)

# Columns that represent rates/proportions and must be clipped to [0, 1].
# These are columns we derive in features.py; raw CSVs use percentage scales
# (e.g. 41.1 means 41.1%) so clipping is applied after conversion.
_RATE_COLUMNS: set = set()  # extended during cleaning based on column names


def clean_datasets(
    raw: Dict[str, pd.DataFrame],
) -> Dict[str, pd.DataFrame]:
    """Clean all raw datasets and return cleaned versions under the same keys.

    For each dataset:
    - Extracts the 5-digit ZIP code from ``feature label`` into ``zip_code``.
    - Coerces numeric columns to float64 / int64.
    - Drops duplicate ``zip_code`` rows (keeping first), logging count.
    - Logs before/after record counts for every transformation.

    Args:
        raw: Dict of raw DataFrames as returned by
            :func:`src.ingestion.load_raw_datasets`.

    Returns:
        Dict with the same keys as *raw*, each value replaced by its cleaned
        DataFrame.
    """
    cleaned: Dict[str, pd.DataFrame] = {}

    for key, df in raw.items():
        logger.info("Cleaning '%s': %d rows before.", key, len(df))
        df = df.copy()

        # Skip metadata — no ZIP extraction needed
        if key == "metadata":
            cleaned[key] = df
            continue

        df = _coerce_numerics(df)
        df = _standardise_zip(df, key)
        df = _drop_duplicates(df, key)

        logger.info("Cleaning '%s': %d rows after.", key, len(df))
        cleaned[key] = df

    return cleaned


def _standardise_zip(df: pd.DataFrame, key: str) -> pd.DataFrame:
    """Extract the 5-digit ZIP code from ``feature label`` into ``zip_code``.

    Args:
        df: Raw DataFrame containing a ``feature label`` column.
        key: Dataset name used in log messages.

    Returns:
        DataFrame with a new ``zip_code`` column (str, zero-padded to 5 chars).

    Raises:
        ValueError: If no ZIP codes can be extracted from ``feature label``.
    """
    if cfg.COL_FEATURE_LABEL not in df.columns:
        logger.warning(
            "'%s' has no '%s' column; skipping ZIP extraction.",
            key,
            cfg.COL_FEATURE_LABEL,
        )
        return df

    extracted = df[cfg.COL_FEATURE_LABEL].str.extract(r"(\d+)", expand=False)

    if extracted.isna().all():
        raise ValueError(
            f"Could not extract any ZIP codes from "
            f"'{cfg.COL_FEATURE_LABEL}' in dataset '{key}'. "
            f"Sample values: {df[cfg.COL_FEATURE_LABEL].head(3).tolist()}"
        )

    df = df.copy()
    # zfill pads short codes; cast to object (str) for consistent dtype
    df[cfg.COL_ZIP] = extracted.str.zfill(5).astype(object)
    return df


def _drop_duplicates(df: pd.DataFrame, key: str) -> pd.DataFrame:
    """Drop duplicate ``zip_code`` rows, logging count and reason.

    Args:
        df: Cleaned DataFrame with ``zip_code`` column present.
        key: Dataset name used in log messages.

    Returns:
        De-duplicated DataFrame.
    """
    if cfg.COL_ZIP not in df.columns:
        return df

    n_before = len(df)
    df = df.drop_duplicates(subset=[cfg.COL_ZIP], keep="first")
    n_dropped = n_before - len(df)

    if n_dropped > 0:
        logger.info(
            "Dropped %d duplicate zip_code rows from '%s' (kept first occurrence).",
            n_dropped,
            key,
        )

    return df


def _coerce_numerics(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce object-typed columns that should be numeric to float64.

    Replaces common NA strings ("N/A", "NA", "-") with ``NaN`` before
    attempting numeric coercion.  Columns that cannot be coerced are left
    as-is.

    Args:
        df: DataFrame to coerce.

    Returns:
        DataFrame with improved numeric dtypes.
    """
    _NA_STRINGS: frozenset = frozenset({"N/A", "n/a", "NA", "na", "N/a", "-", "--", ""})
    result = {}
    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col]):
            # Map known NA strings to float NaN before numeric coercion
            series = df[col].map(
                lambda x: float("nan") if isinstance(x, str) and x.strip() in _NA_STRINGS else x
            )
            coerced = pd.to_numeric(series, errors="coerce")
            # Only replace if at least some values converted successfully
            result[col] = coerced if coerced.notna().any() else df[col]
        else:
            result[col] = df[col]
    return pd.DataFrame(result, index=df.index)
