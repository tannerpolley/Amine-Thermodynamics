# Corrected initial ion starting records

Both declared ion starts are derived from the unchanged stage-2 CO₂–water B record. The bicarbonate–water interaction changes from +0.5 to zero; carbamate–water and protonated-MEA–water interaction and slope remain zero. Trace-ion interactions, source R2/R5, adopted water, pure neutral parameters, refreshed association and stage-2 neutral binaries are preserved. CO₂ dispersion is 169.21 K; unshifted R5 is 2677.91 K. The original file remains unchanged.

Start A retains the source ion seeds. Start B uses the seven values in design §4, with packing and Debye–Hückel diameters equal to 0.88 times each segment diameter. `derived-starts.json` records all input and starting-record hashes.

| State | T, K | Original density, kg/m³ | Corrected density, kg/m³ | Difference, kg/m³ |
|---|---:|---:|---:|---:|
| AMU-DENS-002 | 298.15 | 1009.907212360454 | 1009.907212360454 | 4.547e-13 |
| AMU-DENS-009 | 313.15 | 1003.287419110843 | 1003.287419110845 | 1.364e-12 |
| AMU-DENS-016 | 323.15 | 998.099992017500 | 998.099992017500 | -1.137e-13 |
| AMU-DENS-023 | 343.15 | 986.342794101139 | 986.342794101139 | 2.274e-13 |
| AMU-DENS-030 | 353.15 | 979.927109423929 | 979.927109423930 | 1.137e-12 |

The paired replay has relative objective difference 4.94711e-13, maximum weighted residual difference 5.25135e-13, and identical five row definitions. All five states solve at 30 wt% unloaded MEA and 0.1 MPa, with maximum raw equilibrium residual below 2.3×10⁻¹³ and positive pressure-density derivatives. These values numerically verify that the bicarbonate correction leaves the stage-2 neutral comparisons unchanged at the declared $10^{-8}$ limits. No neutral fit ran.

A reporting assertion initially required exact binary equality and stopped after the completed solves. The retained differences above satisfy the accepted tolerances; the assertion was corrected without repeating the model calls. This was not a failed declared replay, closure or serialization check.

Derivation and paired solves used 0.441394710 recorded command wall-s. CPU was not metered because the assertion preceded the timing write; a conservative 14.124630720 CPU-s charge uses 32 CPUs times the complete command duration. This charge counts against the initial ion-pair allowance. Earlier qualification startup remains unmetered as disclosed in its historical record.

Program boundary before the ion fits: 1187.728494 CPU-s / at least 432.145917 active wall-s; remaining at most 142812.271506 CPU-s / 21167.854083 wall-s. Initial ion-pair allowance after these checks is at most 2385.875369 CPU-s / 359.558605 wall-s. This is numerical verification and starting-record construction; no ion calibration result exists yet.

## Initial ion fit: required stop, no I₀ selected

Both A and B return all nine admitted states and 26 targets. The first A fit reaches the 40-iteration allowance without native convergence, and four coordinates reach lower bounds. Cost falls from 59.17684171980518 to 1.3609750436302284. The native result is `limit_reached`, `usable=true`, with all 26 target predictions available and zero trial failures. This is an incomplete conditional calibration result; it is not an accepted ion precursor or a physical limit of the model. No B fit or later stage ran.

The native iteration counter is 40; its diagnostic message separately says “Maximum number of iterations reached. Number of iterations: 20.” Both are retained exactly in `fit/ion-speciation/A/native-fit.json`; the reason for that discrepancy is unverified.

| Quantity | Start A | Returned A vector | Bounds | Active |
|---|---:|---:|---|---|
| MEAH⁺ segment diameter, Å | 3.563 | 4.49330937370393 | 2 to 5.8 | No |
| Carbamate segment diameter, Å | 3.5605 | 2 | 2 to 5.8 | Lower |
| MEAH⁺ dispersion/k, K | 228.71 | 489.253732302516 | 50 to 950 | No |
| Carbamate dispersion/k, K | 533.11 | 50 | 50 to 1000 | Lower |
| MEAH⁺ Born diameter, Å | 3.563 | 1 | 1 to 7 | Lower |
| Carbamate Born diameter, Å | 3.5605 | 1 | 1 to 7 | Lower |
| Mutual interaction | 0 | -0.763082703628406 | -2 to 2 | No |

