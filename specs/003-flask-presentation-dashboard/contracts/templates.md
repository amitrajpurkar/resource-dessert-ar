# Template Variable Contracts: Flask Presentation Dashboard

**Feature**: 003-flask-presentation-dashboard
**Date**: 2026-03-28

---

## Template: `webapp/templates/index.html`

The single Jinja2 template for the entire presentation. All variables listed below are injected by the `index()` route handler.

---

### `desert_scores` — `list[dict]`

Top-10 most underserved ZIP codes, sorted by `desert_rank` ascending (rank 1 = most deprived).

Each dict has the following keys (matching `DesertScore` display subset):

| Key | Type | Example |
|---|---|---|
| `zip_code` | `str` | `"32209"` |
| `desert_rank` | `int` | `1` |
| `desert_score` | `float` | `87.4` |
| `top_gap_category` | `str` | `"healthcare"` |
| `total_population` | `int` | `28450` |
| `poverty_rate` | `float` | `0.34` |

**Empty list behaviour**: If `desert_scores.csv` is missing, the template renders a "Data not yet generated" placeholder in the Analysis section instead of the table.

---

### `interventions` — `list[dict]`

All 20 simulated interventions, sorted by `score_improvement` descending.

Each dict has the following keys (matching `Intervention` entity):

| Key | Type | Example |
|---|---|---|
| `zip_code` | `str` | `"32209"` |
| `resource_type` | `str` | `"primary_care"` |
| `current_desert_score` | `float` | `87.4` |
| `simulated_desert_score` | `float` | `72.1` |
| `score_improvement` | `float` | `15.3` |
| `pct_improvement` | `float` | `17.5` |
| `population_impacted` | `int` | `28450` |
| `is_highest_impact` | `bool` | `true` (exactly one row) |

**Empty list behaviour**: If `intervention_recommendations.json` is missing, the template renders a "Data not yet generated" placeholder in the Recommendations section instead of the table and call-out card.

---

### `best_intervention` — `dict | None`

The single intervention row where `is_highest_impact == true`. `None` if the file is missing or no row is flagged.

**Usage**: Populates the highlighted call-out card in the Recommendations section. The template MUST guard with `{% if best_intervention %}` before rendering.

Fields are identical to `interventions` row dict above.

---

### `charts` — `list[dict]`

Seven chart descriptors, one per pre-rendered PNG. Order determines render order within each section.

Each dict:

| Key | Type | Notes |
|---|---|---|
| `filename` | `str` | Basename — used as `/figures/<filename>` URL |
| `section` | `str` | `analysis`, `observations`, `recommendations`, or `category` |
| `caption` | `str` | Human-readable label shown beneath the image |
| `missing` | `bool` | `True` if the file does not exist at render time |

**Missing behaviour**: If `missing == true`, the template renders a placeholder `<div>` with the caption and a "Regenerate Data" prompt instead of an `<img>` element.

---

### `map_exists` — `bool`

`True` if `reports/outputs/resource_desert_map.html` is present on disk.

**Usage**: Controls whether the `<iframe src="/map" ...>` is rendered or a "Data not yet generated" placeholder is shown in the Analysis section.

---

### `run_status` — `str`

Current notebook execution state. One of: `idle`, `running`, `complete`, `error`.

**Usage**:
- `running` → disable "Regenerate Data" button, show spinner
- `error` → show error banner with `run_message`
- `complete` → show success indicator (auto-clears after page reload or next action)
- `idle` → default state, button enabled

---

### `run_message` — `str`

Last 500 characters of `stderr` from the notebook process. Empty string unless `run_status == "error"`.

**Usage**: Displayed in an error banner when `run_status == "error"` so the presenter can diagnose the failure.
