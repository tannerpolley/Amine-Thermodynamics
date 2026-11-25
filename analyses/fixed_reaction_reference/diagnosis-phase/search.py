"""Perturb only the homogeneous parent guess before the full stability search."""

from closure import HERE, c, point_for
from phases import trials
from time import monotonic


def probes():
    for design in ("MEA", "DEA"):
        route, point = point_for(design, "selected", "parent-restart")
        spec = route.bind(point)
        if design == "MEA":
            state = next(
                q for q in c.r.states()[1] if q["key"] == "offset|0.4|338.15|0.5375|1.5"
            )
            item = c.r.stability_row(spec, state, 1.0)
        else:
            item = route.stability_row(
                spec, dict(problem="lawson-1976-viii:1:problem"), 1.0
            )
        pressure = (
            c.refit.eq.solve_equilibrium(spec.model, item.pressure_reference).pressure
            * item.pressure_ratio
        )
        p = item.problem
        for factor in [1.0, 1.01, 0.99]:
            tick = monotonic()
            p.pressure = type(p.pressure).fixed(pressure * factor)
            s = c.refit.eq.solve_equilibrium(spec.model, p)
            p.pressure = type(p.pressure).fixed(pressure)
            parent = c.refit.eq.solve_equilibrium(
                spec.model, p, s if factor != 1 else None
            )
            o = c.refit.eq.StabilityOptions()
            o.mode = type(o.mode).Full
            report = c.refit.eq.stability_test(
                c.refit.eq.compile_problem(spec.model, p), parent, o
            )
            yield dict(
                design=design,
                P=pressure,
                starting_pressure_factor=factor,
                parent=parent.message,
                message=report.message,
                completed=report.completed,
                trials=trials(report),
                seconds=monotonic() - tick,
            )


if __name__ == "__main__":
    tick = monotonic()
    c.refit.save(
        HERE / "search.json.gz",
        dict(wheel=c.r.SHA, rows=list(probes()), seconds=monotonic() - tick),
    )
