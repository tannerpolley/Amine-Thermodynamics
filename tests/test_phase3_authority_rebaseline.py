from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_AUTHORITY_FILES = (
    ROOT / "docs/coordination/epcsaft_feedback_reactive_regression_admission.md",
    ROOT / "docs/roadmaps/epcsaft_dependency_matrix.md",
    ROOT / "docs/superpowers/issues/12-native-regression-result-contract.md",
    ROOT / "docs/superpowers/issues/13-coupled-regression-parameter-promotion.md",
    ROOT / "docs/superpowers/issues/14-independent-validation-identifiability.md",
    ROOT / "docs/superpowers/milestones/phase-3-ionic-regression.md",
)
READINESS = (
    ROOT
    / "analyses/phase3/ionic_epcsaft_regression/results/readiness/regression_readiness_summary.json"
)
PIN = "9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785"
SPLIT_HASH = "e7bc893dab825007d009260d2c1f6f5dd42e75ebddbdb4972d52a5ec4f0c1aa0"


def test_active_phase3_docs_use_current_upstream_authority() -> None:
    active_text = "\n".join(
        path.read_text(encoding="utf-8") for path in ACTIVE_AUTHORITY_FILES
    )

    assert "https://github.com/ePC-SAFT/ePC-SAFT/issues/468" not in active_text
    assert "tannerpolley/ePC-SAFT-lab" in active_text
    assert "ePC-SAFT/ePC-SAFT-regression" in active_text
    assert "stage-approved" in active_text
    assert "governance-only skeleton" in active_text


def test_local_agent_policy_uses_current_upstream_authority_when_present() -> None:
    agents = ROOT / "AGENTS.md"
    if not agents.exists():
        return

    text = agents.read_text(encoding="utf-8")
    assert "preserved personal lab" in text
    assert "ePC-SAFT-project" in text
    assert "stage-approved" in text


def test_rebaseline_preserves_pin_and_fail_closed_readiness() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    lock = (ROOT / "uv.lock").read_text(encoding="utf-8")
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))

    assert PIN in pyproject
    assert PIN in lock
    assert readiness["upstream_execution_admitted"] is False
    assert (
        readiness["readiness_decision"]
        == "preregistration_ready_upstream_execution_blocked"
    )
    assert readiness["split_hash"] == SPLIT_HASH
    assert readiness["source_hashes"]


def test_local_tracker_mirrors_do_not_keep_completed_issue_11_as_a_blocker() -> None:
    phase2_parent = (
        ROOT / "docs/superpowers/issues/5-activity-model-comparison-workstream.md"
    ).read_text(encoding="utf-8")
    editorial = (
        ROOT / "docs/superpowers/issues/18-publication-figures-editorial.md"
    ).read_text(encoding="utf-8")

    assert "status:blocked" not in phase2_parent
    assert "- [x] #11 is the only" in phase2_parent
    assert "## Blocked by\n\n- None." in phase2_parent
    editorial_blockers = editorial.split("## Blocked by", maxsplit=1)[1].split(
        "## Non-goals", maxsplit=1
    )[0]
    assert "issues/11" not in editorial_blockers
    assert (
        "https://github.com/tannerpolley/MEA-Thermodynamics/issues/14"
        in editorial_blockers
    )
