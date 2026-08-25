from __future__ import annotations

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor
from importlib.metadata import distribution
import hashlib
import json
import math
import os
from pathlib import Path
import statistics

import epcsaft
from epcsaft import equilibrium

from evaluate_anchored_co2_water_kij import K_SLOPE_PER_K, _mapping
from evaluate_co2_water_kij_transfer import PARAMETERS, _write_csv
from generate import ANALYSIS, COMPONENT_IDS
from run_full_predictive_refinement import _liquid
from MEA.epcsaft_ionic.parameter_document import materialize_parameter_candidate


REPO = ANALYSIS.parents[3]
SOURCE = (
    REPO
    / "data/reference/MEA/observations/vapor_liquid_equilibrium/"
    "Wong_2016_Raman_loading_comparison.csv"
)
OUTPUT = ANALYSIS / "results/new_source_replay"


def _rows() -> list[dict[str, object]]:
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        source_rows = list(csv.DictReader(stream))
    rows: list[dict[str, object]] = []
    for index, row in enumerate(source_rows, start=1):
        for loading_basis, column in (
            ("pressure_drop", "co2_loading_pressure_drop"),
            ("raman", "co2_loading_raman"),
        ):
            rows.append(
                {
                    "identity": f"Wong2016_Table4_{index:02d}_{loading_basis}",
                    "loading_basis": loading_basis,
                    "temperature_k": float(row["temperature_K"]),
                    "mea_mass_fraction": float(row["mea_mass_fraction"]),
                    "loading": float(row[column]),
                    "observed_pressure_pa": float(row["pressure_bar"]) * 100_000.0,
                }
            )
    return rows


def _evaluate(payload: tuple[dict[str, object], dict[str, object]]) -> dict[str, object]:
    mapping, row = payload
    try:
        parameters = epcsaft.Parameters.from_mapping(mapping, components=COMPONENT_IDS)
        identity = str(row["identity"])
        temperature_k = float(row["temperature_k"])
        observed_pressure_pa = float(row["observed_pressure_pa"])
        liquid = _liquid(
            parameters,
            identity=identity,
            temperature_k=temperature_k,
            pressure_pa=observed_pressure_pa,
            loading=float(row["loading"]),
            mea_mass_fraction=float(row["mea_mass_fraction"]),
        )
        problem = equilibrium.GeneralReactiveEquilibriumProblem(
            identity=identity,
            temperature=equilibrium.Fixed(
                temperature_k * epcsaft.unit_registry.kelvin
            ),
            pressure=equilibrium.Solved(
                observed_pressure_pa * epcsaft.unit_registry.pascal,
                (
                    10.0 * epcsaft.unit_registry.pascal,
                    6_000_000.0 * epcsaft.unit_registry.pascal,
                ),
                (observed_pressure_pa * epcsaft.unit_registry.pascal,),
            ),
            phases=(
                equilibrium.ReactivePhase(
                    liquid.phase_identity,
                    "liquid",
                    "finite",
                    equilibrium.AllComponents(),
                    equilibrium.ProviderModel(
                        liquid.phase.admissible_packing_fraction_interval,
                        "installed-provider-eos",
                    ),
                    liquid.continuation_identity,
                    liquid.branch_policy,
                    liquid.continuation_reference,
                ),
                equilibrium.ReactivePhase(
                    "mea-three-neutral-vapor",
                    "vapor",
                    "incipient",
                    equilibrium.DeclaredNeutralComponents(
                        ("carbon-dioxide", "monoethanolamine", "water")
                    ),
                    equilibrium.IdealGasModel("provider-helmholtz-coordinate-basis"),
                ),
            ),
            reaction_system=liquid.reaction_system,
            reaction_phase_ids=(liquid.phase_identity,),
            outputs=(
                equilibrium.EquilibriumOutput(
                    "total-pressure",
                    "system.pressure",
                    "pascal",
                    "equilibrium-total-pressure",
                    support="positive",
                ),
                equilibrium.EquilibriumOutput(
                    "carbon-dioxide-partial-pressure",
                    "phase.partial_pressure",
                    "pascal",
                    "true-species-vapor-partial-pressure",
                    "mea-three-neutral-vapor",
                    (1.0, 0.0, 0.0),
                    support="positive",
                ),
            ),
            continuation_identity=f"{identity}-bubble",
        )
        result = equilibrium.phase_equilibrium(epcsaft.Mixture(parameters), problem)
        if result.status != "evaluated" or any(value is None for value in result.values):
            raise RuntimeError(str(result.failure or "bubble state was non-evaluable"))
        predicted_pressure_pa, predicted_pco2_pa = map(float, result.values)
        return row | {
            "status": "evaluated",
            "predicted_pressure_pa": predicted_pressure_pa,
            "predicted_pco2_pa": predicted_pco2_pa,
            "pressure_factor": max(
                predicted_pressure_pa / observed_pressure_pa,
                observed_pressure_pa / predicted_pressure_pa,
            ),
            "log_residual": math.log(predicted_pressure_pa / observed_pressure_pa),
            "k_co2_water": K_SLOPE_PER_K * (temperature_k - 313.15),
        }
    except Exception as error:
        return row | {"status": "failed", "failure_reason": str(error)}


