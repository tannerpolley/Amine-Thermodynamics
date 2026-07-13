# Final cross-workstream submission readiness gate

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/10
**GitHub Milestone:** Manuscript Submission
**Source Spec:** docs/superpowers/specs/2026-07-13-final-submission-readiness-gate-design.md
**Source Plan:** docs/superpowers/plans/2026-07-13-final-submission-readiness-gate-plan.md
**Labels:** superpowers:issue, kind:workstream, priority:submission-blocker, status:hitl, type:manuscript
Sub-Issue Role: parent
Executable: false
**Goal Command:** HITL aggregation gate; no implementation work belongs under this issue.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-13-final-submission-readiness-gate-plan.md#outcome-proof
**Intent:** Make #10 an independent cross-workstream proof gate rather than a mega-parent or implementation queue.
**Target Output:** Updated #10 mirror/body, blocked-by links, readiness matrix, final verification receipt, and human decision.
**Owner:** Project maintainer and corresponding author.
**Interface:** This mirror, GitHub #10, and the final readiness receipt.
**Cutover:** Replace broad task ownership with evidence aggregation.
**Replaced Path:** Retire tests-only and mega-parent readiness semantics.
**Acceptance Proof:** Every matrix lane passes and the author explicitly selects submit or hold after reviewing final artifacts.
**Stop Criteria:** Any failed, stale, or missing receipt keeps #10 blocked and routes to its owner.
**Avoid:** No submission action, implicit approval, or readiness claim from quick validation alone.

## Acceptance Criteria

- [ ] #5 closes with controlled model-comparison evidence.
- [ ] #6 closes with native regression, promotion, validation, and identifiability evidence.
- [ ] #15 closes with methods, metadata/archive, visual, and editorial evidence.
- [ ] Final confidence validation, pinned ePC-SAFT integration, deterministic PDF, metadata, and archive checks pass.
- [ ] The corresponding author records an explicit submit or hold decision.

## Blocked by

- https://github.com/tannerpolley/MEA-Thermodynamics/issues/5
- https://github.com/tannerpolley/MEA-Thermodynamics/issues/6
- https://github.com/tannerpolley/MEA-Thermodynamics/issues/15

## Non-goals

- Own implementation tasks or child issues.
- Submit the manuscript.
- Override failed evidence with a generic approval.

## Proof Oracle

- Cross-workstream readiness matrix with current receipts.
- `uv run python scripts/validate_project.py confidence`
- `uv run python scripts/check_epcsaft_integration.py --mode final`
- Deterministic manuscript build and explicit submit/hold decision.
