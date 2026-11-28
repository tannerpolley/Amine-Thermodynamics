"""Derivative and property readbacks at one declared endpoint."""

import copy
import csv
import json
from math import exp, fsum, log, sqrt
from types import SimpleNamespace

import epcsaft
import numpy as np
from epcsaft import equilibrium as eq, regression as reg
from .records import RESULTS, read
from MEA.solvent_specification import conditional_information, deviation_statistics

from .model import P_REF, calculation_declaration, evaluate, parameter_values
from .phase import DENSITY_WINDOW, ERROR_TERMS, R, matched, physical, pressure_roots
from .wheel import ROOT, verify


def write_gibbs_derivative_summary():
    wheel = verify()
    folder = RESULTS / "shared/comparisons/properties/derivatives"
    paths = {path.name.removesuffix(".json.gz"): path
             for base in (folder, folder / "rebuild-441") for path in base.glob("*.json.gz")}
    records = {name: read(path) for name, path in sorted(paths.items(), key=lambda item: item[1].name)}
    if any(record["wheel"] != wheel for record in records.values()):
        raise ValueError("Gibbs derivative record uses another wheel")

    rows = []

    def summarize(name, inputs, comparison, admitted_field, discrepancy, arithmetic):
        record = records[inputs[0]]
        matching = ("T_K", "P_Pa", "endpoint_fingerprint", "apparent_amine_feed_mol")
        if any(records[key][field] != record[field] for key in inputs for field in matching):
            raise ValueError(f"Different conditions for the daughter inventories of {name}")
        candidates = []
        for steps in zip(*(records[key]["steps"] for key in inputs), strict=True):
            if all(discrepancy in step for step in steps):
                candidates.append((sum(step[discrepancy] for step in steps),
                                   sum(step[arithmetic] for step in steps),
                                   all(step.get(admitted_field) for step in steps)))
        admitted = [candidate for candidate in candidates if candidate[2]]
        used = admitted or (candidates if len(inputs) == 1 else [])
        if not used:
            return
        delta, arithmetic_error, _ = used[-1]
        span = max(step[0] for step in used) - min(step[0] for step in used)
        error = arithmetic_error + span
        scale = 1 if comparison == "volume" else record["apparent_amine_feed_mol"]
        rows.append(dict(
            state=name, comparison=comparison, temperature_K=record["T_K"], pressure_Pa=record["P_Pa"],
            pressure_basis=record.get("pressure_basis"),
            signed_error=delta / scale, estimated_error=error / scale, admitted_steps=len(admitted),
            disposition=("agreement within numerical error"
                         if len(admitted) >= 2 and abs(delta) <= error else "undecided"),
            records=[paths[key].relative_to(ROOT).as_posix() for key in inputs],
        ))
        if comparison == "volume" and len(inputs) == 1:
            volume = record["center"]["volume_m3"]
            rows[-1].update(relative_error=delta / volume, relative_estimated_error=error / volume)

    states = [(name, [name]) for name, record in records.items() if record.get("steps")]
    states.extend((f"{mode} MDEA daughter-inventory sum", [f"{mode}-MDEA-daughter-{i}" for i in (1, 2)])
                  for mode in ("fixed-at-old", "selected"))
    for state, inputs in states:
        summarize(state, inputs, "volume", "volume_admitted",
                  "signed_volume_error_m3", "volume_arithmetic_error_m3")
        summarize(state, inputs, "Eq. 12", "enthalpy_admitted",
                  "eq12_minus_Gibbs_Helmholtz_J", "caloric_arithmetic_error_J")
    path = ROOT / "analyses/amines/results/shared/properties/gibbs-derivatives.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(wheel=wheel, rows=rows), indent=2) + "\n")


def water_calibration(route, point):
    """Evaluate the adopted water coefficients on W against the IAPWS-95 assessment grid."""
    from collections import Counter
    from scipy.optimize import brentq

    bundle = ROOT / "analyses/mea_parameter_bundle"
    design = read(bundle / "data/input/fit-campaigns/water-124.json")
    reference = bundle / "results/density-cp-160/cp-124-assessment/iapws95-reference.csv"
    targets = read(bundle / "results/water-124/lambda-0.1-A/targets.json")
    counts = Counter(row["kind"] for row in targets)
    values = parameter_values(point["parameters"])
    coefficients = {q["identity"]: values[q["identity"]] for q in design["coordinates"]}
    spec = route.bind(point)
    i = spec.parameters.component_ids.index("water")
    thermal = type(spec.thermal)(spec.thermal.standard_pressure, [spec.thermal.component_intervals[i]])
    model = epcsaft.Pure(epcsaft.Parameters.from_mapping(point["parameters"], components=["water"]),
                         thermochemistry=thermal)
    mass = design["molar_mass_kg_mol"]
    metrics = dict(rho="rho_kg_m3", cp="cp_kJ_kg_K", psat="psat_Pa",
                   saturated_liquid_rho="saturated_liquid_rho_kg_m3")
    rows = []
    with reference.open(newline="") as stream:
        for source in csv.DictReader(stream):
            if source["grid"] == "atmospheric-controls":
                continue
            T, P = float(source["T_K"]), float(source["P_Pa"])
            observed = {q: float(source[key]) for q, key in metrics.items()}
            state = model.state(T, P=P, phase="liquid")
            problem = eq.Problem(T=T, P=eq.Free(observed["psat"]), feed=eq.Amounts({"water": 1.}),
                phases=[eq.Phase("L", kind="liquid", composition_guess=(1.,)),
                        eq.Phase("V", kind="vapor", amount=eq.Pinned(0.), composition_guess=(1.,))],
                row_tolerance=1e-10)
            saturation = eq.solve_equilibrium(model, problem)
            predicted = dict(rho=state.molar_density * mass,
                             cp=state.total_isobaric_heat_capacity / (mass * 1000),
                             psat=saturation.pressure if saturation.requested_tolerance_met else None,
                             saturated_liquid_rho=saturation.molar_densities[0] * mass
                             if saturation.requested_tolerance_met else None)
            rows.append(dict(grid=source["grid"], T_K=T, P_Pa=P, observed=observed, predicted=predicted,
                             saturation_tolerance_met=saturation.requested_tolerance_met,
                             saturation_message=saturation.message))
    T, P = 393.15, P_REF
    liquid = model.state(T, P=P, phase="liquid")
    vapor = model.state(T, P=P, phase="vapor")
    slope = lambda rho: model.state(T, rho=rho).pressure_density_derivative
    spinodal = brentq(slope, 0.75 * liquid.molar_density, liquid.molar_density)
    roots = dict(T_K=T, P_Pa=P, density_mol_m3=liquid.molar_density,
                 vapor_density_mol_m3=vapor.molar_density, spinodal_density_mol_m3=spinodal,
                 dP_drho_liquid=liquid.pressure_density_derivative, dP_drho_spinodal=slope(spinodal),
                 delta_G_liquid_minus_vapor_J_mol=R * T *
                 (liquid.log_fugacity_coefficient[0] - vapor.log_fugacity_coefficient[0]),
                 density_margin_mol_m3=liquid.molar_density - spinodal)
    return dict(reference=reference.relative_to(ROOT).as_posix(), coefficients=coefficients, rows=rows,
                fitted_rows=dict(psat=counts["EquilibriumPressure"], cp=counts["IsobaricHeatCapacity"]),
                roots=roots)


