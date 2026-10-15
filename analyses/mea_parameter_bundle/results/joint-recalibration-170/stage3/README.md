# Stage 3: qualified wheel and unavailable start B

Engine main `0bec2bdf42e31bf37e8d4679169c8174b580408f` passes all four unchanged-record requalification comparisons. Stage 3a stops before either fit: start A solves all 195 targets, while the declared cold calculation for start B cannot return `kiepe-313.20-13`. The parent-authorized [diagnosis](diagnosis-start-B/diagnosis.md) subsequently reaches that exact B row with the original vapor declaration by warming from row 12: pressure 5.50380950 MPa, phase densities 54014.52 / 3100.30 mol/m³. The cold failure is numerical, not evidence of an absent vapor branch. No stage-3 endpoint is selected. Stage 3b and stage 4 have not run; stage-4 inputs cannot be frozen.

The result is numerical verification of the wheel replays and conditional assessment of the declared starting records. It is not a completed calibration, physical validation, a unique parameter determination or evidence that the model cannot fit these observations. Independent delivered review remains with the parent.

## Basis and frozen inputs

The binding design is [#170 part 1, sections 1 and 3](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6158000594), [part 2, sections 8–10](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6158000919), the [pivot decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6156407756), and the superseding [slope decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6158787639). The live issue and these comments were read; the live stage-3 text matches the supplied local design. The issue was rechecked on 15 October 2026; its last update remains 14 October 2026, 01:53:43 UTC.

The published wheel SHA-256 is `a974c0e0c1d1049ffd144c003815a47f313820c5c3065aa395faa0a58e70a60d`. It was installed in a fresh `tmp/stage3/venv`, with Python 3.13.14, NumPy 2.5.4 and SciPy 1.18.1. Each qualification declaration verifies the installed Engine files against the wheel bytes. No Engine source checkout is imported.

The unchanged stage-2 MEA–water A and CO₂–water slope B records are identified by `../stage2/frozen-inputs.json`. The latter supplies the stage-3 reference record, retaining the adopted water, refreshed association, source chemistry and provisional ion assumptions. Its CO₂ dispersion is exactly 169.21 K and its unshifted R5 coefficient is exactly 2677.91 K, matching start A.

`stage3a-spec.json` freezes the declaration used for the attempted calculation. Its input hashes bind the existing source owners, both generated stage-3 tables and the preceding frozen record. The generated tables are `data/input/fit-campaigns/joint-recalibration-170-stage3-rows.json` and `joint-recalibration-170-stage3-requests.json`, relative to this analysis. They retain 25 pressure targets, 131 positive species targets at 44 states, and every one of the 39 Kiepe rows. No target or denominator was changed after a solve.

The four coordinates are CO₂ dispersion (160–190 K, scale 5 K), CO₂–water interaction at 313.15 K (−0.5 to 0.5, scale 0.01), reciprocal-temperature slope (−1000 to 1000 K, scale 10 K), and R5 reference coefficient (2400–3000 K, scale 80 K). Native natural-log residual weights are respectively 1/[25(ln 10)²], 1/[131(ln 10)²] and 1/39 for the pressure, species and Kiepe families. These are declared engineering weights, not measurement uncertainties.

| Start | CO₂ dispersion, K | CO₂–water interaction | Slope, K | R5 reference coefficient, K |
|---|---:|---:|---:|---:|
| A | 169.21 | −0.046416901120577676 | −35.66505220645838 | 2677.91 |
| B | 173.44025 | −0.046416901120577676 | −35.66505220645838 | 2597.91 |

## Requalification

The declared limits are relative objective difference ≤10⁻⁸ and absolute weighted-row difference ≤10⁻⁸. The comparison record uses the full-precision retained values; the rounded numbers in the task are descriptive. The existing `fit_campaign.py --operation replay` path evaluates that record. Water and binary replays call the existing `water_assessment` and `stage2_native` owners with new wheel declarations.

| Unchanged record | Retained cost | New-wheel cost | Relative cost difference | Maximum weighted-row difference | Result |
|---|---:|---:|---:|---:|---|
| Adopted water, 63 objective targets | 0.3883034271799937 | 0.3883034271803113 | 8.18×10⁻¹³ | 4.76×10⁻¹³ | Pass |
| MEA–water A, 53 fitted and 2 assessment targets | 91.84540850646353 | 91.84540850646385 | 3.56×10⁻¹⁵ | 2.70×10⁻¹¹ | Pass |
| CO₂–water slope B, all 39 rows | 0.026481760450542256 | 0.02648176045053506 | 2.72×10⁻¹³ | 1.59×10⁻¹³ | Pass |
| Current comparison record, 149 common and 14 Arcis targets | 32.05668490872888 | 32.056684908771295 | 1.32×10⁻¹² | 3.65×10⁻¹⁰ | Pass |

Water retains all 42 heat-capacity and 39 saturation states; every heat-capacity enthalpy-difference check passes. The current comparison record gives pressure mean absolute relative deviation 13.814747342834215%, species 7.891434570808665%, Vinjarapu heat root mean square error 2.1265722968041008 kJ/mol and Arcis 8.364420937930037 kJ/mol. Its parameter SHA-256 remains `66ff7715958e9d22e77bd129faf7f67822204e3285b50993bf3f67d72c3b9778`.

Exact rows, comparisons, declarations, verified input identities and timings are retained in `qualification/`. Differences in the Engine's diagnostic wording are retained separately from comparisons of numerical targets and their unchanged definitions.

## Start qualification and stopping point

Start A returns all 195 predictions. Its complete objective is 0.29167170313733287. Maximum absolute raw equilibrium residual is 1.0800249583553523×10⁻¹²; minimum returned phase pressure-density derivative is 563.8378236842773 Pa/(mol/m³); the minimum returned reduced-Hessian eigenvalue is zero. Material, charge and source-mass checks are retained in `co2-dispersion-r5-reference/A/start-balances.json`.

| Family | Declared targets | A evaluated | A family cost | A mean absolute relative deviation, % | B evaluated | B family cost | B mean absolute relative deviation, % |
|---|---:|---:|---:|---:|---:|---:|---:|
| Reactive pressure | 25 | 25 | 0.2505838849016584 | 58.86249443589496 | 25 | 0.19276091080813593 | 57.342726587441206 |
| Species | 131 | 131 | 0.04040879873694283 | 73.04228518758033 | 131 | 0.028961725686077765 | 56.910339038867534 |
| Kiepe pressure | 39 | 39 | 0.0006790194987316682 | 2.666523563690128 | 11 | Unavailable for the full family | Unavailable for the full family |

These are starting-record comparisons, with no fitted error change. The incomplete B Kiepe subset is not assigned a 39-row score or complete objective.

| Kiepe isotherm, K | A rows | A mean / maximum absolute relative error, % | B available / declared |
|---|---:|---:|---:|
| 313.20 | 12 | 1.501207 / 2.659100 | 11 / 12 |
| 353.11 | 9 | 3.826095 / 5.577518 | 0 / 9 |
| 373.26 | 12 | 0.972618 / 2.799777 | 0 / 12 |
| 393.17 | 6 | 6.645612 / 11.336118 | 0 / 6 |

`kiepe-start-errors.json` owns the full-precision isotherm values.

At B, `kiepe-313.20-13` has temperature 313.20 K, observed total pressure 9,231,900 Pa and liquid feed CO₂/water fractions 0.02481/0.97519. The declared vapor composition guess is CO₂/water 0.99/0.01. The Engine returns `CentralSolveUnavailable`, `LOCAL_INFEASIBILITY`, raw residual 0.0050988359807841097 against the 10⁻¹⁰ row tolerance after 31 iterations. It returns no pressure prediction for this row. The remaining 27 Kiepe rows are unattempted. `start-qualification.json` names every unavailable and unattempted row; the partial B predictions preserve the 167 available values and the failed row.

Both phase densities, compositions, pressure-density derivatives and raw equilibrium residuals are retained for the available Kiepe start rows, including the 313.20 K high-pressure rows preceding the failure. A's returned roots pass the declared local checks. B's unavailable row prevents qualification of the full declared vapor branch at that start. This observation alone does not establish a critical boundary, global phase stability or a physical absence of equilibrium.

Neither fit was launched. Endpoint costs, full/free ranks, condition numbers, active-bound identification, endpoint start dispersion, endpoint serialization replay and parameter derivative checks therefore do not exist. The new R5 coordinate declaration has not been exercised by a fit. No reaction-temperature fit or interval-heat qualification was attempted; there are no stage-4 frozen coefficients.

The stop follows the owner's explicit rule that an unavailable row at any start returns to the owner. No row was dropped, no parameter start or bound was changed, no tolerance was relaxed, and no previous fitted value was substituted. No further numerical probe ran before returning the stop. The parent then authorized the bounded diagnosis described above, and required the classification to be returned before further work. Its warm result does not amend the campaign calculation. A table is sufficient for this incomplete qualification result; an incomplete fitted comparison figure would not clarify it.

## Execution, code and handoff

`qualification/summary.json` retains four per-call timings; `timing.json` retains the two 3a start calls. The qualification calls used 12.882950 CPU-s / 12.929619 native wall-s, within 1200 CPU-s / 300 s. The attempted 3a process records 29.878130 CPU-s / 29.173444 wall-s, within 5400 CPU-s / 600 s. The initial declaration correction records another 0.282643 CPU-s / 0.280941 wall-s: it selected a system-pressure output with no phase while declaring partial pressure, and was corrected before any numerical solve. Its original input and traceback remain under `declaration-check/`.

The combined recorded total is 43.043723 CPU-s / 42.384004 wall-s. This total mixes native qualification timing with whole-process 3a timing. Water/binary interpreter startup and verification overhead were not metered, so it is a lower bound on total execution time. The current-record replay separately records 14.431783 command wall-s versus 11.532687 native wall-s; including that known overhead raises the recorded wall total to 45.283099 s. No budget was exhausted.

Scientific calculations ran sequentially at `nice -n 10`, with single-thread BLAS/OpenMP settings. The host has 32 CPUs; measured available memory was 19.16 GB when 3a requested 32 native workers at the existing 256 MiB estimate per worker. Start assessment is sequential; no fit worker pool was launched. Actual Engine worker count is not returned. No process was interrupted.

`fit_observations.py` transports the frozen reactive requests through existing source-feed and chemistry owners, and accepts the named component/R5 coordinates in the existing native fit path. `fit_campaign.py` accepts stage-specific declarations, records tolerance-based numerical replay comparisons and stops at deficient or bound-limited endpoints. The stored R5 coefficient maps to the native natural-log reciprocal-temperature coefficient by −ln(10); no local equilibrium, EOS, optimizer or linked reaction-enthalpy mechanism was added. `change-accounting.json` records additions against the accepted design base; stage-3 additions are distinguished from stage 2 in `change-accounting-stage3.json`.

The classifier reports 323 total executable additions against `6c8d20073fd0e5fda8dd323a51f55551d12b7486`, versus 294 in the retained stage-2 accounting. The branch diff against `b6aee49` counts 43 added executable lines and 14 removed. The three inert diagnostic scripts add another 114 lines, charged conservatively as code despite the classifier's text-file category. The combined stage-3 charge is **157 of 200**; adding that to the supplied stage-2 total of 327 gives **484 of 900**. The smaller classifier increment is not used to claim extra capacity.

The diagnosis adds 5.581666 CPU-s / 5.768992 wall-s. Combined recorded execution is therefore **48.625389 CPU-s / 48.152996 wall-s**, or **51.052091 wall-s** including the separately known current-replay command overhead. The remaining unmetered qualification startup/verification overhead still makes these execution totals lower bounds. No scientific allowance was exhausted.

No new persistent test was added: the four retained numerical replays and complete/partial start solves check the changes exercised here. No independent delivered review has run. The root notebook, manuscript, selected-current parameter record and stage-2 results remain unchanged. The worktree contains neither the ignored literature shelf nor the journal preference files; this task used the accepted design and retained source owners and makes no new literature judgment. No GitHub write, push, merge, Engine edit, subagent, worktree or preview-service action was performed.

## Orchestrator amendment, 15 October 2026, pending owner confirmation

The parent authorized the design section 2 Kiepe continuation allowance for stage 3a after the retained B row-13 diagnosis. The amended calculation uses continuation for every row within each isotherm, identically at A and B. At each parameter record, the preceding converged row supplies the next row's Engine pressure `Free(guess)`, both phases' `composition_guess`, and both phases' `packing_guess`. The first row of each isotherm retains its original guesses. No intermediate composition is required unless direct adjacency fails; no intermediate point receives objective weight. There is no local solver. Parameters, target identities, phase kinds, bounds, tolerances and objective weights remain unchanged.

The original cold calculations and their failure remain in their original paths. Amended results are retained under `continuation/`, with a frozen copy of the amended campaign declaration. The preceding result is recomputed at each parameter record before its guesses are transported; guesses never come from the other start or a different parameter record. This amendment is an orchestrator decision pending owner confirmation, as required by the parent task.

## Amended 3a result: lower-bound endpoint, returned for decision

With the amendment above, both A and B return all 195 targets. A retains cost 0.2916717031373328, matching its original cold result to floating-point roundoff; B's complete starting cost is 0.24847134553886543. B row 13 returns 5.503809502954186 MPa and CO₂-rich density 3100.2957005057706 mol/m³, matching the retained adjacent-row diagnosis. The same initialization procedure at A returns 9.000105234320171 MPa and CO₂-rich density 14043.38538551182 mol/m³. The starting root families remain different and are preserved in `continuation/kiepe-313.20-roots.csv` for all twelve rows of that isotherm.

The A fit converges in 26 iterations to cost **0.1475198494358558**, with CO₂ dispersion **160 K**, CO₂–water interaction at 313.15 K **−0.07253664499178383**, slope **−45.66829700762119 K**, and R5 reference coefficient **2500.112408571033 K**. All 195 native endpoint predictions are available. The native function-tolerance termination is accompanied by an active CO₂-dispersion lower bound, so the calibration has not been settled. The explicit owner stop rule applies. No B fit or later calculation was launched, and no precursor was selected.

The full optimizer Jacobian has rank **4/4**, condition **134.90691886476048**; after excluding the active dispersion column, the free matrix has rank **3/3**, condition **5.115862440091624**. `continuation/identification.json` retains both singular spectra, physical spectra, scales, gradient and weakest directions. Native covariance independently reports full rank 4 and an active bound; its interior-point uncertainty assumptions do not apply. There is no physical parameter uncertainty estimate.

Mean absolute relative errors, percent:

| Family | A start | B start | A bound-limited endpoint |
|---|---:|---:|---:|
| Reactive pressure | 58.862494 | 57.342727 | 101.286954 |
| Species | 73.042285 | 56.910339 | 46.112169 |
| Kiepe pressure | 2.666524 | 19.240258 | 4.981335 |

Kiepe mean / maximum absolute relative errors, percent:

| Isotherm, K | A start | B start | A bound-limited endpoint |
|---|---:|---:|---:|
| 313.20 | 1.501207 / 2.659100 | 24.692845 / 40.382700 | 5.277946 / 19.930828 |
| 353.11 | 3.826095 / 5.577518 | 16.546102 / 21.250162 | 5.903299 / 6.303107 |
| 373.26 | 0.972618 / 2.799777 | 16.660296 / 20.367789 | 4.781600 / 6.582074 |
| 393.17 | 6.645612 / 11.336118 | 17.536242 / 26.986562 | 3.404637 / 5.553888 |

The lower log-ratio objective coexists with worse reactive-pressure mean relative error. Its three endpoint family costs are 0.12371264771537516, 0.02195295585330804 and 0.0018542458671724372, respectively. These declared engineering weights allow that trade-off; lower cost does not imply every displayed error improves. Family and isotherm values are retained in the two CSV tables under `continuation/`.

The native A row-13 endpoint pressure is 7.391905913193009 MPa. Its CO₂-rich density, endpoint root family, model CO₂ critical temperature, serialized replay, endpoint equilibrium closure and parameter-derivative checks have **not** been evaluated because the bound stop preceded those calls. There is no B endpoint, so endpoint start dispersion and the A/B endpoint root-family comparison are unavailable. The five failed trial steps, all on Kiepe row 13, remain in `native-fit.json` with their numerical causes; no failed trial received a penalty or changed denominator. At the starts, complete material, charge and source-mass checks are retained in each `start-balances.json`, along with all phase and equilibrium diagnostics in `start-predictions.json`.

Stage 3b is unrun. Its six heat comparisons, family root mean squares, linked shifts, pivot/enthalpy invariants and serialized reaction-temperature replays are unavailable. `stage3/frozen-inputs.json` is not written because the required precursor is unsettled. No unavailable value is inferred from the parameter trend or an earlier fit.

This is a conditional calibration result and numerical verification of starting-state availability, not a completed stage-3 calibration, prediction on independent data or physical validation. A compact table describes the active bound and family trade-off; an incomplete comparison figure would not settle the missing endpoint/root checks. Independent delivered review and investigator promotion have not occurred.

The amended command records 519.271879 aggregate CPU-s and 100.076116 wall-s including the conservative prior charges 48.625389 CPU-s / 51.052091 wall-s. The new measured work is 470.646490 CPU-s / 49.024025 wall-s. It requests 32 native workers on 32 discovered CPUs with 10.67 GB available memory and single-thread BLAS/OpenMP. It runs at `nice -n 10`; actual worker count is not returned by the Engine. Stage 3b uses zero CPU/wall. Neither stage allowance is exhausted. The previously unmetered qualification startup still makes the combined campaign total a lower bound.

The amended code adds 14 executable lines to the existing observation owner. Against the stage-2 head `b6aee49`, stage-3 code now adds 57 lines (31 in `fit_campaign.py`, 26 in `fit_observations.py`) and removes 14. Adding the retained 114 diagnostic-script lines gives **171 of 200** stage-3 gross executable lines, and **498 of 900** for the campaign when combined with the supplied stage-2 charge of 327. `continuation/change-accounting.json` records the final-tree classification against `6c8d20073fd0e5fda8dd323a51f55551d12b7486`; `continuation/change-accounting-stage3.json` preserves the conservative stage-specific charge. No new persistent test, local solver, EOS, parameter derivative or optimizer was added. `continuation/initialization-check.json` checks unchanged target definitions, A's original result and B row 13 against the existing diagnosis.

The working notebook now records the conditional A endpoint and explicit stop. The presentation refresh attempted the existing `analyses/manuscript.py refresh` command without any service change, but could not run because `snakemake` is absent from the command environment. No HTML was refreshed and no package was installed. The notebook source and retained result tables remain available for independent review.

## Ions-first execution on cf26a17b, 15 October 2026

The new wheel passes all four unchanged-record requalifications at the $10^{-8}$ limits; see [qualification](../stage4/qualification-cf26a17b/README.md). The corrected bicarbonate–water reset and all five unloaded-density replays are retained under [initial stage 4](../stage4/initial-source-chemistry/README.md). Initial stage-4 A stops without convergence and with four active bounds, followed by a tied-coordinate serialization error in the application. No I₀ is selected. Reordered S₁, I₁ and S₂, the 195/41-target stage-3 fits, Kim interval qualification, linked pivot/enthalpy checks, and movement tests are unrun. No new stage-3 frozen input is written. The superseded 160 K endpoint remains history and was not used as an input.
