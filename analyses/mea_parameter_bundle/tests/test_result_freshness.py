"""Publication must reject stale numerical inputs and altered rendered outputs."""

import gzip
import importlib.util
import sys
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "result_freshness", Path(__file__).parents[1] / "scripts/result_freshness.py"
)
freshness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(freshness)


def test_certification_refuses_inputs_changed_during_render(monkeypatch):
    snapshots = iter([{"notebook.qmd": "before"}, {"notebook.qmd": "after"}])
    rendered = []
    monkeypatch.setattr(freshness, "require_current_results", lambda: None)
    monkeypatch.setattr(freshness, "render_inputs", lambda: next(snapshots))
    monkeypatch.setattr(
        freshness.subprocess, "run", lambda command, **kwargs: rendered.append(command)
    )
    monkeypatch.setattr(
        freshness, "stamp_results", lambda *args, **kwargs: pytest.fail("stamped")
    )
    with pytest.raises(ValueError, match="changed during rendering"):
        freshness.certify()
    assert rendered == [["bash", "render.sh"]]


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
    monkeypatch.syspath_prepend(str(Path(__file__).parents[1] / "scripts"))
    monkeypatch.setitem(sys.modules, "result_freshness", freshness)
    spec = importlib.util.spec_from_file_location(
        "handoff", Path(__file__).parents[1] / "scripts/build_absorption_handoff.py"
    )
    handoff = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(handoff)
    contents = {}

    def fake_bytes(path):
        data = str(path).encode()
        if path.name.endswith(".json.gz"):
            data = gzip.compress(data, mtime=0)
        return contents.setdefault(path, data)

    monkeypatch.setattr(
        Path, "read_bytes", fake_bytes
    )
    monkeypatch.setattr(
        Path,
        "is_file",
        lambda path: path != handoff.STATE_PACKET.with_suffix(""),
    )
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
