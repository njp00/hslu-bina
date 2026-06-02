"""Forecast engine — port of the V1 notebook's ``compute_forecast()``
(cell 12).

Three scenarios per (city, variable):

* **Basis** — CAGR over the last (up to) ``N_HIST_YEARS`` available years,
  compounded forward from the last observed value.
* **Optimistisch** — 75th percentile of historical year-over-year growth
  rates (needs >= 2 rates, else falls back to CAGR).
* **Pessimistisch** — 25th percentile, same treatment.

Each forecast year ``fy`` is projected as ``last_val * (1 + rate) ** (fy -
last_year)``, i.e. compounded from the most recent actual year.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .constants import FORECAST_YEARS, N_HIST_YEARS
from .data_loader import year_columns

# Output scenario labels (notebook keys -> UI labels).
SCENARIOS = {"basis": "Basis", "opt": "Optimistisch", "pes": "Pessimistisch"}


def compute_forecast(
    df_hist: pd.DataFrame,
    city: str,
    variable: str,
    n: int = N_HIST_YEARS,
    years: list[int] = FORECAST_YEARS,
) -> dict | None:
    """Forecast dict for one (city, variable), or None if not computable.

    Returns ``{'last_val', 'last_year', 'cagr', <fy>: {'basis','opt','pes'}}``.
    """
    row = df_hist[(df_hist["Variable"] == variable) & (df_hist["Stadt"] == city)]
    if row.empty:
        return None

    year_cols = year_columns(df_hist)
    series = row[year_cols].T.rename(columns={row.index[0]: "wert"}).dropna()
    series.index = series.index.astype(int)
    if len(series) < 2:
        return None

    recent = series.tail(n)
    v0, v1 = recent["wert"].iloc[0], recent["wert"].iloc[-1]
    y0, y1 = recent.index[0], recent.index[-1]
    span = y1 - y0
    if v0 == 0 or span == 0:
        return None
    cagr = (v1 / v0) ** (1 / span) - 1

    yoy = series["wert"].pct_change().dropna().values
    opt_rate = float(np.percentile(yoy, 75)) if len(yoy) >= 2 else cagr
    pes_rate = float(np.percentile(yoy, 25)) if len(yoy) >= 2 else cagr

    result: dict = {"last_val": v1, "last_year": y1, "cagr": cagr}
    for fy in years:
        n_fwd = fy - y1
        result[fy] = {
            "basis": v1 * (1 + cagr) ** n_fwd,
            "opt": v1 * (1 + opt_rate) ** n_fwd,
            "pes": v1 * (1 + pes_rate) ** n_fwd,
        }
    return result


def build_forecasts(
    df_hist: pd.DataFrame, years: list[int] = FORECAST_YEARS
) -> pd.DataFrame:
    """Tidy forecasts for every (Stadt, Variable) pair with >= 2 hist values.

    Columns: ``Stadt | Variable | Jahr | Szenario | Wert`` (forecast horizon
    only).
    """
    records: list[dict] = []
    pairs = df_hist[["Stadt", "Variable"]].drop_duplicates()
    for _, (city, variable) in pairs.iterrows():
        result = compute_forecast(df_hist, city, variable, years=years)
        if result is None:
            continue
        for fy in years:
            for key, label in SCENARIOS.items():
                records.append(
                    {
                        "Stadt": city,
                        "Variable": variable,
                        "Jahr": fy,
                        "Szenario": label,
                        "Wert": result[fy][key],
                    }
                )
    return pd.DataFrame.from_records(
        records, columns=["Stadt", "Variable", "Jahr", "Szenario", "Wert"]
    )
