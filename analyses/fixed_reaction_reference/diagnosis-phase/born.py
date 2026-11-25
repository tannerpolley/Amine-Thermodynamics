"""Continue the AMP stationary pair between the two fixed-pressure Gibbs functions."""

# ruff: noqa: E402
from closure import HERE, c
from scipy.optimize import root
from time import monotonic
import os
import sys
import numpy as np

folder = c.r.ROOT / "analyses/mea_parameter_bundle/results/split-diagnosis-433"
sys.path.insert(0, str(folder))
os.environ["EPCA_WHEEL_433"] = str(c.r.WHEEL)
from decompose import off, contribution
from part_ii import Route
from verify import AMP, AMP_RECORD


def run(direct=False):
    t = monotonic()
    a = c.r.read(AMP_RECORD)
    route = Route(
        AMP / "inputs/retransfer-344/phase-2/AMP-05e94210.json",
        c.refit.WORK / "born-probe",
    )
    point = c.r.read(AMP / "results/retransfer-412-f2-05e94210/main/parameters.json")
    models = [route.bind(p) for p in (point, off(point))]
    standards = np.array(
        [a["standard_over_rt"], c.r.read(folder / "born-off.json")["standard"]]
    )
    T, P = a["T_K"], a["P_Pa"]
    form = [
        models[0].spec["element_formulas"][k]
        for k in models[0].parameters.component_ids
    ]
    M = np.array([[f.get(k, 0) for f in form] for k in "CNO"])
    z = np.array([f["charge"] for f in form])
    target = M @ a["feed_mol"]
    nu = np.array([r["stoichiometry"] for r in a["declaration"]["reactions"]])
    keep = [0, 1, 4, 5, 6, 7, 8]

    def encode(ph):
        x = np.array(ph["x"])
        return np.r_[np.log(x[keep] / x[2]), np.log(ph["amount_mol"])]

    def phases(vars, weight):
        ans = []
        for v in vars.reshape(2, 8):
            x = np.ones(9)
            x[keep] = np.exp(v[:-1])
            x[3] = -z[keep] @ x[keep]
            x /= x.sum()
            states = [m.model.state(T, P=P, x=x, phase="liquid") for m in models]
            mu = sum(
                w
                * (
                    np.log(x * s.molar_density)
                    + s.residual_chemical_potential_over_rt
                    + b
                )
                for w, s, b in zip((1 - weight, weight), states, standards)
            )
            ans.append((x, np.exp(v[-1]), mu, states))
        return ans

    def residual(v, w):
        ph = phases(v, w)
        return np.r_[
            (M @ sum(n * x for x, n, _, _ in ph) - target) / target,
            nu @ ph[0][2],
            nu @ ph[1][2],
            (ph[0][2] - ph[1][2])[:3],
        ]

    v = np.concatenate([encode(ph) for ph in a["phases"][1:]])
    out = []
    for weight in [1.0] * 6 if direct else np.linspace(0, 1, 51):
        if direct:
            v = np.concatenate([encode(ph) for ph in a["phases"][1:]])
            # Increase the archived contrast in neutral log composition and change
            # the initial partition while keeping both phase amounts positive.
            gain, mol = [(1, 4), (1.5, 3), (2, 2), (3, 1), (0.5, 5), (4, 0.5)][len(out)]
            diff = (v[:7] - v[8:15]) * (gain - 1) / 2
            v[:7] += diff
            v[8:15] -= diff
            total = np.exp(v[7]) + np.exp(v[-1])
            v[7], v[-1] = np.log([mol, total - mol])
        tick = monotonic()
        try:
            sol = root(
                residual, v, args=(weight,), options=dict(xtol=1e-11, maxfev=320)
            )
            err = max(abs(residual(sol.x, weight)))
            ph = phases(sol.x, weight)
            record = dict(
                w=weight,
                max_residual=err,
                termination=sol.message,
                nfev=sol.nfev,
                phases=[
                    dict(
                        x=x,
                        n=n,
                        rho=s[-1].molar_density,
                        branch=s[-1].returned_density_branch.name,
                        P_error=s[-1].pressure - P,
                        mu=mu,
                    )
                    for x, n, mu, s in ph
                ],
            )
            if weight == 1:
                record["G_over_RT"] = sum(
                    n * sum(contribution(s[-1], T, P, x, standards[1]))
                    for x, n, _, s in ph
                )
            v = sol.x
        except (ValueError, RuntimeError) as e:
            err = np.inf
            record = dict(w=weight, error=str(e))
        out.append(dict(record, seconds=monotonic() - tick))
        if not direct and err > 1e-10:
            break
    c.refit.save(
        HERE / ("born-direct.json.gz" if direct else "born.json.gz"),
        dict(wheel=c.r.SHA, rows=out, seconds=monotonic() - t),
    )


if __name__ == "__main__":
    run("--direct" in sys.argv)
