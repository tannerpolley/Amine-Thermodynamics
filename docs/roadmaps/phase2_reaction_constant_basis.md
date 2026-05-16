# Phase 2 Reaction Constant Basis

Date: 2026-05-15 local

This roadmap records the repo-local evidence gate for the fixed R1-R5 reaction constants used by the Phase 2 activity-based ePC-SAFT evaluation.

## Evidence Artifacts

- `data/reference/MEA/manifests/phase2_reaction_constant_manifest.csv` records the R1-R5 manifest rows and their Phase 2 use status.
- `data/reference/MEA/manifests/phase2_reaction_constant_source_verification.csv` records the repo-local source checks for the R1-R5 numerical coefficients.
- `analyses/phase2_activity_epcsaft/results/phase2_reaction_constant_basis.csv` is the generated copy of the manifest basis used by the Phase 2 run.
- `analyses/phase2_activity_epcsaft/results/phase2_activity_speciation_problem.json` records the reaction rows in the generated problem definition.

## Reaction Rows

The five rows are R1 water autoionization, R2 CO2-to-HCO3-, R3 HCO3--to-CO3^2-, R4 MEACOO- hydrolysis, and R5 MEAH+ dissociation. The generated artifacts record each row as source-verified and used in the native solver with residual-gated manuscript claims.

## Source Boundary

The source-verification table records `external_source_path_used` as `no` for each reaction row. The table also records the repo-local source-paper Markdown file, source table identifier, coefficients A-D, source basis text, and model-use status.

## Claim Boundary

The reaction constants are fixed Phase 2 native-solver inputs. They do not establish a finalized global regression or pressure-optimized parameterization; manuscript claims remain bounded by the generated pressure and speciation residual tables.
