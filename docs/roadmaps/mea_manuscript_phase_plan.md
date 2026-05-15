# MEA–CO2–H2O ePC-SAFT Manuscript Phase Plan

## Purpose

This roadmap organizes the MEA–CO2–H2O manuscript into staged, evidence-gated phases. It preserves the strict manuscript structure and figure plan while preventing overclaims before package and data dependencies are complete.

## Phase 0 — Repository and data inventory

Inventory:

- available data files,
- pressure data,
- speciation data,
- Jou and other VLE data,
- Wong Raman data,
- Amundsen density/viscosity data,
- MEA–H2O dielectric/permittivity data,
- pH/electrochemical candidate sources,
- direct ionic activity/osmotic candidate sources,
- current scripts,
- current parameter files,
- current figures,
- current manuscript source,
- current package import method.

Outputs:

- `docs/roadmaps/mea_data_curation_plan.md`
- `data/reference/MEA/manifests/source_status_manifest.csv`
- `data/reference/MEA/manifests/parameter_provenance_manifest.csv`

Current repo note:

- Wong 2015 and Amundsen 2009 Markdown files are present under `docs/papers/md/` and need extraction.
- MEA-H2O dielectric constants remain a literature-lead extraction task.
- Loaded-MEA pH/electrochemical data and direct MEAH+/carbamate osmotic-activity data remain source-pending.

## Phase 1 — Simplified Smith–Missen-style reproduction baseline

Goal:

Replicate the basic MEA/CO2/H2O workflow used in older PC-SAFT / SAFT-HR MEA papers before adding activity-based ePC-SAFT speciation.

Use:

- pure-component PC-SAFT/ePC-SAFT parameters,
- binary parameters where needed,
- literature reaction/equilibrium constants,
- ideal or apparent Smith–Missen-style speciation,
- no ePC-SAFT activity correction inside speciation equations,
- EOS fugacity/property calculations where appropriate.

Expected outputs:

- `phase1_parameter_table.md`
- `phase1_species_basis.md`
- `phase1_reaction_constants.md`
- `phase1_speciation_validation.csv`
- `phase1_pressure_parity.csv`
- `phase1_figures/`
- `phase1_limitations.md`

Allowed claim:

> This is an ideal/apparent-speciation reproduction baseline.

Forbidden claim:

> This is the final true-species ePC-SAFT activity-based MEA model.

Current repo note:

- The reproducible repo-owned baseline is now consolidated under `analyses/phase1_smith_missen_baseline/`.
- The supporting provenance files are `data/reference/MEA/manifests/phase1_data_inventory.csv`, `data/reference/MEA/manifests/phase1_parameter_provenance.csv`, and `data/reference/MEA/manifests/reaction_constant_manifest.csv`.
- Speciation is now the explicit five-reaction, nine-species ideal Smith-Missen solve; retained six-species and neutral-parity workflows remain only the pressure/parity anchors.

## Phase 2 — Activity-based ePC-SAFT speciation and VLE

Goal:

Move from ideal/apparent speciation to thermodynamic activity-based speciation using ePC-SAFT activities/fugacities.

Use:

- explicit reaction-constant conventions,
- true-species liquid basis,
- ePC-SAFT activity/fugacity/chemical-potential evaluations,
- volatile neutral vapor species only unless explicitly modeled otherwise.

Expected outputs:

- `phase2_reaction_constant_basis.md`
- `phase2_activity_speciation_problem.json`
- `phase2_equilibrium_results.csv`
- `phase2_pressure_speciation_parity.csv`
- `phase2_comparison_to_phase1.md`
- `phase2_package_dependency_matrix.md`

Allowed claim:

> This is an activity-based true-species ePC-SAFT evaluation.

Forbidden claim:

> This is a finalized joint-regression result.

Current repo note:

- Phase 2 now has native ePC-SAFT activity-equilibrium, pressure, diagnostics, residual-audit, and smooth solver-success-only curve artifacts under `analyses/phase2_activity_epcsaft/`.
- Phase 2 model-run status is `model_ran_success`; the target-role residual audit controls which species/properties can be claimed as validated.
- Existing older full-ionic pressure/speciation artifacts remain diagnostic unless they are regenerated through the Phase 2 workflow.
- Wong 2015 should be validation-first after extraction.

## Phase 3 — Coupled regression mode

Goal:

Allow selected reaction-equilibrium constants and selected ePC-SAFT parameters to move together if data justify it.

Fit-capable categories:

- MEAH+ sigma, epsilon, d_born,
- MEACOO- sigma, epsilon, d_born,
- HCO3- d_born,
- CO3^2- d_born,
- selected binary interaction parameters,
- MEA f_solv only with direct dielectric/activity evidence,
- reaction-equilibrium constant corrections only with explicit convention and regularization.

Expected outputs:

- `phase3_regression_problem.json`
- `phase3_fit_result.json`
- `phase3_parameter_movement.csv`
- `phase3_active_bounds.csv`
- `phase3_source_residual_summary.csv`
- `phase3_target_family_summary.csv`
- `phase3_pressure_speciation_figures/`
- `phase3_identifiability_notes.md`

Allowed claim:

> This is a coupled pressure/speciation regression only if all fit artifacts exist and all figures use the same final parameter artifact.

Forbidden claim:

> Newly regressed final parameters, if the final pressure/speciation regression was not actually executed.

Current repo note:

- Current global-regression artifact is not a completed coupled fit. It records `package_fit_not_completed` and keeps `promoted_ionic_fit` as the selected parameter set.
- Pressure/speciation figures cannot be described as final globally regressed results until Phase 3 artifacts exist.

## Phase 4 — Manuscript artifact generation and final audit

Goal:

Generate final manuscript figures/tables, insert them into LaTeX, and audit claims against artifacts.

Required:

- final figure CSV/PNG/SVG/YAML artifact set,
- final parameter table,
- final data manifest,
- final source provenance table,
- final train/validation summary,
- final limitations section,
- data/code availability statement,
- no local-path leakage,
- no internal agent/handoff language in manuscript.

## Strict manuscript structure

1. Introduction
2. Theory
3. Data and Methods
4. Results and Discussion
5. Conclusions
6. Data and Code Availability
7. Supporting Information

Do not alter the manuscript spine without explicit user approval.
