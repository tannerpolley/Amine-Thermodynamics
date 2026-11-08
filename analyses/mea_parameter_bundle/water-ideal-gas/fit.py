"""Fit IAPWS-95 ideal-water Cp and anchor Shomate enthalpy and entropy."""
import csv
import json
from pathlib import Path

import numpy as np
from scipy.integrate import quad

OUT = Path(__file__).resolve().parent
R = 461.51805 * 0.018015268  # IAPWS R6-95(2018), section 3, J/(mol K)
N = np.array([0.012436, 0.97315, 1.27950, 0.96956, 0.24873])
GAMMA = np.array([1.28728967, 3.53734222, 7.74073708, 9.24437796, 27.5075105])
ANCHOR = 298.15


def cp(T):
    x = 647.096 / np.asarray(T)[..., None] * GAMMA
    return R * (1 + 3.00632 + np.sum(N * x*x * np.exp(-x) / (-np.expm1(-x))**2, axis=-1))


def basis(T):
    t = np.asarray(T) / 1000
    return np.stack([np.ones_like(t), t, t*t, t**3, 1/t**2], axis=-1)


def main():
    fit_grid = np.linspace(273.15, 400, 501)
    a = np.linalg.lstsq(basis(fit_grid), cp(fit_grid), rcond=None)[0]
    t = ANCHOR / 1000
    A, B, C, D, E = a
    H = -241.826
    F = H - (A*t + B*t*t/2 + C*t**3/3 + D*t**4/4 - E/t)
    G = 188.834 - (A*np.log(t) + B*t + C*t*t/2 + D*t**3/3 - E/(2*t*t))
    coefficients = [*map(float, a), float(F), float(G), H]
    grid = np.linspace(273.15, 400, 10001)
    rows = []
    for T in grid:
        t = T/1000
        h = -241826 + 1000*(A*t+B*t*t/2+C*t**3/3+D*t**4/4-E/t+F-H)
        s = A*np.log(t)+B*t+C*t*t/2+D*t**3/3-E/(2*t*t)+G
        href = -241826 + quad(cp, ANCHOR, T, epsabs=1e-9)[0]
        sref = 188.834 + quad(lambda x: cp(x)/x, ANCHOR, T, epsabs=1e-11)[0]
        ref = float(cp(T))
        rows.append((T, ref, float(basis(T) @ a), h-href, s-sref))
    with (OUT/'verification-grid.csv').open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['T_K','iapws_cp_J_mol_K','fit_cp_J_mol_K','h_error_J_mol','s_error_J_mol_K']); w.writerows(rows)
    with (OUT/'fit-grid.csv').open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['T_K','iapws_cp_J_mol_K','fit_cp_J_mol_K']); w.writerows(zip(fit_grid, cp(fit_grid), basis(fit_grid) @ a))
    errors = np.array(rows)
    result = dict(coefficients=coefficients, fit_range_K=[273.15,400.0], fit_points=len(fit_grid), verification_points=len(grid),
                  max_relative_cp_error=float(np.max(np.abs(errors[:,2]/errors[:,1]-1))),
                  max_abs_h_error_J_mol=float(np.max(np.abs(errors[:,3]))), max_abs_s_error_J_mol_K=float(np.max(np.abs(errors[:,4]))),
                  anchor_h_J_mol=-241826, anchor_s_J_mol_K=188.834, gas_constant_J_mol_K=R)
    assert result['max_relative_cp_error'] <= .001
    (OUT/'fit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
