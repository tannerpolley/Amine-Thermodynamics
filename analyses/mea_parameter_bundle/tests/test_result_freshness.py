"""Publication must reject stale numerical inputs and altered rendered outputs."""

import importlib.util
import sys
import os
import subprocess
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "result_freshness", Path(__file__).parents[1] / "scripts/result_freshness.py"
)
freshness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(freshness)


def test_working_render_is_explicit_and_cannot_certify_publication(tmp_path):
    script = tmp_path / "render.sh"
    script.write_bytes((Path(__file__).parents[1] / "render.sh").read_bytes())
    commands = tmp_path / "bin"
    commands.mkdir()
    for name, body in {
        "uv": "exit 7",
        "quarto": (
            'test "$#" = 2 && test "$1" = render && test "$2" = --no-execute || exit 9\n'
            "mkdir _site\n"
            "for page in notebook neutral-mea-water/index ionic-speciation-fit/index "
            "co2-r4-calibration/index reaction-temperature-fit/index "
            "born-permittivity/index calorimetry/index "
            "coupling-and-identification/index association-topology/index "
            "historical-designs/index; do "
            'mkdir -p "_site/$(dirname "$page")"; '
            'echo "<html>$page</html>" > "_site/$page.html"; done\n'
            "echo rendered"
        ),
    }.items():
        command = commands / name
        command.write_text("#!/bin/sh\n" + body + "\n")
        command.chmod(0o755)
    env = dict(os.environ, PATH=str(commands) + os.pathsep + os.environ["PATH"])
    working = subprocess.run(
        ["bash", str(script), "notebook.qmd", "--working-copy"],
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert working.returncode == 0, working.stderr
    assert "rendered" in working.stdout
    assert "publication was not certified" in working.stdout
    assert (tmp_path / "notebook.html").is_file()
    assert (tmp_path / "reaction-temperature-fit/index.html").is_file()
    assert not (tmp_path / "_site").exists()
    strict = subprocess.run(
        ["bash", str(script), "notebook.qmd"],
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert strict.returncode == 7
    assert "rendered" not in strict.stdout


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
