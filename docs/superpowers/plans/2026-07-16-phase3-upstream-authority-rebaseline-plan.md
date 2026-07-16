# Phase 3 Upstream Authority Rebaseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebaseline MEA Phase 3 onto the current clean ePC-SAFT authority model, preserve the immutable 1.5.2 evaluation lane, and reconcile stale local and GitHub tracker state without opening regression execution.

**Architecture:** Treat the readiness receipt as the executable downstream gate, the pinned monolithic package as immutable historical evaluation evidence, the migration control plane as the temporary sequencing owner, and clean `ePC-SAFT-regression` as the future production owner. One contract test guards the active documentation surface and immutable readiness/pin invariants; one tracker pass then makes live issue state match the validated repository artifacts.

**Tech Stack:** Python 3.12, pytest, Markdown, JSON, Git, GitHub CLI, uv.

## Global Constraints

- Do not create or use a repo-local `.worktrees` directory; execute in the primary checkout on `codex/phase3-authority-rebaseline`.
- Do not run a reduced or full coupled regression.
- Do not change `pyproject.toml`, `uv.lock`, parameter values, target membership, grouped split membership, readiness hashes, analysis outputs, figures, or manuscript scientific claims.
- Keep `upstream_execution_admitted=false` and readiness decision `preregistration_ready_upstream_execution_blocked`.
- Do not create a clean upstream issue, package surface, test, or capability claim before a stage-approved migration transfer plan exists.
- Preserve downstream optimizer ownership in upstream ePC-SAFT and fail closed on incomplete capability evidence.
- Main-thread ownership is required for Git, GitHub mutations, PR creation, merge, and cleanup.

---

## Source Evidence

- Design: `docs/superpowers/specs/2026-07-16-phase3-upstream-authority-rebaseline-design.md`.
- Current downstream gate: `src/MEA/common/data_access.py::require_regression_execution_admitted` and `scripts/build_regression_readiness.py`.
- Frozen receipt: `analyses/phase3/ionic_epcsaft_regression/results/readiness/regression_readiness_summary.json`.
- Historical lab issue: `https://github.com/tannerpolley/ePC-SAFT-lab/issues/468`.
- Clean regression authority: `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-regression/{AGENTS.md,CONTEXT.md}`.
- Migration status: `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT-project/ePC-SAFT-migration/MIGRATION.md`.

## Outcome Proof

**Intent:** Replace a stale historical-lab dependency with the current clean-package authority and migration gate while preserving every existing scientific failure boundary.
**Current Behavior:** Active MEA issue bodies and coordination files treat the pre-transfer `ePC-SAFT/ePC-SAFT#468` URL as an actionable upstream blocker; Issue #5 remains open behind completed #11, and Issue #18 still lists #11.
**Expected Outcome:** Active repository and GitHub state identify lab #468 as historical evidence, clean `ePC-SAFT-regression` as the future production owner, migration authorization as the next upstream gate, and only open dependencies as blockers.
**Target Output:** One authority-contract test, updated active coordination/roadmap/issue artifacts, one executable rebaseline GitHub issue, corrected live issue bodies, closed Phase 2 parent #5, and a merged verified PR.
**Owner:** MEA cross-repo integration maintainer, with upstream runtime ownership reserved to the ePC-SAFT migration and clean regression owners.
**Interface:** Active Markdown contracts plus `upstream_execution_admitted`, the immutable readiness receipt, `scripts/check_epcsaft_integration.py --mode final`, and live GitHub issue state.
**Cutover:** Active dependency text stops treating lab tracker state as production authority and instead names the clean owner plus migration transfer gate.
**Replaced Path:** Retire `https://github.com/ePC-SAFT/ePC-SAFT/issues/468` from active dependency sections; retain the lab URL only as historical provenance.
**Evidence:** Focused contract tests, byte/hash invariant checks, final integration output, structured GitHub read-back, hosted CI, and post-merge cleanup.
**Acceptance Proof:** Active docs contain one authority chain, readiness and pin identities remain unchanged, final integration passes, #5 is closed, #18 no longer references #11, and #12-#14 retain their scientific ordering.
**Stop Criteria:** Stop on any readiness/pin drift, contradictory owner, missing migration authority, GitHub write-back mismatch, failed final integration, or CI failure.
**Avoid:** Do not implement upstream runtime work, invent clean API names, bypass admission, use a downstream optimizer, or mutate scientific artifacts.
**Risk:** Clean package sequencing may change; exact clean API names remain deferred until an accepted stage-owned upstream specification and immutable receipt exist.

