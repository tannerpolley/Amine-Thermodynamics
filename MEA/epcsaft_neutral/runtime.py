from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np

from MEA.epcsaft_neutral.parameters import SPECIES, legacy_neutral_params


EPCSAFT_REPO = Path(r"C:\Users\Tanner\Documents\git\ePC-SAFT")
EPCSAFT_SRC = EPCSAFT_REPO / "src"


def load_epcsaft():
    try:
        import epcsaft  # type: ignore

        return epcsaft
    except Exception as first_exc:
        if EPCSAFT_SRC.exists():
            src_text = str(EPCSAFT_SRC)
            if src_text not in sys.path:
                sys.path.insert(0, src_text)
            try:
                import epcsaft  # type: ignore

                return epcsaft
            except Exception as second_exc:
                raise RuntimeError(
                    "Unable to import the sibling ePC-SAFT package. From this repository run "
                    "`uv sync`, or build the sibling package from "
                    "C:\\Users\\Tanner\\Documents\\git\\ePC-SAFT with "
                    "`uv sync --no-install-project` and `uv run python scripts\\build_epcsaft.py`."
                ) from second_exc
        raise RuntimeError("Unable to import epcsaft and the sibling source checkout was not found.") from first_exc


def build_neutral_mixture(params: dict[str, Any] | None = None):
    epcsaft = load_epcsaft()
    return epcsaft.ePCSAFTMixture.from_params(params or legacy_neutral_params(), species=SPECIES)


def normalize_composition(x: np.ndarray, floor: float = 1.0e-14) -> np.ndarray:
    values = np.asarray(x, dtype=float).flatten()
    values = np.clip(values, floor, None)
    total = float(np.sum(values))
    if not np.isfinite(total) or total <= 0.0:
        raise ValueError("composition has nonpositive or nonfinite total")
    return values / total

