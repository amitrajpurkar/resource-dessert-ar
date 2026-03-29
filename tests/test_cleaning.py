"""Unit tests for src.cleaning — T010.

Tests use synthetic fixture DataFrames only; no real data files are loaded.
"""

import pandas as pd
import pytest

from src import config as cfg
from src.cleaning import (
    _coerce_numerics,
    _drop_duplicates,
    _standardise_zip,
    clean_datasets,
)


class TestStandardiseZip:
    def test_extracts_5digit_zip_from_feature_label(self):
        """_standardise_zip() extracts ZIP from 'ZIP Code 32202' format."""
        df = pd.DataFrame({"feature label": ["ZIP Code 32201", "ZIP Code 32202"]})
        result = _standardise_zip(df, "test")
        assert cfg.COL_ZIP in result.columns
        assert list(result[cfg.COL_ZIP]) == ["32201", "32202"]

    def test_zip_is_string_type(self):
        """zip_code column is dtype str (object)."""
        df = pd.DataFrame({"feature label": ["ZIP Code 32201"]})
        result = _standardise_zip(df, "test")
        assert result[cfg.COL_ZIP].dtype == object

    def test_zip_is_zero_padded_to_5_chars(self):
        """Short ZIP codes are zero-padded to 5 characters."""
        df = pd.DataFrame({"feature label": ["ZIP Code 3220"]})
        result = _standardise_zip(df, "test")
        assert result[cfg.COL_ZIP].iloc[0] == "03220"

    def test_raises_if_no_zip_can_be_extracted(self):
        """_standardise_zip() raises ValueError when no digits are found."""
        df = pd.DataFrame({"feature label": ["Unknown Area", "No ZIP"]})
        with pytest.raises(ValueError, match="ZIP"):
            _standardise_zip(df, "test")


class TestDropDuplicates:
    def test_removes_duplicate_zip_rows(self):
        """_drop_duplicates() removes rows with duplicate zip_code."""
        df = pd.DataFrame({cfg.COL_ZIP: ["32201", "32202", "32201", "32203"]})
        result = _drop_duplicates(df, "test")
        assert len(result) == 3
        assert result[cfg.COL_ZIP].nunique() == 3

    def test_keeps_first_occurrence(self):
        """_drop_duplicates() keeps the first occurrence when deduplicating."""
        df = pd.DataFrame(
            {
                cfg.COL_ZIP: ["32201", "32201"],
                "value": [10, 99],
            }
        )
        result = _drop_duplicates(df, "test")
        assert result["value"].iloc[0] == 10

    def test_no_duplicates_unchanged(self):
        """_drop_duplicates() is a no-op when no duplicates exist."""
        df = pd.DataFrame({cfg.COL_ZIP: ["32201", "32202", "32203"]})
        result = _drop_duplicates(df, "test")
        assert len(result) == 3


class TestCoerceNumerics:
    def test_converts_na_strings_to_nan(self):
        """_coerce_numerics() converts 'N/A' strings to NaN float."""
        df = pd.DataFrame({"ratio": ["N/A", "354.29", "84.73"]})
        result = _coerce_numerics(df)
        assert pd.isna(result["ratio"].iloc[0])
        assert result["ratio"].iloc[1] == pytest.approx(354.29)

    def test_leaves_already_numeric_columns_unchanged(self):
        """_coerce_numerics() does not alter already-numeric columns."""
        df = pd.DataFrame({"val": [1.0, 2.0, 3.0]})
        result = _coerce_numerics(df)
        assert result["val"].dtype == float


class TestCleanDatasets:
    def test_returns_dict_with_same_keys(self, all_raw_datasets):
        """clean_datasets() returns a dict with the same keys as input."""
        result = clean_datasets(all_raw_datasets)
        assert set(result.keys()) == set(all_raw_datasets.keys())

    def test_zip_code_column_present_in_all_datasets(self, all_raw_datasets):
        """Every cleaned DataFrame has a zip_code column."""
        result = clean_datasets(all_raw_datasets)
        for key, df in result.items():
            assert cfg.COL_ZIP in df.columns, f"{key} missing zip_code"

    def test_no_duplicate_zips_in_any_dataset(self, all_raw_datasets):
        """No cleaned DataFrame has duplicate zip_code values."""
        result = clean_datasets(all_raw_datasets)
        for key, df in result.items():
            assert df[cfg.COL_ZIP].nunique() == len(df), f"{key} has duplicate zips"

    def test_zip_code_is_5_char_string(self, all_raw_datasets):
        """All zip_code values are 5-character strings."""
        result = clean_datasets(all_raw_datasets)
        for key, df in result.items():
            assert all(df[cfg.COL_ZIP].str.len() == 5), f"{key} has bad ZIP format"
