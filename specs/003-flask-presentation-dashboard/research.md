# Research: Flask Presentation Dashboard

**Feature**: 003-flask-presentation-dashboard
**Date**: 2026-03-28

---

## 1. Background Notebook Execution (No Celery)

**Decision**: Use Python `threading.Thread` + `subprocess.run` with a `threading.Lock`-protected module-level status dictionary.

**Rationale**: A datathon demo needs no external infrastructure. `threading.Thread` with `daemon=False` and a shared `dict` guarded by a `Lock` is the simplest correct pattern. The notebook run takes ~30–60s — well within the range where stdlib threading is appropriate without RQ/Celery.

**Implementation pattern**:
```
_run_state = {"status": "idle", "message": ""}   # guarded by _lock
_lock = threading.Lock()

def _run_notebook_thread():
    with _lock: _run_state.update(status="running")
    result = subprocess.run([
        "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
        "--ExecutePreprocessor.kernel_name=prob1-resource-desert",
        "--ExecutePreprocessor.timeout=600",
        "notebooks/resource_desert_analysis.ipynb"
    ], capture_output=True, text=True)
    with _lock:
        if result.returncode == 0:
            _run_state.update(status="complete", message="")
        else:
            _run_state.update(status="error", message=result.stderr[-500:])
```

**Gotchas**:
- Duplicate runs must be blocked by checking `status == "running"` before spawning a thread.
- `stderr` from nbconvert contains progress/warnings on success — only treat non-zero `returncode` as failure.
- The kernel name `prob1-resource-desert` must be registered via `ipykernel install` (already done in this project).

**Alternatives considered**: `subprocess.Popen` with async reading — rejected (unnecessary complexity for a single background task). `concurrent.futures.ThreadPoolExecutor` — viable but adds no benefit over a plain Thread here.

---

## 2. Serving Files Outside Flask's `static/` Folder

**Decision**: Use `flask.send_from_directory(directory, filename)` with explicit route handlers for `reports/figures/` and `reports/outputs/`.

**Rationale**: Flask's built-in static file serving is limited to one folder. `send_from_directory` is the idiomatic way to serve any directory, handles MIME types, and prevents path traversal when the directory is an absolute path.

**Routes**:
```
GET /figures/<filename>  →  send_from_directory(REPORTS_FIGURES_DIR, filename)
GET /map                 →  send_from_directory(REPORTS_OUTPUTS_DIR, "resource_desert_map.html")
```

**Path constants** come from `src/config.py` (`cfg.REPORTS_FIGURES_DIR`, `cfg.REPORTS_OUTPUTS_DIR`), consistent with the existing project convention.

---

## 3. Choropleth Map as Iframe

**Decision**: Serve the Folium HTML via a dedicated `/map` Flask route; embed in the template as `<iframe src="/map" ...>`.

**Rationale**: The file is ~5 MB — too large to inline. A Flask route using `send_from_directory` serves it with correct `text/html` MIME type. The iframe loads it lazily, keeping initial page load fast.

**Security**: The filename is hardcoded in the route (not user-supplied), so path traversal is not a concern.

---

## 4. JS Status Polling (No Framework)

**Decision**: Recursive `setTimeout` + `fetch` pattern. Poll `/api/regenerate/status` every 2 seconds while `status == "running"`.

**Rationale**: `setTimeout` (not `setInterval`) waits for each response before scheduling the next request, preventing request queue build-up if the server is slow. No dependency on React, Vue, or any JS framework.

**Pattern**:
```js
function pollStatus() {
  fetch('/api/regenerate/status')
    .then(r => r.json())
    .then(data => {
      updateUI(data);
      if (data.status === 'running') setTimeout(pollStatus, 2000);
    })
    .catch(() => setTimeout(pollStatus, 2000));
}
```

---

## 5. Flask Route Testing

**Decision**: Use Flask's built-in `app.test_client()` via a `pytest` fixture in `tests/conftest.py`. No `pytest-flask` dependency.

**Rationale**: Flask's test client covers all required assertions (status codes, JSON responses, HTML content). `pytest-flask` adds no critical functionality beyond convenience fixtures, and avoids an extra dependency.

**Fixture pattern**:
```python
@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
```

---

## 6. CSS Design Approach

**Decision**: Hand-written CSS in `webapp/static/css/style.css`. No external CSS framework (Bootstrap/Tailwind).

**Rationale**: The app has one page and five sections. A ~200-line custom stylesheet with CSS custom properties (variables) for the color palette is simpler, faster to load, and easier to tune for presentation aesthetics than loading a full framework. Using `--color-navy`, `--color-accent-red`, `--color-accent-green` variables ensures palette consistency.

**Color palette**:
- Base: `#0d1b2a` (dark navy), `#ffffff` (white), `#f4f6f9` (off-white background)
- Accent: `#d73027` (red — high deprivation), `#fee090` (yellow), `#1a9850` (green — low deprivation)
- Highlight: `#ffe066` (intervention call-out card background)