def endpoint_diagnostics(spec, fit_replay, point, controls):
    verify()
    declared = point["coordinates"]
    native = spec.coordinates()
    rows = spec.inputs["observations"]["fitted"]
    ev = reg.differentiate(
        spec.parameters,
        native,
        [spec.observation(q) for q in rows],
        optimizer=[0.0] * len(native),
        thermochemistry=spec.thermal,
    )
    values = dict(derivative_statuses=[q.name for q in ev.statuses])
    if fit_replay["cost"] is None or any(q.name != "Available" for q in ev.statuses):
        return values
    residual = np.array([q["weighted_residual"] for q in fit_replay["rows"]])
    J = spec.whiten(np.array(ev.residual_optimizer_gradient).reshape(len(rows), len(native)))
    scale = np.array([q.scale for q in native])
    width = np.array([q.upper - q.lower for q in native])
    grad = (J * (width / scale)).T @ residual
    projected = grad.copy()
    active = {}
    for i, q in enumerate(native):
        side = (
            "lower"
            if q.origin - q.lower <= 1e-6 * q.scale
            else "upper"
            if q.upper - q.origin <= 1e-6 * q.scale
            else None
        )
        if side:
            active[declared[i]["identity"]] = side
            if (side == "lower" and grad[i] > 0) or (side == "upper" and grad[i] < 0):
                projected[i] = 0.0
    lower, upper = (np.array([getattr(q, k) - q.origin for q in native]) / scale for k in ("lower", "upper"))
    optimizer_norm = float(np.max(np.abs(np.clip(-grad * scale / width, lower, upper))))
    values.update(
        jacobian_bound_normalized=(J * (width / scale)).tolist(),
        gradient=grad.tolist(),
        projected_gradient=projected.tolist(),
        projected_gradient_inf=float(np.max(np.abs(projected))),
        active_bounds=active,
        optimizer_projected_gradient_inf=optimizer_norm,
        stationarity_met=optimizer_norm <= controls["gradient_tolerance"],
        maximum_prediction_relative_difference=max(
            abs(v - q["value"]) / max(1.0, abs(q["value"]))
            for v, q in zip(ev.predictions, fit_replay["rows"], strict=True)
        ),
    )
    ids = [q["identity"] for q in declared]
    result = SimpleNamespace(
        physical=[q.origin for q in native],
        covariance=SimpleNamespace(active_bounds=[ids.index(i) for i in active]),
    )
    try:
        values["uncertainty"] = conditional_information(
            result,
            J / scale,
            residual,
            ids,
            [q.lower for q in native],
            [q.upper for q in native],
        )
    except np.linalg.LinAlgError as exc:
        values["uncertainty_refusal"] = str(exc)
    return values


def marks(route, T, problem=None):
    used = {r.name for r in problem.reactions} if problem is not None else set(route.config["reaction_ranges_K"])
    ranges = route.config["reaction_ranges_K"]
    return {
        name: (
            "reaction not used"
            if name not in used
            else "source range unknown"
            if ranges.get(name) is None
            else "temperature unavailable"
            if T is None
            else not ranges[name][0] <= T <= ranges[name][1]
        )
        for name in used | ranges.keys()
    }


