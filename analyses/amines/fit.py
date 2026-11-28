"""Reported fit starts, attempts, selection and replay."""

from collections import Counter
import csv
from copy import deepcopy
import gzip
from hashlib import sha256
import json
import os
from time import monotonic

from .model import parameter_values, replay, row_manifest, with_parameter_values
from .properties import endpoint_diagnostics, property_rows
from .wheel import verify
from .records import ROOT, RESULTS, input_path, read
from MEA.solvent_specification import jsonable


def fingerprint(point):
    return sha256(json.dumps(jsonable(point), sort_keys=True, allow_nan=False).encode()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(jsonable(value), allow_nan=False, indent=2) + "\n").encode()
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(gzip.compress(data, mtime=0) if path.suffix == ".gz" else data)
    tmp.replace(path)


def manifest(fit_set, *, preserve_evaluation_counts=()):
    wheel = verify()
    path = fit_set["retained"]
    declaration = read(path / "manifest.json.gz")
    if declaration["wheel"] != wheel:
        raise ValueError(f"{path}: fit manifest wheel differs from the installed wheel")
    manifest_id = fingerprint(declaration)
    replacement = path / "replacement-starts.json.gz"
    starts = declaration["starts"]
    if replacement.is_file():
        extra = read(replacement)
        if extra["wheel"] != wheel or extra["manifest_fingerprint"] != manifest_id:
            raise ValueError(f"{replacement}: replacement starts do not belong to the fit manifest")
        starts = starts | {k: v["start"] for k, v in extra["draws"].items() if v["disposition"] == "eligible"}
    diagnostic_starts = {}
    for source in fit_set.get("diagnostic_attempts", ()):
        data = read(path / source)
        label = data["start"]
        if data["wheel"] != wheel or data["manifest_fingerprint"] != manifest_id:
            raise ValueError(f"{label}: additional start does not belong to the fit manifest")
        diagnostic_starts[label] = dict(optimizer=data["optimizer_start"], controls=data["controls"])
    start_controls, evaluation_counts = {}, {}
    for label in starts:
        data = read(path / f"{label}.json.gz")
        stages, counts = [], []
        while data is not None:
            if data["wheel"] != wheel or data["manifest_fingerprint"] != manifest_id or data["start"] != label:
                raise ValueError(f"{path}: controls for {label} do not belong to the fit manifest")
            stages.append(data["controls"])
            if label in preserve_evaluation_counts:
                report = data["report"]
                elapsed_refusal = any("elapsed work budget exhausted" in failure["message"]
                                      for failure in report["failures"])
                counts.append(dict(entries=len(report["iteration_costs"]),
                                   converged=report["status"] == "converged" and not elapsed_refusal))
            data = data.get("previous_stage")
        start_controls[label] = stages[::-1]
        if counts:
            evaluation_counts[label] = counts[::-1]
    result = dict(declaration, starts=starts, diagnostic_starts=diagnostic_starts, start_controls=start_controls)
    if evaluation_counts:
        result["evaluation_counts"] = evaluation_counts
    return result


def route_for(fit_set):
    return fit_set["route"](fit_set["declaration"], reference_pressure_pa=fit_set["reference_pressure_pa"])


def is_pressure(row):
    return row["constructor"] == "observation" and row["kind"] in ("pressure", "partial_pressure")


def bind_fit(fit_set, point):
    spec = route_for(fit_set).bind(point)
    if "pressure_log_scale" in fit_set:
        held_groups = fit_set.get("held_pressure_groups", ())
        rows = [row for row in spec.inputs["observations"]["fitted"]
                if is_pressure(row) and row["group"] not in held_groups]
        counts = Counter((row["group"], row["kind"]) for row in rows)
        for row in rows:
            arguments = row["arguments"]
            arguments["form"] = "log_ratio"
            arguments.pop("scale", None)
            row["weight"] = 1 / (counts[row["group"], row["kind"]] * fit_set["pressure_log_scale"]**2)
            if isinstance(row["basis"], dict) and "arguments" in row["basis"]:
                row["basis"] = dict(row["basis"], arguments=arguments)
    return spec


