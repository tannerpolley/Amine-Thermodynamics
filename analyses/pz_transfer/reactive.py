"""Issue 308 stage 4/5: variant-A reactive calibration, fluid-phase census and Ermatchkov 2006 hold-out.

Tags: "A" is the frozen 17-coordinate stage-4 endpoint (fitted at 6c213e0, retained results only);
"A12" is the 12-coordinate refit (the record); "A12s" is the penalty fit, kept as a side result. Run with agent-heavy:
  reactive.py fit 1|2        native fit from start 1 (design starts) or 2 (frozen A projected)
  reactive.py score A|A12    calibration errors, 183-state census, Ermatchkov 2006 hold-out
  reactive.py fit-stable     #255 penalty fit (side result)
  reactive.py conditional|ranking TAG, profile TAG K    #307 uncertainty steps
"""

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
from speciation import PZ, PH, PH2, PC, HPC, DC, W, HC, save, problem, document

CO2 = "carbon-dioxide"
# Owner decision 2026-11-12: HPZCOO has finite model volatility, so it belongs in the vapour support.
VAPOR = [W, CO2, PZ, HPC]
NMR_OFFSETS = json.loads((AN / "results/nmr-fit.json").read_text())["optimizer"]
HOLDOUT = AN / "inputs/ermatchkov2006.csv"


def read(name):
    return json.loads((AN / "results" / name).read_text())


def laws_at(offsets):
    rr = json.loads((AN / "results/speciation-reactions.json").read_text())
    for r, v in zip(rr[5:], offsets[-3:], strict=True):
        r["correlation"]["a"] += float(v)
    for r in rr:
        r["correlation"]["temperature_min"] = 283.15
        # Evaluation interval only (covers the 333.65 K T+0.5 K check states); law values are unchanged.
        r["correlation"]["temperature_max"] = max(333.7, r["correlation"]["temperature_max"])
    return rr


def pressure_problem(par, row, offsets, tolerance=1e-10):
    rr = laws_at(offsets)
    for r in rr:
        # Evaluation extension only; source-law domains stay 283-333 K and are reported as extrapolation.
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
                    support=VAPOR,
                    amount=dict(status="pinned", value=0.0),
                    composition_guess={k: v for k, v in {W: 0.5, CO2: 0.4999, PZ: 0.00005, HPC: 0.00005}.items() if k in VAPOR},
                ),
            ],
            reactions=rr,
            neutral_reference=dict(
                solvent=W,
                solute_molality_ratios={i: 4.0 if i == "hydronium-cation" else 1.0 for i in par.component_ids if i != W},
                standard_molality_mol_per_kg=1.0,
            ),
            row_tolerance=tolerance,
        )
    )


def pressure_observation(par, prob, row):
    return reg.observation(
        par, "partial_pressure", prob, phase="V", species=[CO2], observed=float(row["pCO2_kPa"]) * 1000,
        form="difference", scale=1,
    )


def calibration(par, offsets, tolerance=1e-10):
    """232 NMR group fractions plus 62 Hilliard D.5 partial pressures, with their approved covariance."""
    _, rc, obs, C, _, meta = declarations(par=par, offsets=offsets, tolerance=tolerance)
    for row in meta:
        row["row"] = row["identity"]
    pressure_rows = list(csv.DictReader((AN / "inputs/hilliard-d5.csv").open()))
    full = np.zeros((len(obs) + len(pressure_rows),) * 2)
    full[: len(obs), : len(obs)] = C
    for row in pressure_rows:
        i = len(obs)
        obs.append(pressure_observation(par, pressure_problem(par, row, offsets, tolerance), row))
        full[i, i] = float(row["pressure_scale_Pa"]) ** 2
        meta.append(dict(row, group="pressure", observed_fraction=float(row["pCO2_kPa"]) * 1000))
    return rc, obs, full, meta


