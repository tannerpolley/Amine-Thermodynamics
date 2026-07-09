# Manuscript Submission: assemble final submission readiness gate

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/10
**GitHub Milestone:** Manuscript Submission
**Issue Type:** task
**Source Spec:** none
**Source Plan:** docs/superpowers/plans/starter-milestone-issues.md
**Classification:** HITL
**Labels:** status:hitl, superpowers:issue, type:manuscript
**Goal Command:** HITL claim review required before agent execution.
**Execution Mode:** Ask at runtime
**Worktree Policy:** Native Codex worktree thread first
**Integration Policy:** Worker PR reviewed by main thread
**TDD Policy:** Required
**Parallelization Plan:** None
**Reviewer Role:** Main thread orchestrator
**Script Gate Mode:** Safety only

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/starter-milestone-issues.md#manuscript-submission-readiness-gate
**Intent:** Assemble a submission-readiness gate that ties manuscript text, PDF figures, source logs, and final validation commands together.
**Target Output:** A human reviewer can decide whether the manuscript is ready for submission using a single checklist and explicit claim-review gates.
**Owner:** docs/latex
**Interface:** Submission checklist, source log, figure references, final validation commands, and Overleaf mirror sync path.
**Cutover:** Keep manuscript source in `docs/latex` and add a readiness gate rather than moving manuscript ownership into Superpowers artifacts.
**Replaced Path:** Ad hoc final-readiness checks spread across chat context, roadmaps, and manual inspection.
**Acceptance Proof:** Submission checklist, PDF-figure/reference checks, `uv run python scripts/validate_project.py confidence`, `uv run python scripts/check_epcsaft_integration.py --mode final`, and explicit human claim review.
**Stop Criteria:** Stop before submission until the user reviews scientific claim status and final package integration proof.
**Avoid:** Claiming submission readiness from quick validation alone, bypassing source-log updates, or treating HITL claim review as an AFK task.

## Project Merge

**Merge Owner:** Main thread orchestrator
**Merge Gate:** Native UI approval required
**Merge Policy:** Repo default
**Worktree Cleanup Policy:** Remove owned worktree after merge
**Orchestrator Wakeup Policy:** Worker handoff or bounded heartbeat

## What To Build

Create a submission-readiness gate that links manuscript sections, PDF figure references, source-log evidence, final validation commands, and required human claim review.

## Acceptance Criteria

- [ ] Create or refresh a final submission checklist that links `docs/latex`, figure references, source logs, validation commands, and Overleaf mirror sync.
- [ ] Verify manuscript-ready Matplotlib figures are referenced through PDF artifacts where applicable.
- [ ] Confirm final readiness requires `uv run python scripts/validate_project.py confidence` and `uv run python scripts/check_epcsaft_integration.py --mode final`.
- [ ] Record human review decisions for scientific claim status before submission.

## Blocked by

- https://github.com/tannerpolley/MEA-Thermodynamics/issues/6 for final claim promotion.

## Non-goals

- Do not submit the manuscript.
- Do not claim final scientific readiness from quick validation.
- Do not bypass human review for manuscript claim status.

## Proof Oracle

- Submission checklist file.
- PDF figure/reference check.
- `uv run python scripts/validate_project.py confidence` when final artifacts are ready.
- `uv run python scripts/check_epcsaft_integration.py --mode final` before submission.
- Explicit human claim review.
