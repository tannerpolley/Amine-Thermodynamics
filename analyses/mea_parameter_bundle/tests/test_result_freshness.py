"""Publication must reject stale numerical inputs and altered rendered outputs."""

import importlib.util
import sys
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "result_freshness", Path(__file__).parents[1] / "scripts/result_freshness.py"
)
freshness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(freshness)


def test_publication_rejects_changed_inputs_outputs_and_unverified_results(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(freshness, "REPO", tmp_path)
    source = tmp_path / "parameters.json"
    output = tmp_path / "predictions.csv"
    receipt = tmp_path / "generation.json"
    source.write_text('{"value": 1}')
    output.write_text("prediction\n2\n")
    inputs = freshness.hashes((source,))
    freshness.stamp_results(receipt, [output], inputs=inputs)
    freshness.require_results(receipt)
    output.write_text("prediction\n3\n")
    with pytest.raises(ValueError, match="Stale"):
        freshness.require_results(receipt)
    output.write_text("prediction\n2\n")
    source.write_text('{"value": 2}')
    with pytest.raises(ValueError, match="Stale"):
        freshness.require_results(receipt)
    with pytest.raises(ValueError, match="Stale"):
        freshness.stamp_results(receipt, [output], inputs=inputs)
    receipt.write_text("{}")
    with pytest.raises(ValueError, match="Unverified"):
        freshness.require_results(receipt)


def test_handoff_checks_captured_bytes_not_only_live_receipts(monkeypatch):
    monkeypatch.setitem(sys.modules, "result_freshness", freshness)
    spec = importlib.util.spec_from_file_location(
        "handoff", Path(__file__).parents[1] / "scripts/build_absorption_handoff.py"
    )
    handoff = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(handoff)
    contents = {}
    monkeypatch.setattr(
        Path, "read_bytes", lambda path: contents.setdefault(path, str(path).encode())
    )
    monkeypatch.setattr(Path, "is_file", lambda path: True)
    monkeypatch.setattr(handoff, "require_current_results", lambda **kwargs: None)
    monkeypatch.setattr(
        handoff, "reaction_definition", lambda parameters, packet: parameters + packet
    )
    files, captured = handoff.payloads()
    freshness.require_hashes(captured)
    contents[handoff.PARAMETERS] = b"new selection"
    assert files["parameters/parameters.json"] != contents[handoff.PARAMETERS]
    with pytest.raises(ValueError, match="Stale"):
        freshness.require_hashes(captured)