def chart(par, rc):
    """Approved 12-coordinate variant-A chart: carbamates tied, PZ-specific Born diameters fixed at 5 angstrom."""
    decl, coords = [], []

    def add(name, targets, origin, scale, bounds):
        decl.append(dict(name=name, targets=targets, origin=origin, scale=scale, bounds=bounds))
        coords.append(reg.coordinate(par, targets, origin=origin, scale=scale, bounds=bounds))

    def sphere(group):
        return [(f, c, k) for c in group for f, k in [("segment_diameter", 1), ("debye_huckel_diameter", 1), ("packing_diameter", 0.88)]]

    # Limits are the design table's engineering search allowances, not measured bounds.
    add(PH + "/sigma", sphere((PH, PH2)), 5, 0.25, (2, 9))
    add(PH + "/u", [("dispersion_energy_over_k", c, 1) for c in (PH, PH2)], 274.10, 50, (50, 1000))
    add(PH + "/water-k", [("k_ij", (c, W), 1) for c in (PH, PH2)], 0, 0.05, (-1, 0.5))
    add(PH + "/bicarbonate-k", [("k_ij", (c, HC), 1) for c in (PH, PH2)], 0, 0.05, (-1, 0.5))
    add("carbamate/sigma", sphere((PC, DC)), 5, 0.25, (2, 9))
    add("carbamate/u", [("dispersion_energy_over_k", c, 1) for c in (PC, DC)], 274.10, 50, (50, 1000))
    add("carbamate/water-k", [("k_ij", (c, W), 1) for c in (PC, DC)], 0, 0.05, (-0.5, 0.5))
    add(HPC + "/sigma", [("segment_diameter", HPC, 1)], 3.7136, 0.25, (2, 6))
    add(HPC + "/u", [("dispersion_energy_over_k", HPC, 1)], 274.10, 50, (50, 1000))
    for i, c in enumerate(rc, 3):
        decl.append(dict(name=f"P{i}/offset", origin=0, scale=1, bounds=(-3, 3)))
        coords.append(c)
    return coords, decl


def uncertainty(C):
    u = reg.MeasurementUncertainty()
    u.output_sigma = np.sqrt(np.diag(C)).tolist()
    u.covariance = C.ravel().tolist()
    return u


def controls(iterations=100, seconds=3600):
    return reg.FitControls(
        maximum_iterations=iterations, maximum_elapsed_time_seconds=seconds, function_tolerance=1e-10,
        parameter_tolerance=1e-10, gradient_tolerance=1e-8, workers=int(os.environ["AGENT_HEAVY_CORES"]),
    )


def starts():
    """Start 1: design starts with stage-3 offsets. Start 2: frozen A endpoint projected onto the 12-coordinate ties."""
    x = read("reactive-A-fit.json")["optimizer"]
    # Frozen chart order: PH sigma,u,Born,water-k,bic-k; PC sigma,u,Born,water-k; DC sigma,u,Born; HPC sigma,u; P3-P5.
    # Identical origins/scales for the kept coordinates, so their optimizer values transfer unchanged.
    return {1: [0.0] * 9 + list(NMR_OFFSETS), 2: [x[i] for i in (0, 1, 3, 4, 5, 6, 8, 12, 13, 14, 15, 16)]}


def fit(start):
    par = epcsaft.Parameters.from_mapping(document())
    rc, obs, C, _ = calibration(par, NMR_OFFSETS)
    coords, decl = chart(par, rc)
    x0 = starts()[start]
    record = dict(tag="A12", start=start, coordinates=decl, start_optimizer=x0, observations=len(obs))
    result = reg.fit(par, coords, obs, controls=controls(), uncertainty=uncertainty(C), singular_vectors=True, starts=[x0])[0]
    record.update(
        status=result.status, usable=result.usable, message=result.message, iterations=result.iterations,
        initial_cost=result.initial_cost, cost=result.final_cost, optimizer=list(result.optimizer),
        physical=list(result.physical), active_bounds=list(result.covariance.active_bounds),
        iteration_costs=list(result.iteration_costs),
    )
    if result.usable:
        save(f"reactive-A12-start{start}-endpoint.json", epcsaft.parameters.document_mapping(reg.fitted_parameters(par, result)))
    save(f"reactive-A12-start{start}-fit.json", jsonable(record))
    print(json.dumps({k: v for k, v in record.items() if k not in ("coordinates", "iteration_costs")}), flush=True)