def retained_endpoint(fit_set):
    path = fit_set["retained"]
    selection = read(path / "selection.json")
    endpoint = selection["endpoint_fingerprint"]
    (label,) = (label for label, attempt in selection["attempts"].items() if attempt["endpoint"] == endpoint)
    record = read(path / f"{label}.json.gz")
    if record["wheel"] != verify() or fingerprint(record["endpoint"]) != endpoint:
        raise ValueError(f"{path}: selected endpoint identity does not match the retained fit")
    return record["endpoint"], selection


def replay_endpoint(fit_set):
    point, selection = retained_endpoint(fit_set)
    spec = bind_fit(fit_set, point)
    expected = read(fit_set["retained"] / "manifest.json.gz")
    inputs = spec.inputs["observations"]["fitted"]
    retained = expected["rows"]["fitted"]
    if [(r["identity"], r["weight"]) for r in inputs] != [(r["identity"], r["weight"]) for r in retained]:
        raise ValueError(f"{fit_set['retained']}: changed fitted row identity, order, or weight")
    result = replay(spec)
    return dict(
        wheel=verify(),
        endpoint_fingerprint=selection["endpoint_fingerprint"],
        retained_cost=selection["cost"],
        replay=result,
        diagnostics=endpoint_diagnostics(spec, result, point, expected["fit_controls"]),
    )


def rows(fit_set, declaration):
    measured = row_manifest(bind_fit(fit_set, declaration["start_A_declaration"]))
    if measured != declaration["rows"]:
        raise ValueError(f"{fit_set['retained']}: changed start-state row declarations")
    return dict(wheel=verify(), rows=measured)


def reported_manifest(amine, fit_set, output):
    """Bind the reported starts to the upstream endpoint reproduced in this run."""
    from . import salt

    preservation = read(RESULTS / "shared/preservation/fit-cost-budgets.json.gz")
    declaration = manifest(fit_set)
    budgets = {}
    if preservation["wheel"] == declaration["wheel"]:
        for case, record in preservation["fits"].items():
            family, label = case.split(", ", 1)[0].split()
            if family.lower() == amine and label in declaration["starts"]:
                budgets[label] = [dict(entries=stage["iterations"], converged=stage["status"] == "converged")
                                  for stage in record["new_stages"]]
    if budgets:
        declaration["evaluation_counts"] = budgets
    point = deepcopy(declaration["prior_declaration"])
    mapping = point["parameters"]
    if amine == "mea":
        upstream = read(output / "salt/sodium-salts/fit/summary.json.gz")
        if upstream["wheel"] != declaration["wheel"]:
            raise ValueError("Salt and MEA fits require the same Engine wheel")
        values = {f"{salt.LAWS[ion]}/a{i}": upstream["laws_at_record_reference"][ion][f"a{i}"]
                  for ion in (salt.HCO3, salt.CO3) for i in (0, 1)}
        point["parameters"] = with_parameter_values(mapping, values)
    else:
        path = output / "mea/reported/fit"
        selection = read(path / "selection.json")
        (label,) = (name for name, attempt in selection["attempts"].items()
                    if attempt["endpoint"] == selection["endpoint_fingerprint"])
        donor = read(path / f"{label}.json.gz")
        if donor["wheel"] != declaration["wheel"] or fingerprint(donor["endpoint"]) != selection["endpoint_fingerprint"]:
            raise ValueError("The MEA donor does not match the current selection")
        donor = donor["endpoint"]["parameters"]
        for pair in donor["pairs"]:
            species = {pair["component_id_a"], pair["component_id_b"]}
            if species in ({salt.W, salt.HCO3}, {salt.W, salt.CO3}):
                if amine != "mdea":
                    salt.set_pair(mapping, pair["component_id_a"], pair["component_id_b"], pair["coefficients"][0])
                elif pair not in mapping["pairs"]:
                    raise ValueError("MDEA salt laws differ from the reproduced MEA donor")
        values = parameter_values(donor)
        carbamate = "component/carbamate-anion/"
        if amine == "amp":
            size = values[carbamate + "segment_diameter"]
            coordinate = next(q for q in point["coordinates"] if q["identity"] == "AMPCOO-segment-diameter")
            coordinate["bounds"][0] = size
            coordinate["origin"] = max(coordinate["origin"], size)
            changes = {carbamate + family: coordinate["origin"] * factor for family, _, factor in coordinate["targets"]}
            changes["pair/carbamate-anion/water/k_ij"] = values["pair/carbamate-anion/water/k_ij"]
        elif amine == "dea":
            neutral, mea = "component/diethanolamine/", "component/monoethanolamine/"
            model = parameter_values(mapping)
            scale = model[neutral + "segment_count"] * model[neutral + "segment_diameter"]**3
            scale /= values[mea + "segment_count"] * values[mea + "segment_diameter"]**3
            size = scale**(1/3) * values[carbamate + "segment_diameter"]
            changes = {carbamate + family: size for family in ("segment_diameter", "debye_huckel_diameter", "born_diameter")}
            changes[carbamate + "packing_diameter"] = 0.88 * size
        else:
            changes = None
        if changes is not None:
            changes[carbamate + "dispersion_energy_over_k"] = values[carbamate + "dispersion_energy_over_k"]
            point["parameters"] = with_parameter_values(mapping, changes)
    if point != declaration["start_A_declaration"]:
        raise ValueError(f"{amine}: reproduced donor does not recreate the reported fit declaration")
    return declaration


