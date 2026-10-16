# Route 2b: λ=0, start A, two dielectric branches

**smaller-dV:** limit_reached at 53 iterations, training cost 36.7833961664, common-149 cost 23.0753630456. **larger-dV:** Fit running; no returned result.

The two authorized calls use λ=0, start A, 100 iterations, 1200 s native wall and a 1320 s crash backstop, with 12000 CPU-s checked after normal reaping. Bound activity is reported. The frozen declaration has 16 coordinates and 205 positive-weight rows. CO₂–water pivot and reciprocal-temperature slope are free; all 39 Kiepe natural-log pressure residuals have weight 1/39; bicarbonate–water has upper bound 1.0. All other declarations remain unchanged. No loaded-density assessment is run.

| Returned quantity | Smaller d_V | Larger d_V |
|---|---|---|
| Convergence status | limit_reached | Pending |
| Iterations | 53 | Pending |
| Residual evaluations | 54 | Pending |
| Jacobian evaluations | 47 | Pending |
| Projected gradient, tolerance 1e-8 | 0.000110807132411 | Pending |
| Initial training cost | 196.86581561 | Pending |
| Returned training cost | 36.7833961664 | Pending |
| Common-149 cost | 23.0753630456 | Pending |
| Common-149 minus Route 2 partial | -1.20583106812 | Pending |
| Trial failures | 0 | Pending |

The earlier 81-iteration Route 2 partial has common-149 cost **24.2811941137**. Adopted **32.05668491** is historical context from different inputs and wheel. These are partial-iterate calibration statistics; an objective value is not a converged optimum or a parameter-adoption decision.

### Training cost by family

| Family | Rows | Smaller d_V | Larger d_V |
|---|---|---|---|
| Common-149 pressure | 47 | 6.78866387178 | Pending |
| Common-149 species | 94 | 15.0852796903 | Pending |
| Common-149 Vinjarapu heat | 8 | 1.20141948351 | Pending |
| Restored species | 7 | 1.69801644599 | Pending |
| Pooled Jakobsen ratios | 6 | 6.24600648378 | Pending |
| Kiepe pressure | 39 | 2.29832717517 | Pending |
| Equilibrium Cp | 4 | 3.46568301584 | Pending |

Costs are one half the sum of squared weighted residuals. All 149 common targets keep their original definitions, weights and scales. Cost reconstruction from the returned arrays is retained in each reported-results.json; it is arithmetic verification, not serialization replay.

### Kiepe pressure errors by isotherm

| T, K | Rows | Smaller mean absolute error, % | Smaller maximum absolute error, % | Larger mean absolute error, % | Larger maximum absolute error, % |
|---|---|---|---|---|---|
| 313.2 | 12 | 96.3778735169 | 98.2142367181 | Pending | Pending |
| 353.11 | 9 | 77.8852816516 | 85.051357781 | Pending | Pending |
| 373.26 | 12 | 58.9405035288 | 69.1574437004 | Pending | Pending |
| 393.17 | 6 | 31.3686952579 | 46.3200109654 | Pending | Pending |

Errors are calculated from all 39 returned pressure predictions against their retained observations. Signed means, log-residual root-mean-square values and isotherm costs are in each Kiepe-isotherms.csv. The smaller branch underpredicts most binary pressures strongly at its returned partial iterate; its lower common-149 cost therefore does not establish simultaneous agreement with the added binary data.

### Active bounds and objective gradients

| Branch | Coordinate | Value | Unit | Side | Gradient per optimizer unit | Gradient per quantity unit |
|---|---|---|---|---|---|---|
| smaller-dV | Bicarbonate–water k | 1 | dimensionless | upper | -0.000888184514473 | -0.0888184514473 |
| smaller-dV | Carbamate–MEAH⁺ k | -1 | dimensionless | lower | 0.0246367162102 | 2.46367162102 |
| smaller-dV | MEAH⁺ Born diameter | 5 | angstrom | upper | -0.00224389215565 | -0.0224389215565 |
| smaller-dV | Carbamate Born diameter | 5 | angstrom | upper | -0.00431899105143 | -0.0431899105143 |
| smaller-dV | R5 unshifted a_k | 2400 | K | lower | -0.338734138729 | 0.00423417673411 |
| smaller-dV | R5 enthalpy shift | 10000 | J/mol | upper | -0.000445945513378 | -1.78378205351e-07 |
| smaller-dV | MEAH⁺ dispersion/k | 950 | K | upper | -0.0108689636201 | -0.00108689636201 |

