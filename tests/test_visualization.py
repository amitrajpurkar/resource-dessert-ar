"""Unit tests for src.visualization — T027.

Mocks ``matplotlib.figure.Figure.savefig`` and ``folium.Map.save`` so no
real files are written.  Asserts that every plot function:
  - calls save with a path inside the provided output directory
  - produces figures with non-empty title and axis labels
  - uses DPI ≥ 150

Tests use synthetic fixture DataFrames only; no real data files are loaded.

Patching notes
--------------
- ``_CaptureSavefig`` replaces ``Figure.savefig`` as a callable instance.
  Because callable instances are NOT descriptors, Python does NOT bind the
  Figure as ``self`` when looking up the attribute on the instance.  The
  callable therefore receives ``(fname, *args, **kwargs)`` — no Figure arg.
- For tests that need the Figure object (title/label checks), we use
  ``patch.object(..., autospec=True)`` so that ``self`` IS included in
  ``call_args[0][0]``.
"""

import json
from pathlib import Path
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")
import matplotlib.figure  # noqa: E402
import pandas as pd
import pytest

from src import config as cfg
from src.models import RESOURCE_TYPES
from src.visualization import (
    create_choropleth_map,
    plot_category_view,
    plot_desert_scores_bar_chart,
    plot_intervention_impact_heatmap,
    plot_preventative_vs_outcome,
)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


class _CaptureSavefig:
    """Records Figure.savefig calls without writing to disk.

    Because callable instances are not descriptors, ``patch.object`` does NOT
    bind the Figure as an implicit first argument.  ``__call__`` therefore
    starts with ``fname`` directly.
    """

    def __init__(self):
        self.path: str | None = None
        self.dpi: int | None = None
        self.call_count: int = 0

    def __call__(self, fname, *args, **kwargs):
        self.path = str(fname)
        self.dpi = kwargs.get("dpi")
        self.call_count += 1


def _autospec_dpi(mock_sf) -> int:
    """Return the dpi kwarg from an autospec'd Figure.savefig mock."""
    return mock_sf.call_args[1].get("dpi", 0)


def _autospec_fig(mock_sf) -> matplotlib.figure.Figure:
    """Return the Figure instance from an autospec'd Figure.savefig mock."""
    # autospec binds self → call_args positional args are (fig, fname, ...)
    return mock_sf.call_args[0][0]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_desert_scores_df_vis() -> pd.DataFrame:
    """Desert scores with all columns needed by visualization functions."""
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
            cfg.COL_TOP_GAP_CATEGORY: [
                "parks",
                "insurance",
                "healthcare",
                "healthcare",
                "parks",
            ],
            cfg.COL_TOTAL_POPULATION: [5000, 6000, 7000, 8000, 9000],
            cfg.COL_POVERTY_RATE: [0.16, 0.23, 0.086, 0.038, 0.133],
        }
    )


@pytest.fixture()
def sample_merged_df_vis() -> pd.DataFrame:
    """Merged DataFrame with columns needed by scatter-plot function."""
    return pd.DataFrame(
        {
            cfg.COL_ZIP: ["32201", "32202", "32203", "32204", "32205"],
            cfg.COL_TOTAL_POPULATION: [5000, 6000, 7000, 8000, 9000],
            cfg.COL_POVERTY_RATE: [0.16, 0.23, 0.086, 0.038, 0.133],
            cfg.COL_POOR_MENTAL_HEALTH: [22.0, 41.1, 18.0, 15.0, 35.0],
            cfg.COL_OBESITY: [38.0, 45.0, 30.0, 25.0, 40.0],
            cfg.COL_PRIMARY_CARE_RATIO: [120.0, 354.3, 200.0, 84.7, 200.0],
            cfg.COL_FOOD_LOW_ACCESS_PCT: [0.24, 0.22, 0.057, 0.484, 0.222],
            cfg.COL_PARK_COVERAGE_PCT: [1.0, 3.1, 8.0, 1.7, 2.5],
        }
    )


