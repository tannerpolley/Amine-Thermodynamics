# Native regression and independent validation workstream

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/6
**GitHub Milestone:** Phase 3 Ionic Regression
**Source Spec:** docs/superpowers/specs/2026-07-13-phase3-regression-validation-workstream-design.md
**Source Plan:** docs/superpowers/plans/2026-07-13-phase3-regression-validation-workstream-plan.md
**Labels:** superpowers:issue, kind:workstream, area:regression, priority:submission-blocker, status:blocked, type:analysis
Sub-Issue Role: parent
Executable: false
**Goal Command:** Not executable; aggregate the three ordered child receipts.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-13-phase3-regression-validation-workstream-plan.md#outcome-proof
**Intent:** Replace overlapping Phase 3 queues with one dependency-ordered regression and validation workstream.
**Target Output:** Updated #6 mirror/body, three child links, dependency graph, and #3 closure receipt.
**Owner:** Phase 3 maintainer.
**Interface:** This mirror, GitHub #6, and child closeout receipts.
**Cutover:** Replace duplicate #3/#6 active scope with one parent graph.
**Replaced Path:** Retire #3 as an active work queue while preserving its historical discussion.
**Acceptance Proof:** #6 has exactly three intended children in order and #3 links to the native-contract child before closure.
**Stop Criteria:** Stop if any child is missing, dependency direction is wrong, or #3 transfer is incomplete.
**Avoid:** Do not close #6 or claim fitting progress from scaffolding.

## Acceptance Criteria

- [ ] #12 proves the native request/result/status contract.
- [ ] #13 executes and conditionally promotes the coupled regression only after #12.
- [ ] #14 proves independent validation and identifiability only after #13.
- [ ] #3 is closed as superseded with links to #6 and #12.

## Blocked by

- https://github.com/tannerpolley/MEA-Thermodynamics/issues/12
- https://github.com/tannerpolley/MEA-Thermodynamics/issues/13
- https://github.com/tannerpolley/MEA-Thermodynamics/issues/14

## Non-goals

- Treat scaffolding or zero-evaluation output as a completed fit.
- Implement a downstream optimizer outside ePC-SAFT.

## Proof Oracle

- Structured GitHub read-back for milestone, labels, three-child hierarchy, and #3 closure.
- Child closeout receipts and final ePC-SAFT integration proof.
