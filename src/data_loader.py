"""Data layer: load BookA + BookB, normalize, and expose ``df_hist`` plus
the notebook helper functions and the dissolved canton GeoDataFrame.

Single cached entry point :func:`load_data` builds everything once per
session. Ported from notebook cells 2 (BookA aggregation), 3 (BookB merge)
and 20/22 (GeoJSON dissolve).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, TypedDict

import numpy as np
import pandas as pd

from .constants import (
    ADDITIVE_VARS,
    CITY_RENAME_A,
    CITY_RENAME_B,
    KANTON_MAP,
    OUR_CANTONS,
)


class DataBundle(TypedDict):
    """Return type of :func:`load_data`."""

    df_hist: pd.DataFrame
    geodf: Any  # geopandas.GeoDataFrame | None (geopandas import is optional)

try:
    import streamlit as st

    cache = st.cache_data
except Exception:  # pragma: no cover - allow import outside Streamlit
    def cache(func):
        return func

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BOOK_A = DATA_DIR / "BookA.xlsx"
BOOK_B = DATA_DIR / "BookB.xlsx"
GEOJSON = DATA_DIR / "kantone.geojson"


# --------------------------------------------------------------------------
# BookA — aggregate the three geographic levels per city (notebook cell 2)
# --------------------------------------------------------------------------
def _split_city_level(s: object) -> tuple[str, str]:
    """Split a 'City: level' label into (city, level.lower())."""
    if ":" in str(s):
        stadt, ebene = str(s).split(":", 1)
        return stadt.strip(), ebene.strip().lower()
    return str(s).strip(), ""


def _ebenen_klasse(e: str) -> str:
    if "core" in e:
        return "kernstadt"
    if "other" in e:
        return "guertel"
    return "total"


def _load_booka() -> pd.DataFrame:
    """BookA.xlsx -> wide df (Kategorie|Stadt|Variable|<year str cols>).

    Drops the pre-computed agglomeration total (avoids double-counting) and
    rebuilds each city from core city + Gürtelgemeinden: SUM for
    ``ADDITIVE_VARS``, AVERAGE for everything else.
    """
    raw = pd.read_excel(BOOK_A, sheet_name="Sheet1")

    cl = raw["Stadt / Agglomeration"].map(_split_city_level)
    raw["_Stadt_roh"] = [x[0] for x in cl]
    raw["_Ebene"] = [x[1] for x in cl]
    raw["_Klasse"] = raw["_Ebene"].map(_ebenen_klasse)
    raw["Stadt"] = raw["_Stadt_roh"].map(CITY_RENAME_A)

    # Keep only the disjoint parts (kernstadt + guertel), drop the total.
    parts = raw[(raw["_Klasse"] != "total") & raw["Stadt"].notna()].copy()
    parts = parts.rename(columns={"Variablen": "Variable", "TIME_PERIOD": "Jahr"})
    parts["Jahr"] = parts["Jahr"].astype(int)

    agg = (
        parts.groupby(["Kategorie", "Stadt", "Variable", "Jahr"])["OBS_VALUE"]
        .agg(Summe=lambda s: s.sum(min_count=1), Mittel="mean")
        .reset_index()
    )
    agg["Wert"] = np.where(
        agg["Variable"].isin(ADDITIVE_VARS), agg["Summe"], agg["Mittel"]
    )

    wide = (
        agg.pivot_table(
            index=["Kategorie", "Stadt", "Variable"],
            columns="Jahr",
            values="Wert",
            aggfunc="first",
        ).reset_index()
    )
    wide.columns = [str(c) if not isinstance(c, str) else c for c in wide.columns]
    wide.columns.name = None
    return wide


# --------------------------------------------------------------------------
# BookB — wide climate -> long -> wide per city (notebook cell 3)
# --------------------------------------------------------------------------
def _load_bookb() -> pd.DataFrame:
    """BookB.xlsx (wide climate) -> same wide shape as BookA.

    Neuenburg is the climate proxy for Lausanne.
    """
    raw = pd.read_excel(BOOK_B, sheet_name="Sheet1")
    stadt_cols = [c for c in raw.columns if c in CITY_RENAME_B]

    long = raw.melt(
        id_vars=["Kategorie", "Variablen", "Jahr"],
        value_vars=stadt_cols,
        var_name="_Stadt_roh",
        value_name="Wert",
    )
    long["Stadt"] = long["_Stadt_roh"].map(CITY_RENAME_B)
    long = long.rename(columns={"Variablen": "Variable"})
    long["Jahr"] = long["Jahr"].astype(int)

    wide = (
        long.pivot_table(
            index=["Kategorie", "Stadt", "Variable"],
            columns="Jahr",
            values="Wert",
            aggfunc="first",
        ).reset_index()
    )
    wide.columns = [str(c) if not isinstance(c, str) else c for c in wide.columns]
    wide.columns.name = None
    return wide


def _build_df_hist() -> pd.DataFrame:
    df = pd.concat([_load_booka(), _load_bookb()], ignore_index=True)
    year_cols = sorted([c for c in df.columns if str(c).isdigit()], key=int)
    return df[["Kategorie", "Stadt", "Variable"] + year_cols]


# --------------------------------------------------------------------------
# GeoJSON — dissolve cantons to one geometry each (notebook cells 20/22)
# --------------------------------------------------------------------------
def _load_geodf():
    """Dissolved GeoDataFrame of our seven relevant cantons, or None.

    Returns columns ``KantonKürzel | geometry``. Requires geopandas; on any
    failure (missing file, no geopandas) returns None so the app degrades
    gracefully instead of crashing the map.
    """
    if not GEOJSON.exists():
        return None
    try:
        import geopandas as gpd
    except Exception:
        return None
    gdf = gpd.read_file(GEOJSON)
    gdf["KantonKürzel"] = gdf["KantonName"].map(KANTON_MAP)
    gdf = gdf[gdf["KantonKürzel"].isin(OUR_CANTONS)]
    return gdf.dissolve(by="KantonKürzel", as_index=False).reset_index(drop=True)


# --------------------------------------------------------------------------
# Public entry point
# --------------------------------------------------------------------------
@cache
def load_data() -> DataBundle:
    """Build and cache the full data bundle.

    Returns ``{"df_hist": DataFrame, "geodf": GeoDataFrame | None}``.
    """
    if not (BOOK_A.exists() and BOOK_B.exists()):
        raise FileNotFoundError(
            f"Missing data files in {DATA_DIR}. Expected BookA.xlsx, "
            "BookB.xlsx and kantone.geojson."
        )
    return {"df_hist": _build_df_hist(), "geodf": _load_geodf()}


# --------------------------------------------------------------------------
# Helpers (port of notebook cell 6) — operate on df_hist.
# --------------------------------------------------------------------------
def year_columns(df_hist: pd.DataFrame) -> list[str]:
    """Year columns (as strings) present in df_hist, ascending."""
    return sorted([c for c in df_hist.columns if str(c).isdigit()], key=int)


def find_var(df_hist: pd.DataFrame, variable_name: str) -> pd.DataFrame:
    """Rows for a variable; tolerant to Kernstadt/Proxy suffixes (startswith)."""
    exact = df_hist[df_hist["Variable"] == variable_name]
    if not exact.empty:
        return exact
    return df_hist[df_hist["Variable"].str.startswith(variable_name)]


def get_var(
    df_hist: pd.DataFrame, variable_name: str, years: list[str] | None = None
) -> pd.DataFrame:
    """Long ``Stadt | Jahr | Wert`` frame for one variable, NaN dropped."""
    cols = years if years else year_columns(df_hist)
    subset = find_var(df_hist, variable_name).copy()
    if subset.empty:
        return pd.DataFrame(columns=["Stadt", "Jahr", "Wert"])
    melted = subset.melt(
        id_vars="Stadt", value_vars=cols, var_name="Jahr", value_name="Wert"
    )
    melted["Jahr"] = melted["Jahr"].astype(int)
    return melted.dropna(subset=["Wert"])


def latest_val(df_hist: pd.DataFrame, variable_name: str, city: str):
    """Most recent non-NaN value of a variable for one city, or None."""
    subset = find_var(df_hist, variable_name)
    row = subset[subset["Stadt"] == city]
    if row.empty:
        return None
    for yr in reversed(year_columns(df_hist)):
        v = row.iloc[0].get(yr)
        if pd.notna(v):
            return v
    return None


def missing_share(df_hist: pd.DataFrame) -> pd.Series:
    """Share of missing values per variable (0–1), descending."""
    cols = year_columns(df_hist)
    return (
        df_hist.groupby("Variable")[cols]
        .apply(lambda x: x.isna().sum().sum() / x.size)
        .sort_values(ascending=False)
    )
