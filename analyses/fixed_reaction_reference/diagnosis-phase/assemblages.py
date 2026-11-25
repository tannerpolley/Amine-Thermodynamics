"""Rebuild the target phase declarations, keeping the external T, P and feed fixed."""

from closure import HERE, c, cd, physical, point_for, pressure_reclosure
from phases import dilute_vapor_connection
from time import monotonic
from copy import copy


def vapor():
    old = c.r.read(c.r.ROOT / "analyses/round_9/results/mdea-phase-controls.json.gz")[
        "value"
    ]
    for name in ["salt-anchored", "MEA-fitted"]:
        route, point = point_for("MDEA", "selected", "vapor-readback")
        if name == "MEA-fitted":
            point = c.r.read(
                c.r.ROOT / "analyses/round_9/results/MDEA-shared-fit.json.gz"
            )["endpoint"]
        spec = route.bind(point)
        template = spec.problems[
            next(q["bubble"] for q in c.ROWS if q["group"] == "Merkley")
        ]
        for key, record in old.items():
            tick = monotonic()
            x = record["models"][name]
            p = copy(template)
            p.feed = copy(template.feed)
            p.feed.values = dict(zip(x["species"], x["feed_mol"]))
            p.T, p.P = x["T_K"], x["P_Pa"]
            p.phases = [copy(t) for t in p.phases]
            p.phases[1].amount = c.refit.eq.Free()
            a = x["attempts"][0]
            if a.get("phases"):
                for i, phase in enumerate(p.phases):
                    phase.composition_guess = {
                        s: a["phases"][i][x["species"].index(s)] for s in phase.support
                    }
                    phase.packing_guess = a["packings"][i]
            s = c.refit.eq.solve_equilibrium(spec.model, p)
            row = dict(
                key=key,
                model=name,
                message=s.message,
                amounts=list(s.amounts),
                tolerance=s.requested_tolerance_met,
            )
            if s.success and s.requested_tolerance_met and min(s.amounts) > 0:
                n = p._native(spec.parameters)
                row.update(physical(spec, n, s))
                g = cd.gibbs(c.refit.eq.compile_problem(spec.model, n), s)
                row["decrease"] = x["parent_gibbs_RT_mol"][0] - g[0]
                row["error"] = x["parent_gibbs_RT_mol"][1] + g[1]
                row["vapor_trace"] = dilute_vapor_connection(
                    spec.model, p.T, s.phase_mole_fractions(1), s.molar_densities[1]
                )
            yield dict(row, seconds=monotonic() - tick)


def dea():
    route, point = point_for("DEA", "selected", "pressure-readback")
    spec = route.bind(point)
    data = c.r.read(c.OUT / "DEA/screen/selected/declared/summary.json.gz")
    cases = {q["key"]: q for q in data["classifications"]}
    for key in ["weiland-1998:32:problem", "lawson-1976-viii:0:problem"]:
        start = (
            cases["weiland-1998:42:problem"]
            if "weiland" in key
            else cases["weiland-1998:32:problem"]
        )
        seed = next(a for a in start["attempts"] if a["confirmed"])
        p = route.stability_row(spec, dict(problem=key), 1.0).problem
        p.pressure = type(p.pressure).fixed(cases[key]["pressure_Pa"])
        liquid = p.phases
        phases = []
        for i, x in enumerate(seed["phases"]):
            z = type(liquid[0])()
            z.kind = liquid[0].kind
            z.name = f"L{i}"
            z.support = list(range(len(x)))
            z.support_declared = True
            z.composition_guess = x
            z.packing_guess = seed["packings"][i]
            phases.append(z)
        s = None
        steps = range(21) if "weiland" in key else [0]
        for i in steps:
            tick = monotonic()
            feed = p.feed
            values = list(feed.values)
            if "weiland" in key:
                values[0] = 0.5 - i * 0.0025
            feed.values = values
            p.feed = feed
            p.phases = liquid
            parent = c.refit.eq.solve_equilibrium(spec.model, p)
            g = cd.gibbs(c.refit.eq.compile_problem(spec.model, p), parent)
            p.phases = phases
            sol = c.refit.eq.solve_equilibrium(spec.model, p, s)
            row = dict(
                key=key, feed=values, message=sol.message, amounts=list(sol.amounts)
            )
            if sol.success and sol.requested_tolerance_met and min(sol.amounts) > 0:
                s = sol
                compiled = c.refit.eq.compile_problem(spec.model, p)
                split = cd.gibbs(compiled, s)
                row.update(
                    physical(spec, p, s),
                    decrease=g[0] - split[0],
                    error=g[1] + split[1],
                    roots=[],
                )
                b = c.refit.eq.stability_test(compiled, s).standard_over_rt
                for j, phase in enumerate(row["phases"]):
                    x, rho = phase["x"], phase["density_mol_m3"]
                    T, P = s.temperature, s.pressure
                    roots = cd.pressure_roots(spec.model, T, P, x, rho)
                    _, _, test = pressure_reclosure(
                        spec.model,
                        p,
                        T,
                        P,
                        rho,
                        x,
                        b,
                        spec.model.state(T, rho=rho, x=x),
                    )
                    row["roots"].append(dict(original=roots, reclosure=test))
            yield dict(row, seconds=monotonic() - tick)
            if s is not sol:
                break


if __name__ == "__main__":
    tick = monotonic()
    c.refit.save(
        HERE / "assemblages.json.gz",
        dict(
            wheel=c.r.SHA,
            dea=list(dea()),
            mdea=list(vapor()),
            seconds=monotonic() - tick,
        ),
    )
