from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import pandas as pd

from MEA.epcsaft_ionic.parameter_document import COMPONENT_IDS, parameter_mapping
from MEA.epcsaft_ionic.reactive_problem import build_homogeneous_reactive_problem


ROOT = Path(__file__).resolve().parents[5]
ANALYSIS = ROOT / "analyses/phase3/ionic_epcsaft_regression/pressure_first"
RESULTS = ANALYSIS / "results"
PACKET = RESULTS / "pressure_candidate_packet.csv"
CONFIG = ANALYSIS / "config/preregistration.json"
PREDICTIONS = RESULTS / "fixed_pressure_fugacity_screen_predictions.csv"
RECEIPT = RESULTS / "fixed_pressure_fugacity_screen_evaluation_receipt.json"
ACTIVE_IDENTITY = "pair/carbon-dioxide/water/k_ij"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True).encode()
    ).hexdigest()


def main() -> None:
    import epcsaft
    from epcsaft import equilibrium

    config = json.loads(CONFIG.read_text())
    packet = pd.read_csv(PACKET)
    screen_ids = tuple(config["diagnostic_screen"]["retained_point_row_ids"])
    screen = packet.set_index("observation_id").loc[list(screen_ids)].reset_index()
    parameters = epcsaft.Parameters.from_mapping(
        parameter_mapping(), components=COMPONENT_IDS
    )
    active = epcsaft.ActiveParameterSet(parameters, (ACTIVE_IDENTITY,), values=(0.0,))
    started = time.monotonic()
    output_rows: list[dict[str, object]] = []
    branch_fingerprints: list[str] = []
    for row in screen.to_dict("records"):
        problem = build_homogeneous_reactive_problem(
            parameters,
            identity=f"pressure-screen-liquid-{row['observation_id']}",
            phase_identity="mea-nine-species-liquid",
            continuation_identity=f"pressure-screen-local-{row['observation_id']}",
            temperature_k=float(row["temperature_K"]),
            pressure_pa=float(row["state_pressure_pa"]),
            mea_mass_fraction_unloaded=float(row["mea_mass_fraction"]),
            loading_mol_co2_per_mol_mea=float(row["co2_loading_mol_per_mol_mea"]),
            maximum_log_composition_distance=2.0,
            maximum_log_volume_distance=2.0,
        )
        observation = equilibrium.HomogeneousReactiveObservationRow(
            f"{row['observation_id']}-co2-liquid-fugacity",
            "fugacity_pa",
            (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
            support="positive",
        )
        descriptor = equilibrium.homogeneous_reactive_observation_descriptor(
            problem, (observation,), active_parameters=active
        )
        result = equilibrium.evaluate_homogeneous_reactive_observations(
            problem,
            float(row["temperature_K"]) * epcsaft.unit_registry.kelvin,
            float(row["state_pressure_pa"]) * epcsaft.unit_registry.pascal,
            descriptor,
            active_parameters=active,
        )
        if result.status != "evaluated" or result.physical_branch is None:
            code = None if result.failure is None else result.failure.code
            raise RuntimeError(f"closure row {row['observation_id']} rejected: {code}")
        predicted = result.rows[0]
        if predicted.value is None or predicted.jacobian is None:
            raise RuntimeError("evaluated closure row has no value/Jacobian")
        branch_fingerprints.append(result.physical_branch.identity)
        output_rows.append(
            {
                **{
                    key: row[key]
                    for key in (
                        "observation_id",
                        "source_key",
                        "canonical_row_identity",
                        "temperature_K",
                        "mea_mass_fraction",
                        "co2_loading_mol_per_mol_mea",
                        "measurement_role",
                        "measurement_equation",
                        "observed_pco2_pa",
                        "state_pressure_pa",
                        "residual_scale_log10",
                        "analysis_role",
                    )
                },
                "modeled_quantity": "liquid_CO2_fugacity_at_observed_T_and_total_P",
                "modeled_quantity_unit": "Pa",
                "modeled_liquid_co2_fugacity_pa": predicted.value,
                "exact_d_fugacity_d_kij_pa": predicted.jacobian[0],
                "closure_residual_log10_fugacity_over_observed_pco2": math.log10(
                    predicted.value / float(row["observed_pco2_pa"])
                ),
                "evaluated_kij_co2_water": 0.0,
                "parameter_status": "unfitted_preregistered_origin",
                "pressure_prediction_status": "not_computed_observed_pressure_is_input",
                "claim_status": "diagnostic_non_promotable",
            }
        )
    pd.DataFrame(output_rows).to_csv(PREDICTIONS, index=False, lineterminator="\n")
    receipt = {
        "schema_version": 1,
        "identity": "mea-fixed-pressure-closure-evaluation-v1",
        "parameter": {
            "identity": ACTIVE_IDENTITY,
            "value": 0.0,
            "unit": "dimensionless",
            "status": "unfitted_preregistered_origin",
            "active_parameter_fingerprint": active.fingerprint,
        },
        "row_ids": list(screen_ids),
        "evaluated_rows": len(output_rows),
        "runtime_seconds": time.monotonic() - started,
        "physical_branch_fingerprints": branch_fingerprints,
        "prediction_table_sha256": _sha256(PREDICTIONS),
        "scientific_meaning": (
            "Exact liquid-fugacity values and total parameter derivatives at observed "
            "total pressure. No parameter was fitted and no PCO2 pressure was predicted."
        ),
    }
    receipt["receipt_sha256"] = _canonical_sha256(receipt)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(PREDICTIONS.relative_to(ROOT), _sha256(PREDICTIONS))
    print(RECEIPT.relative_to(ROOT), receipt["receipt_sha256"])


if __name__ == "__main__":
    main()