def property_rows(route, point, fitted=None):
    spec, predictions = route.bind(point), []
    fitted = {} if fitted is None else {row["identity"]: row for row in fitted}
    for role in ("fitted", "comparisons"):
        for record in spec.inputs["observations"][role]:
            prediction = fitted.get(record["identity"]) if role == "fitted" else None
            if prediction is None:
                prediction = spec.prediction(record)
            problem = spec.problems[record.get("problem", record.get("initial"))]
            key = json.dumps(calculation_declaration(problem), sort_keys=True) if isinstance(problem.T, eq.Free) else None
            predictions.append((role, record, problem, key, prediction))
    # The paired boiling-temperature and vapor-composition observations have the same problem declaration.
    temperatures = {
        key: prediction["value"]
        for _, record, _, key, prediction in predictions
        if key is not None and record.get("kind") == "temperature" and prediction["status"] == "Available"
    }
    output = []
    for role, record, problem, key, prediction in predictions:
        T = temperatures.get(key) if key is not None else problem.T
        output.append(dict(
            prediction,
            role=record.get("role", "fitted" if role == "fitted" else "not fitted"),
            T_K=T,
            outside_ranges=marks(route, T, problem),
        ))
    summary = []
    for group, role, unit in sorted({(r["group"], r["role"], r.get("unit") or "unit unspecified") for r in output}):
        for name in {name for r in output for name in r["outside_ranges"]}:
            dispositions = [False, True, "source range unknown", "reaction not used"]
            if any(r["outside_ranges"].get(name) == "temperature unavailable" for r in output):
                dispositions.append("temperature unavailable")
            for outside in dispositions:
                rows = [
                    r
                    for r in output
                    if (
                        r["group"],
                        r["role"],
                        r.get("unit") or "unit unspecified",
                        r["outside_ranges"].get(name, "reaction not used"),
                    )
                    == (group, role, unit, outside)
                ]
                pairs = [
                    (r["observed"], r["value"])
                    for r in rows
                    if r.get("value") is not None and r.get("status") == "Available"
                ]
                summary.append(
                    dict(
                        group=group,
                        role=role,
                        unit=unit,
                        range_name=name,
                        outside_range=outside,
                        rows=len(rows),
                        available=len(pairs),
                        statistics=deviation_statistics(pairs, unit) if pairs else None,
                    )
                )
    return dict(rows=output, deviations=summary, wheel=verify())


def parameter_changes(baseline, trial):
    """Compare optimizer coordinates on the reported fit's reference chart."""
    before = {q["identity"]: q for q in baseline["endpoint"]["coordinates"]}
    changes = {}
    for q in trial["endpoint"]["coordinates"]:
        key = q["identity"]
        prior = before.get(key)
        values = {}
        for side, coordinate, record in (("before", prior, baseline), ("after", q, trial)):
            if coordinate is None:
                values[side] = None
                continue
            diagnostics = record["diagnostics"]
            errors = diagnostics.get("uncertainty", {}).get("conditional_standard_error", {})
            value = coordinate["origin"]
            if coordinate.get("kind") == "reaction_enthalpy_shift":
                # The endpoint recenters Δh at zero and translates both bounds by the fitted shift.
                value = prior["bounds"][0] - coordinate["bounds"][0]
            values[side] = dict(value=value, standard_error=errors.get(key),
                                bound=diagnostics.get("active_bounds", {}).get(key))
        reference = values["before"]
        change = values["after"]["value"] - reference["value"] if reference is not None else None
        error = reference["standard_error"] if reference is not None else None
        changes[key] = dict(**values, change=change, change_over_reported_se=change / error if error else None)
    return changes


def fixed_r4_properties(reported, route, point, folder):
    """Compare the fixed and fitted R4 calibrations on identical observations."""
    from .fit import fingerprint, retained_endpoint

    _, baseline = retained_endpoint(reported)
    fit_folder = reported["retained"]
    retained = read(fit_folder.parent / "properties/summary.json.gz")
    if retained["endpoint_fingerprint"] != baseline["endpoint_fingerprint"]:
        raise ValueError("Reported properties belong to another endpoint")
    selected = read(folder / "selection.json")
    trial = read(folder / f'{selected["selected"]}.json.gz')
    original = read(fit_folder / f'{baseline["selected"]}.json.gz')
    result = property_rows(route, point, trial["replay"]["rows"])
    before = {row["identity"]: row for row in retained["rows"]}
    groups = {}
    for row in result["rows"]:
        prior = before[row["identity"]]
        fields = ("observed", "role", "unit", "basis")
        if any(prior[k] != row[k] for k in fields):
            raise ValueError(f'{row["identity"]}: reported and fixed R4 observations differ')
        # AMP's NMR group contains distinct Ciftja observables.
        observable = row["basis"]
        if isinstance(observable, dict):
            observable = ", ".join(observable.get("arguments", {}).get("species", ()))
        key = row["group"], row["role"], row["unit"], observable
        groups.setdefault(key, []).append((prior, row))
    statistics = []
    for (group, role, unit, observable), pairs in sorted(groups.items()):
        available = [(a, b) for a, b in pairs if a["status"] == b["status"] == "Available"]
        statistics.append(dict(group=group, role=role, unit=unit, observable=observable,
                               rows=len(pairs), matched_available=len(available), **{
            name: deviation_statistics([(pair[i]["observed"], pair[i]["value"]) for pair in available], unit)
            if available else None for i, name in enumerate(("reported", "fixed_r4"))
        }))
    result.update(comparison=dict(
        reported_endpoint_fingerprint=baseline["endpoint_fingerprint"],
        endpoint_fingerprint=fingerprint(point),
        objective={"reported": baseline["cost"], "fixed_r4": selected["cost"]},
        statistics=statistics,
        coordinates=parameter_changes(original, trial),
        reaction_correlations={name: next(
            r["correlation"] for r in attempt["endpoint"]["reactions"]["aqueous"] if r["name"] == "carbamate-hydrolysis"
        ) for name, attempt in (("reported", original), ("fixed_r4", trial))},
        **{field: {name: record["diagnostics"][field]
                   for name, record in (("reported", original), ("fixed_r4", trial))}
           for field in ("active_bounds", "optimizer_projected_gradient_inf")},
    ))
    return result