def stability_rows(par, offsets, scale):
    """Design enforced states (#255 method): 121 NMR liquids at 0.1 MPa (at 1.05 times the candidate bubble pressure
    where the model bubble pressure exceeds 0.1 MPa), and each Hilliard feed as an all-liquid parent at 1.05 and 3 times
    its candidate bubble pressure. Returns (observation, key) pairs."""
    model = epcsaft.Mixture(par)
    trials = problem(laws_at([0, 0, 0]))
    trials.phases = [eq.Phase("trial-L", kind="liquid", support=list(par.component_ids)), eq.Phase("trial-V", kind="vapor", support=VAPOR)]
    opt = eq.StabilityOptions()
    opt.trials = trials._native(model).phases
    above = {m["row"] for m in read("reactive-A12-census.json")["summary"]["moved_to_bubble"]}
    rows = []
    for r in declarations(par=par, offsets=offsets)[5]:
        if r["group"] != 1:
            continue
        prob = problem(laws_at(offsets), float(r["T_K"]))
        prob.feed.values = {PZ: float(r["pz_mol"]), W: 1 / 0.0180153, CO2: float(r["co2_mol"])}
        if r["identity"] in above:
            pz = float(r["pz_mol"])
            bubble = pressure_problem(par, dict(T_K=r["T_K"], mPZ=pz, alpha_per_PZ=float(r["co2_mol"]) / pz, pCO2_kPa=100), offsets)
            rows.append((reg.stability(par, prob, scale=scale, options=opt, pressure_reference=bubble, pressure_ratio=1.05), r["identity"] + "|1.05"))
        else:
            rows.append((reg.stability(par, prob, scale=scale, options=opt), r["identity"]))
    for h in csv.DictReader((AN / "inputs/hilliard-d5.csv").open()):
        for c in (1.05, 3.0):
            prob = problem(laws_at(offsets), float(h["T_K"]))
            prob.feed.values = {PZ: 1.0, W: 1 / (0.0180153 * float(h["mPZ"])), CO2: float(h["alpha_per_PZ"])}
            rows.append((reg.stability(par, prob, scale=scale, options=opt, pressure_reference=pressure_problem(par, h, offsets), pressure_ratio=c),
                         f"Hilliard-{h['row']}|{c}"))
    return rows


def tally(predictions, keys):
    descent = [k for k, p in zip(keys, predictions, strict=True) if p and p.get("available") and p.get("value", 0) < 0]
    unavailable = [k for k, p in zip(keys, predictions, strict=True) if not (p and p.get("available"))]
    return dict(enforced=len(keys), descent=descent, unavailable=unavailable)


def fit_stable():
    """#255 penalty fit from the A12 endpoint: scales 1e-2 then 3e-3. A finite-search penalty; see diagnosis-308/refit_checks.py."""
    sys.path.insert(0, str(AN.parents[1] / "src"))
    from MEA.solvent_specification import stability_payload

    x = read("reactive-A12-start2-fit.json")["optimizer"]
    par0 = epcsaft.Parameters.from_mapping(document())
    rc, obs, C, _ = calibration(par0, NMR_OFFSETS)
    coords, decl = chart(par0, rc)
    for stage, s in enumerate((1e-2, 3e-3)):
        stab = stability_rows(par0, NMR_OFFSETS, s)
        # The native measurement matrix spans data rows only; stability rows keep unit weight (#255).
        u = uncertainty(C)
        u.output_sigma = list(u.output_sigma) + [1.0] * len(stab)
        result = reg.fit(par0, coords, obs + [o for o, _ in stab], controls=controls(), uncertainty=u,
                         singular_vectors=True, starts=[x])[0]
        keys = [k for _, k in stab]
        measured = [stability_payload(p) for p in result.stability_predictions][-len(stab):] if result.stability_predictions else [None] * len(stab)
        record = dict(tag="A12s", stage=stage, penalty_scale=s, coordinates=decl, start_optimizer=list(x), status=result.status,
                      usable=result.usable, message=result.message, iterations=result.iterations, cost=result.final_cost,
                      data_cost=result.data_cost, stability_cost=result.stability_cost, optimizer=list(result.optimizer),
                      active_bounds=list(result.covariance.active_bounds), enforced_keys=keys, stability=measured,
                      tally=tally(measured, keys))
        save(f"reactive-A12s-stage{stage}-fit.json", jsonable(record))
        print(json.dumps({k: v for k, v in record.items() if k not in ("coordinates", "stability", "enforced_keys")})[:1500], flush=True)
        if not result.usable:
            break
        save(f"reactive-A12s-stage{stage}-endpoint.json", epcsaft.parameters.document_mapping(reg.fitted_parameters(par0, result)))
        save("reactive-A12s-fit.json", jsonable(dict(record, start=f"stage{stage}")))
        if not record["tally"]["descent"] and not record["tally"]["unavailable"]:
            break
        x = list(result.optimizer)


