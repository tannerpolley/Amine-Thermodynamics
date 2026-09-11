"""Focused checks for the single cached/bounded equilibrium owner."""

import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import pytest


SPEC = importlib.util.spec_from_file_location(
    "shared_evaluation", Path(__file__).parents[1] / "scripts/shared_evaluation.py"
)
shared = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["shared_evaluation"] = shared
SPEC.loader.exec_module(shared)


def _request() -> dict[str, object]:
    return {
        "temperature": {"value": 313.15},
        "phases": [{"model": {"kind": "source", "reference_id": "source"}}],
        "reaction_system": {
            "equilibrium_constants": [[0.0, "", "", "", "", ""] for _ in range(5)],
            "feed_amounts_mol": [0.1, 1.0],
        },
    }


class _Model:
    parameter_fingerprint = "sha256:test-model"


def _snapshot() -> shared.SolveSnapshot:
    return shared.SolveSnapshot(
        status="evaluated",
        predictions={"system-pressure": 101325.0, "co2-partial-pressure": 1000.0},
        phases=[
            {
                "role": "liquid",
                "pressure_pa": 101325.0,
                "molar_density_mol_m3": 1000.0,
                "packing_fraction": 0.1,
                "mechanical_class": "stable",
                "mole_fractions": [0.1, 0.9],
                "molar_volume_m3_per_mol": 1.0e-3,
                "reference_molar_enthalpy_j_per_mol": 1.0,
                "residual_molar_enthalpy_j_per_mol": 2.0,
            }
        ],
    )


def test_cache_records_model_identity_and_separates_candidate(tmp_path, monkeypatch):
    parameter_file = tmp_path / "parameters.json"
    parameter_file.write_text(shared.PARAMETERS.read_text())
    monkeypatch.setattr(shared, "PARAMETERS", parameter_file)
    monkeypatch.setattr(shared, "RUNS", tmp_path / "runs")
    monkeypatch.setattr(shared, "_selected_reactions", lambda: {})
    calls = []
    monkeypatch.setattr(
        shared,
        "solve_with_recovery",
        lambda *args, **kwargs: (calls.append(1) or _snapshot(), []),
    )

    first = shared.evaluate_state(_Model(), _request(), {}, "first", [])
    cached = shared.evaluate_state(_Model(), _request(), {}, "second", [])
    candidate = shared.evaluate_state(
        _Model(), _request(), {"reaction:R1:correlation:a": 1.0}, "candidate", []
    )

    assert first["status"] == "evaluated"
    assert cached["cache_hit"] is True
    assert candidate["cache_hit"] is False
    assert len(calls) == 2
    assert first["model_parameters_fingerprint"] == _Model.parameter_fingerprint
    assert candidate["parameter_role"] == "candidate"
    other_model = _Model()
    other_model.parameter_fingerprint = "sha256:different-model"
    other = shared.evaluate_state(other_model, _request(), {}, "different-model", [])
    assert not other["cache_hit"]
    assert len(calls) == 3


@pytest.mark.parametrize(
    "failure_code,reusable",
    [("evaluation_timeout", False), ("engine_exception", False), ("infeasible", True)],
)
def test_failed_state_cache_policy(tmp_path, monkeypatch, failure_code, reusable):
    parameter_file = tmp_path / "parameters.json"
    parameter_file.write_text(shared.PARAMETERS.read_text())
    monkeypatch.setattr(shared, "PARAMETERS", parameter_file)
    monkeypatch.setattr(shared, "RUNS", tmp_path / "runs")
    monkeypatch.setattr(shared, "_selected_reactions", lambda: {})
    calls = []
    monkeypatch.setattr(
        shared,
        "solve_with_recovery",
        lambda *args, **kwargs: (
            calls.append(1),
            [
                {
                    "kind": "cold-packet-start",
                    "status": "timeout",
                    "wall_s": 0.01,
                    "failure_code": failure_code,
                    "failure_diagnostic": "test",
                }
            ],
        ),
    )

    first = shared.evaluate_state(_Model(), _request(), {}, "first", [])
    cached = shared.evaluate_state(_Model(), _request(), {}, "second", [])
    assert first["status"] == "non_evaluable"
    assert first["failure_code"] == failure_code
    assert cached["cache_hit"] is reusable
    assert cached["failure_code"] == failure_code
    assert len(calls) == (1 if reusable else 2)


