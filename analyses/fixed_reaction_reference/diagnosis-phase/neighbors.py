"""Use a solved neighboring bubble as the full start along T and conserved-feed coordinates."""

from pressure import c, HERE
from phases import dilute_vapor_connection
from time import monotonic
from copy import copy
from multiprocessing import Pool
import numpy as np
import sys


def one(key):
    tick = monotonic()
    spec = c.c.at(c.c.vector(55))

    def problem(i):
        p = copy(spec.problems[c.STATES[i]["problem"]])
        p.feed = copy(p.feed)
        p.phases = [copy(ph) for ph in p.phases]
        return p

    target = problem(key)
    sources = [
        c.c.r.read(f)
        for f in (HERE / "pressure-rows").glob("55-*.gz")
        if "bubble_Pa" in c.c.r.read(f)["trace"][-1]
    ]

    def distance(q):
        p = problem(q["row"])
        return (
            abs(np.log(p.feed.values["water"] / target.feed.values["water"])) * 5
            + abs(p.T - target.T) / 40
            + abs(q["loading"] - target.feed.values["carbon-dioxide"])
        )

    seed = min(sources, key=distance)
    p = problem(seed["row"])
    T0 = p.T
    feed = dict(p.feed.values)
    p.phases[1].amount = c.eq.Free()
    s = None
    trace = []
    for q in seed["trace"]:
        if "bubble" in q:
            p.P = q["P"]
            s = c.eq.solve_equilibrium(spec.model, p, s)
            if not s.success:
                break
    if s and s.success:
        for j, ph in enumerate(p.phases):
            x = s.phase_mole_fractions(j)
            ph.composition_guess = {
                k: x[spec.parameters.component_ids.index(k)] for k in ph.support
            }
            ph.packing_guess = s.packing_fractions[j]
        p.phases[1].amount = c.eq.Pinned(0.0)
        p.P = c.eq.Free(s.pressure)
        s = c.eq.solve_equilibrium(spec.model, p)
        if s.success:
            for t in np.linspace(0, 1, 21):
                p.T = (1 - t) * T0 + t * target.T
                p.feed.values = {
                    k: (1 - t) * v + t * target.feed.values.get(k, 0.0)
                    for k, v in feed.items()
                }
                b = c.eq.solve_equilibrium(spec.model, p, s)
                trace.append(
                    dict(t=t, message=b.message, P=b.pressure if b.success else None)
                )
                if (
                    "--dense" in sys.argv
                    and not b.success
                    and "vapor branch not admitted" in b.message
                ):
                    p.phases[1].kind = "liquid"
                    b = c.eq.solve_equilibrium(spec.model, p, s)
                    trace.append(
                        dict(
                            t=t, message=b.message, P=b.pressure if b.success else None
                        )
                    )
                trace[-1]["kind"] = p.phases[1].kind
                if not b.success or not b.requested_tolerance_met:
                    break
                s = b
                if t == 1:
                    trace[-1].update(
                        densities=list(b.molar_densities),
                        amounts=list(b.amounts),
                        connected=dilute_vapor_connection(
                            spec.model,
                            p.T,
                            b.phase_mole_fractions(1),
                            b.molar_densities[1],
                        )[1],
                    )
    result = dict(
        row=key,
        draw=55,
        source_row=seed["row"],
        source_message=s.message if s else None,
        trace=trace,
        seconds=monotonic() - tick,
    )
    c.c.refit.save(
        HERE
        / ("dense-rows" if "--dense" in sys.argv else "neighbor-rows")
        / f"55-{key}.json.gz",
        result,
    )


if __name__ == "__main__":
    tick = monotonic()
    keys = [
        r["row"]
        for p in (HERE / "fraction-rows").glob("*.gz")
        if (r := c.c.r.read(p))["trace"][-1].get("fraction") != 0
    ]
    assert len(keys) == 12
    with Pool(4) as pool:
        pool.map(one, keys, chunksize=1)
    print(monotonic() - tick)
