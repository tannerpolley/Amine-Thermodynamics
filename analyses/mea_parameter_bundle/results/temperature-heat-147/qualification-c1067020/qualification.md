# Engine c1067020: all requested qualification checks pass

The pinned wheel returns finite-addition heats of **−68169.42621173232 and −68286.33285346051 J/mol CO2** for 0→0.11 and 0→0.45. Checks 1–6 and all three §6.1 local bubble boundaries pass. Checks 1–2 retain their prior results on this same wheel; this continuation ran checks 3–6 and §6.1 once, in order. Checks 3 and 4 reproduced every retained scientific value exactly, including the neutral-anchor shifts, feed-root fields and endpoint state diagnostics.

Evidence type: **numerical verification only**. Negative heat denotes an exothermic increment under the frozen reacting-liquid model. The bubble guards admit the prescribed one-liquid endpoints against these local liquid-vapor boundaries. They do not establish global phase stability, exclude liquid-liquid splitting or solids, validate calorimetry, adopt parameters, qualify concentration transfer or loaded-temperature extrapolation, or establish absorber/stripper performance. Physical parameter, source and model uncertainty are not quantified. Independent delivered review remains with the parent.

Basis: 313.15 K, 1734000 Pa, 1 mol feed MEA, 7.911062165006594 mol water, unloaded MEA mass fraction 0.3, and initial carbon exactly zero. Pure-CO2 feed is queried at the same temperature and pressure with the prescribed `vapor` hint. Frozen Phase A chemistry, five reactions, neutral references, physical inputs, starts, finite-difference steps and numerical limits remain unchanged. Physical parameter SHA-256: `7e9e3f02723700f8b6577681173249c0e7bd2c8c2a098f38a4e0a7e4611852d5`; physical calorics SHA-256: `c94d504e68c6dc6e85d3d950cc51422499846729b1a06994b362040be991924a`.

| Check | Outcome and evidence |
|---|---|
| 1. Historical replay | Pass, retained unchanged: 84 states/142 targets. Pressure/species/total costs 8.143453130517166 / 24.84844413070364 / 32.99189726122081. Differences from the historical reference +2.3163693185779266e−12 / −2.6361135496699717e−12 / −3.197442310920451e−13, below 1e−8. Maximum prediction/allowance ratio 0.00012402064066160403. |
| 2. Frozen-law mapping | Pass, retained unchanged: 12 R2/R4/R5 values at 293.15/313.15/333.15/353.15 K. Maximum absolute ln K difference 7.815970093361102e−14, below 5e−13; stored/native polynomial RT² derivative differences zero. R2 reference pressure 101325 Pa, R4/R5 100000 Pa. Frozen source-admission grids and continuation errors are unchanged. |
| 3. Native heat, feed and phase admission | Pass at both increments: exact-zero initial carbon, identical reactions/references and zero componentwise feed-balance differences. Native values are negative; independent feed root and all required bubble boundaries pass. |
| 4. Independent assembly, anchor shift and conditioning | Pass at both increments; all values below reproduce the prior c1067020 record exactly. |
| 5. Exact heat Jacobian | Pass: five directions at both states, centered h and 2h re-solves, fine/coarse ratios below one. |
| 6. Convergence and conservation | Pass: all fixed-pressure endpoints and retained training states satisfy their requested tolerances and unchanged raw/material/charge limits. Maxima below. |
| §6.1 pure-CO2 feed root | Pass: one stable root, density 723.5928742984386 mol/m³, positive dp/dρ 2196.5242889643346 Pa/(mol/m³), finite total enthalpy −393574.4494137983 J/mol. Returned branch `Unspecified`; requested hint `vapor`. |
| §6.1 bubble boundaries | Pass at α=0, 0.11 and 0.45. All three pressures were computed here, with the prescribed nine-species reacting liquid, five reactions and neutral CO2/MEA/H2O vapor `Pinned(0)`. No Engine handoff pressure was substituted. |

