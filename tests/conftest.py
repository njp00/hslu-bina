"""Ensure the project root is importable so ``from src import ...`` works
regardless of how the tests are launched."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
