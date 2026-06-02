"""Entry point / navigation router for the Halt AG Standortanalyse
dashboard.

Uses ``st.navigation`` so the sidebar labels are explicit (the landing page
shows as "Übersicht", not "streamlit app"). This is the single place that
calls ``st.set_page_config`` — the individual page scripts must not.

Run with ``streamlit run streamlit_app.py``.
"""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Halt AG — Standortanalyse",
    page_icon="📍",
    layout="wide",
)

nav = st.navigation(
    [
        st.Page("pages/0_Übersicht.py", title="Übersicht", icon="📍", default=True),
        st.Page("pages/1_Städte.py", title="Städte", icon="🏙️"),
        st.Page("pages/2_Szenarien.py", title="Szenarien", icon="🎚️"),
        st.Page("pages/3_Forecasts.py", title="Forecasts", icon="📈"),
        st.Page("pages/4_Methodik.py", title="Methodik", icon="📚"),
    ]
)
nav.run()