@pytest.fixture()
def sample_interventions_df() -> pd.DataFrame:
    """Synthetic interventions DataFrame (after ranking, one highest-impact row)."""
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
    rows[0]["score_improvement"] = 99.0
    rows[0]["pct_improvement"] = 90.0
    rows[0]["is_highest_impact"] = True
    return pd.DataFrame(rows)


@pytest.fixture()
def minimal_geojson(tmp_path: Path) -> Path:
    """Minimal valid GeoJSON with ZCTA5CE20 property."""
    data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"ZCTA5CE20": "32201"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-81.8, 30.2],
                            [-81.7, 30.2],
                            [-81.7, 30.3],
                            [-81.8, 30.3],
                            [-81.8, 30.2],
                        ]
                    ],
                },
            }
        ],
    }
    path = tmp_path / "jacksonville_zctas.geojson"
    path.write_text(json.dumps(data))
    return path


# ---------------------------------------------------------------------------
# T027: plot_desert_scores_bar_chart
# ---------------------------------------------------------------------------


class TestPlotDesertScoresBarChart:
    def test_savefig_called_once(
        self, sample_desert_scores_df_vis: pd.DataFrame, tmp_path: Path
    ):
        cap = _CaptureSavefig()
        with patch.object(matplotlib.figure.Figure, "savefig", cap):
            plot_desert_scores_bar_chart(
                sample_desert_scores_df_vis, figures_dir=tmp_path
            )
        assert cap.call_count == 1

    def test_savefig_path_in_figures_dir(
        self, sample_desert_scores_df_vis: pd.DataFrame, tmp_path: Path
    ):
        cap = _CaptureSavefig()
        with patch.object(matplotlib.figure.Figure, "savefig", cap):
            plot_desert_scores_bar_chart(
                sample_desert_scores_df_vis, figures_dir=tmp_path
            )
        assert str(tmp_path) in cap.path

    def test_savefig_filename_matches_config(
        self, sample_desert_scores_df_vis: pd.DataFrame, tmp_path: Path
    ):
        cap = _CaptureSavefig()
        with patch.object(matplotlib.figure.Figure, "savefig", cap):
            plot_desert_scores_bar_chart(
                sample_desert_scores_df_vis, figures_dir=tmp_path
            )
        assert cfg.FIGURE_BAR_CHART.name in cap.path

    def test_dpi_at_least_150(
        self, sample_desert_scores_df_vis: pd.DataFrame, tmp_path: Path
    ):
        with patch.object(
            matplotlib.figure.Figure, "savefig", autospec=True
        ) as mock_sf:
            plot_desert_scores_bar_chart(
                sample_desert_scores_df_vis, figures_dir=tmp_path
            )
        assert _autospec_dpi(mock_sf) >= 150

    def test_figure_has_title_and_labels(
        self, sample_desert_scores_df_vis: pd.DataFrame, tmp_path: Path
    ):
        with patch.object(
            matplotlib.figure.Figure, "savefig", autospec=True
        ) as mock_sf:
            plot_desert_scores_bar_chart(
                sample_desert_scores_df_vis, figures_dir=tmp_path
            )
        assert mock_sf.called
        ax = _autospec_fig(mock_sf).axes[0]
        assert ax.get_title() != ""
        assert ax.get_xlabel() != ""
        assert ax.get_ylabel() != ""


# ---------------------------------------------------------------------------
# T027: create_choropleth_map
# ---------------------------------------------------------------------------


