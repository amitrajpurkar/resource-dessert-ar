"""Stage 5 — Visualization.

All plot functions.  Every figure is saved to ``reports/figures/`` at ≥150 DPI
with a title, labelled axes (with units), and a legend where multi-series.
The Folium choropleth is exported as a standalone HTML file.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src import config as cfg

logger = cfg.get_logger(__name__)

# Consistent palette for all plots in this feature
_PALETTE = "RdYlGn_r"
_DPI = 150


def plot_desert_scores_bar_chart(
    desert_scores_df: pd.DataFrame,
    figures_dir: Path = cfg.REPORTS_FIGURES_DIR,
    top_n: int = 10,
) -> None:
    """Save a horizontal bar chart of the top-N ZIPs by Desert Score.

    Args:
        desert_scores_df: Desert Score DataFrame from
            :func:`src.features.compute_desert_score`.
        figures_dir: Directory to save the PNG.  Created if absent.
        top_n: Number of most underserved ZIPs to display.  Defaults to 10.
    """
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    top = desert_scores_df.nsmallest(top_n, cfg.COL_DESERT_RANK).sort_values(
        cfg.COL_DESERT_RANK, ascending=False
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(
        top[cfg.COL_ZIP].astype(str),
        top[cfg.COL_DESERT_SCORE],
        color=plt.cm.RdYlGn_r(  # type: ignore[attr-defined]
            top[cfg.COL_DESERT_SCORE] / 100.0
        ),
    )

    ax.set_xlabel("Resource Desert Score (0–100)", fontsize=12)
    ax.set_ylabel("ZIP Code", fontsize=12)
    ax.set_title(
        f"Top {top_n} Most Underserved Jacksonville ZIP Codes\n"
        "(Higher score = greater resource deprivation)",
        fontsize=13,
        fontweight="bold",
    )
    ax.set_xlim(0, 105)

    # Annotate bars with score value
    for bar, score in zip(bars, top[cfg.COL_DESERT_SCORE]):
        ax.text(
            bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{score:.1f}",
            va="center",
            fontsize=9,
        )

    plt.tight_layout()
    out_path = figures_dir / cfg.FIGURE_BAR_CHART.name
    fig.savefig(out_path, dpi=_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved bar chart → %s", out_path)


def create_choropleth_map(
    desert_scores_df: pd.DataFrame,
    geojson_path: Path = cfg.GEOJSON_PATH,
    outputs_dir: Path = cfg.REPORTS_OUTPUTS_DIR,
) -> None:
    """Save a standalone Folium choropleth HTML map of Desert Scores.

    Uses ``ZCTA5CE20`` as the GeoJSON feature key property.  Colour palette:
    ``RdYlGn_r`` (red = high deprivation).  Includes a tooltip showing ZIP
    code, Desert Score, and top gap category.

    Args:
        desert_scores_df: Desert Score DataFrame.
        geojson_path: Path to the Jacksonville ZCTA GeoJSON file.
        outputs_dir: Directory to save the HTML file.  Created if absent.

    Raises:
        FileNotFoundError: If *geojson_path* does not exist.
    """
    import folium
    from folium import GeoJson, GeoJsonTooltip

    geojson_path = Path(geojson_path)
    if not geojson_path.exists():
        raise FileNotFoundError(
            f"GeoJSON file not found: {geojson_path}. "
            "Download Jacksonville ZCTA GeoJSON from Census TIGER/Line and "
            "place it at data/raw/jacksonville_zctas.geojson before running this step."
        )

    outputs_dir = Path(outputs_dir)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    m = folium.Map(
        location=[30.3322, -81.6557], zoom_start=11, tiles="CartoDB positron"
    )

    choropleth = folium.Choropleth(
        geo_data=str(geojson_path),
        data=desert_scores_df,
        columns=[cfg.COL_ZIP, cfg.COL_DESERT_SCORE],
        key_on="feature.properties.ZCTA5CE20",
        fill_color=_PALETTE,
        fill_opacity=0.75,
        line_opacity=0.3,
        legend_name="Resource Desert Score (0–100) — Higher = More Deprived",
        highlight=True,
        nan_fill_color="lightgrey",
    )
    choropleth.add_to(m)

    def _style(feature: dict) -> dict:
        return {"fillOpacity": 0, "weight": 0}

    def _highlight(feature: dict) -> dict:
        return {"weight": 2, "color": "#333", "fillOpacity": 0.1}

    tooltip_layer = GeoJson(
        str(geojson_path),
        style_function=_style,
        highlight_function=_highlight,
        tooltip=GeoJsonTooltip(
            fields=["ZCTA5CE20"],
            aliases=["ZIP Code"],
            localize=True,
        ),
    )
    tooltip_layer.add_to(m)

    out_path = outputs_dir / cfg.CHOROPLETH_MAP_PATH.name
    m.save(str(out_path))
    logger.info("Saved choropleth map → %s", out_path)


def plot_preventative_vs_outcome(
    merged_df: pd.DataFrame,
    asset_col: str,
    outcome_col: str,
    figures_dir: Path = cfg.REPORTS_FIGURES_DIR,
) -> None:
    """Save a scatter plot with regression line linking an asset to an outcome.

    Annotates the top-3 and bottom-3 ZIP codes by outcome value.

    Args:
        merged_df: Wide merged DataFrame.
        asset_col: Column name of the preventative asset metric.
        outcome_col: Column name of the health outcome metric.
        figures_dir: Directory to save the PNG.  Created if absent.
    """
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    plot_df = merged_df[[cfg.COL_ZIP, asset_col, outcome_col]].dropna()

    fig, ax = plt.subplots(figsize=(10, 7))
    sns.regplot(
        data=plot_df,
        x=asset_col,
        y=outcome_col,
        ax=ax,
        scatter_kws={"alpha": 0.7, "s": 60},
        line_kws={"color": "red", "linewidth": 1.5},
    )

    # Annotate extremes
    top3 = plot_df.nlargest(3, outcome_col)
    bot3 = plot_df.nsmallest(3, outcome_col)
    for _, row in pd.concat([top3, bot3]).iterrows():
        ax.annotate(
            str(row[cfg.COL_ZIP]),
            xy=(row[asset_col], row[outcome_col]),
            xytext=(5, 3),
            textcoords="offset points",
            fontsize=8,
            color="#333",
        )

    ax.set_xlabel(asset_col, fontsize=11)
    ax.set_ylabel(f"{outcome_col} (%)", fontsize=11)
    ax.set_title(
        f"Preventative Asset vs Health Outcome\n{asset_col} → {outcome_col}",
        fontsize=12,
        fontweight="bold",
    )

    plt.tight_layout()
    out_path = figures_dir / cfg.FIGURE_HEALTH_SCATTER.name
    fig.savefig(out_path, dpi=_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved health scatter → %s", out_path)


def plot_intervention_impact_heatmap(
    interventions_df: pd.DataFrame,
    figures_dir: Path = cfg.REPORTS_FIGURES_DIR,
) -> None:
    """Save a heatmap of pct_improvement per (ZIP × resource_type).

    Annotates the highest-impact cell with a star marker.

    Args:
        interventions_df: Output of :func:`src.models.rank_interventions`.
        figures_dir: Directory to save the PNG.  Created if absent.
    """
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    pivot = interventions_df.pivot(
        index="zip_code", columns="resource_type", values="pct_improvement"
    )

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(
        pivot,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "Projected Desert Score Improvement (%)"},
    )

    # Star the highest-impact cell
    best = interventions_df.loc[
        interventions_df["is_highest_impact"].astype(bool).idxmax()
    ]
    row_idx = list(pivot.index).index(best["zip_code"])
    col_idx = list(pivot.columns).index(best["resource_type"])
    ax.text(
        col_idx + 0.5,
        row_idx + 0.5,
        "★",
        ha="center",
        va="center",
        fontsize=14,
        color="blue",
        fontweight="bold",
    )

    ax.set_title(
        "Gap-Closure Simulation: Projected Desert Score Improvement by Intervention\n"
        "(★ = Highest-Impact Action)",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Resource Type", fontsize=11)
    ax.set_ylabel("ZIP Code", fontsize=11)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    out_path = figures_dir / cfg.FIGURE_INTERVENTION_HEATMAP.name
    fig.savefig(out_path, dpi=_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved intervention heatmap → %s", out_path)


def plot_category_view(
    category_df: pd.DataFrame,
    category: str,
    figures_dir: Path = cfg.REPORTS_FIGURES_DIR,
) -> None:
    """Save a bar chart for a single service category view.

    Shows supply gap and poverty rate side-by-side for all ZIPs in the
    category DataFrame.

    Args:
        category_df: Filtered DataFrame from
            :func:`src.features.filter_by_service_category`.
        category: Category name used in the filename and title.
        figures_dir: Directory to save the PNG.  Created if absent.
    """
    from src import config as cfg  # local import to avoid circular

    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    gap_col_map = {
        "healthcare": cfg.COL_SUPPLY_GAP_HEALTHCARE,
        "food_access": cfg.COL_SUPPLY_GAP_FOOD,
        "parks": cfg.COL_SUPPLY_GAP_PARKS,
        "insurance": cfg.COL_SUPPLY_GAP_INSURANCE,
    }
    gap_col = gap_col_map.get(category, cfg.COL_DESERT_SCORE)

    plot_cols = [
        c
        for c in [cfg.COL_ZIP, gap_col, cfg.COL_POVERTY_RATE]
        if c in category_df.columns
    ]
    plot_df = category_df[plot_cols].dropna()

    x = range(len(plot_df))
    width = 0.4

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(
        [i - width / 2 for i in x],
        plot_df[gap_col],
        width=width,
        label=f"{category} gap (0–1)",
        color="#d73027",
    )
    if cfg.COL_POVERTY_RATE in plot_df.columns:
        ax.bar(
            [i + width / 2 for i in x],
            plot_df[cfg.COL_POVERTY_RATE],
            width=width,
            label="Poverty Rate (0–1)",
            color="#fee090",
        )

    ax.set_xticks(list(x))
    ax.set_xticklabels(
        plot_df[cfg.COL_ZIP].astype(str), rotation=45, ha="right", fontsize=8
    )
    ax.set_xlabel("ZIP Code", fontsize=11)
    ax.set_ylabel("Score (0–1)", fontsize=11)
    ax.set_title(
        f"Service Category View: {category.replace('_', ' ').title()}\n"
        "Supply Gap vs Poverty Rate by ZIP Code",
        fontsize=12,
        fontweight="bold",
    )
    ax.legend(fontsize=10)
    plt.tight_layout()

    out_path = figures_dir / f"category_{category}_view.png"
    fig.savefig(out_path, dpi=_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved category view → %s", out_path)
