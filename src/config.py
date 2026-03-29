"""Central configuration: all Path constants and logging helper.

No hardcoded path strings are permitted outside this module.
"""

import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Root paths
# ---------------------------------------------------------------------------
ROOT: Path = Path(__file__).resolve().parent.parent

DATA_RAW_DIR: Path = ROOT / "data" / "raw"
DATA_PROCESSED_DIR: Path = ROOT / "data" / "processed"
DATA_OUTPUTS_DIR: Path = ROOT / "data" / "outputs"

REPORTS_FIGURES_DIR: Path = ROOT / "reports" / "figures"
REPORTS_OUTPUTS_DIR: Path = ROOT / "reports" / "outputs"

# ---------------------------------------------------------------------------
# Raw data file paths
# ---------------------------------------------------------------------------
CDC_PLACES_PATH: Path = DATA_RAW_DIR / "CDCPlaces.csv"
CENSUS_DEMOGRAPHICS_PATH: Path = DATA_RAW_DIR / "Census-Demographics.csv"
CENSUS_HOUSING_POVERTY_PATH: Path = DATA_RAW_DIR / "Census-Housing&Poverty.csv"
FEMA_PATH: Path = DATA_RAW_DIR / "FEMA.csv"
HEALTHCARE_ACCESS_PATH: Path = DATA_RAW_DIR / "HealthCareAccess.csv"
HEALTHCARE_WORKERS_PATH: Path = DATA_RAW_DIR / "HealthCareWorkers.csv"
PARKS_PATH: Path = DATA_RAW_DIR / "Parks.csv"
SVI_PATH: Path = DATA_RAW_DIR / "SocialVulnerabilityIndex.csv"
USDA_FOOD_ACCESS_PATH: Path = DATA_RAW_DIR / "USDA-FoodAccess.csv"
METADATA_PATH: Path = DATA_RAW_DIR / "Metadata.xlsx"
GEOJSON_PATH: Path = DATA_RAW_DIR / "jacksonville_zctas.geojson"

# ---------------------------------------------------------------------------
# Processed / output file paths
# ---------------------------------------------------------------------------
MERGED_DATA_PATH: Path = DATA_PROCESSED_DIR / "merged_jacksonville.csv"
DESERT_SCORES_PATH: Path = REPORTS_OUTPUTS_DIR / "desert_scores.csv"
INTERVENTION_RECOMMENDATIONS_PATH: Path = (
    REPORTS_OUTPUTS_DIR / "intervention_recommendations.json"
)
CHOROPLETH_MAP_PATH: Path = REPORTS_OUTPUTS_DIR / "resource_desert_map.html"

FIGURE_BAR_CHART: Path = REPORTS_FIGURES_DIR / "desert_scores_bar_chart.png"
FIGURE_HEALTH_SCATTER: Path = (
    REPORTS_FIGURES_DIR / "preventative_asset_vs_health_outcome.png"
)
FIGURE_INTERVENTION_HEATMAP: Path = (
    REPORTS_FIGURES_DIR / "intervention_impact_heatmap.png"
)

# ---------------------------------------------------------------------------
# Column name constants  (exact names as they appear in raw CSV files)
# ---------------------------------------------------------------------------

# Shared across all datasets (mySidewalk export format)
COL_FEATURE_LABEL: str = "feature label"
COL_GEOID: str = "geoid"
COL_ZIP: str = "zip_code"  # standardised name after cleaning

# Census-Demographics
COL_TOTAL_POPULATION: str = "Total Population (2020-2024)"

# Census-Housing & Poverty
COL_POVERTY_COUNT: str = "People Below Poverty Level (2020-2024)"
COL_MEDIAN_INCOME: str = "Median Household Income (2020-2024)"
COL_HOUSING_COST_BURDEN: str = "Excessive Housing Costs (30%+ of Income) (2020-2024)"

# CDC PLACES
COL_POOR_MENTAL_HEALTH: str = "Poor Mental Health Among Adults (2023)"
COL_OBESITY: str = "Obesity Among Adults (2023)"
COL_NO_PHYSICAL_ACTIVITY: str = "No Leisure-Time Physical Activity Among Adults (2023)"
COL_LIFE_EXPECTANCY: str = "Life Expectancy at Birth (2010-2015)"