def control_properties(amine, reported, declaration, folder):
    """Compare the control and reported endpoint on matched pressure and species observations."""
    from collections import defaultdict

    from .fit import bind_fit, is_pressure, retained_endpoint
    from .mea import pressure_statistics

    point, selected = retained_endpoint(declaration | {"retained": folder})
    trial = read(folder / f'{selected["selected"]}.json.gz')
    _, original = retained_endpoint(reported)
    baseline = read(reported["retained"] / f'{original["selected"]}.json.gz')
    retained = reported["retained"].parent / "properties"
    retained_properties = read(retained / "summary.json.gz")
    if retained_properties["endpoint_fingerprint"] != original["endpoint_fingerprint"]:
        raise ValueError("Reported properties belong to another endpoint")
    comparisons = {r["identity"]: r for r in retained_properties["rows"]}
    spec = bind_fit(declaration, point)
    fitted_before, fitted_after = ({r["identity"]: r for r in attempt["replay"]["rows"]}
                                   for attempt in (baseline, trial))
    pressures, species, loaded = defaultdict(list), defaultdict(list), defaultdict(list)
    if amine == "mea":
        from . import mea

        templates, population = mea.pressure_inputs(mea.PRESSURE_INPUTS)
    for role in ("fitted", "comparisons"):
        records = spec.inputs["observations"][role]
        for row in records:
            pressure = is_pressure(row)
            args = row["arguments"]
            if not pressure and not (declaration.get("water_anion_intercepts")
                                     and row["kind"] in ("mole_fraction", "amount_ratio")
                                     and args.get("phase") in ("L", "mea-nine-species-liquid")):
                continue
            identity = row["identity"]
            if role == "fitted":
                before, after = fitted_before[identity], fitted_after[identity]
            else:
                before, after = comparisons[identity], spec.prediction(row)
            pair = dict(before=before, after=after)
            if pressure:
                source = row["group"]
                if amine == "mea" and source == "common149":
                    source = population[identity]["source_key"]
                pressures[(role, source, row["kind"])].append(pair)
                if source != "Kiepe" and spec.problems[row["problem"]].feed.values.get("carbon-dioxide", 0) > 0:
                    loaded[(role, row["kind"])].append(pair)
            else:
                species[(role, row["group"], row["kind"], tuple(args["species"]))].append(pair)

    carbonate = {}
    if amine == "mea":
        expanded = read(retained / "expanded-pressure.json.gz")
        legacy, added = mea.pressure_additions(spec, templates, population)
        prior = {r["identity"]: r for r in expanded["rows"]}
        held = [*expanded["hot_wagner"], *read(retained / "wagner.json.gz")["rows"],
                *(row for row in read(retained / "off-window.json.gz")["rows"] if row["group"] == "Aronu2011")]
        pairs = [(prior[row["identity"]], after) for row, after in zip(added, evaluate(spec, added), strict=True)]
        pairs.extend(zip(held, mea.refresh_pressure_rows(spec, legacy[0], held), strict=True))
        for before, after in pairs:
            pair = dict(before=before, after=after)
            pressures[("comparisons", before["row"]["source"], "partial_pressure")].append(pair)
            loaded[("comparisons", "partial_pressure")].append(pair)
        if declaration.get("water_anion_intercepts"):
            before = read(retained / "mea-comparisons.json.gz")["carbonate_share"]
            after = mea.reported_carbonate_shares(spec, before)
            for side, rows in (("before", before), ("after", after)):
                ratios = [r["value"] / r["observed"] for r in rows
                          if r["status"] == "Available" and r["value"] > 0 and r["observed"] > 0]
                carbonate[side] = dict(rows=rows, geometric_mean_ratio=exp(fsum(map(log, ratios)) / len(rows))
                                       if len(ratios) == len(rows) else None)
    elif amine == "mdea":
        from . import mdea

        row = next(row for row in mdea.kuranov_rows(mdea.FIT_SETS["published"]["observations"])
                   if row["row"] == mdea.FIT_SETS["published"]["restored_row"])
        record = mdea.replay_records(spec, dict(row, alpha=row["m_co2"] / row["m_mdea"]))[-1]
        pair = dict(before=retained_properties["additional_Kuranov_72"], after=spec.prediction(record))
        pressures[("comparisons", "Kuranov-393K", "pressure")].append(pair)
        loaded[("comparisons", "pressure")].append(pair)

    def pressure_summary(rows):
        return dict(rows=rows, **{side: pressure_statistics([pair[side] for pair in rows])
                                  for side in ("before", "after")})

    def species_summary(rows):
        results = {}
        for side in ("before", "after"):
            errors = [r["value"] - r["observed"] for pair in rows if (r := pair[side])["status"] == "Available"
                      and r["requested_tolerance_met"]]
            results[side] = dict(available=len(errors), rmse=sqrt(fsum(e**2 for e in errors) / len(errors))
                                 if errors else None)
        return dict(rows=rows, **results)

    parameters = parameter_changes(baseline, trial)
    water_anion = {}
    if declaration.get("water_anion_intercepts"):
        from . import salt

        laws = read(RESULTS / "move/salt/sodium-salts/fit/summary.json.gz")["laws_at_record_reference"]
        for ion in (salt.HCO3, salt.CO3):
            identity = salt.LAWS[ion]
            law = laws[ion]
            values = {}
            for side, record in (("before", baseline), ("after", trial)):
                mapping = record["endpoint"]["parameters"]
                (coefficient,) = (c for pair in mapping["pairs"] for c in pair["coefficients"]
                                  if c["identity"] == identity)
                reference = coefficient["temperature_law"]["reference_temperature"]["magnitude"]
                a0, a1 = (parameter_values(mapping)[f"{identity}/a{i}"] for i in (0, 1))
                if a1 != law["a1"]:
                    raise ValueError(f"{ion}: expected the same slope as the sodium-salt fit")
                values[side] = a0 + a1 * (law["t_ref"] - reference)
            water_anion[ion] = dict(reference_K=law["t_ref"], a0_salt=law["a0"], a1=law["a1"],
                                    a0_before=values["before"], a0_after=values["after"],
                                    standard_error=parameters[f"{identity}/a0"]["after"]["standard_error"],
                                    bound=parameters[f"{identity}/a0"]["after"]["bound"])
    return dict(wheel=verify(), endpoint_fingerprint=selected["endpoint_fingerprint"],
                reported_endpoint_fingerprint=original["endpoint_fingerprint"],
                objective_before=original["cost"], objective_after=selected["cost"], parameters=parameters,
                pressure=[dict(role=role, source=source, kind=kind, **pressure_summary(rows))
                          for (role, source, kind), rows in sorted(pressures.items())],
                loaded_pressure=[dict(role=role, kind=kind, **pressure_summary(rows))
                                 for (role, kind), rows in sorted(loaded.items())],
                speciation=[dict(role=role, source=source, kind=kind, species=names, **species_summary(rows))
                            for (role, source, kind, names), rows in sorted(species.items())],
                carbonate_share=carbonate, water_anion_intercepts=water_anion)


