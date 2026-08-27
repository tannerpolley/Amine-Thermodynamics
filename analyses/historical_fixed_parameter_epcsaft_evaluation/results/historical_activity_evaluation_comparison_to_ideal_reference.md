# historical fixed-parameter ePC-SAFT evaluation Comparison To ideal reaction-equilibrium reference

ideal reaction-equilibrium reference now solves the explicit five-reaction, nine-species ideal Smith-Missen speciation system with documented reaction constants and activities set equal to mole fractions. It remains distinct from historical fixed-parameter ePC-SAFT evaluation because historical fixed-parameter ePC-SAFT evaluation requires ePC-SAFT activity coefficients and package-native residual/source-validation gates.

historical fixed-parameter ePC-SAFT evaluation now uses pinned ePC-SAFT commit `9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785` and the native activity-coupled reactive speciation / reactive electrolyte bubble route. The generated rows are real solver outputs, not scaffold or diagnostic curves.

historical_activity_evaluation_status: model_ran_success
historical_activity_evaluation_validation_status: residual_limited

historical fixed-parameter ePC-SAFT evaluation activity-evaluation claims are controlled by `historical_activity_evaluation_residual_acceptance_audit.csv`. Failed gates:

- solver: curve_grid_success_fraction success_fraction=0.9968944099378882 threshold=1.0
