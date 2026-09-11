from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "analyses/enrtl_historical_evidence/results/historical_evidence.json"
RECEIPT = ROOT / "analyses/enrtl_historical_evidence/conversion_receipt.json"


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def test_historical_record_is_compact_traceable_and_bounded():
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert record["identity"] == "mea-enrtl-historical-evidence-v1"
    assert set(record["evidence"]) == {
        "six_species_parity",
        "nine_species_topology",
        "fixed_composition_screening",
        "screening_reaction_residuals",
        "D01_equilibrium",
    }
    screening = record["evidence"]["fixed_composition_screening"]
    assert screening["design_count"] == 64
    assert len(screening["states"]) == 64
    assert screening["state_status_counts"] == {"finite_fixed_composition_evaluation": 64, "failed": 0}
    assert screening["role"].endswith("not equilibria")
    assert "converged" not in json.dumps(screening).lower()
    assert record["evidence"]["screening_reaction_residuals"]["d01_excluded"]
    assert record["evidence"]["D01_equilibrium"]["role"].startswith("distinct accepted")
    assert record["source"]["fitting_identity"] == "c9e61fab6ea631c77166ee337f02b83d19b9c9a8"
    assert all(len(item["blob"]) == 40 for item in record["source"]["commits"])
    assert RECORD.stat().st_size < 100 * 1024
    assert sum(1 for _ in RECORD.open("rb")) < 3_000
    assert hashlib.sha256(RECORD.read_bytes()).hexdigest() == receipt["output_sha256"]
    assert receipt["policy"]["protected_analysis_modified"] is False

    text = "\n".join(_strings(record)).lower()
    assert not re.search(r"(?:/home/|/users/|[a-z]:[\\/])", text)
    assert "synthetic absorber adapter" not in text
    assert "production enrtl" not in text


def test_protected_analysis_has_no_worktree_diff():
    result = subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            "HEAD",
            "--",
            "analyses/enrtl_six_species_ideal_comparison",
        ],
        cwd=ROOT,
    )
    assert result.returncode == 0
