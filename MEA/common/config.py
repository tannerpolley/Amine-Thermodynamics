from __future__ import annotations

from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[2]
MEA_DIR = REPO_ROOT / "MEA"
DATA_ROOT = REPO_ROOT / "data" / "MEA"
PLOT_ROOT = REPO_ROOT / "out" / "plots" / "MEA"
LEGACY_BASELINE_OUT = REPO_ROOT / "out" / "legacy_baseline"

CANONICAL_TEMPERATURE_C = 40.0
CANONICAL_TEMPERATURE_K = CANONICAL_TEMPERATURE_C + 273.15
CANONICAL_MEA_WEIGHT_FRACTION = 0.3
JOU_TEMPERATURES_C = (40, 60, 80, 100, 120)

SIX_SPECIES_ALPHA_GRID = np.linspace(0.002, 0.8, 101)
NINE_SPECIES_ALPHA_GRID = np.linspace(0.001, 0.8, 101)