## Implementation Boundaries

**Files To Create:** `tests/test_phase3_authority_rebaseline.py` and this implementation plan.
**Files To Modify:** Local ignored `AGENTS.md`, active tracked ePC-SAFT coordination/roadmap files, Phase 3 milestone, issue mirrors #5/#12/#13/#14/#18, and the design spec only if review finds a contradiction.
**Files To Avoid:** `pyproject.toml`, `uv.lock`, `integration/epcsaft_contract.json`, all canonical data/manifests, readiness/result artifacts, analysis outputs, figures, manuscript sources, and every ePC-SAFT repository.
**Source Of Truth:** Ecosystem doctrine revision 2 and migration status define ownership; the MEA readiness receipt defines downstream execution admission.
**Read Path:** Read doctrine/migration/clean-repository context, then active MEA coordination, issue, milestone, dependency, pin, and readiness artifacts.
**Write Path:** Write only MEA policy/project artifacts and live `tannerpolley/MEA-Thermodynamics` issue state.
**Integration Points:** `require_regression_execution_admitted`, readiness generation/tests, final integration checker, Phase 3 milestone, GitHub issue graph, and hosted CI.
**Migration Or Cutover:** Reclassify lab issue #468 as historical and defer new clean regression intake until a stage-approved transfer plan exists.
**Replaced Path Handling:** Remove the old organization issue URL from active dependency sections; preserve its transferred lab URL only in explicitly historical context.
**Acceptance Proof Gate:** Focused pytest, readiness/pin comparison, final integration, structured GitHub read-back, PR checks, merge state, and cleanup audit must all pass.

## Pre-execution Shape Gate

Create one executable leaf issue in the existing `Phase 3 Ionic Regression` milestone after this plan is committed. Do not parent it under #6 because #6 intentionally owns exactly #12-#14.

Use these six headings exactly:

```markdown
## Outcome

Rebaseline active MEA Phase 3 dependencies onto the current clean ePC-SAFT authority model without changing scientific results or enabling regression execution.

## Context or behavioral delta

The historical blocker moved to `tannerpolley/ePC-SAFT-lab#468`, whose repository no longer owns production issue intake or capability admission. Clean `ePC-SAFT-regression` is a governance-only skeleton and migration Phase 5 provider promotion has not started.

## Scope and non-goals

Update MEA coordination, roadmap, issue, and tracker state; preserve the immutable 1.5.2 pin and readiness receipt. Do not create upstream runtime work, run fitting, change data/results, or open the admission gate.

## Acceptance criteria

- Active MEA artifacts name the clean future owner and migration gate.
- Lab #468 is historical evidence only.
- `upstream_execution_admitted` remains false and all readiness/pin identities remain unchanged.
- #5 closes after completed #11; #18 retains only open #14 as a blocker.
- Final integration and hosted CI pass.

## Verification basis

Focused authority-contract/readiness tests, immutable receipt comparison, `uv run python scripts/check_epcsaft_integration.py --mode final`, structured GitHub read-back, and PR checks.

## Constraints, risks, and authority

