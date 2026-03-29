"""Unit tests for src.features — T011.

Tests use synthetic fixture DataFrames only; no real data files are loaded.
"""

import pandas as pd
import pytest

from src import config as cfg
from src.features import (
    _minmax,
    compute_desert_score,
    compute_health_outcome_correlation,
    filter_by_service_category,
    merge_datasets,
)


class TestMinmax:
    def test_output_range_is_0_to_1(self):
        """_minmax() output is in [0.0, 1.0]."""
        s = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])
        result = _minmax(s)
        assert result.min() >= 0.0
        assert result.max() <= 1.0

    def test_min_value_maps_to_zero(self):
        """The minimum input value maps to 0.0."""
        s = pd.Series([5.0, 10.0, 15.0])
        assert _minmax(s).iloc[0] == pytest.approx(0.0)

    def test_max_value_maps_to_one(self):
        """The maximum input value maps to 1.0."""
        s = pd.Series([5.0, 10.0, 15.0])
        assert _minmax(s).iloc[2] == pytest.approx(1.0)

    def test_constant_series_returns_zeros(self):
        """_minmax() returns all zeros for a constant Series."""
        s = pd.Series([7.0, 7.0, 7.0])
        result = _minmax(s)
        assert (result == 0.0).all()


class TestMergeDatasets:
    def test_returns_dataframe(self, all_raw_datasets):
        """merge_datasets() returns a DataFrame."""
        from src.cleaning import clean_datasets

        cleaned = clean_datasets(all_raw_datasets)
        result = merge_datasets(cleaned)
        assert isinstance(result, pd.DataFrame)

    def test_no_duplicate_zip_codes(self, all_raw_datasets):
        """Merged DataFrame has no duplicate zip_code values."""
        from src.cleaning import clean_datasets

        cleaned = clean_datasets(all_raw_datasets)
        result = merge_datasets(cleaned)
        assert result[cfg.COL_ZIP].nunique() == len(result)

    def test_excludes_zero_population_zips(self, all_raw_datasets):
        """ZIPs with population == 0 are excluded from the merged table."""
        from src.cleaning import clean_datasets

        # Inject a zero-population ZIP into census demo
        demo = all_raw_datasets[cfg.KEY_CENSUS_DEMO].copy()
        zero_row = demo.iloc[0:1].copy()
        zero_row["feature label"] = "ZIP Code 32299"
        zero_row[cfg.COL_TOTAL_POPULATION] = 0
        all_raw_datasets[cfg.KEY_CENSUS_DEMO] = pd.concat(
            [demo, zero_row], ignore_index=True
        )
        cleaned = clean_datasets(all_raw_datasets)
        result = merge_datasets(cleaned)
        assert "32299" not in result[cfg.COL_ZIP].values


class TestComputeDesertScore:
    def test_desert_score_in_0_100_range(self, sample_merged_df):
        """desert_score values are all in [0.0, 100.0]."""
        result = compute_desert_score(sample_merged_df)
        assert result[cfg.COL_DESERT_SCORE].between(0.0, 100.0).all()

    def test_desert_rank_starts_at_one(self, sample_merged_df):
        """desert_rank minimum value is 1."""
        result = compute_desert_score(sample_merged_df)
        assert result[cfg.COL_DESERT_RANK].min() == 1

    def test_desert_rank_is_contiguous(self, sample_merged_df):
        """desert_rank values form a contiguous sequence."""
        result = compute_desert_score(sample_merged_df)
        n = len(result)
        assert sorted(result[cfg.COL_DESERT_RANK].tolist()) == list(range(1, n + 1))

    def test_result_has_required_columns(self, sample_merged_df):
        """Output contains all required ResourceDesertScore columns."""
        result = compute_desert_score(sample_merged_df)
        required = [
            cfg.COL_ZIP,
            cfg.COL_DESERT_SCORE,
            cfg.COL_DESERT_RANK,
            cfg.COL_DEMAND_FACTOR,
            cfg.COL_SUPPLY_GAP_HEALTHCARE,
            cfg.COL_SUPPLY_GAP_FOOD,
            cfg.COL_SUPPLY_GAP_PARKS,
            cfg.COL_SUPPLY_GAP_INSURANCE,
        ]
        for col in required:
            assert col in result.columns, f"Missing column: {col}"

    def test_no_duplicate_zips_in_output(self, sample_merged_df):
        """Output has no duplicate zip_code values."""
        result = compute_desert_score(sample_merged_df)
        assert result[cfg.COL_ZIP].nunique() == len(result)


class TestComputeHealthOutcomeCorrelation:
    def test_returns_dataframe_with_pearson_r(self, sample_merged_df):
        """compute_health_outcome_correlation() returns a DataFrame with pearson_r column."""
        result = compute_health_outcome_correlation(sample_merged_df)
        assert isinstance(result, pd.DataFrame)
        assert "pearson_r" in result.columns

    def test_pearson_r_values_in_valid_range(self, sample_merged_df):
        """All pearson_r values are in [-1, 1]."""
        result = compute_health_outcome_correlation(sample_merged_df)
        assert result["pearson_r"].between(-1.0, 1.0).all()

    def test_at_least_one_row_returned(self, sample_merged_df):
        """At least one asset-outcome pair is returned."""
        result = compute_health_outcome_correlation(sample_merged_df)
        assert len(result) >= 1


class TestFilterByServiceCategory:
    @pytest.mark.parametrize(
        "category",
        ["healthcare", "food_access", "parks", "insurance"],
    )
    def test_valid_categories_return_dataframe(self, sample_desert_scores_df, category):
        """filter_by_service_category() returns a DataFrame for all valid categories."""
        result = filter_by_service_category(sample_desert_scores_df, category)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_invalid_category_raises_value_error(self, sample_desert_scores_df):
        """filter_by_service_category() raises ValueError for unknown category."""
        with pytest.raises(ValueError, match="category"):
            filter_by_service_category(sample_desert_scores_df, "unknown")

    def test_result_has_zip_code_column(self, sample_desert_scores_df):
        """Filtered result always contains zip_code column."""
        result = filter_by_service_category(sample_desert_scores_df, "healthcare")
        assert cfg.COL_ZIP in result.columns
