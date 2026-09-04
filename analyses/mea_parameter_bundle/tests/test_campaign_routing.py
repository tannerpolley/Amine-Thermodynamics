"""Campaigns pass their own parameters and reactions to the shared evaluator."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

import epcsaft
import run_born_permittivity_study as born
import run_direct_parameter_campaign as direct
import compare_permittivity_formulations as comparison


def test_campaigns_use_candidate_reactions_and_retain_failures(monkeypatch):
    captured = []

    def evaluate(model, request, reactions, identity, anchors, **kwargs):
        captured.append((model.parameter_fingerprint, reactions))
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
    selected = epcsaft.Parameters.from_json(direct.BASELINE)
    specs = {
        spec.identity: float(spec.value.magnitude)
        for spec in selected.parameter_specs
        if spec.identity.startswith("reaction:")
    }
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
    candidate = epcsaft.Parameters.from_mapping(born.variant_mapping("E-ORG"))
    expected = {
        spec.identity: float(spec.value.magnitude)
        for spec in candidate.parameter_specs
        if spec.identity.startswith("reaction:")
    }
    assert captured[-1] == (candidate.fingerprint, expected)
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
    packet = json.loads(comparison.STATE_PACKET.read_text())
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
    comparison.main(born.FOUNDATION)
    summary = json.loads(
        (comparison.RESULTS / "permittivity-formulation-comparison.json").read_text()
    )
    assert summary["candidate_selection"]["status"] == "incomplete"
    assert all(row["failed_states"] == 1 for row in summary["variants"].values())
    assert not (comparison.RESULTS / "selected-candidate-parameters.json").exists()


def test_baseline_requires_current_selection(tmp_path, monkeypatch):
    import pytest
    import run_reaction_temperature_fit as fit

    selected = tmp_path / "parameters.json"
    selected.write_text("selected input")
    receipts = [tmp_path / "figure.json", tmp_path / "heat.json"]
    monkeypatch.setattr(fit, "PARAMETERS", selected)
    monkeypatch.setattr(fit, "FIGURE_DATA", receipts[0])
    monkeypatch.setattr(fit, "HEAT", receipts[1])
    checked = []
    monkeypatch.setattr(fit, "require_results", checked.append)
    for path in receipts:
        path.write_text(json.dumps({"parameter_document_sha256": fit.sha256(selected)}))
    fit.require_current_baseline()
    assert checked == receipts
    receipts[1].write_text(json.dumps({"parameter_document_sha256": "old selection"}))
    with pytest.raises(ValueError, match="another selection"):
        fit.require_current_baseline()


def test_empty_heat_and_selected_handoff_metadata(tmp_path):
    import evaluate_direct_absorption_heat as heat
    import build_absorption_handoff as handoff

    output = tmp_path / "curve.csv"
    output.write_text("old predictions")
    heat.write_rows(output, [])
    assert output.read_text() == ""
    assert (
        heat.residual_metrics([{"status": "non_evaluable"}])["rmse_kj_per_mol_CO2"]
        is None
    )
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
