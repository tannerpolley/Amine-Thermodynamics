# Route 2b: release tests pass; smaller fit interrupted, larger fit unrun

**Smaller d_V:** the lambda-0/start-A fit is interrupted after its aggregate-CPU sampler raises `ProcessLookupError`. No native fit result, parameter vector, convergence diagnostic, iteration count, projected gradient, cost or endpoint error returns. **Larger d_V:** both release tests pass, but its fit remains unrun because correcting the launcher requires executable changes and the continuation allows none. This is an execution failure, not evidence against the thermodynamic model or a nonconverged calibration vector.

The four release tests pass at start A and lambda 0/1. All 217 requested rows are Available on both branches; positive-weight matrices have 205 rows at lambda 0 and 217 at lambda 1. Mandatory rank is 14/14, augmented rank 16/16, and projected dispersion rank 2/2 in every case. Release evidence is committed in `ec60a2f`; the interrupted fit ran `b868f15`.

| Requested endpoint | Smaller d_V | Larger d_V |
|---|---|---|
| Fit outcome | Interrupted after launcher failure | Unrun pending code authority |
| Convergence, iterations, projected gradient | Unavailable: no native return | Unrun |
| Training cost by family | Unavailable | Unrun |
| Common-149 cost | Unavailable | Unrun |
| Kiepe errors by isotherm | No fit errors returned | Unrun |
| Active bounds and gradients | No endpoint; active set unavailable | Unrun |
| All 16 coordinates against the prior partial | Starts and historical values retained; no endpoint | Starts and historical values retained; no endpoint |
| Four Cp errors | No fit predictions returned | Unrun |
| Endpoint replay and derivative checks | Unrun: no converged endpoint | Unrun: no fit |

The prior Route 2 partial has common-149 cost **24.2811941137** after 81 iterations without convergence. Adopted **32.05668491** is historical context from different inputs and wheel. Neither fills a Route 2b endpoint or supports a new ranking. [Branch outcomes](branch-outcomes.json) retain explicit missing quantities rather than zero costs. All 16 old values and both declared starts remain in [coordinate-comparison.csv](coordinate-comparison.csv).

## Smaller branch continuation returned, 2026-10-16

The restored launcher returns normally and reaps the smaller native call: **6795.859259000 CPU-s / 1279.288005441 wall-s**, exit 0, no interruption. The fit reaches its native time limit at **53 iterations**, **54 residual / 47 Jacobian evaluations**, projected gradient **0.000110807132411** against 1e-8. Training cost is **196.86581561 → 36.7833961664**; common-149 cost is **23.0753630456**, a partial-iterate diagnostic against earlier **24.2811941137** and adopted **32.05668491** as historical context only. All **205/205 rows are Available**, full/free ranks are **16/16 and 9/9**. Bound activity is reported in the retained coordinate table; none of the hard stops is reached. Endpoint replay and derivative checks are not run because the fit has not converged. The returned native time-limit message covers an internal span; the complete call takes 79.288005441 s beyond the declared 1200 s native limit, below the unchanged 1320 s crash backstop.

[Reported fit values](smaller-dV/lambda-0-A-continuation/reported-results.json), [all targets and costs](smaller-dV/lambda-0-A-continuation/target-costs.csv), [family costs](smaller-dV/lambda-0-A-continuation/family-costs.csv), [all coordinates and gradients](smaller-dV/lambda-0-A-continuation/parameters-and-gradients.csv), [Kiepe isotherms](smaller-dV/lambda-0-A-continuation/Kiepe-isotherms.csv) and [four Cp values](smaller-dV/lambda-0-A-continuation/Cp.csv) retain the result. The whole smaller command charges **6796.09 CPU-s / 1279.52 wall-s** after upward rounding. Larger-branch execution remains authorized after this bounded partial; its remaining allowances and cumulative prior charge are updated without changing any scientific declaration.

## Orchestrator continuation decisions, 2026-10-16

The orchestrator authorizes deletion of live aggregate-CPU sampling and process-group handling, including the disappearing-process failure path. The launcher returns to the call lifecycle demonstrated by `4763f37`: Engine native `maximum_elapsed_time_seconds=1200`, crash backstop at 1320 s, normal child reaping, then aggregate CPU from `RUSAGE_SELF + RUSAGE_CHILDREN`. There is no live CPU enforcement. Measured CPU above 12000 s stops subsequent calls. The executable change must be net zero or negative, with at most 10 gross added lines within the campaign ceiling of 900.

