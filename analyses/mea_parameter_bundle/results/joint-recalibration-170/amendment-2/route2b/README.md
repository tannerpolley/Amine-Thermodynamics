# Route 2b: four release tests pass; fits pending

Both dielectric branches pass the enlarged-coordinate release tests at start A, lambda 0 and 1. Mandatory rank is 14/14, augmented rank 16/16 and projected dispersion rank 2/2 in all four tests. All 217 rows return Available on each branch. Neither branch has a new fit yet. The first historical start-A derivative evaluation, on the smaller-d_V branch, reaches the inherited **60 s non-fit wall guard** before returning its Jacobian. It is killed after **60.057906468 s**, with exit code -9. All ranks and condition numbers are unavailable; no conditioning or rank conclusion follows. The required release-test stop prevents the larger-branch evaluation and both fits. This is an execution non-result, not calibration evidence or a physical limitation.

| Requested endpoint | Smaller d_V | Larger d_V |
|---|---|---|
| Convergence, iterations, projected gradient | Unrun | Unrun |
| Training cost and family contributions | Unavailable | Unavailable |
| Common-149 cost | Unavailable | Unavailable |
| Active bounds and gradients | No endpoint | No endpoint |
| Kiepe errors by isotherm | Unevaluated | Unevaluated |
| Four Cp errors | Unevaluated | Unevaluated |
| Endpoint coordinates and movements | No endpoint | No endpoint |
| Replay and derivative checks | Unrun; no converged endpoint | Unrun; no converged endpoint |

The earlier Route 2 partial has common-149 cost **24.2811941137**, after 81 iterations without convergence. The adopted record's **32.05668491** is a retained reference, with different inputs and wheel; neither number supplies a Route 2b endpoint or ranking. Prior partial parameters, bounds, gradients and Cp remain in [the original report](../route2/README.md), unchanged.

## Authorized continuation: orchestrator decision, 2026-10-16

The orchestrator authorized **180 s wall / 500 aggregate CPU-s per release derivative evaluation only**, within the remaining **1079.724605 CPU-s** release/reporting allowance. This changes numerical execution limits only; all 16 coordinates, rows, bounds, scales, starts, release thresholds and scientific claims remain as declared. An evaluation that reaches the revised wall limit stops the continuation without retrying. The new [release declaration](release-180-spec.json) retains this authority and reserves 70 CPU-s / 120 active wall-s for preparation, reporting, checks and commits. The original 60 s attempt remains below as historical execution evidence.

Release tests run at start A, at lambda 0 and 1, on smaller d_V followed by larger d_V. Each branch that passes is eligible for one lambda-0/start-A fit, capped at 100 iterations, 1200 native wall-s (1320 s crash backstop), and 12000 aggregate CPU-s after normal reaping. Non-convergence stops that branch with its partial record; bound activity is reported. Only a converged fit proceeds to endpoint replay and derivative checks. No lambda-0.1 fit, start B or assessments are authorized.

## Completed release tests under the revised limit

[Retained matrices, spectra and row values](release-180/release-tests.json) and [ranks and conditions](release-180/ranks-and-conditions.csv) establish numerical release readiness for these starts only. The cutoff is 1e-14 times the largest singular value and the condition limit is 10000; all starting coordinates are interior.

| Branch/A | Lambda | Positive-weight rows | Mandatory rank/condition | Augmented rank/condition | Projected dispersion rank/condition |
|---|---:|---:|---|---|---|
| smaller-dV-A | 0 | 205 | 14/14; 6421.24943 | 16/16; 9204.66513 | 2/2; 7.13401849 |
| smaller-dV-A | 1 | 217 | 14/14; 3554.0437 | 16/16; 6123.93805 | 2/2; 10.8100018 |
| larger-dV-A | 0 | 205 | 14/14; 5182.36717 | 16/16; 7682.71156 | 2/2; 7.21482051 |
| larger-dV-A | 1 | 217 | 14/14; 3342.29486 | 16/16; 5908.4496 | 2/2; 10.3597194 |

Both calls return normally, with no interruption: smaller 54.497663704 wall-s / 71.217846 reaped CPU-s, larger 55.463373719 wall-s / 72.404589 reaped CPU-s. Whole-command measurement is 143.89 CPU-s / 110.30 wall-s. [Continuation accounting](continuation-accounting.json) conservatively charges 213.90 CPU-s / at least 230.31 active wall-s including the 70/120 reporting reserve; cumulative program charge is 24657.498914 CPU-s / at least 3737.878996 active wall-s. Release/reporting has 865.824605 CPU-s remaining; both fits retain their 24000 CPU-s allowance. These are numerical derivative/conditioning checks, not physical validation.

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

The [coordinate comparison](coordinate-comparison.csv) retains all 16 original-partial values and both branch starts. Both branches have identical released-coordinate starts; only their fixed dielectric pair differs. The next two numeric columns are historical partial values and declared starts, respectively; there is no new endpoint.

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

## Historical 60 s release evaluation and exact stop

