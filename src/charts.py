"""Chart builders for the dashboard.

matplotlib + seaborn for everything except the geo map; Plotly Express for
the canton choropleth (matches the notebook). Each function returns a figure
object the Streamlit pages render — no Streamlit calls happen in here.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .constants import (
    CITY_COLORS,
    CITY_TO_CANTONS,
    DIMENSIONS,
    WEIGHTS,
)

sns.set_theme(style="whitegrid")

# Stable per-dimension colors for the stacked ranking (notebook cell 17).
_DIM_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]


def _city_color(city: str) -> str:
    return CITY_COLORS.get(city, "#888888")


def ranking_bar(scores_df: pd.DataFrame, weights: dict[str, float] = WEIGHTS):
    """Stacked horizontal ranking: each bar = sum of weighted dimension
    contributions, labelled with the total score on a 0–100 scale."""
    plot_data = scores_df[DIMENSIONS].multiply(pd.Series(weights), axis=1)
    plot_data = plot_data.loc[
        plot_data.sum(axis=1).sort_values(ascending=True).index
    ]

    fig, ax = plt.subplots(figsize=(10, 5))
    left = np.zeros(len(plot_data))
    for dim, color in zip(DIMENSIONS, _DIM_COLORS):
        vals = plot_data[dim].to_numpy()
        ax.barh(plot_data.index, vals, left=left, label=dim, color=color, alpha=0.85, height=0.6)
        left += vals

    for i, city in enumerate(plot_data.index):
        ax.text(left[i] + 0.003, i, f"{left[i] * 100:.1f}", va="center", ha="left", fontweight="bold", fontsize=10)

    ax.set_xlabel("Attraktivitätsindex (gewichtet)")
    ax.set_title("Gesamtranking — Attraktivität für junge Fachkräfte", fontweight="bold", pad=12)
    ax.legend(frameon=False, loc="lower right", fontsize=9)
    fig.tight_layout()
    return fig


def radar(scores_df: pd.DataFrame, city: str):
    """Radar chart of one city's five dimension scores in [0, 1]."""
    values = scores_df.loc[city, DIMENSIONS].tolist() if city in scores_df.index else [0] * len(DIMENSIONS)
    angles = [n / len(DIMENSIONS) * 2 * np.pi for n in range(len(DIMENSIONS))]
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={"polar": True})
    color = _city_color(city)
    ax.plot(angles, values, color=color, linewidth=2)
    ax.fill(angles, values, color=color, alpha=0.2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(DIMENSIONS, fontsize=9)
    ax.set_ylim(0, 1)
    total = scores_df.loc[city, "Gesamt"] * 100 if city in scores_df.index else 0
    ax.set_title(f"{city}\n({total:.1f} Pkt.)", color=color, fontweight="bold", pad=18)
    fig.tight_layout()
    return fig


def heatmap(scores_df: pd.DataFrame):
    """Heatmap of city x dimension scores."""
    fig, ax = plt.subplots(figsize=(7, 0.55 * len(scores_df) + 1.5))
    sns.heatmap(
        scores_df[DIMENSIONS],
        annot=True, fmt=".2f", cmap="crest", vmin=0, vmax=1,
        cbar_kws={"label": "Score [0–1]"}, ax=ax,
    )
    ax.set_title("Dimensionen je Stadt")
    fig.tight_layout()
    return fig


def timeseries(long_df: pd.DataFrame, title: str = ""):
    """Line chart of a variable over time, one line per city.

    ``long_df`` has columns ``Stadt | Jahr | Wert`` (from ``get_var``).
    """
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for city, grp in long_df.groupby("Stadt"):
        grp = grp.sort_values("Jahr")
        ax.plot(grp["Jahr"], grp["Wert"], marker="o", markersize=3, label=city, color=_city_color(city))
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Wert")
    if title:
        ax.set_title(title)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    return fig


def forecast_fan(hist_long: pd.DataFrame, fc_df: pd.DataFrame, title: str = ""):
    """Historical line + Basis/Optimistisch/Pessimistisch forecast fan for a
    single city & variable.

    ``hist_long`` : ``Jahr | Wert`` historical points.
    ``fc_df``     : ``Jahr | Szenario | Wert`` forecast rows for that pair.
    """
    fig, ax = plt.subplots(figsize=(8, 4.5))
    hist_long = hist_long.sort_values("Jahr")
    ax.plot(hist_long["Jahr"], hist_long["Wert"], marker="o", color="#1a1d24", label="Historisch")

    pivot = fc_df.pivot(index="Jahr", columns="Szenario", values="Wert")
    if {"Pessimistisch", "Optimistisch"}.issubset(pivot.columns):
        ax.fill_between(pivot.index, pivot["Pessimistisch"], pivot["Optimistisch"], color="#1f6feb", alpha=0.15, label="Szenario-Bandbreite")
    for scenario, ls in {"Basis": "-", "Optimistisch": "--", "Pessimistisch": ":"}.items():
        if scenario in pivot.columns:
            ax.plot(pivot.index, pivot[scenario], ls, color="#1f6feb", label=scenario)

    ax.set_xlabel("Jahr")
    ax.set_ylabel("Wert")
    if title:
        ax.set_title(title)
    ax.legend(fontsize=8)
    fig.tight_layout()
    return fig


def choropleth(scores_df: pd.DataFrame, geodf, column: str = "Gesamt"):
    """Canton-level choropleth of a score column (Plotly, notebook cell 23).

    ``geodf`` is the dissolved GeoDataFrame (``KantonKürzel | geometry``) from
    ``data_loader._load_geodf``. Cities are expanded to their cantons via
    ``CITY_TO_CANTONS`` (Basel -> BS + BL).
    """
    import plotly.express as px

    rows = []
    for city, cantons in CITY_TO_CANTONS.items():
        if city not in scores_df.index:
            continue
        score = scores_df.loc[city, column] * 100
        for kuerzel in cantons:
            rows.append({"KantonKürzel": kuerzel, "Stadt": city, "Score": score})
    index_df = pd.DataFrame(rows).drop_duplicates(subset="KantonKürzel")

    merged = geodf.merge(index_df, on="KantonKürzel", how="inner").reset_index(drop=True)
    fig = px.choropleth_mapbox(
        merged,
        geojson=merged.geometry,
        locations=merged.index,
        color="Score",
        color_continuous_scale=px.colors.diverging.RdYlGn,
        range_color=[0, 100],
        labels={"Score": "Attraktivitätsindex (0–100)"},
        hover_name="KantonKürzel",
        hover_data={"Stadt": True, "Score": ":.1f"},
        opacity=0.7,
        center={"lat": 46.94809, "lon": 7.44744},
        zoom=6.5,
        mapbox_style="carto-positron",
    )
    fig.update_layout(margin={"l": 0, "r": 0, "t": 10, "b": 0})
    return fig
