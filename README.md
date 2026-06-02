# hslu-bina — Halt AG Standortanalyse

> Gruppe 06: Aebli David, Henke Mario, Knupfer Benjamin, Pfleger Niklas / 
> BINA - Business Intelligence & Analytics - FS26

Interaktives Streamlit-Dashboard zur HSLU-BINA-Fallstudie (fiktive *Halt AG*):
Ranking, Stadtprofile, Szenario-Gewichtung und Forecasts für die sechs
Zielstädte **Zürich, Bern, Basel, Lausanne, Genf, St. Gallen**.

## Abgaben

1. **Jupyter-Notebook (Google Colab)** — die vollständige Standortanalyse:
   Datenaufbereitung, Agglomerations-Aggregation, Attraktivitätsindex,
   Forecasts und Kartenvisualisierung.
   → <https://colab.research.google.com/drive/11oCXe4cgf8tfwT3utrcy8FCSalPwTvS6?usp=sharing>
   (lokal ebenfalls als [`BINA_HaltAG_Standortanalyse_V1.ipynb`](BINA_HaltAG_Standortanalyse_V1.ipynb))

2. **Präsentation (PDF)** — [Praesentation.pdf](Praesentation.pdf): Foliendeck
   zur Fallstudie, Methodik und den Ergebnissen.

3. **Video-Pitch** — [Video-Pitch.mp4](Video-Pitch.mp4): Vorstellung und
   „Verkauf" der Lösung.

4. **Streamlit-App** — interaktives Dashboard (Ranking, Stadtprofile,
   Szenarien, Forecasts, Methodik).
   → <https://hslu-bina.streamlit.app/>
   (lokal via [Lokal starten](#lokal-starten))

## Lokal starten

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

→ <http://localhost:8501> (Auto-Reload bei Speichern).

## Seiten

| Seite | Inhalt |
|---|---|
| **Übersicht** (`streamlit_app.py`) | Ranking, Radar der Siegerstadt, Kennzahlen, Karte |
| **Städte** | Radar-Profil, Indikator-Zeitreihe, aktuelle Werte |
| **Szenarien** | Gewichts-Slider + 5 Presets, Live-Ranking, URL-Sharing |
| **Forecasts** | CAGR + 25/75-Perzentil-Fächer (2024–2026) |
| **Methodik** | Quellen, Index-Formel, Forecast-Methode, Flags, Attribution |

## Projektstruktur

```
streamlit_app.py     Übersicht / Landing
pages/               Unterseiten (Streamlit Auto-Discovery)
src/
  constants.py       CITIES, CITY_COLORS, KANTON_MAP, WEIGHTS, PRESETS, INDEX_VARS
  data_loader.py     BookA-Aggregation + BookB-Merge -> df_hist (cached)
  scenarios.py       Normalisierung, Score-Berechnung
  forecasts.py       CAGR + Perzentil-Engine
  charts.py          Radar, Heatmap, Ranking, Zeitreihe, Choropleth
data/                BookA.xlsx, BookB.xlsx, kantone.geojson
.streamlit/          Theme & Page-Config
```

## Tests

```bash
.venv\Scripts\python.exe tests\test_forecasts.py     # ohne Zusatz-Deps
# oder mit pytest:
pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest tests\
```

`tests/test_forecasts.py` pinnt die portierte Forecast- und Index-Logik
gegen die Notebook-Outputs (exakte numerische Übereinstimmung).

## Status

Vollständig portiert aus dem V1-Notebook und gegen die echten Daten
verifiziert. Einziger offener Punkt: erster GitHub-Push + Streamlit-Cloud-
Verbindung.

## Deployment

Public GitHub-Repo → <https://share.streamlit.io> → *New app* → Repo,
Branch `main`, Main file `streamlit_app.py`. Jeder Push auf `main` löst
ein Auto-Redeploy aus. Keine Secrets, keine Env-Vars.
