"""Methodik — data sources, index formula, dimension→indicator mapping,
forecast method, proxy/flag legend and attribution."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.constants import (
    FORECAST_YEARS,
    INDEX_VARS,
    MISSING_THRESHOLD,
    PRESETS,
    WEIGHTS,
)

st.title("Methodik")

st.header("Datenquellen")
st.markdown(
    "| Quelle | Datei | Inhalt |\n"
    "|---|---|---|\n"
    "| BFS Städtestatistik | `BookA.xlsx` | Alle Nicht-Klima-Indikatoren, "
    "9 Kategorien, 3 geografische Ebenen je Stadt, 2010–2025 |\n"
    "| MeteoSchweiz | `BookB.xlsx` | Klima-Indikatoren (Sonnenschein, "
    "Niederschlag, Temperatur, Neuschnee); Lausanne = Station Neuenburg |\n"
    "| Dozierenden-GeoJSON | `kantone.geojson` | Kantonsgrenzen für die Karte |"
)

st.header("Attraktivitäts-Index")
st.markdown(
    "Fünf Dimensionen (nicht die neun BFS-Kategorien — *Lebensqualität* ist "
    "ein Komposit aus Sicherheit, Umwelt & Gesundheit, Freizeit & Kultur und "
    "Soziales). Pro Dimension: jeden Indikator richtungsbewusst auf [0, 1] "
    "min-max-normalisieren, über die Indikatoren mitteln. Gesamtscore = "
    "gewichtete Summe über die Dimensionen."
)
st.subheader("Standardgewichte (Basis)")
st.dataframe(
    pd.Series(WEIGHTS, name="Gewicht").to_frame().style.format("{:.0%}")
)

st.subheader("Preset-Szenarien")
st.dataframe(pd.DataFrame(PRESETS).T.style.format("{:.0%}"))

st.subheader("Dimension → Indikator (Richtung)")
rows = [
    {
        "Dimension": dim,
        "Indikator": ind,
        "Richtung": "↑ höher = besser" if d > 0 else "↓ tiefer = besser",
    }
    for dim, var_list in INDEX_VARS.items()
    for ind, d in var_list
]
st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

st.header("Forecast-Methode")
st.markdown(
    f"- **Horizont:** {', '.join(map(str, FORECAST_YEARS))}\n"
    "- **Basis (moderat):** CAGR über die letzten (bis zu) 5 verfügbaren "
    "Jahre, fortgeschrieben.\n"
    "- **Optimistisch:** 75.-Perzentil der historischen "
    "Jahr-zu-Jahr-Wachstumsraten, konstant fortgeschrieben.\n"
    "- **Pessimistisch:** 25.-Perzentil, gleich behandelt.\n"
    "- Berechnet für jedes (Stadt, Variable)-Paar mit ≥ 2 historischen Werten."
)

st.header("Hinweise & Flags")
st.markdown(
    "- ⚠ **Lausanne-Klima = Neuenburg.** Proxy-Station, überall markiert.\n"
    "- **Agglomerations-Aggregation.** Vorberechnete Agglo-Totale werden "
    "verworfen; Stadt-Totale aus Kernstadt + Gürtelgemeinden rekonstruiert "
    "(SUM für Zählvariablen, AVERAGE für Raten).\n"
    f"- **Fehlwerte.** Variablen mit > {MISSING_THRESHOLD:.0%} fehlenden "
    "Werten werden markiert und standardmässig aus dem Index ausgeschlossen.\n"
    "- **Städtenamen** werden ausschliesslich in `data_loader.py` "
    "normalisiert (`Geneva`→`Genf`, `Zurich`→`Zürich`)."
)

st.header("Attribution")
st.markdown(
    "HSLU BINA Fallstudie · fiktive *Halt AG* · Daten: BFS Städtestatistik & "
    "MeteoSchweiz · erstellt mit Streamlit."
)
