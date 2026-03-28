"""Stage 3 — Feature Engineering.

Merges cleaned datasets, constructs the demand-weighted Resource Desert Score,
and provides helper functions for category filtering and correlation analysis.
"""

from pathlib import Path
from typing import Dict

import pandas as pd

from src import config as cfg

logger = cfg.get_logger(__name__)

_VALID_CATEGORIES = {"healthcare", "food_access", "parks", "insurance"}

_CATEGORY_TO_GAP_COL = {
    "healthcare": cfg.COL_SUPPLY_GAP_HEALTHCARE,
    "food_access": cfg.COL_SUPPLY_GAP_FOOD,
    "parks": cfg.COL_SUPPLY_GAP_PARKS,
    "insurance": cfg.COL_SUPPLY_GAP_INSURANCE,
}


def merge_datasets(cleaned: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Outer-join all cleaned datasets on ``zip_code`` into one wide table.

    Steps:
    1. Outer-join on ``zip_code`` across all 9 datasets.
    2. Derive ``poverty_rate``, ``uninsured_rate``, ``food_low_access_pct``.
    3. Exclude ZIPs with ``Total Population == 0``; log count.
    4. Impute null supply metrics with column median; log imputation count.
    5. Save result to ``data/processed/merged_jacksonville.csv``.

    Args:
        cleaned: Dict of cleaned DataFrames from
            :func:`src.cleaning.clean_datasets`.

    Returns:
        Wide merged DataFrame with one row per ZIP code.
    """
    # Collect per-dataset subsets with only the columns we need
    frames = []

    def _subset(key: str, cols: list) -> pd.DataFrame:
        df = cleaned.get(key)
        if df is None:
            return pd.DataFrame(columns=[cfg.COL_ZIP] + cols)
        available = [c for c in [cfg.COL_ZIP] + cols if c in df.columns]
        return df[available].copy()

    frames.append(_subset(cfg.KEY_CENSUS_DEMO, [cfg.COL_TOTAL_POPULATION]))
    frames.append(
        _subset(
            cfg.KEY_CENSUS_HOUSING,
            [cfg.COL_POVERTY_COUNT, cfg.COL_MEDIAN_INCOME, cfg.COL_HOUSING_COST_BURDEN],
        )
    )
    frames.append(
        _subset(
            cfg.KEY_CDC,
            [
                cfg.COL_POOR_MENTAL_HEALTH,
                cfg.COL_OBESITY,
                cfg.COL_NO_PHYSICAL_ACTIVITY,
                cfg.COL_LIFE_EXPECTANCY,
            ],
        )
    )
    frames.append(
        _subset(
            cfg.KEY_HEALTHCARE_WORKERS,
            [cfg.COL_PRIMARY_CARE_RATIO, cfg.COL_NP_RATIO, cfg.COL_CHILD_CARE_CENTERS],
        )
    )
    frames.append(
        _subset(
            cfg.KEY_HEALTHCARE_ACCESS,
            [cfg.COL_UNINSURED_COUNT, cfg.COL_INSURED_COUNT, cfg.COL_MENTAL_HEALTH_PROVIDERS],
        )
    )
    frames.append(
        _subset(cfg.KEY_PARKS, [cfg.COL_PARK_COUNT, cfg.COL_PARK_COVERAGE_PCT, cfg.COL_PARK_AREA_ACRES])
    )
    frames.append(
        _subset(
            cfg.KEY_USDA,
            [cfg.COL_FOOD_LOW_ACCESS_1_MILE, cfg.COL_FOOD_LOW_ACCESS_20_MILE, cfg.COL_FOOD_LOW_INCOME],
        )
    )
    frames.append(_subset(cfg.KEY_SVI, [cfg.COL_SVI_SCORE, cfg.COL_SVI_VULNERABLE_FACTORS]))
    frames.append(
        _subset(cfg.KEY_FEMA, [cfg.COL_FEMA_RESILIENCE, cfg.COL_FEMA_ANNUAL_LOSS, cfg.COL_FEMA_SOCIAL_VULN])
    )

    # Outer-join iteratively on zip_code
    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on=cfg.COL_ZIP, how="outer")

    logger.info("Merged all datasets: %d rows before population filter.", len(merged))

    # Exclude ZIPs with zero or missing population
    if cfg.COL_TOTAL_POPULATION in merged.columns:
        merged[cfg.COL_TOTAL_POPULATION] = pd.to_numeric(
            merged[cfg.COL_TOTAL_POPULATION], errors="coerce"
        )
        n_before = len(merged)
        merged = merged[merged[cfg.COL_TOTAL_POPULATION].fillna(0) > 0].copy()
        n_dropped = n_before - len(merged)
        if n_dropped > 0:
            logger.info(
                "Dropped %d ZIPs with population == 0 or missing population.", n_dropped
            )

    # Derive rates
    pop = merged[cfg.COL_TOTAL_POPULATION]

    if cfg.COL_POVERTY_COUNT in merged.columns:
        merged[cfg.COL_POVERTY_RATE] = (
            pd.to_numeric(merged[cfg.COL_POVERTY_COUNT], errors="coerce") / pop
        ).clip(0.0, 1.0)

    if cfg.COL_UNINSURED_COUNT in merged.columns:
        merged[cfg.COL_UNINSURED_RATE] = (
            pd.to_numeric(merged[cfg.COL_UNINSURED_COUNT], errors="coerce") / pop
        ).clip(0.0, 1.0)

    food_col = cfg.COL_FOOD_LOW_ACCESS_20_MILE
    if food_col in merged.columns:
        merged[cfg.COL_FOOD_LOW_ACCESS_PCT] = (
            pd.to_numeric(merged[food_col], errors="coerce") / pop
        ).clip(0.0, 1.0)

    # Impute null supply metrics with column median
    supply_cols = [
        cfg.COL_PRIMARY_CARE_RATIO,
        cfg.COL_FOOD_LOW_ACCESS_PCT,
        cfg.COL_PARK_COVERAGE_PCT,
        cfg.COL_UNINSURED_RATE,
        cfg.COL_POVERTY_RATE,
        cfg.COL_POOR_MENTAL_HEALTH,
        cfg.COL_OBESITY,
    ]
    for col in supply_cols:
        if col not in merged.columns:
            continue
        n_null = merged[col].isna().sum()
        if n_null > 0:
            median_val = merged[col].median()
            merged[col] = merged[col].fillna(median_val)
            logger.info("Imputed %d nulls in '%s' with median %.4f.", n_null, col, median_val)

    # Save processed file
    cfg.DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    merged.to_csv(cfg.MERGED_DATA_PATH, index=False)
    logger.info("Saved merged dataset: %d rows → %s", len(merged), cfg.MERGED_DATA_PATH)

    return merged.reset_index(drop=True)


def compute_desert_score(merged_df: pd.DataFrame) -> pd.DataFrame:
    """Compute the demand-weighted Resource Desert Score for each ZIP.

    Formula::

        supply_gap_healthcare = 1 - normalize(primary_care_ratio)
        supply_gap_food       = normalize(food_low_access_pct)
        supply_gap_parks      = 1 - normalize(park_coverage_pct)
        supply_gap_insurance  = normalize(uninsured_rate)

        disease_burden  = avg(poor_mental_health_pct/100, obesity_pct/100)
        demand_factor   = normalize(poverty_rate * disease_burden)

        raw_score    = (Σ supply_gap_i) * demand_factor
        desert_score = normalize(raw_score) * 100

    Ties in ``desert_rank`` are broken by descending ``poverty_rate``.

    Args:
        merged_df: Wide merged DataFrame from :func:`merge_datasets`.

    Returns:
        DataFrame with ``zip_code``, all supply gap / demand columns, and
        ``desert_score`` (0–100) plus ``desert_rank`` (1 = most underserved).
        Saved to ``reports/outputs/desert_scores.csv``.
    """
    df = merged_df.copy()

    # Ensure required columns are numeric
    for col in [
        cfg.COL_PRIMARY_CARE_RATIO,
        cfg.COL_FOOD_LOW_ACCESS_PCT,
        cfg.COL_PARK_COVERAGE_PCT,
        cfg.COL_UNINSURED_RATE,
        cfg.COL_POVERTY_RATE,
        cfg.COL_POOR_MENTAL_HEALTH,
        cfg.COL_OBESITY,
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Impute remaining nulls with median (safety net)
    for col in [cfg.COL_PRIMARY_CARE_RATIO, cfg.COL_PARK_COVERAGE_PCT]:
        if col in df.columns and df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())

    # Supply gaps (0 = no gap, 1 = maximum gap)
    if cfg.COL_PRIMARY_CARE_RATIO in df.columns:
        df[cfg.COL_SUPPLY_GAP_HEALTHCARE] = 1.0 - _minmax(df[cfg.COL_PRIMARY_CARE_RATIO])
    else:
        df[cfg.COL_SUPPLY_GAP_HEALTHCARE] = 0.0

    if cfg.COL_FOOD_LOW_ACCESS_PCT in df.columns:
        df[cfg.COL_SUPPLY_GAP_FOOD] = _minmax(df[cfg.COL_FOOD_LOW_ACCESS_PCT])
    else:
        df[cfg.COL_SUPPLY_GAP_FOOD] = 0.0

    if cfg.COL_PARK_COVERAGE_PCT in df.columns:
        df[cfg.COL_SUPPLY_GAP_PARKS] = 1.0 - _minmax(df[cfg.COL_PARK_COVERAGE_PCT])
    else:
        df[cfg.COL_SUPPLY_GAP_PARKS] = 0.0

    if cfg.COL_UNINSURED_RATE in df.columns:
        df[cfg.COL_SUPPLY_GAP_INSURANCE] = _minmax(df[cfg.COL_UNINSURED_RATE])
    else:
        df[cfg.COL_SUPPLY_GAP_INSURANCE] = 0.0

    # Demand factor
    poverty = df[cfg.COL_POVERTY_RATE] if cfg.COL_POVERTY_RATE in df.columns else pd.Series(0.0, index=df.index)
    mental_h = (df[cfg.COL_POOR_MENTAL_HEALTH] / 100.0) if cfg.COL_POOR_MENTAL_HEALTH in df.columns else pd.Series(0.0, index=df.index)
    obesity = (df[cfg.COL_OBESITY] / 100.0) if cfg.COL_OBESITY in df.columns else pd.Series(0.0, index=df.index)

    disease_burden = (mental_h + obesity) / 2.0
    df[cfg.COL_DISEASE_BURDEN] = disease_burden
    df[cfg.COL_DEMAND_FACTOR] = _minmax(poverty * disease_burden)

    # Raw and final score
    supply_sum = (
        df[cfg.COL_SUPPLY_GAP_HEALTHCARE]
        + df[cfg.COL_SUPPLY_GAP_FOOD]
        + df[cfg.COL_SUPPLY_GAP_PARKS]
        + df[cfg.COL_SUPPLY_GAP_INSURANCE]
    )
    raw_score = supply_sum * df[cfg.COL_DEMAND_FACTOR]
    df[cfg.COL_DESERT_SCORE] = (_minmax(raw_score) * 100.0).round(2)

    # Top gap category per ZIP
    gap_cols = {
        "healthcare": cfg.COL_SUPPLY_GAP_HEALTHCARE,
        "food_access": cfg.COL_SUPPLY_GAP_FOOD,
        "parks": cfg.COL_SUPPLY_GAP_PARKS,
        "insurance": cfg.COL_SUPPLY_GAP_INSURANCE,
    }
    gap_df = df[[v for v in gap_cols.values()]]
    gap_df.columns = list(gap_cols.keys())
    df[cfg.COL_TOP_GAP_CATEGORY] = gap_df.idxmax(axis=1)

    # Rank: 1 = most underserved; ties broken by poverty_rate descending
    df = df.sort_values(
        [cfg.COL_DESERT_SCORE, cfg.COL_POVERTY_RATE],
        ascending=[False, False],
    ).reset_index(drop=True)
    df[cfg.COL_DESERT_RANK] = range(1, len(df) + 1)

    # Select output columns
    score_cols = [
        cfg.COL_ZIP,
        cfg.COL_DESERT_SCORE,
        cfg.COL_DESERT_RANK,
        cfg.COL_DEMAND_FACTOR,
        cfg.COL_SUPPLY_GAP_HEALTHCARE,
        cfg.COL_SUPPLY_GAP_FOOD,
        cfg.COL_SUPPLY_GAP_PARKS,
        cfg.COL_SUPPLY_GAP_INSURANCE,
        cfg.COL_TOP_GAP_CATEGORY,
    ]
    # Add population and poverty for downstream use
    for extra in [cfg.COL_TOTAL_POPULATION, cfg.COL_POVERTY_RATE]:
        if extra in df.columns:
            score_cols.append(extra)

    scores_df = df[[c for c in score_cols if c in df.columns]].copy()

    cfg.REPORTS_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    scores_df.to_csv(cfg.DESERT_SCORES_PATH, index=False)
    logger.info(
        "Desert scores saved: %d ZIPs → %s", len(scores_df), cfg.DESERT_SCORES_PATH
    )

    return scores_df


def compute_health_outcome_correlation(merged_df: pd.DataFrame) -> pd.DataFrame:
    """Compute Pearson correlation between preventative assets and health outcomes.

    Args:
        merged_df: Wide merged DataFrame from :func:`merge_datasets`.

    Returns:
        DataFrame with columns ``asset``, ``outcome``, ``pearson_r`` for every
        asset × outcome combination.  All ``pearson_r`` values are in [-1, 1].
    """
    asset_cols = {
        "primary_care_ratio": cfg.COL_PRIMARY_CARE_RATIO,
        "food_low_access_pct": cfg.COL_FOOD_LOW_ACCESS_PCT,
        "park_coverage_pct": cfg.COL_PARK_COVERAGE_PCT,
        "uninsured_rate": cfg.COL_UNINSURED_RATE,
    }
    outcome_cols = {
        "poor_mental_health_pct": cfg.COL_POOR_MENTAL_HEALTH,
        "obesity_pct": cfg.COL_OBESITY,
    }

    rows = []
    for asset_name, asset_col in asset_cols.items():
        for outcome_name, outcome_col in outcome_cols.items():
            if asset_col not in merged_df.columns or outcome_col not in merged_df.columns:
                continue
            pair = merged_df[[asset_col, outcome_col]].dropna()
            if len(pair) < 3:
                logger.warning(
                    "Skipping correlation %s × %s: fewer than 3 valid rows.",
                    asset_name,
                    outcome_name,
                )
                continue
            r = pair[asset_col].corr(pair[outcome_col])
            rows.append({"asset": asset_name, "outcome": outcome_name, "pearson_r": round(r, 4)})
            logger.info("Correlation %s × %s: r = %.4f", asset_name, outcome_name, r)

    corr_df = pd.DataFrame(rows, columns=["asset", "outcome", "pearson_r"])
    return corr_df


def filter_by_service_category(
    desert_scores_df: pd.DataFrame,
    category: str,
) -> pd.DataFrame:
    """Return Desert Score DataFrame filtered and re-ranked for one category.

    Args:
        desert_scores_df: Full Desert Score DataFrame from
            :func:`compute_desert_score`.
        category: One of ``"healthcare"``, ``"food_access"``, ``"parks"``,
            ``"insurance"``.

    Returns:
        DataFrame with ZIP codes re-ranked by the chosen supply gap column.

    Raises:
        ValueError: If *category* is not one of the four valid values.
    """
    if category not in _VALID_CATEGORIES:
        raise ValueError(
            f"Invalid category '{category}'. "
            f"Must be one of: {sorted(_VALID_CATEGORIES)}"
        )

    gap_col = _CATEGORY_TO_GAP_COL[category]
    df = desert_scores_df.copy()

    if gap_col in df.columns:
        df = df.sort_values(gap_col, ascending=False).reset_index(drop=True)
        df[cfg.COL_DESERT_RANK] = range(1, len(df) + 1)

    return df


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _minmax(series: pd.Series) -> pd.Series:
    """Min-max normalise a Series to [0, 1].

    If ``max == min`` (constant series), returns a zero-filled Series.

    Args:
        series: Numeric pandas Series.

    Returns:
        Normalised Series in [0.0, 1.0].
    """
    mn = series.min()
    mx = series.max()
    if mx == mn:
        return pd.Series(0.0, index=series.index)
    return (series - mn) / (mx - mn)