# HealthCareWorkers
COL_PRIMARY_CARE_RATIO: str = "Primary Care Physician Ratio (2025)"
COL_NP_RATIO: str = "Primary Care Nurse Practitioner Ratio (2025)"
COL_CHILD_CARE_CENTERS: str = "Child Care Centers (2023)"

# HealthCareAccess
COL_UNINSURED_COUNT: str = "People without Health Insurance (2020-2024)"
COL_INSURED_COUNT: str = "People with Health Insurance (2020-2024)"
COL_TOTAL_HEALTHCARE_WORKERS: str = "Total Health Care Workers (2025)"
COL_MENTAL_HEALTH_PROVIDERS: str = "Mental Health Providers (2025)"

# Parks
COL_PARK_COUNT: str = "Number of Parks (2018)"
COL_PARK_COVERAGE_PCT: str = "Percent Area Covered by Parks (2018)"
COL_PARK_AREA_ACRES: str = "Park Area (acres) (2018)"

# Social Vulnerability Index
COL_SVI_SCORE: str = "Social Vulnerability Index Within the State (2022)"
COL_SVI_VULNERABLE_FACTORS: str = (
    "Social Vulnerability Index Highly Vulnerable Factors Within the State (2022)"
)

# USDA Food Access
COL_FOOD_LOW_ACCESS_HALF_MILE: str = (
    "People 1/2 Mile Urban/10 Miles Rural with Low Access to Healthy Food (2019)"
)
COL_FOOD_LOW_ACCESS_1_MILE: str = (
    "People 1 Miles Urban/10 Miles Rural with Low Access to Healthy Food (2019)"
)
COL_FOOD_LOW_ACCESS_20_MILE: str = (
    "People 1 Mile Urban/20 Miles Rural with Low Access to Healthy Food (2019)"
)
COL_FOOD_LOW_INCOME: str = "Low Income People (USDA) (2019)"

# FEMA
COL_FEMA_RESILIENCE: str = "Environmental Hazard Community Resilience Score (2025)"
COL_FEMA_ANNUAL_LOSS: str = "Environmental Hazard Expected Annual Loss Total (2025)"
COL_FEMA_SOCIAL_VULN: str = "Social Vulnerability to Environmental Hazards (2024)"

# ---------------------------------------------------------------------------
# Derived column names (created during feature engineering)
# ---------------------------------------------------------------------------
COL_POVERTY_RATE: str = "poverty_rate"
COL_UNINSURED_RATE: str = "uninsured_rate"
COL_FOOD_LOW_ACCESS_PCT: str = "food_low_access_pct"
COL_DISEASE_BURDEN: str = "disease_burden"
COL_DEMAND_FACTOR: str = "demand_factor"
COL_SUPPLY_GAP_HEALTHCARE: str = "supply_gap_healthcare"
COL_SUPPLY_GAP_FOOD: str = "supply_gap_food"
COL_SUPPLY_GAP_PARKS: str = "supply_gap_parks"
COL_SUPPLY_GAP_INSURANCE: str = "supply_gap_insurance"
COL_DESERT_SCORE: str = "desert_score"
COL_DESERT_RANK: str = "desert_rank"
COL_TOP_GAP_CATEGORY: str = "top_gap_category"

# ---------------------------------------------------------------------------
# Dataset keys (used as dict keys in the pipeline)
# ---------------------------------------------------------------------------
KEY_CDC = "cdc_places"
KEY_CENSUS_DEMO = "census_demographics"
KEY_CENSUS_HOUSING = "census_housing_poverty"
KEY_FEMA = "fema"
KEY_HEALTHCARE_ACCESS = "healthcare_access"
KEY_HEALTHCARE_WORKERS = "healthcare_workers"
KEY_PARKS = "parks"
KEY_SVI = "social_vulnerability"
KEY_USDA = "usda_food_access"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def get_logger(name: str) -> logging.Logger:
    """Return a consistently configured logger.

    Args:
        name: Logger name, typically ``__name__`` of the calling module.

    Returns:
        Configured :class:`logging.Logger` instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
