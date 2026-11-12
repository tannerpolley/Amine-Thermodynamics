"""Issue 308 stage 4: declared A/B coordinates and calibration-only evidence."""

import copy
import csv
import json
import os
import sys
import tomllib

import epcsaft
import numpy as np
from epcsaft import equilibrium as eq, regression as reg
from fit_speciation import declarations
from binary_evidence import jsonable
from run import AN, verify_wheel, write_csv
from speciation import PZ, PH, PH2, PC, HPC, DC, W, HC, document, save, problem

CO2 = "carbon-dioxide"


def variant(kind):
    doc = document()
    if kind == "B":
        doc["pairs"].append(
            dict(
                component_id_a=PH,
                component_id_b=PH2,
                coefficients=[
                    dict(identity=f"pair/{PH}/{PH2}/k_ij", family="k_ij", value=dict(magnitude=0, unit="dimensionless"))
                ],
            )
        )
        top = doc["topology"]
        for cid in (PH, PH2):
            c = next(c for c in doc["components"] if c["component_id"] == cid)
            c["fixed"]["charged_molecule_ion"] = dict(value=dict(magnitude=1, unit="dimensionless"))
            c["coefficients"] = [v for v in c["coefficients"] if v["family"] != "packing_diameter"]
            for v in c["coefficients"]:
                v["value"]["magnitude"] = dict(
                    segment_count=2.6519, segment_diameter=3.7136, debye_huckel_diameter=3.7136
                ).get(v["family"], v["value"]["magnitude"])
            top["sites"] += [dict(s, component_id=cid) for s in list(top["sites"]) if s["component_id"] == PZ]
            own = copy.deepcopy(
                next(
                    e for e in top["edges"] if e["endpoint_a"]["component_id"] == e["endpoint_b"]["component_id"] == PZ
                )
            )
            for end in ("endpoint_a", "endpoint_b"):
                own[end]["component_id"] = cid
            for f, val in [("energy_over_k", 0.0), ("volume", 0.07275)]:
                own[f]["identity"] = f"association/{cid}/a/b/{f}"
                own[f]["value"]["magnitude"] = val
            top["edges"].append(own)
            for partner in (W, PZ):
                other = next(
                    e
                    for e in top["edges"]
                    if e["endpoint_a"]["component_id"] == e["endpoint_b"]["component_id"] == partner
                )
                for a, b in [("a", "b"), ("b", "a")]:
                    top["edges"].append(
                        dict(
                            endpoint_a=dict(component_id=cid, site_id=a),
                            endpoint_b=dict(component_id=partner, site_id=b),
                            source=dict(
                                kind="combining-rule",
                                rule_id="wolbach-sandler",
                                inputs={
                                    f: [own[f]["identity"], other[f]["identity"]] for f in ("energy_over_k", "volume")
                                },
                            ),
                        )
                    )
            top["no_cross_association"].append(
                dict(
                    component_id_a=CO2,
                    component_id_b=cid,
                    provenance=dict(source_id="issue-308", locator="approved variant B no CO2 association"),
                )
            )
        top["no_cross_association"].append(
            dict(
                component_id_a=PH,
                component_id_b=PH2,
                provenance=dict(
                    source_id="issue-308", locator="zero cation self energies give zero cation-cation association"
                ),
            )
        )
    return doc


def coordinates(par, kind, reaction_coords):
    declarations, coords = [], []

    def add(name, targets, origin, scale, bounds):
        declarations.append(dict(name=name, targets=targets, origin=origin, scale=scale, bounds=bounds))
        coords.append(reg.coordinate(par, targets, origin=origin, scale=scale, bounds=bounds))

    for cid in (PH, PC, DC):
        group = (PH, PH2) if cid == PH else (cid,)
        targets = [
            (f, c, factor)
            for c in group
            for f, factor in [("segment_diameter", 1), ("debye_huckel_diameter", 1)]
            + ([] if cid == PH and kind == "B" else [("packing_diameter", 0.88)])
        ]
        add(
            cid + "/sigma",
            targets,
            3.7136 if cid == PH and kind == "B" else 5,
            0.25,
            (3, 5 if cid == PH and kind == "B" else 7),
        )
        add(cid + "/u", [("dispersion_energy_over_k", c, 1) for c in group], 274.10, 50, (100, 500))
        add(cid + "/Born", [("born_diameter", c, 1) for c in group], 5, 0.5, (3, 8))
        if cid != DC:
            add(
                cid + "/water-k",
                [("k_ij", (c, W), 1) for c in (group if cid == PH else (PC, DC))],
                0,
                0.05,
                (-0.5, 0.5),
            )
        if cid == PH:
            add(cid + "/bicarbonate-k", [("k_ij", (c, HC), 1) for c in group], 0, 0.05, (-0.5, 0.5))
    add(HPC + "/sigma", [("segment_diameter", HPC, 1)], 3.7136, 0.25, (3, 5))
    add(HPC + "/u", [("dispersion_energy_over_k", HPC, 1)], 274.10, 50, (100, 500))
    for i, c in enumerate(reaction_coords, 3):
        declarations.append(dict(name=f"P{i}/offset", origin=0, scale=1, bounds=(-3, 3)))
        coords.append(c)
    assert len(coords) == 17
    return coords, declarations


