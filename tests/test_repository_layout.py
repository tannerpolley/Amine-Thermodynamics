import runpy
from pathlib import Path

VALIDATOR = runpy.run_path(
    Path(__file__).resolve().parents[1] / "scripts/validate_project.py"
)
MAX_TRACKED_JSON_BYTES = VALIDATOR["MAX_TRACKED_JSON_BYTES"]
MAX_TRACKED_JSON_LINES = VALIDATOR["MAX_TRACKED_JSON_LINES"]
json_size_problem = VALIDATOR["json_size_problem"]


def test_tracked_json_size_boundaries(tmp_path):
    compact = tmp_path / "compact.json"
    compact.write_text("{}\n")
    assert json_size_problem(compact) is None

    oversized = tmp_path / "oversized.json"
    oversized.write_bytes(b" " * (MAX_TRACKED_JSON_BYTES + 1))
    assert "bytes" in json_size_problem(oversized)

    overlong = tmp_path / "overlong.json"
    overlong.write_text("{}\n" * (MAX_TRACKED_JSON_LINES + 1))
    assert "lines" in json_size_problem(overlong)
