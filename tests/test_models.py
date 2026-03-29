"""Unit tests for src.models — T021.

Tests use synthetic fixture DataFrames only; no real data files are loaded.
"""

import pandas as pd
import pytest

from src import config as cfg
from src.models import RESOURCE_TYPES, rank_interventions, run_gap_closure_simulation


@pytest.fixture()
def sample_interventions_df() -> pd.DataFrame:
    """Synthetic interventions DataFrame before ranking (is_highest_impact all False)."""
    rows = []
    for zip_code, score in [("32201", 72.5), ("32202", 85.1)]:
        for rt in RESOURCE_TYPES:
            rows.append(
                {
                    "zip_code": zip_code,
                    "resource_type": rt,
                    "current_desert_score": score,
                    "simulated_desert_score": score * 0.8,
                    "score_improvement": score * 0.2,
                    "pct_improvement": 20.0,
                    "population_impacted": 6000,
                    "is_highest_impact": False,
                }
            )
    # Make one row have a clearly higher improvement
    rows[0]["score_improvement"] = 99.0
    rows[0]["pct_improvement"] = 90.0
    return pd.DataFrame(rows)


class TestRunGapClosureSimulation:
    def test_returns_top_n_times_4_rows(
        self, sample_desert_scores_df, sample_merged_df
    ):
        """run_gap_closure_simulation() returns exactly top_n × 4 rows."""
        result = run_gap_closure_simulation(
            sample_desert_scores_df, sample_merged_df, top_n=3
        )
        assert len(result) == 3 * 4

    def test_returns_dataframe(self, sample_desert_scores_df, sample_merged_df):
        """run_gap_closure_simulation() returns a DataFrame."""
        result = run_gap_closure_simulation(
            sample_desert_scores_df, sample_merged_df, top_n=2
        )
        assert isinstance(result, pd.DataFrame)

    def test_score_improvement_non_negative(
        self, sample_desert_scores_df, sample_merged_df
    ):
        """score_improvement is >= 0 for all rows (simulation never worsens score)."""
        result = run_gap_closure_simulation(
            sample_desert_scores_df, sample_merged_df, top_n=5
        )
        assert (result["score_improvement"] >= 0).all()

    def test_pct_improvement_in_valid_range(
        self, sample_desert_scores_df, sample_merged_df
    ):
        """pct_improvement values are all in [0, 100]."""
        result = run_gap_closure_simulation(
            sample_desert_scores_df, sample_merged_df, top_n=5
        )
        assert result["pct_improvement"].between(0.0, 100.0).all()

    def test_is_highest_impact_all_false_before_ranking(
        self, sample_desert_scores_df, sample_merged_df
    ):
        """is_highest_impact is False for all rows before rank_interventions() is called."""
        result = run_gap_closure_simulation(
            sample_desert_scores_df, sample_merged_df, top_n=5
        )
        assert not result["is_highest_impact"].any()

    def test_required_columns_present(self, sample_desert_scores_df, sample_merged_df):
        """Output DataFrame has all required columns."""
        result = run_gap_closure_simulation(
            sample_desert_scores_df, sample_merged_df, top_n=2
        )
        required = [
            "zip_code",
            "resource_type",
            "current_desert_score",
            "simulated_desert_score",
            "score_improvement",
            "pct_improvement",
            "population_impacted",
            "is_highest_impact",
        ]
        for col in required:
            assert col in result.columns, f"Missing column: {col}"

    def test_resource_types_are_four_expected_values(
        self, sample_desert_scores_df, sample_merged_df
    ):
        """resource_type column contains exactly the 4 expected resource types."""
        result = run_gap_closure_simulation(
            sample_desert_scores_df, sample_merged_df, top_n=2
        )
        assert set(result["resource_type"].unique()) == set(RESOURCE_TYPES)

    def test_only_top_n_zips_simulated(self, sample_desert_scores_df, sample_merged_df):
        """Only the top-N most underserved ZIPs appear in the simulation output."""
        top_n = 2
        result = run_gap_closure_simulation(
            sample_desert_scores_df, sample_merged_df, top_n=top_n
        )
        expected_zips = set(
            sample_desert_scores_df.nsmallest(top_n, cfg.COL_DESERT_RANK)[
                cfg.COL_ZIP
            ].tolist()
        )
        assert set(result["zip_code"].unique()) == expected_zips


class TestRankInterventions:
    def test_exactly_one_highest_impact_row(self, sample_interventions_df):
        """rank_interventions() sets is_highest_impact=True on exactly one row."""
        result = rank_interventions(sample_interventions_df)
        assert result["is_highest_impact"].sum() == 1

    def test_highest_impact_row_has_max_improvement(self, sample_interventions_df):
        """The row with is_highest_impact=True has the maximum score_improvement."""
        result = rank_interventions(sample_interventions_df)
        best = result.loc[result["is_highest_impact"]]
        assert best["score_improvement"].iloc[0] == result["score_improvement"].max()

    def test_sorted_by_score_improvement_descending(self, sample_interventions_df):
        """Output is sorted by score_improvement in descending order."""
        result = rank_interventions(sample_interventions_df)
        scores = result["score_improvement"].tolist()
        assert scores == sorted(scores, reverse=True)

    def test_returns_same_row_count(self, sample_interventions_df):
        """rank_interventions() returns the same number of rows as input."""
        result = rank_interventions(sample_interventions_df)
        assert len(result) == len(sample_interventions_df)

    def test_json_output_written(self, sample_interventions_df, tmp_path, monkeypatch):
        """rank_interventions() writes JSON to reports/outputs/."""
        out_path = tmp_path / "intervention_recommendations.json"
        monkeypatch.setattr(cfg, "INTERVENTION_RECOMMENDATIONS_PATH", out_path)
        monkeypatch.setattr(cfg, "REPORTS_OUTPUTS_DIR", tmp_path)
        rank_interventions(sample_interventions_df)
        assert out_path.exists()
        assert out_path.stat().st_size > 0