def pressure_problem(par, row, tolerance=1e-10, x=None):
    if x is None:
        x = np.r_[np.zeros(14), json.loads((AN / "results/nmr-fit.json").read_text())["optimizer"]]
    rr = laws_at(x)
    for r in rr:
        r["correlation"]["temperature_min"] = 283.15
        r["correlation"]["temperature_max"] = max(float(row["T_K"]), r["correlation"]["temperature_max"])
        r["correlation"] = eq.ReactionLogPolynomial(**r["correlation"])
    return eq.problem_from_mapping(
        dict(
            T=float(row["T_K"]),
            P=dict(free=True, guess=10000 + float(row["pCO2_kPa"]) * 1000),
            feed=dict(
                basis="amounts",
                values={PZ: 1.0, W: 1 / (0.0180153 * float(row["mPZ"])), CO2: float(row["alpha_per_PZ"])},
            ),
            phases=[
                dict(name="L", kind="liquid", support=list(par.component_ids)),
                dict(
                    name="V",
                    kind="vapor",
                    support=[W, CO2, PZ],
                    amount=dict(status="pinned", value=0.0),
                    composition_guess={W: 0.5, CO2: 0.4999, PZ: 0.0001},
                ),
            ],
            reactions=rr,
            neutral_reference=dict(
                solvent=W,
                solute_molality_ratios={
                    i: 4.0 if i == "hydronium-cation" else 1.0 for i in par.component_ids if i != W
                },
                standard_molality_mol_per_kg=1.0,
            ),
            row_tolerance=tolerance,
        )
    )


def calibration(kind, tolerance=1e-10):
    par = epcsaft.Parameters.from_mapping(variant(kind))
    offsets = json.loads((AN / "results/nmr-fit.json").read_text())["optimizer"]
    _, rc, obs, C, _, meta = declarations(par=par, offsets=offsets, tolerance=tolerance)
    for row in meta:
        row["row"] = row["identity"]
    pressure_rows = list(csv.DictReader((AN / "inputs/hilliard-d5.csv").open()))
    full = np.zeros((len(obs) + len(pressure_rows),) * 2)
    full[: len(obs), : len(obs)] = C
    for row in pressure_rows:
        prob = pressure_problem(par, row, tolerance)
        value = float(row["pCO2_kPa"]) * 1000
        i = len(obs)
        obs.append(
            reg.observation(
                par, "partial_pressure", prob, phase="V", species=[CO2], observed=value, form="difference", scale=1
            )
        )
        full[i, i] = float(row["pressure_scale_Pa"]) ** 2
        meta.append(dict(row, group="pressure", observed_fraction=value))
    C = full
    coords, decl = coordinates(par, kind, rc)
    x = np.zeros(17)
    x[-3:] = json.loads((AN / "results/nmr-fit.json").read_text())["optimizer"]
    return par, coords, obs, C, meta, decl, x


def evaluate(par, coords, obs, C, x):
    d = reg.differentiate(par, coords, obs, optimizer=list(x))
    pred = np.array(d.predictions)
    J = np.linalg.solve(np.linalg.cholesky(C), np.array(d.residual_optimizer_gradient).reshape(len(obs), len(coords)))
    _, s, vt = np.linalg.svd(J, full_matrices=False)
    rank = int(np.linalg.matrix_rank(J))
    cov = (vt.T / s**2) @ vt if rank == len(coords) else None
    se = np.sqrt(np.diag(cov)) if cov is not None else None
    return dict(
        predictions=pred.tolist(),
        jacobian=J.tolist(),
        singular_values=s.tolist(),
        right_vectors=vt.tolist(),
        rank=rank,
        covariance=None if cov is None else cov.tolist(),
        se=None if se is None else se.tolist(),
        correlations=None if se is None else (cov / np.outer(se, se)).tolist(),
    )


