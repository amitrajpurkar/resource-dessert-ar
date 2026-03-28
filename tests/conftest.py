"""Synthetic fixture DataFrames for unit tests.

All fixtures use small (5-row) synthetic DataFrames that mirror the schema of
the real raw datasets.  Real data files in ``data/raw/`` are never loaded in
unit tests.
"""

import numpy as np
import pandas as pd
import pytest

from src import config as cfg


@pytest.fixture()
def sample_census_demo_df() -> pd.DataFrame:
    """5-row synthetic Census-Demographics DataFrame."""
    return pd.DataFrame(
        {
            cfg.COL_FEATURE_LABEL: [
                "ZIP Code 32201",
                "ZIP Code 32202",
                "ZIP Code 32203",
                "ZIP Code 32204",
                "ZIP Code 32205",
            ],
            cfg.COL_GEOID: ["32201", "32202", "32203", "32204", "32205"],
            cfg.COL_TOTAL_POPULATION: [5000, 6000, 7000, 8000, 9000],
        }
    )


@pytest.fixture()
def sample_census_housing_df() -> pd.DataFrame:
    """5-row synthetic Census-Housing&Poverty DataFrame."""
    return pd.DataFrame(
        {
            cfg.COL_FEATURE_LABEL: [
                "ZIP Code 32201",
                "ZIP Code 32202",
                "ZIP Code 32203",
                "ZIP Code 32204",
                "ZIP Code 32205",
            ],
            cfg.COL_GEOID: ["32201", "32202", "32203", "32204", "32205"],
            cfg.COL_POVERTY_COUNT: [800, 1400, 600, 300, 1200],
            cfg.COL_MEDIAN_INCOME: [32000, 35000, 55000, 65000, 40000],
            cfg.COL_HOUSING_COST_BURDEN: [900, 1400, 700, 400, 1100],
        }
    )


@pytest.fixture()
def sample_cdc_df() -> pd.DataFrame:
    """5-row synthetic CDCPlaces DataFrame."""
    return pd.DataFrame(
        {
            cfg.COL_FEATURE_LABEL: [
                "ZIP Code 32201",
                "ZIP Code 32202",
                "ZIP Code 32203",
                "ZIP Code 32204",
                "ZIP Code 32205",
            ],
            cfg.COL_GEOID: ["32201", "32202", "32203", "32204", "32205"],
            cfg.COL_POOR_MENTAL_HEALTH: [22.0, 41.1, 18.0, 15.0, 35.0],
            cfg.COL_OBESITY: [38.0, 45.0, 30.0, 25.0, 40.0],
            cfg.COL_NO_PHYSICAL_ACTIVITY: [30.0, 42.0, 25.0, 20.0, 38.0],
            cfg.COL_LIFE_EXPECTANCY: [74.5, 73.1, 78.2, 80.1, 75.3],
        }
    )


@pytest.fixture()
def sample_healthcare_workers_df() -> pd.DataFrame:
    """5-row synthetic HealthCareWorkers DataFrame."""
    return pd.DataFrame(
        {
            cfg.COL_FEATURE_LABEL: [
                "ZIP Code 32201",
                "ZIP Code 32202",
                "ZIP Code 32203",
                "ZIP Code 32204",
                "ZIP Code 32205",
            ],
            cfg.COL_GEOID: ["32201", "32202", "32203", "32204", "32205"],
            cfg.COL_PRIMARY_CARE_RATIO: [120.0, 354.3, np.nan, 84.7, 200.0],
            cfg.COL_NP_RATIO: [50.0, 80.0, 40.0, 30.0, 60.0],
            cfg.COL_CHILD_CARE_CENTERS: [2, 3, 5, 5, 4],
        }
    )


