# Paper Validation: lock Baygi 2015 recreation acceptance gate

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/9
**GitHub Milestone:** Paper Validation
**Issue Type:** task
**Source Spec:** none
**Source Plan:** docs/superpowers/plans/starter-milestone-issues.md
**Classification:** AFK
**Labels:** status:ready, superpowers:issue, type:analysis, phase:paper-validation
**Goal Command:** /goal Lock the Baygi 2015 paper-validation acceptance gate and prove the artifacts remain manuscript-ready.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/starter-milestone-issues.md#paper-validation-baygi-2015-acceptance-gate
**Intent:** Lock a repeatable acceptance gate for the Baygi 2015 recreation artifacts before later manuscript work depends on them.
**Target Output:** A reviewer can inspect the Baygi validation root and see which artifacts prove paper recreation, which plot bundle files exist, and which validation command protects them.
**Owner:** analyses/paper_validation/2015_baygi
**Interface:** Analysis README, generated artifact files, validation checks, and milestone links.
**Cutover:** Keep the current analysis root and tighten its acceptance documentation and validation coverage.
**Replaced Path:** Informal paper-validation confidence based on manually inspecting generated files.
**Acceptance Proof:** Baygi artifact checks plus `uv run python scripts/validate_project.py quick`.
**Stop Criteria:** Stop when the Baygi artifact gate is explicit, quick validation passes, and no manuscript-facing claim relies on an unstated paper-recreation assumption.
**Avoid:** Creating a second Baygi validation root, treating screenshots as source artifacts, or moving paper-validation work under milestone-owned folders.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Create a narrow Baygi 2015 paper-validation acceptance gate that documents expected artifacts, checks Matplotlib plot companions, and ties the proof to quick validation.

## Acceptance Criteria

- [ ] Document the Baygi 2015 validation target, reproduced artifacts, and manuscript-use boundary in or near `analyses/paper_validation/2015_baygi`.
- [ ] Verify generated Baygi Matplotlib outputs have plotted-data snapshots plus PNG, SVG, PDF, and `.mpl.yaml` companions where applicable.
- [ ] Confirm `uv run python scripts/validate_project.py quick` covers the Baygi artifacts or add focused checks for missing coverage.
- [ ] Update `docs/superpowers/milestones/paper-validation.md` if the validated acceptance boundary changes.

## Blocked by

- None

## Non-goals

- Do not create a second Baygi validation root.
- Do not redigitize figures unless the current artifact proof is insufficient.
- Do not move canonical issue artifacts under milestone folders.

## Proof Oracle

- `uv run python scripts/validate_project.py quick`
- File checks for Baygi plotted-data snapshots and PNG/SVG/PDF/`.mpl.yaml` companions.
