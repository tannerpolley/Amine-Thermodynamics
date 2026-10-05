# Engine 9c31cb9a qualification: heat checks pass; exact-zero bubble boundary unavailable

The pinned wheel returns native finite-addition heats of **−68169.42621173232
and −68286.33285346051 J/mol CO2** for 0→0.11 and 0→0.45. Independent
endpoint/feed assembly, neutral-anchor invariance, all five exact parameter
directions at both loadings, and fixed-pressure convergence/conservation pass.
Qualification is **incomplete**: the first §6.1 bubble calculation rejects the
prescribed exact-zero-carbon incipient vapor support before returning a state.
No later bubble calculation ran. Checks 1–2 stand and were not rerun.

Evidence type: **numerical verification**. Negative heat means an exothermic
increment under the frozen model and declared one-liquid endpoint calculations.
The missing bubble boundary prevents local liquid-vapor phase admission. These
values do not establish calorimetric physical validation, parameter adoption,
loaded-temperature extrapolation, or absorber/stripper performance.

Basis: 313.15 K, 1734000 Pa, 1 mol feed MEA, 7.911062165006594 mol water,
unloaded MEA mass fraction 0.3, initial carbon exactly zero, and pure-CO2
feed at the same temperature and pressure with the prescribed `vapor` hint.
Frozen Phase A chemistry, all five reaction declarations, neutral references,
physical parameters and calorics are unchanged. Physical parameter SHA-256 is
`7e9e3f02723700f8b6577681173249c0e7bd2c8c2a098f38a4e0a7e4611852d5`;
physical calorics SHA-256 is
`c94d504e68c6dc6e85d3d950cc51422499846729b1a06994b362040be991924a`.

| Check | Outcome and evidence |
|---|---|
| 1. Historical replay | Pass, retained unchanged: 84 states/142 targets. Pressure cost 8.143453130514477, species 24.848444130706277, total 32.99189726122075. Cost differences −3.730349362740526e−13, 0 and −3.765876499528531e−13 (limit 1e−8). Maximum prediction/allowance ratio 1.7684921378575326e−5. |
| 2. Frozen-law mapping | Pass, retained unchanged: 12 R2/R4/R5 values at 293.15/313.15/333.15/353.15 K. Maximum absolute ln K difference 7.815970093361102e−14 (limit 5e−13); stored/native polynomial RT² derivative differences zero. Reference pressures R2 101325 Pa, R4/R5 100000 Pa. |
| 3. Vinjarapu 0→0.11 | Native value, fixed-P endpoints and independent feed pass: −68169.42621173232 J/mol CO2. Exactly zero initial carbon; componentwise feed-balance differences zero; identical reactions/references. Required bubble admission remains incomplete under §6.1. |
| 3. Vinjarapu 0→0.45 | Native value, fixed-P endpoints and independent feed pass: −68286.33285346051 J/mol CO2. Same exact-zero initial state, zero feed-balance differences and unchanged reactions/references. Required bubble admission remains incomplete under §6.1. |
| 4. Assembly, anchor shift, conditioning | Pass at both loadings; numbers below. |
| 5. Exact heat Jacobian | Pass for all five directions at both loadings, with h and 2h centered re-solves; all error/allowance ratios below one. |
| 6. Convergence and conservation | Pass for the returned fixed-P endpoints and retained training states; maxima below. No boundary-state convergence result exists. |
| §6.1 feed root | Pass at both observations: one stable root, density 723.5928742984386 mol/m³, dp/dρ 2196.5242889643346 Pa/(mol/m³), finite H. Returned density branch is `Unspecified`; the requested hint remains `vapor`. |
| §6.1 bubble boundary | Fail/unavailable at α=0: exact diagnostic below. Final α=0.11 and 0.45 boundary checks remain unrun. Bubble pressure, separation and global phase stability are unestablished. |

The supported independent feed query selects only `carbon-dioxide` through
`Parameters.from_mapping`, retains that component's existing thermochemistry
interval and queries `Pure.state(...).total_enthalpy`. It returns
**−393574.4494137983 J/mol** on this wheel: ideal contribution
−392950.7093424419 and residual contribution −623.740071356366 J/mol.
The current calculation happens to match the old-wheel reference; that old
value was not used in the new assembly. Likewise the Engine candidate-wheel
values are comparison history, not a claim of recomputation on that candidate.

| Quantity | 0→0.11 | 0→0.45 |
|---|---:|---:|
| Initial H (J) | −2313691.8924407274 | −2313691.8924407274 |
| Final H (J) | −2364483.718759536 | −2521529.244460994 |
| Independent assembled heat (J/mol CO2) | −68169.42621173232 | −68286.33285346051 |
| Assembly minus native (J/mol CO2) | 0 | 0 |
| Relative plus cancellation allowance (J/mol CO2) | 0.0425980386189414 | 0.010814222192635062 |
| Heat change after +10000 J/mol CO2 neutral-anchor shift | +4.249159246683121e−9 | +1.0477378964424133e−9 |
| Conditioning, (abs(Hi)+abs(Hf))/(nadd abs(heat)) | 623.8701358675985 | 157.35119182398864 |

Both conditioning values are below 1e4. The allowance is the unchanged §8.4
relative term plus its endpoint-cancellation allowance. No tolerance was changed.

