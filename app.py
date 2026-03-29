"""Flask presentation dashboard for the Resource Desert analysis.

Single-page scrollable app serving pre-generated pipeline outputs to
datathon judges. Provides a background notebook regeneration endpoint
for live re-execution during presentation.
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

import pandas as pd
from flask import Flask, jsonify, render_template, send_from_directory

import src.config as cfg

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "webapp" / "templates"),
    static_folder=str(BASE_DIR / "webapp" / "static"),
)

# ---------------------------------------------------------------------------
# Notebook run state (protected by _lock)
# ---------------------------------------------------------------------------
_run_state: dict[str, str] = {"status": "idle", "message": ""}
_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Known chart images (order = display order within each section)
# ---------------------------------------------------------------------------
_CHART_IMAGES: list[dict[str, str]] = [
    {
        "filename": "desert_scores_bar_chart.png",
        "section": "analysis",
        "caption": "Top 10 Most Underserved Jacksonville ZIP Codes",
    },
    {
        "filename": "preventative_asset_vs_health_outcome.png",
        "section": "observations",
        "caption": "Preventative Asset vs Health Outcome (regression)",
    },
    {
        "filename": "intervention_impact_heatmap.png",
        "section": "recommendations",
        "caption": "Gap-Closure Simulation: Projected Improvement by Intervention",
    },
    {
        "filename": "category_healthcare_view.png",
        "section": "category",
        "caption": "Healthcare Supply Gap by ZIP Code",
    },
    {
        "filename": "category_food_access_view.png",
        "section": "category",
        "caption": "Food Access Supply Gap by ZIP Code",
    },
    {
        "filename": "category_parks_view.png",
        "section": "category",
        "caption": "Parks Supply Gap by ZIP Code",
    },
    {
        "filename": "category_insurance_view.png",
        "section": "category",
        "caption": "Insurance Coverage Gap by ZIP Code",
    },
]


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------
def load_desert_scores() -> list[dict[str, Any]]:
    """Load the top-10 most underserved ZIP codes from desert_scores.csv.

    Returns:
        List of dicts with display-subset fields, sorted by desert_rank asc.
        Returns an empty list if the file is missing or unreadable.
    """
    path = cfg.DESERT_SCORES_PATH
    if not path.exists():
        logger.warning("desert_scores.csv not found at %s", path)
        return []
    try:
        df = pd.read_csv(path)
        # Normalise population column name from pipeline output
        if cfg.COL_TOTAL_POPULATION in df.columns:
            df = df.rename(columns={cfg.COL_TOTAL_POPULATION: "total_population"})
        display_cols = [
            "zip_code",
            "desert_rank",
            "desert_score",
            "top_gap_category",
            "total_population",
            "poverty_rate",
        ]
        available = [c for c in display_cols if c in df.columns]
        df = df[available].sort_values("desert_rank").head(10)
        logger.info("Loaded %d desert score rows", len(df))
        return df.to_dict(orient="records")
    except Exception as exc:
        logger.error("Failed to load desert_scores.csv: %s", exc)
        return []


def load_interventions() -> list[dict[str, Any]]:
    """Load all 20 intervention recommendations, sorted by score_improvement desc.

    Returns:
        List of dicts with all Intervention fields.
        Returns an empty list if the file is missing or unreadable.
    """
    path = cfg.INTERVENTION_RECOMMENDATIONS_PATH
    if not path.exists():
        logger.warning("intervention_recommendations.json not found at %s", path)
        return []
    try:
        with path.open() as fh:
            data = json.load(fh)
        rows = sorted(data, key=lambda r: r.get("score_improvement", 0), reverse=True)
        logger.info("Loaded %d intervention rows", len(rows))
        return rows
    except Exception as exc:
        logger.error("Failed to load intervention_recommendations.json: %s", exc)
        return []


def build_chart_list() -> list[dict[str, Any]]:
    """Return chart descriptors with missing-file flags.

    Returns:
        List of ChartImage dicts, each with a ``missing`` bool field.
    """
    charts = []
    for item in _CHART_IMAGES:
        charts.append(
            {
                **item,
                "missing": not (cfg.REPORTS_FIGURES_DIR / item["filename"]).exists(),
            }
        )
    return charts


# ---------------------------------------------------------------------------
# Background notebook runner
# ---------------------------------------------------------------------------
def _run_notebook_thread() -> None:
    """Execute the analysis notebook as a background subprocess.

    Updates ``_run_state`` under ``_lock`` on start, completion, and failure.
    """
    with _lock:
        _run_state.update(status="running", message="")
    logger.info("Notebook execution started")
    result = subprocess.run(
        [
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--inplace",
            "--ExecutePreprocessor.kernel_name=prob1-resource-desert",
            "--ExecutePreprocessor.timeout=600",
            str(BASE_DIR / "notebooks" / "resource_desert_analysis.ipynb"),
        ],
        capture_output=True,
        text=True,
    )
    with _lock:
        if result.returncode == 0:
            _run_state.update(status="complete", message="")
            logger.info("Notebook execution completed successfully")
        else:
            _run_state.update(status="error", message=result.stderr[-500:])
            logger.error("Notebook execution failed: %s", result.stderr[-200:])


# ---------------------------------------------------------------------------
# Routes: file serving
# ---------------------------------------------------------------------------
@app.route("/figures/<path:filename>")
def serve_figure(filename: str):
    """Serve a pre-generated PNG chart from reports/figures/.

    Args:
        filename: Basename of the PNG file.

    Returns:
        PNG file response, or 404 if not found.
    """
    return send_from_directory(str(cfg.REPORTS_FIGURES_DIR), filename)


@app.route("/map")
def serve_map():
    """Serve the Folium choropleth HTML map.

    Returns:
        HTML file response, or 404 if not found.
    """
    return send_from_directory(str(cfg.REPORTS_OUTPUTS_DIR), "resource_desert_map.html")


# ---------------------------------------------------------------------------
# Routes: notebook regeneration API
# ---------------------------------------------------------------------------
@app.route("/api/regenerate", methods=["POST"])
def api_regenerate():
    """Trigger full notebook execution as a background thread.

    Returns:
        202 JSON if run started, 409 JSON if already running.
    """
    with _lock:
        current = _run_state["status"]
    if current == "running":
        return jsonify({"status": "running", "message": "Already running"}), 409
    thread = threading.Thread(target=_run_notebook_thread, daemon=False)
    thread.start()
    return jsonify({"status": "running", "message": ""}), 202


@app.route("/api/regenerate/status")
def api_regenerate_status():
    """Return the current notebook run state.

    Returns:
        JSON with ``status`` and ``message`` fields.
    """
    with _lock:
        state = dict(_run_state)
    return jsonify(state)


# ---------------------------------------------------------------------------
# Routes: main page
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Render the single-page presentation dashboard.

    Returns:
        Rendered index.html with all template variables injected.
    """
    desert_scores = load_desert_scores()
    interventions = load_interventions()
    best_intervention = next(
        (r for r in interventions if r.get("is_highest_impact")), None
    )
    charts = build_chart_list()
    map_exists = cfg.CHOROPLETH_MAP_PATH.exists()
    with _lock:
        run_status = _run_state["status"]
        run_message = _run_state["message"]

    return render_template(
        "index.html",
        desert_scores=desert_scores,
        interventions=interventions,
        best_intervention=best_intervention,
        charts=charts,
        map_exists=map_exists,
        run_status=run_status,
        run_message=run_message,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
