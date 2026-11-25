"""At the two remaining MEA pressures, restart the same parent from a nearby pressure."""

from closure import HERE, c, mea, point_for, pressure_reclosure, physical
from time import monotonic
from types import SimpleNamespace
from collections import Counter


def rows(search=False):
    route, point = point_for("MEA", "selected", "pressure-readback")
    spec, records = mea.preparations(point["parameters"], c.refit.P_REF)
    selected = {"vle_obs_0047-pco2", "vle_obs_0162-pco2"}
    for f in sorted((c.OUT / "E/MEA/measured").glob("*.gz")):
        for q in c.r.read(f):
            if q["identity"] not in selected:
                continue
            p = mea.bubble_problem(spec.problems[records[q["identity"]]["problem"]])
            P = q["P_Pa"]
            phases = q["parent"]["phases"]
            p.phases = p.phases[: len(phases)]
            for phase, old in zip(p.phases, phases):
                phase.amount = c.refit.eq.Free()
                phase.composition_guess = {
                    k: old["x"][spec.parameters.component_ids.index(k)]
                    for k in phase.support
                }
                phase.packing_guess = old[
                    "density_mol_m3"
                ] * spec.model._model.packing_fraction_coefficient(p.T, old["x"])
            for factor in (0.999,) if search else (1.001, 0.999, 1.01, 0.99):
                tick = monotonic()
                p.P = P * factor
                seed = c.refit.eq.solve_equilibrium(spec.model, p)
                p.P = P
                s = c.refit.eq.solve_equilibrium(
                    spec.model, p, seed if seed.success else None
                )
                out = dict(key=q["identity"], factor=factor, message=s.message, P=P)
                if s.success and s.requested_tolerance_met and min(s.amounts) > 0:
                    n = p._native(spec.parameters)
                    out.update(physical(spec, n, s))
                    b = c.refit.eq.stability_test(
                        c.refit.eq.compile_problem(spec.model, n), s
                    ).standard_over_rt
                    checks = []
                    for ph in out["phases"]:
                        x, rho = ph["x"], ph["density_mol_m3"]
                        st = spec.model.state(p.T, rho=rho, x=x)
                        _, _, check = pressure_reclosure(
                            spec.model, n, p.T, P, rho, x, b, st
                        )
                        checks.append(check)
                    out["reclosure"] = checks
                    if search:
                        # The bank contains finite trial compositions. Replay the same
                        # ion-rich witness as well, at the restarted parent.
                        compiled = c.refit.eq.compile_problem(spec.model, n)
                        options = c.refit.eq.StabilityOptions()
                        options.mode = type(options.mode).Full
                        native = c.refit.eq.stability_test(compiled, s, options)
                        bank = [
                            dict(w, kind=w["kind"].capitalize())
                            for w in c.r.read(mea.BASE / "split-registry.json")[
                                "trials"
                            ]
                        ]
                        ion = q["ion_rich_seed"]
                        amounts = ion["amounts_mol"]
                        x = [
                            amounts[k] / sum(amounts.values())
                            for k in spec.parameters.component_ids
                        ]
                        bank.append(
                            dict(
                                support=list(range(len(x))),
                                composition=x,
                                kind="Liquid",
                                packing=ion["packing_fraction"],
                            )
                        )
                        phases, _, repeated, _ = c.r._applicable(
                            SimpleNamespace(problem=n),
                            bank,
                            set(range(len(x))) - set(compiled.removed_species),
                        )
                        opts = c.refit.eq.StabilityOptions()
                        opts.prepared_trials = c.refit.eq.prepare_supplied_trials(
                            spec.model, p.T, phases
                        )
                        ts = c.refit.eq.stability_test(compiled, s, opts).trials
                        out.update(
                            native_message=native.message,
                            native_descent=any(
                                z.resolved_descent for z in native.trials
                            ),
                            supplied=Counter(ts[i].evidence for i, _ in repeated),
                            supplied_descent=sum(
                                c.r.supplied_negative(
                                    dict(
                                        evidence=ts[i].evidence,
                                        quantities=ts[i].quantities,
                                    )
                                )
                                for i, _ in repeated
                            ),
                        )
                yield dict(out, seconds=monotonic() - tick)


if __name__ == "__main__":
    import sys

    search = "--search" in sys.argv
    tick = monotonic()
    c.refit.save(
        HERE / ("parent-search.json.gz" if search else "parents.json.gz"),
        dict(wheel=c.r.SHA, rows=list(rows(search)), seconds=monotonic() - tick),
    )
