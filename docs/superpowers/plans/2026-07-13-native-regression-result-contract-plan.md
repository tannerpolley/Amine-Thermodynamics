# Split-Package Reactive Regression Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adopt and prove an upstream-admitted public split-package reactive-regression contract while preserving the current stable integration lane.

**Architecture:** A compatibility matrix and upstream capability gate precede one fail-closed adapter. Development uses an explicit upstream worktree; final evidence uses released or immutable pinned package sources.

**Tech Stack:** Python 3.13, split ePC-SAFT provider/equilibrium/regression packages, Ceres/CppAD capability metadata, pytest, JSON, `uv`, Bash.

## Global Constraints

- Preserve the pinned monolithic 1.5.2 final lane until cutover proof passes.
- ePC-SAFT owns the optimizer and derivative implementation; MEA owns targets, validation, and evidence.
- No private imports, downstream optimizer, shared dirty checkout, silent fallback, or permanent compatibility shim.
- Do not invent public callable or result field names before upstream admission.

## Source Evidence

- Spec: `docs/superpowers/specs/2026-07-13-native-regression-result-contract-design.md`.
- Cross-repo request: `docs/coordination/epcsaft_feedback_reactive_regression_admission.md`.
- Current seams: `src/MEA/epcsaft_ionic/native_regression.py`, `runtime.py`, and the final integration checker.

## Outcome Proof

**Intent:** Make the upstream architecture transition explicit, reproducible, and failure-safe.
**Current Behavior:** MEA is pinned to monolithic 1.5.2; the split public regression package does not yet admit the required coupled reactive problem.
**Expected Outcome:** Upstream publicly admits the capability and MEA consumes it through one validated adapter from immutable package sources.
**Target Output:** Compatibility matrix, upstream receipt, versioned adapter/schema, adversarial tests, reduced public smoke, and final pinned integration receipt.
**Owner:** Cross-repo integration maintainer.
**Interface:** Public split-package APIs through one approved MEA adapter.
**Cutover:** Keep 1.5.2 green, validate the split lane, pin it immutably, switch consumers, then delete legacy access.
**Replaced Path:** Root-package regression calls, private imports, opportunistic field access, and implicit status coercion.
**Evidence:** Capability report, public API tests, red/green fixtures, reduced smoke, immutable metadata, and final-mode integration check.
**Acceptance Proof:** Required reactive target families and native hot loop are admitted; complete results map; malformed states fail; smoke writes no curated files.
**Stop Criteria:** Stop on missing upstream admission, mutable source, private API dependence, unknown result semantics, or incomplete diagnostics.
**Avoid:** No guessed schema, compatibility shim, downstream optimizer, or success inference from finite values.
**Risk:** Upstream capability timing can delay Phase 3; preserve the stable lane and continue independent downstream preparation.

## Implementation Boundaries

**Files To Create:** Compatibility-matrix artifact, admitted contract module/schema, and reduced public fixtures.
**Files To Modify:** `native_regression.py`, `runtime.py`, native-regression/approval tests, dependency metadata, and integration checker.
**Files To Avoid:** Upstream source in this repository, curated parameter results before promotion, and the shared dirty ePC-SAFT checkout.
**Source Of Truth:** Upstream capability report and public API at an immutable source ref.
**Read Path:** Canonical targets and parameter specs to adapter to split packages.
**Write Path:** Structured package result to run-local JSON/CSV diagnostics and receipt.
**Integration Points:** `load_epcsaft()`, approval check, cross-repo checker, and final integration script.
**Migration Or Cutover:** Matrix and upstream gate, dev-worktree smoke, adapter tests, immutable pin, consumer cutover, legacy deletion.
**Replaced Path Handling:** Delete root-package and implicit-field branches after cutover; do not retain a permanent dual path.
**Acceptance Proof Gate:** Focused contract tests and reduced public smoke pass, followed by final-mode validation from immutable sources.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| API schema | Approved spec | Lock only the upstream-admitted public schema. | Prevents speculative integration code. | Yes | upstream regression maintainer |
| Development source | Cross-repo policy | Use one explicit ePC-SAFT development worktree. | Isolates mutable co-development. | No | integration maintainer |
| Final source | Submission proof policy | Require release or immutable Git refs and final-mode validation. | Makes manuscript evidence reproducible. | No | release maintainer |

