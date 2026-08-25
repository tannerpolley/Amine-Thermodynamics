from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import json
import math

from evaluate_co2_water_kij_transfer import (
    PARAMETERS,
    RESULTS,
    _mapping_at_temperature,
)
from run_full_predictive_refinement import _compile_pressure, _pressure_rows
from MEA.epcsaft_ionic.parameter_document import materialize_parameter_candidate


OUTPUT = RESULTS.parent / "co2_water_kij_transfer_k_co2_mea_screen"


def main() -> None:
    mapping = materialize_parameter_candidate(PARAMETERS)
    rows = [row for row in _pressure_rows() if row["analysis_role"] == "training"]
    payloads = [
        (_mapping_at_temperature(mapping, float(row["temperature_K"])), row)
        for row in rows
    ]
    with ProcessPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(_compile_pressure, payloads))
    diagnostics = [diagnostic for _, diagnostic in results]
    failures = [row for row in diagnostics if row["status"] != "evaluated"]
    if failures:
        raise RuntimeError(
            f"{len(failures)} training pressure states were not evaluated"
        )

    residuals = [
        math.log(float(row["predicted"]) / float(row["observed"]))
        for row in diagnostics
    ]
    derivatives = [
        float(row["jacobian"][0]) / float(row["predicted"]) for row in diagnostics
    ]
    step = -math.fsum(
        d * r for d, r in zip(derivatives, residuals, strict=True)
    ) / math.fsum(d * d for d in derivatives)
    current = next(
        coefficient["value"]["magnitude"]
        for pair in mapping["pairs"]
        for coefficient in pair["coefficients"]
        if coefficient["identity"] == "pair/carbon-dioxide/monoethanolamine/k_ij"
    )
    candidate = min(1.0, max(-1.0, current + step))
    linearized = [
        r + d * (candidate - current)
        for r, d in zip(residuals, derivatives, strict=True)
    ]
    summary = {
        "schema": "mea.co2-water-kij-transfer-k-co2-mea-screen.v1",
        "status": "completed",
        "state_count": len(diagnostics),
        "failure_count": 0,
        "current_k_co2_mea": current,
        "gauss_newton_step": step,
        "candidate_k_co2_mea": candidate,
        "baseline_log_rmse": math.sqrt(
            math.fsum(r * r for r in residuals) / len(residuals)
        ),
        "linearized_candidate_log_rmse": math.sqrt(
            math.fsum(r * r for r in linearized) / len(linearized)
        ),
        "derivative_min": min(derivatives),
        "derivative_max": max(derivatives),
        "derivative_rms": math.sqrt(
            math.fsum(d * d for d in derivatives) / len(derivatives)
        ),
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