def phases(par, prob):
    model = epcsaft.Mixture(par)
    sol = eq.solve_equilibrium(model, prob)
    trials = problem(laws_at(np.zeros(17)))
    trials.phases = [
        eq.Phase("trial-L", kind="liquid", support=list(par.component_ids)),
        eq.Phase("trial-V", kind="vapor", support=[W, CO2, PZ]),
    ]
    opt = eq.StabilityOptions()
    opt.trials = trials._native(model).phases
    native = eq.stability_test(eq.compile_problem(model, prob), sol, opt)
    policy = tomllib.loads((AN.parent / "solvent_specification_mdea/B1-declarations.toml").read_text())["phase_policy"]
    report = dict(
        completed=native.completed,
        message=native.message,
        mode=opt.mode.name,
        present_phases=jsonable(native.present_phases),
        trials=[],
        unresolved=[],
        dense=[],
        gas=[],
        ambiguous=[],
    )
    for t in native.trials:
        r = {
            k: jsonable(getattr(t, k))
            for k in [
                "seed",
                "evidence",
                "message",
                "resolved_descent",
                "quantities",
                "composition",
                "split_coordinates",
                "raw_coordinates",
                "raw_residuals",
            ]
        }
        r.update(
            kind=t.phase.kind.name, optimizer_success=t.optimizer.success, optimizer_status=t.optimizer.solver_status
        )
        if t.resolved_descent and (not t.split_coordinates or not np.isfinite(t.split_coordinates[-1])):
            report["unresolved"].append(t.seed)
        if t.resolved_descent and t.split_coordinates:
            eta = float(np.exp(t.split_coordinates[-1]))
            r["packing_fraction"] = eta
            report["dense" if eta >= policy["packing_fraction_threshold"] else "gas"].append(t.seed)
            if policy["ambiguity_interval"][0] < eta < policy["ambiguity_interval"][1]:
                report["ambiguous"].append(t.seed)
        if (
            t.evidence in ["unresolved", "indeterminate", "negative_plane_without_positive_donor"]
            or not t.optimizer.success
        ):
            report["unresolved"].append(t.seed)
        report["trials"].append(r)
    report["passed"] = (
        native.completed
        and sol.requested_tolerance_met
        and {t.phase.kind.name for t in native.trials} == {"Liquid", "Vapor"}
        and not any(report[k] for k in ["unresolved", "dense", "gas", "ambiguous"])
    )
    report["solution"] = dict(
        requested_tolerance_met=sol.requested_tolerance_met,
        residuals=list(sol.residuals),
        mole_fractions=list(sol.mole_fractions),
    )
    return report


def laws_at(x):
    rr = json.loads((AN / "results/speciation-reactions.json").read_text())
    for r, v in zip(rr[5:], x[-3:], strict=True):
        r["correlation"]["a"] += float(v)
    for r in rr:
        r["correlation"]["temperature_min"] = 283.15
        r["correlation"]["temperature_max"] = max(333.3, r["correlation"]["temperature_max"])
    return rr


def qualification(kind):
    par, coords, obs, C, meta, decl, x = calibration(kind)
    record = dict(
        variant=kind,
        coordinates=decl,
        optimizer=x.tolist(),
        scope="232 NMR group observations plus 62 Hilliard D.5 partial pressures",
    )
    save(f"reactive-{kind}-start.json", variant(kind))
    try:
        record["information"] = evaluate(par, coords, obs, C, x)
        save(f"reactive-{kind}-qualification.json", record)
        L = np.linalg.cholesky(C)
        pred = np.array(record["information"]["predictions"])
        J = np.array(record["information"]["jacobian"])
        v = np.array(record["information"]["right_vectors"][-1])
        checks = []
        for h in (1e-3, 1e-4):
            plus = reg.differentiate(par, coords, obs, optimizer=(x + h * v).tolist())
            minus = reg.differentiate(par, coords, obs, optimizer=(x - h * v).tolist())
            fd = np.linalg.solve(L, (np.array(plus.predictions) - minus.predictions) / (2 * h))
            checks.append(
                dict(
                    step=h,
                    relative_error=float(np.linalg.norm(fd - J @ v) / np.linalg.norm(J @ v)),
                    finite_difference_direction_norm=float(np.linalg.norm(fd)),
                )
            )
        record["derivatives"] = checks
        replay = reg.differentiate(par, coords, obs, optimizer=x.tolist())
        record["replay_max_difference"] = float(np.max(np.abs(pred - replay.predictions)))
        record.update(qualification_checks(kind))
    except Exception as e:
        record.update(passed=False, exception=type(e).__name__, message=str(e))
    save(f"reactive-{kind}-qualification.json", record)
    print(kind, record.get("passed"), record.get("message"), flush=True)