def curve_rows(route, point, declarations=None):
    spec, output = route.bind(point), []
    for row in route.load(route.config["curve_rows"]) if declarations is None else declarations:
        record = copy.deepcopy(row["observation"])
        for key, declaration in row["problems"].items():
            spec.problems[key] = spec.problem(declaration["template"], declaration["bindings"])
        record.update(
            observation_parameters=spec.parameter_sha256,
            temperature_domain=route.config["calculation_interval_K"],
        )
        T = spec.problems[record.get("problem", record.get("initial"))].T
        assert route.config["calculation_interval_K"][0] <= T <= route.config["calculation_interval_K"][1]
        output.append(
            dict(
                spec.prediction(record),
                curve=row["curve"],
                loading=row["loading"],
                T_K=T,
                outside_ranges=marks(
                    route,
                    T,
                    spec.problems[record.get("problem", record.get("initial"))],
                ),
            )
        )
    return dict(rows=output, wheel=verify())


def amp_isotherms(route, point):
    groups = {"loaded-pressure", "hartono-2021-supplemental", "tong"}
    declarations = [row for row in route.load(route.config["curve_rows"])
                    if row["observation"]["group"] in groups]
    return curve_rows(route, point, declarations)["rows"]


def mdea_speciation_curves(route, point):
    spec = route.bind(point)
    amine = route.config["amine"]
    series = {}
    for row in spec.inputs["observations"]["comparisons"]:
        if not row["group"].startswith("Bottinger-"):
            continue
        parent = spec.problems[row["problem"]]
        feed = parent.feed.values
        key = row["group"], parent.T, feed["water"] / feed[amine], parent.P
        series.setdefault(key, []).append((feed["carbon-dioxide"] / feed[amine], row))
    curves = []
    for (group, T, stock, pressure), rows in sorted(series.items()):
        first, last = min(a for a, _ in rows), max(a for a, _ in rows)
        if first == last:
            continue
        parent = spec.problems[rows[0][1]["problem"]]
        for i, loading in enumerate(np.linspace(first, last, 21)):
            key = f"curve:{group}:{T}:{stock}:{pressure}:{i}"
            problem = copy.copy(parent)
            feed = parent.feed.values
            problem.feed = eq.Amounts(dict(feed, **{"carbon-dioxide": float(loading) * feed[amine]}))
            spec.problems[key] = problem
            result = spec.prediction(dict(rows[0][1], identity=key, problem=key))
            curves.append(dict(identity=key, group=group, T_K=T, water_per_mole_amine=stock,
                               pressure_Pa=pressure, loading=float(loading), value=result["value"],
                               status=result["status"], message=result["message"],
                               requested_tolerance_met=result["requested_tolerance_met"]))
    return curves


def reported_curves(amine, route, point):
    from .fit import fingerprint

    folder = RESULTS / amine / "reported/properties"
    if amine == "mea":
        from .mea import reported_curves as mea_curves

        return mea_curves(route, point)
    if amine == "amp":
        return dict(curves=amp_isotherms(route, point))
    if amine == "dea":
        groups = {"Lawson", "Lawson-394K", "SeoHong", "Lal"}
        declarations = [row for row in route.load(route.config["curve_rows"])
                        if row["observation"]["group"] in groups]
        retained = read(folder / "DEA/property-comparisons/selected.json.gz")["curves"]
    elif amine == "mdea":
        folder = folder / "curves"
        templates = read(folder / "templates.json")
        spec = route.bind(point)
        observations = {(row["group"], fingerprint(row["row"])): row for role in ("fitted", "comparisons")
                        for row in spec.inputs["observations"][role]}
        declarations = []
        for row in read(folder / "population.json.gz")["rows"]:
            group = row["group"]
            _, T, water = row["curve"].split(":")
            source = observations[group, fingerprint(row["row"])]
            (declared,) = templates[group].values()
            if row["basis"] != source["basis"] or declared["template"] != "loaded-bubble":
                raise ValueError(f"Changed curve declaration for {row['identity']}")
            key = row["identity"] + ":problem"
            base = spec.problems[source["problem"]]
            bindings = dict(declared["bindings"], T=float(T), P=base.P.guess, water=float(water), alpha=row["loading"])
            declarations.append(dict(curve=row["curve"], loading=row["loading"],
                observation=dict(source, identity=row["identity"], problem=key, observed=row["observed"]),
                problems={key: dict(template=declared["template"], bindings=bindings)}))
        retained = [row for path in sorted(folder.glob("batch-*.json.gz")) for row in read(path)["rows"]]
    else:
        return {}
    fresh = curve_rows(route, point, declarations)["rows"]
    key = lambda row: (row["curve"], row["identity"], row["loading"])
    result = dict(curves=fresh, curve_differences=curve_differences(retained, fresh, key))
    if amine == "mdea":
        result["speciation_curves"] = mdea_speciation_curves(route, point)
    return result


