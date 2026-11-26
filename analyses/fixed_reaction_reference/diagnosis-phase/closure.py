"""Hold each returned composition fixed and probe neighboring densities on the same EOS."""

# ruff: noqa: E402
from pathlib import Path
from time import monotonic
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "diagnosis-starts"))
import retained_starts as c
from phase_replays import point_for
import mea_stability as mea
from reference_derivatives import pressure_reclosure
from phases import cd, physical
from copy import copy


def mea_rows():
    _, point = point_for("MEA", "selected", "pressure-readback")
    spec, records = mea.preparations(point["parameters"], c.refit.P_REF)
    for path in sorted((c.OUT / "E/MEA/measured").glob("*.gz")):
        for row in c.r.read(path):
            if row["available"]:
                continue
            t = monotonic()
            p = copy(spec.problems[records[row["identity"]]["problem"]])
            p.P = row["P_Pa"]
            p.phases = [copy(mea.bubble_problem(p).phases[0])]
            original = row["parent"]["phases"][0]
            p.phases[0].composition_guess = original["x"]
            p.phases[0].packing_guess = original[
                "density_mol_m3"
            ] * spec.model._model.packing_fraction_coefficient(p.T, original["x"])
            n = p._native(spec.parameters)
            s = c.refit.eq.solve_equilibrium(spec.model, n)
            out = dict(key=row["identity"], P=p.P, parent=s.message)
            if s.requested_tolerance_met and s.amounts:
                b = c.refit.eq.stability_test(
                    c.refit.eq.compile_problem(spec.model, n), s
                ).standard_over_rt
                out["phases"] = []
                for phase in row["parent"]["phases"]:
                    x, rho = phase["x"], phase["density_mol_m3"]
                    st = spec.model.state(p.T, rho=rho, x=x)
                    _, _, check = pressure_reclosure(
                        spec.model, n, p.T, p.P, rho, x, b, st
                    )
                    out["phases"].append(
                        dict(original_error=st.pressure / p.P - 1, readback=check)
                    )
            yield dict(out, seconds=monotonic() - t)


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
    fn = {"dea": dea_rows, "mea": mea_rows}[sys.argv[1]]
    tick = monotonic()
    c.refit.save(
        HERE / (sys.argv[1] + ".json.gz"),
        dict(wheel=c.r.SHA, rows=list(fn()), seconds=monotonic() - tick),
    )