## Test Complete and Metrics

- Compatibility matrix covers every consumed legacy capability and its split-package owner or explicit gap.
- Capability report proves coupled reactive pressure/speciation targets, native Ceres hot loop, and supported derivative path.
- Adversarial status/schema fixtures pass and no private upstream import exists.
- Reduced public smoke records exact package identities and leaves curated hashes unchanged.
- Final integration passes from immutable package sources.

### Task 1: Publish and track upstream admission

**Use Cases:**
- Acceptance evidence makes the generic upstream gap reproducible without making the public API MEA-specific, while the unsupported private/legacy path remains explicitly displaced.

**Files:**
- Modify: `docs/coordination/epcsaft_feedback_reactive_regression_admission.md`
- Create: compatibility-matrix artifact and its completeness test.

**Interfaces:**
- Consumes: current legacy call sites, split-package capability reports, and a reduced reactive fixture.
- Produces: upstream issue receipt and an explicit gap matrix.

- [ ] **Step 1: Inventory** — map provider, equilibrium, regression, derivatives, status, diagnostics, and provenance from the legacy lane to split-package owners or gaps.
- [ ] **Step 2: Reproduce** — verify the reduced public fixture is rejected as not admitted and record exact immutable source identities.
- [ ] **Step 3: Publish** — submit the generic upstream request and link its milestone/dependencies without editing the shared checkout.
- [ ] **Step 4: Gate** — keep this issue `status:blocked` until public capability reporting and API tests admit the required surface.
- [ ] **Step 5: Checkpoint commit** — commit as `docs: track reactive regression admission`.

### Task 2: Validate the admitted contract TDD-first

**Use Cases:**
- Acceptance evidence proves public result semantics, and cutover tests prevent malformed, private, or legacy paths from silently passing.

**Files:**
- Create: admitted contract module/schema and fixture JSON files.
- Modify: native-regression tests, `native_regression.py`, and `runtime.py`.

**Interfaces:**
- Consumes: admitted public request and structured result.
- Produces: validated MEA regression result and run-local diagnostics.

- [ ] **Step 1: RED** — add fixtures for converged, nonconverged, missing-field, unknown-status, nonfinite, mismatched-parameter, and partial-row results; expect failures.
- [ ] **Step 2: GREEN** — implement minimal parsing, schema validation, and explicit status mapping against the public API.
- [ ] **Step 3: Refactor/verify** — remove implicit/private access and rerun focused tests; expect PASS.
- [ ] **Step 4: Public smoke** — run the reduced problem from the explicit upstream development worktree; expect admitted capability, structured receipt, and zero curated diff.
- [ ] **Step 5: Checkpoint commit** — commit as `feat: validate split reactive regression contract`.

### Task 3: Pin, cut over, and prove the final lane

**Use Cases:**
- Acceptance evidence proves the manuscript uses one reproducible public package path after cutover and that the displaced legacy path is gone.

**Files:**
- Modify: dependency metadata, integration checker, runtime loader, approval tests, and provenance documentation.

**Interfaces:**
- Consumes: released or immutable split-package sources and the validated adapter.
- Produces: final integration receipt and legacy-path removal proof.

- [ ] **Step 1: Pin** — select released or immutable provider/equilibrium/regression refs and record all identities.
- [ ] **Step 2: RED** — make final-mode validation reject legacy root calls, mutable sources, and missing capability metadata.
- [ ] **Step 3: Cut over** — switch consumers to the validated adapter and delete legacy access without adding a compatibility shim.
- [ ] **Step 4: Verify** — run focused tests, reduced public smoke, and `uv run python scripts/check_epcsaft_integration.py --mode final`; expect PASS and clean curated hashes.
- [ ] **Step 5: Checkpoint commit** — commit as `feat: adopt split epcsaft regression packages`.