def curve_differences(retained, fresh, key):
    def signature(row):
        value = row["value"]
        return (row["status"], row.get("requested_tolerance_met"), (row.get("cause") or "").split(":", 1)[0],
                row.get("unit"), None if value is None else f"{value:.4g}")

    before, after = ({key(row): signature(row) for row in rows} for rows in (retained, fresh))
    if len(before) != len(retained) or len(after) != len(fresh):
        raise ValueError("Curve row keys are not unique")
    return [dict(key=k, retained=before.get(k), replayed=after.get(k))
            for k in sorted(before.keys() | after.keys(), key=repr) if before.get(k) != after.get(k)]


def observable(kind: str, phase: int, component: int = 0, prop: object | None = None) -> object:
    kind_value = getattr(eq.SolvedStateObservableKind, kind)
    if prop is None:
        return eq.SolvedStateObservable(kind_value, phase, component)
    return eq.SolvedStateObservable(kind_value, phase, component, prop)


def first_actions(model: object, problem: object, result: object, observables: list, directions: list) -> list:
    width = len(model.component_ids)
    batches = eq.solved_state_first_actions(eq.compile_problem(model, problem), result, observables, [
        eq.SolvedStateActionDirection(d_t, d_p, feed or [0.0] * width, []) for d_t, d_p, feed in directions])
    for batch in batches:
        for item in batch.results:
            if item.status.name != "Available":
                raise RuntimeError(f"{item.observable}: {item.status.name} {item.diagnostic_message}")
    return [[(item.value, item.action) for item in batch.results] for batch in batches]


def anchored_offsets(anchor_model, thermal, declaration, T, unanchored):
    """Use the native reaction contractions and independently bind the neutral caloric gauge."""
    supplied = np.array([bool(x) for x in thermal.component_intervals])
    nu = np.array([q.stoichiometry for q in declaration.reactions])
    offsets = np.zeros(len(supplied))
    P0 = thermal.standard_pressure
    neutral = {}
    for i in np.flatnonzero(supplied):
        composition = np.zeros(len(supplied))
        composition[i] = 1.
        state = anchor_model.state(T,rho=P0/(R*T),x=composition,derived_properties=True)
        h,s = state.ideal_enthalpy,state.ideal_entropy
        if h is None or s is None:
            raise ValueError(f'Caloric anchor unavailable for {anchor_model.component_ids[i]}')
        offsets[i] = (h-T*s)/(R*T)+log(R*T/P0)
        neutral[anchor_model.component_ids[i]] = dict(h_J_mol=h,s_J_mol_K=s,offset_over_RT=offsets[i])
    # The retained neutral anchors determine the reference on all conserved
    # neutral components. The remaining charge gauge cancels in each phase.
    contraction = nu @ np.asarray(unanchored)
    offsets[~supplied] = np.linalg.lstsq(nu[:,~supplied],contraction-nu @ offsets,rcond=None)[0]
    return offsets,neutral,(nu @ offsets-contraction).tolist()


def solve(spec, model, anchor_model, thermal, declaration, seed=None):
    if seed is not None:
        phases = declaration.phases
        for i, phase in enumerate(phases):
            phase.composition_guess = [seed.phase_mole_fractions(i)[j] for j in phase.support]
            phase.packing_guess = seed.packing_fractions[i]
        declaration.phases = phases
    result = eq.solve_equilibrium(model, declaration, start=seed if seed and len(seed.amounts)==len(declaration.phases) else None)
    row = dict(T_K=result.temperature,P_Pa=result.pressure,solver=result.message,
               admitted=False, requested_tolerance_met=result.requested_tolerance_met)
    if not result.requested_tolerance_met:
        return row, result
    checks = physical(spec, declaration, result)
    row['convergence_message'] = result.message
    row.update(checks)
    T,P = result.temperature,result.pressure
    compiled = eq.compile_problem(model,declaration)
    standard = eq.stability_test(compiled, result)
    unanchored = standard.standard_over_rt
    b,neutral,contraction_error = anchored_offsets(anchor_model,thermal,declaration,T,unanchored)
    assert all(activity.reference_pressure_pa==P_REF for activity in eq.reaction_activities(model,result))
    values = []
    for i,(n,rho) in enumerate(zip(result.amounts,result.molar_densities,strict=True)):
        x = result.phase_mole_fractions(i)
        state = model.state(T,rho=rho,x=x)
        eos = n*R*T*(state.residual_helmholtz + P/(rho*R*T) - 1 + fsum(
            v*log(v*rho) for v in x if v>0))
        standard_g = n*R*T*fsum(v*bb for v,bb in zip(x,b,strict=True) if v>0)
        roots = pressure_roots(model,T,P,x,rho)
        admitted_roots = matched(roots,declaration.row_tolerance)
        continued_dense = (seed is not None and state.pressure_density_derivative>0
                           and abs(log(rho/seed.molar_densities[i]))<=DENSITY_WINDOW)
        values.append(dict(amount_mol=n,x=x,rho_mol_m3=rho,roots=roots,volume_m3=n/rho,
                           eos_G_J=eos,standard_G_J=standard_g,pressure_slope=state.pressure_density_derivative,
                           H_res_J=n*state.residual_enthalpy,
                           continued_dense=continued_dense,
                           liquid_root=any(q['returned']=='liquid' for q in admitted_roots),
                           energy_error_J=n*R*T*fsum(standard.present_phases[i][k] for k in ERROR_TERMS)))
    row.update(values=values,b=b,unanchored_b=unanchored,neutral_caloric_anchors=neutral,
               reaction_contraction_error_over_RT=contraction_error,
               G_J=fsum(q['eos_G_J']+q['standard_G_J'] for q in values),
               volume_m3=fsum(q['volume_m3'] for q in values),
               G_error_J=fsum(q['energy_error_J'] for q in values),reference_pressure_Pa=P_REF)
    row['admitted'] = (checks['physical_checks_pass'] and
                       all(q['amount_mol']>0 and (q['liquid_root'] or q['continued_dense']) for q in values))
    observables = [observable('SystemEnthalpy',0)]+[
        observable('PhaseProperty',i,prop=epcsaft.PropertyObservable.TotalEntropy) for i in range(len(values))]
    try:
        h,*entropy = [value for value,_ in first_actions(model,declaration,result,observables,
                                                        [(0.,0.,[0.]*len(b))])[0]]
        row.update(engine_H_J=h,engine_H_over_T_minus_S_J_K=h/T-fsum(
            s*q['amount_mol'] for s,q in zip(entropy,values,strict=True)))
    except (ValueError,RuntimeError) as error:
        row['caloric_refusal'] = str(error)
    return row,result