@pytest.mark.skipif(
    not hasattr(os, "fork"), reason="hard native timeout requires POSIX fork"
)
def test_native_solver_timeout_terminates_owned_child(monkeypatch):
    original = shared.equilibrium.solve

    def block(*_args, **_kwargs):
        time.sleep(5)

    monkeypatch.setattr(shared.equilibrium, "solve", block)
    try:
        with pytest.raises(shared.EvaluationTimeout):
            shared._solve_in_child(object(), object(), 0.05)
    finally:
        monkeypatch.setattr(shared.equilibrium, "solve", original)


def test_pinned_engine_state_and_cached_replay(tmp_path, monkeypatch):
    shared.verify_wheel()
    monkeypatch.setattr(shared, "RUNS", tmp_path)
    parameters = shared.epcsaft.Parameters.from_json(shared.PARAMETERS)
    model = shared.epcsaft.Mixture(parameters)
    request = shared.load_state_packet()["observations"][0]["request"]
    reactions = {
        spec.identity: float(spec.value.magnitude)
        for spec in parameters.parameter_specs
        if spec.identity.startswith("reaction:")
    }
    result = shared.evaluate_state(
        model, request, reactions, "native-smoke", [], budget_s=15
    )
    assert result["status"] == "evaluated", result["attempts"]
    assert result["parameter_role"] == "selected"
    assert result["solver_status"] == "solve_succeeded"
    assert result["predictions"]["co2-partial-pressure"] > 0
    replay = shared.evaluate_state(
        model, request, reactions, "cached-smoke", [], budget_s=15
    )
    assert replay["cache_hit"]
    assert replay["predictions"] == result["predictions"]


def test_compact_packet_expands_all_observations_and_isolated_values():
    packet = shared.load_state_packet()
    assert len(packet["observations"]) == 123
    first = packet["observations"][0]["request"]
    replay = shared.load_state_packet()
    second = replay["observations"][0]["request"]
    assert first["reaction_system"] == second["reaction_system"]
    first["reaction_system"]["feed_amounts_mol"][0] = -1
    assert second["reaction_system"]["feed_amounts_mol"][0] != -1


def test_compact_packet_rejects_bad_reference():
    document = json.loads(shared.source_bytes(shared.STATE_PACKET))
    document["observations"][0]["request"]["temperature"] = 999999
    with pytest.raises(ValueError, match="out-of-range temperature reference"):
        shared.expand_state_packet(document)


def test_fixed_pressure_warm_start_does_not_gain_unknown_pressure_fields(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(shared, "RUNS", tmp_path)
    packet = shared.load_state_packet()
    request = next(
        o["request"]
        for o in packet["observations"]
        if o["request"]["pressure"]["role"] == "fixed"
    )
    problem = shared.equilibrium.general_reactive_equilibrium_problem_from_mapping(
        shared.corrected_request(request)
    )
    phase = problem.continuation_state.phases[0]
    anchor = shared.Anchor(
        round(request["temperature"]["value"] - 273.15),
        request["reaction_system"]["feed_amounts_mol"][0],
        request["pressure"]["value"],
        phase.mole_fractions,
        phase.molar_volume_m3_per_mol,
    )
    monkeypatch.setattr(shared, "_solve_in_child", lambda *args: _snapshot())
    result, attempts = shared.solve_with_recovery(
        _Model(), request, {}, "fixed-pressure", [anchor]
    )
    assert result.status == "evaluated"
    assert attempts[0]["kind"] == "same-temperature-anchor"
