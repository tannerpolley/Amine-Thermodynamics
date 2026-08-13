from __future__ import annotations

import csv
import hashlib
import json
import time
from pathlib import Path
from typing import Any, cast

import epcsaft
from epcsaft import regression

from MEA.epcsaft_ionic.parameter_document import COMPONENT_IDS, parameter_mapping
from MEA.epcsaft_ionic.reactive_problem import build_homogeneous_reactive_problem


ROOT = Path(__file__).resolve().parents[5]
ANALYSIS = ROOT / "analyses/phase3/ionic_epcsaft_regression/pressure_first"
RESULTS = ANALYSIS / "results"
PACKET = RESULTS / "pressure_candidate_packet.csv"
FIT_INPUT = RESULTS / "fixed_pressure_fugacity_screen_fit.json"
FIT_RESULT = RESULTS / "fixed_pressure_fugacity_screen_result.json"
FIT_RECEIPT = RESULTS / "fixed_pressure_fugacity_screen_receipt.json"
ENGINE_LOCK = ROOT / "data/reference/MEA/manifests/engine_artifact_lock.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True).encode()
    ).hexdigest()


def main() -> None:
    packet = {
        row["observation_id"]: row
        for row in csv.DictReader(PACKET.open(newline="", encoding="utf-8"))
    }
    fit_input = cast(dict[str, Any], json.loads(FIT_INPUT.read_text(encoding="utf-8")))
    parameters = epcsaft.Parameters.from_mapping(
        parameter_mapping(), components=COMPONENT_IDS
    )
    anchor_seconds: dict[str, float] = {}
    for observation in fit_input["observations"]:
        row_id = str(observation["identity"]).removeprefix("pressure-screen-batch-")
        row = packet[row_id]
        started = time.monotonic()
        problem = build_homogeneous_reactive_problem(
            parameters,
            identity=str(observation["identity"]),
            phase_identity=str(observation["phase"]["identity"]),
            continuation_identity=str(observation["continuation"]["identity"]),
            temperature_k=float(row["temperature_K"]),
            pressure_pa=float(row["state_pressure_pa"]),
            mea_mass_fraction_unloaded=float(row["mea_mass_fraction"]),
            loading_mol_co2_per_mol_mea=float(
                row["co2_loading_mol_per_mol_mea"]
            ),
            maximum_log_composition_distance=float(
                observation["continuation"]["reference"][
                    "maximum_log_composition_distance"
                ]
            ),
            maximum_log_volume_distance=float(
                observation["continuation"]["reference"][
                    "maximum_log_volume_distance"
                ]
            ),
        )
        if problem.continuation_reference is None:
            raise RuntimeError(f"{row_id} returned no continuation reference")
        observation["continuation"]["reference"] = (
            problem.continuation_reference.to_mapping()
        )
        anchor_seconds[row_id] = time.monotonic() - started

    FIT_INPUT.write_text(
        json.dumps(fit_input, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    fit_started = time.monotonic()
    result = regression.fit(fit_input, base_path=ROOT)
    fit_seconds = time.monotonic() - fit_started
    result.to_json(FIT_RESULT)
    accepted = result.accepted_start
    engine_lock = json.loads(ENGINE_LOCK.read_text(encoding="utf-8"))
    receipt: dict[str, object] = {
        "schema_version": 1,
        "identity": "mea-fixed-pressure-regression-result-v1",
        "claim_status": "diagnostic_non_promotable_observed_pressure_is_input",
        "engine": {
            "commit": engine_lock["engine_commit"],
            "tree": engine_lock["engine_tree"],
            "wheel_filename": engine_lock["wheel_filename"],
            "wheel_sha256": engine_lock["wheel_sha256"],
        },
        "input_sha256": _sha256(FIT_INPUT),
        "result_sha256": _sha256(FIT_RESULT),
        "result_digest": result.digest,
        "anchor_seconds_by_row": anchor_seconds,
        "fit_seconds": fit_seconds,
        "accounting": result.accounting.to_mapping(),
        "accepted_start": None if accepted is None else accepted.start_identity,
        "fitted_values": [
            {"identity": identity, "value": value, "unit": unit}
            for identity, value, unit in result.fitted_values()
        ],
        "scientific_meaning": (
            "Exact-Jacobian fixed-observed-pressure liquid-fugacity diagnostic. "
            "It is neither a predicted PCO2 fit nor eligible for parameter promotion."
        ),
    }
    receipt["receipt_sha256"] = _canonical_sha256(receipt)
    FIT_RECEIPT.write_text(
        json.dumps(receipt, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
