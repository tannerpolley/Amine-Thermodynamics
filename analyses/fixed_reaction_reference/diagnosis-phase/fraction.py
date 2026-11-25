"""Continue from the last positive TP solution in vapor fraction toward the bubble."""

from pressure import HERE, c
from phases import dilute_vapor_connection
from copy import copy
from time import monotonic
from multiprocessing import Pool
import sys


def one(path):
    case = c.c.r.read(path)
    t = monotonic()
    draw, i = case["draw"], case["row"]
    spec = c.c.at(c.c.vector(draw))
    p = copy(spec.problems[c.STATES[i]["problem"]])
    p.phases = [copy(q) for q in p.phases]
    p.phases[-1].amount = c.eq.Free()
    s = None
    trace = []
    for q in case["trace"]:
        if "bubble" not in q:
            continue
        p.P = q["P"]
        s = c.eq.solve_equilibrium(spec.model, p, s)
        trace.append(dict(P=p.P, message=s.message, amounts=list(s.amounts)))
        if not s.success or not s.requested_tolerance_met:
            s = None
            break
    if s is not None:
        frac = s.amounts[-1] / sum(p.feed.values.values())
        for f in (1.0, 0.98, 0.95, 0.90, 0.8, 0.65, 0.5, 0.3, 0.1, 0.03, 0.01, 0.0):
            p.phases[-1].amount = c.eq.Pinned(f * frac)
            p.P = c.eq.Free(s.pressure)
            for j, ph in enumerate(p.phases):
                x = s.phase_mole_fractions(j)
                ph.composition_guess = {
                    k: x[spec.parameters.component_ids.index(k)] for k in ph.support
                }
                ph.packing_guess = s.packing_fractions[j]
            sol = c.eq.solve_equilibrium(spec.model, p)
            trace.append(
                dict(
                    fraction=f * frac,
                    pressure=sol.pressure if sol.success else None,
                    amounts=list(sol.amounts),
                    densities=list(sol.molar_densities),
                    message=sol.message,
                )
            )
            trace[-1]["kind"] = p.phases[-1].kind
            if not sol.success and "vapor branch not admitted" in sol.message:
                # Same chemical support and seed; probe the other density branch.
                p.phases[-1].kind = "liquid"
                sol = c.eq.solve_equilibrium(spec.model, p)
                trace.append(
                    dict(
                        fraction=f * frac,
                        kind="liquid",
                        pressure=sol.pressure if sol.success else None,
                        amounts=list(sol.amounts),
                        densities=list(sol.molar_densities),
                        message=sol.message,
                    )
                )
            if not sol.success or not sol.requested_tolerance_met:
                break
            st = spec.model.state(
                p.T, rho=sol.molar_densities[1], x=sol.phase_mole_fractions(1)
            )
            trace[-1].update(
                x=sol.phase_mole_fractions(1),
                dPdrho=st.pressure_density_derivative,
                dilute_connected=dilute_vapor_connection(
                    spec.model, p.T, sol.phase_mole_fractions(1), sol.molar_densities[1]
                )[1],
            )
            s = sol
    row = dict(draw=draw, row=i, trace=trace, seconds=monotonic() - t)
    c.c.refit.save(HERE / "fraction-rows" / path.name, row)
    return row["seconds"]


if __name__ == "__main__":
    t = monotonic()
    paths = [
        p
        for p in sorted((HERE / "pressure-rows").glob("*.gz"))
        if not c.c.r.read(p)["trace"][-1].get("bubble_Pa")
    ]
    if "--pilot" in sys.argv:
        paths = [HERE / "pressure-rows/16-39.json.gz"]
    with Pool(1 if "--pilot" in sys.argv else 4) as pool:
        durations = pool.map(one, paths, chunksize=1)
    print(len(paths), monotonic() - t, sum(durations))
