# Preregister and execute coupled regression after upstream admission

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/13
**GitHub Milestone:** Phase 3 Ionic Regression
Parent Issue: https://github.com/tannerpolley/MEA-Thermodynamics/issues/6
**Source Spec:** docs/superpowers/specs/2026-07-13-coupled-regression-parameter-promotion-design.md
**Source Plan:** docs/superpowers/plans/2026-07-13-coupled-regression-parameter-promotion-plan.md
**Labels:** superpowers:issue, kind:deliverable, area:regression, priority:submission-blocker, status:blocked, type:analysis
Sub-Issue Role: leaf
Executable: true
**Goal Command:** /goal Preregister the coupled fit, then execute and conditionally promote it only after upstream capability admission.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-13-coupled-regression-parameter-promotion-plan.md#outcome-proof
**Intent:** Prepare an immutable preregistration now, then replace provisional zero-evaluation evidence with an admitted native joint fit and guarded promotion decision.
**Target Output:** Preregistration, immutable run bundle, package result, diagnostics, promotion decision, and curated parameter artifact on pass.
**Owner:** Regression maintainer.
**Interface:** Full-fit entrypoint plus `approval_check --run-label final_candidate --promote`.
**Cutover:** Approved curated parameters replace provisional current values in downstream consumers.
**Replaced Path:** Retire historical/provisional promotion semantics and zero-evaluation global summaries as current fit evidence.
**Acceptance Proof:** Package reports convergence/success, objective improves, all required rows succeed, gates pass, and promotion is atomic.
**Stop Criteria:** Stop execution on absent upstream admission, contract failure, nonconvergence, missing rows, disallowed bounds, implausibility, or mutable dependency state.
**Avoid:** No threshold tuning after results, pressure-only promotion, or manual artifact editing.

## Acceptance Criteria

- [ ] Freeze objective, bounds, inputs, hashes, split, and acceptance gates before the full run.
- [ ] Verify the upstream capability report admits generic coupled reactive pressure/speciation targets, a native Ceres hot loop, supported derivatives, and the complete result schema.
- [ ] Record benchmark throughput and execute the native joint pressure/speciation fit.
- [ ] Reject zero-evaluation, nonconverged, incomplete, implausible, or degraded candidates.
- [ ] Promote atomically only when every preregistered gate passes.

## Blocked by

- https://github.com/tannerpolley/MEA-Thermodynamics/issues/12
- https://github.com/ePC-SAFT/ePC-SAFT/issues/468

## Non-goals

- Tune gates after observing results.
- Manually edit promoted artifacts.

## Proof Oracle

- Immutable preregistration and input hashes.
- Upstream capability and immutable package-source receipt.
- Native regression result and approval receipt.
- Clean repeat generation after eligible promotion.
