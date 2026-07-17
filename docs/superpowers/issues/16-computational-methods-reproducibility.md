# Document computational methods and reproducibility

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/16
**GitHub Milestone:** Manuscript Submission
Parent Issue: https://github.com/tannerpolley/MEA-Thermodynamics/issues/15
**Source Spec:** docs/superpowers/specs/2026-07-13-computational-methods-reproducibility-design.md
**Source Plan:** docs/superpowers/plans/2026-07-13-computational-methods-reproducibility-plan.md
**Submission Sprint:** docs/superpowers/plans/2026-07-17-fluid-phase-equilibria-submission-sprint-plan.md
**Labels:** superpowers:issue, kind:deliverable, area:reproducibility, priority:submission-blocker, status:blocked, type:manuscript
Sub-Issue Role: leaf
Executable: true
**Goal Command:** /goal Generate and publish a testable computational-method inventory for the manuscript.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-13-computational-methods-reproducibility-plan.md#outcome-proof
**Intent:** Build the testable method-inventory machinery now, then publish only the exact algorithms, settings, failures, versions, and runtimes recorded by the accepted #13/#14 execution receipts.
**Target Output:** Method inventory, generator/test, revised sections/table, commands, and fresh PDF.
**Owner:** Reproducibility maintainer.
**Interface:** `build_method_inventory() -> dict` and `docs/latex/generated/method_inventory.json`.
**Cutover:** Manuscript values derive from the inventory instead of manual prose constants.
**Replaced Path:** Retire undocumented defaults and untested duplicated settings.
**Acceptance Proof:** Every published method field is bound to final Phase 3 evidence and immutable package identities; no prospective or unresolved method field enters the compiled manuscript.
**Stop Criteria:** Stop on conflicting sources, hidden defaults, unpinned package state, or missing final Phase 3 algorithm.
**Avoid:** No prospective method presented as executed or exhaustive settings dumped without explanation.

## Acceptance Criteria

- [ ] Inventory the executed algorithms, initialization, continuation, limits, damping, tolerances, failures, correlations, versions, and runtime from accepted #13/#14 receipts.
- [ ] Attach source locators and hashes to every material setting.
- [ ] Make manuscript methods and generated tables consume the inventory.
- [ ] Build and verify a fresh deterministic manuscript PDF.

## Blocked by

- https://github.com/tannerpolley/MEA-Thermodynamics/issues/14

## Submission Sprint Role

Method-inventory code and tests may be prepared early, but submission-facing method content is generated only after #13 and #14 close. The Wednesday manuscript freeze must contain final executed language, not status markers or prospective solver descriptions.

## Non-goals

- Describe prospective Phase 3 methods as executed.
- Duplicate runtime constants manually in prose.

## Proof Oracle

- Focused method-inventory and manuscript consistency tests.
- Test proving absent or nonfinal Phase 3 receipts cannot render submission-facing methods or satisfy closeout.
- `uv run python scripts/check_epcsaft_integration.py --mode final`
- `bash scripts/build_manuscript.sh`
