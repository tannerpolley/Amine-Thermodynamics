# Phase 2 Model Comparison Workstream Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert GitHub issue #5 into an evidence-backed Phase 2 parent whose only remaining child is controlled model comparison and metric integrity.

**Architecture:** Preserve completed Phase 2 implementation evidence, replace the stale checklist with a parent closeout contract, and use GitHub parent/blocked-by relationships for the remaining child.

**Tech Stack:** Markdown, Bash, GitHub CLI, Superpowers issue-mirror validators.

## Global Constraints

- Preserve the verified 161 pressure and 74 speciation solve evidence.
- Do not place Phase 3 or manuscript-package work under #5.
- Validate the local mirror before GitHub mutation and verify the live relationship afterward.

## Source Evidence

- Spec: `docs/superpowers/specs/2026-07-13-phase2-model-comparison-workstream-design.md`
- Receipt: `.superpowers/runs/2026-07-09-mea-project-audit/final-verification.json`
- Live parent: GitHub issue #5.

## Outcome Proof

**Intent:** Preserve Phase 2 history while making the remaining completion boundary accurate.
**Current Behavior:** #5 contains a broad historical checklist even though the fixed-parameter workflow is substantially complete.
**Expected Outcome:** #5 is a workstream parent blocked only by the controlled-comparison child.
**Target Output:** Updated #5 body, local mirror, labels, milestone, child relationship, and verification receipt.
**Owner:** Phase 2 maintainer.
**Interface:** `docs/superpowers/issues/5-phase-2-activity-epcsaft-workstream.md` and GitHub issue #5.
**Cutover:** Replace stale implementation checkboxes with completed evidence and remaining child proof.
**Replaced Path:** Retire the old mega-checklist as active project state while preserving it in GitHub history.
**Evidence:** Mirror validator output, GitHub JSON readback, and July 9 row-count receipt.
**Acceptance Proof:** GitHub shows #5 in the Phase 2 milestone with `kind:workstream`, `priority:submission-blocker`, and exactly the intended child.
**Stop Criteria:** Stop if evidence counts conflict, the child is absent, or relationship mutation fails.
**Avoid:** Do not close #5 before its child proof passes or rewrite scientific results in the tracker.
**Risk:** A parent can appear unfinished without context; the new body must separate completed infrastructure from remaining proof.

## Implementation Boundaries

**Files To Create:** `docs/superpowers/issues/5-phase-2-activity-epcsaft-workstream.md`.
**Files To Modify:** `docs/superpowers/milestones/phase-2-activity-epcsaft.md`.
**Files To Avoid:** Scientific result tables, LaTeX, and Phase 3 artifacts.
**Source Of Truth:** July 9 verification receipt plus the controlled-comparison child mirror.
**Read Path:** Verification receipt and child mirror to parent issue body.
**Write Path:** Validated local mirror to GitHub issue #5 and milestone index.
**Integration Points:** Issue-mirror validator, `gh issue edit`, and parent/blocked-by API.
**Migration Or Cutover:** Publish the child first, then rewrite #5 and link it.
**Replaced Path Handling:** Preserve historical comments; remove stale active checklist text instead of adding compatibility prose.
**Acceptance Proof Gate:** Live readback must match the mirror before the task closes.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Parent role | Approved spec | Keep #5 as Phase 2 workstream parent. | Retains phase history without stale scope. | No | Phase 2 maintainer |

## Test Complete and Metrics

- Mirror validator passes.
- GitHub readback shows one intended child and no unrelated children.
- #5 body records 161/161 pressure and 74/74 speciation solves.

### Task 1: Cut over #5 to the workstream contract

**Use Cases:**
- A reviewer sees acceptance evidence and the displaced old path instead of stale unchecked work.
- The child relationship makes remaining proof visible and the cutover auditable.

**Files:**
- Create: `docs/superpowers/issues/5-phase-2-activity-epcsaft-workstream.md`
- Modify: `docs/superpowers/milestones/phase-2-activity-epcsaft.md`

**Interfaces:**
- Consumes: controlled-comparison child URL and July 9 receipt.
- Produces: validated parent mirror and live relationship.

- [ ] **Step 1: RED** — run the issue-mirror validator before the mirror exists; expect a missing-file failure.
- [ ] **Step 2: GREEN** — create the mirror with completed evidence, source spec/plan, labels, milestone, and child dependency.
- [ ] **Step 3: Verify** — run `bash "$SUPERPOWERS_PROJECT_PLUGIN_ROOT/skills/create-issues/scripts/validate-issue-mirror.sh" -RepoRoot . -IssuePath docs/superpowers/issues/5-phase-2-activity-epcsaft-workstream.md`; expect PASS.
- [ ] **Step 4: Publish and read back** — edit #5 and verify structured GitHub fields match the mirror.
- [ ] **Step 5: Checkpoint commit** — `git add docs/superpowers/issues/5-phase-2-activity-epcsaft-workstream.md docs/superpowers/milestones/phase-2-activity-epcsaft.md && git commit -m "docs: align phase 2 workstream"`.
