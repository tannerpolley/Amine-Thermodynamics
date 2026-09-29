"""Baygi and Pahlavanzadeh 2015 CO2 partial-pressure model.

Ideal Smith-Missen chemistry (activity = mole fraction, Table 4 constants; the repo's
`MEA.smith_missen.ideal_speciation` solver) gives the true liquid composition. The molecular species
(CO2, MEA, H2O) are equilibrated with the vapour by PC-SAFT (Fig. 1 of the paper);
ions never enter the EOS (their moles are lumped with water, see `liquid_molecular_fractions`). p_CO2 = P_bubble * y_CO2.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np
import pandas as pd
from pcsaft import flashTQ, pcsaft_den, pcsaft_fugcoef
from scipy.optimize import brentq

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = ANALYSIS_DIR.parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
from MEA.smith_missen.ideal_speciation import SPECIES_INDEX, solve_ideal_speciation  # noqa: E402

TABLE2 = pd.read_csv(ANALYSIS_DIR / "data" / "processed" / "baygi_table2_pure_parameters.csv")
K_MEA_H2O = -0.0520  # Baygi Table 3, MEA 3B + H2O 4C; CO2-H2O and CO2-MEA are 0 (section 3.3)


def _row(species: str, scheme: str) -> pd.Series:
    return TABLE2[(TABLE2.species == species) & (TABLE2.association_scheme == scheme)].iloc[0]


def pcsaft_params(mea_scheme: str = "3B", water_scheme: str = "4C", k_mea_h2o: float = K_MEA_H2O) -> dict:
    """PC-SAFT parameters ordered CO2, MEA, H2O from Table 2."""
    rows = [_row("CO2", "nonassociating"), _row("MEA", mea_scheme), _row("H2O", water_scheme)]
    k = np.zeros((3, 3))
    k[1, 2] = k[2, 1] = k_mea_h2o
    return {
        "m": np.array([r.m for r in rows]),
        "s": np.array([r.sigma_A for r in rows]),
        "e": np.array([r.epsilon_K for r in rows]),
        "vol_a": np.nan_to_num(np.array([r.kappa_AB for r in rows], dtype=float)),
        "e_assoc": np.nan_to_num(np.array([r.epsilon_AB_K for r in rows], dtype=float)),
        "assoc_scheme": [None, mea_scheme.lower(), water_scheme.lower()],
        "k_ij": k,
    }


PARAMS = pcsaft_params()


def liquid_molecular_fractions(x9: np.ndarray, ions: str = "water") -> np.ndarray:
    """Pseudo-ternary CO2, MEA, H2O liquid for the PC-SAFT step. The paper's Fig. 1 keeps ions out of the EOS
    but does not say what becomes of their moles:
    ions="water": molecular CO2 and MEA moles kept, ions lumped with water (Nasrifar and Tafazzol 2010, the
        cited source of the a_i = x_i assumption, section "effective water mole fraction");
    ions="drop": ions removed and the three molecules renormalised."""
    x = np.array([x9[SPECIES_INDEX[s]] for s in ("CO2", "MEA", "H2O")])
    if ions == "water":
        return np.array([x[0], x[1], 1.0 - x[0] - x[1]])
    return x / x.sum()


def _ln_sum_kx(ln_p: float, T: float, x: np.ndarray, params: dict) -> float:
    """ln(sum x_i K_i) at pressure exp(ln_p), with the vapour composition converged by successive substitution."""
    p = np.exp(ln_p)
    y = np.array([0.9, 1e-3, 0.099])
    for _ in range(200):
        k = np.exp(
            np.log(pcsaft_fugcoef(T, pcsaft_den(T, p, x, params, phase="liq"), x, params))
            - np.log(pcsaft_fugcoef(T, pcsaft_den(T, p, y, params, phase="vap"), y, params))
        )
        total = float(np.sum(x * k))
        y_new = x * k / total
        done = np.max(np.abs(y_new - y)) < 1e-12
        y = y_new
        if done:
            break
    return np.log(total), y


def bubble_pressure(T: float, x: np.ndarray, params: dict = PARAMS) -> tuple[float, np.ndarray]:
    """Bubble pressure (Pa) and vapour mole fractions. flashTQ first; it fails above a few MPa, so fall back to
    a pressure scan for the first + to - crossing of ln(sum x K), then brentq."""
    try:
        p, _, y = flashTQ(T, 0, x, params=params)
        return float(p), np.asarray(y)
    except Exception:  # pcsaft raises SolutionError
        pass
    grid = np.log(np.logspace(3, 8, 26))
    previous = grid[0]
    for ln_p in grid[1:]:
        if _ln_sum_kx(ln_p, T, x, params)[0] < 0.0:
            root = brentq(lambda v: _ln_sum_kx(v, T, x, params)[0], previous, ln_p, xtol=1e-10)
            return float(np.exp(root)), _ln_sum_kx(root, T, x, params)[1]
        previous = ln_p
    raise RuntimeError(f"no bubble pressure below 100 MPa at T={T}, x={x}")


def baygi_pco2_kpa(
    loading: float, temperature_K: float, mea_weight_fraction: float = 0.3, params: dict = PARAMS, ions: str = "water"
) -> float:
    x9 = solve_ideal_speciation(loading, mea_weight_fraction, temperature_K).mole_fractions
    p_total, y = bubble_pressure(temperature_K, liquid_molecular_fractions(x9, ions), params)
    return float(p_total * y[0] / 1000.0)