def qualification_checks(kind):
    par, coords, obs, C, meta, decl, x = calibration(kind)
    record = {}
    shared = json.loads((AN.parent / "mea_parameter_bundle/results/selected-current-best-parameters.json").read_text())
    values = []
    for doc in (shared, variant(kind)):
        model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(doc, components=[W, CO2]))
        st = model.state(313.15, P=100000, phase="liquid", x=[0.99, 0.01], derived_properties=True)
        values.append([st.pressure, *st.log_fugacity_coefficient])
    record["shared_prediction_difference"] = (np.array(values[0]) - values[1]).tolist()
    record["source_anchors"] = json.loads((AN / "results/speciation-source-anchors.json").read_text())
    record["balances_owner"] = (
        "speciation.calculate: all eight reactions element/charge balanced; unchanged stoichiometry"
    )
    rr = laws_at(x)
    prob = problem(rr)
    record["loaded_phase"] = phases(par, prob)
    fine = copy.copy(prob)
    fine.row_tolerance = 1e-12
    record["refined_phase"] = phases(par, fine)
    record["loaded_refinement_max_fraction"] = float(
        np.max(
            np.abs(
                np.array(record["loaded_phase"]["solution"]["mole_fractions"])
                - record["refined_phase"]["solution"]["mole_fractions"]
            )
        )
    )
    record["passed"] = record["loaded_phase"]["passed"]
    return record


def endpoint_evidence(kind):
    par, coords, obs, C, meta, decl, _ = calibration(kind)
    fit = json.loads((AN / f"results/reactive-{kind}-fit.json").read_text())
    if not fit.get("usable"):
        raise ValueError(f"No usable endpoint: {fit}")
    x = np.array(fit["optimizer"])
    endpoint = epcsaft.Parameters.from_mapping(json.loads((AN / f"results/reactive-{kind}-endpoint.json").read_text()))
    info = fit["endpoint_information"]
    pred = np.array(info["predictions"])
    target = np.array([r["observed_fraction"] for r in meta])
    z = np.linalg.solve(np.linalg.cholesky(C), pred - target)
    records = [
        dict(
            r,
            calculated=float(y),
            difference=float(y - r["observed_fraction"]),
            residual_marginal=float((y - r["observed_fraction"]) / np.sqrt(C[i, i])),
            whitened_residual=float(z[i]),
        )
        for i, (r, y) in enumerate(zip(meta, pred, strict=True))
    ]
    # Union columns preserve each source's original units and blank identity.
    keys = list(dict.fromkeys(k for r in records for k in r))
    write_csv(f"reactive-{kind}-residuals.csv", [{k: r.get(k, "") for k in keys} for r in records])
    report = dict(
        replay_cost=float(z @ z / 2),
        fit_cost=fit["cost"],
        rms=float(np.sqrt(np.mean(z * z))),
        NMR_RMS=float(np.sqrt(np.mean(z[:232] ** 2))),
        pressure_RMS=float(np.sqrt(np.mean(z[232:] ** 2))),
        q039_NMR_RMS=float(np.sqrt(np.mean(z[:232] ** 2)) * 0.02 / 0.039),
        phases=[],
    )
    for r in meta:
        if r["group"] == 2:
            continue
        if r["group"] == "pressure":
            prob = pressure_problem(endpoint, r, x=x)
        else:
            prob = problem(laws_at(x), float(r["T_K"]))
            prob.feed.values = {PZ: float(r["pz_mol"]), W: 1 / 0.0180153, CO2: float(r["co2_mol"])}
        try:
            out = phases(endpoint, prob)
        except Exception as error:
            out = dict(passed=False, exception=type(error).__name__, message=str(error))
        out.update(row=r["row"], group=r["group"], T_K=r["T_K"])
        report["phases"].append(out)
        save(f"reactive-{kind}-evidence.json", report)
        print(kind, "phase", len(report["phases"]), out["passed"], flush=True)
    report["phase_passed"] = all(r["passed"] for r in report["phases"])
    report["selection"] = (
        "none: owner gate"
        if not report["phase_passed"] or fit["active_bounds"] or info["rank"] < 17
        else "eligible for calibration-only comparison"
    )
    save(f"reactive-{kind}-evidence.json", report)


