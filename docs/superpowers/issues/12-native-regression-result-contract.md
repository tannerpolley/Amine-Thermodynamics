# Finalize the native regression result and status contract

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/12
**GitHub Milestone:** Phase 3 Ionic Regression
Parent Issue: https://github.com/tannerpolley/MEA-Thermodynamics/issues/6
**Source Spec:** docs/superpowers/specs/2026-07-13-native-regression-result-contract-design.md
**Source Plan:** docs/superpowers/plans/2026-07-13-native-regression-result-contract-plan.md
**Labels:** superpowers:issue, kind:deliverable, area:regression, priority:submission-blocker, status:ready, type:analysis
Sub-Issue Role: leaf
Executable: true
**Goal Command:** /goal Finalize and prove the pinned native ePC-SAFT regression result contract.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-13-native-regression-result-contract-plan.md#outcome-proof
**Intent:** Make native regression status, diagnostics, and failure semantics explicit and fail-closed.
**Target Output:** Contract module/schema, adversarial tests, reduced smoke artifacts, and integration receipt.
**Owner:** Cross-repo integration maintainer.
**Interface:** `run_native_regression(problem, options) -> NativeRegressionResult`.
**Cutover:** All production fitting calls use the validated adapter.
**Replaced Path:** Retire ad hoc field access and implicit status coercion.
**Acceptance Proof:** Known converged/nonconverged fixtures map correctly; malformed results fail; smoke writes no curated files.
**Stop Criteria:** Stop on unsupported upstream API, mutable package state, or incomplete row diagnostics.
**Avoid:** No downstream optimizer, silent default, or success inference from finite values.

## Acceptance Criteria

- [ ] Validate serialized regression requests and structured package results.
- [ ] Map converged, nonconverged, malformed, nonfinite, and unknown statuses explicitly.
- [ ] Run a reduced native smoke test without mutating curated parameters.
- [ ] Pass final pinned-package integration validation.

## Blocked by

- None.

## Non-goals

- Execute the full coupled fit.
- Change the upstream ePC-SAFT API without a cross-repo contract decision.

## Proof Oracle

- Focused adversarial contract tests.
- Reduced native regression receipt.
- `uv run python scripts/check_epcsaft_integration.py --mode final`
