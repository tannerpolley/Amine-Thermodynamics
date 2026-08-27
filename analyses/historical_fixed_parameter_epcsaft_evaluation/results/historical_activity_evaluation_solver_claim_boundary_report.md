# historical fixed-parameter ePC-SAFT evaluation Solver And Claim Boundary Report

historical_activity_evaluation_status: model_ran_success
historical_activity_evaluation_validation_status: residual_limited
source_status: source_verified
solver_status: native_epcsaft_activity_solver_ran

historical fixed-parameter ePC-SAFT evaluation activity-evaluation claims are controlled by `historical_activity_evaluation_residual_acceptance_audit.csv`.
This does not claim a reactive ePC-SAFT parameter evidence package-native joint regression.

This run uses pinned ePC-SAFT commit `9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785` and generates actual activity-coupled equilibrium rows from the historical fixed-parameter ePC-SAFT evaluation parameter artifact.

Evidence now present:
- 5 of 5 R1-R5 source-value rows are verified against repo-local source text in `historical_activity_evaluation_reaction_constant_source_verification.csv`.
- The generated problem definition separates material balances from electroneutrality constraints.
- `historical_activity_evaluation_equilibrium_results.csv`, `historical_activity_evaluation_pressure_speciation_parity.csv`, metrics, `historical_activity_evaluation_solver_diagnostics.csv`, and activity-curve rows are generated from the native ePC-SAFT solver.
- `historical_activity_evaluation_source_residual_summary.csv` records source-resolved pressure and speciation residual accounting without mixing nonzero, zero-reported, and balance-inferred target roles.
- `historical_activity_evaluation_speciation_activity_curves.csv` contains only solver-success curve rows.
- `historical_activity_evaluation_speciation_target_roles.csv` prevents reported-zero and balance-inferred rows from being treated as direct log-residual targets.

Failed gates:
- solver: curve_grid_success_fraction success_fraction=0.9968944099378882 threshold=1.0
