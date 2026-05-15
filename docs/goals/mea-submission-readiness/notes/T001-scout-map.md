# T001 Scout Map

## Result

Read-only Scout pass completed on 2026-05-13.

## File and Artifact Map

- Roadmap overlay exists under `docs/roadmaps/` with key files including `manuscript_artifact_plan.md`, `manuscript_structure_and_figures.md`, `mea_data_curation_plan.md`, `mea_manuscript_phase_plan.md`, `phase_acceptance_gates.md`, `epcsaft_dependency_matrix.md`, and `reproducibility_dependency_note.md`.
- Prompt overlay exists under `docs/prompts/MEA_ePCSAFT/` with `CODEX_BOOTSTRAP_PROMPT.md`, `FIRST_SIX_EXECUTION_STEPS.md`, `INGEST_ZIP_AND_EXECUTE.md`, and `WEB_SOURCE_SEARCH_PROMPT_AFTER_APPROVAL.md`.
- Source and artifact manifests exist under `data/reference/MEA/manifests/`: `source_status_manifest.csv`, `figure_artifact_manifest.csv`, `regression_artifact_manifest.csv`, and `parameter_provenance_manifest.csv`.
- Repo-local paper Markdown exists for Wong 2015 and Amundsen 2009:
  - `docs/papers/md/Wong et al. - 2015 - Chemical speciation of CO2 absorption in aqueous monoethanolamine investigated by in situ Raman spec.md`
  - `docs/papers/md/Amundsen et al. - 2009 - Density and viscosity of monoethanolamine + water + carbon dioxide from (25 to 80) °C.md`
  - `docs/papers/md/Amundsen and Dag - 2009 - APPENDIX A  PARAMETER CORRELATIONS.md`
- Current global regression artifact is `analyses/epcsaft_ionic_regression/results/global_regression/global_regression_summary.json`.

## Package-Independent Work That Can Proceed

- Manifest consistency checks and targeted manifest improvements.
- Extraction schemas and status metadata for Wong 2015, Amundsen 2009, MEA-H2O dielectric, pH, and ionic-activity placeholders.
- Small machine-readable extraction from repo-local Markdown where tables are unambiguous.
- Manuscript and roadmap claim audit for Phase 3/global-regression overclaims and local path leakage.
- Mapping existing diagnostic figure artifacts to the 15-figure plan.
- Documentation of the package dependency gap and rerun commands.

## Package-Dependent Blockers

- `uv.lock` points `epcsaft` at `C:/Users/Tanner/.codex/worktrees/epcsaft-dev/ePC-SAFT`.
- That path is missing in the current environment.
- Phase 2/3 package execution and final-mode package validation should remain blocked until the worktree/build is restored.
- `global_regression_summary.json` reports `completion_status=package_fit_not_completed`, `attempted_optimization=false`, and `selected_parameter_set=promoted_ionic_fit`.

## Extraction Observations

- Wong 2015 Markdown appears to contain narrative, equations, and figure captions rather than obvious pipe-delimited Markdown tables. Extraction should start as staged metadata/provenance unless a later narrow pass identifies unambiguous numeric blocks.
- Amundsen 2009 Markdown contains multiple table captions for density and viscosity tables. It appears more extraction-ready than Wong 2015, but numeric table structure still needs a careful table-specific pass.
- The Amundsen/Dag appendix includes correlation-source table material and may be useful for provenance/status metadata rather than immediate direct data extraction.

## Manifest Observations

- `source_status_manifest.csv` correctly marks Wong2015 and Amundsen2009 as `present_md_needs_extraction`, MEA-H2O dielectric as `local_literature_lead`, and loaded pH/direct ionic activity as `source_pending`.
- Target directories for source manifest rows exist.
- `regression_artifact_manifest.csv` correctly marks `phase3_fit_result.json` as `blocked_by_package_runtime`.
- `figure_artifact_manifest.csv` has the 15 figure IDs and current diagnostic/planned status, but it does not contain concrete artifact path columns. T050 should either add path/status detail or create a companion figure-plan mapping artifact.

## Candidate Worker Slices

- T010: tighten manifest/roadmap ingest consistency first; allowed files should include `data/reference/MEA/manifests/*.csv` and `docs/roadmaps/*.md`.
- T020: add extraction-ready schemas/manifests and README/status files for Wong 2015, Amundsen 2009, and MEA-H2O dielectric.
- T030: begin with Amundsen 2009 table extraction only if a table-specific pass confirms numeric rows are unambiguous; otherwise stage extraction tasks with source/status metadata.
- T040: audit `docs/latex/` and `docs/roadmaps/` for overclaims and local path leakage.
- T050: map current diagnostic artifacts to the 15-figure plan without regenerating package-dependent figures.
- T060: document missing ePC-SAFT dev worktree/build and final rerun commands.
