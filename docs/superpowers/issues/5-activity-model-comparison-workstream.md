# Activity-model comparison and metric integrity workstream

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/5
**GitHub Milestone:** Phase 2 Activity ePC-SAFT
**Source Spec:** docs/superpowers/specs/2026-07-13-phase2-model-comparison-workstream-design.md
**Source Plan:** docs/superpowers/plans/2026-07-13-phase2-model-comparison-workstream-plan.md
**Labels:** superpowers:issue, kind:workstream, area:model-comparison, priority:submission-blocker, status:blocked, type:analysis
Sub-Issue Role: parent
Executable: false
**Goal Command:** Not executable; close only after child evidence passes.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-13-phase2-model-comparison-workstream-plan.md#outcome-proof
**Intent:** Preserve completed Phase 2 implementation evidence while isolating the remaining comparison-integrity work.
**Target Output:** Updated #5 body, local mirror, labels, milestone, child relationship, and verification receipt.
**Owner:** Phase 2 maintainer.
**Interface:** This mirror, GitHub #5, and the controlled-comparison child receipt.
**Cutover:** Replace stale implementation checkboxes with completed evidence and remaining child proof.
**Replaced Path:** Retire the old mega-checklist as active project state while preserving it in GitHub history.
**Acceptance Proof:** GitHub shows #5 in the Phase 2 milestone with exactly the intended child and that child's proof passes.
**Stop Criteria:** Stop if evidence counts conflict, the child is absent, or relationship mutation fails.
**Avoid:** Do not close #5 before its child proof passes or rewrite scientific results in the tracker.

## Acceptance Criteria

- [ ] #11 is the only remaining sub-issue and carries the model-comparison implementation scope.
- [ ] Completed Phase 2 pressure/speciation evidence remains linked and reproducible.
- [ ] #5 closes only after the controlled-comparison proof oracle passes.

## Blocked by

- https://github.com/tannerpolley/MEA-Thermodynamics/issues/11

## Non-goals

- Reimplement completed Phase 2 thermodynamic workflows.
- Move Phase 3 regression work into this workstream.

## Proof Oracle

- Structured GitHub read-back for milestone, labels, and one-child hierarchy.
- `uv run python scripts/validate_project.py confidence`
