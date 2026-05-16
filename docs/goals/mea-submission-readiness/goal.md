# MEA-Thermodynamics Submission Readiness

## Objective

Turn the newly ingested MEA roadmap package into a PR-ready repository tranche that advances repo-owned data, provenance, manuscript, roadmap, manifest, and handoff work without requiring a working upstream ePC-SAFT dev build.

## Original Request

Prepare a GoalBuddy board for MEA-Thermodynamics submission-readiness while the upstream ePC-SAFT package build is unavailable.

## Intake Summary

- Input shape: `existing_plan`
- Audience: Tanner and future Codex GoalBuddy agents preparing a PR-ready MEA-Thermodynamics tranche.
- Authority: `requested`
- Proof type: `artifact`
- Completion proof: `state.yaml` is valid; roadmaps/manifests are internally consistent; no final manuscript or roadmap claim says Phase 3/global regression is complete; extracted data, if any, are traceable to repo-local Markdown with source/status metadata; package-dependent blockers are documented as generic ePC-SAFT dependencies; cleanup hook has run.
- Likely misfire: GoalBuddy could spend the run rediscovering the whole MEA/ePC-SAFT project or trying to fix/run the unavailable package build instead of advancing safe repo-owned submission-readiness work.
- Blind spots considered: ePC-SAFT-dependent Phase 2/3 execution may be blocked by the missing dev worktree; public web data search is not approved for source-pending MEA datasets; manuscript/roadmap overclaims and local path leakage may be more important than new computation.
- Existing plan facts: preserve the strict manuscript structure, 15-figure plan, Phase 1/2/3 staging, repo-local extraction from `docs/papers/md`, no fabricated data, no full article text in roadmaps, no MEA-specific public APIs in ePC-SAFT, and bounded PR-ready changes.

## Goal Kind

`existing_plan`

## Current Tranche

This tranche should complete successive safe local slices that do not require a working ePC-SAFT dev build: audit the roadmap/package ingest, make source/data manifests extraction-ready, extract only clear repo-local Markdown tables into small machine-readable datasets, audit manuscript and roadmap claims, map figures to the 15-figure plan, document the package dependency gap and rerun commands, and leave a PR-ready summary.

Phase 2/3 package-dependent validation, global regression execution, or final acceptance must remain gated until the upstream ePC-SAFT dev worktree/build is available and the repo passes the documented rerun commands.

## Non-Negotiable Constraints

- Do not fabricate data.
- Do not paste full article text into roadmap files.
- Use repo-local paper Markdown under `docs/papers/md` for extraction.
- Do not web search for source-pending MEA pH/electrochemical or direct MEAH+/carbamate osmotic-activity data unless Tanner approves.
- Do not request MEA-specific public APIs in `epcsaft`.
- Preserve the strict manuscript structure, 15-figure plan, and Phase 1/2/3 staging.
- Keep MEA-specific data curation, figures, manifests, and interpretation in MEA-Thermodynamics.
- Put only generic solver/regression/API blockers into ePC-SAFT.
- Keep changes PR-ready and bounded.
- Treat current Phase 3 as not accepted: `global_regression_summary.json` reports `package_fit_not_completed`, `attempted_optimization=false`, and `selected_parameter_set=promoted_ionic_fit`.
- Gate package-dependent Phase 2/3 work behind the missing ePC-SAFT dev worktree/build readiness.

## Stop Rule

Stop only when a final audit proves the full original outcome for this tranche is complete.

Do not stop after planning, discovery, or Judge selection if a safe Worker task can be activated.

Do not stop after a single verified Worker slice when the broader owner outcome still has safe local follow-up slices. After each slice audit, advance the board to the next highest-leverage safe Worker task and continue.

Do not stop because the ePC-SAFT dev worktree/build is missing. Mark the exact package-dependent task blocked with a receipt, document exact rerun commands, and continue all repo-owned local work that does not require package execution.

## Canonical Board

Machine truth lives at:

`docs/goals/mea-submission-readiness/state.yaml`

If this charter and `state.yaml` disagree, `state.yaml` wins for task status, active task, receipts, verification freshness, and completion truth.

## Run Command

```text
/goal Follow docs/goals/mea-submission-readiness/goal.md.
```

## PM Loop

On every `/goal` continuation:

1. Read this charter.
2. Read `state.yaml`.
3. Run the bundled GoalBuddy update checker when available and mention a newer version without blocking.
4. Re-check the intake: original request, input shape, authority, proof, blind spots, existing plan facts, and likely misfire.
5. Work only on the active board task.
6. Assign Scout, Judge, Worker, or PM according to the task.
7. Write a compact task receipt.
8. Update the board.
9. If Judge selected a safe Worker task with `allowed_files`, `verify`, and `stop_if`, activate it and continue unless blocked.
10. Treat package-dependent blockers as generic ePC-SAFT dependency gaps and keep safe repo-local work moving.
11. Treat a slice audit as a checkpoint, not completion, unless it explicitly proves the full original outcome is complete.
12. Finish only with a Judge/PM audit receipt that maps receipts and verification back to the original user outcome and records `full_outcome_complete: true`.

Issue and PR handoffs are supporting artifacts. `state.yaml` remains authoritative, and every external artifact decision must be recorded in a task receipt.