Gradients are Jᵀr for the weighted residual objective, using the returned weighted optimizer Jacobian. Quantity gradients include the reciprocal-correlation sign for R5 unshifted a_k. Bounds are search limits, not confidence intervals.

### All coordinate values against the 81-iteration Route 2 partial

| Coordinate | Unit | A start | Route 2 partial | Smaller d_V | Larger d_V |
|---|---|---|---|---|---|
| Carbamate–water k | dimensionless | 0.134080741317 | -0.202719733667 | 0.214819481849 | Pending |
| MEAH⁺–water k | dimensionless | -0.379554080066 | -0.152249129162 | -0.208848402803 | Pending |
| Bicarbonate–water k | dimensionless | 0.5 | 0.5 | 1 | Pending |
| Carbamate–MEAH⁺ k | dimensionless | -0.707285890215 | -1 | -1 | Pending |
| MEAH⁺–water slope b | K | -112.567750584 | 36.9034558902 | -337.127093362 | Pending |
| MEAH⁺ segment diameter | angstrom | 3.563 | 5.51743301647 | 4.16295757137 | Pending |
| Carbamate segment diameter | angstrom | 3.5605 | 5.8 | 5.38701343402 | Pending |
| MEAH⁺ Born diameter | angstrom | 3.563 | 5 | 5 | Pending |
| Carbamate Born diameter | angstrom | 3.5605 | 3.62897938162 | 5 | Pending |
| R5 unshifted a_k | K | 2677.91 | 2568.56004544 | 2400 | Pending |
| R2 enthalpy shift | J/mol | 0 | -10000 | 1667.91582297 | Pending |
| R5 enthalpy shift | J/mol | 0 | -8392.06021931 | 10000 | Pending |
| CO₂–water k(313.15 K) | dimensionless | -0.0464169011206 | -0.0464169011206 | -0.212524867101 | Pending |
| CO₂–water slope b | K | -35.6650522065 | -35.6650522065 | -249.206280174 | Pending |
| MEAH⁺ dispersion/k | K | 228.71 | 251.302802793 | 950 | Pending |
| Carbamate dispersion/k | K | 533.11 | 168.034884166 | 677.551986745 | Pending |

The fixed dielectric pairs remain smaller d_V/d_T = **0.2464540312088979 L/mol / 2436.4423007273617 K** and larger **0.7309888238084122 L/mol / 1019.0786110170793 K**. Segment-size coordinates retain the 0.88 packing/Debye–Hückel ties. R2/R5 enthalpy shifts preserve the 313.15 K pivot. R5 unshifted a_k is separate from the composed serialized reaction law, retained in each partial parameter file.

### Four molality-based solution Cp errors

| T, K | Loading | Observed Cp, kJ/(kg K) | Smaller Cp | Smaller signed error, % | Larger Cp | Larger signed error, % |
|---|---|---|---|---|---|---|
| 318.15 | 0 | 3.7195 | 3.84329140224 | 3.32817320169 | Pending | Pending |
| 318.15 | 0.358 | 3.3675 | 3.45783007606 | 2.6824076039 | Pending | Pending |
| 353.15 | 0 | 3.8566 | 3.83233767735 | -0.629111721565 | Pending | Pending |
| 353.15 | 0.358 | 3.4707 | 3.3662461415 | -3.0095905294 | Pending | Pending |

These four equilibrium Cp targets use 7 mol MEA/kg water and 101325 Pa; nominal unloaded states retain the declared 1e-6 CO₂ proxy. Molar-to-mass conversion uses the retained complete-feed amount and mass, and reproduces each source observation. These are fitted observations, not withheld validation.

### Numerical checks and limits

| Branch | Available rows | Full rank / columns | Free rank / columns | Full condition | Free condition | Native CPU-s | Complete call wall-s |
|---|---|---|---|---|---|---|---|
| smaller-dV | {'Available': 205} | 16/16 | 9/9 | 166973.649595 | 271.337775542 | 6795.859259 | 1279.28800544 |

Every returned native call exits 0 and is reaped without interruption. The driver retains a nonconvergence traceback for limit-reached returns; this does not supersede the owner instruction to run the other authorized branch. The native time-limit message describes an internal solver span; complete call timing can exceed 1200 s while remaining below the 1320 s crash backstop.

| Branch | Endpoint replay | Derivative checks | Hard stops before another call |
|---|---|---|---|
| smaller-dV | Unrun: fit did not converge | Unrun: fit did not converge | None reached |

