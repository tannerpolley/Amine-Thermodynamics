# Issues 4 and 5 Acceptance Status

This file is the PR #7 acceptance ledger. It prevents source inventory, solver execution, and residual validation from being collapsed into one completion claim.

Allowed status values here are `pass`, `fail`, `blocked`, `not_started`, and `not_applicable`.

## Issue 4 - Phase 1 Smith-Missen Baseline

| Gate | Status | Evidence | Notes |
|---|---|---|---|
| Reaction-constant source table generated | pass | `analyses/phase1_smith_missen_baseline/results/phase1_reaction_constant_table.csv` | R1 coefficient sign is repaired in the generated table. |
| Phase 1 model lineage documented | pass | `analyses/phase1_smith_missen_baseline/results/phase1_model_lineage.md` | Lineage now records the explicit five-reaction, nine-species ideal speciation solve. |
| Pressure residual audit generated | pass | `analyses/phase1_smith_missen_baseline/results/phase1_residual_acceptance_audit.csv` | Pressure claim permission is metric-row-specific. |
| Speciation residual audit generated | pass with trace limits | `analyses/phase1_smith_missen_baseline/results/phase1_residual_acceptance_audit.csv` | Major observed species pass after switching to the explicit ideal Smith-Missen solve; trace/unobserved species remain limited. |
| Claim boundary documented | pass | `analyses/phase1_smith_missen_baseline/results/phase1_claim_boundary.md` | Status reports major-species speciation validation with pressure/trace limits. |
| Final Phase 1 manuscript result | bounded | pressure and trace-species residual gates | Major speciation is ready for Phase 1 use; pressure rows and trace species remain gate-limited. |

## Issue 5 - Phase 2 Activity ePC-SAFT Evaluation

| Gate | Status | Evidence | Notes |
|---|---|---|---|
| True-species problem definition generated | pass | `analyses/phase2_activity_epcsaft/results/phase2_activity_speciation_problem.json` | JSON separates material balances from electroneutrality constraints. |
| Source-value verification table present | pass | `data/reference/MEA/manifests/phase2_reaction_constant_source_verification.csv` | Source values are verified against repo-local Nasrifar Table 1 and used as fixed inputs in the native activity solve. |
| Local absolute paths removed from tracked artifacts | pass | `scripts/check_no_local_paths.py` | The quick validator runs this check before tests. |
| Phase 2 equilibrium rows generated | pass | `analyses/phase2_activity_epcsaft/results/phase2_equilibrium_results.csv` | Rows come from the pinned native ePC-SAFT activity solver; top-level run status is `model_ran_success`. |
| Pressure/speciation residual metrics generated | pass | `analyses/phase2_activity_epcsaft/results/phase2_residual_acceptance_audit.csv` | Residual rows control claim permission only; they do not change the model-run status. |
| Speciation target roles generated | pass | `analyses/phase2_activity_epcsaft/results/phase2_speciation_target_roles.csv` | Direct positive targets, reported-zero upper bounds, and balance-inferred context rows are separated before metric calculation. |
| Phase 2 comparison report generated | pass | `analyses/phase2_activity_epcsaft/results/phase2_comparison_to_phase1.md` | Report labels Phase 2 as native model output with residual-gated limits. |
| Final Phase 2 manuscript result | pass | residual audit and Phase 3 boundary | The Phase 2 activity-evaluation residual gates pass under the target-role policy; the absent Phase 3 joint regression still prevents final global-regression claims. |