def move_manifest(amine, fit_set, output, *, ablation=False):
    """Declare the W fit from the prescribed retained start and current donor."""
    from . import dea, salt

    wheel = verify()
    preserved = fit_set["preserved"]
    retained = read(preserved / "manifest.json.gz")
    if ablation:
        held = read(RESULTS / amine / "water-bicarbonate-ablation/fit/A.json.gz")
        point = deepcopy(held["endpoint"])
    elif amine in ("mea", "amp"):
        point = deepcopy(retained["prior_declaration"])
    else:
        held = read(preserved / "A.json.gz")
        point = deepcopy(held["endpoint"])
    mapping = point["parameters"]
    if ablation:
        if amine == "mea":
            coordinates = read(ROOT / "analyses/solvent_specification_mea/inputs/fit-coordinates.json")
            coordinate = deepcopy(next(q for q in coordinates if q["identity"] == salt.LAWS[salt.HCO3]))
            coordinate["origin"] = parameter_values(mapping)[coordinate["identity"]]
            point["coordinates"].append(coordinate)
        else:
            donor_path = output / "mea/water-bicarbonate-ablation/fit"
            donor, selection = retained_endpoint({"retained": donor_path})
            attempt = read(donor_path / f'{selection["selected"]}.json.gz')
            if salt.LAWS[salt.HCO3] in attempt["diagnostics"]["active_bounds"]:
                raise ValueError("The MEA water–bicarbonate interaction is on a bound")
            node = next(c for p in donor["parameters"]["pairs"] for c in p["coefficients"]
                        if c["identity"] == salt.LAWS[salt.HCO3])
            salt.set_pair(mapping, salt.W, salt.HCO3, node)
    else:
        if amine == "mea":
            donor = read(output / "salt/sodium-salts/fit/summary.json.gz")
            pair_keys = {salt.W, salt.NA, salt.HCO3, salt.CO3}
            for pair in donor["document"]["pairs"]:
                a, b = pair["component_id_a"], pair["component_id_b"]
                if a in pair_keys and b in pair_keys and salt.W in (a, b) and salt.NA not in (a, b):
                    salt.set_pair(mapping, a, b, pair["coefficients"][0])
        else:
            donor_path = output / "mea/reported/fit"
            selection = read(donor_path / "selection.json")
            donor = read(donor_path / f'{selection["selected"]}.json.gz')
            donor_mapping = donor["endpoint"]["parameters"]
            if fingerprint(donor["endpoint"]) != selection["endpoint_fingerprint"]:
                raise ValueError("MEA donor fingerprint differs from the selected endpoint")
            for pair in donor_mapping["pairs"]:
                a, b = pair["component_id_a"], pair["component_id_b"]
                if {a, b} in ({salt.W, salt.HCO3}, {salt.W, salt.CO3}):
                    salt.set_pair(mapping, a, b, pair["coefficients"][0])
            if amine in ("amp", "dea"):
                values = parameter_values(donor_mapping)
                carbamate = "component/carbamate-anion/"
                size = values[carbamate + "segment_diameter"]
                changes = {carbamate + "dispersion_energy_over_k": values[carbamate + "dispersion_energy_over_k"]}
                if amine == "amp":
                    coordinate = next(q for q in point["coordinates"] if q["identity"] == "AMPCOO-segment-diameter")
                    coordinate["bounds"][0] = size
                    coordinate["origin"] = max(coordinate["origin"], size)
                    size = coordinate["origin"]
                else:
                    neutral, mea = "component/diethanolamine/", "component/monoethanolamine/"
                    model = parameter_values(mapping)
                    ratio = model[neutral + "segment_count"] / values[mea + "segment_count"]
                    size *= ratio**(1 / 3) * model[neutral + "segment_diameter"] / values[mea + "segment_diameter"]
                    changes["pair/bicarbonate-anion/protonated-diethanolamine/k_ij"] = values[
                        "pair/bicarbonate-anion/protonated-monoethanolamine/k_ij"]
                changes.update({carbamate + k: size * factor for k, factor in (
                    ("segment_diameter", 1), ("debye_huckel_diameter", 1),
                    ("born_diameter", 1), ("packing_diameter", 0.88))})
                changes["pair/carbamate-anion/water/k_ij"] = values["pair/carbamate-anion/water/k_ij"]
                point["parameters"] = with_parameter_values(mapping, changes)
        if donor["wheel"] != wheel:
            raise ValueError("The fitted donor uses another wheel")
    if amine == "dea":
        point = dea.repaired_point(point)
    controls = dict(retained["fit_controls"], maximum_elapsed_time_seconds=900.0)
    starts = {"A": dict(optimizer=[0.0] * len(point["coordinates"]))}
    if amine == "dea":
        starts["B"] = dict(optimizer=dea.alternate_start(point))
    return dict(wheel=wheel, source_wheel=retained["wheel"], source=retained["source"],
                start_A_declaration=point, fit_controls=controls, starts=starts, diagnostic_starts={},
                rows=row_manifest(route_for(fit_set).bind(point)))