def endpoint(tag):
    """Endpoint parameters and fitted P3-P5 offsets. A12 is the lower-cost usable start (calibration data only)."""
    if tag == "A":
        return epcsaft.Parameters.from_mapping(read("reactive-A-endpoint.json")), read("reactive-A-fit.json")["optimizer"][-3:], None
    if tag == "A12s":
        best = read("reactive-A12s-fit.json")
        return epcsaft.Parameters.from_mapping(read(f"reactive-A12s-{best['start']}-endpoint.json")), best["optimizer"][-3:], best
    fits = [read(f"reactive-A12-start{s}-fit.json") for s in (1, 2)]
    best = min((f for f in fits if f["usable"]), key=lambda f: f["cost"])
    par = epcsaft.Parameters.from_mapping(read(f"reactive-A12-start{best['start']}-endpoint.json"))
    return par, best["optimizer"][-3:], best


def phases(par, prob):
    model = epcsaft.Mixture(par)
    sol = eq.solve_equilibrium(model, prob)
    trials = problem(laws_at([0, 0, 0]))
    trials.phases = [
        eq.Phase("trial-L", kind="liquid", support=list(par.component_ids)),
        eq.Phase("trial-V", kind="vapor", support=VAPOR),
    ]
    opt = eq.StabilityOptions()
    opt.trials = trials._native(model).phases
    native = eq.stability_test(eq.compile_problem(model, prob), sol, opt)
    policy = tomllib.loads((AN.parent / "solvent_specification_mdea/B1-declarations.toml").read_text())["phase_policy"]
    report = dict(completed=native.completed, message=native.message, present_phases=jsonable(native.present_phases),
                  pressure_Pa=sol.pressure, trials=[], unresolved=[], dense=[], gas=[], ambiguous=[])
    for t in native.trials:
        r = {k: jsonable(getattr(t, k)) for k in ["seed", "evidence", "message", "resolved_descent", "quantities", "composition", "split_coordinates"]}
        r.update(kind=t.phase.kind.name, optimizer_success=t.optimizer.success)
        if t.resolved_descent and (not t.split_coordinates or not np.isfinite(t.split_coordinates[-1])):
            report["unresolved"].append(t.seed)
        if t.resolved_descent and t.split_coordinates:
            eta = float(np.exp(t.split_coordinates[-1]))
            r["packing_fraction"] = eta
            report["dense" if eta >= policy["packing_fraction_threshold"] else "gas"].append(t.seed)
            if policy["ambiguity_interval"][0] < eta < policy["ambiguity_interval"][1]:
                report["ambiguous"].append(t.seed)
        if t.evidence in ["unresolved", "indeterminate", "negative_plane_without_positive_donor"] or not t.optimizer.success:
            report["unresolved"].append(t.seed)
        report["trials"].append(r)
    report["passed"] = (
        native.completed and sol.requested_tolerance_met
        and {t.phase.kind.name for t in native.trials} == {"Liquid", "Vapor"}
        and not any(report[k] for k in ["unresolved", "dense", "gas", "ambiguous"])
    )
    report["requested_tolerance_met"] = sol.requested_tolerance_met
    return report


