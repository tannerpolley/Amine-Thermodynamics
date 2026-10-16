# Route 2: graceful partial return at the native time limit

**No completed Route 2 comparison record is available.** The unchanged lambda=0 start A rerun returns a usable partial vector after **29 iterations**, with training cost **196.865136591 → 42.4903033067**, **29 residual / 17 Jacobian evaluations**, and no trial failures. All **166 requested predictions are Available**. The native status is `limit_reached`, with message `Maximum solver time reached. Total solver time: 1.202227e+02 >= 1.075647e+02.`. Five free coordinates are active at bounds. No B or lambda=0.1 fit, replay, derivative or assessment call follows this stop. The primary lambda=0.1 common-149 metric remains unavailable.

The [partial record](lambda-0/F1/A/rerun-1/incomplete-fit.json), [native return](lambda-0/F1/A/rerun-1/native.json), [usable partial vector](lambda-0/F1/A/rerun-1/usable-budget-endpoint.json) and [iteration history](lambda-0/F1/A/rerun-1/iteration-history.csv) retain the values. The vector is incomplete calibration evidence, not a comparison endpoint, adopted parameter set or physical validation. The fit does not establish a limitation of the equation of state. Independent delivered review and any further scientific execution decision belong to the parent.

## Launcher correction and actual return

The existing `fit_campaign.py:stage6_study` owns the correction: native `maximum_elapsed_time_seconds=300` remains unchanged; the outer crash backstop is **420 s**, reserved before launch. CPU is measured after normal owner reaping, and an aggregate value above **3000 CPU-s** stops the sequence after return. This does not enforce aggregate CPU during execution. The same owner already retains status, iterations, residual/Jacobian counts, cost/time histories, projected gradient and bounds. No scheduler or Engine change is added.

[The launcher check](launcher-check.json) confirms a disposable owner returning beyond its simulated native deadline is reaped normally and its descendant CPU is recovered. Wheel SHA-256 is `98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a`; all **12 installed Engine files** match. Engine merged main is `84ca269dfa0c7068417a1c4c326acae276d4d965`. The real rerun uses nice 10, single-thread BLAS/OpenMP, and **32 requested native workers**, with **17.919 GB** available at launch. Engine does not return its actual worker count.

The real owner returns with **exit code 0, interrupted=false**, after **334.034949113 wall-s / 2115.811199 CPU-s**. The whole command uses **334.269446354 wall-s / 2116.045215 CPU-s**. The aggregate fit CPU margin is **884.188801 CPU-s**. Native solver time is bounded by its own stopping checks; the complete call exceeds 300 s by **34.034949113 s**, including work outside the reported iteration spans and return/cleanup. No native limit was raised, and the 420 s backstop did not fire. The driver then exits 1 on the required non-convergence/bound stop; that traceback is distinct from the native owner's graceful return. Host load at return is 12.7534 / 11.2852 / 8.83154 over 1/5/15 minutes.

## Partial numerical diagnostics and stops

The last projected gradient norm is **5.48891531689**, against the declared **1e-8** gradient tolerance. Full weighted/scaled rank is **14/14**, condition **11468.4807697**. Excluding the five native bound-active columns gives free rank **9/9**, condition **733.531580929**. The native covariance status is `not_converged`; no conditional uncertainty is asserted. Reconstructing one half the sum of squared returned weighted residuals gives **42.490303306668636**, exactly the reported final cost. This arithmetic check is not a serialization replay, derivative test or physical assessment.

| Active coordinate | Physical bound | Side |
|---|---:|---|
| pair/bicarbonate-anion/water/k_ij | 0.5 | upper |
| pair/carbamate-anion/protonated-monoethanolamine/k_ij | -1 | lower |
| component/protonated-monoethanolamine/born_diameter | 5 | upper |
| component/carbamate-anion/born_diameter | 2 | lower |
| reaction:R2:enthalpy_shift | -10000 | lower |

The segment-size/packing ties and ordinary native physical quantities remain in the full serialized partial vector. R5's unshifted a_k is **2839.113225350851 K**; R2/R5 enthalpy shifts are **-10000 / -5501.50839734298 J/mol** at the **313.15 K** pivot. These are partial fit quantities, with no endpoint identification claim.

The sequence stops on non-convergence and active bounds. After charging this rerun and conservative reporting overhead, less than 3000 CPU-s remains in Route 2 even before presentation, so another full per-fit CPU reservation also cannot fit. Limits, bounds, starts and weights remain unchanged. No additional fit is authorized by this record.

## Native cost and time history

Entry zero is the start. Later entries include rejected trial costs; the returned vector's cost is the final entry. These native durations are not total call wall time. [The CSV](lambda-0/F1/A/rerun-1/iteration-history.csv) owns the exact values. The installed scientific plotting backend (`matplotlib`) is absent from the pinned venv and system interpreter; no plot was generated or dependency installed.