| Heat verification quantity | 0→0.11 | 0→0.45 |
|---|---:|---:|
| Native heat (J/mol CO2) | -68169.42621173232 | -68286.33285346051 |
| Initial H (J) | -2313691.8924407274 | -2313691.8924407274 |
| Final H (J) | -2364483.718759536 | -2521529.244460994 |
| Independently queried feed H (J/mol) | -393574.4494137983 | -393574.4494137983 |
| Independent assembly (J/mol CO2) | -68169.42621173232 | -68286.33285346051 |
| Assembly minus native (J/mol CO2) | 0.0 | 0.0 |
| Allowance (J/mol CO2) | 0.0425980386189414 | 0.010814222192635062 |
| Heat change after +10000 J/mol neutral CO2 anchor shift | 0.0 | 2.0372681319713593e-09 |
| Conditioning | 623.8701358675985 | 157.35119182398864 |

The assembly allowance is 1e−9 abs(heat)+1e−9(abs(Hi)+abs(Hf))/nadd+1e−6 J/mol. Conditioning is (abs(Hi)+abs(Hf))/(nadd abs(heat)), below 1e4. Independently queried feed ideal/residual contributions are −392950.7093424419 / −623.740071356366 J/mol. Checks 3 and 4 reproduce the prior c1067020 values with differences exactly zero; the native heats also equal the b83c4250 results.

| Parameter direction | α=0.11 fine | α=0.11 coarse | α=0.45 fine | α=0.45 coarse |
|---|---:|---:|---:|---:|
| Carbamate–water intercept | 0.03520689158624007 | 0.03264384013244511 | 0.004924454221681587 | 0.0060198750282613855 |
| Protonated MEA–water intercept | 0.001470586041224449 | 0.00307360248844585 | 0.0016031621640805896 | 0.0017350275156487423 |
| Bicarbonate–water intercept | 0.06659739368442695 | 0.00480029982335419 | 0.004758528518131554 | 0.0006578458539476028 |
| Carbamate–protonated MEA intercept | 0.01303467228114922 | 0.0019027271653271505 | 0.0034596995437119263 | 0.00037120905232691695 |
| Protonated MEA–water inverse-temperature slope | 4.539230028135744e-06 | 1.1534858145910217e-06 | 9.020874793635969e-06 | 3.4641081656013954e-07 |
| Maximum | 0.06659739368442695 | 0.03264384013244511 | 0.004924454221681587 | 0.0060198750282613855 |

Fine ratios divide abs(exact−FD(h)) by 5e−6 max(1,abs(FD(h))); coarse ratios use four times the same allowance. Intercept h=1e−4 and slope h=1 K. `remaining-qualification.json` retains all exact actions, fine/coarse derivatives and error ratios; the 40 `fd-*.json` records retain the four re-solves per direction. The largest truncation estimate abs(FD(2h)−FD(h))/3 is 0.0007867250436296066 J/mol per parameter unit; maximum eight-ulp roundoff estimate is 1.1641532182693481e−6 for intercepts and 1.1641532182693481e−10 for the slope. These describe finite-step and cancellation effects, not physical uncertainty or formal equilibrium-solve error bounds. No step, seed, tolerance or physics changed.

Against b83c4250, α=0.11 fine/coarse maxima change from **0.03434805942801085 / 0.03253644283281535** to **0.06659739368442695 / 0.03264384013244511**. At α=0.45 they change from **0.005455402229353226 / 0.005611162721701841** to **0.004924454221681587 / 0.0060198750282613855**. Every ratio on both wheels is below one. `qualification.json` retains each direction’s previous ratios, ratio differences and exact-action difference; the maximum absolute exact-action difference is 9.491486707702279e−9 J/mol per parameter unit.

| Endpoint loading α | Computed bubble P (Pa) | 1734000/P | Max raw row | Max material error (mol) | Charge error (mol) |
|---:|---:|---:|---:|---:|---:|
| 0.0 | 6289.083617367117 | 275.7158443897312 | 4.263256414560601e-14 | 1.717376241217039e-16 | 1.1372555640984076e-16 |
| 0.11 | 6383.03638497024 | 271.6575459420767 | 1.9895196601282805e-13 | 1.5048726154098802e-16 | 3.523190765941896e-17 |
| 0.45 | 7256.301033961463 | 238.96472760493373 | 5.684341886080802e-14 | 4.0245584642661925e-16 | 8.734151966715284e-17 |

All boundaries satisfy 1734000 > P_bubble(1+1e−7), raw rows ≤1e−10, and material/charge errors ≤1e−7 mol. All requested solver tolerances are met. At α=0, all four carbon species are literal zero in both phases. The independently calculated α=0 pressure happens to equal the Engine handoff; its source is the new `bubble-0.11-0.json` state.