def nmr_phases(par, row, offsets):
    """Source NMR liquid at 0.1 MPa; if the model bubble pressure exceeds 0.1 MPa, at 1.05 times it instead."""
    prob = problem(laws_at(offsets), float(row["T_K"]))
    prob.feed.values = {PZ: float(row["pz_mol"]), W: 1 / 0.0180153, CO2: float(row["co2_mol"])}
    out = phases(par, prob)
    if out["gas"]:
        mPZ, alpha = float(row["pz_mol"]), float(row["co2_mol"]) / float(row["pz_mol"])
        bubble = eq.solve_equilibrium(
            epcsaft.Mixture(par), pressure_problem(par, dict(T_K=row["T_K"], mPZ=mPZ, alpha_per_PZ=alpha, pCO2_kPa=100), offsets)
        )
        assert bubble.requested_tolerance_met and bubble.pressure > 1e5, (row["row"], bubble.pressure)
        prob.P = 1.05 * bubble.pressure
        at_source = {k: out[k] for k in ("passed", "dense", "gas", "unresolved", "pressure_Pa")}
        out = phases(par, prob)
        out.update(model_bubble_pressure_Pa=bubble.pressure, at_0p1MPa=at_source)
    return out


def summarize_census(states):
    def count(cond):
        return sum(1 for s in states if cond(s))
    return dict(
        states=len(states),
        no_extra_phase=count(lambda s: s.get("passed")),
        undecided=count(lambda s: s.get("unresolved")),
        dense_split=[s["row"] for s in states if s.get("dense")],
        gas_split=[s["row"] for s in states if s.get("gas")],
        ambiguous=[s["row"] for s in states if s.get("ambiguous")],
        failed_other=[s["row"] for s in states if not s.get("passed") and not any(s.get(k) for k in ("unresolved", "dense", "gas", "ambiguous"))],
        moved_to_bubble=[dict(row=s["row"], bubble_kPa=s["model_bubble_pressure_Pa"] / 1000) for s in states if "model_bubble_pressure_Pa" in s],
    )


def nominal(m, levels):
    return min(levels, key=lambda v: abs(v - m))


def relative_summary(rows, key):
    out = {}
    for k in dict.fromkeys(key(r) for r in rows):
        e = np.array([r["relative_error"] for r in rows if key(r) == k])
        out[str(k)] = dict(n=len(e), MARE_percent=100 * float(np.mean(abs(e))), bias_percent=100 * float(np.mean(e)))
    return out


def holdout(par, offsets):
    """Frozen-endpoint score on Ermatchkov 2006 Tables 1-3 (52 rows). Never used for fitting or selection."""
    model, rows = epcsaft.Mixture(par), []
    for row in csv.DictReader(HOLDOUT.open()):
        prob = pressure_problem(par, row, offsets)
        y = reg.predict(model, pressure_observation(par, prob, row))
        p, obs, dp = y.value / 1000, float(row["pCO2_kPa"]), float(row["pCO2_total_uncertainty_kPa"])
        state = phases(par, prob)
        rows.append(dict(
            identity=f"Ermatchkov2006-T{row['table']}-{row['row']}", T_K=float(row["T_K"]), mPZ=float(row["mPZ"]),
            nominal_mPZ=nominal(float(row["mPZ"]), (1, 2, 2.75, 4)), alpha_per_PZ=float(row["alpha_per_PZ"]),
            observed_kPa=obs, total_uncertainty_kPa=dp, repeatability_kPa=float(row["pCO2_repeatability_kPa"]),
            calculated_kPa=p, available=y.status.name == "Available" and y.requested_tolerance_met,
            relative_error=p / obs - 1, log_ratio=float(np.log(p / obs)), scaled_residual=(p - obs) / dp,
            within_source_uncertainty=abs(p - obs) <= dp, outside_distance_kPa=max(0.0, abs(p - obs) - dp),
            phase_passed=state["passed"], undecided=bool(state["unresolved"]), dense=bool(state["dense"]), gas=bool(state["gas"]),
        ))
    z = np.array([r["scaled_residual"] for r in rows])
    summary = dict(
        rows=len(rows), all_available=all(r["available"] for r in rows),
        MARE_percent=100 * float(np.mean([abs(r["relative_error"]) for r in rows])),
        bias_percent=100 * float(np.mean([r["relative_error"] for r in rows])),
        RMS_scaled_residual=float(np.sqrt(np.mean(z * z))),
        within_source_uncertainty=sum(r["within_source_uncertainty"] for r in rows),
        phase_passed=sum(r["phase_passed"] for r in rows),
        by_temperature=relative_summary(rows, lambda r: r["T_K"]),
        by_temperature_and_concentration=relative_summary(rows, lambda r: f"{r['T_K']} K, ~{r['nominal_mPZ']} mol/kg"),
        within_by_temperature={str(t): sum(r["within_source_uncertainty"] for r in rows if r["T_K"] == t) for t in dict.fromkeys(r["T_K"] for r in rows)},
        excluding_393K=relative_summary([r for r in rows if r["T_K"] < 390], lambda r: "313-353 K"),
    )
    return rows, summary


