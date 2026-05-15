# Submission-Readiness PR Summary

## Scope

This tranche advances MEA-Thermodynamics submission readiness without requiring a working upstream ePC-SAFT dev build. It is limited to repo-owned manifests, provenance, extraction staging, roadmap consistency, and dependency-gate documentation.

## Files changed

### Manifests and schemas

- `data/reference/MEA/manifests/source_status_manifest.csv`
- `data/reference/MEA/manifests/extraction_target_manifest.csv`
- `data/reference/MEA/manifests/figure_artifact_manifest.csv`
- `data/reference/MEA/manifests/figure_artifact_file_manifest.csv`
- `data/reference/MEA/manifests/regression_artifact_manifest.csv`
- `data/reference/MEA/ChEq/Wong_2015_Raman_speciation_schema.csv`
- `data/reference/MEA/ChEq/Wong_2015_Raman_metadata_schema.csv`
- `data/reference/MEA/density_viscosity/Amundsen_2009_density_viscosity_schema.csv`
- `data/reference/MEA/dielectric/MEA_H2O_dielectric_schema.csv`

### Extracted or staged source data

- `data/reference/MEA/density_viscosity/Amundsen_2009_density_viscosity.csv`
- `data/reference/MEA/density_viscosity/Amundsen_2009_correlation_metadata.csv`
- `data/reference/MEA/ChEq/Wong_2015_Raman_metadata.csv`

### Roadmaps and handoff docs

- `docs/roadmaps/manuscript_artifact_plan.md`
- `docs/roadmaps/epcsaft_dependency_matrix.md`
- `docs/roadmaps/phase_acceptance_gates.md`
- `docs/roadmaps/reproducibility_dependency_note.md`
- `docs/roadmaps/submission_readiness_pr_summary.md`

### GoalBuddy control files

- `docs/goals/mea-submission-readiness/goal.md`
- `docs/goals/mea-submission-readiness/state.yaml`
- `docs/goals/mea-submission-readiness/notes/T001-scout-map.md`
- `docs/goals/mea-submission-readiness/.goalbuddy-board/`

## Data/provenance status

- Wong 2015: repo-local Markdown exists; metadata was staged in `Wong_2015_Raman_metadata.csv`. Numeric Raman speciation remains `staged_figure_digitization_required` because the inspected source region is figure/caption based rather than a clear numeric table.
- Amundsen 2009: 70 unloaded MEA-water density/viscosity rows were extracted from clear repo-local Markdown tables with source-line metadata. Loaded density/viscosity tables remain for a later table-specific extraction pass.
- MEA-H2O dielectric: schema exists, but data remain `source_lead_only`; do not promote MEA `f_solv` without repo-local table/correlation evidence or user-approved source.
- Loaded-MEA pH/electrochemical and direct MEAH+/carbamate ionic-activity data remain `source_pending`; no public web search was performed.

## Figure and manuscript status

- The 15-figure plan is preserved.
- Figures F08-F14 have a file-level diagnostic manifest with 37 existing CSV/PNG/SVG/sidecar paths and zero missing files.
- Current figure artifacts are marked `diagnostic_only`, not publication-ready.
- Roadmaps continue to state that Phase 3/global regression is not complete.
- Manuscript source sections were checked for local Windows/Codex/worktree leakage and Phase 3 acceptance overclaims; matches are limited to roadmap dependency notes or explicit blocked-status language.

## ePC-SAFT package blocker

The configured dev dependency path is missing:

```powershell
Test-Path C:\Users\Tanner\.codex\worktrees\epcsaft-dev\ePC-SAFT
# False
```

`pyproject.toml` and `uv.lock` both point `epcsaft` at that worktree-backed path. Package-dependent Phase 2/3 work stays blocked until the dev worktree is restored or `epcsaft` is repinned.

This tranche does not request MEA-specific public APIs from `epcsaft`. Package-side blockers are generic ePC-SAFT solver/regression/readiness dependencies.

## Rerun commands after ePC-SAFT is available

Run from the repository root:

```powershell
Test-Path C:\Users\Tanner\.codex\worktrees\epcsaft-dev\ePC-SAFT
uv sync
uv run python scripts/check_epcsaft_integration.py --mode dev --self-only
uv run python scripts/check_epcsaft_integration.py --mode dev
uv run python scripts/check_epcsaft_integration.py --mode final
```

Only after those pass should a later GoalBuddy run attempt package-dependent Phase 2/3 figure regeneration, coupled pressure/speciation validation, or final manuscript/archive acceptance checks.

## Validation run in this tranche

- GoalBuddy state checker passed after each board transition.
- CSV parse checks passed for source, extraction, regression, figure, and schema manifests.
- Figure file manifest check found 37 listed diagnostic files and 0 missing paths.
- Claim/path audit found no manuscript-section local path leakage or Phase 3 acceptance claim.
- Cleanup hook was run before completion.

## Validation intentionally skipped

- ePC-SAFT integration and package-dependent validation were skipped because the configured dev worktree path is missing.
- No web search was performed for source-pending pH/electrochemical or direct ionic-activity data.
