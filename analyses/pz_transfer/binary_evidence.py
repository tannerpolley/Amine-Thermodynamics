"""Endpoint residual diagnosis and declared liquid/vapor phase trials for #308."""

import copy
import json
import math
import tomllib

import epcsaft
from epcsaft import equilibrium as eq, regression as reg
from binary import AN, PZ, W, SCALES, document, load_rows, observations, problem
from run import verify_wheel, write_csv


def jsonable(value):
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if hasattr(value, "name"):
        return value.name
    return [jsonable(v) for v in value]


def parameters(values):
    doc = document()
    for term, value in zip(
        doc["pairs"][0]["coefficients"][0]["temperature_law"]["terms"],
        values,
        strict=True,
    ):
        term["coefficient"]["value"]["magnitude"] = float(value)
    return epcsaft.Parameters.from_mapping(doc)


def predictions(par, rows):
    model = epcsaft.Mixture(par)
    result = [reg.predict(model, o) for o in observations(par, rows)]
    assert all(
        p.status.name == "Available" and p.requested_tolerance_met for p in result
    )
    return [p.value for p in result], [p.residual for p in result]


def phase_report(par, prob, r):
    model = epcsaft.Mixture(par)
    sol = eq.solve_equilibrium(model, prob)
    policy = tomllib.loads(
        (AN.parent / "solvent_specification_mdea/B1-declarations.toml").read_text()
    )["phase_policy"]
    trials = copy.copy(prob)
    trials.phases = [
        eq.Phase("trial-L", kind="liquid", support=[PZ, W]),
        eq.Phase("trial-V", kind="vapor", support=[PZ, W]),
    ]
    options = eq.StabilityOptions()
    assert options.mode.name == "Full"
    options.trials = trials._native(model).phases
    native = eq.stability_test(eq.compile_problem(model, prob), sol, options)
    report = {
        k: jsonable(getattr(native, k))
        for k in ["completed", "message", "present_phases", "work"]
    }
    report.update(
        mode=options.mode.name,
        classifier_owner="analyses/solvent_specification_mdea/B1-declarations.toml:phase_policy",
        row=r["row"],
        T_K=r["T_K"],
        x=r["x"],
        pressure_Pa=sol.pressure,
        dense=[],
        gas=[],
        ambiguous=[],
        unresolved=[],
        trials=[],
    )
    for t in native.trials:
        item = {
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
        item["phase_kind"] = t.phase.kind.name
        item["optimizer_status"] = t.optimizer.solver_status
        item["optimizer_success"] = t.optimizer.success
        if t.resolved_descent:
            if t.split_coordinates and math.isfinite(t.split_coordinates[-1]):
                eta = math.exp(t.split_coordinates[-1])
                item["packing_fraction"] = eta
                report[
                    "dense" if eta >= policy["packing_fraction_threshold"] else "gas"
                ].append(t.seed)
                if (
                    policy["ambiguity_interval"][0]
                    < eta
                    < policy["ambiguity_interval"][1]
                ):
                    report["ambiguous"].append(t.seed)
            else:
                report["unresolved"].append(t.seed)
        if (
            t.evidence
            in ["unresolved", "indeterminate", "negative_plane_without_positive_donor"]
            or not t.optimizer.success
        ):
            report["unresolved"].append(t.seed)
        report["trials"].append(item)
    report["passed"] = (
        native.completed
        and sol.requested_tolerance_met
        and {t.phase.kind.name for t in native.trials} == {"Liquid", "Vapor"}
        and not any(report[k] for k in ["dense", "gas", "ambiguous", "unresolved"])
    )
    return report


def calculate():
    verify_wheel()
    log = json.loads((AN / "results/binary-calibration.json").read_text())
    selected = log["starts"][0]
    values = selected["values"]
    par = parameters(values)
    model = epcsaft.Mixture(par)
    rows = load_rows("hartono-table6.csv")
    residuals = []
    for r in rows:
        pred, res = predictions(par, [r])
        P, y = pred
        sol = eq.solve_equilibrium(model, problem(r))
        refined = eq.solve_equilibrium(model, problem(r, 1e-12))
        rr = dict(
            r,
            predicted_P_kPa=P / 1000,
            predicted_y=y,
            predicted_pPZ_Pa=P * y,
            P_source_units=res[0],
            y_source_units=res[1],
            P_difference_kPa=P / 1000 - float(r["P_kPa"]),
            y_difference=y - float(r["y"]),
            P_relative_percent=100 * (P / (float(r["P_kPa"]) * 1000) - 1),
            y_relative_percent=100 * (y / float(r["y"]) - 1),
            P_outside_source_scale_kPa=abs(P / 1000 - float(r["P_kPa"])) - 0.3,
            y_outside_source_scale=abs(y - float(r["y"]))
            - math.hypot(0.01 * float(r["y"]), 0.00005 / math.sqrt(3)),
            max_equation_residual=max(map(abs, sol.residuals)),
            P_refinement_source_units=abs(refined.pressure - P) / 300,
        )
        for key, delta in [
            ("T_K", 0.05),
            ("x", math.hypot(0.01 * float(r["x"]), 0.00005 / math.sqrt(3))),
        ]:
            shifted = dict(r)
            shifted[key] = float(r[key]) + delta
            _, sr = predictions(par, [shifted])
            rr[key + "_sensitivity_P_source_units"] = sr[0] - res[0]
            rr[key + "_sensitivity_y_source_units"] = sr[1] - res[1]
        residuals.append(rr)
    write_csv("binary-calibration-residuals.csv", residuals)
    fitrows = [r for r in rows if r["role"] == "calibration"]
    exact = selected["information"]["jacobian"]
    import numpy as np

    fd = []
    for step in [1e-4, 5e-5]:
        columns = []
        for j in range(2):
            endpoints = []
            for sign in [-1, 1]:
                shifted = np.array(values)
                shifted[j] += sign * step * SCALES[j]
                endpoints.append(np.array(predictions(parameters(shifted), fitrows)[1]))
            columns.append((endpoints[1] - endpoints[0]) / (2 * step))
        J = np.array(columns).T
        fd.append(
            dict(
                step_optimizer=step,
                singular_values=np.linalg.svd(J, compute_uv=False).tolist(),
                max_abs_J_difference=float(np.max(abs(J - np.array(exact)))),
            )
        )
    (AN / "results/binary-derivative-check.json").write_text(
        json.dumps(fd, indent=2) + "\n"
    )
    phases = []
    for r in fitrows:
        prob = problem(r)
        sol = eq.solve_equilibrium(model, prob)
        report = phase_report(par, prob, r)
        phases.append(report)
        (AN / "results/binary-calibration-phases.json").write_text(
            json.dumps(phases, indent=2) + "\n"
        )
        print(
            json.dumps(
                {
                    k: report[k]
                    for k in [
                        "row",
                        "completed",
                        "passed",
                        "dense",
                        "gas",
                        "ambiguous",
                        "unresolved",
                        "message",
                    ]
                }
            ),
            flush=True,
        )

    w = 0.1001
    x = (w / 0.08613) / (w / 0.08613 + (1 - w) / 0.01801528)
    r = dict(row="Concepcion-393.15", T_K=393.15, x=x, y=0.001, P_kPa=100.0)
    sol = eq.solve_equilibrium(model, problem(r))
    reports = []
    for P in [100000.0, 500000.0]:
        prob = eq.Problem(
            T=393.15,
            P=P,
            feed=eq.Amounts({PZ: x, W: 1 - x}),
            phases=[eq.Phase("L", kind="liquid", support=[PZ, W])],
            row_tolerance=1e-12,
        )
        reports.append(phase_report(par, prob, r))
    (AN / "results/binary-density-phase-diagnosis.json").write_text(
        json.dumps(
            dict(bubble_pressure_Pa=sol.pressure, x=x, reports=reports), indent=2
        )
        + "\n"
    )


if __name__ == "__main__":
    calculate()