**Large interaction movement:** mutual MEAH⁺–carbamate interaction changes by −0.763082703628406 from A, exceeding the 0.03 reporting scale. This scale is the earlier interaction search half-width, not measured uncertainty. The source R5 reference remains 2677.91 K, the CO₂–water pivot interaction remains −0.046416901120577676, and its slope remains −35.66505220645838 K. Their movement is zero in this ion-only attempt. CO₂ dispersion remains 169.21 K.

The weighted optimizer Jacobian is 26×7, rank 7/7, condition 16199.960584. Removing active columns 1, 3, 4 and 5 leaves rank 3/3, condition 147.29070907; the declared relative rank cutoff is $10^{-14}$. `identification.json` retains spectra, gradient, coordinate scales, covariance diagnostics and native singular vectors. Native covariance is `not_converged`, with no variance multiplier; no standard errors or movement allowances are inferred from this vector. The physical Jacobian is 26×11 because the diameter ties produce eleven parameter targets for seven coordinates.

| Family | A start cost | B start cost | A unconverged cost | A start / returned mean relative error, % |
|---|---:|---:|---:|---|
| All 26 targets | 59.1768417198 | 42.3676729612 | 1.36097504363 | 144.16579 / 18.180933 |
| 18 mole-fraction targets | 7.2027965343 | 5.25673578656 | 0.523204661816 | 63.006749 / 16.799706 |
| 8 Jakobsen ratios | 51.9740451855 | 37.1109371747 | 0.837770381815 | 326.77362 / 21.288693 |

The error rows are dimensionless in their declared mole-fraction or amount-ratio basis, with difference scale $0.1y^{obs}+0.001$ and weight 1/26. Their weighting is an engineering declaration, not source covariance. Mole fractions and ratios retain separate errors in `fit/family-errors.csv`. Native endpoint values were used directly; endpoint equilibrium diagnostics were not copied from a starting record.

The source-corrected packet supplies Böttinger 030/042/046 and Matin 009/019/016; newly declared Böttinger 051 uses raw row 51 at 313.15 K, 30 wt% and loading 0.508, preserving 0.0647 amine aggregate and 0.0483 carbamate. Its campaign declaration explicitly overrides the earlier membership loading exclusion. Jakobsen 011/022 retain raw rows 11/22, printed `loadNMR` 0.29/0.59, corrected CO₂-free fractions 0.2714274817259226/0.11583721405835971, and species/total-amine ratios. Their model pressure is the existing single-liquid packet convention, 101325 Pa. The exact requests, analytical feeds, source rows, admission and hashes are frozen in `fit/stage4-spec.json` and its input tables.

Start material, charge, carbon and source-mass checks pass, with all state predictions and raw residuals retained. The fit stops before endpoint replay, centered diameter/other-coordinate derivative checks, endpoint closure, or cost/start selection. The two byproduct-bearing Böttinger states and remaining corrected Jakobsen comparisons are unrun after the stop. Neither their absence nor the incomplete fit is treated as failed physics.

### Serialization defect and retained native values

The application runner assumed one `physical` result per coordinate. The Engine returns eleven parameter-target values for the seven coordinates: each size coordinate contributes segment, packing and Debye–Hückel diameters. A strict seven-to-eleven `zip` raises `ValueError` before the runner writes its normal incomplete-fit record. This is an application serialization defect; it does not change the separately retained native non-convergence or active bounds. The accepted correction boundary is the tied-coordinate result reader and physical-Jacobian dimensions. No correction or further model call has been made after the stop.