The fit allowance increases by 12000 CPU-s, from 24000 to **36000 CPU-s**. The interrupted fit retains its conservative **12000 CPU-s** reservation; **24000 CPU-s** remain for the two authorized calls. Program entry remains **36657.498914 CPU-s**, including that reservation, against 144000 CPU-s. Program wall entry including the earlier owner-requested idle wait is at least **9809.316196 s**. Preparation, checking, reporting, presentation and commits reserve **100 CPU-s / 240 active wall-s** within the remaining release/reporting allowance. These decisions supersede the earlier zero-addition stop; historical failure files remain unchanged.

Execution remains lambda 0/start A, smaller then larger d_V, one fit each: 100 iterations, 1200 s native wall and 12000 CPU-s measured after normal reaping. Nonconvergence at a limit retains the partial record and permits the other branch; active bounds are reported. Unavailable rows, failed replay or derivatives, rank deficiency, excess measured CPU or code-limit failure stop further calls. A converged endpoint alone receives replay and derivative checks. No lambda 0.1, start B or assessments are authorized.

Launcher owner remains `scripts/fit_campaign.py::stage6_study`; its existing stage-6 fit/information callers keep the same declaration interface. The `/proc` CPU sampler, process-group setup/kill path, live sampling loop, sampling-only imports and per-process CPU resource limit are removed. The native fit wall limit and crash backstop remain. `completion-change-accounting.json`, base `79ea7bc`, measures **5 gross executable additions / 28 removals, net -23**. The conservative campaign gross charge becomes **857/900** (852 prior + 5); deletions do not recover earlier gross charges. Compilation and installed-wheel/input verification pass; all 12 installed Engine files match the pin. Free memory at preflight is 22.01 GB against the 8.59 GB estimate for 32 native workers. The full requested fit is the behavior check; passed release tests are not repeated.

## Orchestrator decision, 2026-10-16

The orchestrator authorized **180 s wall / 500 aggregate CPU-s per release derivative evaluation only**, inside the remaining **1079.724605 CPU-s** release/reporting allowance. This is a numerical execution limit; no coordinate, row, bound, scale, start, threshold or scientific declaration changes. A release evaluation reaching the revised wall limit stops without retrying. [release-180-spec.json](release-180-spec.json) records the decision and the 70 CPU-s / 120 active wall-s preparation/reporting/check/commit reserve. The original 60 s interruption remains retained separately.

The authorized fits are lambda 0/start A on smaller then larger d_V, one per passing branch: **100 iterations, 1200 s native wall, 1320 s crash backstop, 12000 aggregate CPU-s after normal reaping**. Bound activity is reported. Non-convergence at a limit stops that branch while the other branch remains authorized. Only a converged fit receives endpoint replay and derivative checks. No lambda 0.1, start B or assessments follow. The present stop is a launcher defect requiring executable changes, not a bound or non-convergence decision.

## Completed release tests under the revised limit

[Retained matrices, spectra and row values](release-180/release-tests.json) and [ranks and conditions](release-180/ranks-and-conditions.csv) establish numerical release readiness for these starts only. The cutoff is 1e-14 times the largest singular value and the condition limit is 10000; all starting coordinates are interior.

| Branch/A | Lambda | Positive-weight rows | Mandatory rank/condition | Augmented rank/condition | Projected dispersion rank/condition |
|---|---:|---:|---|---|---|
| smaller-dV-A | 0 | 205 | 14/14; 6421.24943 | 16/16; 9204.66513 | 2/2; 7.13401849 |
| smaller-dV-A | 1 | 217 | 14/14; 3554.0437 | 16/16; 6123.93805 | 2/2; 10.8100018 |
| larger-dV-A | 0 | 205 | 14/14; 5182.36717 | 16/16; 7682.71156 | 2/2; 7.21482051 |
| larger-dV-A | 1 | 217 | 14/14; 3342.29486 | 16/16; 5908.4496 | 2/2; 10.3597194 |

Both calls return normally, with no interruption: smaller 54.497663704 wall-s / 71.217846 reaped CPU-s, larger 55.463373719 wall-s / 72.404589 reaped CPU-s. Whole-command measurement is 143.89 CPU-s / 110.30 wall-s. The 12 installed Engine files and all declared inputs match [the continuation check](continuation-wheel-and-input-check.json). Wheel SHA-256 is `98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a`, merged Engine `84ca269dfa0c7068417a1c4c326acae276d4d965`. Python 3.13.14, NumPy 2.5.4 and SciPy 1.18.1 match the pin. These are numerical derivative/conditioning checks, not physical validation.

## Frozen declaration and engineering basis

The [owner decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6208172805) authorizes start A, lambda=0, on the two retained dielectric branches. The [release declaration](release-spec.json) has **16 coordinates**, with 14 mandatory columns followed by the two optional ion-dispersion columns. It retains the original A ion/chemistry start rather than the earlier partial endpoint. The [smaller](smaller-dV/start-parameters.json) and [larger](larger-dV/start-parameters.json) records differ only in the two authorized MEA dielectric coefficients.

