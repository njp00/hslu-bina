"""Pin a few known values against the V1 notebook output so the ported
forecast + index engines stay numerically aligned with it.

Reference values taken from the executed notebook
(``BINA_HaltAG_Standortanalyse_V1.ipynb``), cells 12 and 15.

Run: ``python -m pytest tests/`` (or just ``python tests/test_forecasts.py``).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import forecasts, scenarios
from src.data_loader import load_data

_BUNDLE = load_data()
DF = _BUNDLE["df_hist"]

MIETZINS = "Monatlicher Netto-Mietzins pro m2 (in CHF)"


def _close(a, b, tol=0.05):
    return math.isclose(a, b, abs_tol=tol)


def test_forecast_mietzins_zuerich():
    """Cell 12 reference: last 21.4 (2023), CAGR 1.83%, fan as below."""
    fc = forecasts.compute_forecast(DF, "Zürich", MIETZINS)
    assert fc is not None
    assert _close(fc["last_val"], 21.4)
    assert fc["last_year"] == 2023
    assert _close(fc["cagr"] * 100, 1.83, tol=0.01)
    expected = {
        2024: (21.79, 21.76, 21.45),
        2025: (22.19, 22.13, 21.51),
        2026: (22.60, 22.50, 21.56),
    }
    for year, (basis, opt, pes) in expected.items():
        assert _close(fc[year]["basis"], basis), year
        assert _close(fc[year]["opt"], opt), year
        assert _close(fc[year]["pes"], pes), year


def test_index_ranking():
    """Cell 15 reference: total scores (x100) and ranking order."""
    scores = scenarios.compute_scores(DF)
    total = (scores["Gesamt"] * 100).round(1)
    assert list(total.index) == ["St. Gallen", "Bern", "Zürich", "Lausanne", "Basel", "Genf"]
    expected = {
        "St. Gallen": 67.2, "Bern": 65.3, "Zürich": 52.8,
        "Lausanne": 44.1, "Basel": 38.2, "Genf": 30.2,
    }
    for city, val in expected.items():
        assert _close(total[city], val, tol=0.1), city


def test_build_forecasts_shape():
    """Every computable pair yields 3 scenarios x 3 years."""
    fc = forecasts.build_forecasts(DF)
    assert set(fc["Szenario"]) == {"Basis", "Optimistisch", "Pessimistisch"}
    assert set(fc["Jahr"]) == {2024, 2025, 2026}
    counts = fc.groupby(["Stadt", "Variable"]).size()
    assert (counts == 9).all()


if __name__ == "__main__":
    test_forecast_mietzins_zuerich()
    test_index_ranking()
    test_build_forecasts_shape()
    print("all tests passed")
