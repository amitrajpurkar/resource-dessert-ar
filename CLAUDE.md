# CLAUDE.md — UNF Datathon 2025

> This file defines the guiding principles, conventions, and expectations for Claude Code
> when working on any Python data-science task within this project.

---

## Project Context

This repository contains three data-science problem cases for the **2025 UNF CodeforAwhile Datathon**:

| # | Problem Case | Data |
|---|---|---|
| 1 | Analyzing Nonprofit Financial Stability | `Duval_StJohns.csv` |
| 2 | Predicting Voter Turnout with Classification | `VoterRegistrationComp/`, `VotingHistoryComp/` |
| 3 | Patterns in Police-Involved Shootings | `Police_involved.xlsx` |

All work must be **reproducible, well-documented, and defensible** — outputs will be presented to judges.

---

## Project Structure

```
unf_datathon_2025/
├── CLAUDE.md                  ← You are here
├── .claude/
│   └── skills/                ← Domain-specific skill prompts
├── data/
│   ├── raw/                   ← Original, unmodified source files (read-only)
│   ├── processed/             ← Cleaned/transformed datasets
│   └── outputs/               ← Model outputs, predictions, exports
├── notebooks/                 ← Exploratory Jupyter notebooks (.ipynb)
├── src/                       ← Importable Python modules & pipelines
├── tests/                     ← Unit and integration tests
└── reports/
    ├── figures/               ← All saved plots and charts
    └── outputs/               ← Final written reports
```

**Rules:**
- Never overwrite files in `data/raw/`. Always write processed outputs to `data/processed/`.
- Notebooks in `notebooks/` are for exploration only. Production code lives in `src/`.
- All figures saved to disk go in `reports/figures/` with descriptive filenames.

---

## Design Principles

### 1. Reproducibility First
- Set random seeds explicitly wherever randomness is involved: `np.random.seed(42)`, `random.seed(42)`.
- Pin library versions in `requirements.txt` or `pyproject.toml`.
- All data transformations must be scripted — never manually edit raw data files.
- Pipelines must be runnable end-to-end from a clean environment with a single command.

### 2. Code Quality
- Follow **PEP 8** for all Python code. Use `black` for formatting, `ruff` or `flake8` for linting.
- All public functions and classes must have **Google-style docstrings** with `Args`, `Returns`, and `Raises` sections.
- Use **type hints** on all function signatures (`def clean_df(df: pd.DataFrame) -> pd.DataFrame:`).
- Keep functions small and single-purpose. If a function exceeds ~40 lines, decompose it.
- Avoid notebook-style imperative scripting in `src/` — write functions and classes.

### 3. Data Integrity
- Always validate input data at the start of every pipeline stage (shape, dtypes, null counts).
- Never silently drop rows. Log or raise when data is discarded, with counts and reasons.
- Document every transformation with a comment explaining *why*, not just *what*.
- After cleaning, run a post-clean assertion suite to confirm invariants hold.

### 4. Modularity & Separation of Concerns
- Separate data ingestion, cleaning, feature engineering, modelling, and reporting into distinct modules.
- No hardcoded file paths. Use `pathlib.Path` and define paths in a central `config.py` or via environment variables.
- Avoid global state. Pass DataFrames and configurations explicitly as function arguments.

### 5. Observability
- Use Python's built-in `logging` module (not `print`) for runtime messages.
- Log pipeline entry/exit, record counts before and after each transformation, and any anomalies found.
- All models must output a summary of evaluation metrics — do not just print them; write them to `reports/outputs/`.

### 6. Testing
- Every function in `src/` must have a corresponding unit test in `tests/`.
- Use `pytest` as the test runner. Tests must pass before any code is considered done.
- Use small, synthetic fixture DataFrames in tests — never load real raw data in unit tests.
- Integration/end-to-end tests may use real data but must be tagged `@pytest.mark.e2e` and isolated.

### 7. Visualisation Standards
- Use **matplotlib** or **seaborn** as the primary plotting libraries.
- Every plot must have: a descriptive title, labelled axes (with units), and a legend if multiple series.
- Save all figures programmatically with `fig.savefig(...)` at 150 DPI minimum. Never rely on interactive display alone.
- Use a consistent colour palette across all plots in a single problem case.

### 8. Model Development
- Always establish a **baseline model** before attempting complex approaches.
- Report metrics appropriate to the task type: classification → precision/recall/F1/AUC; regression → MAE/RMSE/R².
- Use cross-validation, not a single train/test split, unless the dataset is too small.
- Document model assumptions, hyperparameter choices, and limitations explicitly.

---

## Available Skills

Use these skills (via `.claude/skills/`) to get structured, expert assistance on specific tasks:

| Skill | When to Use |
|---|---|
| `data-evaluation-skill` | First look at a new dataset — profiling, quality assessment |
| `data-cleaning-skill` | Fixing nulls, types, duplicates, outliers, standardisation |
| `data-visualization-skill` | Generating EDA charts or final presentation plots |
| `code-review-skill` | Reviewing Python code for quality, correctness, and conventions |
| `unit-testing-skill` | Writing pytest unit tests for `src/` functions |
| `end-to-end-testing-skill` | Building pipeline integration tests that run the full workflow |

---

## Python Environment

```bash
# Recommended setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run linting
ruff check src/ tests/
black --check src/ tests/
```

### Core Dependencies
```
pandas>=2.0
numpy>=1.26
scikit-learn>=1.4
matplotlib>=3.8
seaborn>=0.13
jupyter>=1.0
pytest>=8.0
ruff>=0.4
black>=24.0
```

---

## Git Conventions
- Branch per problem case: `case1/nonprofit-analysis`, `case2/voter-prediction`, `case3/shootings-patterns`
- Commit messages: `[case1] add null-handling for revenue columns`
- Do not commit notebooks with large cell outputs — clear outputs before committing.
- Do not commit raw data files if they are large (>10 MB) — add to `.gitignore` and document where to obtain them.

---

*Last updated: March 27, 2026*
