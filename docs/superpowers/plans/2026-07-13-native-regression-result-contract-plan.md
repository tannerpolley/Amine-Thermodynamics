# Native Regression Result Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lock and verify the pinned ePC-SAFT native regression request/result/status contract consumed by MEA.

**Architecture:** A fail-closed adapter validates serialized problems and structured package results, writes run-local diagnostics, and refuses unknown statuses or curated overwrites.

**Tech Stack:** Python 3.13, `epcsaft` 1.5.2+, JSON Schema-style validation, pytest, `uv`, Bash.

## Global Constraints

- ePC-SAFT owns optimization; MEA owns targets and evidence.
- No SciPy optimizer or fallback contract.
- All runtime artifacts are run-local until later promotion.

## Source Evidence

- Spec: `docs/superpowers/specs/2026-07-13-native-regression-result-contract-design.md`.
- Current seams: `src/MEA/epcsaft_ionic/native_regression.py`, `runtime.py`, and native-regression tests.

## Outcome Proof

**Intent:** Make native fitting integration explicit and failure-safe.
**Current Behavior:** Scaffolding exists, but the final status/result schema and real reduced receipt are not closed.
**Expected Outcome:** One versioned adapter accepts complete results and rejects malformed, unknown, or mutable states.
**Target Output:** Contract module/schema, adversarial tests, reduced smoke artifacts, and integration receipt.
**Owner:** Cross-repo integration maintainer.
**Interface:** `run_native_regression(problem, options) -> NativeRegressionResult`.
**Cutover:** All production fitting calls use the validated adapter.
**Replaced Path:** Retire ad hoc field access and any implicit status coercion.
**Evidence:** Red/green fixtures, real package smoke, immutable metadata, and final-mode integration check.
**Acceptance Proof:** Known converged/nonconverged fixtures map correctly; malformed results fail; smoke writes no curated files.
**Stop Criteria:** Stop on unsupported upstream API, mutable package state, or incomplete row diagnostics.
**Avoid:** No downstream optimizer, silent default, or success inference from finite values.
**Risk:** Upstream schema evolution requires coordinated versioning.

## Implementation Boundaries

**Files To Create:** `src/MEA/epcsaft_ionic/native_contract.py`, `tests/fixtures/native_regression/`.
**Files To Modify:** `native_regression.py`, `runtime.py`, native-regression/approval tests, integration checker.
**Files To Avoid:** Upstream source and curated parameter results.
**Source Of Truth:** Pinned public ePC-SAFT API and serialized contract fixtures.
**Read Path:** Native problem to adapter to package.
**Write Path:** Package result to run-local JSON/CSV diagnostics and receipt.
**Integration Points:** `load_epcsaft()`, approval check, final integration script.
**Migration Or Cutover:** Add rejecting tests, implement adapter, then remove ad hoc access.
**Replaced Path Handling:** Delete implicit field fallbacks and prohibit compatibility shims.
**Acceptance Proof Gate:** Focused tests and real reduced smoke pass at pinned commit.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Status mapping | Approved spec | Explicit allowlist; unknown fails. | Protects claims. | No | adapter maintainer |

## Test Complete and Metrics

- Adversarial schema/status fixtures pass.
- No production optimizer imports exist.
- Reduced smoke records exact package version/commit and no curated diff.

### Task 1: Lock the adapter contract TDD-first

**Use Cases:**
- Acceptance evidence is visible; malformed old-path field access is displaced during cutover.

**Files:**
- Create: `src/MEA/epcsaft_ionic/native_contract.py`, fixture JSON files
- Modify: `tests/test_epcsaft_ionic_native_regression.py`, `src/MEA/epcsaft_ionic/native_regression.py`

**Interfaces:**
- Consumes: serialized problem and package result.
- Produces: validated `NativeRegressionResult`.

- [ ] **Step 1: RED** — add fixtures for converged, nonconverged, missing-field, unknown-status, nonfinite, and mismatched-parameter results; run focused tests and expect failures.
- [ ] **Step 2: GREEN** — implement minimal parsing/validation and explicit status mapping.
- [ ] **Step 3: Refactor/verify** — remove old access paths and rerun focused tests; expect PASS.
- [ ] **Step 4: Smoke** — run reduced native regression and final integration check; expect structured receipt and zero curated diff.
- [ ] **Step 5: Checkpoint commit** — commit as `feat: lock native regression result contract`.