def score(tag):
    par, offsets, best = endpoint(tag)
    model = epcsaft.Mixture(par)
    rc, obs, C, meta = calibration(par, offsets)
    preds = []
    for o in obs:
        y = reg.predict(model, o)
        assert y.status.name == "Available" and y.requested_tolerance_met, y.message
        preds.append(y.value)
    pred = np.array(preds)
    target = np.array([r["observed_fraction"] for r in meta])
    z = np.linalg.solve(np.linalg.cholesky(C), pred - target)
    records = [dict(r, calculated=float(y), difference=float(y - r["observed_fraction"]), whitened_residual=float(z[i]))
               for i, (r, y) in enumerate(zip(meta, pred, strict=True))]
    keys = list(dict.fromkeys(k for r in records for k in r))
    write_csv(f"reactive-{tag}-residuals.csv", [{k: r.get(k, "") for k in keys} for r in records])
    hp = [dict(r, relative_error=r["calculated"] / r["observed_fraction"] - 1) for r in records if r["group"] == "pressure"]
    record = dict(
        tag=tag, offsets=list(offsets), fit=best and {k: best[k] for k in ("start", "status", "message", "iterations", "cost", "active_bounds")},
        cost=float(z @ z / 2), NMR_RMS=float(np.sqrt(np.mean(z[:232] ** 2))), pressure_RMS=float(np.sqrt(np.mean(z[232:] ** 2))),
        hilliard=dict(
            MARE_percent=100 * float(np.mean([abs(r["relative_error"]) for r in hp])),
            bias_percent=100 * float(np.mean([r["relative_error"] for r in hp])),
            by_concentration=relative_summary(hp, lambda r: nominal(float(r["mPZ"]), (0.9, 2.0, 2.5, 3.6, 5.0))),
            by_temperature=relative_summary(hp, lambda r: round(float(r["T_K"]) - 273.15, -1)),
        ),
        carbamate_MAE={g: float(np.mean([abs(r["difference"]) for r in records if r["group"] == g])) for g in (1, 2)},
    )
    if tag == "A":
        # Support change check: retained stage-4 predictions used vapour [W, CO2, PZ].
        old = [float(r["calculated"]) for r in csv.DictReader((AN / "results/reactive-A-stage4-residuals.csv").open())]
        record["vapour_support_change_max_relative"] = float(np.max(np.abs(pred / np.array(old) - 1)[232:]))
        record["vapour_support_change_max_NMR"] = float(np.max(np.abs(pred - np.array(old))[:232]))
    states = []
    for r in meta:
        if r["group"] == 2:
            continue  # the f2 observation repeats the f1 liquid state
        try:
            out = nmr_phases(par, r, offsets) if r["group"] == 1 else phases(par, pressure_problem(par, r, offsets))
        except Exception as error:
            out = dict(passed=False, exception=type(error).__name__, message=str(error))
        out.update(row=r["row"], group=r["group"], T_K=r["T_K"])
        states.append(out)
        print(tag, "state", len(states), out["passed"], flush=True)
    record["census"] = summarize_census(states)
    save(f"reactive-{tag}-census.json", dict(summary=record["census"], states=jsonable(states)))
    rows, record["holdout"] = holdout(par, offsets)
    write_csv(f"holdout-{tag}.csv", rows)
    save(f"reactive-{tag}-record.json", jsonable(record))
    print(json.dumps({k: v for k, v in record.items() if k != "holdout"}), json.dumps(record["holdout"]), flush=True)