class TestCreateChoroplethMap:
    def test_raises_if_geojson_missing(
        self, sample_desert_scores_df_vis: pd.DataFrame, tmp_path: Path
    ):
        """FileNotFoundError raised when GeoJSON is absent."""
        missing = tmp_path / "no_such.geojson"
        with pytest.raises(FileNotFoundError, match="GeoJSON"):
            create_choropleth_map(
                sample_desert_scores_df_vis,
                geojson_path=missing,
                outputs_dir=tmp_path,
            )

    def test_map_save_called_once(
        self,
        sample_desert_scores_df_vis: pd.DataFrame,
        minimal_geojson: Path,
        tmp_path: Path,
    ):
        """folium Map.save is called exactly once."""
        import folium

        save_calls: list[str] = []

        def mock_save(self_map, path, *args, **kwargs):
            save_calls.append(str(path))

        with patch.object(folium.Map, "save", mock_save):
            create_choropleth_map(
                sample_desert_scores_df_vis,
                geojson_path=minimal_geojson,
                outputs_dir=tmp_path,
            )
        assert len(save_calls) == 1

    def test_map_save_path_in_outputs_dir(
        self,
        sample_desert_scores_df_vis: pd.DataFrame,
        minimal_geojson: Path,
        tmp_path: Path,
    ):
        """HTML save path is inside the provided outputs_dir and ends with .html."""
        import folium

        save_calls: list[str] = []

        def mock_save(self_map, path, *args, **kwargs):
            save_calls.append(str(path))

        with patch.object(folium.Map, "save", mock_save):
            create_choropleth_map(
                sample_desert_scores_df_vis,
                geojson_path=minimal_geojson,
                outputs_dir=tmp_path,
            )
        assert str(tmp_path) in save_calls[0]
        assert save_calls[0].endswith(".html")


# ---------------------------------------------------------------------------
# T027: plot_preventative_vs_outcome
# ---------------------------------------------------------------------------


class TestPlotPreventativeVsOutcome:
    def test_savefig_called_once(
        self, sample_merged_df_vis: pd.DataFrame, tmp_path: Path
    ):
        cap = _CaptureSavefig()
        with patch.object(matplotlib.figure.Figure, "savefig", cap):
            plot_preventative_vs_outcome(
                sample_merged_df_vis,
                asset_col=cfg.COL_PRIMARY_CARE_RATIO,
                outcome_col=cfg.COL_POOR_MENTAL_HEALTH,
                figures_dir=tmp_path,
            )
        assert cap.call_count == 1

    def test_savefig_path_matches_config(
        self, sample_merged_df_vis: pd.DataFrame, tmp_path: Path
    ):
        cap = _CaptureSavefig()
        with patch.object(matplotlib.figure.Figure, "savefig", cap):
            plot_preventative_vs_outcome(
                sample_merged_df_vis,
                asset_col=cfg.COL_PRIMARY_CARE_RATIO,
                outcome_col=cfg.COL_POOR_MENTAL_HEALTH,
                figures_dir=tmp_path,
            )
        assert cfg.FIGURE_HEALTH_SCATTER.name in cap.path

    def test_dpi_at_least_150(self, sample_merged_df_vis: pd.DataFrame, tmp_path: Path):
        with patch.object(
            matplotlib.figure.Figure, "savefig", autospec=True
        ) as mock_sf:
            plot_preventative_vs_outcome(
                sample_merged_df_vis,
                asset_col=cfg.COL_PRIMARY_CARE_RATIO,
                outcome_col=cfg.COL_POOR_MENTAL_HEALTH,
                figures_dir=tmp_path,
            )
        assert _autospec_dpi(mock_sf) >= 150

    def test_figure_has_title_and_labels(
        self, sample_merged_df_vis: pd.DataFrame, tmp_path: Path
    ):
        with patch.object(
            matplotlib.figure.Figure, "savefig", autospec=True
        ) as mock_sf:
            plot_preventative_vs_outcome(
                sample_merged_df_vis,
                asset_col=cfg.COL_PRIMARY_CARE_RATIO,
                outcome_col=cfg.COL_POOR_MENTAL_HEALTH,
                figures_dir=tmp_path,
            )
        assert mock_sf.called
        ax = _autospec_fig(mock_sf).axes[0]
        assert ax.get_title() != ""
        assert ax.get_xlabel() != ""
        assert ax.get_ylabel() != ""


# ---------------------------------------------------------------------------
# T027: plot_intervention_impact_heatmap
# ---------------------------------------------------------------------------


