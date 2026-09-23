"""Campaigns pass their own parameters and reactions to the shared evaluator."""

import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

import run_born_permittivity_study as born
import run_direct_parameter_campaign as direct
import compare_permittivity_formulations as comparison
from shared_evaluation import parameter_fingerprint, parameter_mapping, reaction_values


def test_campaigns_use_candidate_reactions_and_retain_failures(monkeypatch):
    captured = []

    def evaluate(model, request, reactions, identity, anchors, **kwargs):
        captured.append((kwargs["model_fingerprint"], reactions))
        return {
            "status": "non_evaluable",
            "failure_code": "evaluation_timeout",
            "failure_diagnostic": "test timeout",
            "predictions": {},
            "cache_hit": False,
        }

    pressure = direct.pressure_catalog(False)[:1]
    monkeypatch.setattr(direct, "pressure_catalog", lambda full: pressure)
    monkeypatch.setattr(direct, "speciation_catalog", lambda: [])
    monkeypatch.setattr(direct, "evaluate_state", evaluate)
    _, _, rows = direct.evaluate_scenario(("test", {"r4_a": 2.1}, False))
    specs = reaction_values(parameter_mapping(direct.BASELINE))
    assert captured[-1][1]["reaction:R4:correlation:a"] == 2.1
    assert (
        captured[-1][1]["reaction:R2:correlation:a"]
        == specs["reaction:R2:correlation:a"]
    )
    assert rows[0]["failure_code"] == "evaluation_timeout"
    summary = direct.summarize("test", {}, rows)
    assert summary["pressure_coverage"] == 0
    assert summary["pressure_log10_rmse"] is None

    observation = born.packet_catalog()[0]
    monkeypatch.setattr(born, "sparse_catalog", lambda: [observation])
    monkeypatch.setattr(born, "evaluate_state", evaluate)
    states, targets = born.evaluate_variant(("E-ORG", "sparse", 0, 1))
    candidate = born.variant_mapping("E-ORG")
    assert captured[-1] == (parameter_fingerprint(candidate), reaction_values(candidate))
    assert captured[-1][0] != parameter_fingerprint(parameter_mapping(direct.BASELINE))
    assert states[0]["failure_code"] == "evaluation_timeout"
    assert not targets


def test_empty_checkpoint_cannot_leave_previous_predictions(tmp_path):
    output = tmp_path / "targets.csv"
    output.write_text("old predictions")
    comparison.write_csv(output, [])
    assert output.read_text() == ""


def test_failed_comparison_retains_failures_without_selecting_candidate(
    tmp_path, monkeypatch
):
    packet = json.loads(gzip.decompress(comparison.STATE_PACKET.read_bytes()))
    packet["observations"] = packet["observations"][:1]
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet))
    monkeypatch.setattr(comparison, "STATE_PACKET", packet_path)
    monkeypatch.setattr(comparison, "ANALYSIS", tmp_path)
    monkeypatch.setattr(comparison, "RESULTS", tmp_path / "results")
    monkeypatch.setattr(
        comparison,
        "evaluate_state",
        lambda *args, **kwargs: {
            "status": "non_evaluable",
            "failure_code": "evaluation_timeout",
            "failure_diagnostic": "test",
            "cache_hit": False,
        },
    )
    comparison.main(direct.BASELINE)
    summary = json.loads(
        (comparison.RESULTS / "permittivity-formulation-comparison.json").read_text()
    )
    assert summary["candidate_selection"]["status"] == "incomplete"
    assert all(row["failed_states"] == 1 for row in summary["variants"].values())
    assert not (comparison.RESULTS / "selected-candidate-parameters.json").exists()


def test_selected_handoff_metadata():
    import build_absorption_handoff as handoff

    selected = json.loads(handoff.PARAMETERS.read_text())
    selected["reaction_correlations"][0]["coefficients"][0]["value"]["magnitude"] += 1.0
    definition = json.loads(
        handoff.reaction_definition(
            json.dumps(selected).encode(), handoff.STATE_PACKET.read_bytes()
        )
    )
    for row in selected["reaction_correlations"]:
        reaction = next(
            r for r in definition["reactions"] if r["reaction_id"] == row["reaction_id"]
        )
        assert reaction["qualification"] == row["qualification"]
        assert reaction["source"] == row["source"]
        assert reaction["coefficients"] == {
            c["name"]: c["value"]["magnitude"] for c in row["coefficients"]
        }
    assert definition["domains"] == selected["domains"]
