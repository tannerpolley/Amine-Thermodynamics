from __future__ import annotations

from pathlib import Path

import numpy as np

from MEA.common.config import REPO_ROOT


SPECIES = ("CO2", "MEA", "H2O")
DATASET_DIR = REPO_ROOT / "data" / "epcsaft_datasets" / "MEA_CO2_H2O_neutral_legacy"

K_CO2_MEA = 0.16
K_CO2_H2O = 0.15
K_MEA_H2O = -0.18


def legacy_neutral_params() -> dict[str, object]:
    """Return the neutral apparent-component parameters used by the legacy PC-SAFT gate."""
    return {
        "m": np.array([2.079, 3.0353, 1.9599], dtype=float),
        "s": np.array([2.7852, 3.0435, 2.363], dtype=float),
        "e": np.array([169.21, 277.174, 279.42], dtype=float),
        "e_assoc": np.array([0.0, 2586.3, 2059.28], dtype=float),
        "vol_a": np.array([0.0, 0.037470, 0.1750], dtype=float),
        "assoc_scheme": [None, "2B", "2B"],
        "k_ij": np.array(
            [
                [0.0, K_CO2_MEA, K_CO2_H2O],
                [K_CO2_MEA, 0.0, K_MEA_H2O],
                [K_CO2_H2O, K_MEA_H2O, 0.0],
            ],
            dtype=float,
        ),
        "k_hb": np.zeros((3, 3), dtype=float),
        "z": np.zeros(3, dtype=float),
        "dielc": np.array([1.4122, 32.0, 78.09], dtype=float),
        "d_born": np.zeros(3, dtype=float),
        "f_solv": np.array([1.0, 1.0, 1.5], dtype=float),
        "MW": np.array([0.04401, 0.06108, 0.01801528], dtype=float),
    }


def legacy_neutral_dataset_rows() -> tuple[list[dict[str, object]], np.ndarray]:
    params = legacy_neutral_params()
    rows = []
    for idx, component in enumerate(SPECIES):
        rows.append(
            {
                "component": component,
                "m": float(np.asarray(params["m"], dtype=float)[idx]),
                "s": float(np.asarray(params["s"], dtype=float)[idx]),
                "e": float(np.asarray(params["e"], dtype=float)[idx]),
                "e_assoc": float(np.asarray(params["e_assoc"], dtype=float)[idx]),
                "vol_a": float(np.asarray(params["vol_a"], dtype=float)[idx]),
                "assoc_scheme": "" if params["assoc_scheme"][idx] is None else str(params["assoc_scheme"][idx]),
                "z": float(np.asarray(params["z"], dtype=float)[idx]),
                "dielc": float(np.asarray(params["dielc"], dtype=float)[idx]),
                "d_born": float(np.asarray(params["d_born"], dtype=float)[idx]),
                "f_solv": float(np.asarray(params["f_solv"], dtype=float)[idx]),
                "MW": float(np.asarray(params["MW"], dtype=float)[idx]),
            }
        )
    return rows, np.asarray(params["k_ij"], dtype=float)