MEA owns downstream data and gates. Clean `ePC-SAFT-regression` owns future Ceres regression only after a stage-approved promotion. Exact future API names remain deferred; no external upstream write is authorized.
```

Create it with existing labels `superpowers:issue`, `kind:deliverable`, `area:regression`, `status:ready`, and `type:analysis`. Record the returned issue URL and use its exact number in the Phase 3 milestone update and PR body.

### Task 1: Encode and apply the active authority contract

**Files:**
- Create: `tests/test_phase3_authority_rebaseline.py`
- Modify: `AGENTS.md`
- Modify: `docs/coordination/epcsaft_feedback_reactive_regression_admission.md`
- Modify: `docs/roadmaps/epcsaft_dependency_matrix.md`
- Modify: `docs/superpowers/issues/12-native-regression-result-contract.md`
- Modify: `docs/superpowers/issues/13-coupled-regression-parameter-promotion.md`
- Modify: `docs/superpowers/issues/14-independent-validation-identifiability.md`
- Modify: `docs/superpowers/milestones/phase-3-ionic-regression.md`

**Interfaces:**
- Consumes: doctrine revision 2, migration status, clean repository contexts, pinned package identity, readiness JSON, and the returned rebaseline issue URL.
- Produces: one test-enforced active owner chain and unchanged executable admission state.

**Use Cases:**
- A maintainer can identify historical runtime evidence, current migration authority, and future production ownership without following a stale issue URL.
- A regression attempt remains blocked until immutable clean capability evidence passes the existing acceptance proof.
- The cutover removes the displaced active blocker while retaining historical provenance.

- [ ] **Step 1: Add the failing authority contract test.**

Create `tests/test_phase3_authority_rebaseline.py` with:

```python
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
READINESS = ROOT / "analyses/phase3/ionic_epcsaft_regression/results/readiness/regression_readiness_summary.json"
PIN = "9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785"
SPLIT_HASH = "e7bc893dab825007d009260d2c1f6f5dd42e75ebddbdb4972d52a5ec4f0c1aa0"


def test_active_phase3_docs_use_current_upstream_authority() -> None:
    active_text = "\n".join(path.read_text(encoding="utf-8") for path in ACTIVE_AUTHORITY_FILES)

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
    assert readiness["readiness_decision"] == "preregistration_ready_upstream_execution_blocked"
    assert readiness["split_hash"] == SPLIT_HASH
    assert readiness["source_hashes"]
```

- [ ] **Step 2: Verify RED.**

Run:

```bash
uv run pytest tests/test_phase3_authority_rebaseline.py -q
```

Expected: the authority test fails because active files still contain the old #468 URL and do not consistently name the clean owner/migration gate; the immutable pin/readiness test passes.

- [ ] **Step 3: Update the active authority surface.**

Apply these exact semantic changes:

- Local ignored `AGENTS.md`: rename `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT` as the historical lab/transitional source; name `ePC-SAFT-project/ePC-SAFT`, `ePC-SAFT-regression`, and `ePC-SAFT-migration` as clean owner/control roots; allow development only after stage approval; preserve stable/final pinned behavior. Do not force-add this local policy file.
- Coordination note: add an authority-status section, move lab #468 under historical evidence, name the migration transfer plan as the next gate, and retain the existing required native Ceres/Jacobian/result evidence.
- Dependency matrix: split provider and regression owners, mark 1.5.2 as immutable historical evaluation evidence, remove obsolete task-number expectations, and state that Phase 3 waits on stage-approved clean promotion.
- Issue #12 mirror: replace old #468 under `Blocked by` with the migration transfer gate and clean regression skeleton; retain lab #468 only under a `Historical evidence` heading.
- Issue #13 mirror: keep #12 as its active MEA blocker, add the clean-package promotion receipt as an execution prerequisite, and move lab #468 to historical evidence.
- Issue #14 mirror: keep #13 as its only active blocker and state that candidate-bound validation requires an immutable candidate produced through the clean admitted contract.
- Phase 3 milestone: link this spec, plan, and returned rebaseline issue URL; describe the current authority chain and preserve the readiness hashes.

- [ ] **Step 4: Verify GREEN and immutable inputs.**

Run:

```bash
uv run pytest tests/test_phase3_authority_rebaseline.py tests/test_epcsaft_ionic_native_regression.py tests/test_regression_readiness.py -q
git diff --exit-code -- pyproject.toml uv.lock integration/epcsaft_contract.json data/reference analyses/phase3/ionic_epcsaft_regression/results
```

Expected: tests pass and the protected scientific/runtime paths have no diff.

- [ ] **Step 5: Commit Task 1.**

```bash
git add tests/test_phase3_authority_rebaseline.py docs/coordination/epcsaft_feedback_reactive_regression_admission.md docs/roadmaps/epcsaft_dependency_matrix.md docs/superpowers/issues/12-native-regression-result-contract.md docs/superpowers/issues/13-coupled-regression-parameter-promotion.md docs/superpowers/issues/14-independent-validation-identifiability.md docs/superpowers/milestones/phase-3-ionic-regression.md docs/superpowers/plans/2026-07-16-phase3-upstream-authority-rebaseline-plan.md
git commit -m "docs: rebaseline Phase 3 upstream authority"
```

### Task 2: Reconcile completed and blocked tracker state

**Files:**
- Modify: `docs/superpowers/issues/5-activity-model-comparison-workstream.md`
- Modify: `docs/superpowers/issues/18-publication-figures-editorial.md`
- Modify: live GitHub issues created by the shape gate and #5/#12/#13/#14/#18

**Interfaces:**
- Consumes: committed Task 1 authority text, closed Issue #11 evidence, and the returned rebaseline issue URL.
- Produces: local/live tracker parity with no completed blocker represented as active.

**Use Cases:**
- Phase 2 closes when its sole controlled-comparison child and acceptance evidence are complete.
- Editorial work remains blocked only by open validation work, not by a closed child.
- GitHub evidence visibly matches the rebaseline cutover and repository acceptance contract.

- [ ] **Step 1: Extend the tracker contract test.**

Add to `tests/test_phase3_authority_rebaseline.py`:

```python
def test_local_tracker_mirrors_do_not_keep_completed_issue_11_as_a_blocker() -> None:
    phase2_parent = (ROOT / "docs/superpowers/issues/5-activity-model-comparison-workstream.md").read_text(
        encoding="utf-8"
    )
    editorial = (ROOT / "docs/superpowers/issues/18-publication-figures-editorial.md").read_text(
        encoding="utf-8"
    )

    assert "status:blocked" not in phase2_parent
    assert "- [x] #11 is the only" in phase2_parent
    assert "## Blocked by\n\n- None." in phase2_parent
    assert "issues/11" not in editorial.split("## Blocked by", maxsplit=1)[1].split("## Non-goals", maxsplit=1)[0]
    assert "https://github.com/tannerpolley/MEA-Thermodynamics/issues/14" in editorial