def alternate_starts(fit_set, target):
    """Test the declared alternate vectors against the W start-A result."""
    reported = fit_set["retained"]
    declaration = read(reported / "manifest.json.gz")
    baseline = read(reported / "A.json.gz")
    prior = read(fit_set["preserved"] / "manifest.json.gz")
    point = declaration["start_A_declaration"]
    coordinates = point["coordinates"]
    if [q["identity"] for q in coordinates] != prior["coordinate_order"]:
        raise ValueError("Alternate start coordinate order differs from W")
    replacements = read(fit_set["preserved"] / "replacement-starts.json.gz")
    if replacements["manifest_fingerprint"] != fingerprint(prior):
        raise ValueError("Replacement starts do not belong to the preserved declaration")
    declared = prior["starts"] | {label: draw["start"] for label, draw in replacements["draws"].items()
                                  if draw["disposition"] == "eligible"}
    selected = read(fit_set["preserved"] / "selection.json")
    starts = {}
    for label in selected["tied"]:
        if label != selected["selected"]:
            start = declared[label]
            optimizer = [(value - q["origin"]) / q["scale"]
                         for value, q in zip(start["vector"], coordinates, strict=True)]
            starts[label] = dict(start, optimizer=optimizer)
    declaration = dict(declaration, starts=starts)
    save(target / "manifest.json.gz", declaration)
    attempts = {}
    print_cost = f'{baseline["replay"]["cost"]:.3f}'
    for label in starts:
        path = target / f"{label}.json.gz"
        record = continue_fit(fit_set, declaration, label, path, attempt(fit_set, declaration, label, path))
        cost = record.get("replay", {}).get("cost")
        tied = (record["report"]["status"] == "converged" and record.get("replay_passed")
                and cost is not None and f"{cost:.3f}" == print_cost)
        attempts[label] = dict(cost=cost, tied=tied, endpoint=record.get("endpoint_fingerprint"))
    return dict(wheel=verify(), baseline=baseline["endpoint_fingerprint"],
                baseline_cost=baseline["replay"]["cost"], attempts=attempts,
                tied_count=1 + sum(a["tied"] for a in attempts.values()))


