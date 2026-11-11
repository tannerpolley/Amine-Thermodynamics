"""Bounded checks of the stage-3 misfit without changing the model or data roles."""

import json
import numpy as np
from epcsaft import regression as reg
from fit_speciation import declarations
from run import AN, write_csv
from speciation import save


def calculate():
    p, c, o, C, u, metadata = declarations()
    f = json.loads((AN / "results/nmr-fit.json").read_text())
    x = np.array(f["optimizer"])
    base = reg.differentiate(p, c, o, optimizer=x.tolist())
    start = reg.differentiate(p, c, o, optimizer=[0.0, 0.0, 0.0])
    _, _, refined_obs, _, _, _ = declarations(tolerance=1e-12)
    refined = reg.differentiate(p, c, refined_obs, optimizer=x.tolist())
    pred = np.array(base.predictions)
    initial = np.array(start.predictions)
    L = np.linalg.cholesky(C)
    target = np.array([r["observed_fraction"] for r in metadata])
    z = np.linalg.solve(L, pred - target)
    # Native exact columns versus central differences in the weakest scaled direction.
    J = np.array(base.residual_optimizer_gradient).reshape(len(o), 3)
    v = np.array(f["endpoint_information"]["right_vectors"][-1])
    checks = []
    for h in [1e-3, 1e-4]:
        plus = reg.differentiate(p, c, o, optimizer=(x + h * v).tolist())
        minus = reg.differentiate(p, c, o, optimizer=(x - h * v).tolist())
        fd = (np.array(plus.predictions) - np.array(minus.predictions)) / (2 * h)
        checks.append(
            dict(
                step=h,
                relative_column_error=float(
                    np.linalg.norm(np.linalg.solve(L, fd - J @ v))
                    / np.linalg.norm(np.linalg.solve(L, J @ v))
                ),
            )
        )
    output = []
    for i, (r, y, yi, zi) in enumerate(zip(metadata, pred, initial, z, strict=True)):
        n = float(r["pz_mol"])
        obs = r["observed_fraction"]
        output.append(
            dict(
                r,
                calculated_fraction=y,
                initial_fraction=yi,
                calculated_mol=y * n,
                difference_mol=(y - obs) * n,
                initial_difference_mol=(yi - obs) * n,
                marginal_scale_mol=np.sqrt(C[i, i]) * n,
                residual_marginal=(y - obs) / np.sqrt(C[i, i]),
                whitened_residual=zi,
                q039_whitened_residual=zi * 0.02 / 0.039,
                refinement_mol=(refined.predictions[i] - y) * n,
            )
        )
    write_csv("nmr-residuals.csv", output)
    summary = []
    for T in [283.15, 298.15, 313.15, 333.15]:
        for g in [1, 2]:
            data = [r for r in output if float(r["T_K"]) == T and r["group"] == g]
            summary.append(
                dict(
                    T_K=T,
                    group=g,
                    count=len(data),
                    bias_mol=float(np.mean([r["difference_mol"] for r in data])),
                    rms_mol=float(
                        np.sqrt(np.mean([r["difference_mol"] ** 2 for r in data]))
                    ),
                    marginal_RMS=float(
                        np.sqrt(np.mean([r["residual_marginal"] ** 2 for r in data]))
                    ),
                    max_abs_mol=max(abs(r["difference_mol"]) for r in data),
                )
            )
    write_csv("nmr-summary.csv", summary)
    save(
        "nmr-diagnosis.json",
        dict(
            weighted_RMS=float(np.linalg.norm(z) / np.sqrt(len(z))),
            cost=float(z @ z / 2),
            q039_weighted_RMS=float(np.linalg.norm(z) / np.sqrt(len(z)) * 0.02 / 0.039),
            q039_SE=(np.array(f["endpoint_information"]["se"]) * 0.039 / 0.02).tolist(),
            q039_endpoint="identical: uniform q rescaling multiplies entire objective by (.02/.039)^2",
            max_refinement_fraction=float(
                max(abs(np.array(refined.predictions) - pred))
            ),
            derivative_checks=checks,
            diagnosis="Interior identifiable three-offset conditional A fit leaves source-scale residuals. Source units, source-law reversal, normalized NMR groups and numerical refinement checked; no added coordinate or bound change authorized. EOS start-property hypotheses and fixed source-law slopes remain unresolved contributors; stage 4 has not been run.",
        ),
    )
    print(summary, flush=True)


if __name__ == "__main__":
    calculate()
