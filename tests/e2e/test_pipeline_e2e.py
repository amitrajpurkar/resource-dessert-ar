"""End-to-end pipeline test — T029.

Runs the full pipeline on data/raw/ and validates all expected outputs.

Tag: ``@pytest.mark.e2e`` — requires ``data/raw/`` to be populated with the
real source files.  Excluded from the default unit-test run via
``pytest tests/ -m "not e2e"``.
"""

import json

import pytest

from src import config as cfg
from src.cleaning import clean_datasets
from src.features import (
    compute_desert_score,
    filter_by_service_category,
    merge_datasets,
)
from src.ingestion import load_raw_datasets
from src.models import rank_interventions, run_gap_closure_simulation
from src.visualization import (
    create_choropleth_map,
    plot_category_view,
    plot_desert_scores_bar_chart,
    plot_intervention_impact_heatmap,
    plot_preventative_vs_outcome,
)


@pytest.mark.e2e
class TestFullPipeline:
    """End-to-end validation of every pipeline stage."""

    @pytest.fixture(scope="class")
    def pipeline_outputs(self):
        """Run the full pipeline once and cache outputs for all tests in this class."""
        raw = load_raw_datasets()
        cleaned = clean_datasets(raw)
        merged = merge_datasets(cleaned)
        desert_scores = compute_desert_score(merged)
        interventions = run_gap_closure_simulation(desert_scores, merged, top_n=5)
        ranked = rank_interventions(interventions)
        return {
            "raw": raw,
            "cleaned": cleaned,
            "merged": merged,
            "desert_scores": desert_scores,
            "interventions": interventions,
            "ranked": ranked,
        }

    # ------------------------------------------------------------------
    # Stage 1: Ingestion
    # ------------------------------------------------------------------

    def test_load_raw_returns_9_datasets(self, pipeline_outputs):
        assert len(pipeline_outputs["raw"]) == 9

    def test_each_raw_dataset_has_rows(self, pipeline_outputs):
        for key, df in pipeline_outputs["raw"].items():
            assert len(df) >= 1, f"Dataset '{key}' is empty"

    # ------------------------------------------------------------------
    # Stage 2: Cleaning
    # ------------------------------------------------------------------

    def test_cleaned_zip_codes_are_5_char_strings(self, pipeline_outputs):
        for key, df in pipeline_outputs["cleaned"].items():
            if cfg.COL_ZIP in df.columns:
                assert (
                    df[cfg.COL_ZIP].str.len().eq(5).all()
                ), f"ZIP codes in '{key}' are not all 5 characters"

    def test_no_duplicate_zips_per_dataset(self, pipeline_outputs):
        for key, df in pipeline_outputs["cleaned"].items():
            if cfg.COL_ZIP in df.columns:
                assert (
                    not df[cfg.COL_ZIP].duplicated().any()
                ), f"Duplicate ZIP codes found in '{key}'"

    # ------------------------------------------------------------------
    # Stage 3: Feature engineering — desert_scores.csv
    # ------------------------------------------------------------------

    def test_desert_scores_csv_exists(self, pipeline_outputs):
        assert (
            cfg.DESERT_SCORES_PATH.exists()
        ), f"Expected file not found: {cfg.DESERT_SCORES_PATH}"

    def test_desert_scores_has_expected_columns(self, pipeline_outputs):
        df = pipeline_outputs["desert_scores"]
        for col in [cfg.COL_ZIP, cfg.COL_DESERT_SCORE, cfg.COL_DESERT_RANK]:
            assert col in df.columns, f"Missing column: {col}"

    def test_desert_score_range(self, pipeline_outputs):
        scores = pipeline_outputs["desert_scores"][cfg.COL_DESERT_SCORE]
        assert scores.between(0, 100).all(), "desert_score values outside [0, 100]"

    def test_desert_rank_starts_at_1(self, pipeline_outputs):
        ranks = pipeline_outputs["desert_scores"][cfg.COL_DESERT_RANK]
        assert ranks.min() == 1, "desert_rank does not start at 1"

    def test_no_duplicate_zips_in_desert_scores(self, pipeline_outputs):
        zips = pipeline_outputs["desert_scores"][cfg.COL_ZIP]
        assert not zips.duplicated().any()

    # ------------------------------------------------------------------
    # Stage 4: Gap-closure simulation — intervention_recommendations.json
    # ------------------------------------------------------------------

    def test_intervention_json_exists(self, pipeline_outputs):
        assert (
            cfg.INTERVENTION_RECOMMENDATIONS_PATH.exists()
        ), f"Expected file not found: {cfg.INTERVENTION_RECOMMENDATIONS_PATH}"

    def test_intervention_json_has_20_rows(self, pipeline_outputs):
        data = json.loads(cfg.INTERVENTION_RECOMMENDATIONS_PATH.read_text())
        assert len(data) == 20, f"Expected 20 rows, got {len(data)}"

    def test_exactly_one_highest_impact(self, pipeline_outputs):
        df = pipeline_outputs["ranked"]
        assert df["is_highest_impact"].sum() == 1

    def test_score_improvement_non_negative(self, pipeline_outputs):
        assert (pipeline_outputs["ranked"]["score_improvement"] >= 0).all()

    # ------------------------------------------------------------------
    # Stage 5: Visualizations
    # ------------------------------------------------------------------

    def test_bar_chart_saved(self, pipeline_outputs):
        plot_desert_scores_bar_chart(pipeline_outputs["desert_scores"])
        assert cfg.FIGURE_BAR_CHART.exists()

    def test_health_scatter_saved(self, pipeline_outputs):
        plot_preventative_vs_outcome(
            pipeline_outputs["merged"],
            asset_col=cfg.COL_PRIMARY_CARE_RATIO,
            outcome_col=cfg.COL_POOR_MENTAL_HEALTH,
        )
        assert cfg.FIGURE_HEALTH_SCATTER.exists()

    def test_intervention_heatmap_saved(self, pipeline_outputs):
        plot_intervention_impact_heatmap(pipeline_outputs["ranked"])
        assert cfg.FIGURE_INTERVENTION_HEATMAP.exists()

    def test_choropleth_map_saved(self, pipeline_outputs):
        if not cfg.GEOJSON_PATH.exists():
            pytest.skip("GeoJSON not available — skipping choropleth test")
        create_choropleth_map(pipeline_outputs["desert_scores"])
        assert cfg.CHOROPLETH_MAP_PATH.exists()
        assert cfg.CHOROPLETH_MAP_PATH.stat().st_size > 0

    def test_category_bar_charts_saved(self, pipeline_outputs):
        for category in ["healthcare", "food_access", "parks", "insurance"]:
            cat_df = filter_by_service_category(
                pipeline_outputs["desert_scores"], category
            )
            plot_category_view(cat_df, category=category)
            expected = cfg.REPORTS_FIGURES_DIR / f"category_{category}_view.png"
            assert expected.exists(), f"Category chart not saved: {expected}"
