# Document computational methods and reproducibility

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/16
**GitHub Milestone:** Manuscript Submission
Parent Issue: https://github.com/tannerpolley/MEA-Thermodynamics/issues/15
**Source Spec:** docs/superpowers/specs/2026-07-13-computational-methods-reproducibility-design.md
**Source Plan:** docs/superpowers/plans/2026-07-13-computational-methods-reproducibility-plan.md
**Labels:** superpowers:issue, kind:deliverable, area:reproducibility, priority:submission-blocker, status:blocked, type:manuscript
Sub-Issue Role: leaf
Executable: true
**Goal Command:** /goal Generate and publish a testable computational-method inventory for the manuscript.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-13-computational-methods-reproducibility-plan.md#outcome-proof
**Intent:** Make executed algorithms, settings, failures, versions, and runtimes testable rather than implicit.
**Target Output:** Method inventory, generator/test, revised sections/table, commands, and fresh PDF.
**Owner:** Reproducibility maintainer.
**Interface:** `build_method_inventory() -> dict` and `docs/latex/generated/method_inventory.json`.
**Cutover:** Manuscript values derive from the inventory instead of manual prose constants.
**Replaced Path:** Retire undocumented defaults and untested duplicated settings.
**Acceptance Proof:** Inventory covers every required field and manuscript/runtime values match exactly.
**Stop Criteria:** Stop on conflicting sources, hidden defaults, unpinned package state, or missing final Phase 3 algorithm.
**Avoid:** No prospective method presented as executed or exhaustive settings dumped without explanation.

## Acceptance Criteria

- [ ] Inventory algorithms, initialization, continuation, limits, damping, tolerances, failures, correlations, versions, and runtime.
- [ ] Attach source locators and hashes to every material setting.
- [ ] Make manuscript methods and generated tables consume the inventory.
- [ ] Build and verify a fresh deterministic manuscript PDF.

## Blocked by

- https://github.com/tannerpolley/MEA-Thermodynamics/issues/6

## Non-goals

- Describe prospective Phase 3 methods as executed.
- Duplicate runtime constants manually in prose.

## Proof Oracle

- Focused method-inventory and manuscript consistency tests.
- `uv run python scripts/check_epcsaft_integration.py --mode final`
- `bash scripts/build_manuscript.sh`