def _metrics(rows: list[dict[str, object]]) -> dict[str, float | int]:
    residuals = [float(row["log_residual"]) for row in rows]
    rmse = math.sqrt(math.fsum(value * value for value in residuals) / len(residuals))
    return {
        "state_count": len(rows),
        "log_rmse": rmse,
        "rms_factor": math.exp(rmse),
        "median_factor": math.exp(statistics.median(map(abs, residuals))),
        "mean_log_bias": statistics.fmean(residuals),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=os.process_cpu_count() or 1)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    mapping = materialize_parameter_candidate(PARAMETERS)
    rows = _rows()
    payloads = [
        (_mapping(mapping, float(row["temperature_k"])), row) for row in rows
    ]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(_evaluate, payloads))
    evaluated = [row for row in results if row["status"] == "evaluated"]
    failures = [row for row in results if row["status"] != "evaluated"]
    metric_rows = [
        {"loading_basis": basis} | _metrics(
            [row for row in evaluated if row["loading_basis"] == basis]
        )
        for basis in ("pressure_drop", "raman")
    ]
    wheel_path = Path(
        json.loads(distribution("epcsaft").read_text("direct_url.json"))["url"]
        .removeprefix("file://")
    )
    admission = [
        {
            "source_block": "Wong 2016 Table 4 pressure/loading",
            "row_count": 27,
            "status": "external_challenge_omitted_internal_standard_salt",
            "reason": "state inputs are explicit, but the source added 0.517 mol/kg NaClO4 and the nine-species model omits Na+ and ClO4-",
        },
        {
            "source_block": "Wong 2016 Figures 5-6 Raman speciation",
            "row_count": 101,
            "status": "held_out_missing_state_pressure",
            "reason": "digitized figure rows do not identify the pressure paired with each loading",
        },
        {
            "source_block": "Fan 2009 Figure 3 NMR speciation",
            "row_count": 23,
            "status": "held_out_missing_feed_conversion",
            "reason": "5.0 mol/L unloaded MEA needs source solution density to become an exact mass-fraction feed",
        },
        {
            "source_block": "du Preez 2019 Figure 7 ATR-FTIR carbamate",
            "row_count": 18,
            "status": "held_out_missing_feed_conversion",
            "reason": "0.33 mol/L unloaded MEA and mol/L carbamate need source solution density",
        },
        {
            "source_block": "MEA heat of absorption",
            "row_count": 158,
            "status": "held_out_missing_complete_model_observable",
            "reason": "Engine exposes residual EOS enthalpy but not complete reaction, ideal, and reference-state absorption enthalpy",
        },
    ]
    summary = {
        "schema": "mea.new-source-frozen-replay.v1",
        "status": "completed" if not failures else "completed_with_failures",
        "source": "Wong et al. (2016), Table 4, DOI 10.1039/C5RA22926J",
        "model_role": "frozen independent validation; no parameters fitted",
        "source_system_difference": "all source MEA solutions contained 0.517 mol/kg NaClO4; the replay omits Na+ and ClO4-",
        "evaluated_state_count": len(evaluated),
        "failure_count": len(failures),
        "metrics": metric_rows,
        "engine_wheel_sha256": hashlib.sha256(wheel_path.read_bytes()).hexdigest(),
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    _write_csv(OUTPUT / "predictions.csv", results)
    _write_csv(OUTPUT / "metrics.csv", metric_rows)
    _write_csv(OUTPUT / "source_admission.csv", admission)
    (OUTPUT / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