`fit/ion-speciation/A/returned-parameter-targets.json` records the exact eleven-to-seven correspondence. The source-coordinate values reconstructed from retained optimizer origins/scales agree with those native target values and the 0.88 diameter ties. `usable-budget-endpoint.json` preserves that vector for diagnosis only; it is not replay-qualified or selected. No complete `parameters.json` or stage-4 frozen selection is written.

### Kiepe evidence and unrun repeat test

The new wheel requalifies the unchanged stage-2 CO₂–water record. The following errors and `fit/kiepe-qualified-313.20-roots.csv` come only from that requalification, with its original 39 rows. They are not results for a new stage-3 fit. The twelve 313.20 K rows retain pressure, both phase densities/packing fractions, positive pressure-density derivatives and raw equilibrium residuals. No second 3a starting root family exists in this reordered attempt. A new model CO₂ critical-temperature calculation was unnecessary and did not run.

| Kiepe isotherm, K | Rows | Mean absolute relative error, % | Maximum, % |
|---|---:|---:|---:|
| 313.2 | 12 | 1.50120691 | 2.65909999 |
| 353.11 | 9 | 3.8260945 | 5.57751768 |
| 373.26 | 12 | 0.97261782 | 2.79977739 |
| 393.17 | 6 | 6.64561194 | 11.3361183 |

| Record or decision | Result |
|---|---|
| I₀ | Not selected: A non-convergence, four bounds, serialization defect |
| S₁ (3a/3b on I₀) | Unrun |
| I₁ (ion refit on S₁) | Unrun |
| Ion-coordinate and frozen-family movement test | Unavailable without complete I₀ and I₁ |
| S₂ | Unrun; repeat condition cannot be evaluated |
| Final precursor, replay and conditional mismatch | Unavailable |

The design requires a return to the owner before any additional start fit or stage. Neither bounds, iteration limits, observations, weights, starts nor the repeat rule were changed.

### Execution and remaining allowance

The initial ion-pair boundary entry is retained in `fit/entry-accounting.json`; its exit is in `fit/summary.json`. Pair charges including derived-record/density work are 50.514018720 CPU-s / 6.875057967 wall-s, leaving 2349.485981 CPU-s / 353.124942 wall-s in this pair. New fit-process charges exclude the separately recorded density work: 36.389388000 CPU-s / 6.433663257 wall-s. Qualification adds 11.251984 CPU-s / 11.278405983 s. These are execution charges, not elapsed conversational time.

Program cumulative charges are 1224.117881720 CPU-s / at least 438.579579950 active wall-s. Remaining program allowance is at most 142775.882118280 CPU-s / 21161.420420050 active wall-s. Prior 1162.351879 CPU-s / 420.426116 wall-s were charged once, including the already cumulative superseded stage-3 work. Earlier unmetered startup/verification overhead and bookkeeping-only inspections remain disclosed rather than assigned zero. The unsuccessful argument-parsing command executed no scientific call; its process startup was unmetered.

All model calls ran at `nice -n 10` with single-thread BLAS/OpenMP. The fit requested 32 native row workers on 32 CPUs; available memory was 15,347,884,032 bytes at the existing 256 MiB/worker estimate. Actual native worker count is not returned. A start used 0.663389 CPU-s / 0.666275 wall-s, B start 0.697842 / 0.697703, and A fit 34.715622 / 4.832730. No call was interrupted. Per-call wall limits were 60 s for assessments and 180 s for the fit. No scientific budget was exhausted.

This stopped conditional calibration and numerical verification requires the parent’s stop decision and independent delivered review. It supports no unique single-ion property, independent prediction, simultaneous optimum, parameter adoption or physical validation. No Engine edit, GitHub write, push, merge, additional worktree, subagent or preview-service action occurred. The worktree has no ignored literature shelf or journal preferences; the accepted design and retained source owners were used without a new literature judgment.

### Code accounting and verification

This block adds **37 gross executable lines**, removes 13, and uses 37/250 of its authorized ceiling. The conservative campaign charge is **535/900**, leaving 365 lines; 213 remain in this block. `fit/change-accounting.json` classifies the final code against `6c8d20073fd0e5fda8dd323a51f55551d12b7486`: 361 gross executable additions. The smaller classifier total does not replace the retained 498-line prior campaign charge. `change-accounting-block.json` records the distinction.

