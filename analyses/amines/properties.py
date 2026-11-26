"""Derivative and property readbacks at one declared endpoint."""

import copy
import json
from types import SimpleNamespace

import numpy as np
from epcsaft import regression as reg
from MEA.common.retained_results import read
from MEA.solvent_specification import conditional_information, deviation_statistics

from .wheel import ROOT, verify


def write_gibbs_derivative_summary():
    wheel = verify()
    folder = ROOT / "analyses/fixed_reaction_reference/results/C1"
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
            else not ranges[name][0] <= T <= ranges[name][1]
        )
        for name in used | ranges.keys()
    }


def property_rows(route, point, fitted=None):
    spec, output = route.bind(point), []
    fitted = {} if fitted is None else {row["identity"]: row for row in fitted}
    for role in ("fitted", "comparisons"):
        for record in spec.inputs["observations"][role]:
            T = spec.problems[record.get("problem", record.get("initial"))].T
            prediction = fitted.get(record["identity"]) if role == "fitted" else None
            output.append(
                dict(
                    prediction if prediction is not None else spec.prediction(record),
                    role=record.get("role", "fitted" if role == "fitted" else "not fitted"),
                    T_K=T,
                    outside_ranges=marks(
                        route,
                        T,
                        spec.problems[record.get("problem", record.get("initial"))],
                    ),
                )
            )
    summary = []
    for group, role, unit in sorted({(r["group"], r["role"], r.get("unit") or "unit unspecified") for r in output}):
        for name in {name for r in output for name in r["outside_ranges"]}:
            for outside in (False, True, "source range unknown", "reaction not used"):
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
