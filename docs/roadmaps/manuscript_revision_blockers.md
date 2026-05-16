# Manuscript Revision Blockers

Date: 2026-05-15 local

This file records unresolved evidence gates for the Major Revision pass controlled by `docs/roadmaps/codex_mea_revision_grounding_gate.md`.

## Blocked Evidence Gates

- Required roadmap files were not found at the requested paths or by exact filename search:
  `docs/roadmaps/manuscript_artifact_plan.md`,
  `docs/roadmaps/manuscript_structure_and_figures.md`,
  `docs/roadmaps/mea_manuscript_phase_plan.md`, and
  `docs/roadmaps/submission_readiness_pr_summary.md`.
- Publication-ready figure status is not verified. `data/reference/MEA/manifests/figure_artifact_manifest.csv` currently groups as 7 `diagnostic_only`, 7 `not_started`, and 1 `blocked_until_phase3_fit`; `data/reference/MEA/manifests/figure_artifact_file_manifest.csv` currently lists 37 existing files as `diagnostic_only`.
- No completed Phase 3/global-regression artifact is verified. `data/reference/MEA/manifests/regression_artifact_manifest.csv` lists Phase 3 artifacts as `planned` or `blocked_by_package_runtime`; `analyses/epcsaft_ionic_regression/results/global_regression/global_regression_summary.json` reports `completion_status: package_fit_not_completed` and `attempted_optimization: false`.
- No archive DOI is verified. The manuscript now states that no archival DOI has been minted.
- No release tag is verified. `git tag --list` returned no tags during this revision pass.
- Submission-facing condition ranges are not verified from the required roadmap set because the roadmap files listed above are missing. The manuscript therefore avoids adding new numeric temperature, loading, pressure, or composition ranges beyond existing record counts and residual values.
- Full source-by-source residual tables for the final manuscript evidence set were not verified. A train/validation pressure-by-source file exists, but a complete pressure-plus-speciation source-by-source residual table was not found in this pass.

## Resolved Evidence Gates

- Residual threshold evidence exists in `analyses/phase2_activity_epcsaft/results/phase2_residual_acceptance_audit.csv` and `analyses/phase1_smith_missen_baseline/results/phase1_residual_acceptance_audit.csv`; the revised manuscript still removes undefined "accepted" terminology and reports neutral residual language.
- The repository URL is verified from `git remote -v` as `https://github.com/tannerpolley/MEA-Thermodynamics.git`.
