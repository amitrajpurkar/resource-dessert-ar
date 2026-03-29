"""Unit tests for src.ingestion — T009.

Tests use synthetic fixtures only; real data/raw/ files are never loaded.
"""

import pandas as pd
import pytest

from src import config as cfg
from src.ingestion import _load_csv, load_raw_datasets


class TestLoadRawDatasets:
    def test_returns_dict_with_all_expected_keys(self, tmp_path, monkeypatch):
        """load_raw_datasets() returns a dict containing all 9 dataset keys."""
        # Create minimal stub CSVs so file-existence checks pass
        for path in [
            cfg.CDC_PLACES_PATH,
            cfg.CENSUS_DEMOGRAPHICS_PATH,
            cfg.CENSUS_HOUSING_POVERTY_PATH,
            cfg.FEMA_PATH,
            cfg.HEALTHCARE_ACCESS_PATH,
            cfg.HEALTHCARE_WORKERS_PATH,
            cfg.PARKS_PATH,
            cfg.SVI_PATH,
            cfg.USDA_FOOD_ACCESS_PATH,
        ]:
            stub = tmp_path / path.name
            stub.write_text(
                "feature id,feature label,shid,geoid,col1\n1,ZIP Code 32201,x,32201,1.0\n"
            )

        stub_xlsx = tmp_path / cfg.METADATA_PATH.name
        # write a minimal xlsx via openpyxl
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Variables", "Source", "Link", "Data File Name"])
        ws.append(["col1", "CDC", "http://example.com", "CDCPlaces.csv"])
        wb.save(str(stub_xlsx))

        # Monkeypatch config paths to point to tmp_path stubs
        monkeypatch.setattr(cfg, "CDC_PLACES_PATH", tmp_path / cfg.CDC_PLACES_PATH.name)
        monkeypatch.setattr(
            cfg,
            "CENSUS_DEMOGRAPHICS_PATH",
            tmp_path / cfg.CENSUS_DEMOGRAPHICS_PATH.name,
        )
        monkeypatch.setattr(
            cfg,
            "CENSUS_HOUSING_POVERTY_PATH",
            tmp_path / cfg.CENSUS_HOUSING_POVERTY_PATH.name,
        )
        monkeypatch.setattr(cfg, "FEMA_PATH", tmp_path / cfg.FEMA_PATH.name)
        monkeypatch.setattr(
            cfg, "HEALTHCARE_ACCESS_PATH", tmp_path / cfg.HEALTHCARE_ACCESS_PATH.name
        )
        monkeypatch.setattr(
            cfg, "HEALTHCARE_WORKERS_PATH", tmp_path / cfg.HEALTHCARE_WORKERS_PATH.name
        )
        monkeypatch.setattr(cfg, "PARKS_PATH", tmp_path / cfg.PARKS_PATH.name)
        monkeypatch.setattr(cfg, "SVI_PATH", tmp_path / cfg.SVI_PATH.name)
        monkeypatch.setattr(
            cfg, "USDA_FOOD_ACCESS_PATH", tmp_path / cfg.USDA_FOOD_ACCESS_PATH.name
        )
        monkeypatch.setattr(cfg, "METADATA_PATH", stub_xlsx)

        result = load_raw_datasets()

        expected_keys = {
            cfg.KEY_CDC,
            cfg.KEY_CENSUS_DEMO,
            cfg.KEY_CENSUS_HOUSING,
            cfg.KEY_FEMA,
            cfg.KEY_HEALTHCARE_ACCESS,
            cfg.KEY_HEALTHCARE_WORKERS,
            cfg.KEY_PARKS,
            cfg.KEY_SVI,
            cfg.KEY_USDA,
        }
        assert expected_keys.issubset(result.keys())

    def test_each_value_is_dataframe_with_at_least_one_row(self, tmp_path, monkeypatch):
        """Every value in the returned dict is a non-empty DataFrame."""
        for path_attr in [
            "CDC_PLACES_PATH",
            "CENSUS_DEMOGRAPHICS_PATH",
            "CENSUS_HOUSING_POVERTY_PATH",
            "FEMA_PATH",
            "HEALTHCARE_ACCESS_PATH",
            "HEALTHCARE_WORKERS_PATH",
            "PARKS_PATH",
            "SVI_PATH",
            "USDA_FOOD_ACCESS_PATH",
        ]:
            stub = tmp_path / getattr(cfg, path_attr).name
            stub.write_text(
                "feature id,feature label,shid,geoid,col1\n1,ZIP Code 32201,x,32201,1.0\n"
            )
            monkeypatch.setattr(cfg, path_attr, stub)

        import openpyxl

        stub_xlsx = tmp_path / cfg.METADATA_PATH.name
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Variables", "Source", "Link", "Data File Name"])
        ws.append(["col1", "CDC", "http://example.com", "CDCPlaces.csv"])
        wb.save(str(stub_xlsx))
        monkeypatch.setattr(cfg, "METADATA_PATH", stub_xlsx)

        result = load_raw_datasets()
        for key, df in result.items():
            assert isinstance(df, pd.DataFrame), f"{key} is not a DataFrame"
            assert len(df) >= 1, f"{key} has zero rows"

    def test_raises_file_not_found_when_csv_missing(self, tmp_path, monkeypatch):
        """load_raw_datasets() raises FileNotFoundError if a CSV is absent."""
        missing = tmp_path / "CDCPlaces.csv"
        monkeypatch.setattr(cfg, "CDC_PLACES_PATH", missing)
        with pytest.raises(FileNotFoundError, match="CDCPlaces"):
            load_raw_datasets()


class TestLoadCsv:
    def test_returns_dataframe(self, tmp_path):
        """_load_csv() returns a DataFrame for a valid CSV."""
        f = tmp_path / "test.csv"
        f.write_text("a,b\n1,2\n3,4\n")
        df = _load_csv(f, "test")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    def test_raises_file_not_found(self, tmp_path):
        """_load_csv() raises FileNotFoundError for a missing file."""
        with pytest.raises(FileNotFoundError):
            _load_csv(tmp_path / "missing.csv", "missing")

    def test_raises_value_error_for_empty_csv(self, tmp_path):
        """_load_csv() raises ValueError for a CSV with no data rows."""
        f = tmp_path / "empty.csv"
        f.write_text("a,b\n")
        with pytest.raises(ValueError):
            _load_csv(f, "empty")