These two bounded end-state comparisons are reported as scalar tables rather than an inferred continuous calibration curve. No parameter uncertainty, independent physical validation, adoption, manuscript promotion or delivered independent review is claimed. No λ=0.1, start B or assessment is run. Frozen, hash-checked source inputs are reused; no new literature judgment is made, and this worktree has no local literature reading shelf.

## Orchestrator continuation decisions, 2026-10-16

1. Delete the Route 2b live aggregate-CPU and process-group monitoring. Restore the lifecycle demonstrated by 4763f37: Engine native maximum_elapsed_time_seconds=1200, crash backstop at limit +120 s, normal reaping, and aggregate CPU after the call as RUSAGE_SELF + RUSAGE_CHILDREN. **No live CPU enforcement.** Measured CPU above 12000 s stops subsequent calls. Net executable change must be zero or negative, at most 10 gross additions inside the 900-line campaign ceiling.
2. Increase the fit allowance by **12000 CPU-s to 36000 CPU-s total**. Preserve the interrupted fit’s conservative **12000 CPU-s** reservation. Program entry is **36657.498914 CPU-s** against 144000, with at least **9809.316196 wall-s** including the earlier 5215.0172 s owner-requested idle wait. Preparation, checks, reporting, presentation and commits reserve **100 CPU-s / 240 active wall-s** from the remaining release/reporting allowance.

## Launcher deletion and evidence

Owner remains fit_campaign.py::stage6_study; its stage-6 callers and declarations remain. The /proc sampler, process-group setup/kill path, live sampling loop, sampling-only imports and per-process CPU resource limit are removed. Native wall control and crash containment remain. Base 79ea7bc: **5 gross executable additions / 28 removals, net −23**, within the 10-addition ceiling. Conservative campaign gross charge is **857/900** (852 prior + 5); deletions do not recover earlier gross charges. No executable is added for reporting. Compilation and all installed-wheel/input checks pass. [Change accounting](completion-change-accounting.json) and [wheel/input check](completion-wheel-and-input-check.json) retain the evidence. Engine wheel SHA-256 is 98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a, merged Engine 84ca269dfa0c7068417a1c4c326acae276d4d965; all 12 installed files and Python/package pins match. Both fits request 32 native workers, single-thread BLAS/OpenMP and nice 10. Each call records sufficient free memory for its 8.59 GB estimate; actual worker count is not returned by Engine.

## Release tests and interrupted-call history

The four retained start-A release tests pass on both branches at λ=0/1: mandatory rank 14/14, augmented rank 16/16 and projected dispersion rank 2/2. All 217 requested rows are Available; 205/217 have positive weights at λ=0/1. [Release matrices, spectra and ranks](release-180/release-tests.json) are reused without repetition. The declaration retains the [owner decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6208172805), fixed dielectric branch, original A start and all original Route 2 conditions except its authorized additions.

The earlier smaller call stopped after a disappearing /proc entry raised ProcessLookupError. Its native workers also occupied separate process groups, defeating group-only live sampling. [Failure trace](smaller-dV/lambda-0-A/failure.json), [captured process identities and CPU snapshot](smaller-dV/process-stop.json), [inactive-process check](smaller-dV/process-stop-check.json) and [prior charges](continuation-accounting.json) remain unchanged. Its exact final CPU and endpoint are unavailable; the full 12000 CPU-s reservation remains charged. The launcher correction ran at 3dfc796; the smaller fit ran that commit, and the larger fit started at 257aa8c with the same executable tree.

## Retained branch evidence

- **smaller-dV:** [native return](smaller-dV/lambda-0-A-continuation/native.json) · [reported values](smaller-dV/lambda-0-A-continuation/reported-results.json) · [family costs](smaller-dV/lambda-0-A-continuation/family-costs.csv) · [all target errors](smaller-dV/lambda-0-A-continuation/target-costs.csv) · [Kiepe isotherms](smaller-dV/lambda-0-A-continuation/Kiepe-isotherms.csv) · [coordinates and gradients](smaller-dV/lambda-0-A-continuation/parameters-and-gradients.csv) · [Cp](smaller-dV/lambda-0-A-continuation/Cp.csv) · [rank and conditions](smaller-dV/lambda-0-A-continuation/identification.json) · [partial parameters](smaller-dV/lambda-0-A-continuation/usable-budget-endpoint.json).

The [working notebook](../../../../notebook.qmd) presents these retained values. Native return files own predictions, residuals, Jacobians and optimization diagnostics; tables are derived views. No Quarto preview service, subagent, push, merge or GitHub write is used.
