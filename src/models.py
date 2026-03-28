"""Stage 4 — Gap-Closure Simulation (Optimization Model).

Simulates adding each resource type to the top-N most underserved ZIP codes
and identifies the single highest-impact intervention.
"""

import random
from pathlib import Path

import numpy as np
import pandas as pd

from src import config as cfg

logger = cfg.get_logger(__name__)

RESOURCE_TYPES = ["primary_care", "food_access", "parks", "insurance_outreach"]


def run_gap_closure_simulation(
    desert_scores_df: pd.DataFrame,
    merged_df: pd.DataFrame,
    top_n: int = 5,
) -> pd.DataFrame:
    """Simulate setting each supply metric to its 75th-percentile value.

    For each of the *top_n* most underserved ZIPs and each of the 4 resource
    types, sets the corresponding supply metric to the 75th percentile of that
    column across all ZIPs, recomputes the Desert Score, and records the delta.

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
        ``is_highest_impact`` (False for all rows until
        :func:`rank_interventions` is called).
    """
    raise NotImplementedError


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
    raise NotImplementedError
