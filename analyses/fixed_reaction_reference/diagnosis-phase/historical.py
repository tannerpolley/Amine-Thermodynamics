"""Evaluate L+V at the historical target pressures on each control's own references."""

from closure import HERE, c, cd, physical
from calculations import mdea_incumbent
from mdea_reference import route, FixedReference
from phases import dilute_vapor_connection
from reaction_reference import references
from copy import copy
from time import monotonic


def rows():
    for family in ("salt", "historical"):
        for label in ("original", "rms", "fixed"):
            if label == "fixed" and family != "salt":
                continue
            run = (
                route(family, "diagnosis-phase/" + label, FixedReference)
                if label == "fixed"
                else route(family, "diagnosis-phase/" + label)
            )
            point = (
                mdea_incumbent(family)[0]
                if label != "rms"
                else c.r.read(c.refit.ROUND7 / f"C/{family}/selection.json.gz")[
                    "selected"
                ][2]
            )
            spec = run.bind(point)
            template = spec.problems[
                next(r["bubble"] for r in c.ROWS if r["group"] == "Merkley")
            ]
            controls = c.r.read(
                c.refit.ROUND7
                / f"C/{family}/{'original' if label == 'fixed' else label}-fixed-pressures.json.gz"
            )
            for key in ("pressure_121_MPa", "pressure_262_MPa"):
                q = controls[key]
                if (
                    label == "fixed"
                    and key != "pressure_121_MPa"
                    or label != "fixed"
                    and any(a["confirmed"] for a in q["attempts"])
                ):
                    continue
                t = monotonic()
                p = copy(template)
                p.T, p.P = q["T_K"], q["P_Pa"]
                p.feed = copy(template.feed)
                p.feed.values = q.get("feed") or dict(zip(q["species"], q["feed_mol"]))
                p.phases = [copy(z) for z in template.phases]
                p.phases[-1].amount = c.refit.eq.Free()
                if label == "fixed":
                    a = c.r.read(c.refit.ROUND7 / "A/reference.json.gz")["comparisons"][
                        "100 kPa"
                    ]["attempts"][0]
                    for i, ph in enumerate(p.phases):
                        ph.composition_guess = {
                            k: a["phases"][i][spec.parameters.component_ids.index(k)]
                            for k in ph.support
                        }
                        ph.packing_guess = a["packings"][i]
                n = p._native(spec.parameters)
                if label == "fixed":
                    references(n, True)
                    assert all(
                        rx.reference.reference_pressure_pa == 100000
                        for rx in n.reactions
                    )
                s = c.refit.eq.solve_equilibrium(spec.model, n)
                out = dict(
                    family=family,
                    weights=label,
                    T=p.T,
                    P=p.P,
                    message=s.message,
                    amounts=list(s.amounts),
                )
                if s.success and s.requested_tolerance_met and min(s.amounts) > 0:
                    out.update(physical(spec, n, s))
                    g = cd.gibbs(c.refit.eq.compile_problem(spec.model, n), s)
                    out["trace"] = dilute_vapor_connection(
                        spec.model, p.T, s.phase_mole_fractions(1), s.molar_densities[1]
                    )
                    n.phases = n.phases[:1]
                    parent = c.refit.eq.solve_equilibrium(spec.model, n)
                    if parent.success:
                        pg = cd.gibbs(c.refit.eq.compile_problem(spec.model, n), parent)
                        out.update(decrease=pg[0] - g[0], error=pg[1] + g[1])
                yield dict(out, seconds=monotonic() - t)


if __name__ == "__main__":
    tick = monotonic()
    c.refit.save(
        HERE / "historical.json.gz",
        dict(wheel=c.r.SHA, rows=list(rows()), seconds=monotonic() - tick),
    )
