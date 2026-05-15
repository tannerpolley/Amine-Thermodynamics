# Phase 1 Claim Boundary

phase1_status: model_ran_but_failed_validation
lineage_status: retained_baseline_audit

Allowed claims:
- The retained baseline artifacts were regenerated and audited against explicit pressure and speciation residual gates.
- Pressure comparisons may be discussed only where `phase1_residual_acceptance_audit.csv` has `claim_allowed=true`.
- Speciation comparisons may be discussed only as species-specific retained-baseline diagnostics unless the audit row for that species has `claim_allowed=true`.

Forbidden claims:
- Do not claim Phase 1 has passed validation.
- Do not claim an independent full five-reaction Smith-Missen reproduction.
- Do not use trace or unsupported species as successful validation evidence.
- Do not promote this retained-baseline audit to a finalized joint-regression parameter set.

Residual-gate failures or diagnostic-only targets:
- pressure: CO2_pressure at 40
- pressure: CO2_pressure at 60
- speciation: CO2 at 20.0
- speciation: CO3^2- at 20.0
- speciation: HCO3- at 20.0
- speciation: MEACOO- at 20.0
- speciation: MEAH+ at 20.0
- speciation: CO2 at 40.0
- speciation: CO3^2- at 40.0
- speciation: HCO3- at 40.0
- speciation: CO2 at overall
- speciation: CO3^2- at overall
- speciation: H3O+ at overall
- speciation: HCO3- at overall
- speciation: MEACOO- at overall
- speciation: MEAH+ at overall
- speciation: OH- at overall