| Quantity | Smaller d_V start | Larger d_V start |
|---|---:|---:|
| MEA d_V, L/mol | 0.2464540312088979 | 0.7309888238084122 |
| MEA d_T, K | 2436.4423007273617 | 1019.0786110170793 |
| CO2–water k_ij at 313.15 K | -0.046416901120577676 | -0.046416901120577676 |
| CO2–water reciprocal-temperature slope b, K | -35.66505220645838 | -35.66505220645838 |

The binary law remains $k(T)=k(313.15)+b(1/T-1/313.15)$. Its pivot and slope boxes/scales are respectively [-0.5,0.5]/0.01 and [-1000,1000] K/10 K. Bicarbonate–water has box [-0.5,1.0], with its original +0.5 start. All other coordinates, bounds, scales and starts are unchanged. Segment diameters retain the 0.88 packing/Debye–Hückel ties. R5's unshifted reference and the two 313.15 K pivot-preserving reaction-enthalpy shifts retain their separate declared meanings and one composed serialized correlation.

All **39 existing Kiepe pressure rows** are added once, with natural-log pressure residuals and weight 1/39. [added-rows.json](added-rows.json) preserves the source row identities, compositions, pressure units, isotherm order and observations. The existing continuation rule uses the preceding converged row on that isotherm at the same parameter record. Existing Kiepe neutral-domain declarations are reused for the native parameter record; this admits the retained 393.17 K source isotherm without altering common-row definitions. The declared objective has **205 positive-weight rows at lambda=0** and **217 at lambda=1**, including the unchanged common-149. These are declaration counts, not returned prediction counts.

The [coordinate comparison](coordinate-comparison.csv) retains all 16 original-partial values and both branch starts. Both branches have identical released-coordinate starts; only their fixed dielectric pair differs. The next two numeric columns are historical partial values and declared starts, respectively; there is no returned fit endpoint.

| Coordinate | Earlier 81-iteration partial | Declared A start, both branches |
|---|---:|---:|
| Carbamate–water k | -0.202719733667 | 0.134080741317 |
| Protonated MEA–water k | -0.152249129162 | -0.379554080066 |
| Bicarbonate–water k | 0.5 | 0.5 |
| Carbamate–protonated MEA k | -1 | -0.707285890215 |
| Protonated MEA–water slope, K | 36.9034558902 | -112.567750584 |
| Protonated MEA segment size, Å | 5.51743301647 | 3.563 |
| Carbamate segment size, Å | 5.8 | 3.5605 |
| Protonated MEA Born diameter, Å | 5 | 3.563 |
| Carbamate Born diameter, Å | 3.62897938162 | 3.5605 |
| R5 unshifted a_k, K | 2568.56004544 | 2677.91 |
| R2 enthalpy shift, J/mol | -10000 | 0 |
| R5 enthalpy shift, J/mol | -8392.06021931 | 0 |
| CO2–water k(313.15 K) | -0.0464169011206 | -0.0464169011206 |
| CO2–water slope b, K | -35.6650522065 | -35.6650522065 |
| Protonated MEA dispersion/k, K | 251.302802793 | 228.71 |
| Carbamate dispersion/k, K | 168.034884166 | 533.11 |

## Smaller-branch failure and containment

The fit uses the [frozen fit declaration](smaller-dV/fit-spec.json), original A start, nice 10, single-thread BLAS/OpenMP and 32 requested native workers. [Machine sizing](smaller-dV/lambda-0-A/machine.json) records **10460008448 available bytes** against **8589934592 bytes** for the declared 32-worker estimate. Engine does not return the actual worker count. The release differentiation declaration has no worker-count argument.

At launcher elapsed **767.885850080 s**, reading a disappearing `/proc/<pid>/stat` entry raises `ProcessLookupError` at `fit_campaign.py:96`. The sampler catches `FileNotFoundError` only. The exception exits the monitoring loop before `calls` is appended or a native endpoint is returned. [failure.json](smaller-dV/lambda-0-A/failure.json) and [summary.json](smaller-dV/lambda-0-A/summary.json) retain the traceback and exact stopping point. That summary's **264.837270 CPU-s** is incomplete parent/reaped-child usage before cleanup; its empty calls list does not mean the fit used no CPU.

After the exception, the Python launcher waits for its non-daemon child. The native owner and workers therefore continue outside the failed monitoring loop until containment. The owner PID **2287247**, its verified launcher parent **2287224**, and **31 descendant processes** are captured through kernel parent/child links. The native owner is stopped first; descendants are captured by PID/start tick and stopped, then those same verified processes are killed. [process-stop.json](smaller-dV/process-stop.json) records the identities and CPU snapshot; [the final process check](smaller-dV/process-stop-check.json) confirms no captured process remains active. No process is selected for termination by a shared environment variable or a broad command-line match.

