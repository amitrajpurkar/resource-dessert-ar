# Skill: Data Visualization

## Purpose
Produce clear, publication-quality visualisations for exploratory data analysis (EDA), model evaluation, and final presentation. Every chart must be self-explanatory, accessible, and saved to disk.

## When to Use
- During EDA to understand distributions, relationships, and patterns
- After modelling to communicate results (feature importance, confusion matrix, ROC, etc.)
- When preparing charts for the datathon presentation deck

---

## Global Style Setup

Always apply this at the top of any visualisation script or notebook:

```python
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

# --- Project-wide style ---
FIGURES_DIR = Path("reports/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
plt.rcParams.update({
    "figure.dpi":        150,
    "figure.facecolor":  "white",
    "axes.facecolor":    "white",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "font.family":       "sans-serif",
    "axes.titlesize":    13,
    "axes.labelsize":    11,
    "xtick.labelsize":   10,
    "ytick.labelsize":   10,
    "legend.fontsize":   10,
})

def save_fig(fig: plt.Figure, filename: str, tight: bool = True) -> None:
    """Save figure to reports/figures/ at 150 DPI."""
    if tight:
        fig.tight_layout()
    path = FIGURES_DIR / filename
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Saved: {path}")
```

---

## Chart Recipes

### 1. Distribution — Single Numeric Column
```python
def plot_distribution(series: pd.Series, title: str, filename: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Histogram
    axes[0].hist(series.dropna(), bins=30, edgecolor="black", color="#4878d0")
    axes[0].set_title(f"{title} — Distribution")
    axes[0].set_xlabel(series.name)
    axes[0].set_ylabel("Count")

    # Box plot
    axes[1].boxplot(series.dropna(), vert=True, patch_artist=True,
                    boxprops=dict(facecolor="#4878d0", alpha=0.6))
    axes[1].set_title(f"{title} — Box Plot")
    axes[1].set_ylabel(series.name)

    save_fig(fig, filename)
```

### 2. Bar Chart — Category Counts / Means
```python
def plot_bar(
    df: pd.DataFrame, x_col: str, y_col: str,
    title: str, filename: str,
    orient: str = "v"  # "v" or "h"
) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    summary = df.groupby(x_col)[y_col].mean().sort_values(ascending=(orient == "h"))

    if orient == "h":
        ax.barh(summary.index.astype(str), summary.values, color="#4878d0", edgecolor="black")
        ax.set_xlabel(f"Mean {y_col}")
        ax.set_ylabel(x_col)
    else:
        ax.bar(summary.index.astype(str), summary.values, color="#4878d0", edgecolor="black")
        ax.set_ylabel(f"Mean {y_col}")
        ax.set_xlabel(x_col)
        plt.xticks(rotation=45, ha="right")

    ax.set_title(title)
    save_fig(fig, filename)
```

### 3. Correlation Heatmap
```python
def plot_correlation_heatmap(df: pd.DataFrame, title: str, filename: str) -> None:
    corr = df.select_dtypes(include=[np.number]).corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))  # upper triangle

    fig, ax = plt.subplots(figsize=(max(8, len(corr)), max(6, len(corr) - 1)))
    sns.heatmap(
        corr, mask=mask, annot=True, fmt=".2f",
        cmap="RdBu_r", center=0, vmin=-1, vmax=1,
        linewidths=0.5, ax=ax, square=True,
        cbar_kws={"shrink": 0.8}
    )
    ax.set_title(title)
    save_fig(fig, filename)
```

### 4. Scatter Plot with Optional Colour Encoding
```python
def plot_scatter(
    df: pd.DataFrame, x_col: str, y_col: str,
    hue_col: str | None, title: str, filename: str
) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    scatter_kws = dict(alpha=0.65, edgecolors="none", s=40)

    if hue_col:
        for label, group in df.groupby(hue_col):
            ax.scatter(group[x_col], group[y_col], label=str(label), **scatter_kws)
        ax.legend(title=hue_col, bbox_to_anchor=(1.01, 1), loc="upper left")
    else:
        ax.scatter(df[x_col], df[y_col], color="#4878d0", **scatter_kws)

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_title(title)
    save_fig(fig, filename)
```

### 5. Time Series / Line Chart
```python
def plot_time_series(
    df: pd.DataFrame, date_col: str, value_col: str,
    group_col: str | None, title: str, filename: str
) -> None:
    fig, ax = plt.subplots(figsize=(12, 5))

    if group_col:
        for label, group in df.groupby(group_col):
            ax.plot(group[date_col], group[value_col], label=str(label), linewidth=1.8)
        ax.legend(title=group_col)
    else:
        ax.plot(df[date_col], df[value_col], color="#4878d0", linewidth=1.8)

    ax.set_xlabel("Date")
    ax.set_ylabel(value_col)
    ax.set_title(title)
    fig.autofmt_xdate()
    save_fig(fig, filename)
```

### 6. Confusion Matrix (Classification)
```python
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix

def plot_confusion_matrix(
    y_true, y_pred, class_labels: list,
    title: str, filename: str
) -> None:
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_labels)
    disp.plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set_title(title)
    save_fig(fig, filename)
```

### 7. ROC Curve
```python
from sklearn.metrics import roc_curve, auc

def plot_roc_curve(y_true, y_prob, title: str, filename: str) -> None:
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(fpr, tpr, color="#4878d0", lw=2, label=f"AUC = {roc_auc:.3f}")
    ax.plot([0, 1], [0, 1], color="gray", lw=1.2, linestyle="--", label="Random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(title)
    ax.legend(loc="lower right")
    save_fig(fig, filename)
```

### 8. Feature Importance Bar Chart
```python
def plot_feature_importance(
    feature_names: list, importances: np.ndarray,
    title: str, filename: str, top_n: int = 20
) -> None:
    pairs = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)[:top_n]
    names, vals = zip(*pairs)

    fig, ax = plt.subplots(figsize=(9, max(5, top_n * 0.35)))
    ax.barh(list(reversed(names)), list(reversed(vals)), color="#4878d0", edgecolor="black")
    ax.set_xlabel("Importance")
    ax.set_title(title)
    save_fig(fig, filename)
```

---

## Checklist — Before Saving Any Chart
- [ ] Title is descriptive (not generic like "Plot 1")
- [ ] Both axes are labelled, including units where applicable
- [ ] Legend present if multiple series / groups
- [ ] Readable at A4 print size (font size ≥ 10pt)
- [ ] Saved via `save_fig()` to `reports/figures/`
- [ ] Filename is descriptive: `case1_revenue_distribution.png`, not `plot.png`

---

## Conventions
- Never use `plt.show()` in scripts — only in notebooks. Use `save_fig()` always.
- Do not use default matplotlib colours (`C0`, `C1`) — use named colours or a seaborn palette.
- Keep all visualisation helper functions in `src/visualisation.py`.
- For the presentation deck, export at 300 DPI: `fig.savefig(..., dpi=300)`.
