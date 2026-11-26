"""Replay the DEA liquid pair along the loading continuation."""

# ruff: noqa: E402
from pathlib import Path
from time import monotonic
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "diagnosis-starts"))
import retained_starts as c
from phase_replays import point_for
from phases import cd, physical


def dea_rows():
    route, point = point_for("DEA", "selected", "pressure-readback")
    spec = route.bind(point)
    data = c.r.read(c.OUT / "DEA/screen/selected/declared/summary.json.gz")
    cases = {q["key"]: q for q in data["classifications"]}
    pair = next(
        a for a in cases["weiland-1998:32:problem"]["attempts"] if a["confirmed"]
    )
    for loading in [0.495, 0.49, 0.485, 0.48, 0.475, 0.47, 0.465, 0.46, 0.455, 0.45]:
        tick = monotonic()
        item = route.stability_row(spec, dict(problem="weiland-1998:31:problem"), 1.0)
        p = item.problem
        feed = p.feed
        values = list(feed.values)
        values[0] = loading
        feed.values = values
        p.feed = feed
        parent = c.refit.eq.solve_equilibrium(spec.model, p)
        g = cd.gibbs(c.refit.eq.compile_problem(spec.model, p), parent)
        result = cd.coexistence(
            spec,
            p,
            g,
            zip(pair["phases"], pair["packings"]),
            inspect=lambda _, s: (
                physical(spec, p, s)
                if s.amounts and s.requested_tolerance_met
                else None
            ),
        )
        yield dict(loading=loading, seconds=monotonic() - tick, result=result)
        if result.get("phases"):
            pair = result


if __name__ == "__main__":
    assert sys.argv[1:] == ["dea"]
    tick = monotonic()
    c.refit.save(
        HERE / (sys.argv[1] + ".json.gz"),
        dict(wheel=c.r.SHA, rows=list(dea_rows()), seconds=monotonic() - tick),
    )
