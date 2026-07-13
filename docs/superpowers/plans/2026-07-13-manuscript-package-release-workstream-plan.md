# Manuscript Package and Release Workstream Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a Manuscript Package and Release parent with separate methods, metadata/archive, and figures/editorial children.

**Architecture:** The parent owns package integration; children own their proof and use cross-workstream blocked-by links without becoming children of #10.

**Tech Stack:** Markdown, GitHub CLI, Bash, Superpowers issue mirrors.

## Global Constraints

- Keep Phase 2/3 work in their milestones.
- #10 remains a final gate, not this parent.
- Author/legal/archive mutations remain HITL.

## Source Evidence

- Spec: `docs/superpowers/specs/2026-07-13-manuscript-package-release-workstream-design.md`.

## Outcome Proof

**Intent:** Give manuscript/release deliverables one coherent owner without creating a submission mega-issue.
**Current Behavior:** Methods, metadata, figures, and readiness are mixed in broad #10 scope.
**Expected Outcome:** A separate parent owns three children and closes only after their receipts integrate.
**Target Output:** New parent issue/mirror, three child relationships, cross-workstream blockers, and milestone update.
**Owner:** Manuscript maintainer.
**Interface:** New parent mirror plus `docs/superpowers/milestones/manuscript-submission.md`.
**Cutover:** Move implementation scope out of #10 into this workstream.
**Replaced Path:** Retire #10's active ownership of methods, metadata, and editorial tasks.
**Evidence:** Validated mirrors, GitHub structured readback, and dependency graph.
**Acceptance Proof:** Parent has exactly three intended children; #10 links through blocked-by only.
**Stop Criteria:** Stop on missing child, wrong parentage, or unresolved relationship mutation.
**Avoid:** Do not place Phase 2/3 scientific children under this parent.
**Risk:** Cross-workstream dependencies can be misread; encode them explicitly.

## Implementation Boundaries

**Files To Create:** New manuscript-package parent mirror.
**Files To Modify:** Manuscript milestone index and #10 mirror.
**Files To Avoid:** Scientific implementation and external archive state.
**Source Of Truth:** Validated child mirrors and approved distributed taxonomy.
**Read Path:** Child contracts to parent body/dependency graph.
**Write Path:** Local mirror to GitHub parent, children, and milestone.
**Integration Points:** `gh issue create/edit`, parent/blocked-by API, issue-mirror validator.
**Migration Or Cutover:** Create parent and children, link, then narrow #10.
**Replaced Path Handling:** Preserve #10 history but remove active duplicate task lists.
**Acceptance Proof Gate:** Fresh GitHub JSON matches local mirrors and graph.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Parent placement | User-approved hierarchy | Separate Manuscript Submission workstream. | Distributes ownership. | No | manuscript maintainer |

## Test Complete and Metrics

- Four new mirrors validate.
- Parent has three children and required blockers.
- #10 has no unrelated children.

### Task 1: Publish the manuscript-package hierarchy

**Use Cases:**
- Acceptance evidence and migration away from #10's old path are visible.

**Files:**
- Create: manuscript-package parent mirror
- Modify: `docs/superpowers/milestones/manuscript-submission.md`

**Interfaces:**
- Consumes: three child URLs and cross-workstream dependencies.
- Produces: verified parent graph.

- [ ] **Step 1: RED** — validate the absent parent mirror; expect failure.
- [ ] **Step 2: GREEN** — create the parent mirror and milestone entries.
- [ ] **Step 3: Verify** — validate all four mirrors; expect PASS.
- [ ] **Step 4: Publish/read back** — create/link the hierarchy and verify structured state.
- [ ] **Step 5: Checkpoint commit** — commit as `docs: add manuscript package workstream`.

