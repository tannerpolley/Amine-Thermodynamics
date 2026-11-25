"""Trace density on the actual incipient composition at each recovered Kuranov bubble."""

from pressure import HERE, c
from phases import dilute_vapor_connection
from time import monotonic
from copy import copy
from multiprocessing import Pool


def one(case):
    tick = monotonic()
    spec = c.c.at(c.c.vector(case["draw"]))
    p = copy(spec.problems[c.STATES[case["row"]]["problem"]])
    p.phases = [copy(ph) for ph in p.phases]
    p.phases[1].amount = c.eq.Free()
    s = None
    for q in case["trace"]:
        if "bubble" in q:
            p.P = q["P"]
            s = c.eq.solve_equilibrium(spec.model, p, s)
            assert s.success and s.requested_tolerance_met
    for j, ph in enumerate(p.phases):
        x = s.phase_mole_fractions(j)
        ph.composition_guess = {
            k: x[spec.parameters.component_ids.index(k)] for k in ph.support
        }
        ph.packing_guess = s.packing_fractions[j]
    p.phases[1].amount = c.eq.Pinned(0.0)
    p.P = c.eq.Free(s.pressure)
    b = c.eq.solve_equilibrium(spec.model, p)
    assert b.success and b.requested_tolerance_met
    x = b.phase_mole_fractions(1)
    return dict(
        draw=case["draw"],
        row=case["row"],
        P=b.pressure,
        amounts=list(b.amounts),
        x=x,
        densities=list(b.molar_densities),
        path=dilute_vapor_connection(spec.model, p.T, x, b.molar_densities[1]),
        seconds=monotonic() - tick,
    )


if __name__ == "__main__":
    tick = monotonic()
    cases = [c.c.r.read(p) for p in (HERE / "pressure-rows").glob("*.gz")]
    with Pool(4) as pool:
        rows = pool.map(
            one, [q for q in cases if "bubble_Pa" in q["trace"][-1]], chunksize=1
        )
    c.c.refit.save(
        HERE / "roots.json.gz",
        dict(wheel=c.c.r.SHA, rows=rows, seconds=monotonic() - tick),
    )
