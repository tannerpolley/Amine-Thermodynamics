# Bounded water feasibility study — issue #124

**Passed:** the first fit, `lambda-0.1-A` (λ = 0.1, start A = #160), meets every declared property and numerical gate. The search stopped after this one candidate. Nothing is adopted. Execute §2 of the accepted design only; dependent calibrations, solution Cp, C5, notebook, manuscript and independent delivered review remain outside this sub-agent delivery.

Liquid Cp: 20 primary states at 298.15–393.15 K and 0.300 MPa, 19 staggered states at 300.65–390.65 K and 0.300 MPa, and three atmospheric controls at 298.15/318.15/353.15 K. Saturation: both temperature grids. The objective has 20 saturated densities, 20 pressures and 23 Cp rows. The retained IAPWS-95 reference was reused byte-for-byte.

Five fitted values: m = 1.252753837934407; σ₀ = 2.780432614942962 Å; ε/k = 432.3788130932931 K; εAB/k = 1756.6497964508999 K; κAB = 0.0376197279502706. The four diameter-law exponential coefficients, 2B topology and ideal calorics stay fixed. `parameters.json` is a full historical document with only those five magnitudes changed; its inherited provenance and dependent mixture coefficients are historical, and it is not a qualified mixture record.

Errors below are mean / maximum absolute relative errors in percent.

| Grid / quantity | Original 9055458d | #160 756fec50 | Candidate |
|---|---:|---:|---:|
| primary / cp | 12.791634 / 15.008697 | 0.412549 / 0.604524 | 0.440033 / 1.486940 |
| staggered / cp | 12.792164 / 14.883558 | 0.432562 / 0.604049 | 0.415904 / 1.361324 |
| atmospheric-controls / cp | 13.845726 / 15.005115 | 0.372918 / 0.561504 | 0.784410 / 1.484535 |
| primary / saturated_liquid_rho | 0.048854 / 0.234396 | 0.132313 / 0.194363 | 0.036295 / 0.098465 |
| staggered / saturated_liquid_rho | 0.044745 / 0.208493 | 0.136279 / 0.194760 | 0.034330 / 0.077957 |
| primary / psat | 0.618734 / 0.966415 | 0.295906 / 0.436665 | 0.075413 / 0.170901 |
| staggered / psat | 0.620926 / 0.968438 | 0.299973 / 0.437434 | 0.070039 / 0.141053 |

Both frozen replay comparisons pass. The maximum statistical difference from the retained metrics is 3.15×10⁻¹⁴ absolute relative, versus the 10⁻⁶ limit. The candidate returns all 42 Cp states and all 39 saturation states. Maximum raw saturation residual is 4.286×10⁻¹⁴. Minimum ∂P/∂ρ is 81884.72 Pa·m³/mol on pressure-closed liquid roots and 81868.96 Pa·m³/mol on saturated liquid roots. Every saturated liquid density exceeds its vapor density.

All 42 centered total-enthalpy ladders improve from 0.1 to 0.05 K. Maximum errors are 1.147×10⁻⁸ (coarse) and 2.875×10⁻⁹ (fine), relative to native Cp, below 10⁻⁶ at both steps. No roundoff plateau exception was needed for this candidate. The historical 343.15 K row is retained in the frozen replay, with both errors and the subtraction-roundoff estimate.

Native fit: converged, 32 iterations, 33 residual-vector and 34 Jacobian evaluations; cost 4.3520994570 → 0.3883034272; 17.191779 CPU-s and 1.564529 native wall-s. Native row workers requested: 32 from 32 CPUs and 10.04 GB available memory. The Engine did not return the actual worker count. Fits were sequential and numerical-library threads were one.

Complete process accounting, including startup, final-tree reassessment and a conservative 2 s charge for the failed serialization attempt: **21.99 CPU-s, 7.08 active wall-s and 116.61 s elapsed wall time**, far below each 600 s limit. The elapsed timer includes intervening diagnosis, editing and tool interaction; the process timers count active execution commands. The failed replay attempt is retained under `serialization-attempt/`; it returned no fit and failed only while serializing the typed density-convergence object. The corrected boundary uses the existing serializer.

Evidence is calibration to an evaluated IAPWS-95 reference plus numerical verification. Staggered-grid comparison assesses unfitted sample points and was used for candidate selection. It does not establish independent experimental validation, a continuous error bound, parameter uniqueness, propagated uncertainty, solution/absorber performance, or behavior outside these temperatures and pressures. The fixed ideal-gas water record retains its disclosed extrapolation below 500 K.

`spec.json` and `inputs.json` retain all input and wheel hashes and package versions. `metrics.csv`, `lambda-0.1-A/assessment.json`, `water.csv`, `gates.json`, `native-fit.json`, `targets.json` and `parameters.json` retain the quantities and checks. `verification.json` records the objective-cost and five-coordinate invariants. The Engine wheel is the merged main-36485a88 artifact, SHA-256 da5a2b65668ab5647e51b917a659614bdcb4afbe7e5c3149aee2294b86a4c1bd; every installed Engine package file was verified against it.

The existing declarative runner owns execution and the existing observation module owns the water observation and assessment declarations. Added code implements no optimizer or EOS equations and retires no valid prior path. The authorized executable ceiling is 150 gross added lines against 0e923d6f. The unchanged existing declaration check passes all 48 historical campaign starts, including its hash rejection and constrained-memory checks (`structure-check.json`). Independent delivered review and investigator promotion remain open gates before any downstream use.
