# Coupled Regression and Parameter Promotion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze a preregistered coupled pressure/speciation fit, then execute and promote it only after upstream public capability admission and every scientific/artifact gate pass.

**Architecture:** Immutable preregistration and input hashes drive a run-local package fit; an approval checker alone may copy an approved candidate into curated parameters.

**Tech Stack:** Python 3.13, pinned ePC-SAFT, NumPy/pandas, JSON/CSV, pytest, `uv`, Bash.

## Global Constraints

- Full-model endpoint; joint pressure/speciation evidence is mandatory.
- Freeze targets, split, parameters, bounds, weights, and gates before full execution.
- Failed/smoke runs cannot mutate curated artifacts.
- Full execution is blocked until #12 proves public reactive target admission, native Ceres ownership, supported derivatives, complete diagnostics, and immutable package sources.

## Source Evidence

- Spec: `docs/superpowers/specs/2026-07-13-coupled-regression-parameter-promotion-design.md`.
- Existing entrypoint: `analyses/phase3/ionic_epcsaft_regression/scripts/fit_global_pressure_speciation.py`.

## Outcome Proof

**Intent:** Replace provisional historical parameters with a reproducible current fit.
**Current Behavior:** Global summary reports `success=false`, `nfev=0`, and a fixed provisional set; the upstream split regression surface is not yet admitted for this problem.
**Expected Outcome:** A preregistered full run either promotes an approved candidate or records a specific scientific failure.
**Target Output:** Preregistration, immutable run bundle, package result, diagnostics, promotion decision, and curated parameter artifact on pass.
**Owner:** Regression maintainer.
**Interface:** Full-fit entrypoint plus `approval_check --run-label final_candidate --promote`.
**Cutover:** Approved curated parameters replace provisional current values in downstream consumers.
**Replaced Path:** Retire historical/provisional promotion semantics and zero-evaluation global summaries as current fit evidence.
**Evidence:** RED/GREEN promotion tests, full run receipts, hashes, metrics, bounds, and parameter deltas.
**Acceptance Proof:** Package reports convergence/success, objective improves, all required rows succeed, gates pass, and promotion is atomic.
**Stop Criteria:** Stop on absent upstream admission, contract failure, nonconvergence, missing rows, disallowed bounds, implausibility, or mutable dependency state.
**Avoid:** No threshold tuning after results, pressure-only promotion, or manual artifact editing.
**Risk:** Scientific nonidentifiability or runtime cost may prevent promotion and therefore block the selected paper endpoint.

## Implementation Boundaries

**Files To Create:** preregistration schema/artifact and promotion fixtures.
**Files To Modify:** `global_regression.py`, `approval_check.py`, full-fit entrypoint, promotion tests, curated parameter manifest on pass.
**Files To Avoid:** Upstream kernels and manuscript claims before validation.
**Source Of Truth:** Frozen preregistration plus package result.
**Read Path:** Canonical targets and parameter evidence to native problem.
**Write Path:** Run-local artifacts to approval receipt to curated parameters only on pass.
**Integration Points:** Native contract, validation split, sensitivity, renderers, final integration.
**Migration Or Cutover:** Prove promotion isolation, execute fit, then atomically cut over approved parameters.
**Replaced Path Handling:** Remove old provisional-current labels when promotion succeeds; retain failed runs only as diagnostics.
**Acceptance Proof Gate:** Approval checker and deterministic regeneration pass before any manuscript consumer updates.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Objective | Approved spec | Joint pressure/speciation with preregistered components. | Supports full-model claim. | No | regression owner |
| Budget | Reduced throughput evidence | Size without changing success gates. | Controls runtime honestly. | Yes | regression owner |

## Test Complete and Metrics

- Promotion tests prove failed/smoke runs leave curated hashes unchanged.
- Full result has positive evaluations, converged status, objective improvement, complete rows, and acceptable bounds.
- Second approved regeneration is deterministic.

### Task 1: Preregister and guard promotion

**Use Cases:**
- Acceptance proof is fixed before execution and the displaced provisional path cannot overwrite curated values.

**Files:**
- Create: `analyses/phase3/ionic_epcsaft_regression/config/final_fit_preregistration.json`
- Modify: `tests/test_epcsaft_ionic_artifact_promotion.py`, `src/MEA/epcsaft_ionic/approval_check.py`

**Interfaces:**
- Consumes: frozen target/parameter hashes.
- Produces: promotion decision with exact failed/passed gates.

- [ ] **Step 1: RED** — add tests for zero evaluations, nonconvergence, objective regression, active bounds, missing rows, and curated-hash protection; expect failures.
- [ ] **Step 2: GREEN** — implement preregistration validation and atomic promotion gating.
- [ ] **Step 3: Verify/refactor** — rerun focused tests; expect PASS and no duplicated gate logic.
- [ ] **Step 4: Checkpoint commit** — commit as `test: preregister coupled fit promotion`.

### Task 2: Preflight upstream admission, then execute and promote the full fit

**Use Cases:**
- The target-perspective result is visible whether promotion passes or the old provisional path remains displaced.

**Files:**
- Modify: full-fit entrypoint and run artifacts; modify curated parameter manifest only on pass.

**Interfaces:**
- Consumes: validated native contract and preregistration.
- Produces: immutable run and promotion receipt.

- [ ] **Step 1: Preflight** — require #12 closeout and verify capability admission, native Ceres/derivative metadata, complete result schema, and immutable package identities.
- [ ] **Step 2: Benchmark** — run the reduced public problem and record throughput, status, evaluations, and package refs.
- [ ] **Step 3: Execute** — run the full preregistered package-native fit with the measured budget.
- [ ] **Step 4: Verify/promote if eligible** — require explicit PASS, atomically update curated artifacts, and rerun deterministic generation; otherwise preserve a failed-run diagnostic without claim promotion.
- [ ] **Step 5: Checkpoint commit** — commit the approved receipt/artifacts or the honest blocker evidence.