def remove_mdea_gap_bound(point):
    coordinate = next(q for q in point["coordinates"]
                      if q["identity"].startswith("pair/mdea-water/k_ij/a0"))
    # Restore the upper limit of the interaction coordinate before the binary gap constraint.
    coordinate["bounds"][1] = 0.5


def pressure_fit_manifest(fit_set, source, controls_source):
    wheel = verify()
    path = controls_source["retained"] / "manifest.json.gz"
    controls = read(path)
    if controls["wheel"] != wheel:
        raise ValueError(f"{path}: fit controls use another wheel")
    if "endpoint" in source:
        path = source["endpoint"]
        point = read(path)
    else:
        point = controls["start_A_declaration"]
    return dict(wheel=wheel, source_wheel=controls["wheel"],
                source=path.relative_to(ROOT).as_posix(),
                start_A_declaration=point, fit_controls=controls["fit_controls"],
                starts={"A": dict(optimizer=[0.0] * len(point["coordinates"]))},
                diagnostic_starts={}, rows=row_manifest(route_for(fit_set).bind(point)))


def mdea_weighted_manifest(fit_set, unweighted):
    """Use the unweighted control's start and change the binary row weights."""
    source = unweighted["retained"] / "manifest.json.gz"
    declaration = read(source)
    if declaration["wheel"] != verify():
        raise ValueError(f"{source}: unweighted start uses another wheel")
    point = declaration["start_A_declaration"]
    return dict(declaration, source=source.relative_to(ROOT).as_posix(),
                source_wheel=declaration["wheel"], rows=row_manifest(bind_fit(fit_set, point)))


def mdea_without_gap_bound(fit_set, target):
    declaration = read(fit_set["retained"] / "manifest.json.gz")
    remove_mdea_gap_bound(declaration["start_A_declaration"])
    save(target / "manifest.json.gz", declaration)
    return reported_fit(fit_set, declaration, target)


def control_manifest(reported, fit_set, *, bicarbonate_donor=None):
    """Start the control at the selected reported endpoint on the locked wheel."""
    point, selection = retained_endpoint(reported)
    if bicarbonate_donor is not None:
        from . import salt

        donor, donor_selection = retained_endpoint({"retained": bicarbonate_donor})
        record = read(bicarbonate_donor / f'{donor_selection["selected"]}.json.gz')
        if salt.LAWS[salt.HCO3] in record["diagnostics"]["active_bounds"]:
            raise ValueError("The MEA water–bicarbonate interaction is on a bound")
        node = next(c for pair in donor["parameters"]["pairs"] for c in pair["coefficients"]
                    if c["identity"] == salt.LAWS[salt.HCO3])
        salt.set_pair(point["parameters"], salt.W, salt.HCO3, node)
    if fit_set.get("water_anion_intercepts"):
        from . import salt

        values = parameter_values(point["parameters"])
        for ion in (salt.HCO3, salt.CO3):
            identity = salt.LAWS[ion] + "/a0"
            point["coordinates"].append(dict(
                identity=identity,
                origin=values[identity],
                scale=salt.SCALES[0],
                bounds=salt.BOUNDS[0],
                targets=[("temperature_law_coefficient", identity, 1.0)],
            ))
    source = reported["retained"] / f'{selection["selected"]}.json.gz'
    controls = dict(read(source)["controls"], maximum_elapsed_time_seconds=reported["maximum_seconds"])
    return dict(
        wheel=selection["wheel"],
        source_wheel=selection["wheel"],
        source=str(source.relative_to(ROOT)),
        source_endpoint_fingerprint=selection["endpoint_fingerprint"],
        start_A_declaration=point,
        fit_controls=controls,
        starts={"A": dict(optimizer=[0.0] * len(point["coordinates"]))},
        diagnostic_starts={},
        rows=row_manifest(bind_fit(fit_set, point)),
        **({"donor_endpoint_fingerprint": donor_selection["endpoint_fingerprint"]}
           if bicarbonate_donor is not None else {}),
    )


