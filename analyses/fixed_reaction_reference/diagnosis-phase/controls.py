"""Check native support, capped endpoints and actual AMP daughter density paths."""

from collections import Counter
from copy import copy
from time import monotonic
from closure import HERE, c, point_for
from phase_replays import release_routes
from phases import dilute_vapor_connection


def caps(spec):
    for i in [362, 364, 366, 370, 374, 376, 378, 380]:
        tick = monotonic()
        row = next(
            q
            for q in spec.inputs["observations"]["comparisons"]
            if q["identity"] == f"comparison:{i}"
        )
        p = c.reg.predict(spec.model, spec.observation(row))
        out = dict(
            key=row["identity"],
            args=row["arguments"],
            message=p.message,
            T=spec.problems[row["initial"]].T,
        )
        if p.saturation:
            nodes = []
            for n in p.saturation.nodes:
                rec = dict(
                    a=n.loading,
                    converged=n.state.success,
                    mismatch=n.mismatch if n.state.success else None,
                )
                if not n.state.success:
                    bubble = copy(spec.problems[row["bubble"]])
                    bubble.feed = copy(bubble.feed)
                    bubble.feed.values = dict(bubble.feed.values) | {
                        "carbon-dioxide": n.loading
                    }
                    b = c.refit.eq.solve_equilibrium(spec.model, bubble)
                    rec.update(
                        cold=b.message, cold_pressure=b.pressure if b.success else None
                    )
                nodes.append(rec)
            out["nodes"] = nodes
        yield dict(out, seconds=monotonic() - tick)


def run():
    tick = monotonic()
    run, point = point_for("MDEA", "selected", "pressure-readback")
    spec = run.bind(point)
    _, route, bank = release_routes("MDEA", "support-readback")[0]
    states = {q["key"]: q for q in route.states(spec)}
    rows = c.r.read(c.OUT / "MDEA/screen/selected/declared/summary.json.gz")["rows"]
    supplied = []
    for q in rows:
        if (
            q.get("supplied_available") is not False
            or q["key"].startswith("grid:")
            or "same_calculation_as" in q
        ):
            continue
        t = monotonic()
        item = route.stability_row(spec, states[q["key"]], 1.0)
        support = set(range(len(spec.parameters.component_ids))) - set(
            q["removed_species"]
        )
        trials, absent, repeated, unique = c.r._applicable(item, bank, support)
        parent = c.refit.eq.solve_equilibrium(spec.model, item.problem)
        counts = Counter()
        if trials:
            opt = c.refit.eq.StabilityOptions()
            opt.prepared_trials = c.refit.eq.prepare_supplied_trials(
                spec.model, parent.temperature, trials
            )
            report = c.refit.eq.stability_test(
                c.refit.eq.compile_problem(spec.model, item.problem), parent, opt
            )
            counts.update(report.trials[i].evidence for i, _ in repeated)
        supplied.append(
            dict(
                key=q["key"],
                support=sorted(support),
                absent=len(absent),
                counts=counts,
                seconds=monotonic() - t,
            )
        )
    amp = []
    for design in ("AMP_free", "AMP_fixed"):
        route, point = point_for(design, "selected", "pressure-readback")
        sp = route.bind(point)
        label = c.r.read(c.OUT / f"{design}/selection.json")["selected"]
        rows = c.r.read(c.OUT / f"{design}/controls/{label}.json.gz")["rows"]
        for key, r in rows.items():
            v = r["value"]
            lv = next(
                (
                    a
                    for a in v.get("candidates", [])
                    if a["support"] == "L+V" and a.get("physical_checks_pass")
                ),
                None,
            )
            if lv:
                t = monotonic()
                ph = lv["phases"][1]
                path = dilute_vapor_connection(
                    sp.model, v["T_K"], ph["x"], ph["density_mol_m3"]
                )
                amp.append(
                    dict(
                        design=design,
                        key=key,
                        trace=path,
                        amounts=lv["amounts_mol"],
                        decrease=v["parent_gibbs_RT_mol"][0] - lv["Gibbs_over_RT_mol"],
                        error=v["parent_gibbs_RT_mol"][1] + lv["error"],
                        seconds=monotonic() - t,
                    )
                )
    c.refit.save(
        HERE / "controls.json.gz",
        dict(
            wheel=c.r.SHA,
            supplied=supplied,
            amp=amp,
            caps=list(caps(spec)),
            seconds=monotonic() - tick,
        ),
    )


if __name__ == "__main__":
    run()
