# Implementation Plan: Flask Presentation Dashboard

**Branch**: `003-flask-presentation-dashboard` | **Date**: 2026-03-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-flask-presentation-dashboard/spec.md`

## Summary

Build a single-page Flask web application that reads pre-generated analysis outputs (CSV, JSON, PNG, HTML) and renders a scrollable five-section presentation dashboard for datathon judges. The app provides a sticky nav bar, a "Regenerate Data" button that triggers notebook execution in a background thread with polling status, and graceful fallbacks for all missing output files. No in-browser chart rendering — all charts are static PNGs served via `send_from_directory`.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Flask ≥ 3.0, pandas ≥ 2.0, threading (stdlib), subprocess (stdlib), pathlib (stdlib)
**Storage**: Read-only local files — `reports/outputs/` (CSV, JSON, HTML map) and `reports/figures/` (PNG charts). No database.
**Testing**: pytest ≥ 8.0, Flask built-in `test_client()` (no pytest-flask)
**Target Platform**: localhost — datathon demo on a 1280×800 laptop
**Project Type**: web-service (single-page Flask app)
**Performance Goals**: All five sections load within 3 seconds on localhost
**Constraints**: No external CSS/JS frameworks; hand-written CSS with custom properties; no user authentication; Flask dev server acceptable
**Scale/Scope**: Single presenter, single page, ~10 simultaneous viewers maximum

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|---|---|---|
| I. Python Code Quality | PASS | `app.py` uses `pathlib.Path`, logging, type hints, `ruff`/`black`-clean |
| II. Data Science Reproducibility | PASS | App is read-only; pipeline stages unchanged; no global mutable state except `_run_state` (guarded by `Lock`) |
| III. Test-First Development | PASS | `tests/test_app.py` written before `app.py`; unit tests use Flask `test_client()` with mocked file I/O |
| IV. Data Integrity & Observability | PASS | Missing files trigger graceful fallback (no silent failure); `logging` used throughout |
| V. Simplicity & YAGNI | PASS | No framework, no external task queue, no DB; stdlib threading is sufficient for single background task |
| VI. Analytical Rigour | N/A | Dashboard is display-only; all analytical claims come from pipeline outputs |

No constitution violations. No complexity justification required.

## Project Structure

### Documentation (this feature)

```text
specs/003-flask-presentation-dashboard/
├── plan.md              ← This file
├── spec.md              ← Feature specification
├── research.md          ← Phase 0 research decisions
├── data-model.md        ← Entities and file dependency map
├── quickstart.md        ← Developer quickstart
├── contracts/
│   ├── routes.md        ← Flask route contracts (5 routes)
│   └── templates.md     ← Jinja2 template variable contracts
└── tasks.md             ← Phase 2 task breakdown (created by /speckit.tasks)
```

### Source Code

```text
app.py                          ← Flask app factory, routes, background thread runner
webapp/
├── templates/
│   └── index.html              ← Single Jinja2 template, five-section layout
└── static/
    ├── css/
    │   └── style.css           ← Hand-written CSS, custom properties for palette
    └── js/
        └── app.js              ← fetch + setTimeout polling for /api/regenerate/status

tests/
└── test_app.py                 ← Flask route tests (test_client fixture)

src/
└── config.py                   ← REPORTS_FIGURES_DIR, REPORTS_OUTPUTS_DIR (already exists)
```

**Structure Decision**: Single-project layout. The Flask app lives at the repo root alongside the existing `src/` pipeline. `app.py` imports path constants from `src/config.py` directly, consistent with the existing convention. No separate `backend/` or `frontend/` directory is needed for a single-file Flask app.

## Key Design Decisions (from research.md)

1. **Background execution**: `threading.Thread` + `subprocess.run` + `threading.Lock`-protected `_run_state` dict. No Celery/RQ — datathon demo requires no external infrastructure.

2. **File serving**: `flask.send_from_directory(ABSOLUTE_DIR, filename)` for `/figures/<filename>` and `/map`. Prevents path traversal; handles MIME types automatically.

3. **Choropleth embed**: `<iframe src="/map" ...>` — file is ~5 MB, too large to inline. Flask route serves it lazily.

4. **JS polling**: Recursive `setTimeout` + `fetch` (not `setInterval`) — waits for each response before scheduling the next, preventing request queue buildup during slow notebook runs.

5. **CSS**: Hand-written, ~200 lines, CSS custom properties for palette. No Bootstrap/Tailwind dependency.
   - `--color-navy: #0d1b2a` | `--color-accent-red: #d73027` | `--color-accent-green: #1a9850`
   - Highlight card: `--color-highlight: #ffe066`

6. **Testing**: Flask `app.test_client()` fixture in `tests/conftest.py`. No pytest-flask.