def reported_fit(fit_set, declaration, target):
    attempts = {}
    for label in declaration["starts"] | declaration["diagnostic_starts"]:
        path = target / f"{label}.json.gz"
        record = attempt(fit_set, declaration, label, path)
        if label in declaration["starts"]:
            attempts[label] = continue_fit(fit_set, declaration, label, path, record)
    selection = select(declaration, attempts)
    save(target / "selection.json", selection)
    if selection["selected"] is None:
        raise ValueError("No reproduced fit met the selection criteria")
    if "source_wheel" in declaration:
        return selection
    old, retained = retained_endpoint(fit_set)
    selected = attempts[selection["selected"]]
    retained_attempt = read(fit_set["retained"] / f'{retained["selected"]}.json.gz')
    row_differences, predictions = compare_rows(retained_attempt["replay"]["rows"], selected["replay"]["rows"])
    values = parameter_values(selected["endpoint"]["parameters"])
    return dict(
        wheel=selection["wheel"], selected=selection["selected"], retained_selected=retained["selected"],
        endpoint_fingerprint=selection["endpoint_fingerprint"], retained_fingerprint=fingerprint(old),
        cost=selection["cost"], retained_cost=retained["cost"],
        parameter_differences={key: (before, values[key]) for key, before in parameter_values(old["parameters"]).items()
                               if before != values[key]},
        row_differences=row_differences, prediction_differences=predictions,
    )


def attempt(fit_set, declaration, label, path, *, previous=None):
    wheel = verify()
    route = route_for(fit_set)
    point = declaration["start_A_declaration"]
    start = (declaration["starts"] | declaration["diagnostic_starts"])[label]
    controls = start.get("controls", declaration["fit_controls"])
    u = start["optimizer"]
    manifest_id = fingerprint(declaration)
    stage = 0
    if previous is not None:
        if (
            previous["wheel"] != wheel
            or previous["manifest_fingerprint"] != manifest_id
            or previous["endpoint_fingerprint"] != fingerprint(previous["endpoint"])
            or previous["start"] != label
            or not previous["replay_passed"]
            or previous["report"]["status"] != "limit_reached"
        ):
            raise ValueError("Continuation requires the same fit, start and wheel at a replayable work limit")
        controls = previous["controls"]
        point = previous["endpoint"]
        earlier = previous
        while earlier is not None:
            stage += 1
            earlier = earlier.get("previous_stage")
    recorded = declaration.get("start_controls", {}).get(label, ())
    if stage < len(recorded):
        controls = recorded[stage]
    controls = controls | dict(workers=int(os.environ["AGENT_HEAVY_CORES"]))
    controls.setdefault("maximum_elapsed_time_seconds", fit_set["maximum_seconds"])
    counts = declaration.get("evaluation_counts", {}).get(label)
    if counts is not None:
        # S records the initial cost at iteration zero.
        budget = counts[stage]
        # A tolerance stop tests its final step before reaching the iteration limit.
        controls.update(maximum_iterations=budget["entries"] - 1 + budget["converged"],
                        maximum_elapsed_time_seconds=24 * 60 * 60)
    spec = bind_fit(fit_set, point)
    spec.spec["optimizer"] = controls
    tick = monotonic()
    _, report, _ = spec.fit(starts=None if previous is not None else [u])
    record = dict(
        start=label,
        wheel=wheel,
        manifest_fingerprint=manifest_id,
        controls=controls,
        optimizer_start=u,
        report=report,
        fit_seconds=monotonic() - tick,
    )
    if previous is not None:
        record["previous_stage"] = previous
    if counts is not None:
        record["cost_entries"] = dict(retained=budget["entries"], attained=len(report["iteration_costs"]))
    save(path, record)
    if report["physical"] and report["reactions"]:
        endpoint = route.endpoint_mapping(point, report, point["coordinates"])
        record.update(endpoint=endpoint, endpoint_fingerprint=fingerprint(endpoint))
        save(path, record)
        tick = monotonic()
        bound = bind_fit(fit_set, endpoint)
        fit_replay = replay(bound)
        record.update(replay=fit_replay, replay_seconds=monotonic() - tick)
        cost = report["data_cost"] if report["data_cost"] is not None else report["final_cost"]
        replayed = fit_replay["cost"]
        record["replay_passed"] = (
            replayed is not None
            and cost is not None
            and abs(replayed - cost) / max(abs(replayed), abs(cost), 1e-300) <= fit_set["replay_tolerance"]
        )
        save(path, record)
        tick = monotonic()
        record["diagnostics"] = endpoint_diagnostics(bound, fit_replay, endpoint, controls)
        record["diagnostic_seconds"] = monotonic() - tick
        save(path, record)
    return record


