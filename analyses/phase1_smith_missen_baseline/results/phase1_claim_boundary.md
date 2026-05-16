# Phase 1 Claim Boundary

phase1_status: validated_major_species_speciation_with_pressure_limits
lineage_status: explicit_ideal_smith_missen_reproduction

Allowed claims:
- The Phase 1 speciation workflow solves the explicit five-reaction, nine-species ideal Smith-Missen equilibrium system.
- Major observed speciation species may be used as Phase 1 validation evidence where `phase1_residual_acceptance_audit.csv` has `claim_allowed=true`.
- Pressure comparisons may be discussed only where `phase1_residual_acceptance_audit.csv` has `claim_allowed=true`.

Forbidden claims:
- Do not use trace or unobserved species as successful major-species validation evidence.
- Do not present the lower-temperature pressure rows as validated where their audit rows fail.
- Do not promote this Phase 1 baseline to a finalized joint-regression parameter set.

Residual-gate failures, trace limits, or unobserved targets:
- pressure: CO2_pressure at 40
- pressure: CO2_pressure at 60
- speciation: CO2 at 20.0
- speciation: CO3^2- at 20.0
- speciation: CO2 at 40.0
- speciation: CO3^2- at 40.0
- speciation: CO2 at overall
- speciation: CO3^2- at overall
- speciation: H3O+ at overall
- speciation: OH- at overall
