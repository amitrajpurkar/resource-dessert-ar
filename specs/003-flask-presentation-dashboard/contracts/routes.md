# Route Contracts: Flask Presentation Dashboard

**Feature**: 003-flask-presentation-dashboard
**Date**: 2026-03-28

---

## GET /

Returns the single-page HTML presentation.

**Handler**: `index()`

**Response**:
- `200 OK` — `text/html` — rendered `index.html` template
- `200 OK` — template context includes graceful fallback messages when source files are missing

**Template variables injected**:

| Variable | Type | Source | Notes |
|---|---|---|---|
| `desert_scores` | `list[dict]` | `desert_scores.csv` (top 10) | Empty list if file missing |
| `interventions` | `list[dict]` | `intervention_recommendations.json` (all 20) | Empty list if file missing |
| `best_intervention` | `dict \| None` | row where `is_highest_impact == true` | None if file missing or no row flagged |
| `charts` | `list[dict]` | Derived from `ChartImage` known instances | `missing: true` flag set per image |
| `map_exists` | `bool` | `reports/outputs/resource_desert_map.html` existence check | |
| `run_status` | `str` | `NotebookRunStatus.status` (lock-protected read) | One of: `idle`, `running`, `complete`, `error` |
| `run_message` | `str` | `NotebookRunStatus.message` | Empty string unless `status == "error"` |

**Error behaviour**: No exceptions propagate to the client. Missing files → empty variables with `missing` flags set in chart list.

---

## GET /figures/\<filename\>

Serves a pre-generated PNG chart from `reports/figures/`.

**Handler**: `serve_figure(filename)`

**Path parameter**:
- `filename` — basename of the PNG file (e.g., `desert_scores_bar_chart.png`)

**Response**:
- `200 OK` — `image/png` — file content via `send_from_directory`
- `404 Not Found` — if the file does not exist in `REPORTS_FIGURES_DIR`

**Security**: Directory is an absolute path constant from `src/config.py`. Flask's `send_from_directory` prevents path traversal.

---

## GET /map

Serves the Folium choropleth HTML map.

**Handler**: `serve_map()`

**Response**:
- `200 OK` — `text/html` — `resource_desert_map.html` served via `send_from_directory`
- `404 Not Found` — if `REPORTS_OUTPUTS_DIR / "resource_desert_map.html"` does not exist

**Security**: Filename is hardcoded — not derived from user input. No path traversal risk.

---

## POST /api/regenerate

Triggers full notebook execution as a background thread.

**Handler**: `api_regenerate()`

**Request body**: None required.

**Response** — JSON:

| Condition | Status | Body |
|---|---|---|
| Run started successfully | `202 Accepted` | `{"status": "running", "message": ""}` |
| Already running | `409 Conflict` | `{"status": "running", "message": "Already running"}` |

**Side effects**:
- Sets `NotebookRunStatus.status = "running"` (inside lock)
- Spawns `threading.Thread(target=_run_notebook_thread, daemon=False)`
- Thread executes: `jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=prob1-resource-desert notebooks/resource_desert_analysis.ipynb`
- On completion: updates `NotebookRunStatus` to `complete` or `error` (inside lock)

**Duplicate run prevention**: If `status == "running"` at request time, returns `409` without spawning a second thread.

---

## GET /api/regenerate/status

Reads and returns the current notebook run state.

**Handler**: `api_regenerate_status()`

**Response** — `200 OK` — JSON:

```json
{
  "status": "idle | running | complete | error",
  "message": "<empty string or last 500 chars of stderr>"
}
```

**Thread safety**: Both `status` and `message` fields are read inside `threading.Lock` before serialisation.

**Polling contract**: Clients MUST use recursive `setTimeout` (not `setInterval`) — wait for response before scheduling next poll. Recommended interval: 2000 ms while `status == "running"`.