def continue_fit(fit_set, declaration, label, path, record):
    stages, previous = 1, record
    while "previous_stage" in previous:
        stages += 1
        previous = previous["previous_stage"]
    # The reported campaigns permit two continuations at the same controls.
    counts = declaration.get("evaluation_counts", {}).get(label)
    while stages < (len(counts) if counts is not None else 3) and record["report"]["status"] == "limit_reached" and record.get("replay_passed"):
        record = attempt(fit_set, declaration, label, path, previous=record)
        stages += 1
    return record


def select(declaration, records):
    wheel, manifest_id = verify(), fingerprint(declaration)
    if any(r["wheel"] != wheel or r["manifest_fingerprint"] != manifest_id for r in records.values()):
        raise ValueError("Selection requires attempts from the same fit and wheel")
    eligible = {
        label: r
        for label in declaration["starts"]
        if (r := records.get(label)) and r.get("replay_passed") and r["report"]["status"] == "converged"
    }
    best = min((v["replay"]["cost"] for v in eligible.values()), default=None)
    tolerance = declaration["fit_controls"]["function_tolerance"]
    tied = [label for label, r in eligible.items() if abs(r["replay"]["cost"] - best) <= tolerance * best]
    selected = tied[0] if tied else None
    return dict(
        wheel=wheel,
        selected=selected,
        numerical_minimum=best,
        tied=tied,
        endpoint_fingerprint=eligible[selected]["endpoint_fingerprint"] if selected else None,
        cost=eligible[selected]["replay"]["cost"] if selected else None,
        attempts={
            label: dict(
                cost=r.get("replay", {}).get("cost"),
                status=r["report"]["status"],
                replay_passed=r.get("replay_passed", False),
                endpoint=r.get("endpoint_fingerprint"),
            )
            for label, r in records.items()
        },
    )


def descent_probe(route, fit_record, fractions=(1.0, 0.5)):
    """Test the bounded local least-squares direction at the evaluated endpoint."""
    from scipy.optimize import lsq_linear
    import numpy as np
    from epcsaft import regression as reg

    wheel = verify()
    point = fit_record["endpoint"]
    endpoint = fit_record["endpoint_fingerprint"]
    if fit_record["wheel"] != wheel or endpoint != fingerprint(point):
        raise ValueError("Descent probe requires the evaluated endpoint and wheel")
    cost = fit_record["replay"]["cost"]
    spec = route.bind(point)
    coordinates = point["coordinates"]
    lower, upper = (np.array([(d["bounds"][i] - d["origin"]) / d["scale"] for d in coordinates]) for i in (0, 1))
    width = np.array([(d["bounds"][1] - d["bounds"][0]) / d["scale"] for d in coordinates])
    jacobian = np.array(fit_record["diagnostics"]["jacobian_bound_normalized"]) / width
    residual = np.array([row["weighted_residual"] for row in fit_record["replay"]["rows"]])
    linear = lsq_linear(jacobian, -residual, bounds=(lower, upper), method="bvls", tol=1e-13)
    if not linear.success:
        raise ValueError(linear.message)
    u = np.clip(linear.x, lower, upper)
    ju = jacobian @ u
    predicted = -float((residual + 0.5 * ju) @ ju) / cost
    trials = []
    for fraction in fractions:
        try:
            step = (fraction * u).tolist()
            chart = reg.evaluate_coordinates(
                spec.parameters, spec.coordinates(), step, [], thermochemistry=spec.thermal
            )
            candidate = route.endpoint_mapping(
                point,
                dict(optimizer=step, physical=chart.physical, reactions=spec.fitted_reactions(chart)),
                coordinates,
            )
        except (ValueError, RuntimeError) as error:
            trials.append(dict(fraction=fraction, refusal=str(error), relative_reduction=None))
            continue
        trial = replay(route.bind(candidate))
        trial_cost = trial["cost"]
        reduction = (cost - trial_cost) / cost if trial_cost is not None else None
        trials.append(
            dict(
                fraction=fraction,
                point=candidate,
                endpoint_fingerprint=fingerprint(candidate),
                replay=trial,
                relative_reduction=reduction,
            )
        )
        if reduction is not None and reduction > fit_record["controls"]["function_tolerance"]:
            break
    return dict(
        endpoint=endpoint,
        wheel=wheel,
        cost=cost,
        relative_linearized_reduction=predicted,
        optimizer_step=u.tolist(),
        trials=trials,
    )


