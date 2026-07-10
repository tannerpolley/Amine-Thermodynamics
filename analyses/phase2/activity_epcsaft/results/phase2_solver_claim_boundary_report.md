# Phase 2 Solver And Claim Boundary Report

phase2_status: model_ran_success
phase2_validation_status: residual_limited
source_status: source_verified
solver_status: native_epcsaft_activity_solver_ran

Phase 2 activity-evaluation claims are controlled by `phase2_residual_acceptance_audit.csv`.
This does not claim a Phase 3 package-native joint regression.

This run uses pinned ePC-SAFT commit `9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785` and generates actual activity-coupled equilibrium rows from the Phase 2 parameter artifact.

Evidence now present:
- 5 of 5 R1-R5 source-value rows are verified against repo-local source text in `phase2_reaction_constant_source_verification.csv`.
- The generated problem definition separates material balances from electroneutrality constraints.
- `phase2_equilibrium_results.csv`, `phase2_pressure_speciation_parity.csv`, metrics, `phase2_solver_diagnostics.csv`, and activity-curve rows are generated from the native ePC-SAFT solver.
- `phase2_source_residual_summary.csv` records source-resolved pressure and speciation residual accounting without mixing nonzero, zero-reported, and balance-inferred target roles.
- `phase2_speciation_activity_curves.csv` contains only solver-success curve rows.
- `phase2_speciation_target_roles.csv` prevents reported-zero and balance-inferred rows from being treated as direct log-residual targets.

Failed gates:
- solver: curve_grid_success_fraction success_fraction=0.9968944099378882 threshold=1.0