GROUPS = {1: "NMR PZCOO- + HPZCOO", 2: "NMR PZ(COO)2 2-", "pressure": "Hilliard pCO2"}


def fixed_chart(x):
    """Chart whose document and laws sit at optimizer x, so coordinates omitted from a fit stay at x."""
    par0 = epcsaft.Parameters.from_mapping(document())
    coords0, _ = chart(par0, calibration(par0, NMR_OFFSETS)[0])
    par = epcsaft.Parameters(reg.evaluate_coordinates(par0, coords0[:9], list(x[:9]), []).parameters, par0.component_ids, par0.site_ids)
    rc, obs, C, meta = calibration(par, x[9:])
    coords, decl = chart(par, rc)
    return par, coords, decl, obs, C, meta


def subset_fit(x, keep, path, tag):
    """#307 conditional/profile refit: coordinates outside `keep` held at x; 40 iterations, 2100 s."""
    par, coords, decl, obs, C, _ = fixed_chart(x)
    r = reg.fit(par, [coords[i] for i in keep], obs, controls=controls(40, 2100.0), uncertainty=uncertainty(C),
                singular_vectors=True, starts=[[x[i] for i in keep]])[0]
    cov = r.covariance
    out = dict(keep=keep, start=list(x), status=r.status, usable=r.usable, message=r.message, iterations=r.iterations,
               cost=r.final_cost, optimizer=list(r.optimizer), predictions=list(r.predictions),
               covariance=dict(status=cov.status, active_bounds=list(cov.active_bounds), optimizer=list(cov.optimizer),
                               variance_factor=cov.variance_factor))
    unc = AN / f"results/uncertainty-{tag}"
    unc.mkdir(exist_ok=True)
    (unc / path).write_text(json.dumps(jsonable(out), indent=2) + "\n")
    print(path, r.status, r.final_cost, flush=True)


def profile_points(best, decl):
    """Each bound coordinate moved 1, 5 and 10 % of its interval inward, as in #307."""
    x, points = best["optimizer"], []
    for i in best["active_bounds"]:
        q = decl[i]
        value = q["origin"] + q["scale"] * x[i]
        lo, hi = q["bounds"]
        sign = 1 if value - lo < hi - value else -1
        for f in (0.01, 0.05, 0.1):
            moved = list(x)
            moved[i] = (value + sign * f * (hi - lo) - q["origin"]) / q["scale"]
            points.append((i, f, moved))
    return points


def conditional(tag):
    _, _, best = endpoint(tag)
    keep = [i for i in range(12) if i not in best["active_bounds"]]
    subset_fit(best["optimizer"], keep, "conditional.json", tag)


def profile(tag, k):
    _, _, best = endpoint(tag)
    i, f, moved = profile_points(best, best["coordinates"])[k]
    subset_fit(moved, [j for j in range(12) if j != i], f"profile-{i}-{f}.json", tag)


