"""Stage 2 of #308: Hartono binary fit and frozen aqueous comparisons."""

import csv
import hashlib
import json
import math
import os

import epcsaft
import numpy as np
from epcsaft import equilibrium as eq, regression as reg
from run import AN, SHA, verify_wheel

PZ, W = "piperazine", "water"
SCALES = np.array([0.05, 0.001])


def load_rows(name):
    return list(csv.DictReader((AN / "inputs" / name).open()))


def document():
    shared_path = (
        AN.parent / "mea_parameter_bundle/results/stable-refit-255/evidence/candidate-parameters.json"
    )
    assert (
        hashlib.sha256(shared_path.read_bytes()).hexdigest()
        == "f8f64820b161377a0d97d1e4ad4f6cea764cd0558dc63231d58e2096988eef97"
    )
    shared = json.loads(shared_path.read_text())
    doc = json.loads((AN / "results/refit-parameters.json").read_text())
    doc["components"] += [c for c in shared["components"] if c["component_id"] == W]
    # Neutral binary projection: electrostatic coefficients have no contribution.
    doc["components"][-1]["coefficients"] = [
        c
        for c in doc["components"][-1]["coefficients"]
        if c["family"] in {"segment_count", "dispersion_energy_over_k"}
    ]
    doc["correlations"] = shared["correlations"]
    doc["topology"]["sites"] += [
        s for s in shared["topology"]["sites"] if s["component_id"] == W
    ]
    water_edge = next(
        e
        for e in shared["topology"]["edges"]
        if {e["endpoint_a"]["component_id"], e["endpoint_b"]["component_id"]} == {W}
    )
    pz_edge = doc["topology"]["edges"][0]
    doc["topology"]["edges"].append(water_edge)
    for a, b in [("a", "b"), ("b", "a")]:
        doc["topology"]["edges"].append(
            dict(
                endpoint_a=dict(component_id=PZ, site_id=a),
                endpoint_b=dict(component_id=W, site_id=b),
                source=dict(
                    kind="combining-rule",
                    rule_id="wolbach-sandler",
                    inputs={
                        f: [pz_edge[f]["identity"], water_edge[f]["identity"]]
                        for f in ["energy_over_k", "volume"]
                    },
                ),
            )
        )
    doc["pairs"] = [
        dict(
            component_id_a=PZ,
            component_id_b=W,
            coefficients=[
                dict(
                    identity="pair/pz-water/k",
                    family="k_ij",
                    temperature_law=dict(
                        form="polynomial-plus-reciprocal-temperature",
                        reference_temperature=dict(magnitude=353.15, unit="kelvin"),
                        terms=[
                            dict(
                                power=i,
                                coefficient=dict(
                                    identity=f"pair/pz-water/k{i}",
                                    value=dict(
                                        magnitude=0.0,
                                        unit="dimensionless"
                                        if i == 0
                                        else "1 / kelvin",
                                    ),
                                ),
                            )
                            for i in range(2)
                        ],
                    ),
                )
            ],
        )
    ]
    return doc


def problem(r, tolerance=1e-10):
    x, y, T, P = (float(r[k]) for k in ["x", "y", "T_K", "P_kPa"])
    return eq.problem_from_mapping(
        dict(
            T=T,
            P=dict(free=True, guess=P * 1000),
            feed=dict(basis="amounts", values={PZ: x, W: 1 - x}),
            phases=[
                dict(
                    name="L",
                    kind="liquid",
                    support=[PZ, W],
                    composition_guess={PZ: x, W: 1 - x},
                ),
                dict(
                    name="V",
                    kind="vapor",
                    support=[PZ, W],
                    amount=dict(status="pinned", value=0.0),
                    composition_guess={PZ: y, W: 1 - y},
                ),
            ],
            row_tolerance=tolerance,
        )
    )


def observations(par, rows, pressure_shift=0):
    obs = []
    for r in rows:
        y = float(r["y"])
        obs.extend(
            [
                reg.observation(
                    par,
                    "pressure",
                    problem(r),
                    observed=float(r["P_kPa"]) * 1000 + pressure_shift,
                    form="difference",
                    scale=300.0,
                ),
                reg.observation(
                    par,
                    "mole_fraction",
                    problem(r),
                    phase="V",
                    species=[PZ],
                    observed=y,
                    form="difference",
                    scale=math.hypot(0.01 * y, 0.00005 / math.sqrt(3)),
                ),
            ]
        )
    return obs


