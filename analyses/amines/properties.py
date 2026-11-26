"""Derivative and property readbacks at one declared endpoint."""

import copy
from types import SimpleNamespace

import numpy as np
from epcsaft import regression as reg
from MEA.solvent_specification import conditional_information, deviation_statistics

from .wheel import verify


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
                    role=record["role"],
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
