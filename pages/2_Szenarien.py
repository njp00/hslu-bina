"""Szenarien — adjust the five dimension weights via sliders or pick a
preset, and watch the ranking recompute live. Weights are mirrored to the
URL via ``st.query_params`` so a configuration is shareable.

Selecting a preset loads its weights into the sliders (via an ``on_change``
callback that writes the slider session-state keys). Manual slider edits
persist and update the URL; on first load the sliders are seeded from the
URL if present, otherwise from the first preset.
"""

from __future__ import annotations

import streamlit as st

from src import charts, scenarios
from src.constants import DIMENSIONS, PRESETS
from src.data_loader import load_data

st.title("Szenarien & Gewichtung")


@st.cache_data(show_spinner=False)
def _bundle():
    return load_data()


PRESET_NAMES = list(PRESETS.keys())
SLIDER_KEYS = {dim: f"w_{dim}" for dim in DIMENSIONS}


def _apply_preset() -> None:
    """on_change for the preset selectbox: push its weights into the sliders."""
    preset = PRESETS[st.session_state["preset"]]
    for dim in DIMENSIONS:
        st.session_state[SLIDER_KEYS[dim]] = float(preset[dim])


def _init_state() -> None:
    """Seed the slider + preset state once per session.

    Priority: URL query params (shareable link) > first preset.
    """
    if st.session_state.get("_scn_init"):
        return
    st.session_state["_scn_init"] = True
    st.session_state.setdefault("preset", PRESET_NAMES[0])

    qp = st.query_params
    weights = None
    if all(d in qp for d in DIMENSIONS):
        try:
            weights = {d: float(qp[d]) for d in DIMENSIONS}
        except ValueError:
            weights = None
    if weights is None:
        weights = PRESETS[st.session_state["preset"]]

    for dim in DIMENSIONS:
        st.session_state[SLIDER_KEYS[dim]] = float(weights[dim])


try:
    bundle = _bundle()
except Exception as exc:
    st.error("Datenschicht konnte nicht geladen werden.")
    st.caption(f"`{type(exc).__name__}: {exc}`")
    st.stop()

_init_state()

st.selectbox("Preset", PRESET_NAMES, key="preset", on_change=_apply_preset)

st.caption("Gewichte (werden auf Summe 1.0 normalisiert):")
cols = st.columns(len(DIMENSIONS))
for col, dim in zip(cols, DIMENSIONS):
    col.slider(dim, 0.0, 1.0, step=0.05, key=SLIDER_KEYS[dim])

weights = {dim: st.session_state[SLIDER_KEYS[dim]] for dim in DIMENSIONS}
st.query_params.update({d: f"{w:.2f}" for d, w in weights.items()})

norm = scenarios.normalize_weights(weights)
st.caption("Normalisiert: " + " · ".join(f"{d} {norm[d]:.0%}" for d in DIMENSIONS))

scores_df = scenarios.compute_scores(bundle["df_hist"], norm)
st.subheader("Ranking")
st.pyplot(charts.ranking_bar(scores_df, norm))
st.dataframe((scores_df * 100).round(1), width="stretch")
