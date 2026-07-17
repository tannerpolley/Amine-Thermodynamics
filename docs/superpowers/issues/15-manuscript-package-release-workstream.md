# Manuscript package and release workstream

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/15
**GitHub Milestone:** Manuscript Submission
**Source Spec:** docs/superpowers/specs/2026-07-13-manuscript-package-release-workstream-design.md
**Source Plan:** docs/superpowers/plans/2026-07-13-manuscript-package-release-workstream-plan.md
**Submission Sprint:** docs/superpowers/plans/2026-07-17-fluid-phase-equilibria-submission-sprint-plan.md
**Labels:** superpowers:issue, kind:workstream, area:reproducibility, priority:submission-blocker, status:blocked, type:manuscript
Sub-Issue Role: parent
Executable: false
**Goal Command:** Not executable; aggregate methods, release, and editorial child receipts.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-13-manuscript-package-release-workstream-plan.md#outcome-proof
**Intent:** Give manuscript-package work a real owner without turning #10 into a mega-parent.
**Target Output:** New parent issue/mirror, three child relationships, cross-workstream blockers, and milestone update.
**Owner:** Manuscript maintainer.
**Interface:** This mirror and `docs/superpowers/milestones/manuscript-submission.md`.
**Cutover:** Move implementation scope out of #10 into this workstream.
**Replaced Path:** Retire #10's active ownership of methods, metadata, and editorial tasks.
**Acceptance Proof:** Parent has exactly three intended children; #10 links through blocked-by only.
**Stop Criteria:** Stop on missing child, wrong parentage, or unresolved relationship mutation.
**Avoid:** Do not place Phase 2/3 scientific children under this parent.

## Acceptance Criteria

- [ ] #16 owns computational-method reporting and reproducibility proof.
- [ ] #17 owns author-controlled metadata, licensing, release, and archive proof.
- [ ] #18 owns publication figures, tables, layout, and editorial proof.
- [ ] #10 remains independent and is blocked by this parent rather than parenting it.

## Blocked by

- https://github.com/tannerpolley/MEA-Thermodynamics/issues/16
- https://github.com/tannerpolley/MEA-Thermodynamics/issues/17
- https://github.com/tannerpolley/MEA-Thermodynamics/issues/18

## Submission Sprint Role

This workstream aggregates the Wednesday scientific manuscript freeze and Thursday publication freeze. It closes only when #16–18 have mutually consistent receipts; it does not permit a fixed-parameter or incomplete-regression submission fallback.

## Non-goals

- Own Phase 2 comparison or Phase 3 fitting implementation.
- Perform submission or irreversible archival publication.

## Proof Oracle

- Structured GitHub read-back for milestone, labels, and exact three-child hierarchy.
- Three child closeout receipts.
