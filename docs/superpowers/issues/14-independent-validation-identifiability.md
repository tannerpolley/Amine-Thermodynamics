# Prove independent validation and parameter identifiability

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/14
**GitHub Milestone:** Phase 3 Ionic Regression
Parent Issue: https://github.com/tannerpolley/MEA-Thermodynamics/issues/6
**Source Spec:** docs/superpowers/specs/2026-07-13-independent-validation-identifiability-design.md
**Source Plan:** docs/superpowers/plans/2026-07-13-independent-validation-identifiability-plan.md
**Labels:** superpowers:issue, kind:deliverable, area:validation, priority:submission-blocker, status:blocked, type:analysis
Sub-Issue Role: leaf
Executable: true
**Goal Command:** /goal Prove or reject predictive validity and practical identifiability on reserved evidence.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-13-independent-validation-identifiability-plan.md#outcome-proof
**Intent:** Separate training fit quality from predictive validation and expose weak parameter directions honestly.
**Target Output:** Frozen split, validation predictions/metrics, sensitivity/robustness artifacts, and approval receipt.
**Owner:** Model-validation maintainer.
**Interface:** `evaluate_candidate(candidate_hash, split_manifest) -> ValidationBundle`.
**Cutover:** Manuscript validation claims consume the new reserved-evidence artifacts.
**Replaced Path:** Demote post hoc train-validation wording and provisional sensitivity as current validation proof.
**Acceptance Proof:** No leakage; all reserved rows accounted for; metrics, uncertainty, and failed rows visible; identifiability decision names weak directions.
**Stop Criteria:** Stop on candidate drift, leakage, missing groups, failed-row omission, or singular analyses overstated as identified.
**Avoid:** No training residuals presented as validation or unsupported confidence intervals.

## Acceptance Criteria

- [ ] Freeze a grouped holdout manifest before fitting and prove no leakage.
- [ ] Account for every reserved row, including failed predictions.
- [ ] Evaluate sensitivity, robustness, active bounds, correlations, and physical plausibility.
- [ ] Bound manuscript claims to the resulting validation and identifiability decision.

## Blocked by

- https://github.com/tannerpolley/MEA-Thermodynamics/issues/13

## Non-goals

- Present training residuals as validation.
- Report unsupported confidence intervals.

## Proof Oracle

- Frozen split and candidate hashes.
- Deterministic validation/sensitivity bundles.
- Leakage, failure-accounting, and identifiability tests.
