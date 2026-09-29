import runpy
from pathlib import Path

VALIDATOR = runpy.run_path(
    Path(__file__).resolve().parents[1] / "scripts/validate_project.py"
)
MAX_TRACKED_JSON_BYTES = VALIDATOR["MAX_TRACKED_JSON_BYTES"]
MAX_TRACKED_JSON_LINES = VALIDATOR["MAX_TRACKED_JSON_LINES"]
MAX_TRACKED_TEXT_BYTES = VALIDATOR["MAX_TRACKED_TEXT_BYTES"]
MAX_TRACKED_FILE_BYTES = VALIDATOR["MAX_TRACKED_FILE_BYTES"]
tracked_size_problem = VALIDATOR["tracked_size_problem"]
ROOT = Path(__file__).resolve().parents[1]


def test_tracked_file_size_boundaries(tmp_path):
    compact = tmp_path / "compact.json"
    compact.write_text("{}\n")
    assert tracked_size_problem(compact) is None

    oversized = tmp_path / "oversized.json"
    oversized.write_bytes(b" " * (MAX_TRACKED_JSON_BYTES + 1))
    assert "bytes" in tracked_size_problem(oversized)

    overlong = tmp_path / "overlong.json"
    overlong.write_text("{}\n" * (MAX_TRACKED_JSON_LINES + 1))
    assert "lines" in tracked_size_problem(overlong)

    large_text = tmp_path / "large.csv"
    large_text.write_bytes(b"x" * (MAX_TRACKED_TEXT_BYTES + 1))
    assert "bytes" in tracked_size_problem(large_text)

    large_binary = tmp_path / "large.bin"
    large_binary.write_bytes(b"x" * (MAX_TRACKED_FILE_BYTES + 1))
    assert "bytes" in tracked_size_problem(large_binary)


def test_cse_layout_keeps_cas_and_retires_central_notebook():
    assert not (ROOT / "docs/scientific/notebook").exists()
    main = (ROOT / "docs/scientific/latex/main.tex").read_text()
    assert r"\documentclass[a4paper,fleqn]{cas-sc}" in main
    assert r"\graphicspath{{figures/generated/}}" in main
    assert (ROOT / "docs/scientific/latex/figures/generated").is_dir()
    assert (
        ROOT
        / "analyses/reactive_epcsaft_parameter_evidence/co2_water_induced_association/scripts/generate.py"
    ).is_file()