@pytest.fixture()
def sample_healthcare_access_df() -> pd.DataFrame:
    """5-row synthetic HealthCareAccess DataFrame."""
    return pd.DataFrame(
        {
            cfg.COL_FEATURE_LABEL: [
                "ZIP Code 32201",
                "ZIP Code 32202",
                "ZIP Code 32203",
                "ZIP Code 32204",
                "ZIP Code 32205",
            ],
            cfg.COL_GEOID: ["32201", "32202", "32203", "32204", "32205"],
            cfg.COL_UNINSURED_COUNT: [800, 1100, 500, 300, 900],
            cfg.COL_INSURED_COUNT: [4200, 4900, 6500, 7700, 8100],
            cfg.COL_MENTAL_HEALTH_PROVIDERS: [10, 33, 20, 83, 15],
            cfg.COL_TOTAL_HEALTHCARE_WORKERS: [150, 268, 400, 1709, 300],
        }
    )


@pytest.fixture()
def sample_parks_df() -> pd.DataFrame:
    """5-row synthetic Parks DataFrame."""
    return pd.DataFrame(
        {
            cfg.COL_FEATURE_LABEL: [
                "ZIP Code 32201",
                "ZIP Code 32202",
                "ZIP Code 32203",
                "ZIP Code 32204",
                "ZIP Code 32205",
            ],
            cfg.COL_GEOID: ["32201", "32202", "32203", "32204", "32205"],
            cfg.COL_PARK_COUNT: [5, 14, 20, 14, 8],
            cfg.COL_PARK_COVERAGE_PCT: [1.0, 3.1, 8.0, 1.7, 2.5],
            cfg.COL_PARK_AREA_ACRES: [20.0, 58.6, 120.0, 45.4, 35.0],
        }
    )


@pytest.fixture()
def sample_usda_df() -> pd.DataFrame:
    """5-row synthetic USDA-FoodAccess DataFrame."""
    return pd.DataFrame(
        {
            cfg.COL_FEATURE_LABEL: [
                "ZIP Code 32201",
                "ZIP Code 32202",
                "ZIP Code 32203",
                "ZIP Code 32204",
                "ZIP Code 32205",
            ],
            cfg.COL_GEOID: ["32201", "32202", "32203", "32204", "32205"],
            cfg.COL_FOOD_LOW_ACCESS_1_MILE: [1200, 1325, 400, 3870, 2000],
            cfg.COL_FOOD_LOW_ACCESS_20_MILE: [1100, 1200, 300, 3500, 1800],
            cfg.COL_FOOD_LOW_INCOME: [1800, 2127, 1000, 3147, 2200],
        }
    )


@pytest.fixture()
def sample_svi_df() -> pd.DataFrame:
    """5-row synthetic SocialVulnerabilityIndex DataFrame."""
    return pd.DataFrame(
        {
            cfg.COL_FEATURE_LABEL: [
                "ZIP Code 32201",
                "ZIP Code 32202",
                "ZIP Code 32203",
                "ZIP Code 32204",
                "ZIP Code 32205",
            ],
            cfg.COL_GEOID: ["32201", "32202", "32203", "32204", "32205"],
            cfg.COL_SVI_SCORE: [0.75, 0.93, 0.45, 0.64, 0.80],
            cfg.COL_SVI_VULNERABLE_FACTORS: [5, 7, 2, 2, 6],
        }
    )


@pytest.fixture()
def sample_fema_df() -> pd.DataFrame:
    """5-row synthetic FEMA DataFrame."""
    return pd.DataFrame(
        {
            cfg.COL_FEATURE_LABEL: [
                "ZIP Code 32201",
                "ZIP Code 32202",
                "ZIP Code 32203",
                "ZIP Code 32204",
                "ZIP Code 32205",
            ],
            cfg.COL_GEOID: ["32201", "32202", "32203", "32204", "32205"],
            cfg.COL_FEMA_RESILIENCE: [49.8, 49.8, 55.0, 60.0, 52.0],
            cfg.COL_FEMA_ANNUAL_LOSS: [3_400_000, 4_800_000, 2_000_000, 3_000_000, 4_000_000],
            cfg.COL_FEMA_SOCIAL_VULN: [0.57, 0.51, 0.35, 0.45, 0.60],
        }
    )