| Parameter direction | 0→0.11 fine ratio | 0→0.11 coarse ratio | 0→0.45 fine ratio | 0→0.45 coarse ratio |
|---|---:|---:|---:|---:|
| Carbamate–water intercept | 0.03434805942801085 | 0.03253644283281535 | 0.005455402229353226 | 0.005611162721701841 |
| Protonated MEA–water intercept | 0.0024269027496875814 | 0.0029781007519724353 | 0.001603262078669189 | 0.001721265889506389 |
| Bicarbonate–water intercept | 0.029887403287002037 | 0.010503008735541459 | 0.0010532829639931121 | 0.00026332074099827803 |
| Carbamate–protonated MEA intercept | 0.006121612952640171 | 0.004495170765832698 | 0.0021393303330876834 | 0.00037122661627571535 |
| Protonated MEA–water inverse-temperature slope | 1.6961727313481318e−5 | 1.1762773626017533e−6 | 6.4694686551910305e−6 | 3.459780859518721e−7 |
| Maximum over five directions | 0.03434805942801085 | 0.03253644283281535 | 0.005455402229353226 | 0.005611162721701841 |

Fine ratios divide abs(exact−FD(h)) by 5e−6 max(1,abs(FD(h))); coarse
ratios use four times that same allowance. h=1e−4 for intercepts and 1 K for
the slope. `remaining-qualification.json` retains exact actions, four re-solved
values per direction via the child files, truncation estimates abs(FD(2h)−FD(h))/3
and eight-ulp roundoff estimates. The largest truncation estimate is
7.902660096685091e−4 J/mol per parameter unit; roundoff estimates are
1.1641532182693481e−6 for intercepts and 1.1641532182693481e−10 for the slope.
These describe finite-step comparisons and cancellation, not physical uncertainty
or formal error bounds on equilibrium solves. No step, seed or coordinate changed.

For the four returned fixed-P endpoint records (three distinct states), maximum
raw residual/equation magnitude is **1.9895196601282805e−13**, classified
residual **5.045085355955182e−14**, material error **3.0531133177191805e−16 mol**
and charge error **4.96507676858133e−16 mol**. All requested tolerances are met;
raw rows are below 1e−10 and material/charge errors below 1e−7. Retained training
maxima are raw stationarity **3.979039320256561e−13**, material
**2.0605739337042905e−13 mol**, and charge **3.7951851945411784e−14 mol**.

The first failure in this continuation is:

```text
epcsaft._core.ParameterError: zero_inventory_incipient_support: component 0 in phase V needs the discarded conserved potential in chemical stationarity
```

It occurs in `eq.solve_equilibrium` for the initial α=0 boundary, declared
with the same reacting liquid and a neutral CO2/MEA/H2O vapor of `Pinned(0)`
amount. The Engine rejects that incipient support before returning a boundary
state. `bubble-0.11-0.json`, `phase-boundary-failure.json`,
`remaining-qualification.json` and `continuation.log.gz` retain the complete
exception and child/parent tracebacks. This is phase-boundary unavailability;
there is no finite pressure or separation value to report. Diagnosis and any
correction or further run remain with the owner; the stop rule forbids probes,
CO2 epsilon, support substitutions or retries in this worker's run.

The earlier `FeedEnthalpy` AttributeError is preserved unchanged in
`qualification-failure.json` and the byte-identical `previous-0271e5f/` copies.
That folder's `original-SHA256SUMS` preserves the old checksum index; its
`SHA256SUMS` verifies the files actually archived there. All archived originals
were compared byte-for-byte with commit `0271e5f`. Earlier-wheel records and
checks 1–2 remain unchanged. The new producer is driver commit **713f29d**,
SHA-256 `60a5b7946c71d61f6753db178a0fb865211585aa80ec24613611b28d056fea9c`;
the retained new results are commit **bd744f7**.

Wheel SHA-256:
`b83c42502235e8915cd07b0eabf24398c7f54a884d41ca914273ddd0f1703667`;
Engine `9c31cb9a89b6fb42fd386ca44de2331601b4751c`. The archive hash was checked
before execution; the private `.venv-9c31cb9a` was used as-is, with installed
RECORD verification and actual module origin retained. No build or install ran.

The 53 serial child calls took **34.694176909995804 s** summed wall time:
Q1 **5.717458443999931 s**, Q2 **28.976718465995873 s**. The enclosing job took
**35.11 s**, user/system CPU **31.06/3.43 s**. All numerical calls ran within
`agent-heavy --wait 180 --timeout 3540s --max 1G`, each child limited by
`timeout -k 5s 175s` and its remaining Q1/Q2 budget. OMP/OpenBLAS/MKL threads
were one; there was no pool. Fifty-two calls completed; the final call returned
the ParameterError with exit code 1. No memory-cap, timeout or admission failure
occurred. With the supplied prior charge of about 166 s, cumulative conservative
compute is **about 201.11 s of 50400 s**, leaving about 50198.89 s.

CSE accounting uses base `76ea465fe1ede72257a809d04fc986489c5267f3`.
The feed replacement adds **10 gross executable lines** and removes three,
retiring the unsupported enum/prediction path while preserving root admission.
Owner accounting is **466 + 10 = 476 of 481**, five lines remaining; removals
receive no credit. The base-to-final-tree report measures **472 surviving
executable additions** (120 source-law, 211 original-driver, 141 successor-driver
lines). The four-line difference is the earlier one-line removal plus this
three-line replacement. Documents and retained JSON/CSV/log/checksum changes are
reported separately in `change-accounting.json`. No test or dependency was added.
The protected pre-existing untracked diagnosis is explicitly excluded from the
task's changed surface and remains untracked.

The two final-loading bubble checks are unrun, and full phase qualification
remains unresolved. There was no fit, loaded solve above 333.15 K, #152/#160
input substitution, notebook/manuscript change, parameter adoption or remote
publication. Independent delivered review has not occurred; the parent owns it.
