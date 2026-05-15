# Phase 2 Comparison To Phase 1

Phase 1 now solves the explicit five-reaction, nine-species ideal Smith-Missen speciation system with documented reaction constants and activities set equal to mole fractions. It remains distinct from Phase 2 because Phase 2 requires ePC-SAFT activity coefficients and package-native residual/source-validation gates.

Phase 2 now uses pinned ePC-SAFT commit `9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785` and the native activity-coupled reactive speciation / reactive electrolyte bubble route. The generated rows are real solver outputs, not scaffold or diagnostic curves.

phase2_status: model_ran_success
phase2_validation_status: validated

Phase 2 activity-evaluation claims are controlled by `phase2_residual_acceptance_audit.csv`. Failed gates:

- none
