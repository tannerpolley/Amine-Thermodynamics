# Phase 2 Reaction Constant Basis

## Rule

Phase 2 must not mix apparent mole-fraction or molality constants with ePC-SAFT activity coefficients unless a conversion and reference-state convention are documented. A package API accepting a `standard_state` is not itself a source conversion.

## Manifest

The machine-readable manifest is:

`data/reference/MEA/manifests/phase2_reaction_constant_manifest.csv`

The local source-audit candidate manifest is:

`data/reference/MEA/manifests/phase2_activity_constant_candidates.csv`

## Current status

| ID | Source basis | Activity basis needed | Conversion status | Phase 2 use |
|---|---|---|---|---|
| R1 | Austgen unsymmetric mole-fraction activity | thermodynamic activity | thermodynamic activity | fixed input pending upstream solver |
| R2 | Austgen unsymmetric mole-fraction activity | thermodynamic activity | thermodynamic activity | fixed input pending upstream solver |
| R3 | Austgen unsymmetric mole-fraction activity | thermodynamic activity | thermodynamic activity | fixed input pending upstream solver |
| R4 | Austgen unsymmetric mole-fraction activity | thermodynamic activity | thermodynamic activity | fixed input pending upstream solver |
| R5 | Austgen unsymmetric mole-fraction activity corrected to pure amine reference | thermodynamic activity | thermodynamic activity | fixed input pending upstream solver |

## Local activity-constant candidates

The expanded local paper audit found a complete H3O+-basis candidate set for R1-R5 in `Nasrifar and Tafazzol - 2010 - Vapor-liquid equilibria of acid gas-aqueous ethanolamine solutions us.md` Table 1. That table traces the constants to Austgen et al. (1991), lists the MEA protonation and carbamate-hydrolysis reactions in the same H3O+ reaction family used by the current MEA reaction matrix, and defines the equilibrium relation with `x_j gamma_j` terms.

The supplied Austgen 1991 PDF and extracted markdown resolve the promotion gate. Austgen states that water and alkanolamine solvents use pure-liquid standard states, ionic and molecular solutes use the ideal infinitely dilute aqueous solution, activity coefficients follow an unsymmetric convention, and reaction constants are evaluated as products of `x_i gamma_i` terms. Table V gives R1-R5 coefficients on the mole-fraction scale and states the MEA protonation constant is corrected to the pure amine reference state.

The MDEA ePC-SAFT literature path (`Uyan et al.md`, `Wangler et al.md`, `Bülow et al.md`, and `Cleeton et al.md`) remains useful method evidence for activity-coefficient treatment and reference-state normalization. It is no longer needed as a direct fallback for MEA R4/R5 constants, and its H+ reaction convention must not be silently mixed with the current H3O+ MEA reaction matrix.

## Implementation consequence

The first Phase 2 artifacts can define species, balances, package routes, one parameter artifact, and the promoted R1-R5 fixed-input rows. A claimed activity-based speciation result must now wait on upstream ePC-SAFT issue #115 because the pinned package raises `backend_unavailable` for the activity-coupled native chemical-equilibrium backend.

## Phase 3 role

The current constants can regularize or initialize Phase 3 only after their convention is explicit. They must not become free reaction-constant fit targets in Phase 2.
