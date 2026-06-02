"""Single source of truth for cities, colors, canton mapping, dimension
weights, scenario presets and the index variable mapping.

Ported verbatim from the V1 notebook
(``BINA_HaltAG_Standortanalyse_V1.ipynb``) — keep aligned with it.
Referenced by ``data_loader.py``, ``scenarios.py``, ``charts.py`` and the
Methodik page.
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# Cities & colors (notebook tab10 palette)
# --------------------------------------------------------------------------
CITY_COLORS: dict[str, str] = {
    "Zürich": "#1f77b4",
    "Bern": "#ff7f0e",
    "Basel": "#2ca02c",
    "Lausanne": "#d62728",
    "Genf": "#9467bd",
    "St. Gallen": "#8c564b",
}
CITIES: list[str] = list(CITY_COLORS.keys())

# City-centre coordinates (for the bubble map / hover).
CITY_COORDS: dict[str, tuple[float, float]] = {
    "Zürich": (47.3769, 8.5417),
    "Bern": (46.9481, 7.4474),
    "Basel": (47.5596, 7.5886),
    "Lausanne": (46.5197, 6.6323),
    "Genf": (46.2044, 6.1432),
    "St. Gallen": (47.4245, 9.3767),
}

# --------------------------------------------------------------------------
# Canton mapping (for the choropleth)
# --------------------------------------------------------------------------
# GeoJSON KantonName (German/native) -> ISO 3166-2:CH abbreviation.
KANTON_MAP: dict[str, str] = {
    "Zürich": "ZH", "Bern": "BE", "Luzern": "LU", "Uri": "UR",
    "Schwyz": "SZ", "Obwalden": "OW", "Nidwalden": "NW", "Glarus": "GL",
    "Zug": "ZG", "Fribourg": "FR", "Solothurn": "SO", "Basel-Stadt": "BS",
    "Basel-Landschaft": "BL", "Schaffhausen": "SH",
    "Appenzell Ausserrhoden": "AR", "Appenzell Innerrhoden": "AI",
    "St. Gallen": "SG", "Graubünden": "GR", "Aargau": "AG", "Thurgau": "TG",
    "Ticino": "TI", "Vaud": "VD", "Valais": "VS", "Neuchâtel": "NE",
    "Genève": "GE", "Jura": "JU",
}

# Cantons relevant to our six cities (Basel = BS + BL agglomeration).
OUR_CANTONS: set[str] = {"ZH", "BE", "BS", "BL", "VD", "GE", "SG"}

# City -> canton(s) for the index→canton join.
CITY_TO_CANTONS: dict[str, list[str]] = {
    "Zürich": ["ZH"],
    "Bern": ["BE"],
    "Basel": ["BS", "BL"],
    "Lausanne": ["VD"],
    "Genf": ["GE"],
    "St. Gallen": ["SG"],
}

# --------------------------------------------------------------------------
# Data aggregation (BookA)
# --------------------------------------------------------------------------
# Variables aggregated by SUM (absolute counts). Everything else averages.
ADDITIVE_VARS: set[str] = {
    "Ständige Wohnbevölkerung, total",
    "Kinos",
    "Museen",
    "Theater",
}

# Raw city label -> canonical German short form.
CITY_RENAME_A: dict[str, str] = {
    "Zurich": "Zürich", "Bern": "Bern", "Basel": "Basel",
    "Geneva": "Genf", "Lausanne": "Lausanne", "St. Gallen": "St. Gallen",
}
CITY_RENAME_B: dict[str, str] = {
    "Basel": "Basel", "Bern": "Bern", "Genf": "Genf",
    "Neuenburg (Lausanne)": "Lausanne",
    "St. Gallen": "St. Gallen", "Zürich": "Zürich",
}

# --------------------------------------------------------------------------
# Attractiveness index — dimensions, weights, indicator mapping
# --------------------------------------------------------------------------
WEIGHTS: dict[str, float] = {
    "Arbeitsmarkt": 0.30,
    "Wohnen": 0.25,
    "Lebensqualität": 0.20,
    "Demografie": 0.15,
    "Mobilität": 0.10,
}
DIMENSIONS: list[str] = list(WEIGHTS.keys())

# Dimension -> list of (indicator, direction). +1 higher is better,
# -1 lower is better. Ported verbatim from notebook cell 15.
INDEX_VARS: dict[str, list[tuple[str, int]]] = {
    "Arbeitsmarkt": [
        ("Erwerbstätigenquote der 20-64-Jährigen (in %), total", +1),
        ("Arbeitslosenquote (SECO) in %, total", -1),
        ("Jugendarbeitslosenquote (SECO) der 15- bis 24-Jährigen (in %), total", -1),
        ("Durchschnittliches steuerbares Einkommen, das für die direkte Bundessteuer pro steuerpflichtige Person massgebend ist (in CHF)", +1),
        ("Anteil der Beschäftigten im IKT-Sektor (Medienbranche enthalten), in %", +1),
        ("Anteil der Beschäftigten des tertiären Wirtschaftssektors (in %)", +1),
    ],
    "Wohnen": [
        ("Monatlicher Netto-Mietzins pro m2 (in CHF)", -1),
        ("Leerwohnungsziffer (in %)", +1),
        ("Durchschnittliche Wohnfläche pro Person (in m2)", +1),
    ],
    "Lebensqualität": [
        ("Museen pro 100'000 Einwohnerinnen und Einwohner", +1),
        ("Theater pro 100'000 Einwohnerinnen und Einwohner", +1),
        ("Kinos pro 100'000 Einwohnerinnen und Einwohner", +1),
        ("Tägliche Sonnenscheindauer in Stunden", +1),
        ("Mittlere Jahrestemperatur in °C", +1),
        ("Jahresniederschlag (mm)", -1),
        ("Anzahl Gewaltstraftaten pro 1000 Einwohnerinnen und Einwohner", -1),
        ("Einbruch- und Einschleichdiebstähle in Wohneinheiten pro 1000 Einwohnerinnen und Einwohner", -1),
    ],
    "Demografie": [
        ("Anteil der ständigen Wohnbevölkerung im Alter von 20 bis 24 Jahren (in %), total", +1),
        ("Anteil der ständigen Wohnbevölkerung im Alter von 25 bis 34 Jahren (in %), total", +1),
        ("Medianalter (in Jahren)", -1),
        ("Sozialhilfequote (in %), total", -1),
        ("Anteil der Bevölkerung im Alter von 25 bis 64 Jahren mit Tertiärstufe als höchstem Bildungsabschluss (ISCED 5-8) in %, total", +1),
    ],
    "Mobilität": [
        ("Anteil öffentlicher Verkehr-Pendler (in %)", +1),
        ("Preis einer kombinierten Monatskarte (ÖV) für Fahrten von 5 bis 10 km im Stadtzentrum (in CHF)", -1),
        ("Durchschnittliche Arbeitswegzeit (in Minuten)", -1),
        ("Motorisierungsgrad", -1),
    ],
}

# Five preset scenarios offered in the Szenarien page (per CLAUDE.md).
PRESETS: dict[str, dict[str, float]] = {
    "Basis (Ausgangslage)": dict(WEIGHTS),
    "Einheitliche Gewichtung": {d: 0.20 for d in DIMENSIONS},
    "Fokus Kosten": {
        "Arbeitsmarkt": 0.20, "Wohnen": 0.40, "Lebensqualität": 0.15,
        "Demografie": 0.15, "Mobilität": 0.10,
    },
    "Fokus Arbeitsmarkt": {
        "Arbeitsmarkt": 0.50, "Wohnen": 0.15, "Lebensqualität": 0.15,
        "Demografie": 0.10, "Mobilität": 0.10,
    },
    "Fokus Lebensqualität": {
        "Arbeitsmarkt": 0.20, "Wohnen": 0.15, "Lebensqualität": 0.40,
        "Demografie": 0.15, "Mobilität": 0.10,
    },
}

# --------------------------------------------------------------------------
# Forecasts & data quality
# --------------------------------------------------------------------------
FORECAST_YEARS: list[int] = [2024, 2025, 2026]
N_HIST_YEARS: int = 5  # trailing years used for the CAGR base
MISSING_THRESHOLD: float = 0.20  # >20% missing -> flagged (cell 5/12)
