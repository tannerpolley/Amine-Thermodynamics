# Starter Milestone Issues Plan

## Purpose

Seed the empty Superpowers Project milestones with narrow tracker work that can be executed later without blurring issue scope.

## Source Context

- Project context: `docs/superpowers/PROJECT_CONTEXT.md`
- Paper-validation milestone page: `docs/superpowers/milestones/paper-validation.md`
- Manuscript-submission milestone page: `docs/superpowers/milestones/manuscript-submission.md`
- Canonical paper-validation analysis root: `analyses/paper_validation/2015_baygi`
- Canonical manuscript root: `docs/latex`

## Paper Validation Baygi 2015 Acceptance Gate

### Outcome Proof

**Intent:** Lock a repeatable acceptance gate for the Baygi 2015 recreation artifacts before later manuscript work depends on them.

**Target Output:** A reviewer can inspect the Baygi validation root and see which artifacts prove paper recreation, which plot bundle files exist, and which validation command protects them.

**Owner:** `analyses/paper_validation/2015_baygi`

**Interface:** Analysis README, generated artifact files, validation checks, and milestone links.

**Cutover:** Keep the current analysis root and tighten its acceptance documentation and validation coverage.

**Replaced Path:** Informal paper-validation confidence based on manually inspecting generated files.

**Acceptance Proof:** Baygi artifact checks plus `uv run python scripts/validate_project.py quick`.

**Stop Criteria:** Stop when the Baygi artifact gate is explicit, quick validation passes, and no manuscript-facing claim relies on an unstated paper-recreation assumption.

**Avoid:** Creating a second Baygi validation root, treating screenshots as source artifacts, or moving paper-validation work under milestone-owned folders.

## Manuscript Submission Readiness Gate

### Outcome Proof

**Intent:** Assemble a submission-readiness gate that ties manuscript text, PDF figures, source logs, and final validation commands together.

**Target Output:** A human reviewer can decide whether the manuscript is ready for submission using a single checklist and explicit claim-review gates.

**Owner:** `docs/latex`

**Interface:** Submission checklist, source log, figure references, final validation commands, and Overleaf mirror sync path.

**Cutover:** Keep manuscript source in `docs/latex` and add a readiness gate rather than moving manuscript ownership into Superpowers artifacts.

**Replaced Path:** Ad hoc final-readiness checks spread across chat context, roadmaps, and manual inspection.

**Acceptance Proof:** Submission checklist, PDF-figure/reference checks, `uv run python scripts/validate_project.py confidence`, `uv run python scripts/check_epcsaft_integration.py --mode final`, and explicit human claim review.

**Stop Criteria:** Stop before submission until the user reviews scientific claim status and final package integration proof.

**Avoid:** Claiming submission readiness from quick validation alone, bypassing source-log updates, or treating HITL claim review as an AFK task.
