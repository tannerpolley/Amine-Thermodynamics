# Phase 3 Regression and Validation Workstream Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Maintain #6 as the Phase 3 parent for split-package adoption, coupled fitting/promotion, and independent validation while preserving explicit upstream and immutable-source gates.

**Architecture:** Three dependency-ordered child issues own distinct proof; #6 aggregates their receipts and no longer duplicates implementation details.

**Tech Stack:** Markdown, Bash, GitHub CLI, Superpowers issue relationships.

## Global Constraints

- Full-model submission requires all three children, upstream reactive-regression admission, and final immutable-source integration proof.
- #3 closes only after its remaining scope is represented.
- No parameter promotion occurs at the parent layer.

## Source Evidence

- Spec: `docs/superpowers/specs/2026-07-13-phase3-regression-validation-workstream-design.md`.
- Current evidence: global regression `success=false`, `nfev=0`.

## Outcome Proof

**Intent:** Separate Phase 3 architecture, fitting, and validation ownership.
**Current Behavior:** #3 has been superseded and #6 has three children, but its closeout contract still assumes the legacy monolithic regression surface while no promoted coupled fit exists.
**Expected Outcome:** #6 has three ordered children whose closeout receipts prove public upstream admission, fit/promotion, and independent validation.
**Target Output:** Updated #6 mirror/body, three child links, upstream receipt, and final integration receipt.
**Owner:** Phase 3 maintainer.
**Interface:** GitHub #6, its local mirror, and child closeout receipts.
**Cutover:** Preserve the established three-child graph while replacing the legacy contract gate with upstream admission and immutable split-package proof.
**Replaced Path:** Retire #3 as an active work queue while preserving its historical discussion.
**Evidence:** Mirror validators, GitHub readback, and structured dependency checks.
**Acceptance Proof:** #6 has exactly three intended children in order; the upstream capability is admitted; final package sources are immutable; every child closes with proof.
**Stop Criteria:** Stop if upstream admission is absent, any child is missing, dependency direction is wrong, or final source state is mutable.
**Avoid:** Do not close #6 or claim fitting progress from scaffolding.
**Risk:** Cross-repo blockers may delay child 1; preserve the stable lane and record them without widening parent scope.

## Implementation Boundaries

**Files To Create:** None at the parent layer.
**Files To Modify:** `docs/superpowers/issues/6-native-regression-validation-workstream.md`, its source spec/plan, and milestone linkage if child URLs change.
**Files To Avoid:** Scientific code/results during tracker alignment.
**Source Of Truth:** Three validated child mirrors and their plans.
**Read Path:** Child contracts and current GitHub bodies to parent mirror.
**Write Path:** Validated mirror to #6, child relationships, and #3 closure comment.
**Integration Points:** GitHub issues/relationships and issue-mirror validator.
**Migration Or Cutover:** Keep the three children and hierarchy, revise their gates, link the upstream blocker, and verify live read-back.
**Replaced Path Handling:** Preserve closed #3 history; do not reopen its overlapping queue.
**Acceptance Proof Gate:** Fresh GitHub JSON must reproduce the local hierarchy.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Hierarchy | Approved spec | #6 parent with three ordered children. | Removes overlap. | No | Phase 3 maintainer |

## Test Complete and Metrics

- Three child mirrors validate.
- #6 live hierarchy matches local graph.
- #3 is closed only after transfer comment resolves.
- Upstream capability and final immutable-source receipts are linked before #6 closes.

### Task 1: Revise and verify the Phase 3 graph

**Use Cases:**
- Reviewers see acceptance evidence, migration, and the displaced duplicate path.

**Files:**
- Modify: #6/#12/#13/#14 mirrors and their source specs/plans; update milestone linkage only if URLs change.

**Interfaces:**
- Consumes: three child issue URLs.
- Produces: verified #6 hierarchy and #3 supersession receipt.

- [ ] **Step 1: Audit** — compare current upstream capability and package architecture with every child gate.
- [ ] **Step 2: Revise** — update mirrors/specs/plans and publish the generic upstream blocker without changing the three-child hierarchy.
- [ ] **Step 3: Verify** — validate mirrors/plans and read back titles, labels, milestone, bodies, blockers, and exact child set.
- [ ] **Step 4: Checkpoint commit** — commit as `docs: align phase 3 with upstream architecture`.