```

- [ ] **Step 2: Verify RED.**

Run:

```bash
uv run pytest tests/test_phase3_authority_rebaseline.py::test_local_tracker_mirrors_do_not_keep_completed_issue_11_as_a_blocker -q
```

Expected: failure because #5 is still blocked and #18 still lists #11.

- [ ] **Step 3: Update local mirrors.**

- In #5, remove `status:blocked`, mark all three acceptance criteria complete, replace `Blocked by` with `- None.`, and add a closeout note naming merged PR #19 and the passing controlled-comparison proof.
- In #18, remove #11 from `Blocked by` and retain #14 unchanged.

- [ ] **Step 4: Verify local GREEN.**

Run:

```bash
uv run pytest tests/test_phase3_authority_rebaseline.py -q
```

Expected: all authority and tracker mirror tests pass.

- [ ] **Step 5: Update live GitHub issues from validated mirrors.**

Run:

```bash
gh issue edit 12 -R tannerpolley/MEA-Thermodynamics --body-file docs/superpowers/issues/12-native-regression-result-contract.md
gh issue edit 13 -R tannerpolley/MEA-Thermodynamics --body-file docs/superpowers/issues/13-coupled-regression-parameter-promotion.md
gh issue edit 14 -R tannerpolley/MEA-Thermodynamics --body-file docs/superpowers/issues/14-independent-validation-identifiability.md
gh issue edit 18 -R tannerpolley/MEA-Thermodynamics --body-file docs/superpowers/issues/18-publication-figures-editorial.md
gh issue edit 5 -R tannerpolley/MEA-Thermodynamics --body-file docs/superpowers/issues/5-activity-model-comparison-workstream.md --remove-label status:blocked
gh issue close 5 -R tannerpolley/MEA-Thermodynamics --reason completed --comment "Closed after #11 and merged PR #19 completed the controlled Phase 1/2 comparison and metric-integrity proof. The rebaseline pass removed the stale closed-child blocker from active project state."
```

Expected: all edits succeed and #5 closes as completed.

- [ ] **Step 6: Read back live state.**

Run structured `gh issue view` calls for the rebaseline issue and #5/#12/#13/#14/#18. Verify:

- the rebaseline issue is open, `status:ready`, and in `Phase 3 Ionic Regression`;
- #5 is closed and has no `status:blocked` label;
- #12/#13 contain no old organization #468 URL and name clean regression plus migration authority;
- #14 remains blocked only by #13;
- #18 contains #14 but not #11.

Stop without further GitHub writes if any read-back differs.

- [ ] **Step 7: Commit Task 2.**

```bash
git add tests/test_phase3_authority_rebaseline.py docs/superpowers/issues/5-activity-model-comparison-workstream.md docs/superpowers/issues/18-publication-figures-editorial.md
git commit -m "chore: reconcile project tracker state"
```

### Task 3: Prove, publish, merge, and clean the rebaseline

**Files:**
- Verify: all task-owned commits and protected scientific paths
- Modify: GitHub rebaseline issue and pull request state only

**Interfaces:**
- Consumes: committed local changes and verified live tracker state.
- Produces: merged `main`, closed rebaseline issue, synchronized local/remote branches, and clean repository state.

**Use Cases:**
- A reviewer can independently verify authority, scientific invariants, tracker cutover, and final integration before merge.
- Hosted CI proves the documentation/test changes do not weaken manuscript or package evidence.
- Final cleanup removes the task branch without recreating the forbidden repo-local worktree path.

- [ ] **Step 1: Run focused and repository validation.**

```bash
uv run ruff check tests/test_phase3_authority_rebaseline.py
uv run pytest tests/test_phase3_authority_rebaseline.py tests/test_epcsaft_ionic_native_regression.py tests/test_regression_readiness.py -q
uv run python scripts/check_epcsaft_integration.py --mode final
uv run python scripts/validate_project.py quick
git diff main...HEAD --check
git diff --exit-code main...HEAD -- pyproject.toml uv.lock integration/epcsaft_contract.json data/reference analyses/phase3/ionic_epcsaft_regression/results
```

Expected: all commands pass; final integration reports package 1.5.2 at pinned commit `9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785`; protected paths have no diff.

- [ ] **Step 2: Run cleanup audit before publication.**

```bash
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
git status --short --branch
```

Expected: cleanup reports clean except for committed branch divergence; worktree has no uncommitted files.

- [ ] **Step 3: Push and create the PR.**

```bash
git push -u origin codex/phase3-authority-rebaseline
REBASELINE_ISSUE=$(gh issue list -R tannerpolley/MEA-Thermodynamics --state open --search '"Rebaseline Phase 3 upstream authority" in:title' --json number,title --jq 'map(select(.title == "Rebaseline Phase 3 upstream authority")) | if length == 1 then .[0].number else error("expected exactly one rebaseline issue") end')
gh pr create -R tannerpolley/MEA-Thermodynamics --base main --head codex/phase3-authority-rebaseline --title "Rebaseline Phase 3 upstream authority" --body "Closes #${REBASELINE_ISSUE}. Reclassifies lab #468 as historical evidence, names clean ePC-SAFT-regression plus migration authorization as the future authority path, preserves the pinned 1.5.2/readiness contracts, closes stale Phase 2 parent #5, and removes completed #11 from #18."
```

- [ ] **Step 4: Wait for and inspect hosted checks.**

Use `gh pr checks --watch` and inspect failures by owning job. Do not merge while any required check is pending or failed.

- [ ] **Step 5: Merge and synchronize.**

```bash
gh pr merge --merge --delete-branch
git switch main
git pull --ff-only origin main
```

Expected: PR merged, remote task branch deleted, and local `main` equals `origin/main`.

- [ ] **Step 6: Final read-back and cleanup.**

Verify the PR is merged, the rebaseline issue is closed, #5 remains closed, #12-#14/#18 bodies match the merged artifacts, readiness/pin invariants still hold, only local `main` remains, and only the primary worktree is registered. Run:

```bash
bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .
git status --short --branch
git branch --format='%(refname:short)'
git worktree list --porcelain
```

Expected: clean synchronized `main`, no task branch, no repo-local `.worktrees`, and one registered primary checkout.