@pytest.fixture()
def all_raw_datasets(
    sample_census_demo_df,
    sample_census_housing_df,
    sample_cdc_df,
    sample_healthcare_workers_df,
    sample_healthcare_access_df,
    sample_parks_df,
    sample_usda_df,
    sample_svi_df,
    sample_fema_df,
) -> dict:
    """Dict of all 9 synthetic raw DataFrames keyed by dataset name."""
    return {
        cfg.KEY_CENSUS_DEMO: sample_census_demo_df,
        cfg.KEY_CENSUS_HOUSING: sample_census_housing_df,
        cfg.KEY_CDC: sample_cdc_df,
        cfg.KEY_HEALTHCARE_WORKERS: sample_healthcare_workers_df,
        cfg.KEY_HEALTHCARE_ACCESS: sample_healthcare_access_df,
        cfg.KEY_PARKS: sample_parks_df,
        cfg.KEY_USDA: sample_usda_df,
        cfg.KEY_SVI: sample_svi_df,
        cfg.KEY_FEMA: sample_fema_df,
    }


@pytest.fixture()
def sample_merged_df() -> pd.DataFrame:
    """5-row synthetic merged wide DataFrame (post-cleaning, pre-scoring)."""
    return pd.DataFrame(
        {
            cfg.COL_ZIP: ["32201", "32202", "32203", "32204", "32205"],
            cfg.COL_TOTAL_POPULATION: [5000, 6000, 7000, 8000, 9000],
            cfg.COL_POVERTY_RATE: [0.16, 0.23, 0.086, 0.038, 0.133],
            cfg.COL_UNINSURED_RATE: [0.16, 0.18, 0.071, 0.038, 0.10],
            cfg.COL_POOR_MENTAL_HEALTH: [22.0, 41.1, 18.0, 15.0, 35.0],
            cfg.COL_OBESITY: [38.0, 45.0, 30.0, 25.0, 40.0],
            cfg.COL_PRIMARY_CARE_RATIO: [120.0, 354.3, 200.0, 84.7, 200.0],
            cfg.COL_FOOD_LOW_ACCESS_PCT: [0.24, 0.22, 0.057, 0.484, 0.222],
            cfg.COL_PARK_COVERAGE_PCT: [1.0, 3.1, 8.0, 1.7, 2.5],
        }
    )


@pytest.fixture()
def sample_desert_scores_df() -> pd.DataFrame:
    """5-row synthetic ResourceDesertScore DataFrame."""
    return pd.DataFrame(
        {
            cfg.COL_ZIP: ["32201", "32202", "32203", "32204", "32205"],
            cfg.COL_DESERT_SCORE: [72.5, 85.1, 15.3, 42.8, 61.0],
            cfg.COL_DESERT_RANK: [2, 1, 5, 4, 3],
            cfg.COL_DEMAND_FACTOR: [0.55, 0.80, 0.20, 0.15, 0.65],
            cfg.COL_SUPPLY_GAP_HEALTHCARE: [0.70, 0.60, 0.30, 0.90, 0.50],
            cfg.COL_SUPPLY_GAP_FOOD: [0.40, 0.35, 0.10, 0.85, 0.42],
            cfg.COL_SUPPLY_GAP_PARKS: [0.80, 0.70, 0.10, 0.75, 0.65],
            cfg.COL_SUPPLY_GAP_INSURANCE: [0.60, 0.70, 0.20, 0.15, 0.45],
            cfg.COL_TOP_GAP_CATEGORY: ["parks", "insurance", "healthcare", "healthcare", "parks"],
            cfg.COL_TOTAL_POPULATION: [5000, 6000, 7000, 8000, 9000],
            cfg.COL_POVERTY_RATE: [0.16, 0.23, 0.086, 0.038, 0.133],
        }
    )
