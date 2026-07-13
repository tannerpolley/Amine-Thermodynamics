# Establish controlled Phase 1/2 model comparison and metric integrity

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/11
**GitHub Milestone:** Phase 2 Activity ePC-SAFT
Parent Issue: https://github.com/tannerpolley/MEA-Thermodynamics/issues/5
**Source Spec:** docs/superpowers/specs/2026-07-13-controlled-model-comparison-metrics-design.md
**Source Plan:** docs/superpowers/plans/2026-07-13-controlled-model-comparison-metrics-plan.md
**Labels:** superpowers:issue, kind:deliverable, area:model-comparison, priority:submission-blocker, status:ready, type:analysis
Sub-Issue Role: leaf
Executable: true
**Goal Command:** /goal Establish a controlled same-record Phase 1/2 comparison and repair metric integrity.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-13-controlled-model-comparison-metrics-plan.md#outcome-proof
**Intent:** Make every Phase 1/2 performance comparison scientifically commensurate and traceable to saved rows.
**Target Output:** Comparison module, paired CSV, metrics JSON/CSV, uncertainty coverage, revised table/text, and proof tests.
**Owner:** Model-validation maintainer.
**Interface:** `build_controlled_comparison()` and `analyses/phase2/activity_epcsaft/results/controlled_comparison/`.
**Cutover:** Manuscript comparisons consume generated paired metrics rather than manually juxtaposed summaries.
**Replaced Path:** Retire the manual 31-versus-161 comparison and hard-coded reported-zero count.
**Acceptance Proof:** Saved paired rows reproduce published metrics and canonical role aggregation yields 15 reported-zero targets unless source data intentionally change.
**Stop Criteria:** Stop on duplicate keys, incompatible units/reaction bases, role ambiguity, or unexplained row loss.
**Avoid:** No fake uncertainties, silent failure exclusion, or post hoc metric selection.

## Acceptance Criteria

- [ ] Join both models on stable, identical experimental-record identities and expose rejected rows.
- [ ] Generate paired and full-set contextual metrics with source/uncertainty coverage.
- [ ] Correct the reported-zero target count from 14 to the canonical 15, or document a proven source change.
- [ ] Bound Wong/curve-grid claims to the evidence actually evaluated.
- [ ] Build the manuscript and visually inspect the revised table and claims.

## Blocked by

- None.

## Non-goals

- Refit Phase 3 parameters.
- Select metrics after inspecting which model looks better.

## Proof Oracle

- `uv run pytest tests/test_model_comparison.py -q`
- Deterministic paired CSV and metrics JSON/CSV regeneration.
- `bash scripts/build_manuscript.sh`