class TestPlotInterventionImpactHeatmap:
    def test_savefig_called_once(
        self, sample_interventions_df: pd.DataFrame, tmp_path: Path
    ):
        cap = _CaptureSavefig()
        with patch.object(matplotlib.figure.Figure, "savefig", cap):
            plot_intervention_impact_heatmap(
                sample_interventions_df, figures_dir=tmp_path
            )
        assert cap.call_count == 1

    def test_savefig_path_matches_config(
        self, sample_interventions_df: pd.DataFrame, tmp_path: Path
    ):
        cap = _CaptureSavefig()
        with patch.object(matplotlib.figure.Figure, "savefig", cap):
            plot_intervention_impact_heatmap(
                sample_interventions_df, figures_dir=tmp_path
            )
        assert cfg.FIGURE_INTERVENTION_HEATMAP.name in cap.path

    def test_dpi_at_least_150(
        self, sample_interventions_df: pd.DataFrame, tmp_path: Path
    ):
        with patch.object(
            matplotlib.figure.Figure, "savefig", autospec=True
        ) as mock_sf:
            plot_intervention_impact_heatmap(
                sample_interventions_df, figures_dir=tmp_path
            )
        assert _autospec_dpi(mock_sf) >= 150

    def test_figure_has_title_and_labels(
        self, sample_interventions_df: pd.DataFrame, tmp_path: Path
    ):
        with patch.object(
            matplotlib.figure.Figure, "savefig", autospec=True
        ) as mock_sf:
            plot_intervention_impact_heatmap(
                sample_interventions_df, figures_dir=tmp_path
            )
        assert mock_sf.called
        ax = _autospec_fig(mock_sf).axes[0]
        assert ax.get_title() != ""
        assert ax.get_xlabel() != ""
        assert ax.get_ylabel() != ""


# ---------------------------------------------------------------------------
# T027: plot_category_view
# ---------------------------------------------------------------------------


class TestPlotCategoryView:
    @pytest.mark.parametrize(
        "category",
        ["healthcare", "food_access", "parks", "insurance"],
    )
    def test_savefig_called_once_per_category(
        self,
        sample_desert_scores_df_vis: pd.DataFrame,
        tmp_path: Path,
        category: str,
    ):
        cap = _CaptureSavefig()
        with patch.object(matplotlib.figure.Figure, "savefig", cap):
            plot_category_view(
                sample_desert_scores_df_vis, category=category, figures_dir=tmp_path
            )
        assert cap.call_count == 1

    def test_savefig_path_includes_category_name(
        self, sample_desert_scores_df_vis: pd.DataFrame, tmp_path: Path
    ):
        cap = _CaptureSavefig()
        with patch.object(matplotlib.figure.Figure, "savefig", cap):
            plot_category_view(
                sample_desert_scores_df_vis, category="healthcare", figures_dir=tmp_path
            )
        assert "healthcare" in cap.path

    def test_savefig_path_in_figures_dir(
        self, sample_desert_scores_df_vis: pd.DataFrame, tmp_path: Path
    ):
        cap = _CaptureSavefig()
        with patch.object(matplotlib.figure.Figure, "savefig", cap):
            plot_category_view(
                sample_desert_scores_df_vis, category="parks", figures_dir=tmp_path
            )
        assert str(tmp_path) in cap.path

    def test_dpi_at_least_150(
        self, sample_desert_scores_df_vis: pd.DataFrame, tmp_path: Path
    ):
        with patch.object(
            matplotlib.figure.Figure, "savefig", autospec=True
        ) as mock_sf:
            plot_category_view(
                sample_desert_scores_df_vis,
                category="food_access",
                figures_dir=tmp_path,
            )
        assert _autospec_dpi(mock_sf) >= 150

    def test_figure_has_title_and_labels(
        self, sample_desert_scores_df_vis: pd.DataFrame, tmp_path: Path
    ):
        with patch.object(
            matplotlib.figure.Figure, "savefig", autospec=True
        ) as mock_sf:
            plot_category_view(
                sample_desert_scores_df_vis, category="insurance", figures_dir=tmp_path
            )
        assert mock_sf.called
        ax = _autospec_fig(mock_sf).axes[0]
        assert ax.get_title() != ""
        assert ax.get_xlabel() != ""
        assert ax.get_ylabel() != ""
