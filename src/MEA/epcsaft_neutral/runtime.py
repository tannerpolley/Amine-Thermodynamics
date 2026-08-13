from __future__ import annotations

from typing import Any

import numpy as np


def load_epcsaft():
    """Import only the installed unified Engine distribution."""
    try:
        import epcsaft  # type: ignore

        return epcsaft
    except Exception as first_exc:
        raise RuntimeError(
            "Unable to import the installed unified epcsaft Engine wheel. "
            "Source-checkout discovery is forbidden."
        ) from first_exc


def build_neutral_mixture(params: dict[str, Any] | None = None):
    del params
    raise RuntimeError(
        "The retired ePCSAFTMixture neutral diagnostic is quarantined; it is "
        "not a compatibility path for the installed unified Engine."
    )


def normalize_composition(x: np.ndarray, floor: float = 1.0e-14) -> np.ndarray:
    values = np.asarray(x, dtype=float).flatten()
    values = np.clip(values, floor, None)
    total = float(np.sum(values))
    if not np.isfinite(total) or total <= 0.0:
        raise ValueError("composition has nonpositive or nonfinite total")
    return values / total
