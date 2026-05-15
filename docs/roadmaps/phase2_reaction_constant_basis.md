# Phase 2 Reaction Constant Basis

## Rule

Phase 2 must not mix apparent mole-fraction or molality constants with ePC-SAFT activity coefficients unless a conversion and reference-state convention are documented. A package API accepting a `standard_state` is not itself a source conversion.

## Manifest

The machine-readable manifest is:

`data/reference/MEA/manifests/phase2_reaction_constant_manifest.csv`

The local source-audit candidate manifest is:

`data/reference/MEA/manifests/phase2_activity_constant_candidates.csv`

The value-level source verification ledger is:

`data/reference/MEA/manifests/phase2_reaction_constant_source_verification.csv`

## Current status

| ID | Source basis | Activity basis needed | Conversion status | Phase 2 use |
|---|---|---|---|---|
| R1 | Repo-local Nasrifar Table 1 via Austgen 1991 | thermodynamic activity | source_verified | not_yet_solver_blocked |
| R2 | Repo-local Nasrifar Table 1 via Austgen 1991 | thermodynamic activity | source_verified | not_yet_solver_blocked |
| R3 | Repo-local Nasrifar Table 1 via Austgen 1991 | thermodynamic activity | source_verified | not_yet_solver_blocked |
| R4 | Repo-local Nasrifar Table 1 k9 via Austgen 1991 | thermodynamic activity | source_verified | not_yet_solver_blocked |
| R5 | Repo-local Nasrifar Table 1 k7 via Austgen 1991 | thermodynamic activity | source_verified | not_yet_solver_blocked |

## Local activity-constant candidates

The expanded local paper audit found a complete H3O+-basis candidate set for R1-R5 in `Nasrifar and Tafazzol - 2010 - Vapor-liquid equilibria of acid gas-aqueous ethanolamine solutions us.md` Table 1. That table traces the constants to Austgen et al. (1991), lists the MEA protonation and carbamate-hydrolysis reactions in the same H3O+ reaction family used by the current MEA reaction matrix, and defines the equilibrium relation with `x_j gamma_j` terms.

The source ledger deliberately uses repo-local source text. If the original Austgen source must be cited as the primary source in a later manuscript pass, it should be added as a repo-local extracted source or marked `source_pending`; this PR does not use outside-repo absolute paths as evidence.

The MDEA ePC-SAFT literature path (`Uyan et al.md`, `Wangler et al.md`, `Bülow et al.md`, and `Cleeton et al.md`) remains useful method evidence for activity-coefficient treatment and reference-state normalization. It is no longer needed as a direct fallback for MEA R4/R5 constants, and its H+ reaction convention must not be silently mixed with the current H3O+ MEA reaction matrix.

## Implementation consequence

The first Phase 2 artifacts can define species, balances, constraints, package routes, one parameter artifact, and source-verified R1-R5 fixed-input rows. A claimed activity-based speciation result must wait on upstream ePC-SAFT issue #115 because the pinned package raises `backend_unavailable` for the activity-coupled native chemical-equilibrium backend.

## Phase 3 role

The current constants can regularize or initialize Phase 3 only after their convention is explicit. They must not become free reaction-constant fit targets in Phase 2.