| Native entry | Training cost | Native entry seconds |
|---:|---:|---:|
| 0 | 196.865136591 | 0.000029087 |
| 1 | 160.313433385 | 18.194932938 |
| 2 | 151.69221747 | 18.022783041 |
| 3 | 127.332965623 | 17.733698845 |
| 4 | 106.438857504 | 17.562413216 |
| 5 | 131.665509609 | 1.980744123 |
| 6 | 149.069478284 | 1.758784056 |
| 7 | 211.633623004 | 1.758696795 |
| 8 | 167.684903431 | 1.823529005 |
| 9 | 48.7598904954 | 17.652109861 |
| 10 | 46.5776643357 | 17.345985889 |
| 11 | 46.6188243024 | 1.828355074 |
| 12 | 45.5157495778 | 17.216112852 |
| 13 | 44.7233705379 | 17.224885941 |
| 14 | 44.1679011816 | 17.473483801 |
| 15 | 61.9228497447 | 1.879843950 |
| 16 | 64.4241125695 | 1.809130907 |
| 17 | 76.326136814 | 1.796185970 |
| 18 | 45.1845637083 | 1.863045931 |
| 19 | 44.0856776867 | 17.510129929 |
| 20 | 146.113473871 | 1.935956001 |
| 21 | 758.01836341 | 1.936848879 |
| 22 | 1792.4989814 | 1.850243092 |
| 23 | 43.8538896068 | 23.655389071 |
| 24 | 43.3517208783 | 18.431669235 |
| 25 | 44.5389295941 | 1.887282133 |
| 26 | 43.1406292151 | 17.980966091 |
| 27 | 42.8720660911 | 17.588671923 |
| 28 | 42.700010686 | 17.379419088 |
| 29 | 42.4903033067 | 17.576105118 |

## Release tests


All matrices are native residual derivatives multiplied by the declared square-root observation weights, in scaled optimizer coordinates. The cutoff is 1e-14 times the largest singular value; the declared condition limit is 10000. Source-increasing R5 a_k has the opposite sign to its native coefficient column; rank and condition are unchanged by that sign. Starting bicarbonate-water is exactly +0.5 for A/B, and B mutual interaction is exactly -1. Those columns alone are excluded from the free-matrix tests; the coordinates remain free in the fits.

| Start | Density weight | Rows | Mandatory free rank | Condition | Augmented free rank | Condition | Projected dispersion rank | Condition |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 0 | 166 | 11/11 | 4243.33872941 | 13/13 | 7804.89559687 | 2/2 | 10.10168821 |
| A | 1 | 178 | 11/11 | 3076.25475378 | 13/13 | 3491.17755113 | 2/2 | 8.07274519 |
| B | 0 | 166 | 10/10 | 2132.21089915 | 12/12 | 6468.29576964 | 2/2 | 14.66806763 |
| B | 1 | 178 | 10/10 | 1543.86275706 | 12/12 | 2296.28558963 | 2/2 | 5.65005523 |

Both dispersion origins are interior. Both dispersions are therefore released together with all 12 mandatory coordinates for the same branch/problem at every fitted density weight. Full singular spectra, weakest directions, active columns, exact unweighted columns and weighted matrices are in [release-tests.json](release-tests.json) and the `information/A` and `information/B` files. The two actual derivative evaluations each include all 178 requested rows; positive-weight subsets give 166/178 rows at lambda=0/1. Every starting row is available. The lambda=1 calculation is an information check, not a fit.


## Matched fits and report availability

| Density weight | Start | Attempt | Complete endpoint | Common-149 comparison cost |
|---|---|---|---|---|
| 0 | A | Original interrupted attempt; graceful rerun stops at native time limit, 29 iterations | None; partial retained | Unavailable |
| 0 | B | Not launched after stop | None | Unavailable |
| 0.1 | A | Not launched after stop | None | Unavailable |
| 0.1 | B | Not launched after stop | None | Unavailable |

No lower-training-cost complete A/B record can be selected. The partial **42.4903033067** is whole-training cost, not a common-149 comparison metric. [endpoints.csv](endpoints.csv) retains all four dispositions.

| Required report item | Retained evidence or unavailability |
|---|---|
| common-149 cost/contributions | No completed comparison records; both exact starting values retained; no primary lambda=0.1 metric |
| pressure/species family errors | Starting values only; no fitted records |
| Vinjarapu/Arcis heat errors | Eight starting Vinjarapu heats available per start; Arcis unrun |
| pooled Jakobsen/restored target errors | All 13 added starting rows available; no fitted records |
| all 103 densities by seven groups | 12 loaded starting densities per start available; remaining 91 and endpoint densities unrun |
| four Cp values and proxy/enthalpy checks | Four starting Cp values per start available; proxy and enthalpy verification unrun |
| direct C5 requests | Unrun; no endpoint; absorber evidence unchanged |
| Kiepe isotherm assessment | Unrun for Route 2; existing unchanged-binary qualification remains separate |
| weighted/scaled ranks and spectra | Four start/weight checks and returned partial full/free matrices and spectra available; no complete endpoint |
| active bounds and parameter movements | Partial vector and five active bounds retained; no completed fit |
| A/B cost and vector dispersion | Starting values retained; fitted 1e-6 relative-cost diagnostic unavailable |
| CPU/wall/iterations/work counts | Graceful partial: 29 iterations, 29 residual and 17 Jacobian evaluations; full native cost/time histories and aggregate CPU retained |
| secondary union score and six Kim heats | Unrun: union not evaluated, six intervals not qualified, s_H not frozen |
| fixed-record pressure/temperature/concentration and Wagner | Unrun; no comparison record |
| fixed-record corrected Jakobsen, 14 Arcis and 28 Hajj | Unrun; starting Jakobsen ratios are not fixed-record endpoint assessments |
| gas-root falsifier | Unrun; no physical-eligibility conclusion |
| 73-point flash family | Unrun; zero attempted points; no passed/failed/unresolved point classification |
| water and complete serialization replay | Four unchanged-record qualification checks remain passed; new endpoint replay unavailable |

