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
