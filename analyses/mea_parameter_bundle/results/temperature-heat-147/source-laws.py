"""Issue 147 S1: one source-only representation solve per admitted R4/R5 law.

Run from this checkout: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
MKL_NUM_THREADS=1 timeout 60s uv run --no-project --with numpy==2.5.1
python analyses/mea_parameter_bundle/results/temperature-heat-147/source-laws.py
No Engine import, equilibrium calculation, or loaded-data fitting.
"""
import ast
import csv
import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
DATA = ROOT / "data/reference/MEA"
TREF, R = 313.15, 8.31446261815324


def table(name, rows):
    with (OUT / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def coefficients(beta):
    l0, b, c, d = map(float, beta)
    a = l0 - b / TREF - c * np.log(TREF) - d * TREF
    return dict(L0=l0, A=float(a), B_K=b, C=c, D_per_K=d,
                a_native=float(a + c * np.log(TREF)), Tref_K=TREF)


def basis(t):
    return np.array([np.ones_like(t), 1 / t - 1 / TREF,
                     np.log(t / TREF), t - TREF]).T


def solve(x, y):
    norms = np.linalg.norm(x, axis=0)
    beta, _, rank, singular = np.linalg.lstsq(x / norms, y, rcond=None)
    assert rank == x.shape[1]
    return beta / norms, dict(rank=int(rank), singular_values=singular.tolist(), column_norms=norms.tolist())


krows = list(csv.DictReader((DATA / "observations/reaction_constants/Kim_2011_MEA_dissociation_constants.csv").open()))
hrows = list(csv.DictReader((DATA / "observations/calorimetry/Kim_2011_MEA_protonation_enthalpy.csv").open()))
kt = np.array([float(row["temperature_K"]) for row in krows])
ht = np.array([float(row["temperature_K"]) for row in hrows])
ky = np.array([float(row["ln_Ka"]) for row in krows])
hy = 1000 * np.array([float(row["enthalpy_protonation_reported_kJ_per_mol"]) for row in hrows])
ks, hs = np.full(7, np.log(10) * 0.02), 0.025 * hy
x = np.vstack([basis(kt)[:, [0, 2, 3]] / ks[:, None],
               np.array([np.zeros(6), R * ht, R * ht**2]).T / hs[:, None]])
y = np.concatenate([ky / ks, hy / hs])
beta, info = solve(x, y)
r5 = coefficients([beta[0], 0, beta[1], beta[2]])
residuals = x @ beta - y
r5.update(info, passed=bool(np.max(abs(residuals)) <= 2), source_fit_count=1,
          scaled_RMS_lnK=float(np.sqrt(np.mean(residuals[:7]**2))),
          scaled_RMS_heat=float(np.sqrt(np.mean(residuals[7:]**2))))
rows = []
for i, row in enumerate(krows + hrows):
    scale = float(np.concatenate([ks, hs])[i])
    rows.append(dict(source_row=row["source_row"], family="lnK" if i < 7 else "dissociation_heat",
                     T_K=float(row["temperature_K"]), observed=float(np.concatenate([ky, hy])[i]),
                     unit="dimensionless" if i < 7 else "J/mol", scale=scale, weight=1,
                     calculated=float((x @ beta)[i] * scale), raw_residual=float(residuals[i] * scale),
                     scaled_residual=float(residuals[i])))
table("r5-residuals.csv", rows)
# Reuse only the existing source-density function, without importing its Engine callers.
density_file = ROOT / "analyses/mea_parameter_bundle/scripts/verify_temperature_reference.py"
node = next(n for n in ast.parse(density_file.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "water_reference")
namespace = {"math": np}
exec(compile(ast.Module(body=[node], type_ignores=[]), str(density_file), "exec"), namespace)
water = namespace["water_reference"]


def r4_source(t):
    q = water(t)[1] * 0.01801528 / 1000
    dq = water(t + 1e-20j)[1].imag * 0.01801528 / 1000 / 1e-20
    return -np.log(10) * (-0.934 + 671 / t) - np.log(q), R * (np.log(10) * 671 - t**2 * dq / q)


grid = 298 + 5 * np.arange(7, dtype=float)
beta4, info4 = solve(basis(grid), np.array([r4_source(t)[0] for t in grid]))
r4 = coefficients(beta4)
r4.update(info4, temperature_samples_K=grid.tolist(), source_fit_count=1)
old = json.loads((ROOT / "analyses/mea_parameter_bundle/results/temperature-reanchor-140/stage-3/source-fit.json").read_text())
r2 = old["coefficients"]
checks = []
check_grid = list(293.15 + np.arange(61))
wagner = list(csv.DictReader((DATA / "observations/vapor_liquid_equilibrium/Wagner_2013_VLE.csv").open()))
diagnostic = sorted({293.15, 313.15, 322.5, 333.15, 353.15, 372.9, 373.15, 393.15} | {float(r["temperature_reported"]) for r in wagner if 293.15 <= float(r["temperature_reported"]) <= 393.15})
for t in sorted(set(check_grid + list(grid) + diagnostic)):
    for law in ["R4", "R2"]:
        if law == "R4":
            lk, heat = r4_source(t)
            represented = float((basis(np.array([t])) @ beta4)[0])
            represented_heat = R * (-r4["B_K"] + r4["C"] * t + r4["D_per_K"] * t**2)
        else:
            lk = np.log(10) * (-356.3094 - 0.06091964 * t + 21834.37 / t + 126.8339 * np.log10(t) - 1684915 / t**2)
            heat = R * np.log(10) * (-0.06091964 * t**2 - 21834.37 + 126.8339 * t / np.log(10) + 2 * 1684915 / t)
            represented = r2["A_stored"] + r2["B_K"] / t + r2["C"] * np.log(t) + r2["D_per_K"] * t
            represented_heat = R * (-r2["B_K"] + r2["C"] * t + r2["D_per_K"] * t**2)
        checks.append(dict(law=law, T_K=float(t), in_admission_interval=293.15 <= t <= 353.15,
                           diagnostic_temperature=t in diagnostic, source_lnK=float(lk), represented_lnK=float(represented),
                           lnK_error=float(represented - lk), source_heat_kJ_mol=float(heat / 1000),
                           represented_heat_kJ_mol=float(represented_heat / 1000), heat_error_kJ_mol=float((represented_heat - heat) / 1000)))
table("representation-errors.csv", checks)
for law, record in [("R4", r4), ("R2", r2)]:
    admitted = [row for row in checks if row["law"] == law and row["in_admission_interval"]]
    record.update(max_lnK_error=max(abs(row["lnK_error"]) for row in admitted),
                  max_heat_error_kJ_mol=max(abs(row["heat_error_kJ_mol"]) for row in admitted))
    record["passed"] = record["max_lnK_error"] <= 0.002 and record["max_heat_error_kJ_mol"] <= 0.15
assert all(record["passed"] for record in [r2, r4, r5])
(OUT / "source-laws.json").write_text(json.dumps(
    dict(R2_reused=r2, R4=r4, R5=r5, gas_constant_J_mol_K=R,
         diagnostic_temperatures_K=diagnostic), indent=2, allow_nan=False) + "\n")
