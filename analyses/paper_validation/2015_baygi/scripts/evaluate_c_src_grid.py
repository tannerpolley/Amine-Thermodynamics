"""Evaluate refit C_src (variant source-R4-C-f66-v5) on a loading grid at 40 and 120 degC, for the curves in the
comparison figure. Single process, warm-started exactly as `calibration-misfit/probe.py` does; three canonical rows
are replayed as a check against the retained `refit-C-states.csv` predictions. Read-only on the refit record.

    OMP_NUM_THREADS=1 uv run python analyses/paper_validation/2015_baygi/scripts/evaluate_c_src_grid.py
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import pandas as pd

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = ANALYSIS_DIR.parents[2]
MISFIT = REPO_ROOT / "analyses" / "mea_parameter_bundle" / "calibration-misfit"
sys.path.insert(0, str(MISFIT))
import probe  # noqa: E402  (verifies the pinned Engine wheel)

OUT = ANALYSIS_DIR / "data" / "processed" / "ours_c_src_loading_grid.csv"
VARIANT = "source-R4-C-f66-v5"
TEMPERATURES_C = (40, 120)
LOADINGS = [round(0.05 + 0.025 * i, 3) for i in range(27)]  # 0.05 ... 0.70
REPLAY = ("vle_obs_0034", "vle_obs_0036", "vle_obs_0233")  # Aronu 40 C x2 and a Jou 120 C row

probe.RECORD = MISFIT / "refit-C-parameters.json"
grid_rows = ANALYSIS_DIR / "data" / "processed" / "_grid_rows.csv"


def main() -> int:
    with grid_rows.open("w", newline="", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=["observation_id", "source_key", "MEA_weight_fraction", "temperature_reported_C",
                                          "temperature_canonical_C", "CO2_loading", "CO2_pressure", "active_view_member"])
        w.writeheader()
        for t in TEMPERATURES_C:
            for a in LOADINGS:
                w.writerow({"observation_id": f"grid_{t}_{a}", "source_key": "grid", "MEA_weight_fraction": 0.3,
                            "temperature_reported_C": t, "temperature_canonical_C": t, "CO2_loading": a,
                            "CO2_pressure": 1.0, "active_view_member": "yes"})
    canonical_csv = probe.shared.CANONICAL_VLE
    probe.shared.CANONICAL_VLE = grid_rows
    states = probe.pressure_observations(lambda row: True)
    probe.shared.CANONICAL_VLE = canonical_csv
    states += [s for s in probe.CANONICAL if s["identity"].removeprefix("canonical:") in REPLAY]

    retained = pd.read_csv(MISFIT / "refit-C-states.csv")
    retained = retained[(retained.variant == VARIANT) & retained.identity.str.startswith("canonical:")].set_index("identity")
    rows = []
    for rec in probe.evaluate(dict(probe.SOURCE_R4), states=states):
        p_kpa = rec["predictions"]["co2-partial-pressure"] / 1000.0 if rec["status"] == "evaluated" else float("nan")
        ident = rec["identity"]
        if ident.startswith("canonical:vle_obs"):
            print(f"replay {ident}: now {p_kpa:.6g} kPa, retained {retained.loc[ident, 'predicted']:.6g} kPa", flush=True)
            continue
        rows.append({"variant": VARIANT, "temperature_C": round(rec["T"] - 273.15), "CO2_loading": rec["feed"][0],
                     "pCO2_kPa": p_kpa, "status": rec["status"], "wall_s": round(rec["wall_s"], 2),
                     "engine_wheel_sha256": rec["wheel"], "record_sha256": rec["record_sha256"]})
        print(rows[-1], flush=True)
        pd.DataFrame(rows).to_csv(OUT, index=False, float_format="%.8g")
    grid_rows.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