def derivatives(spec, model, thermal, problem, T, P, amine_feed, starting_solution=None):
    P0 = thermal.standard_pressure
    zero = epcsaft.IdealInterval(250.,500.,True,True,
        epcsaft.IdealCorrelation(epcsaft.IdealPolynomial([0.],350.,0.,0.),P0))
    # Native bulk ideal output requires intervals in every slot. The inserted
    # zero records have zero mole fraction in every pure-anchor call.
    anchor_model = epcsaft.Mixture(spec.parameters,thermochemistry=epcsaft.ThermochemistryRecord(
        P0,[q or [zero] for q in thermal.component_intervals]))
    center, seed = solve(spec,model,anchor_model,thermal,problem,starting_solution)
    record = dict(center=center,T_K=T,P_Pa=P,apparent_amine_feed_mol=amine_feed,steps=[])
    if 'G_J' not in center:
        return record
    for factor, dt in ((1e-4,.04),(5e-5,.02),(2.5e-5,.01)):
        dp = factor*P
        points = {}
        for label,t,p in (('P+',T,P+dp),('P-',T,P-dp),('T+',T+dt,P),('T-',T-dt,P)):
            try:
                problem.temperature = type(problem.temperature).fixed(t)
                problem.pressure = type(problem.pressure).fixed(p)
                points[label],_ = solve(spec,model,anchor_model,thermal,problem,seed)
            except (RuntimeError,ValueError) as error:
                points[label] = dict(T_K=t,P_Pa=p,admitted=False,refusal=str(error))
        row = dict(step_Pa=dp,step_K=dt,points=points)
        record['steps'].append(row)
        if all('G_J' in points[k] for k in ('P+','P-')):
            plus,minus = [points[k] for k in ('P+','P-')]
            volume = (plus['G_J']-minus['G_J'])/(2*dp)
            row.update(G_pressure_derivative_m3=volume,signed_volume_error_m3=volume-center['volume_m3'],
                       relative_volume_error=volume/center['volume_m3']-1,
                       volume_admitted=center['admitted'] and plus['admitted'] and minus['admitted'],
                       volume_arithmetic_error_m3=(plus['G_error_J']+minus['G_error_J'])/(2*dp))
        if all('G_J' in points[k] for k in ('T+','T-')):
            plus,minus = [points[k] for k in ('T+','T-')]
            b_T = [(x-y)/(2*dt) for x,y in zip(plus['b'],minus['b'],strict=True)]
            components = []
            neutral = [bool(x) for x in thermal.component_intervals]
            for phase in center['values']:
                offset_h = [-phase['amount_mol']*R*T*T*v*db for v,db in zip(phase['x'],b_T,strict=True)]
                # The ideal-density term uses ln(rho_i). The +nRT term and
                # each species standard's derivative give the ideal enthalpy.
                h_i = [phase['amount_mol']*R*T*v+h for v,h in zip(phase['x'],offset_h,strict=True)]
                components.append(dict(eos_residual_H_J=phase['H_res_J'],offset_H_by_species_J=offset_h,
                    neutral_caloric_H_J=fsum(h for h,anchor in zip(h_i,neutral,strict=True) if anchor),
                    reaction_completed_H_J=fsum(h for h,anchor in zip(h_i,neutral,strict=True) if not anchor),
                    pressure_chain_H_J=0.,eq12_H_J=phase['H_res_J']+fsum(h_i)))
            h = -T*T*(plus['G_J']/(T+dt)-minus['G_J']/(T-dt))/(2*dt)
            eq12 = fsum(q['eq12_H_J'] for q in components)
            row.update(fixed_reference_offset_temperature_derivative_per_K=b_T,caloric_components=components,
                       eq12_H_J=eq12,Gibbs_Helmholtz_H_J=h,eq12_minus_Gibbs_Helmholtz_J=eq12-h,
                       enthalpy_admitted=center['admitted'] and plus['admitted'] and minus['admitted'],
                       caloric_arithmetic_error_J=(T*T/(2*dt))*(
                           plus['G_error_J']/(T+dt)+minus['G_error_J']/(T-dt)))
            if 'engine_H_J' in center:
                row.update(engine_minus_Gibbs_Helmholtz_J=center['engine_H_J']-h,
                           engine_minus_eq12_J=center['engine_H_J']-eq12)
            if all('engine_H_over_T_minus_S_J_K' in q for q in (plus,minus)):
                row['H_over_T_minus_S_check_J'] = -T*T*(
                    plus['engine_H_over_T_minus_S_J_K']-minus['engine_H_over_T_minus_S_J_K'])/(2*dt)
    return record


