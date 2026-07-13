# Independent Validation and Identifiability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove or reject predictive validity and practical identifiability of the immutable Phase 3 candidate on preregistered reserved evidence.

**Architecture:** Grouped holdout membership is frozen before fitting; validation, sensitivity, robustness, bounds, and plausibility operate on the candidate hash and write separate evidence lanes.

**Tech Stack:** Python 3.13, NumPy/pandas, SciPy diagnostics where non-optimizing, pytest, Matplotlib, `uv`.

## Global Constraints

- No split leakage or post hoc relabeling.
- Training, validation, and sensitivity language remain distinct.
- Failed predictions remain visible and penalized according to the preregistered policy.

## Source Evidence

- Spec: `docs/superpowers/specs/2026-07-13-independent-validation-identifiability-design.md`.
- Existing scripts: validation-split and parameter-sensitivity entrypoints under Phase 3.

## Outcome Proof

**Intent:** Distinguish optimizer convergence from predictive and parameter trust.
**Current Behavior:** Existing split/sensitivity artifacts are post hoc diagnostics on provisional values.
**Expected Outcome:** Reserved groups test an immutable candidate and identifiability claims are evidence-bounded.
**Target Output:** Frozen split, validation predictions/metrics, sensitivity/robustness artifacts, and approval receipt.
**Owner:** Model-validation maintainer.
**Interface:** `evaluate_candidate(candidate_hash, split_manifest) -> ValidationBundle`.
**Cutover:** Manuscript validation claims consume the new reserved-evidence artifacts.
**Replaced Path:** Demote post hoc train-validation wording and provisional sensitivity as current validation proof.
**Evidence:** Leakage tests, deterministic predictions, grouped metrics, perturbation/multistart results, and candidate hash checks.
**Acceptance Proof:** No leakage; all reserved rows accounted for; metrics/uncertainty/failed rows visible; identifiability decision names weak directions.
**Stop Criteria:** Stop on candidate drift, leakage, missing groups, failed-row omission, or singular analyses overstated as identified.
**Avoid:** No training residuals presented as validation or unsupported confidence intervals.
**Risk:** Data may be insufficient; the correct outcome may be claim narrowing or a blocked paper.

## Implementation Boundaries

**Files To Create:** split manifest tests and candidate-validation receipt.
**Files To Modify:** `evaluate_train_validation_split.py`, `compute_parameter_sensitivity.py`, Phase 3 tests, manuscript validation narrative.
**Files To Avoid:** Fitting code and candidate parameters.
**Source Of Truth:** Frozen split manifest and immutable candidate hash.
**Read Path:** Candidate and reserved targets to predictions and analyses.
**Write Path:** Separate validation/sensitivity result roots and approval receipt.
**Integration Points:** Approval check, manuscript results, final readiness.
**Migration Or Cutover:** Reproduce old diagnostic limitation, add leakage tests, then replace claims with new evidence.
**Replaced Path Handling:** Label old artifacts historical/diagnostic or remove them from active manuscript inputs.
**Acceptance Proof Gate:** Focused tests, deterministic rerun, and manuscript claim tests pass.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Holdout | Approved spec | Grouped, preregistered, frozen before fit. | Prevents leakage. | No | validation maintainer |

## Test Complete and Metrics

- Leakage and hash-drift fixtures fail correctly before implementation and pass afterward.
- Validation rows reconcile by source/condition and expose failures.
- Identifiability report records correlations, weak directions, bounds, and perturbation stability.

### Task 1: Freeze and prove independent validation

**Use Cases:**
- Acceptance evidence is target-perspective and post hoc old-path validation is displaced at cutover.

**Files:**
- Modify: `analyses/phase3/ionic_epcsaft_regression/scripts/evaluate_train_validation_split.py`
- Test: Phase 3 validation tests and split fixtures.

**Interfaces:**
- Consumes: immutable candidate hash and grouped split.
- Produces: validation bundle with complete row accounting.

- [ ] **Step 1: RED** — add leakage, changed-candidate, missing-group, and failed-row tests; run focused tests and expect failures.
- [ ] **Step 2: GREEN** — implement frozen split validation and complete prediction accounting.
- [ ] **Step 3: Verify** — rerun tests and deterministic validation generation; expect PASS and no diff on repeat.
- [ ] **Step 4: Checkpoint commit** — commit as `feat: add independent phase 3 validation`.

### Task 2: Gate identifiability and claims

**Use Cases:**
- Reviewers see proof of weak directions and migration away from provisional sensitivity claims.

**Files:**
- Modify: `compute_parameter_sensitivity.py`, Phase 3 sensitivity tests, results narrative.

**Interfaces:**
- Consumes: validated candidate and predictions.
- Produces: identifiability/robustness decision.

- [ ] **Step 1: RED** — add tests for active-bound and nonidentifiable fixtures; expect rejection failures.
- [ ] **Step 2: GREEN** — add correlation, perturbation, and plausibility gates with explicit limitations.
- [ ] **Step 3: Verify** — regenerate sensitivity/robustness twice and run manuscript claim tests.
- [ ] **Step 4: Checkpoint commit** — commit as `feat: gate phase 3 identifiability`.