The installed 12 Engine files and every declared input match [the wheel/input check](wheel-and-input-check.json). Wheel SHA-256 is `98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a`, merged Engine `84ca269dfa0c7068417a1c4c326acae276d4d965`; Python 3.13.14, NumPy 2.5.4 and SciPy 1.18.1 match the pin. Declaration/cap implementation commit is `44ca579`; the interrupted calculation ran that commit. Its exact command uses the existing `tmp/amendment-2-84ca269d/venv/bin/python`, `PYTHONPATH=src`, positional declaration/output arguments, `--case stage6 --operation information`, `nice -n 10` and single-thread BLAS/OpenMP.

One exact derivative evaluation was intended to supply both lambda=0 and 1 weighted/scaled matrices for each branch. Full/free mandatory rank and conditioning, augmented free conditioning and the two projected dispersion columns retain the original cutoff 1e-14*s_max and condition limit 1e4. No matrix returns, so no release test passes or fails its numerical threshold.

| Branch/start | Lambda | Matrix rows declared | Mandatory rank/condition | Augmented rank/condition | Projected dispersion rank/condition |
|---|---:|---:|---|---|---|
| Smaller/A | 0 | 205 | Unavailable: interrupted evaluation | Unavailable | Unavailable |
| Smaller/A | 1 | 217 | Unavailable: same interrupted evaluation | Unavailable | Unavailable |
| Larger/A | 0 | 205 | Unrun after stop | Unrun | Unrun |
| Larger/A | 1 | 217 | Unrun after stop | Unrun | Unrun |

[summary.json](release/summary.json), [timing.json](release/timing.json) and [failure.json](release/failure.json) retain the stop. No native result file exists and the parent did not receive partial derivatives. The log does not identify whether interruption occurred during row construction/continuation or differentiation. There is no unavailable-row diagnostic, rank deficiency or evidence of a thermodynamic solve failure. No attempt was made to infer missing derivatives, reuse the old 14-column matrix, raise the guard, split the calculation or continue to fitting.

## Historical charge, aggregate CPU enforcement, memory and code

The launcher gives its own child a separate process group, sums Linux process CPU for that group including native workers and reaped descendants, and checks every 0.05 s. A one-full-machine-CPU-second margin precedes the hard allowance. Normal returns are charged from process-plus-reaped-worker resource usage. On forced termination, the full call allowance is conservatively reserved rather than assigning unknown unreaped-worker CPU zero. The final guard also includes launcher CPU and tolerates a process group already gone at termination; these final refinements did not rerun the stopped scientific evaluation. [The original guard check](aggregate-cpu-check.json) verifies a normally reaped four-worker pool and aggregate termination. [The final guard check](aggregate-cpu-final-check.json) verifies the pool-plus-launcher measurement and one group termination. These disposable calculations evaluate CPU control only.

The release call's reaped aggregate CPU is **78.904605 s**, including launcher monitoring. The sampled process-group CPU is **59.96 s**. The [whole-command measurement](release-command-time.txt) is **79.17 CPU-s / 60.33 wall-s**, rounded to 0.01 s. The guard did not reach its **800 CPU-s** allowance; the 60 s wall limit stopped the call. [Machine sizing](release/machine.json) records **19,659,259,904 available bytes**, **32 requested workers** and **8,589,934,592 bytes** for their declared memory estimate. Engine does not return actual worker count. The non-fit differentiation declaration has no worker-count argument; the requested count is reserved for subsequent native fits, which never launch.

[Program accounting](timing-and-program-accounting.json) conservatively charges **920.275395 CPU-s / at least 180.34 active wall-s** for this task: 79.18/60.34 rounded-up whole-command charges; **721.095395 CPU-s** additional interrupted-worker reservation to preserve the full 800 s call allowance; and **120 CPU-s / 120 wall-s** preparation/reporting/presentation/check/commit reserve. That reserve includes the original 60 s preparation reserve once, both small CPU-control checks and the [argument-parsing failure](release-setup-time.txt), which performed no thermodynamic calculation. Subsequent measured presentation/check overhead must fit this reserve.

Cumulative program charge is **24443.598914 CPU-s / at least 3507.568996 active wall-s**, from the supplied 23523.323519/3327.228996 prior charge. Shared remainder is at most **119556.401086 CPU-s / 18092.431004 wall-s**. The 2000 CPU-s release/reporting allowance has **1079.724605 CPU-s** remaining; all **24000 fit CPU-s** remain unused. Earlier unknown overhead remains unknown. Actual measured command CPU and the conservative reservation are both disclosed; a reservation is not measured consumption.

Executable additions against `7dadd34` are **40**, removals **17**, across `fit_campaign.py` and `fit_observations.py`: aggregate CPU enforcement and normal/forced-reap charges; declaration-sized stage-6 rank/row checks; 32-worker memory sizing; and returning the existing Kiepe-domain parameter declaration. No scientific equations or solvers are implemented locally. The task is at **40/40**; the campaign is at **852/900** conservative gross additions. JSON files retain declarations and evidence. No executable file is hidden in a text extension. Final [change accounting](change-accounting.json) records the categories.

## Presentation and review

The earlier [notebook](../../../../notebook.qmd) records the 60 s interruption; it will be refreshed with this continuation after its authorized branch runs. The previous presentation-only refresh found no `snakemake` in this environment; static rendering through `analyses/render.sh` remains available without model execution or preview-service action. This continuation has no independent delivered review or investigator promotion. No new executable lines, subagents, push, merge or GitHub writes are authorized.
