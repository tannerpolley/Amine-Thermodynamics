from __future__ import annotations

from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
MEA_DIR = SRC_ROOT / "MEA"
REFERENCE_DATA_ROOT = REPO_ROOT / "data" / "reference"
DATA_ROOT = REFERENCE_DATA_ROOT / "MEA"
EPCSAFT_DATASET_ROOT = REFERENCE_DATA_ROOT / "epcsaft_datasets"
ANALYSES_ROOT = REPO_ROOT / "analyses"
CANONICAL_TEMPERATURE_C = 40.0
CANONICAL_TEMPERATURE_K = CANONICAL_TEMPERATURE_C + 273.15
CANONICAL_MEA_WEIGHT_FRACTION = 0.3
JOU_TEMPERATURES_C = (40, 60, 80, 100, 120)

SIX_SPECIES_ALPHA_GRID = np.linspace(0.002, 0.8, 101)