def replay_retained(fit_set):
    wheel = verify()
    if "replay" in fit_set:
        return dict(fit_set["replay"](fit_set), wheel=wheel, archive=fit_set["archive"])
    point = read(fit_set["endpoint"])
    for key in fit_set["endpoint_keys"]:
        point = point[key]
    if "born_diameter" in fit_set:
        species, path = fit_set["born_diameter"]
        point = dict(point, parameters=with_parameter_values(
            point["parameters"], {f"component/{species}/born_diameter": read(path)["born_A"]}
        ))
    reference_path = input_path(fit_set["reference"])
    if reference_path.suffix == ".csv":
        with reference_path.open(newline="") as stream:
            reference = [
                dict(
                    row,
                    value=float(row["predicted"]) if row["predicted"] else None,
                    status="Available" if row["predicted"] else "Unavailable",
                )
                for row in csv.DictReader(stream)
            ]
    else:
        reference = read(reference_path)
    for key in fit_set["reference_keys"]:
        reference = reference[key]
    route = route_for(fit_set)
    result = replay(route.bind(point))
    if isinstance(reference, list):
        retained_rows = reference
        objective = read(fit_set["objective"])
        for key in fit_set["objective_keys"]:
            objective = objective[key]
        if "prediction_record" in fit_set:
            predictions = read(fit_set["prediction_record"])
            for key in fit_set["prediction_keys"]:
                predictions = predictions[key]
            retained_rows = [
                dict(
                    identity=row["identity"],
                    value=value,
                    status="Available",
                    requested_tolerance_met=True,
                )
                for row, value in zip(
                    (row for row in retained_rows if row["role"] == "fitted"),
                    predictions,
                    strict=True,
                )
            ]
        if "prediction" in retained_rows[0]:
            retained_rows = [dict(row["prediction"], role=row["role"]) for row in retained_rows]
        if "role" in retained_rows[0]:
            result["properties"] = property_rows(route, point, result["rows"])
    else:
        retained_rows, objective = reference["rows"], reference["cost"]
    replayed_rows = (
        result["properties"]["rows"] if "properties" in result else result["rows"]
    )
    differences, values = compare_rows(retained_rows, replayed_rows)
    return dict(
        wheel=wheel,
        archive=fit_set["archive"],
        endpoint_fingerprint=fingerprint(point),
        replay=result,
        retained_cost=objective,
        retained_available=sum(row["status"] == "Available" for row in retained_rows),
        replayed_available=sum(row["status"] == "Available" for row in replayed_rows),
        row_differences=differences,
        value_differences=values,
    )


def compare_rows(retained_rows, replayed_rows):
    old = {row["identity"]: row for row in retained_rows}
    new = {row["identity"]: row for row in replayed_rows}
    differences, values = [], []
    for identity in sorted(old.keys() | new.keys()):
        before, after = old.get(identity), new.get(identity)
        if before is None or after is None:
            differences.append(
                dict(
                    identity=identity,
                    retained=before is not None,
                    replayed=after is not None,
                )
            )
            continue
        for field in ("status", "requested_tolerance_met", "role"):
            if field == "requested_tolerance_met" and field not in before:
                continue
            if before.get(field) != after.get(field):
                differences.append(
                    dict(
                        identity=identity,
                        field=field,
                        retained=before.get(field),
                        replayed=after.get(field),
                    )
                )
        if before.get("status") != "Available" or after.get("status") != "Available":
            stop = [(r.get("convergence") or {}).get("stop") for r in (before, after)]
            if stop[0] != stop[1]:
                differences.append(
                    dict(
                        identity=identity,
                        field="stop",
                        retained=stop[0],
                        replayed=stop[1],
                    )
                )
        if before.get("value") != after.get("value"):
            values.append(
                dict(
                    identity=identity,
                    retained=before.get("value"),
                    replayed=after.get("value"),
                )
            )
    return differences, values
