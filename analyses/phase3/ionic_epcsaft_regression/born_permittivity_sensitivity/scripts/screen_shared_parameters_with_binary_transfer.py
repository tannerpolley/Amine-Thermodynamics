from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import json
import math

import numpy as np

from evaluate_co2_water_kij_transfer import PARAMETERS, RESULTS, _mapping_at_temperature
from run_full_predictive_refinement import (
    ACTIVE,
    BOUNDS,
    _compile_pressure,
    _compile_speciation,
    _pressure_rows,
    _speciation_states,
)
from MEA.epcsaft_ionic.parameter_document import materialize_parameter_candidate


OUTPUT = RESULTS.parent / "co2_water_kij_transfer_shared_parameter_screen"


def main() -> None:
    mapping = materialize_parameter_candidate(PARAMETERS)
    pressure = [row for row in _pressure_rows() if row["analysis_role"] == "training"]
    speciation = _speciation_states("active_training")
    pressure_payloads = [
        (_mapping_at_temperature(mapping, float(row["temperature_K"])), row)
        for row in pressure
    ]
    speciation_payloads = [
        (_mapping_at_temperature(mapping, float(state["temperature_k"])), state)
        for state in speciation
    ]
    with ProcessPoolExecutor(max_workers=12) as pool:
        pressure_results = list(pool.map(_compile_pressure, pressure_payloads))
        speciation_results = list(pool.map(_compile_speciation, speciation_payloads))
    diagnostics = [item for _, item in (*pressure_results, *speciation_results)]
    failures = [row for row in diagnostics if row["status"] != "evaluated"]
    if failures:
        raise RuntimeError(f"{len(failures)} training states were not evaluated")

    pressure_targets = [
        (
            math.log(float(row["predicted"]) / float(row["observed"])),
            np.asarray(row["jacobian"], dtype=float) / float(row["predicted"]),
        )
        for _, row in pressure_results
    ]
    speciation_targets = [
        (
            math.log(float(target["predicted"]) / float(target["observed"])),
            np.asarray(target["jacobian"], dtype=float) / float(target["predicted"]),
        )
        for _, state in speciation_results
        for target in state["targets"]
    ]
    weighted = [
        (residual / math.sqrt(len(block)), jacobian / math.sqrt(len(block)))
        for block in (pressure_targets, speciation_targets)
        for residual, jacobian in block
    ]
    residual = np.asarray([row[0] for row in weighted])
    jacobian = np.vstack([row[1][1:] for row in weighted])
    step, *_ = np.linalg.lstsq(jacobian, -residual, rcond=None)
    origins = np.asarray(
        [
            next(
                coefficient["value"]["magnitude"]
                for container in (*mapping["components"], *mapping["pairs"])
                for coefficient in container["coefficients"]
                if coefficient["identity"] == identity
            )
            for identity in ACTIVE[1:]
        ]
    )
    lower = np.asarray([bounds[0] for bounds in BOUNDS[1:]])
    upper = np.asarray([bounds[1] for bounds in BOUNDS[1:]])
    candidate = np.clip(origins + step, lower, upper)
    linearized = residual + jacobian @ (candidate - origins)
    singular_values = np.linalg.svd(jacobian, compute_uv=False)
    summary = {
        "schema": "mea.co2-water-kij-transfer-shared-parameter-screen.v1",
        "status": "completed",
        "state_count": len(diagnostics),
        "target_count": len(weighted),
        "failure_count": 0,
        "active_identities": list(ACTIVE[1:]),
        "origins": origins.tolist(),
        "gauss_newton_step": step.tolist(),
        "candidate": candidate.tolist(),
        "baseline_balanced_log_rmse": float(np.sqrt(np.mean(residual**2))),
        "linearized_candidate_balanced_log_rmse": float(
            np.sqrt(np.mean(linearized**2))
        ),
        "singular_values": singular_values.tolist(),
        "condition_number": float(singular_values[0] / singular_values[-1]),
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
