<!--
SYNC IMPACT REPORT
==================
Version change: (none) → 1.0.0 (initial ratification)
Modified principles: N/A (initial)
Added sections:
  - Core Principles (6 principles)
  - Technology Stack
  - Quality Gates
  - Governance
Removed sections: N/A
Templates reviewed:
  - .specify/templates/plan-template.md     ✅ aligned (Constitution Check section present)
  - .specify/templates/spec-template.md     ✅ aligned (requirements/acceptance criteria structure compatible)
  - .specify/templates/tasks-template.md    ✅ aligned (test-first tasks, phase structure compatible)
Follow-up TODOs:
  - None; all fields resolved from repo context and user input.
-->

# Resource Desert — Project Constitution

## Core Principles

### I. Python Code Quality (NON-NEGOTIABLE)

All production code in `src/` MUST adhere to the following rules without exception:

- **Type hints** MUST be present on every public function signature.
- **Docstrings** MUST follow Google style with `Args`, `Returns`, and `Raises` sections on all
  public functions and classes.
- **Paths** MUST use `pathlib.Path`; string literals for file paths are forbidden.
  All project-level paths MUST be defined in `src/config.py`.
- **Imports** and **formatting** MUST pass `ruff check` and `black --check` with no errors.
- **`print()`** is forbidden in `src/`; use the `logging` module exclusively.

**Rationale**: Consistent style and tooling enforcement reduces cognitive overhead, catches
bugs at lint-time, and ensures the codebase remains maintainable across contributors.

### II. Data Science Reproducibility (NON-NEGOTIABLE)

All analytical and modelling code MUST guarantee reproducibility:

- **Random seeds**: `np.random.seed(42)` and `random.seed(42)` MUST be set wherever
  any randomness appears (train/test splits, sampling, model initialisation).
- **Pipeline separation**: code MUST follow the five-stage architecture —
  `ingestion → cleaning → features → models → visualization` — with no stage mixing logic
  from another stage.
- **No global state**: DataFrames and configuration MUST be passed explicitly as arguments;
  module-level mutable state is forbidden.
- **Raw data is immutable**: files under `data/raw/` MUST NEVER be written to or modified.
  All transformations produce artefacts under `data/processed/` or `data/outputs/`.

**Rationale**: Reproducibility is a first-class scientific requirement. Any result that
cannot be re-derived identically from source data is analytically untrustworthy.

### III. Test-First Development (NON-NEGOTIABLE)

TDD MUST be followed for all `src/` code:

- Tests MUST be written **before** implementation; the Red-Green-Refactor cycle is mandatory.
- Unit tests MUST use **synthetic fixture DataFrames** — no reads from `data/raw/` or
  `data/processed/` in unit tests.
- End-to-end (E2E) tests that touch real data MUST be tagged `@pytest.mark.e2e` and
  are excluded from the default `pytest` run (`pytest -m "not e2e"`).
- **Minimum test coverage: 70%** across `src/` (measured by `pytest --cov=src`).
  Coverage MUST be verified before any PR is merged.
- Coverage below 70% is a **hard block** — implementation is considered incomplete.

**Rationale**: The 70% floor ensures critical pipeline logic (ingestion, cleaning, feature
engineering) is validated against known inputs. Synthetic fixtures keep unit tests fast
and deterministic.

### IV. Data Integrity & Observability

Every transformation that changes data shape MUST be observable:

- **Row-drop logging**: before any `dropna`, filter, or deduplication, code MUST log the
  count of rows being dropped and the reason (e.g.,
  `logger.info("Dropping %d rows with null ZIP code", n)`).
- **Record counts**: log record count before AND after every transformation step.
- **Boundary validation**: validate schema, dtypes, and null rates at the entry point of
  each pipeline stage (`ingestion` validates raw files; `cleaning` asserts post-clean
  invariants). No silent failures.
- **Figures**: every plot MUST have a title, labelled axes (with units), and a legend where
  multi-series. Figures MUST be saved via `fig.savefig(path, dpi=150)` to `reports/figures/`
  with descriptive filenames.
- **Model metrics**: all model evaluation metrics MUST be written to `reports/outputs/`
  as structured files (JSON or CSV).

**Rationale**: Data pipelines fail silently. Mandatory logging and count tracking make
regressions immediately visible during development and review.

### V. Simplicity & YAGNI

Code MUST solve the current problem — no more, no less:

- Do NOT add abstractions, helpers, or utilities for one-time operations.
- Do NOT design for hypothetical future requirements; implement exactly what the current
  task demands.
- Three similar lines of code is preferable to a premature abstraction.
- Error handling and validation MUST only be added at actual system boundaries
  (raw file reads, user-facing outputs). Do NOT add fallbacks for scenarios that
  cannot occur given the internal pipeline guarantees.
- Feature flags, backwards-compatibility shims, and unused code MUST NOT be committed.

**Rationale**: Datathon timelines reward focused, working solutions. Speculative complexity
slows delivery and obscures analytical intent.

### VI. Analytical Rigour

Every quantitative claim in reports or dashboards MUST be traceable:

- Claims about "resource deserts" MUST be grounded in operationalised metrics
  (composite scores, statistical thresholds) defined in `src/features/`.
- The causal chain **Preventative Assets → Poor Outcomes** MUST be supported by
  correlation or regression evidence, not assertion.
- Cross-validation MUST be used for any predictive model; single train/test splits
  without CV are forbidden for reported metrics.
- Spatial analysis outputs (choropleth maps, ZIP-level scores) MUST specify the
  geographic identifier (ZIP code or census tract) used for aggregation.

**Rationale**: The deliverable is a data-driven prototype presented to judges. Unsubstantiated
claims or non-reproducible results undermine the team's credibility.

## Technology Stack

| Layer | Technology | Version Constraint |
|---|---|---|
| Language | Python | ≥ 3.11 |
| Data manipulation | pandas | ≥ 2.0 |
| Numerical | numpy | ≥ 1.26 |
| Visualisation | matplotlib, seaborn | ≥ 3.8, ≥ 0.13 |
| Notebooks | jupyter | ≥ 1.0 |
| Spreadsheet reads | openpyxl | any compatible |
| Testing | pytest, pytest-cov | latest stable |
| Linting/formatting | ruff, black | latest stable |

No new top-level dependencies may be added without updating `requirements.txt` and
noting the rationale in the relevant PR.

## Quality Gates

The following checks MUST pass before any feature branch is considered complete:

1. `ruff check src/ tests/` — zero errors.
2. `black --check src/ tests/` — zero formatting violations.
3. `pytest tests/ -v -m "not e2e"` — all unit tests pass.
4. `pytest tests/ --cov=src --cov-fail-under=70` — coverage ≥ 70%.
5. Notebook outputs MUST be cleared (`nbconvert --clear-output`) before committing.
6. No files under `data/raw/` appear in the git diff.

## Governance

This constitution supersedes all other practices and informal conventions. Amendments
require the following:

1. **Propose** the change with a rationale referencing a concrete problem it solves.
2. **Document** the change in this file with a version bump following semantic versioning:
   - MAJOR: removal or redefinition of an existing principle.
   - MINOR: addition of a new principle or materially expanded guidance.
   - PATCH: clarifications, wording, or typo fixes.
3. **Propagate** to all dependent templates (plan, spec, tasks) as part of the same commit.
4. All PRs and code reviews MUST verify compliance with this constitution before merging.

Use `CLAUDE.md` for runtime development guidance (commands, path conventions, branch
naming). This constitution governs *what* is built and *how* it is validated.

**Version**: 1.0.0 | **Ratified**: 2026-03-28 | **Last Amended**: 2026-03-28