def ranking(tag):
    """Conditional SE (bound coordinates fixed) and sensitivity ranking on the calibration states only (#307 method)."""
    sys.path.insert(0, str(AN.parent / "mea_parameter_bundle/calibration-misfit"))
    from refit import identifiability  # the #307 adopted-point conditional covariance
    from types import SimpleNamespace

    _, _, best = endpoint(tag)
    UNC = AN / f"results/uncertainty-{tag}"
    x = np.array(best["optimizer"])
    par, coords, decl, obs, C, meta = fixed_chart(x)
    d = reg.differentiate(par, coords, obs, optimizer=list(x))
    y = np.array(d.predictions)
    L = np.linalg.cholesky(C)
    G = np.array(d.optimizer_gradient).reshape(len(obs), 12)
    J = np.linalg.solve(L, np.array(d.residual_optimizer_gradient).reshape(len(obs), 12))
    r = np.linalg.solve(L, y - np.array([m["observed_fraction"] for m in meta]))
    scales = np.array([q["scale"] for q in decl])
    names = [q["name"] for q in decl]
    active = best["active_bounds"]
    free = [i for i in range(12) if i not in active]
    local = identifiability(SimpleNamespace(physical=list(decl[i]["origin"] + scales[i] * x[i] for i in range(12)),
                                            covariance=SimpleNamespace(active_bounds=active)),
                            J / scales, r, names, [q["bounds"][0] for q in decl], [q["bounds"][1] for q in decl])
    cond = json.loads((UNC / "conditional.json").read_text())
    movement = dict(zip([names[i] for i in free], np.array(cond["optimizer"]) - x[free]))
    native = cond["covariance"]
    # Measurement-covariance fits return source-scaled covariance (no factor); #307 scales by the residual variance.
    base = best.get("data_cost", best["cost"])  # penalty fits: data part only
    factor = native["variance_factor"] or 2 * base / (len(obs) - len(free))
    use_native = native["status"] == "available" and max(map(abs, movement.values())) <= 1e-4
    Cn = np.array(native["optimizer"]).reshape(len(free), len(free)) * factor if use_native else None
    se = np.sqrt(np.diag(Cn)) * scales[free] if use_native else np.array([local["conditional_standard_error"][names[i]] for i in free])
    Copt = Cn if use_native else np.array(local["conditional_correlation"]) * np.outer(se / scales[free], se / scales[free])
    group = np.array([str(m["group"]) for m in meta])
    rows = []
    for k, i in enumerate(free):
        delta = G[:, i] * se[k] / scales[i]
        changes = {GROUPS[g]: float(np.max(np.abs(delta[group == str(g)]) / np.maximum(np.abs(y[group == str(g)]), 1e-30))) for g in GROUPS}
        rows.append(dict(parameter=names[i], value=decl[i]["origin"] + scales[i] * x[i], SE_bound_fixed=float(se[k]), profile_step=None,
                         max_fractional_change=max(changes.values()), top=max(changes, key=changes.get), group_changes=changes))
    profiles = []
    for i, f, moved in profile_points(best, decl):
        p = json.loads((UNC / f"profile-{i}-{f}.json").read_text())
        changes = {GROUPS[g]: float(np.max(np.abs(np.array(p["predictions"])[group == str(g)] / y[group == str(g)] - 1))) for g in GROUPS}
        profiles.append(dict(parameter=names[i], fraction=f, fixed_value=decl[i]["origin"] + scales[i] * moved[i], status=p["status"],
                             delta_cost=p["cost"] - base, group_changes=changes))
        if f == 0.01:
            rows.append(dict(parameter=names[i], value=decl[i]["origin"] + scales[i] * x[i], SE_bound_fixed=None,
                             profile_step=scales[i] * (moved[i] - x[i]),
                             max_fractional_change=max(changes.values()), top=max(changes, key=changes.get), group_changes=changes))
    rows.sort(key=lambda q: q["max_fractional_change"], reverse=True)
    pressure = group == "pressure"
    band = np.sqrt(np.maximum(0, np.einsum("ij,jk,ik->i", G[:, free], Copt, G[:, free])))[pressure] / y[pressure]
    _, sv, vt = np.linalg.svd(J, full_matrices=False)
    out = dict(active=[names[i] for i in active], free=[names[i] for i in free], ranking_covariance="native conditional" if use_native else "endpoint conditional inverse-Jacobian",
               conditional_movement=movement, conditional_cost_change=cond["cost"] - base, residual_variance_factor=factor,
               endpoint_conditional=local, ranking=rows, profiles=profiles, hilliard_relative_SE=[float(band.min()), float(band.max())],
               singular_values=sv.tolist(), right_vectors=vt.tolist())
    (UNC / "ranking.json").write_text(json.dumps(jsonable(out), indent=2) + "\n")
    write_csv(f"uncertainty-{tag}/ranking.csv", [{k: v for k, v in q.items() if k != "group_changes"} for q in rows])
    print(json.dumps({k: out[k] for k in ("active", "ranking_covariance", "hilliard_relative_SE")}), flush=True)


if __name__ == "__main__":
    verify_wheel()
    command = sys.argv[1]
    if command == "fit":
        fit(int(sys.argv[2]))
    elif command == "fit-stable":
        fit_stable()
    elif command == "score":
        score(sys.argv[2])
    elif command == "conditional":
        conditional(sys.argv[2])
    elif command == "profile":
        profile(sys.argv[2], int(sys.argv[3]))
    else:
        ranking(sys.argv[2])