`fit_observations.py` adds explicit denominator species for native amount-ratio observations and transports multiple targets for each size coordinate. `fit_campaign.py` serializes diameter ties, records program/stage accounting, and retains full/free Jacobian diagnostics before an endpoint is eligible. The former late identification writer was removed. The old one-physical-value-per-coordinate assumption remains defective for tied native outputs, as disclosed above; the new fit path is incomplete and not qualified for another fit.

The completed checks are Python syntax, input/wheel hashes, exact target count/identity declarations, A/B starting size ties, four unchanged-record requalifications, five paired unloaded densities, both 26-target starting solves, and their material/charge/source-mass checks. No persistent test was added. Endpoint centered derivatives, closure/replay, byproduct/expanded comparisons and independent delivered review remain unrun after the stop.

### Notebook rendering

The notebook source was updated from retained values through CSE Summarize. `nice -n 10 bash analyses/render.sh mea_parameter_bundle/notebook.qmd` produced `analyses/_site/mea_parameter_bundle/notebook.html` with execution disabled. The new result text and table were checked in the T3 in-app browser at 1280×800; the inspected text fits the page and reports the stop and missing stages. No system browser or preview service was opened, started, stopped or restarted.

The broad `manuscript.py refresh` first lacked Snakemake on PATH; using the presentation interpreter documented in `analyses/README.md` reached a historical presentation job but that job failed with `ModuleNotFoundError: No module named MEA` in the worktree’s unpopulated default environment. The guarded notebook-only render succeeded without that unrelated presentation preparation. The home page was not refreshed. All three command logs are retained in `fit/`; rendering establishes no scientific claim and is outside numerical fit charges.

## Parent-authorized diagnosis and reader correction

After the initial stop, the parent authorized a 120 CPU-s / 120 wall-s diagnosis, the eleven-target reader correction, and two exact chemistry columns, with no fit or changed bounds/starts/iterations. The [diagnosis report](diagnosis-chemistry/README.md) supersedes the earlier statements that the reader remains uncorrected. It reports all eleven physical values, all 26 row and nine state cost/gradient contributions, exact nine-column matrices, source-unit chemistry gradients and projection angles. The corrected reader passes the exact retained failing-case comparison; no new fit exercised it.

The result supports strong local overlap between fixed R5 reference-level and the bound-active ion sensitivities: cosine 0.98923978 at A and 0.98765249 at iteration 40. Both nine-column matrices have rank 9, with condition numbers 175500.87 and 131178.52. R2’s pivot-preserving temperature direction is much weaker on these 20/40 °C rows and does not test its reference-level offset. The fixed zero reactive interactions were not varied. No unique physical cause or design change is selected.

The original non-convergence and four lower-bound stops remain. At iteration 40, projected gradient is 1.07738919×10⁻⁵ against 10⁻⁸, and cost is still falling by 3.50635×10⁻⁷ per last step. The native history does not retain intermediate active-bound membership; the initial zero and final four active bounds are known. No further fit or stage ran.

The two native Jacobian evaluations plus process overhead used 1.050963 CPU-s / 1.053779847 wall-s. With 64 CPU-s / 2 wall-s conservatively charged for short unmetered inspection/reader-check/algebra commands, diagnosis charges are 65.050963 CPU-s / 3.053779847 wall-s within 120/120. New cumulative program charges are **1289.168844720 CPU-s / at least 441.633359797 active wall-s**, leaving at most **142710.831155280 CPU-s / 21158.366640203 wall-s**. Prior unmetered overhead remains disclosed.

Final code accounting after the reader correction is **46/250 added executable lines for this block and 544/900 for the campaign**, with 204/356 lines remaining. The earlier 37/535 figures describe the initial build before the correction. `diagnosis-chemistry/change-accounting*.json` records the final tree; initial accounting remains history.
