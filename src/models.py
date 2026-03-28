"""Stage 4 — Gap-Closure Simulation (Optimization Model).

Simulates adding each resource type to the top-N most underserved ZIP codes
and identifies the single highest-impact intervention.
"""

import random

import numpy as np
import pandas as pd

from src import config as cfg

logger = cfg.get_logger(__name__)

# The four resource types the simulation considers.
RESOURCE_TYPES = ["primary_care", "food_access", "parks", "insurance_outreach"]

# Maps each resource type to its supply gap column in desert_scores_df.
# The gap is in [0, 1] where 1 = maximum deprivation.
_RESOURCE_TO_GAP_COL = {
    "primary_care": cfg.COL_SUPPLY_GAP_HEALTHCARE,
    "food_access": cfg.COL_SUPPLY_GAP_FOOD,
    "parks": cfg.COL_SUPPLY_GAP_PARKS,
    "insurance_outreach": cfg.COL_SUPPLY_GAP_INSURANCE,
}

_ALL_GAP_COLS = list(_RESOURCE_TO_GAP_COL.values())


def run_gap_closure_simulation(
    desert_scores_df: pd.DataFrame,
    merged_df: pd.DataFrame,
    top_n: int = 5,
) -> pd.DataFrame:
    """Simulate setting each supply gap to its 25th-percentile value for the top-N ZIPs.

    For each of the *top_n* most underserved ZIPs and each of the 4 resource
    types, sets the corresponding normalised supply gap to the 25th percentile
    of that gap across all ZIPs (i.e. the level where 75% of ZIPs currently do
    better), recomputes the Desert Score proportionally, and records the delta.

    The simulation never worsens a score: if a ZIP's gap is already at or below
    the 25th-percentile target, improvement is 0 for that resource type.

    ``is_highest_impact`` is ``False`` for all rows until
    :func:`rank_interventions` is called.

    Args:
        desert_scores_df: Full Desert Score DataFrame from
            :func:`src.features.compute_desert_score`.
        merged_df: Wide merged DataFrame from
            :func:`src.features.merge_datasets`.
        top_n: Number of most underserved ZIPs to simulate.  Defaults to 5.

    Returns:
        DataFrame with ``top_n * 4`` rows and columns: ``zip_code``,
        ``resource_type``, ``current_desert_score``,
        ``simulated_desert_score``, ``score_improvement``,
        ``pct_improvement``, ``population_impacted``,
        ``is_highest_impact`` (all ``False``).
    """
    np.random.seed(42)
    random.seed(42)

    # Identify top-N ZIPs (rank 1 = most underserved)
    top_zips = (
        desert_scores_df.nsmallest(top_n, cfg.COL_DESERT_RANK)[cfg.COL_ZIP].tolist()
    )

    # Pre-compute 25th-percentile target for each supply gap column
    p25_targets = {
        col: float(desert_scores_df[col].quantile(0.25))
        for col in _ALL_GAP_COLS
        if col in desert_scores_df.columns
    }

    # Population lookup
    pop_lookup: dict = {}
    if cfg.COL_TOTAL_POPULATION in merged_df.columns:
        pop_lookup = (
            merged_df.set_index(cfg.COL_ZIP)[cfg.COL_TOTAL_POPULATION]
            .to_dict()
        )
    elif cfg.COL_TOTAL_POPULATION in desert_scores_df.columns:
        pop_lookup = (
            desert_scores_df.set_index(cfg.COL_ZIP)[cfg.COL_TOTAL_POPULATION]
            .to_dict()
        )

    rows = []
    for zip_code in top_zips:
        zip_row = desert_scores_df[desert_scores_df[cfg.COL_ZIP] == zip_code].iloc[0]
        current_score = float(zip_row[cfg.COL_DESERT_SCORE])
        demand_factor = float(zip_row.get(cfg.COL_DEMAND_FACTOR, 0.0))
        population = int(pop_lookup.get(zip_code, 0))

        # Current sum-of-gaps (un-weighted by demand factor)
        current_gaps = {
            rt: float(zip_row.get(gap_col, 0.0))
            for rt, gap_col in _RESOURCE_TO_GAP_COL.items()
            if gap_col in zip_row.index
        }
        current_gap_sum = sum(current_gaps.values())

        for resource_type in RESOURCE_TYPES:
            gap_col = _RESOURCE_TO_GAP_COL.get(resource_type)
            if gap_col is None or gap_col not in zip_row.index:
                continue

            current_gap = current_gaps.get(resource_type, 0.0)
            target_gap = p25_targets.get(gap_col, current_gap)

            # Intervention can only improve (reduce) the gap, never worsen it
            simulated_gap = min(current_gap, target_gap)
            gap_reduction = current_gap - simulated_gap

            # Recompute score: replace this resource's gap with the simulated value
            simulated_gap_sum = current_gap_sum - gap_reduction
            simulated_raw = simulated_gap_sum * demand_factor

            # Proportional scaling: maintain the same normalisation as the
            # original score (avoids re-running full min-max across all ZIPs)
            current_raw = current_gap_sum * demand_factor
            if current_raw > 0 and current_score > 0:
                simulated_score = current_score * (simulated_raw / current_raw)
            else:
                simulated_score = current_score

            simulated_score = float(np.clip(simulated_score, 0.0, 100.0))
            score_improvement = max(0.0, current_score - simulated_score)
            pct_improvement = (
                (score_improvement / current_score * 100.0) if current_score > 0 else 0.0
            )
            pct_improvement = float(np.clip(pct_improvement, 0.0, 100.0))

            rows.append(
                {
                    "zip_code": zip_code,
                    "resource_type": resource_type,
                    "current_desert_score": round(current_score, 2),
                    "simulated_desert_score": round(simulated_score, 2),
                    "score_improvement": round(score_improvement, 2),
                    "pct_improvement": round(pct_improvement, 2),
                    "population_impacted": population,
                    "is_highest_impact": False,
                }
            )

    interventions_df = pd.DataFrame(rows)
    logger.info(
        "Gap-closure simulation complete: %d interventions across top-%d ZIPs.",
        len(interventions_df),
        top_n,
    )
    return interventions_df


def rank_interventions(interventions_df: pd.DataFrame) -> pd.DataFrame:
    """Sort interventions and flag the single highest-impact action.

    Sets ``is_highest_impact = True`` on the row with the largest
    ``score_improvement``.  Writes the result to
    ``reports/outputs/intervention_recommendations.json``.

    Args:
        interventions_df: Output of :func:`run_gap_closure_simulation`.

    Returns:
        Sorted DataFrame with exactly one row where
        ``is_highest_impact == True``.
    """
    df = interventions_df.copy().sort_values(
        "score_improvement", ascending=False
    ).reset_index(drop=True)

    df["is_highest_impact"] = False
    df.loc[0, "is_highest_impact"] = True

    cfg.REPORTS_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_json(cfg.INTERVENTION_RECOMMENDATIONS_PATH, orient="records", indent=2)
    logger.info(
        "Saved %d intervention recommendations → %s",
        len(df),
        cfg.INTERVENTION_RECOMMENDATIONS_PATH,
    )

    best = df.iloc[0]
    logger.info(
        "Highest-impact action: %s in ZIP %s — %.1f%% Desert Score improvement "
        "(%.2f → %.2f)",
        best["resource_type"],
        best["zip_code"],
        best["pct_improvement"],
        best["current_desert_score"],
        best["simulated_desert_score"],
    )

    return df