def worked_state(spec, model, thermal, observation, amine_feed):
    """Continue the liquid branch of a declared bubble state for C1."""
    row = next(q for role in ("fitted", "comparisons") for q in spec.inputs["observations"][role]
               if q["identity"] == observation)
    bubble = copy.copy(spec.problems[row['problem']])
    result = eq.solve_equilibrium(model,bubble)
    if not result.requested_tolerance_met:
        raise ValueError(result.message)
    problem = copy.copy(bubble)
    liquid = copy.copy(problem.phases[0])
    liquid.amount = eq.Free()
    liquid.composition_guess = result.phase_mole_fractions(0)
    liquid.packing_guess = result.packing_fractions[0]
    problem.phases = [liquid]
    problem.P = result.pressure
    native = reg.stability(spec.parameters,problem,scale=1.).problem
    return derivatives(spec,model,thermal,native,result.temperature,result.pressure,amine_feed,result)


def reported_derivatives(amine, route, point):
    from .fit import fingerprint

    label = "AMP_free" if amine == "amp" else amine.upper()
    path = RESULTS / "shared/comparisons/properties/derivatives" / f"selected-{label}.json.gz"
    retained = read(path)
    spec = route.bind(point)
    observation = retained["observation"]
    record = worked_state(spec, spec.model, spec.thermal, observation, retained["apparent_amine_feed_mol"])
    return dict(record, wheel=verify(), endpoint_fingerprint=fingerprint(point), observation=observation,
                declaration_source=path.relative_to(ROOT).as_posix())


def worked_calorimetry(spec, record):
    """Replay the recorded addition enthalpy and heat-capacity stencil."""
    verify()
    T, P = record["T_K"], record["P_Pa"]
    cp_row = next(row for row in spec.inputs["observations"]["fitted"] if row["group"] == "Cp")
    template = spec.problems[cp_row["problem"]]
    problems = {}
    values = {}
    points = {}
    loaded = None
    for label, retained in record["points"].items():
        problem = copy.copy(template)
        problem.T, problem.P = retained["T_K"], P
        problem.feed = eq.Amounts(dict(zip(spec.parameters.component_ids, retained["feed_mol"], strict=True)))
        result = eq.solve_equilibrium(spec.model, problem)
        checks = physical(spec, problem, result) if result.requested_tolerance_met else {}
        if not checks.get("physical_checks_pass"):
            raise ValueError(f"Caloric state {label} failed closure: {result.message}")
        kinds = [observable("SystemEnthalpy", 0)]
        if label == "loaded":
            kinds.append(observable("EquilibriumIsobaricHeatCapacity", 0))
        values[label] = [value for value, _ in first_actions(spec.model, problem, result, kinds, [(0., 0., None)])[0]]
        problems[label] = problem
        points[label] = dict(feed_mol=retained["feed_mol"], T_K=result.temperature, H_J=values[label][0],
                             physical_checks=checks)
        if label == "loaded":
            loaded = result
    added = record["added_CO2_mol"]
    observation = reg.addition_enthalpy(spec.parameters, problems["initial"], problems["loaded"],
        {"carbon-dioxide": 1.0}, added, T, P, phase="vapor", observed=0.0, form="difference", scale=1.0)
    prediction = reg.predict(spec.model, observation)
    if prediction.status.name != "Available" or not prediction.requested_tolerance_met:
        raise ValueError(prediction.message)
    amount = fsum(record["apparent_feed_mol"])
    finite = [(values[str(step)][0] - values[str(-step)][0]) / (2 * step * amount)
              for step in record["stencil_steps_K"]]
    cp = values["loaded"][1]
    stream = (values["loaded"][0] - values["initial"][0]) / added - prediction.value
    problem = problems["loaded"]
    actions = first_actions(spec.model, problem, loaded, [observable("PhaseLogActivity", 0, i)
                            for i in range(len(spec.parameters.component_ids))], [(1., 0., None)])[0]
    reactions = []
    for reaction, activity in zip(problem.reactions, eq.reaction_activities(spec.model, loaded), strict=True):
        law = reaction.correlation
        nu = [reaction.stoichiometry.get(c, 0.) for c in spec.parameters.component_ids]
        dnu = fsum(nu)
        slope = fsum(n * dt for n, (_, dt) in zip(nu, actions, strict=True)) + dnu / T
        source_slope = -law.b / T**2 + law.c / T + law.d - 2 * law.e / T**3 + 2 * law.f * T
        scale = R * T*T / 1000
        water = spec.parameters.component_ids.index("water")
        water_mass = next(q["fixed"]["molar_mass"]["value"]["magnitude"] for q in spec.inputs["endpoint"]["components"]
                          if q["component_id"] == "water")
        molality = (dnu - nu[water]) * log(water_mass * problem.neutral_reference.standard_molality_mol_per_kg)
        reactions.append(dict(name=reaction.name, P_source_Pa=activity.reference_pressure_pa,
            ln_K_source=activity.log_quotient, Gamma=activity.log_pressure_quotient-activity.log_quotient-molality,
            source_kJ_mol=scale * source_slope, fugacity_kJ_mol=scale * (slope-source_slope), ideal_gas_kJ_mol=scale * slope))
    conditions = ("T_K", "P_Pa", "MEA_wt_percent", "loading_initial", "loading_final",
                  "apparent_feed_mol", "loaded_mass_kg", "added_CO2_mol", "stencil_steps_K")
    return dict({name: record[name] for name in conditions}, points=points, reactions=reactions,
                heat_kJ_mol=prediction.value / 1000, cp_J_mol_K=cp, cp_stencil_J_mol_K=finite,
                cp_minus_fine_J_mol_K=cp-finite[-1], cp_kJ_kg_K=cp*amount/record["loaded_mass_kg"]/1000,
                added_stream={"H_J_per_mol": stream})
