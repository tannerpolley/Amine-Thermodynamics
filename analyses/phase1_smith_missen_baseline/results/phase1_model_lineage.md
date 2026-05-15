# Phase 1 Model Lineage

lineage_status: retained_baseline_audit
phase1_status: model_ran_but_failed_validation

This artifact is a retained-baseline audit, not an independent Smith-Missen reproduction. It copies the repo's historical six-species apparent-equilibrium pressure/speciation outputs and the neutral ePC-SAFT parity outputs into a Phase 1 comparison surface.

The analysis records the Baygi/Nasrifar-style reaction-constant table and selected neutral parameter options, but the retained solver does not solve the full five-reaction explicit-ion Smith-Missen problem in this Phase 1 script. Claims must therefore be limited by `phase1_residual_acceptance_audit.csv`.