def reduction_effects(kind):
    par, coords, obs, C, meta, decl, _ = calibration(kind)
    fit = json.loads((AN / f"results/reactive-{kind}-fit.json").read_text())
    x = np.array(fit["optimizer"])
    base = np.array(fit["endpoint_information"]["predictions"])
    L = np.linalg.cholesky(C)
    names = [r["name"] for r in decl]
    records = []
    steps = [
        "tie dicarbamate sigma/u/Born to monocarbamate",
        "fix P4 offset at zero",
        "fix tied carbamate Born diameters at 5 angstrom",
        "fix HPZCOO u at 274.10 kelvin",
    ]
    for step, label in enumerate(steps):
        if step == 0:
            for family in ("sigma", "u", "Born"):
                x[names.index(DC + "/" + family)] = x[names.index(PC + "/" + family)]
        elif step == 1:
            x[names.index("P4/offset")] = 0.0
        elif step == 2:
            x[names.index(PC + "/Born")] = x[names.index(DC + "/Born")] = 0.0
        else:
            x[names.index(HPC + "/u")] = 0.0
        info = evaluate(par, coords, obs, C, x)
        delta = np.array(info["predictions"]) - base
        z = np.linalg.solve(L, delta)
        record = dict(
            step=step + 1,
            proposal=label,
            applied_to_fit=False,
            optimizer=x.tolist(),
            observable_change_scaled_norm=float(np.linalg.norm(z)),
            NMR_max_fraction_change=float(max(abs(delta[:232]))),
            pressure_max_change_Pa=float(max(abs(delta[232:]))),
            singular_values_unreduced_chart=info["singular_values"],
        )
        # These are counterfactual substitutions only; no reduced optimization.
        records.append(record)
        save(f"reactive-{kind}-reduction-effects.json", records)
    print(kind, "reduction observable effects retained", flush=True)


def sensitivities(kind):
    par, coords, obs, C, meta, decl, _ = calibration(kind)
    fit = json.loads((AN / f"results/reactive-{kind}-fit.json").read_text())
    x = np.array(fit["optimizer"])
    endpoint = epcsaft.Parameters.from_mapping(json.loads((AN / f"results/reactive-{kind}-endpoint.json").read_text()))
    model = epcsaft.Mixture(endpoint)
    output = []
    for row in meta[232:]:
        out = dict(
            row=row["row"],
            T_K=row["T_K"],
            pressure_conversion_effect_Pa=float(row["pCO2_kPa"]) * 1000 * 640 / 101325,
            pressure_reference="101325 Pa assumed atmospheric; actual row total pressure not printed",
        )
        for name, field, delta in [
            ("loading", "alpha_per_PZ", 0.02 * float(row["alpha_per_PZ"])),
            ("T_control", "T_K", 0.1),
            ("T_thermometer", "T_K", 0.01),
        ]:
            vals = []
            for sign in (-1, 1):
                perturbed = dict(row, **{field: float(row[field]) + sign * delta})
                prob = pressure_problem(endpoint, perturbed, x=x)
                o = reg.observation(
                    endpoint,
                    "partial_pressure",
                    prob,
                    phase="V",
                    species=[CO2],
                    observed=float(row["pCO2_kPa"]) * 1000,
                    form="difference",
                    scale=1,
                )
                y = reg.predict(model, o)
                assert y.status.name == "Available" and y.requested_tolerance_met, y.message
                vals.append(y.value)
            out[name + "_minus_Pa"], out[name + "_plus_Pa"] = vals
        output.append(out)
    write_csv(f"reactive-{kind}-input-sensitivities.csv", output)


