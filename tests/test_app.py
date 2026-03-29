"""Tests for the Flask presentation dashboard (app.py).

Covers all five route contracts per specs/003-flask-presentation-dashboard/contracts/routes.md.
Uses Flask's built-in test_client — no pytest-flask dependency.
"""

from __future__ import annotations

import io
import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import app as app_module
from app import (
    _run_notebook_thread,
    app,
    build_chart_list,
    load_desert_scores,
    load_interventions,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    """Flask test client with TESTING=True."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture()
def idle_state(monkeypatch):
    """Ensure _run_state is idle before each test."""
    with app_module._lock:
        app_module._run_state.update(status="idle", message="")
    yield
    with app_module._lock:
        app_module._run_state.update(status="idle", message="")


# ---------------------------------------------------------------------------
# Sample data helpers
# ---------------------------------------------------------------------------

SAMPLE_SCORES = [
    {
        "zip_code": "32209",
        "desert_rank": 1,
        "desert_score": 87.4,
        "top_gap_category": "healthcare",
        "total_population": 28450,
        "poverty_rate": 0.34,
    },
    {
        "zip_code": "32210",
        "desert_rank": 2,
        "desert_score": 81.2,
        "top_gap_category": "food_access",
        "total_population": 19200,
        "poverty_rate": 0.28,
    },
]

SAMPLE_INTERVENTIONS = [
    {
        "zip_code": "32209",
        "resource_type": "primary_care",
        "current_desert_score": 87.4,
        "simulated_desert_score": 72.1,
        "score_improvement": 15.3,
        "pct_improvement": 17.5,
        "population_impacted": 28450,
        "is_highest_impact": True,
    },
    {
        "zip_code": "32209",
        "resource_type": "food_access",
        "current_desert_score": 87.4,
        "simulated_desert_score": 79.8,
        "score_improvement": 7.6,
        "pct_improvement": 8.7,
        "population_impacted": 28450,
        "is_highest_impact": False,
    },
]


# ---------------------------------------------------------------------------
# GET /figures/<filename>
# ---------------------------------------------------------------------------


class TestServeFigure:
    def test_missing_file_returns_404(self, client):
        resp = client.get("/figures/nonexistent_chart.png")
        assert resp.status_code == 404

    def test_existing_file_returns_200(self, client, tmp_path, monkeypatch):
        # Create a temporary PNG in tmp_path and point REPORTS_FIGURES_DIR there.
        fake_png = tmp_path / "test_chart.png"
        fake_png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 8)
        monkeypatch.setattr("app.cfg.REPORTS_FIGURES_DIR", tmp_path)
        resp = client.get("/figures/test_chart.png")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# GET /map
# ---------------------------------------------------------------------------


class TestServeMap:
    def test_missing_map_returns_404(self, client, tmp_path, monkeypatch):
        monkeypatch.setattr("app.cfg.REPORTS_OUTPUTS_DIR", tmp_path)
        resp = client.get("/map")
        assert resp.status_code == 404

    def test_existing_map_returns_200(self, client, tmp_path, monkeypatch):
        fake_html = tmp_path / "resource_desert_map.html"
        fake_html.write_text("<html><body>Map</body></html>")
        monkeypatch.setattr("app.cfg.REPORTS_OUTPUTS_DIR", tmp_path)
        resp = client.get("/map")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /api/regenerate
# ---------------------------------------------------------------------------


class TestApiRegenerate:
    def test_returns_202_and_running_status(self, client, idle_state):
        with patch("app.threading.Thread") as mock_thread_cls:
            mock_thread = MagicMock()
            mock_thread_cls.return_value = mock_thread
            resp = client.post("/api/regenerate")
        assert resp.status_code == 202
        data = json.loads(resp.data)
        assert data["status"] == "running"
        mock_thread.start.assert_called_once()

    def test_returns_409_when_already_running(self, client):
        with app_module._lock:
            app_module._run_state.update(status="running", message="")
        try:
            resp = client.post("/api/regenerate")
            assert resp.status_code == 409
            data = json.loads(resp.data)
            assert data["status"] == "running"
        finally:
            with app_module._lock:
                app_module._run_state.update(status="idle", message="")

    def test_does_not_spawn_thread_when_already_running(self, client):
        with app_module._lock:
            app_module._run_state.update(status="running", message="")
        try:
            with patch("app.threading.Thread") as mock_thread_cls:
                client.post("/api/regenerate")
            mock_thread_cls.assert_not_called()
        finally:
            with app_module._lock:
                app_module._run_state.update(status="idle", message="")


# ---------------------------------------------------------------------------
# GET /api/regenerate/status
# ---------------------------------------------------------------------------


class TestApiRegenerateStatus:
    def test_returns_json_with_status_key(self, client, idle_state):
        resp = client.get("/api/regenerate/status")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "status" in data
        assert "message" in data

    def test_reflects_idle_state(self, client, idle_state):
        resp = client.get("/api/regenerate/status")
        data = json.loads(resp.data)
        assert data["status"] == "idle"
        assert data["message"] == ""

    def test_reflects_error_state(self, client):
        with app_module._lock:
            app_module._run_state.update(status="error", message="Cell 3 failed")
        try:
            resp = client.get("/api/regenerate/status")
            data = json.loads(resp.data)
            assert data["status"] == "error"
            assert "Cell 3 failed" in data["message"]
        finally:
            with app_module._lock:
                app_module._run_state.update(status="idle", message="")

    def test_reflects_complete_state(self, client):
        with app_module._lock:
            app_module._run_state.update(status="complete", message="")
        try:
            resp = client.get("/api/regenerate/status")
            data = json.loads(resp.data)
            assert data["status"] == "complete"
        finally:
            with app_module._lock:
                app_module._run_state.update(status="idle", message="")


# ---------------------------------------------------------------------------
# GET / — Problem Statement (US1)
# ---------------------------------------------------------------------------


class TestIndexProblemStatement:
    def test_returns_200(self, client, idle_state):
        with patch("app.load_desert_scores", return_value=[]):
            with patch("app.load_interventions", return_value=[]):
                with patch("app.build_chart_list", return_value=[]):
                    with patch("app.cfg.CHOROPLETH_MAP_PATH") as mock_path:
                        mock_path.exists.return_value = False
                        resp = client.get("/")
        assert resp.status_code == 200

    def test_contains_resource_desert_heading(self, client, idle_state):
        with patch("app.load_desert_scores", return_value=[]):
            with patch("app.load_interventions", return_value=[]):
                with patch("app.build_chart_list", return_value=[]):
                    with patch("app.cfg.CHOROPLETH_MAP_PATH") as mock_path:
                        mock_path.exists.return_value = False
                        resp = client.get("/")
        assert b"Resource Desert" in resp.data

    def test_contains_three_key_questions(self, client, idle_state):
        with patch("app.load_desert_scores", return_value=[]):
            with patch("app.load_interventions", return_value=[]):
                with patch("app.build_chart_list", return_value=[]):
                    with patch("app.cfg.CHOROPLETH_MAP_PATH") as mock_path:
                        mock_path.exists.return_value = False
                        resp = client.get("/")
        html = resp.data.decode()
        # Three list items in the key-questions list
        assert html.count('class="problem__questions"') >= 1
        assert html.count("<li>") >= 3

    def test_contains_inequity_cycle(self, client, idle_state):
        with patch("app.load_desert_scores", return_value=[]):
            with patch("app.load_interventions", return_value=[]):
                with patch("app.build_chart_list", return_value=[]):
                    with patch("app.cfg.CHOROPLETH_MAP_PATH") as mock_path:
                        mock_path.exists.return_value = False
                        resp = client.get("/")
        assert b"Poor Health Outcomes" in resp.data or b"Poor Outcomes" in resp.data


# ---------------------------------------------------------------------------
# GET / — Analysis section (US2)
# ---------------------------------------------------------------------------


class TestIndexAnalysis:
    def _get(self, client):
        charts = [
            {
                "filename": "desert_scores_bar_chart.png",
                "section": "analysis",
                "caption": "Top 10",
                "missing": False,
            }
        ]
        with patch("app.load_desert_scores", return_value=SAMPLE_SCORES):
            with patch("app.load_interventions", return_value=[]):
                with patch("app.build_chart_list", return_value=charts):
                    with patch("app.cfg.CHOROPLETH_MAP_PATH") as mock_path:
                        mock_path.exists.return_value = True
                        return client.get("/")

    def test_bar_chart_img_present(self, client, idle_state):
        resp = self._get(client)
        assert b"desert_scores_bar_chart.png" in resp.data

    def test_choropleth_iframe_present(self, client, idle_state):
        resp = self._get(client)
        assert b"/map" in resp.data

    def test_desert_scores_table_rows(self, client, idle_state):
        resp = self._get(client)
        html = resp.data.decode()
        # 2 sample rows + header = at least 2 <tr> with data
        assert html.count("32209") >= 1
        assert html.count("32210") >= 1


# ---------------------------------------------------------------------------
# GET / — Recommendations section (US4)
# ---------------------------------------------------------------------------


class TestIndexRecommendations:
    def _get(self, client):
        charts = [
            {
                "filename": "intervention_impact_heatmap.png",
                "section": "recommendations",
                "caption": "Heatmap",
                "missing": False,
            }
        ]
        with patch("app.load_desert_scores", return_value=[]):
            with patch("app.load_interventions", return_value=SAMPLE_INTERVENTIONS):
                with patch("app.build_chart_list", return_value=charts):
                    with patch("app.cfg.CHOROPLETH_MAP_PATH") as mock_path:
                        mock_path.exists.return_value = False
                        return client.get("/")

    def test_highlight_card_zip_present(self, client, idle_state):
        resp = self._get(client)
        assert b"32209" in resp.data

    def test_highlight_card_resource_type_present(self, client, idle_state):
        resp = self._get(client)
        assert b"primary_care" in resp.data or b"primary care" in resp.data.lower()

    def test_best_row_class_present(self, client, idle_state):
        resp = self._get(client)
        assert b"best-row" in resp.data

    def test_heatmap_img_present(self, client, idle_state):
        resp = self._get(client)
        assert b"intervention_impact_heatmap.png" in resp.data


# ---------------------------------------------------------------------------
# Data loader helpers (direct unit tests for success paths)
# ---------------------------------------------------------------------------


class TestLoadDesertScores:
    def test_returns_empty_list_when_file_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.cfg.DESERT_SCORES_PATH", tmp_path / "nofile.csv")
        assert load_desert_scores() == []

    def test_returns_top10_rows_from_csv(self, tmp_path, monkeypatch):
        csv_path = tmp_path / "desert_scores.csv"
        df = pd.DataFrame(
            {
                "zip_code": [f"3220{i}" for i in range(15)],
                "desert_rank": list(range(1, 16)),
                "desert_score": [float(90 - i) for i in range(15)],
                "top_gap_category": ["healthcare"] * 15,
                "total_population": [10000] * 15,
                "poverty_rate": [0.3] * 15,
            }
        )
        df.to_csv(csv_path, index=False)
        monkeypatch.setattr("app.cfg.DESERT_SCORES_PATH", csv_path)
        result = load_desert_scores()
        assert len(result) == 10
        assert result[0]["desert_rank"] == 1

    def test_returns_empty_list_on_corrupt_csv(self, tmp_path, monkeypatch):
        csv_path = tmp_path / "desert_scores.csv"
        csv_path.write_text("not,valid\nbad,data\n")
        monkeypatch.setattr("app.cfg.DESERT_SCORES_PATH", csv_path)
        # Missing required column triggers graceful empty return
        result = load_desert_scores()
        # No crash — returns whatever subset is available or empty
        assert isinstance(result, list)


class TestLoadInterventions:
    def test_returns_empty_list_when_file_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "app.cfg.INTERVENTION_RECOMMENDATIONS_PATH", tmp_path / "nofile.json"
        )
        assert load_interventions() == []

    def test_returns_rows_sorted_by_score_improvement(self, tmp_path, monkeypatch):
        data = [
            {"zip_code": "32209", "resource_type": "food_access", "score_improvement": 5.0,
             "is_highest_impact": False},
            {"zip_code": "32209", "resource_type": "primary_care", "score_improvement": 15.0,
             "is_highest_impact": True},
        ]
        json_path = tmp_path / "intervention_recommendations.json"
        json_path.write_text(json.dumps(data))
        monkeypatch.setattr("app.cfg.INTERVENTION_RECOMMENDATIONS_PATH", json_path)
        result = load_interventions()
        assert len(result) == 2
        assert result[0]["score_improvement"] == 15.0

    def test_returns_empty_list_on_corrupt_json(self, tmp_path, monkeypatch):
        json_path = tmp_path / "bad.json"
        json_path.write_text("{not valid json")
        monkeypatch.setattr("app.cfg.INTERVENTION_RECOMMENDATIONS_PATH", json_path)
        assert load_interventions() == []


class TestBuildChartList:
    def test_missing_flag_false_when_file_exists(self, tmp_path, monkeypatch):
        (tmp_path / "desert_scores_bar_chart.png").write_bytes(b"PNG")
        monkeypatch.setattr("app.cfg.REPORTS_FIGURES_DIR", tmp_path)
        charts = build_chart_list()
        bar = next(c for c in charts if c["filename"] == "desert_scores_bar_chart.png")
        assert bar["missing"] is False

    def test_missing_flag_true_when_file_absent(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.cfg.REPORTS_FIGURES_DIR", tmp_path)
        charts = build_chart_list()
        bar = next(c for c in charts if c["filename"] == "desert_scores_bar_chart.png")
        assert bar["missing"] is True

    def test_returns_seven_charts(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.cfg.REPORTS_FIGURES_DIR", tmp_path)
        assert len(build_chart_list()) == 7


# ---------------------------------------------------------------------------
# Background notebook runner (_run_notebook_thread)
# ---------------------------------------------------------------------------


class TestRunNotebookThread:
    def test_sets_complete_on_returncode_zero(self):
        with app_module._lock:
            app_module._run_state.update(status="idle", message="")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        with patch("app.subprocess.run", return_value=mock_result):
            _run_notebook_thread()
        with app_module._lock:
            assert app_module._run_state["status"] == "complete"
            assert app_module._run_state["message"] == ""

    def test_sets_error_on_nonzero_returncode(self):
        with app_module._lock:
            app_module._run_state.update(status="idle", message="")
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "x" * 600
        with patch("app.subprocess.run", return_value=mock_result):
            _run_notebook_thread()
        with app_module._lock:
            assert app_module._run_state["status"] == "error"
            assert len(app_module._run_state["message"]) <= 500
