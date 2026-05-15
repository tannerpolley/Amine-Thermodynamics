# Issues 4 and 5 Acceptance Status

This file is the PR #7 acceptance ledger. It prevents source inventory, scaffold generation, and residual validation from being collapsed into one completion claim.

Allowed status values here are `pass`, `fail`, `blocked`, `not_started`, and `not_applicable`.

## Issue 4 - Phase 1 Smith-Missen Baseline

| Gate | Status | Evidence | Notes |
|---|---|---|---|
| Reaction-constant source table generated | pass | `analyses/phase1_smith_missen_baseline/results/phase1_reaction_constant_table.csv` | R1 coefficient sign is repaired in the generated table. |
| Phase 1 model lineage documented | pass | `analyses/phase1_smith_missen_baseline/results/phase1_model_lineage.md` | Lineage is retained-baseline audit, not independent full five-reaction reproduction. |
| Pressure residual audit generated | pass | `analyses/phase1_smith_missen_baseline/results/phase1_residual_acceptance_audit.csv` | Pressure claim permission is metric-row-specific. |
| Speciation residual audit generated | fail | `analyses/phase1_smith_missen_baseline/results/phase1_residual_acceptance_audit.csv` | Multiple species are failed or diagnostic-only, so Phase 1 cannot be called validated. |
| Claim boundary documented | pass | `analyses/phase1_smith_missen_baseline/results/phase1_claim_boundary.md` | Status remains `model_ran_but_failed_validation`. |
| Final Phase 1 manuscript result | blocked | upstream solver/package and residual gates | Not claimed in this PR. |

## Issue 5 - Phase 2 Activity ePC-SAFT Scaffold

| Gate | Status | Evidence | Notes |
|---|---|---|---|
| True-species problem definition generated | pass | `analyses/phase2_activity_epcsaft/results/phase2_activity_speciation_problem.json` | JSON separates material balances from electroneutrality constraints. |
| Source-value verification table present | pass | `data/reference/MEA/manifests/phase2_reaction_constant_source_verification.csv` | Source values are verified against repo-local Nasrifar Table 1; model use remains blocked. |
| Local absolute paths removed from tracked artifacts | pass | `scripts/check_no_local_paths.py` | The quick validator runs this check before tests. |
| Phase 2 equilibrium rows generated | blocked | upstream ePC-SAFT issue #115 | No `phase2_equilibrium_results.csv` is present or claimed. |
| Pressure/speciation residual metrics generated | blocked | `phase2_equilibrium_results.csv` | Metrics remain bounded incomplete until actual equilibrium rows exist. |
| Phase 2 comparison report generated | pass | `analyses/phase2_activity_epcsaft/results/phase2_comparison_to_phase1.md` | Report labels Phase 2 as bounded incomplete scaffold/problem definition. |
| Final Phase 2 manuscript result | blocked | upstream issue #115 and residual gates | Not claimed in this PR. |
