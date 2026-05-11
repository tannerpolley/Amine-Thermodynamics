# Refresh ePC-SAFT MEA Submission Workflow

## Objective

Refresh the MEA-Thermodynamics workflow against the latest local ePC-SAFT package changes, rerun the full data-to-regression-to-figures-to-LaTeX manuscript pipeline, fix local friction discovered during verification, and finish with an evidence-backed audit that the scientific data, regression artifacts, and submission-facing manuscript are internally consistent.

## Original Request

After merging the recent MEA submission-artifact changes, reinstall the latest ePC-SAFT version, revisit/rerun/retry all actions, tests, and scripts related to this project, especially friction points, and continue the full manuscript workflow to validate and solidify data, regression, and LaTeX paper building using GoalBuddy, academic researcher, article-writer-latex-submission, and chemical-engineer standards.

## Intake Summary

- Input shape: `specific`
- Audience: user and future MEA/ePC-SAFT manuscript agents
- Authority: `requested`
- Proof type: `test`, `artifact`, `metric`, `review`
- Completion proof: latest ePC-SAFT package is installed into the MEA repo environment; core MEA scripts/tests/regression artifacts/figures/manuscript build have been rerun or explicitly bounded; any local friction is fixed or documented; final audit maps every requirement to concrete command output and artifacts.
- Likely misfire: only running tests or only rebuilding LaTeX while missing package reinstall effects, stale generated artifacts, regression output drift, submission-facing overclaiming, or data/provenance inconsistencies.
- Blind spots considered: upstream package API changes, slow all-row reactive regression, stale local artifacts after reinstall, Zotero-owned bibliography constraints, Overleaf mirror not being source of truth, and manuscript language that could overclaim pressure-optimized parameter readiness.
- Existing plan facts:
  - Root plan exists at `plan.md`.
  - Current merged main includes global regression, train/validation, sensitivity, residual diagnostic, literature comparison, availability, and LaTeX manuscript artifacts.
  - Local project memory says global fit may be `bounded_incomplete` if the all-row reactive objective remains too expensive.
  - Use repo `.venv` Python directly unless the user explicitly asks for `uv run`.
  - `docs/latex` is source of truth; do not manually edit Zotero-owned `references.bib`.

## Goal Kind

`specific`

## Current Tranche

Complete a refresh-and-hardening pass on the current merged `main`: update/reinstall the latest local ePC-SAFT package, collect baseline evidence, rerun and validate package-dependent MEA scripts and tests, refresh artifacts where needed, rebuild the manuscript, fix bounded local friction, and perform a final prompt-to-artifact audit. Continue through safe verified implementation slices until the full refresh outcome is complete.

## Non-Negotiable Constraints

- Work from `C:\Users\Tanner\Documents\git\MEA-Thermodynamics` unless a task explicitly targets `C:\Users\Tanner\Documents\git\ePC-SAFT`.
- Treat `C:\Users\Tanner\Documents\git\ePC-SAFT` as the local upstream package source of truth.
- Use `C:\Users\Tanner\Documents\git\MEA-Thermodynamics\.venv\Scripts\python.exe` for MEA commands unless a Worker proves a different environment is required.
- Do not manually edit `docs/latex/references.bib`.
- Keep submission-facing manuscript text free of Codex, agent, branch, worktree, local-path, artifact-process, and unsupported novelty/readiness claims.
- Do not create repo-local temp/scratch folders.
- Do not treat passing tests as sufficient unless the final audit proves coverage of the actual user outcome.
- Preserve unrelated user changes if the worktree becomes dirty.

## Required Named Skill Standards For `/goal`

- `academic-researcher`: preserve source integrity, do not fabricate citations, and maintain source traceability for scholarly claims.
- `article-writer-latex-submission`: apply submission-safe wording to `docs/latex/main.tex`, `docs/latex/sections/*.tex`, `docs/latex/tables/*.tex`, captions, availability text, and declarations.
- `chemical-engineer`: verify model inputs, units, species maps, bounds, reaction assumptions, and objective definitions before changing solver or regression behavior.

## Stop Rule

Stop only when a final PM/Judge audit proves the refresh outcome is complete.

Do not stop after planning, discovery, or a single successful test if package-dependent scripts or manuscript artifacts remain stale or unaudited.

Do not stop merely because the full pressure/speciation regression is too expensive. If it remains bounded-incomplete, record runtime evidence and ensure manuscript claims stay bounded to workflow/validation scope.

## Canonical Board

Machine truth lives at:

`docs/goals/refresh-epcsaft-mea-submission/state.yaml`

If this charter and `state.yaml` disagree, `state.yaml` wins for task status, active task, receipts, verification freshness, and completion truth.

## Run Command

```text
/goal Follow docs/goals/refresh-epcsaft-mea-submission/goal.md.
```

## PM Loop

On every `/goal` continuation:

1. Read this charter.
2. Read `state.yaml`.
3. Run the GoalBuddy update checker when available.
4. Work only on the active board task.
5. Use Scout/Judge/Worker/PM according to task type.
6. Write compact receipts into `state.yaml`.
7. Activate the next safe task when the previous task is verified.
8. End only with a final audit receipt that maps evidence back to the original user outcome and records `full_outcome_complete: true`.
