# Phase 3 Regression and Validation Workstream Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert #6 into the Phase 3 parent for contract completion, coupled fitting/promotion, and independent validation while closing overlapping #3 as superseded.

**Architecture:** Three dependency-ordered child issues own distinct proof; #6 aggregates their receipts and no longer duplicates implementation details.

**Tech Stack:** Markdown, Bash, GitHub CLI, Superpowers issue relationships.

## Global Constraints

- Full-model submission requires all three children.
- #3 closes only after its remaining scope is represented.
- No parameter promotion occurs at the parent layer.

## Source Evidence

- Spec: `docs/superpowers/specs/2026-07-13-phase3-regression-validation-workstream-design.md`.
- Current evidence: global regression `success=false`, `nfev=0`.

## Outcome Proof

**Intent:** Separate Phase 3 architecture, fitting, and validation ownership.
**Current Behavior:** #3 and #6 overlap while no promoted coupled fit exists.
**Expected Outcome:** #6 has three ordered children and #3 closes with a precise supersession link.
**Target Output:** Updated #6 mirror/body, three child links, dependency graph, #3 closure receipt.
**Owner:** Phase 3 maintainer.
**Interface:** GitHub #6, its local mirror, and child closeout receipts.
**Cutover:** Replace duplicate #3/#6 active scope with one parent graph.
**Replaced Path:** Retire #3 as an active work queue while preserving its historical discussion.
**Evidence:** Mirror validators, GitHub readback, and structured dependency checks.
**Acceptance Proof:** #6 has exactly three intended children in order and #3 links to the native-contract child before closure.
**Stop Criteria:** Stop if any child is missing, dependency direction is wrong, or #3 transfer is incomplete.
**Avoid:** Do not close #6 or claim fitting progress from scaffolding.
**Risk:** Cross-repo blockers may delay child 1; record them without widening parent scope.

## Implementation Boundaries

**Files To Create:** `docs/superpowers/issues/6-phase-3-regression-validation-workstream.md`.
**Files To Modify:** `docs/superpowers/milestones/phase-3-ionic-regression.md`.
**Files To Avoid:** Scientific code/results during tracker alignment.
**Source Of Truth:** Three validated child mirrors and their plans.
**Read Path:** Child contracts and current GitHub bodies to parent mirror.
**Write Path:** Validated mirror to #6, child relationships, and #3 closure comment.
**Integration Points:** GitHub issues/relationships and issue-mirror validator.
**Migration Or Cutover:** Create children, link dependencies, update #6, then close #3.
**Replaced Path Handling:** Preserve #3 history and add an explicit supersession pointer.
**Acceptance Proof Gate:** Fresh GitHub JSON must reproduce the local hierarchy.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Hierarchy | Approved spec | #6 parent with three ordered children. | Removes overlap. | No | Phase 3 maintainer |

## Test Complete and Metrics

- Three child mirrors validate.
- #6 live hierarchy matches local graph.
- #3 is closed only after transfer comment resolves.

### Task 1: Publish and verify the Phase 3 graph

**Use Cases:**
- Reviewers see acceptance evidence, migration, and the displaced duplicate path.

**Files:**
- Create: `docs/superpowers/issues/6-phase-3-regression-validation-workstream.md`
- Modify: `docs/superpowers/milestones/phase-3-ionic-regression.md`

**Interfaces:**
- Consumes: three child issue URLs.
- Produces: verified #6 hierarchy and #3 supersession receipt.

- [ ] **Step 1: RED** — validate the absent parent mirror; expect failure.
- [ ] **Step 2: GREEN** — create/update mirror and milestone links.
- [ ] **Step 3: Verify** — run mirror validation; expect PASS.
- [ ] **Step 4: Publish** — link children/dependencies, update #6, comment and close #3, then read back all states.
- [ ] **Step 5: Checkpoint commit** — commit as `docs: align phase 3 workstream`.

