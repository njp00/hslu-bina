"""Städte — per-city deep dive: radar across the 5 dimensions, an indicator
time-series, and the latest-values table."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src import charts, scenarios
from src.constants import CITIES, WEIGHTS
from src.data_loader import get_var, latest_val, load_data

st.title("Städte im Detail")


@st.cache_data(show_spinner=False)
def _bundle():
    return load_data()


try:
    bundle = _bundle()
except Exception as exc:
    st.error("Datenschicht konnte nicht geladen werden.")
    st.caption(f"`{type(exc).__name__}: {exc}`")
    st.stop()

df_hist = bundle["df_hist"]
scores_df = scenarios.compute_scores(df_hist, WEIGHTS)

city = st.selectbox("Stadt", CITIES)

col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("Dimensionsprofil")
    st.pyplot(charts.radar(scores_df, city))
with col2:
    st.subheader("Indikator-Zeitreihe")
    variables = sorted(str(v) for v in df_hist["Variable"].unique())
    var = st.selectbox("Indikator", variables)
    if var is None:
        st.stop()
    ts = get_var(df_hist, var)
    if ts.empty:
        st.info("Keine Werte für diesen Indikator.")
    else:
        st.pyplot(charts.timeseries(ts, title=var))

st.subheader(f"Aktuellste Werte — {city}")
rows = [
    {"Variable": v, "Wert": latest_val(df_hist, v, city)}
    for v in sorted(df_hist["Variable"].unique())
]
st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