def information(par, coords, obs, optimizer):
    d = reg.differentiate(par, coords, obs, optimizer=list(optimizer))
    J = np.array(d.residual_optimizer_gradient).reshape(len(obs), 2)
    _, s, vt = np.linalg.svd(J, full_matrices=False)
    cov = (vt.T / s**2) @ vt * np.outer(SCALES, SCALES)
    se = np.sqrt(np.diag(cov))
    return dict(
        singular_values=s.tolist(),
        right_vectors=vt.tolist(),
        rank=int(np.linalg.matrix_rank(J)),
        covariance=cov.tolist(),
        se=se.tolist(),
        correlation=(cov / np.outer(se, se)).tolist(),
        jacobian=J.tolist(),
    )


def coordinates(par):
    return [
        reg.coordinate(
            par,
            [("temperature_law_coefficient", f"pair/pz-water/k{i}", 1.0)],
            origin=0.0,
            scale=float(s),
            bounds=(-b, b),
        )
        for i, s, b in zip(range(2), SCALES, [0.5, 0.005])
    ]


def fit_controls():
    return reg.FitControls(
        maximum_iterations=100,
        maximum_elapsed_time_seconds=600,
        function_tolerance=1e-10,
        parameter_tolerance=1e-10,
        gradient_tolerance=1e-8,
        workers=int(os.environ["AGENT_HEAVY_CORES"]),
    )


def calculate():
    verify_wheel()
    doc = document()
    par = epcsaft.Parameters.from_mapping(doc)
    rows = load_rows("hartono-table6.csv")
    fitted_rows = [r for r in rows if r["role"] == "calibration"]
    assert len(fitted_rows) == 23
    coords = coordinates(par)
    obs = observations(par, fitted_rows)
    controls = fit_controls()
    log = dict(wheel_sha256=SHA, starts=[])
    for k0 in [-0.10, -0.15]:
        start_doc = document()
        start_doc["pairs"][0]["coefficients"][0]["temperature_law"]["terms"][0][
            "coefficient"
        ]["value"]["magnitude"] = k0
        start_model = epcsaft.Mixture(epcsaft.Parameters.from_mapping(start_doc))
        initial_pressures = []
        for row in fitted_rows:
            solved = eq.solve_equilibrium(start_model, problem(row))
            assert solved.requested_tolerance_met and solved.pressure is not None, (
                k0,
                row,
                solved.message,
            )
            initial_pressures.append(solved.pressure)
        initial = [k0 / 0.05, 0.0]
        info = information(par, coords, obs, initial)
        # Native differentiation admits each observation only after an admissible solve.
        result = reg.fit(
            par, coords, obs, controls=controls, singular_vectors=True, starts=[initial]
        )[0]
        record = dict(
            start=[k0, 0.0],
            initial_pressure_Pa=initial_pressures,
            status=result.status,
            usable=result.usable,
            message=result.message,
            optimizer=list(result.optimizer),
            cost=result.final_cost,
            iterations=result.iterations,
            active_bounds=list(result.covariance.active_bounds),
            initial_information=info,
        )
        if result.usable:
            record["values"] = (np.array(result.optimizer) * SCALES).tolist()
            record["information"] = information(par, coords, obs, result.optimizer)
        log["starts"].append(record)
        (AN / "results/binary-calibration.json").write_text(
            json.dumps(log, indent=2) + "\n"
        )
        print(
            json.dumps(
                {
                    k: v
                    for k, v in record.items()
                    if k not in ["initial_information", "information"]
                }
            ),
            flush=True,
        )
        if result.usable:
            endpoint_doc = document()
            for term, value in zip(
                endpoint_doc["pairs"][0]["coefficients"][0]["temperature_law"]["terms"],
                record["values"],
                strict=True,
            ):
                term["coefficient"]["value"]["magnitude"] = value
            (AN / f"results/binary-endpoint-{abs(k0):.2f}.json").write_text(
                json.dumps(endpoint_doc, indent=2) + "\n"
            )

    log["common_pressure_sensitivity"] = []
    for shift in [-300.0, 300.0]:
        result = reg.fit(
            par,
            coords,
            observations(par, fitted_rows, shift),
            controls=controls,
            starts=[log["starts"][0]["optimizer"]],
        )[0]
        log["common_pressure_sensitivity"].append(
            dict(
                shift_Pa=shift,
                status=result.status,
                values=(np.array(result.optimizer) * SCALES).tolist(),
                cost=result.final_cost,
            )
        )
    (AN / "results/binary-calibration.json").write_text(
        json.dumps(log, indent=2) + "\n"
    )


if __name__ == "__main__":
    calculate()
