"""Forecasts — CAGR + 25/75-percentile scenario fan per (city, indicator)
for the 2024–2026 horizon. Indicator picker + city multi-select."""

from __future__ import annotations

import streamlit as st

from src import charts
from src.constants import CITIES
from src.data_loader import get_var, load_data
from src.forecasts import build_forecasts

st.title("Forecasts 2024–2026")
st.caption(
    "Basis = CAGR der letzten 5 Jahre · Optimistisch/Pessimistisch = "
    "75./25.-Perzentil der historischen Jahreswachstumsraten, fortgeschrieben "
    "ab dem letzten IST-Jahr."
)


@st.cache_data(show_spinner=False)
def _bundle():
    return load_data()


@st.cache_data(show_spinner=False)
def _forecasts(df_hist):
    return build_forecasts(df_hist)


try:
    bundle = _bundle()
except Exception as exc:
    st.error("Datenschicht konnte nicht geladen werden.")
    st.caption(f"`{type(exc).__name__}: {exc}`")
    st.stop()

df_hist = bundle["df_hist"]
fc = _forecasts(df_hist)

variables = sorted(str(v) for v in fc["Variable"].unique())
var = st.selectbox("Indikator", variables)
if var is None:
    st.stop()
chosen = st.multiselect("Städte", CITIES, default=CITIES[:3])

for city in chosen:
    ts = get_var(df_hist, var)
    hist = ts.loc[ts["Stadt"] == city, ["Jahr", "Wert"]]
    mask = (fc["Stadt"] == city) & (fc["Variable"] == var)
    fc_pair = fc.loc[mask, ["Jahr", "Szenario", "Wert"]]
    if hist.empty or fc_pair.empty:
        st.info(f"Keine ausreichenden Daten für {city} / {var}.")
        continue
    st.pyplot(charts.forecast_fan(hist, fc_pair, title=f"{var} — {city}"))