All **31 captured descendants have separate process groups** from their native owner. Thus the existing process-group-only sampler also omits live native worker CPU until reaping, independently of the disappearing-process exception. The earlier disposable four-worker group check did not exercise this native worker arrangement. The aggregate CPU control is not demonstrated for native fits and must be corrected before further fits. No executable correction or rerun is made under the zero-addition instruction.

The whole command ends after **856.41 wall-s**, exit 1, with **319.13 measured CPU-s**. This measurement excludes unreaped native workers and is not the fit's aggregate CPU. The live descendant snapshot alone is **4667.83 CPU-s**, plus the owner's **54.23 CPU-s** (the owner is already included in whole-command usage). Exact final aggregate CPU and orderly worker reaping are unavailable after forced containment. The full **12000 CPU-s** interrupted-fit allowance is conservatively reserved; missing worker CPU is not assigned zero. No `native.json` or endpoint parameter record exists. Iterations, projected gradient, training family costs, common-149 cost, Kiepe isotherm errors, active-bound gradients and four Cp errors remain unavailable. Start-A release predictions are not substituted for fit predictions.

## Charges and code

[Continuation accounting](continuation-accounting.json) preserves the entry program charge **24443.598914 CPU-s / at least 3507.568996 active wall-s** and all prior reservations. The continuation charges **143.90 CPU-s / 110.31 wall-s** for the successful release command (rounded upward), **12000 CPU-s / 856.42 wall-s** for the interrupted fit (full CPU reservation and rounded-up measured wall), and **70 CPU-s / 120 active wall-s** for preparation, containment, reporting, presentation, checks and commits. This is **12213.90 CPU-s / at least 1086.73 active wall-s** for the continuation.

Cumulative program charge is **36657.498914 CPU-s / at least 4594.298996 active wall-s**, leaving at most **107342.501086 CPU-s / 17005.701004 wall-s** against 144000/21600. Earlier unknown overhead remains unknown. Fit allowance remaining is **12000 of 24000 CPU-s**; release/reporting remaining is **865.824605 CPU-s**. Remaining allowance does not authorize a correction or another native call.

Executable additions in this continuation are **0**. The retained earlier Route 2b implementation remains **40 additions / 17 removals** against `7dadd34`, and the campaign remains **852/900** conservative gross additions. Limits and declarations are in JSON. No scientific equation, optimizer, solver, persistent executable or test is added.

## Historical 60 s interruption, presentation and handoff

The original [60 s summary](release/summary.json), [timing](release/timing.json), [failure](release/failure.json) and [accounting](timing-and-program-accounting.json) remain unchanged. That attempt returned no matrix and reserved its full 800 CPU-s allowance after interruption. The new release matrices supersede its unavailable ranks without erasing its charge.

The existing [notebook](../../../../notebook.qmd) presents the passing release ranks and this bounded execution failure. The comparison contains a few scalar rank/condition values and no fit endpoint; a table states the available result without inventing a fit curve. No independent delivered review, parameter uncertainty, physical validation, parameter adoption or investigator promotion is claimed.

Further work requires a new executable-code allowance to handle disappearing processes, account for native descendants across their separate process groups, and stop/reap owned descendants if monitoring fails. The zero-addition instruction prevents attempting that correction now. The larger fit and any retry remain stopped pending an explicit decision. An automatic user-away answer is not authority. No subagent, preview-service action, push, merge or GitHub write occurs.

Static HTML renders of the notebook and home page both succeed with `analyses/render.sh` and `--no-execute`: **33.02 measured CPU-s / 31.61 wall-s**, within the charged 70/120 reporting reserve before the small checks and commits. [Presentation measurements and HTML value checks](continuation-presentation-checks.json) retain both outputs. Snakemake remains absent; no new workflow executable is installed. [Continuation checks](continuation-checks.json) verify unchanged scientific declarations, finite 217-row/16-coordinate release derivatives, frozen release hash, fit limits, no fit endpoint, inactive captured processes and zero executable diff since `2b632e1`.

The owner requested waiting until **2026-10-16 00:50 America/Denver** instead of changing the code scope. The interruptible idle wait lasted **5215.0172 s**, with no calculation or correction. Charging that wait conservatively adds no fit CPU and gives **at least 9809.316196 total wall-s**, including the **4594.298996 active wall-s** above, leaving at most **11790.683804 s** against the 21600-s program limit. The executable allowance remains zero; the wait supplies no authority to correct or resume the fits.
