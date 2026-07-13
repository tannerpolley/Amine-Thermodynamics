# Final Submission Readiness Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite #10 as an independent cross-workstream proof gate and record the final human submit/hold decision only after all evidence passes.

**Architecture:** A readiness matrix consumes three parent closeout receipts plus final repository/manuscript proofs; failures route back to owners and cannot be overridden by a generic approval.

**Tech Stack:** Python/JSON or Markdown readiness receipt, Bash, GitHub CLI, LaTeX, PDF inspection.

## Global Constraints

- #10 owns no unrelated children.
- Scientific failures cannot be overridden by HITL approval.
- Final proof runs from clean pinned state.

## Source Evidence

- Spec: `docs/superpowers/specs/2026-07-13-final-submission-readiness-gate-design.md`.
- Live gate: GitHub issue #10.

## Outcome Proof

**Intent:** Provide one honest final decision surface without centralizing implementation ownership.
**Current Behavior:** #10 is a broad checklist with incomplete blocker coverage.
**Expected Outcome:** #10 is blocked by workstream parents and aggregates their receipts plus final clean proof.
**Target Output:** Updated #10 mirror/body, blocked-by links, readiness matrix, final verification receipt, and human decision.
**Owner:** Project maintainer and corresponding author.
**Interface:** #10, its local mirror, and final readiness receipt.
**Cutover:** Replace broad task ownership with evidence aggregation.
**Replaced Path:** Retire tests-only and mega-parent readiness semantics.
**Evidence:** Parent receipts, confidence/final integration, deterministic PDF, visual review, metadata/archive checks, clean state.
**Acceptance Proof:** Every matrix lane passes and the author explicitly selects submit or hold after reviewing final artifacts.
**Stop Criteria:** Any failed/stale/missing receipt keeps #10 blocked and routes to its owner.
**Avoid:** No submission action, implicit approval, or readiness claim from quick validation alone.
**Risk:** External venue review may add requirements after this venue-neutral gate.

## Implementation Boundaries

**Files To Create:** Final readiness matrix/receipt and refreshed #10 mirror.
**Files To Modify:** Manuscript milestone index and final-check scripts/tests as needed.
**Files To Avoid:** Upstream workstream implementations and external submission portal.
**Source Of Truth:** Verified parent closeout receipts and final clean-checkout commands.
**Read Path:** Workstream receipts and repository state to readiness matrix.
**Write Path:** Matrix to #10 status and human decision record.
**Integration Points:** confidence validation, final integration, manuscript build/freshness, cleanup, GitHub blocked-by links.
**Migration Or Cutover:** Link parent blockers, narrow #10 body, then execute final gate only after parent closure.
**Replaced Path Handling:** Remove duplicate child task lists and preserve links to workstream evidence.
**Acceptance Proof Gate:** Machine lanes pass before native human submit/hold gate is shown.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Gate role | Approved spec | Evidence aggregator only. | Preserves distributed ownership. | No | project maintainer |
| Final decision | Publication authority | Explicit submit/hold after proof. | Keeps author control. | Yes | corresponding author |

## Test Complete and Metrics

- #10 has no children and exactly three workstream blockers.
- Confidence validation, final integration, deterministic PDF/freshness, visual, metadata/archive, and cleanup lanes pass.
- Final decision is timestamped and evidence-linked.

### Task 1: Cut #10 over to the readiness matrix

**Use Cases:**
- Reviewers see target-perspective proof and migration away from the mega-parent old path.

**Files:**
- Create: final readiness receipt and refreshed #10 mirror.
- Modify: manuscript milestone index and final gate tests.

**Interfaces:**
- Consumes: three parent receipts and final proof commands.
- Produces: readiness matrix and GitHub gate state.

- [ ] **Step 1: RED** — add tests/validator fixture requiring all lanes and exact blocker relationships; expect current #10 to fail.
- [ ] **Step 2: GREEN** — implement matrix generation and rewrite the mirror/body.
- [ ] **Step 3: Link/read back** — add the three blocked-by relationships and verify #10 has no children.
- [ ] **Step 4: Verify** — run all final commands, inspect PDF/metadata/archive, and record exact outputs.
- [ ] **Step 5: HITL** — show final artifact review and request explicit submit/hold decision.
- [ ] **Step 6: Checkpoint commit** — commit as `docs: establish final submission readiness gate`.