For the four fixed-pressure endpoint records (three distinct states), maxima are raw row **2.8421709430404007e-13**, classified residual **7.567628033932771e-14**, material error **9.959481156451844e-16 mol**, and charge error **7.770991991234328e-16 mol**. These diagnostics reproduce the prior c1067020 records exactly. Retained 84-state training maxima are raw stationarity **5.968558980384842e-13**, material **6.066258606551855e-13 mol**, and charge **2.0431756812929434e-13 mol**. Training states were not rerun.

No failure occurred in this continuation: all 55 serial child calls completed. The earlier execution failure remains byte-identical in `previous-f023cf5/qualification-failure.json` and the original top-level `qualification-failure.json`, which records resolved history:

```text
TypeError: coordinate() takes 2 positional arguments but 3 positional arguments (and 2 keyword-only arguments) were given
```

The owner-approved fix replaces that broken call with `coordinate(params, [(family, pair, 1.0)], origin=0., scale=1.)`, preserving family, pair, origin and scale. Coefficient 1.0 preserves the old map. The installed wheel’s `epcsaft/regression.py` lines 78–92 confirms the signature. The replacement adds one gross executable line and removes one; no fallback, test, helper or dependency was added.

Wheel SHA-256: `e8ad39e0c5d7da471a6d3ace6ff62d60518c57bc1c96fe5198d8bf18747ba8b5`. Engine source commit: `c106702048e87d0c583a3a5516cb5746e7a6ac07`. The archive hash was checked before execution. The existing noneditable `.venv-c1067020` was used unchanged; every child retains its actual `site-packages` module origin, and `installed-record-check.json` verifies 18 hashed installed RECORD entries. No build, install or Engine source import ran. Existing `wheel-identity.json` and `build-toolchain.json` retain build/compiler/dependency identities.

Driver commit: **2e54c1633ee165a7ed39c31e9f157194d174833a**; producer SHA-256 `d8ba410a183b77950bb7203bf3cafd6f932081909baabc53212520a5c76ce1e9`. The 37 files from the previous record are archived under `previous-f023cf5/`, byte-identical to commit `f023cf5929ecb2c3dd6d205f87e929ab38040b5f`. `original-SHA256SUMS` preserves the previous index and the archive’s `SHA256SUMS` verifies its archived filenames. `historical-preservation.json` records the archive comparisons and checks of 1858 protected files, including the untouched untracked `zero-carbon-diagnosis/`. Earlier-wheel results are unchanged except for the explicitly authorized shared wrapper. Checks 1–2 on this wheel are unchanged.

The continuation took **45.11 s** enclosing wall, user/system CPU **38.93 / 3.81 s**, with reported peak process RSS **69904 KiB**. Summed child wall is **44.629922751002596 s**, Q1 **8.391875878999599 s**, Q2 **36.238046872003 s**. All calls ran under `agent-heavy --wait 180 --timeout 3540s --max 1G`, with Q1/Q2 1770 s budgets, the unchanged Q1 prior reservation of 49.79 s, per-child `timeout -k 5s 175s` bounded by remaining budget, and OMP/OpenBLAS/MKL threads one. No pool, exit 137, 124 or 75 occurred. The job exit was zero. New conservative numerical charge is **45.11 s**, counting the enclosing serial job without child double counting; cumulative use is **about 325.12193797600025 of 50400 s**, leaving about **50074.878062024 s**.

Accounting from `76ea465fe1ede72257a809d04fc986489c5267f3`: **485 gross executable additions of 491**, six remaining, with no removal credit. The Git numstat sum is 120 source-law + 213 original-driver + 152 wrapper additions. The fix contributes one gross addition and one removal. `gross-line-history.txt` records the cross-check. The final-tree CSE report in `change-accounting.json` measures **473 surviving executable additions**; the 12 removed historical lines explain the difference from 485. Documents, JSON/CSV/log/checksum evidence are reported separately; no notebook code or test was added.

No requested qualification check remains unrun. Independent delivered review is pending with the parent. Fits, additional loadings or temperatures, notebook/manuscript edits, parameter adoption, push, PR and issue edits remain outside this worker’s delivery.
