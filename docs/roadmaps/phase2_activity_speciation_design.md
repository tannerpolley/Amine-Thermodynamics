# Phase 2 Activity Speciation Design

Date: 2026-05-15 local

This roadmap records the fixed Phase 2 activity-based ePC-SAFT speciation and pressure-evaluation design represented by `analyses/phase2/activity_epcsaft/results/phase2_activity_speciation_problem.json` and the generated Phase 2 CSV artifacts. It is not a Phase 3 coupled pressure/speciation regression plan.

## Species

The true-species liquid basis contains CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-, H3O+, and OH-. The charged species use the charge assignments recorded in `phase2_activity_speciation_problem.json`.

## Vapor/liquid split

The volatile species are CO2, H2O, and MEA. MEAH+, MEACOO-, HCO3-, CO3^2-, H3O+, and OH- are recorded as nonvolatile species in the generated problem definition.

## Reaction network

The Phase 2 native solver uses the five reaction-constant rows R1-R5 from `data/reference/MEA/manifests/phase2_reaction_constant_manifest.csv` and the corresponding generated `phase2_reaction_constant_basis.csv`. The code names are water autoionization, CO2-to-HCO3-, HCO3--to-CO3^2-, MEACOO- hydrolysis, and MEAH+ dissociation.

## Balances

The material balances in the generated problem definition are total amine over MEA, MEAH+, and MEACOO-, and total carbon over CO2, MEACOO-, HCO3-, and CO3^2-. Electroneutrality is recorded as a separate constraint over the charged species.

## Activity convention

The activity convention is mole-fraction activity. The activity-constant candidate manifest records five source-verified native-solver inputs, and the source-verification table records that no external source path was used for the checked reaction-constant values.

## Reference states

The generated problem definition records `standard_state_used` as `mole_fraction_activity`. Residual claims remain controlled by the generated residual tables rather than by the presence of source-verified reaction constants alone.

## Parameter set

The fixed parameter artifact for this Phase 2 evaluation is `data/reference/epcsaft_datasets/MEA_CO2_H2O_phase2`.

## Dielectric option

The generated problem definition records the dielectric option as sensitivity-only unless direct MEA-H2O dielectric evidence supports a fit. No completed coupled regression is reported here.

## Born option

The generated problem definition records the Born option as advanced Born SSM+DS with the promoted regularized carbonate pair.

## Solver route

The generated route builds the true-species problem definition from the JSON and reaction manifest, uses the pinned native ePC-SAFT reactive-speciation route for liquid activity-equilibrium rows, uses the pinned reactive electrolyte bubble route for volatile-species pressure rows, and records solver status and residual gates explicitly.

## Package dependency status

The generated problem definition records the pinned `epcsaft` commit `9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785` as the package dependency for the Phase 2 artifacts.

## Source-resolved residual accounting

The source-level accounting table is `analyses/phase2/activity_epcsaft/results/phase2_source_residual_summary.csv`. It accounts for the 161 pressure records and 74 speciation state records while keeping measured pressure, nonzero measured speciation, zero-reported targets, and balance-inferred quantities in separate rows.
