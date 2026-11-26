"""Reported fit starts, attempts, selection and replay."""

import csv
import gzip
from hashlib import sha256
import json
import os
from time import monotonic

from .model import replay, row_manifest, with_parameter_values
from .properties import endpoint_diagnostics, property_rows
from .wheel import verify
from MEA.common.retained_results import read
from MEA.solvent_specification import jsonable


def fingerprint(point):
    return sha256(json.dumps(jsonable(point), sort_keys=True, allow_nan=False).encode()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(jsonable(value), allow_nan=False, indent=2) + "\n").encode()
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(gzip.compress(data, mtime=0) if path.suffix == ".gz" else data)
    tmp.replace(path)


def manifest(fit_set):
    wheel = verify()
    path = fit_set["retained"]
    declaration = read(path / "manifest.json.gz")
    if declaration["wheel"] != wheel:
        raise ValueError(f"{path}: fit manifest wheel differs from the installed wheel")
    replacement = path / "replacement-starts.json.gz"
    starts = declaration["starts"]
    if replacement.is_file():
        extra = read(replacement)
        if extra["wheel"] != wheel or extra["manifest_fingerprint"] != fingerprint(declaration):
            raise ValueError(f"{replacement}: replacement starts do not belong to the fit manifest")
        starts = starts | {k: v["start"] for k, v in extra["draws"].items() if v["disposition"] == "eligible"}
    diagnostic_starts = {}
    for source in fit_set.get("diagnostic_attempts", ()):
        data = read(path / source)
        label = data["start"]
        if data["wheel"] != wheel or data["manifest_fingerprint"] != fingerprint(declaration):
            raise ValueError(f"{label}: additional start does not belong to the fit manifest")
        diagnostic_starts[label] = dict(optimizer=data["optimizer_start"], controls=data["controls"])
    return dict(declaration, starts=starts, diagnostic_starts=diagnostic_starts)


def route_for(fit_set):
    return fit_set["route"](fit_set["declaration"], reference_pressure_pa=fit_set["reference_pressure_pa"])


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
    spec = route_for(fit_set).bind(point)
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
    measured = row_manifest(route_for(fit_set).bind(declaration["start_A_declaration"]))
    if measured != declaration["rows"]:
        raise ValueError(f"{fit_set['retained']}: changed start-state row declarations")
    return dict(wheel=verify(), rows=measured)


def attempt(fit_set, declaration, label, path, *, previous=None):
    wheel = verify()
    route = route_for(fit_set)
    point = declaration["start_A_declaration"]
    start = (declaration["starts"] | declaration["diagnostic_starts"])[label]
    controls = start.get("controls", declaration["fit_controls"]) | dict(workers=int(os.environ["AGENT_HEAVY_CORES"]))
    controls.setdefault("maximum_elapsed_time_seconds", fit_set["maximum_seconds"])
    u = start["optimizer"]
    manifest_id = fingerprint(declaration)
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
    spec = route.bind(point)
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
    save(path, record)
    if report["physical"] and report["reactions"]:
        endpoint = route.endpoint_mapping(point, report, point["coordinates"])
        record.update(endpoint=endpoint, endpoint_fingerprint=fingerprint(endpoint))
        save(path, record)
        tick = monotonic()
        bound = route.bind(endpoint)
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
    while stages < 3 and record["report"]["status"] == "limit_reached" and record.get("replay_passed"):
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
    reference_path = fit_set["reference"]
    if reference_path.suffix == ".csv":
        with reference_path.open(newline="") as stream:
            reference = list(csv.DictReader(stream))
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
