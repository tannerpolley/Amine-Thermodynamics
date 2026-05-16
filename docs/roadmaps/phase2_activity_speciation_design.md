# Phase 2 Activity-Based ePC-SAFT Speciation Design

## Purpose

Phase 2 evaluates MEA-CO2-H2O with a true-species ePC-SAFT liquid basis and ePC-SAFT fugacity/activity evaluations. It is a convention-safe evaluation phase, not the final coupled-regression phase.

## Species

| Species | Phase role | Charge | Notes |
|---|---|---:|---|
| CO2 | liquid and vapor | 0 | Volatile molecular acid gas. |
| MEA | liquid and vapor | 0 | Volatile neutral amine. |
| H2O | liquid and vapor | 0 | Volatile solvent. |
| MEAH+ | liquid only | 1 | Protonated MEA. |
| MEACOO- | liquid only | -1 | Carbamate species. |
| HCO3- | liquid only | -1 | Bicarbonate trace species. |
| CO3^2- | liquid only | -2 | Carbonate trace species. |
| H3O+ | liquid only | 1 | Proton carrier. |
| OH- | liquid only | -1 | Hydroxide trace species. |

## Vapor/liquid split

- Volatile species: `CO2`, `H2O`, `MEA`.
- Nonvolatile species: `MEAH+`, `MEACOO-`, `HCO3-`, `CO3^2-`, `H3O+`, `OH-`.
- Ions remain liquid-only unless a future generic package equilibrium problem explicitly supports ionic vapor species.

## Reaction network

| ID | Reaction | Current Phase 2 use |
|---|---|---|
| R1 | `2 H2O <-> H3O+ + OH-` | Source value verified against repo-local Nasrifar Table 1, which traces the value family to Austgen 1991; used as a fixed input in the pinned native ePC-SAFT activity solve. |
| R2 | `CO2 + 2 H2O <-> HCO3- + H3O+` | Source value verified against repo-local Nasrifar Table 1, which traces the value family to Austgen 1991; used as a fixed input in the pinned native ePC-SAFT activity solve. |
| R3 | `HCO3- + H2O <-> CO3^2- + H3O+` | Source value verified against repo-local Nasrifar Table 1, which traces the value family to Austgen 1991; used as a fixed input in the pinned native ePC-SAFT activity solve. |
| R4 | `MEACOO- + H2O <-> MEA + HCO3-` | Source value verified against repo-local Nasrifar Table 1 k9; used as a fixed input in the pinned native ePC-SAFT activity solve. |
| R5 | `MEAH+ + H2O <-> MEA + H3O+` | Source value verified against repo-local Nasrifar Table 1 k7; used as a fixed input in the pinned native ePC-SAFT activity solve. |

The reaction-constant source table is `data/reference/MEA/manifests/phase2_reaction_constant_manifest.csv`, and the value-level source audit is `data/reference/MEA/manifests/phase2_reaction_constant_source_verification.csv`. Phase 2 must not pass apparent mole-fraction constants into thermodynamic-activity equations as if they were residual-validated activity-equilibrium results.

## Balances

The Phase 2 problem definition uses these conserved quantities:

- Material balance, total amine: `MEA + MEAH+ + MEACOO-`.
- Material balance, total carbon: `CO2 + MEACOO- + HCO3- + CO3^2-`.
- Constraint, liquid electroneutrality: `MEAH+ + H3O+ - MEACOO- - HCO3- - 2 CO3^2- - OH- = 0`.
- Water appears explicitly in all hydrolysis/proton reactions and remains the dominant liquid solvent.

## Activity convention

- Needed Phase 2 basis: thermodynamic activity constants with explicit reference states.
- Current manifest status: repo-local Nasrifar Table 1 verifies R1-R5 source values on the mole-fraction equilibrium-constant family traced to Austgen 1991; the values are used as fixed inputs in the pinned native ePC-SAFT activity solve.
- Allowed current use: model-run evidence from solver-success rows plus target-role residual-gated pressure/speciation comparisons.
- Blocked current use: final joint-regression claims before Phase 3 package-native regression and approval gates pass.

## Reference states

Reference states are not inferred. Each reaction must declare one of:

- `mole_fraction_apparent`
- `molality_apparent`
- `thermodynamic_activity`
- `converted`
- `not_converted`
- `not_used`

The package `ReactionDefinition` supports a `standard_state` and convention metadata, but the MEA repo still owns the source-to-package mapping and must not silently choose a standard state.

## Parameter set

Phase 2 uses one parameter artifact for all pressure, speciation, residual, and comparison outputs:

`data/reference/epcsaft_datasets/MEA_CO2_H2O_phase2/`

The initial Phase 2 artifact is a documented promotion of the current `MEA_CO2_H2O_ionic_fit` dataset into a Phase 2-owned folder. Later parameter movement must update this one artifact or write a rejected candidate outside it.

## Dielectric option

Current policy: sensitivity-only unless direct MEA-H2O dielectric/permittivity evidence supports fitting.

The MEA neutral row keeps `f_solv = 1` for Phase 2. Do not promote a fitted MEA `f_solv` from pressure data alone.

## Born option

Phase 2 uses the current advanced Born SSM+DS option set from the promoted ionic dataset. The trace carbonate values remain the regularized promoted pair:

- `HCO3- d_born = 3.0`
- `CO3^2- d_born = 3.0`

The earlier trace-only alternative remains an identifiability warning, not a promoted Phase 2 parameter set.

## Solver route

1. Build the true-species problem definition from this document, the reaction manifest, and the Phase 2 parameter artifact.
2. Use the pinned native ePC-SAFT activity speciation route for liquid equilibrium rows.
3. Use package electrolyte bubble/fugacity support for volatile species after a liquid state is convention-safe.
4. Write solver diagnostics and residual gates explicitly; validation outcomes do not rewrite model-run success.
5. Use `phase2_speciation_target_roles.csv` to keep direct positive targets, reported-zero upper bounds, and balance-inferred context rows separate before plotting or metric calculation.

## Package dependency status

Current package inspection found generic reactive speciation, electrolyte bubble/fugacity, target dataset, and reactive electrolyte batch regression surfaces. The pinned package commit `9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785` runs the Phase 2 native activity-equilibrium and reactive bubble paths successfully. Remaining limits are residual/claim gates and Phase 3 coupled-regression readiness, not a Phase 2 solver availability blocker.
