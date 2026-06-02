"""Übersicht — landing page: ranking under the active scenario, the winner
city's radar profile, quick per-city stats and the canton choropleth.

Registered in ``streamlit_app.py`` via ``st.navigation`` (page config is set
there — do not call ``st.set_page_config`` here).
"""

from __future__ import annotations

import streamlit as st

from src import charts, scenarios
from src.constants import WEIGHTS
from src.data_loader import load_data


@st.cache_data(show_spinner=False)
def _bundle():
    return load_data()


st.title("Halt AG — Standortanalyse")
st.markdown(
    "Interaktive Auswertung der Standort-Attraktivität für junge Fachkräfte "
    "in den sechs Zielstädten **Zürich · Bern · Basel · Lausanne · Genf · "
    "St. Gallen**."
)

try:
    bundle = _bundle()
except Exception as exc:
    st.error("Datenschicht konnte nicht geladen werden.")
    st.caption(f"`{type(exc).__name__}: {exc}`")
    st.stop()

df_hist = bundle["df_hist"]
scores_df = scenarios.compute_scores(df_hist, WEIGHTS)
winner = scores_df.index[0]

st.success(f"**Empfehlung (Basis-Szenario): {winner}** — höchster gewichteter Attraktivitätsindex.")

col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("Ranking (Basis-Szenario)")
    st.pyplot(charts.ranking_bar(scores_df, WEIGHTS))
with col2:
    st.subheader("Profil der Siegerstadt")
    st.pyplot(charts.radar(scores_df, winner))

st.subheader("Karte — Attraktivitätsindex je Kanton")
if bundle.get("geodf") is not None:
    st.plotly_chart(charts.choropleth(scores_df, bundle["geodf"]), width="stretch")
else:
    st.info("`data/kantone.geojson` oder geopandas fehlt — Karte wird übersprungen.")

st.subheader("Schnellkennzahlen")
table = (scores_df * 100).round(1)
table.index.name = "Stadt"
st.dataframe(table, width="stretch")
