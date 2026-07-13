# Coupled Regression and Parameter Promotion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute a preregistered package-native joint pressure/speciation fit and promote only a converged, improved, plausible parameter set.

**Architecture:** Immutable preregistration and input hashes drive a run-local package fit; an approval checker alone may copy an approved candidate into curated parameters.

**Tech Stack:** Python 3.13, pinned ePC-SAFT, NumPy/pandas, JSON/CSV, pytest, `uv`, Bash.

## Global Constraints

- Full-model endpoint; joint pressure/speciation evidence is mandatory.
- Freeze targets, split, parameters, bounds, weights, and gates before full execution.
- Failed/smoke runs cannot mutate curated artifacts.

## Source Evidence

- Spec: `docs/superpowers/specs/2026-07-13-coupled-regression-parameter-promotion-design.md`.
- Existing entrypoint: `analyses/phase3/ionic_epcsaft_regression/scripts/fit_global_pressure_speciation.py`.

## Outcome Proof

**Intent:** Replace provisional historical parameters with a reproducible current fit.
**Current Behavior:** Global summary reports `success=false`, `nfev=0`, and a fixed provisional set.
**Expected Outcome:** A preregistered full run either promotes an approved candidate or records a specific scientific failure.
**Target Output:** Preregistration, immutable run bundle, package result, diagnostics, promotion decision, and curated parameter artifact on pass.
**Owner:** Regression maintainer.
**Interface:** Full-fit entrypoint plus `approval_check --run-label final_candidate --promote`.
**Cutover:** Approved curated parameters replace provisional current values in downstream consumers.
**Replaced Path:** Retire historical/provisional promotion semantics and zero-evaluation global summaries as current fit evidence.
**Evidence:** RED/GREEN promotion tests, full run receipts, hashes, metrics, bounds, and parameter deltas.
**Acceptance Proof:** Package reports convergence/success, objective improves, all required rows succeed, gates pass, and promotion is atomic.
**Stop Criteria:** Stop on contract failure, nonconvergence, missing rows, disallowed bounds, implausibility, or mutable dependency state.
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

### Task 2: Execute, assess, and promote the full fit

**Use Cases:**
- The target-perspective result is visible whether promotion passes or the old provisional path remains displaced.

**Files:**
- Modify: full-fit entrypoint and run artifacts; modify curated parameter manifest only on pass.

**Interfaces:**
- Consumes: validated native contract and preregistration.
- Produces: immutable run and promotion receipt.

- [ ] **Step 1: Benchmark** — run the reduced problem and record throughput, status, and evaluations.
- [ ] **Step 2: Execute** — run the full preregistered package-native fit with the measured budget.
- [ ] **Step 3: Verify** — run approval; expect explicit PASS or a recorded scientific blocker, never an inferred success.
- [ ] **Step 4: Promote if eligible** — atomically update curated artifacts and rerun deterministic generation.
- [ ] **Step 5: Checkpoint commit** — commit approved artifacts/receipt or the failed-run diagnostic without claim promotion.
