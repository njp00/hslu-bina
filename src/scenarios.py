"""Attractiveness index computation — port of notebook cell 15.

For each dimension, min-max normalize every indicator across the six cities
(respecting its +1/-1 direction), average the normalized indicators, then
take a weighted sum across dimensions for the total score.

``INDEX_VARS`` (dimension -> [(indicator, direction)]) and ``WEIGHTS`` live
in ``constants.py``.
"""

from __future__ import annotations

import pandas as pd

from .constants import CITIES, DIMENSIONS, INDEX_VARS, WEIGHTS
from .data_loader import latest_val


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    """Rescale dimension weights to sum to 1.0 (equal-weight on degenerate)."""
    total = sum(weights.values())
    if total <= 0:
        return {d: 1.0 / len(DIMENSIONS) for d in DIMENSIONS}
    return {d: w / total for d, w in weights.items()}


def minmax_normalize(series: pd.Series, direction: int) -> pd.Series:
    """Min-max scale a per-city series to [0, 1], honoring direction.

    A flat series maps to a neutral 0.5. NaN values are dropped upstream.
    """
    s = pd.to_numeric(series, errors="coerce").dropna()
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series([0.5] * len(s), index=s.index)
    norm = (s - mn) / (mx - mn)
    return norm if direction == 1 else 1 - norm


def compute_scores(
    df_hist: pd.DataFrame,
    weights: dict[str, float] = WEIGHTS,
    index_vars: dict[str, list[tuple[str, int]]] = INDEX_VARS,
) -> pd.DataFrame:
    """Per-city dimension scores + weighted total, sorted descending.

    Returns a frame indexed by city with one column per dimension plus a
    ``Gesamt`` column (all in [0, 1]).
    """
    scores: dict[str, object] = {dim: {} for dim in weights}
    for dim, var_list in index_vars.items():
        dim_scores = []
        for var, direction in var_list:
            raw = {city: latest_val(df_hist, var, city) for city in CITIES}
            s = pd.Series({k: float(v) for k, v in raw.items() if v is not None})
            if len(s) >= 2:
                dim_scores.append(minmax_normalize(s, direction))
        if dim_scores:
            scores[dim] = pd.concat(dim_scores, axis=1).mean(axis=1).reindex(CITIES)

    scores_df = pd.DataFrame(scores)
    scores_df["Gesamt"] = sum(
        scores_df[dim] * w for dim, w in weights.items() if dim in scores_df.columns
    )
    return scores_df.sort_values("Gesamt", ascending=False)