def phase_diagnosis(kind):
    fit = json.loads((AN / f"results/reactive-{kind}-fit.json").read_text())
    evidence = json.loads((AN / f"results/reactive-{kind}-evidence.json").read_text())
    failed = [r for r in evidence["phases"] if not r["passed"]]
    if not failed:
        return
    par, coords, _, _, meta, decl, _ = calibration(kind)
    x = np.array(fit["optimizer"])
    case = failed[0]
    row = next(r for r in meta if r["row"] == case["row"] and r["group"] == case["group"])

    def probe(point):
        chart = reg.evaluate_coordinates(par, coords[:14], point[:14].tolist(), [])
        p = epcsaft.Parameters(chart.parameters, par.component_ids, par.site_ids)
        if row["group"] == "pressure":
            prob = pressure_problem(p, row, x=point)
        else:
            prob = problem(laws_at(point), float(row["T_K"]))
            prob.feed.values = {PZ: float(row["pz_mol"]), W: 1 / 0.0180153, CO2: float(row["co2_mol"])}
        return phases(p, prob)

    proposals = json.loads((AN / f"results/reactive-{kind}-reduction-effects.json").read_text())
    point = x.copy()
    point[13] -= 1  # One approved optimizer unit lowers HPZCOO dispersion by 50 K.
    probes = [dict(proposal="HPZCOO u/k minus 50 K; diagnostic only", optimizer=point.tolist(), phase=probe(point))]
    for proposal in proposals:
        point = np.array(proposal["optimizer"])
        probes.append(
            dict(proposal=proposal["proposal"], step=proposal["step"], optimizer=point.tolist(), phase=probe(point))
        )
    pressure_row = next(r for r in meta if r["group"] == "pressure")
    source_prob = problem(laws_at(x), float(pressure_row["T_K"]))
    source_prob.P = 101325.0
    source_prob.feed.values = {
        PZ: 1.0,
        W: 1 / (0.0180153 * float(pressure_row["mPZ"])),
        CO2: float(pressure_row["alpha_per_PZ"]),
    }
    chart = reg.evaluate_coordinates(par, coords[:14], x[:14].tolist(), [])
    source_par = epcsaft.Parameters(chart.parameters, par.component_ids, par.site_ids)
    source_trial = phases(source_par, source_prob)
    save(
        f"reactive-{kind}-phase-diagnosis.json",
        dict(
            case=case,
            component_order=list(par.component_ids),
            probes=probes,
            association="HPZCOO has no sites; no association parameter is fitted",
            atmospheric_pressure_probe=dict(row=pressure_row["row"], assumed_P_Pa=101325.0, phase=source_trial),
            scope="Counterfactual native chart evaluations only; no reduced fit, no selection, no adoption.",
        ),
    )


def fit_variant(kind):
    par, coords, obs, C, meta, decl, x = calibration(kind)
    u = reg.MeasurementUncertainty()
    u.output_sigma = np.sqrt(np.diag(C)).tolist()
    u.covariance = C.ravel().tolist()
    qualification_record = json.loads((AN / f"results/reactive-{kind}-qualification.json").read_text())
    assert "refined_phase" in qualification_record and "derivatives" in qualification_record
    record = dict(variant=kind, coordinates=decl, start_optimizer=x.tolist(), observations=len(obs))
    try:
        controls = reg.FitControls(
            maximum_iterations=100,
            maximum_elapsed_time_seconds=3600,
            function_tolerance=1e-10,
            parameter_tolerance=1e-10,
            gradient_tolerance=1e-8,
            workers=int(os.environ["AGENT_HEAVY_CORES"]),
        )
        # Native chart starts are the document's parameter and observation law values.
        # Start reaction laws at the accepted stage-3 offsets, keeping original bounds.
        fit = reg.fit(par, coords, obs, controls=controls, uncertainty=u, singular_vectors=True)
        record.update(
            status=fit.status,
            usable=fit.usable,
            message=fit.message,
            optimizer=list(fit.optimizer),
            cost=fit.final_cost,
            active_bounds=list(fit.covariance.active_bounds),
        )
        save(f"reactive-{kind}-fit.json", record)
        if fit.usable:
            endpoint = reg.fitted_parameters(par, fit)
            save(f"reactive-{kind}-endpoint.json", epcsaft.parameters.document_mapping(endpoint))
            record["endpoint_information"] = evaluate(par, coords, obs, C, fit.optimizer)
    except Exception as e:
        record.update(exception=type(e).__name__, message=str(e))
    save(f"reactive-{kind}-fit.json", record)
    print(json.dumps({k: v for k, v in record.items() if k not in ["endpoint_information", "coordinates"]}), flush=True)


if __name__ == "__main__":
    verify_wheel()
    {
        "qualify": qualification,
        "fit": fit_variant,
        "evidence": endpoint_evidence,
        "reductions": reduction_effects,
        "sensitivities": sensitivities,
        "diagnose": phase_diagnosis,
    }[sys.argv[2] if len(sys.argv) > 2 else "qualify"](sys.argv[1])
