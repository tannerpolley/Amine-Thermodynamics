"""Inspect the native trial estimates separately from selection of the scalar minimum."""

from closure import HERE, c, point_for
from phases import trials
from time import monotonic


def rows():
    route, point = point_for("MDEA", "selected", "pressure-readback")
    spec = route.bind(point)
    folder = c.OUT / "MDEA/screen/selected/declared"
    states = {
        q["key"]: q["state"]
        for q in c.r.read(folder / "state-inventory.json.gz")["rows"]
    }
    for q in c.r.read(folder / "summary.json.gz")["rows"]:
        key = q["key"]
        if (
            key.startswith("grid:")
            or q["status"] != "CentralSolveUnavailable"
            or "same_calculation_as" in q
        ):
            continue
        tick = monotonic()
        item = route.stability_row(spec, states[key], 1.0)
        p = item.problem
        p.pressure = type(p.pressure).fixed(q["supplied_parent_pressure_Pa"])
        s = c.refit.eq.solve_equilibrium(spec.model, p)
        opt = c.refit.eq.StabilityOptions()
        opt.mode = type(opt.mode).Full
        rep = c.refit.eq.stability_test(
            c.refit.eq.compile_problem(spec.model, p), s, opt
        )
        yield dict(
            key=key,
            message=q["message"],
            parent=s.message,
            report=rep.message,
            trials=trials(rep),
            seconds=monotonic() - tick,
        )


if __name__ == "__main__":
    tick = monotonic()
    c.refit.save(
        HERE / "trials.json.gz",
        dict(wheel=c.r.SHA, rows=list(rows()), seconds=monotonic() - tick),
    )
