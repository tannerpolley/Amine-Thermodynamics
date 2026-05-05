from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


ANALYSIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = ANALYSIS_DIR.parents[1]
OUT_DIR = ANALYSIS_DIR / "out"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from MEA.epcsaft_neutral.plot_pressure import compute_neutral_parity  # noqa: E402


PURE_PARAMETER_ROWS = [
    {"species": "MEA", "association_scheme": "4C", "m": 4.5208, "sigma_A": 2.6574, "epsilon_K": 237.6864, "kappa_AB": 0.187533, "epsilon_AB_K": 989.8984, "AAD_percent_psat": 0.24, "AAD_percent_rhoL": 0.23, "reference": "Baygi 2015 Table 2"},
    {"species": "MEA", "association_scheme": "3B", "m": 4.5354, "sigma_A": 2.6019, "epsilon_K": 204.0438, "kappa_AB": 0.118488, "epsilon_AB_K": 2383.4744, "AAD_percent_psat": 1.75, "AAD_percent_rhoL": 0.43, "reference": "Baygi 2015 Table 2"},
    {"species": "MEA", "association_scheme": "2B", "m": 3.0353, "sigma_A": 3.0435, "epsilon_K": 277.174, "kappa_AB": 0.037470, "epsilon_AB_K": 2586.3, "AAD_percent_psat": 0.62, "AAD_percent_rhoL": 0.12, "reference": "Baygi 2015 Table 2"},
    {"species": "H2O", "association_scheme": "2B", "m": 1.9599, "sigma_A": 2.362, "epsilon_K": 279.42, "kappa_AB": 0.1750, "epsilon_AB_K": 2059.28, "AAD_percent_psat": 1.18, "AAD_percent_rhoL": 3.92, "reference": "Diamantonis and Economou 2011"},
    {"species": "H2O", "association_scheme": "4C", "m": 2.1945, "sigma_A": 2.229, "epsilon_K": 141.66, "kappa_AB": 0.2039, "epsilon_AB_K": 1804.17, "AAD_percent_psat": 1.98, "AAD_percent_rhoL": 0.83, "reference": "Diamantonis and Economou 2011"},
    {"species": "CO2", "association_scheme": "nonassociating", "m": 2.0729, "sigma_A": 2.7852, "epsilon_K": 169.21, "kappa_AB": None, "epsilon_AB_K": None, "AAD_percent_psat": 2.78, "AAD_percent_rhoL": 2.73, "reference": "Gross and Sadowski 2001"},
]

BINARY_ASSOCIATION_ROWS = [
    {"MEA_scheme": "2B", "H2O_scheme": "2B", "AAD_percent_x_MEA": 5.66, "AAD_percent_y_MEA": 2.38, "k_ij": -0.0420},
    {"MEA_scheme": "3B", "H2O_scheme": "2B", "AAD_percent_x_MEA": 4.24, "AAD_percent_y_MEA": 2.08, "k_ij": -0.0146},
    {"MEA_scheme": "4C", "H2O_scheme": "2B", "AAD_percent_x_MEA": 5.41, "AAD_percent_y_MEA": 2.28, "k_ij": -0.0362},
    {"MEA_scheme": "2B", "H2O_scheme": "4C", "AAD_percent_x_MEA": 3.52, "AAD_percent_y_MEA": 8.63, "k_ij": -0.1305},
    {"MEA_scheme": "3B", "H2O_scheme": "4C", "AAD_percent_x_MEA": 3.54, "AAD_percent_y_MEA": 1.54, "k_ij": -0.0520},
    {"MEA_scheme": "4C", "H2O_scheme": "4C", "AAD_percent_x_MEA": 8.05, "AAD_percent_y_MEA": 3.60, "k_ij": -0.1245},
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pure_path = OUT_DIR / "baygi_table2_pure_parameters.csv"
    binary_path = OUT_DIR / "baygi_table3_mea_h2o_association_comparison.csv"
    pressure_path = OUT_DIR / "baygi_neutral_epcsaft_pcsaft_pressure_parity_raw.csv"
    summary_path = OUT_DIR / "baygi_neutral_epcsaft_pcsaft_pressure_parity_summary.csv"

    pd.DataFrame(PURE_PARAMETER_ROWS).to_csv(pure_path, index=False)
    pd.DataFrame(BINARY_ASSOCIATION_ROWS).to_csv(binary_path, index=False)
    _, summary, curves = compute_neutral_parity()
    curves.to_csv(pressure_path, index=False)
    summary.to_csv(summary_path, index=False)

    print(f"Baygi pure parameters: {pure_path}")
    print(f"Baygi MEA-H2O association comparison: {binary_path}")
    print(f"Neutral ePC-SAFT pressure parity raw data: {pressure_path}")
    print(f"Neutral ePC-SAFT pressure parity summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

