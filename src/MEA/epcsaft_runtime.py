from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[2]
EPCSAFT_REPO = Path(r"C:\Users\Tanner\Documents\git\ePC-SAFT")
EPCSAFT_SRC = EPCSAFT_REPO / "src"
DATASET_DIR = REPO_ROOT / "data" / "reference" / "epcsaft_datasets" / "MEA_CO2_H2O_draft"
EPCSAFT_OUT_DIR = REPO_ROOT / "analyses" / "epcsaft_ionic_regression" / "results" / "diagnostics"

SPECIES = (
    "CO2",
    "MEA",
    "H2O",
    "MEAH+",
    "MEACOO-",
    "HCO3-",
    "CO3^2-",
    "H3O+",
    "OH-",
)

ADVANCED_BORN_USER_OPTIONS = {
    "elec_model": {
        "rel_perm": {
            "rule": "empirical",
            "differential_mode": "numerical",
        },
        "born_model": {
            "d_Born_mode": 3,
            "solvation_shell_model": True,
            "dielectric_saturation": True,
            "mu_born_model": {
                "differential_mode": "numerical",
                "comp_dep_delta_d": True,
            },
        },
    },
}


def load_epcsaft():
    """Import the sibling ePC-SAFT package with a clear setup failure."""
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
                    "Unable to import the sibling ePC-SAFT package. Build/install it first, "
                    "for example from C:\\Users\\Tanner\\Documents\\git\\ePC-SAFT with "
                    "`uv sync --no-install-project` and `uv run python scripts\\build_epcsaft.py`, "
                    "then run this repository with `uv sync` and `uv run python scripts\\validate_project.py quick`."
                ) from second_exc
        raise RuntimeError("Unable to import epcsaft and the sibling source checkout was not found.") from first_exc


def dataset_label() -> str:
    return str(DATASET_DIR)


def output_dir(*parts: str) -> Path:
    path = EPCSAFT_OUT_DIR.joinpath(*parts)
    path.mkdir(parents=True, exist_ok=True)
    return path


def diagnostic_composition(
    loading: float = 0.30,
    mea_weight_fraction: float = 0.30,
) -> np.ndarray:
    """Return a charge-balanced true-species estimate for package diagnostics.

    This is a deterministic diagnostic seed, not a fitted chemical-equilibrium
    model. Regression and full reactive-equilibrium coupling are intentionally
    kept out of this workflow.
    """
    if loading <= 0:
        raise ValueError("CO2 loading must be positive for the diagnostic state.")
    if not 0 < mea_weight_fraction < 1:
        raise ValueError("MEA weight fraction must be between zero and one.")

    n_mea_total = mea_weight_fraction / 0.06108
    n_h2o_total = (1.0 - mea_weight_fraction) / 0.01801528
    n_co2_total = loading * n_mea_total

    n_meacoo = min(0.45 * n_co2_total, 0.40 * n_mea_total)
    n_hco3 = min(0.35 * n_co2_total, 0.08 * n_h2o_total)
    n_co3 = min(0.01 * n_co2_total, 0.005 * n_h2o_total)
    n_h3o = 1.0e-10
    n_oh = 1.0e-10
    n_meah = n_meacoo + n_hco3 + 2.0 * n_co3 + n_oh - n_h3o

    if n_meah + n_meacoo >= 0.95 * n_mea_total:
        scale = 0.95 * n_mea_total / (n_meah + n_meacoo)
        n_meacoo *= scale
        n_hco3 *= scale
        n_co3 *= scale
        n_meah = n_meacoo + n_hco3 + 2.0 * n_co3 + n_oh - n_h3o

    n_co2 = max(n_co2_total - n_meacoo - n_hco3 - n_co3, 1.0e-12)
    n_mea = max(n_mea_total - n_meah - n_meacoo, 1.0e-12)
    n_h2o = max(n_h2o_total - n_hco3 - n_co3 - n_h3o - n_oh, 1.0e-12)

    amounts = np.array([n_co2, n_mea, n_h2o, n_meah, n_meacoo, n_hco3, n_co3, n_h3o, n_oh], dtype=float)
    return amounts / float(np.sum(amounts))


def build_mixture(T: float, x: np.ndarray):
    epcsaft = load_epcsaft()
    return epcsaft.ePCSAFTMixture.from_dataset(
        DATASET_DIR,
        SPECIES,
        np.asarray(x, dtype=float),
        float(T),
        user_options=ADVANCED_BORN_USER_OPTIONS,
    )


def is_finite_payload(value: Any) -> bool:
    if isinstance(value, dict):
        return all(is_finite_payload(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(is_finite_payload(item) for item in value)
    if isinstance(value, np.ndarray):
        return bool(np.all(np.isfinite(value)))
    if isinstance(value, (int, float, np.integer, np.floating)):
        return math.isfinite(float(value))
    return True


def to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return [to_jsonable(item) for item in value.tolist()]
    if isinstance(value, (np.integer, np.floating)):
        return float(value)
    return value


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_jsonable(payload), indent=2) + "\n", encoding="utf-8")
    return path
