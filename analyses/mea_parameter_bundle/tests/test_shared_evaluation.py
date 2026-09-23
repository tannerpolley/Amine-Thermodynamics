"""Focused checks for the single cached/bounded equilibrium owner."""

import importlib.util
import json
import math
import os
import sys
import time
from copy import deepcopy
from pathlib import Path

import pytest
from MEA.common.mea_source_contracts import common_source_ln_k


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

    model = "sha256:test-model"
    first = shared.evaluate_state(None, _request(), {}, "first", [], model_fingerprint=model)
    cached = shared.evaluate_state(None, _request(), {}, "second", [], model_fingerprint=model)
    candidate = shared.evaluate_state(
        None, _request(), {"reaction:R1:correlation:a": 1.0}, "candidate", [],
        model_fingerprint=model,
    )

    assert first["status"] == "evaluated"
    assert cached["cache_hit"] is True
    assert candidate["cache_hit"] is False
    assert len(calls) == 2
    assert first["model_parameters_fingerprint"] == model
    assert candidate["parameter_role"] == "candidate"
    other = shared.evaluate_state(
        None, _request(), {}, "different-model", [], model_fingerprint="sha256:different-model"
    )
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
    original = shared.equilibrium.solve_equilibrium

    def block(*_args, **_kwargs):
        time.sleep(5)

    monkeypatch.setattr(shared.equilibrium, "solve_equilibrium", block)
    try:
        with pytest.raises(shared.EvaluationTimeout):
            shared._solve_in_child(object(), object(), 0.05)
    finally:
        monkeypatch.setattr(shared.equilibrium, "solve_equilibrium", original)


def test_pinned_engine_state_and_cached_replay(tmp_path, monkeypatch):
    shared.verify_wheel()
    monkeypatch.setattr(shared, "RUNS", tmp_path)
    parameters = shared.load_parameters()
    model = shared.epcsaft.Mixture(parameters)
    request = next(
        observation["request"]
        for observation in shared.load_state_packet()["observations"]
        if observation["identity"] == "Bottinger2008_state_050"
    )
    reactions = shared._selected_reactions()
    result = shared.evaluate_state(
        model, request, reactions, "Bottinger2008_state_050", [], budget_s=60
    )
    assert result["status"] == "evaluated", result["attempts"]
    assert result["failure_code"] == ""
    # Fitted exclusion-mode record (SHA 868a5018...). The superseded all-ion-pairs record
    # still reproduces the former pins (hco3 0.005214865, mea_meah 0.06771946, meacoo
    # 0.04449868) to 6e-14 on this wheel, so the change is the declared model, not the Engine.
    assert result["predictions"] == pytest.approx(
        {
            "Bottinger2008_state_050-hco3": 0.010779404008693854,
            "Bottinger2008_state_050-mea_meah": 0.07456750655659783,
            "Bottinger2008_state_050-meacoo": 0.0376488801816921,
        },
        rel=5e-8,
        abs=1e-12,
    )
    liquid = next(phase for phase in result["phases"] if phase["role"] == "liquid")
    species = dict(zip(liquid["support"], liquid["mole_fractions"], strict=True))
    assert species["carbamate-anion"] == pytest.approx(0.0376488801816921, rel=5e-8)
    assert species["bicarbonate-anion"] == pytest.approx(0.010779404008693854, rel=5e-8)
    assert species["hydronium-cation"] == pytest.approx(3.906278160355156e-10, rel=5e-6)
    evidence = dict(result["evidence"])
    compiled = evidence["compiled_point_evaluation"]
    assert compiled["raw_stationarity_max_abs"] <= 1e-10
    assert max(abs(value) for value in evidence["residuals"]) <= 1e-10
    assert max(abs(value) for value in evidence["classified_residuals"]) <= 1e-10
    diagnostics = next(
        row[1] for row in result["evidence"] if row[0] == "neutral_reference_diagnostics"
    )
    assert all(item["status"] == "Available" for item in diagnostics)
    assert max(item["observed_terminal_change"] for item in diagnostics) <= 5.0e-5
    replay = shared.evaluate_state(
        model, request, reactions, "Bottinger2008_state_050-replay", [], budget_s=15
    )
    assert replay["cache_hit"] is True
    assert replay["predictions"] == result["predictions"]


def test_source_normalizer_keeps_common_r2_and_converts_only_log10_form():
    request = next(
        o["request"]
        for o in shared.load_state_packet()["observations"]
        if o["identity"] == "Bottinger2008_state_050"
    )
    selected = shared._engine_reaction_records(request, shared._selected_reactions())
    r2 = selected[1]
    assert r2["engine_correlation"]["a"] == pytest.approx(
        232.33141533884407
        - 36.7816 * math.log(shared.REACTION_REFERENCE_TEMPERATURE_K)
    )
    assert r2["engine_correlation"]["b"] == -11105.640030520277
    assert r2["engine_correlation"]["reference_temperature"] == 313.15
    assert r2["engine_correlation"]["standard_state_id"] == (
        shared.COMMON_SOURCE_STANDARD_STATE_ID
    )
    assert r2["engine_reference"]["source_basis"] == "CommonMolalityInfiniteDilution"
    r5 = selected[4]["engine_correlation"]
    assert r5["a"] == -math.log(10.0) * -1.0173150837285996
    assert r5["b"] == -math.log(10.0) * 3037.6399534696106
    baseline = shared._engine_reaction_records(request, {})
    assert baseline[1]["engine_correlation"]["a"] == pytest.approx(
        231.465 - 36.7816 * math.log(shared.REACTION_REFERENCE_TEMPERATURE_K)
    )
    assert baseline[1]["engine_reference"]["source_basis"] == "RawMoleFractionInfiniteDilution"
    selected_r2 = selected[1]["engine_correlation"]
    shift_j_per_mol = -8201.884540543741
    gas_constant = 8.31446261815324
    for temperature in (293.15, 303.15, 313.15):
        expected = common_source_ln_k(temperature)[1] + shift_j_per_mol / gas_constant * (
            1.0 / 313.15 - 1.0 / temperature
        )
        actual = (
            selected_r2["a"]
            + selected_r2["b"] / temperature
            + selected_r2["c"]
            * math.log(temperature / selected_r2["reference_temperature"])
            + selected_r2["d"] * temperature
        )
        assert actual == pytest.approx(expected, abs=2.0e-12)


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
    request = deepcopy(next(
        o["request"]
        for o in shared.load_state_packet()["observations"]
        if o["request"]["pressure"]["role"] == "fixed"
    ))
    request["reaction_system"]["engine_reactions"] = [
        {
            "reaction_id": f"R{i + 1}",
            "engine_correlation": {
                "a": 0.0, "b": 0.0, "c": 0.0, "d": 0.0,
                "reference_temperature": 300.0,
                "temperature_min": 250.0, "temperature_max": 450.0,
                "standard_state_id": shared.equilibrium.EOS_STANDARD_STATE_ID,
            },
        }
        for i in range(5)
    ]
    problem = shared._problem_from_request(request)
    assert problem.P == request["pressure"]["value"]
