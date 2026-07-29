# Preregister and execute coupled regression after upstream admission

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/13
**GitHub Milestone:** Phase 3 Ionic Regression
Parent Issue: https://github.com/tannerpolley/MEA-Thermodynamics/issues/6
**Source Spec:** docs/superpowers/specs/2026-07-13-coupled-regression-parameter-promotion-design.md
**Source Plan:** docs/superpowers/plans/2026-07-13-coupled-regression-parameter-promotion-plan.md
**Submission Sprint:** docs/superpowers/plans/2026-07-17-fluid-phase-equilibria-submission-sprint-plan.md
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

Issue #12 can close only after a stage-approved clean `ePC-SAFT/ePC-SAFT-regression` slice produces an immutable capability and integration receipt. No lab issue or capability payload can satisfy this execution prerequisite.

## Historical evidence

- https://github.com/tannerpolley/ePC-SAFT-lab/issues/468 records the original admission request but does not schedule clean production work.

## Frozen Data Readiness Prerequisite

- Target admission: `data/reference/MEA/manifests/target_admission_manifest.csv`
- Grouped split: `data/reference/MEA/manifests/grouped_split_manifest.csv`
- Readiness receipt: `analyses/phase3/ionic_epcsaft_regression/results/readiness/regression_readiness_summary.json`
- Split hash: `af205ad5968667cf25dc9205d780738035769664a94cc9a421cd3c67148ff804`
- Frozen state membership: 147 training and 220 reserved states.
- Executable Gate 0 v2 observations: 24 training and 97 reserved pressure rows;
  131 training and 67 reserved speciation scalars.
- Active coordinates: `MEAH+::sigma`, `MEAH+::epsilon_over_k`, and
  `MEACOO-::sigma`, in that order.

Loading is a state input, not an observation target. Heat of absorption is
`NOT_ADMITTED` until its definition, sign, reference state, basis, uncertainty,
and covariance are source-complete. Reported-zero speciation rows without
source-backed detection bounds, model-derived pressure rows, and Böttinger
states at or above 0.5 loading are not executable. No tracer row is selected
until both its pressure and speciation contracts are complete.

Execution remains blocked by Issue #12 and by the typed Gate 0 preregistration
blockers. Density is staged under its frozen source-specific scales; dielectric,
pH, ionic activity, viscosity, calorimetry, and heat targets remain non-admitted.

## Submission Sprint Role

Gate 0 freezes and tests the application contract without running a fit. A
later execution must preserve the 147-state training membership while consuming
only observation rows that remain executable under the frozen metrology and
speciation rules.

## Non-goals

- Tune gates after observing results.
- Manually edit promoted artifacts.

## Proof Oracle

- Immutable preregistration and input hashes.
- Upstream capability and immutable package-source receipt.
- Native regression result and approval receipt.
- Clean repeat generation after eligible promotion.
