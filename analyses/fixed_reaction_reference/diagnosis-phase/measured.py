"""Try an explicit liquid plus neutral vapor for every distinct MDEA descent."""

from closure import HERE, c, point_for, physical, cd
from phases import dilute_vapor_connection
from copy import copy
from time import monotonic


def rows():
    route, point = point_for("MDEA", "selected", "vapor-readback")
    spec = route.bind(point)
    folder = c.OUT / "MDEA/screen/selected/declared"
    screen = c.r.read(folder / "summary.json.gz")
    states = {q["key"]: q for q in c.r.read(folder / "state-inventory.json.gz")["rows"]}
    template = spec.problems[
        next(q["bubble"] for q in c.ROWS if q["group"] == "Merkley")
    ]
    for q in screen["rows"]:
        if not q["descent"] or "same_calculation_as" in q:
            continue
        t = monotonic()
        rec = states[q["key"]]
        p = copy(template)
        p.phases = [copy(ph) for ph in template.phases]
        p.phases[1].amount = c.refit.eq.Free()
        p.feed = copy(template.feed)
        p.T = rec["T_K"]
        p.P = rec.get("declared_pressure_Pa") or q["supplied_parent_pressure_Pa"]
        p.feed.values = dict(zip(spec.parameters.component_ids, rec["feed_mol"]))
        s = c.refit.eq.solve_equilibrium(spec.model, p)
        row = dict(
            key=q["key"], T=p.T, P=p.P, message=s.message, amounts=list(s.amounts)
        )
        if s.success and s.requested_tolerance_met and min(s.amounts) > 0:
            n = p._native(spec.parameters)
            row.update(physical(spec, n, s))
            split = cd.gibbs(c.refit.eq.compile_problem(spec.model, n), s)
            p.phases = p.phases[:1]
            parent = c.refit.eq.solve_equilibrium(spec.model, p)
            if parent.success:
                g = cd.gibbs(c.refit.eq.compile_problem(spec.model, p), parent)
                row.update(decrease=g[0] - split[0], error=g[1] + split[1])
            row["vapor_trace"] = dilute_vapor_connection(
                spec.model, p.T, s.phase_mole_fractions(1), s.molar_densities[1]
            )
        yield dict(row, seconds=monotonic() - t)


if __name__ == "__main__":
    tick = monotonic()
    c.refit.save(
        HERE / "measured.json.gz",
        dict(wheel=c.r.SHA, rows=list(rows()), seconds=monotonic() - tick),
    )
