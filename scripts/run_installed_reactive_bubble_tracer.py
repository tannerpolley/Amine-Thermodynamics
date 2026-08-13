from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, replace
from pathlib import Path

import epcsaft
from epcsaft import equilibrium

from MEA.epcsaft_ionic.reduced_tracer import build_reduced_tracer_input


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "analyses/phase3/ionic_epcsaft_regression/results/reactive_vle_vertical_slice"
    / "installed_reactive_bubble_tracer_receipt.json"
)
LOCK = ROOT / "data/reference/MEA/manifests/engine_artifact_lock.json"


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def _write(payload: dict[str, object]) -> None:
    payload["receipt_sha256"] = _canonical_sha256(payload)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(OUTPUT.relative_to(ROOT))
    print(payload["receipt_sha256"])


def main() -> None:
    started = time.monotonic()
    source = build_reduced_tracer_input()
    liquid_reference = source.problem.continuation_reference
    if liquid_reference is None:
        raise RuntimeError(
            "the homogeneous liquid tracer has no continuation reference"
        )
    liquid = replace(
        source.problem,
        continuation_reference=replace(
            liquid_reference,
            maximum_log_composition_distance=2.0,
            maximum_log_volume_distance=2.0,
        ),
    )
    problem = equilibrium.ReactiveBubbleVLEProblem(
        identity="mea-gate0-stage5-reactive-bubble-tracer",
        liquid_problem=liquid,
        vapor_phase_identity="mea-declared-neutral-incipient-vapor",
        vapor_component_ids=("carbon-dioxide", "monoethanolamine", "water"),
        vapor_model=equilibrium.ProviderNonidealVapor("installed-provider-eos"),
        pressure_interval_pa=(6105.45, 300000.0),
        pressure_starts_pa=(7326.7, 15000.0, 50000.0, 150000.0),
        continuation_identity="mea-gate0-local-reactive-bubble-branch",
    )
    rows = (
        equilibrium.ReactiveBubbleObservationRow(
            "mea-gate0-bubble-pressure", "bubble_pressure_pa"
        ),
        equilibrium.ReactiveBubbleObservationRow(
            "mea-gate0-co2-partial-pressure",
            "vapor_partial_pressure_pa",
            (1.0, 0.0, 0.0),
        ),
        equilibrium.ReactiveBubbleObservationRow(
            "mea-gate0-carbamate-liquid-fraction",
            "liquid_mole_fraction",
            (0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0),
        ),
    )
    descriptor = equilibrium.reactive_bubble_observation_descriptor(problem, rows)
    temperature = source.temperature_k * epcsaft.unit_registry.kelvin
    result = equilibrium.evaluate_reactive_bubble_observations(
        problem, temperature, descriptor
    )
    payload: dict[str, object] = {
        "schema_version": 1,
        "identity": "mea-installed-cap13-reactive-bubble-tracer-v1",
        "engine": json.loads(LOCK.read_text()),
        "scope": "stage_5_coupled_solver_tracer_not_parameter_fit_or_model_score",
        "input": {
            "temperature_k": source.temperature_k,
            "liquid_component_ids": list(descriptor.component_ids),
            "vapor_component_ids": list(descriptor.vapor_component_ids),
            "pressure_interval_pa": list(problem.pressure_interval_pa),
            "pressure_starts_pa": list(problem.pressure_starts_pa),
            "vapor_model": type(problem.vapor_model).__name__,
            "active_parameter_identities": [],
        },
        "status": result.status,
        "failure": None if result.failure is None else asdict(result.failure),
        "rows": [asdict(row) for row in result.rows],
        "search": asdict(result.search),
        "runtime_seconds": time.monotonic() - started,
        "fingerprints": {
            "descriptor": descriptor.fingerprint,
            "parameter": descriptor.parameter_fingerprint,
            "partner_parameter": descriptor.partner_parameter_fingerprint,
            "topology": descriptor.topology_fingerprint,
            "reference": descriptor.reference_fingerprint,
            "domain": descriptor.domain_fingerprint,
            "problem": descriptor.problem_fingerprint,
            "reaction": descriptor.reaction_fingerprint,
        },
        "scientific_decision": (
            "This installed-wheel calculation is a coupled-solver tracer only. "
            "No MEA parameter is fitted or promoted because the application has no "
            "admitted pressure/speciation scoring rows or qualified Stage-1 packet."
        ),
    }
    if result.status == "evaluated":
        assert result.physical_branch is not None
        assert result.certification is not None
        assert result.liquid_state is not None
        payload["coupled_state"] = {
            "pressure_pa": result.pressure_pa,
            "physical_branch": asdict(result.physical_branch),
            "liquid_state_identity": result.liquid_state.state_identity,
            "phases": [asdict(phase) for phase in result.phases],
            "certification": asdict(result.certification),
            "globality_claim": "not_established",
        }
    _write(payload)


if __name__ == "__main__":
    main()