The gas-root falsifier and the 73-point flash family have **zero attempted points** for a Route 2 comparison record. No physical-eligibility, stability, secondary-union or Kim-heat score is inferred. No missing quantity receives zero score.

## Starting values, separated from incomplete fitted results


| Start | Common-149 cost | Pressure contribution | Species contribution | Vinjarapu contribution | Pressure mean absolute relative error, % | Species mean absolute relative error, % | Vinjarapu RMSE, kJ/mol CO2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 160.863262274 | 24.051711172 | 22.248462154 | 114.563088949 | 27.662866 | 8.183326 | 18.097837 |
| B | 882.766472292 | 523.632083924 | 316.441430522 | 42.692957846 | 66.902029 | 33.444708 | 11.027447 |

These are the declared source-chemistry, seed-ion starting predictions, not fit endpoints or the primary comparison metric. The original 149 row identities and weights match exactly. [starting-targets.csv](starting-targets.csv) retains all 178 values at each start; [starting-density.csv](starting-density.csv), [starting-Cp.csv](starting-Cp.csv), and [starting-Jakobsen.csv](starting-Jakobsen.csv) retain the corresponding units, errors and bases. Density is kg/m3; native Cp is J/(mol-feed K), with the source kJ/(kg K) conversion retained separately. No endpoint density, Cp, Arcis, Kiepe or C5 assessment is inferred from these starts.


## Inputs, charges and code

Authority is [amendment 2](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6204801680), sections 4–6, and the parent launcher/rerun decision of 2026-10-16. Both the live issue and the binding local design were read. CO2–water k_p=-0.046416901120577676 and b=-35.66505220645838 K, CO2 dispersion/k=169.21 K, shared smaller d_V=0.2464540312088979 L/mol and d_T=2436.4423007273617 K remain fixed. Both corrected Jakobsen feeds are 27.14274817 wt%, with pooled inorganic-carbon targets. The declared scientific inputs, starts, 14 coordinates, weights, 40 iterations and 300 s native time limit are unchanged; only prior-accounting fields differ in the frozen rerun declaration.

[timing-and-program-accounting.json](timing-and-program-accounting.json) owns the current measured/lower-bound and conservative cumulative charges, including separately measured presentation.

| Charge | Recorded CPU plus conservative overhead, original missing workers excluded / CPU-s | Conservative CPU reservation total / CPU-s | Active wall / s |
|---|---:|---:|---:|
| Route 2 | 2775.451684000 | 12089.434501256 | 999.673608383 |
| Shared program | 5042.986821720 | 14356.969638976 | at least 1702.437960510 |

Remaining Route 2 allowance is **2910.565498744 CPU-s / 1100.326391617 wall-s**; shared program remaining is **129643.030361024 CPU-s / at most 19897.562039490 wall-s**. Route 2 remains inside 15000/2100 and the shared program inside 144000/21600 CPU/wall seconds. The new charge is the measured full rerun command plus **60 CPU-s / 60 wall-s conservative preparation, probe, arithmetic/checks, report and commits**, plus separately measured presentation **43.919280000 CPU-s / 39.928467183 wall-s**, each once. Native call CPU is a subset of command CPU and is not charged twice.

The standard presentation refresh fails because `snakemake` is absent. Both guarded HTML renders succeed, with execution disabled, at `analyses/_site/mea_parameter_bundle/notebook.html` and `analyses/_site/index.html`. No preview service is touched.
 The [pre-rerun accounting](timing-before-rerun.json), [original interrupted record](lambda-0/F1/A/incomplete-fit.json) and [wall-limit diagnosis](diagnosis-wall/README.md) remain retained. Original missing worker CPU stays reserved at the conservative upper bound; the complete rerun measurement never erases it. Earlier unmetered overhead remains disclosed; program active wall remains a lower bound.

The correction adds **6 executable lines and removes 3**, charged without credit: **185/200** part-2 gross additions and **810/900** conservative campaign gross additions. [code-accounting.json](code-accounting.json) and [change-accounting.json](change-accounting.json) retain the accounting. No persistent test, local optimizer, local equation of state or second fit owner is added. The existing notebook is refreshed from retained values only. No Quarto preview service action, subagent, push, merge or GitHub write occurs.
