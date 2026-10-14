# Stage 2 CO₂–water diagnosis

The immediate cause of start A's row-10 failure is the imposed low-density vapor-root selection, reached because this starting interaction severely overpredicts pressure. A distinct aqueous/CO₂-rich fluid coexistence solution exists at **24.19308948 MPa**, but its CO₂-rich phase is dense and Engine rejects it when declared `kind='vapor'`. This is not evidence of liquid/vapor compositions and densities coalescing at a mixture critical point. Bounded composition continuation alone does not recover the row under the original phase declaration. A diagnostic eight-row interaction fit gives **k_ij = −0.046912921483332176** and solves **all 39 rows cold**, with the original liquid/vapor declaration and 1e-10 tolerance.

These are disposable numerical diagnosis results, not a completed Stage 2 calibration or parameter adoption. No tracked edits, commits, GitHub writes, record-changing fits, or subagents were used. All files created for this task are under `tmp/stage2-diagnose/`.

## Basis and reproduction

Worktree: `/home/tnnrpolley21/.t3/worktrees/Amine-Thermodynamics/t3-170-stage-2-build-and-run-mea-water-an-c331b494`; branch `t3/170-stage-2-build-and-run-mea-water-an-c331b494`; HEAD `222ff8b6088ea228b82b698f474e59f84371dcdb`. The working tree was clean before and after the probes.

Read the installed CSE research/diagnosis skills, root instructions, scientific README/context, accepted #170 comments, frozen Stage 2 declaration and retained evidence, and the observation/campaign owners. Neither requested journal memory file exists in this worktree. The declaration actually resides at `analyses/mea_parameter_bundle/data/input/fit-campaigns/joint-recalibration-170.json`; the prompt's shorter `data/input/fit-campaigns/` path does not exist here. The frozen `stage2/spec.json` supplies the exact same calculation inputs used by the probes.

Engine: merged main `36485a88`, wheel SHA-256 `da5a2b65668ab5647e51b917a659614bdcb4afbe7e5c3149aee2294b86a4c1bd`. All 11 installed Engine distribution files match the wheel bytes (`wheel-check.json`). Python/environment is the existing `tmp/stage2/venv`. New water, fixed CO₂ dispersion 169.21 K, all remaining reference quantities, liquid feed amounts on a one-mole basis, two neutral phase supports, zero incipient-phase amount, and total pressure are preserved. Refreshed reciprocal association energy is 878.3248982254499 K, volume 0.0376197279502706. Every solve uses `row_tolerance=1e-10`; no numerical tolerance was relaxed.

Representative reproduction commands, from this worktree:

```bash
nice -n 10 env PYTHONPATH=src:analyses/mea_parameter_bundle/scripts OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 60s tmp/stage2/venv/bin/python tmp/stage2-diagnose/probe.py A
nice -n 10 env PYTHONPATH=src:analyses/mea_parameter_bundle/scripts OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 60s tmp/stage2/venv/bin/python tmp/stage2-diagnose/probe.py fit8
nice -n 10 env PYTHONPATH=src:analyses/mea_parameter_bundle/scripts OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 60s tmp/stage2/venv/bin/python tmp/stage2-diagnose/probe.py fitted -0.046912921483332176
nice -n 10 env PYTHONPATH=src:analyses/mea_parameter_bundle/scripts OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 60s tmp/stage2/venv/bin/python tmp/stage2-diagnose/root_probe.py root
```

These commands write scratch results only. `probe.py` constructs the original observations through `fit_observations.stage2_rows`; calls `eq.solve_equilibrium(model, problem, start=previous_state)` for continuation; bisects composition at most eight levels between adjacent source rows; and gives intermediate points no objective weight. It records every attempted solve, including failed intermediates. Evaluations continue past failed observations for diagnosis, while retaining their unavailable values and the original 39-row denominator. They are not campaign completion calls.

## 1. Why start A fails at row 10

At 313.20 K and liquid x_CO₂ = 0.01639, observed pressure is 4.6671 MPa. The exact cold call returns `LOCAL_INFEASIBILITY`, residual 0.0021452086689242953 after 26 iterations; the retained pressure observation reports `CentralSolveUnavailable`. Failed native results return empty density/composition/coordinate arrays. Consequently the original cold termination cannot be assigned a physical pressure or described as a measured approach to coalescence.

The preceding row 9 (x_CO₂ = 0.00713) converges at 3.27222103 MPa, with densities 54,788.3693 and 1,493.4064 mol/m³ and vapor y_CO₂ = 0.9968276088. Composition continuation then reaches success at intermediate x_CO₂ = 0.01176, P = 6.18507147 MPa, densities 54,602.8599/3,622.4366; x_CO₂ = 0.0129175, P = 7.21546630 MPa, densities 54,559.5752/4,917.2540; x_CO₂ = 0.014075, P = 9.30119656 MPa, densities 54,526.4892/14,392.6020; and x_CO₂ = 0.01465375, P = 12.25149045 MPa, densities 54,528.2160/16,873.1830. An eighth-level intermediate x_CO₂ = 0.014689921875 reaches 12.45935415 MPa and 54,528.5465/16,978.5721 mol/m³. The target remains unavailable; the method has used its eight-level allowance rather than simply neglecting continuation.

The target is solved independently with exactly the same EOS and equations, changing only the incipient CO₂-rich phase's density-root declaration to `kind='liquid'` and supplying a dense packing guess. Three pressure starts, 15, 30 and 50 MPa, converge to the same **24.19308948 MPa** state:

| Quantity | Aqueous phase | CO₂-rich phase |
|---|---:|---:|
| CO₂ mole fraction | 0.0163900000 | 0.9827693879 |
| Molar density, mol/m³ | 54562.32117 | 20147.92996 |
| Pressure-density derivative, Pa/(mol/m³) | 106078.3825 | 6447.708857 |

The composition difference is **0.96637939** and density ratio is **2.7081**, so this is not the trivial identical-phase solution. Maximum raw residual is ≤5.96e-14 for these converged calls. Pressure exceeds observation by **418.375%**. This is a numerically verified dense fluid coexistence pressure; it is not a recovered low-density vapor bubble or proof of global stability.

Changing that already converged dense state's second phase back to `kind='vapor'` and passing the identical solution as the warm start still returns:

> phase V has no locally unique anchored root: vapor branch absent: the sole stable root 20147.929961303518 mol/m3 lies above the negative-slope sample 10241.92084100771 mol/m3

At fixed CO₂-rich composition y_CO₂ = 0.9827693879, direct EOS evaluation has pressure-density turning points at **8.035269956 MPa, 8870.26554 mol/m³**, and **7.958054979 MPa, 11507.76698 mol/m³**. A negative-slope interval separates the low- and high-density branches. The required 24.193 MPa lies above the low-density branch's local pressure maximum. Thus the branch rejection has a concrete EOS basis; merely changing initial pressure cannot produce the requested low-density branch. Real pure CO₂'s supplied Tc/Pc (304.13 K/7.377 MPa) do not specify this mixture EOS's critical locus. Here the CO₂-rich fluid crosses a density-branch region near 8 MPa, but the aqueous and CO₂-rich phases remain far apart. No mixture critical-point calculation was performed.

The Stage 2 run did **not** try continuation: `stage2_native` calls `reg.predict` on cold declarations and raises immediately at the first unavailable observation; `stage2_study` stops before fitting. Its README explicitly records cold initialization and no subsequent continuation call. The allowed continuation in [accepted design §2](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6158000594) was not implemented in that path.

## 2. Eight-row diagnostic fit and all-row coverage

Native one-coordinate least-squares estimation on **313.20 K rows 02–09 only**, with weight 1 and residual ln(P_pred/P_obs), converges in 3 iterations to **−0.046912921483332176**. Cost decreases from **1.1330144227953605** to **0.00005236572402471421**, with zero trial failures. This is a start-generation diagnosis only; these eight rows do not replace the 39-row objective.

| k_ij | Available/declared | 313.20 K mean absolute pressure error | 353.11 K | 373.26 K | 393.17 K |
|---|---:|---:|---:|---:|---:|
| −0.048912921483332176 | 39/39, all cold | 6.99314% | 24.33727% | 30.32261% | 30.21890% |
| −0.046912921483332176 | 39/39, all cold | 1.85916% | 21.29485% | 27.97347% | 28.77273% |
| −0.044912921483332176 | 38/39 | 11/12 available; complete-isotherm score unavailable | 18.09476% | 25.51544% | 27.27088% |

At the fitted value, all-39 cost is **1.4405975039406982** and mean absolute pressure error is **18.52004%**. Maximum raw equilibrium residual is **3.02869e-13** and minimum phase pressure-density derivative is **43.42524 Pa/(mol/m³)**. All available solutions retain distinct compositions and densities. The highest 313.20 K row is particularly sensitive: its CO₂-rich density is 9807.1098 mol/m³ and pressure 8.37843302 MPa. Row 10 gives 4.53666319 MPa (−2.79481%). High-temperature errors remain predominantly negative; solving all rows does not mean fitting all isotherms accurately.

At the upper neighbor, row 13 at 313.20 K is rejected even with eight-level continuation. Its dense-phase diagnostic coexistence pressure is **11.55221874 MPa**, densities 54,071.7424/16,626.6444 mol/m³, raw residual 3.20e-14. That result is reported separately, not substituted into the unavailable liquid/vapor observation.

Every row's signed pressure error is below. A numeric entry means **Available**, including finite pressure and the retained equilibrium evidence; **U** means unavailable after cold solve and allowed continuation. Error is 100(P_pred/P_obs−1), in percent. Exact pressures, all inputs, cold/continuation outcomes, densities and messages for every case are in `row-results.csv` and the case JSON files.

| Row | Observed MPa | Start A error % | Start B error % | Lower neighbor error % | Eight-row fit error % | Upper neighbor error % |
|---|---:|---:|---:|---:|---:|---:|
| kiepe-313.20-02 | 0.09509 | +63.268 | +275.277 | -3.610 | +0.517 | +4.838 |
| kiepe-313.20-03 | 0.24574 | +66.371 | +296.590 | -4.364 | -0.021 | +4.527 |
| kiepe-313.20-04 | 0.39751 | +68.749 | +312.857 | -4.022 | +0.420 | +5.076 |
| kiepe-313.20-05 | 0.55887 | +69.271 | +325.797 | -4.514 | -0.039 | +4.656 |
| kiepe-313.20-06 | 0.71035 | +70.794 | +342.625 | -4.341 | +0.187 | +4.941 |
| kiepe-313.20-07 | 0.88933 | +71.630 | +363.284 | -4.646 | -0.085 | +4.708 |
| kiepe-313.20-08 | 1.12480 | +73.325 | +402.927 | -4.748 | -0.132 | +4.725 |
| kiepe-313.20-09 | 1.83440 | +78.381 | U | -5.494 | -0.735 | +4.296 |
| kiepe-313.20-10 | 4.66710 | U | U | -8.377 | -2.795 | +3.304 |
| kiepe-313.20-11 | 5.66400 | U | U | -9.642 | -3.608 | +3.145 |
| kiepe-313.20-12 | 6.64380 | U | U | -11.151 | -4.526 | +3.215 |
| kiepe-313.20-13 | 9.23190 | U | U | -19.009 | -9.245 | U |
| kiepe-353.11-02 | 0.13423 | +15.565 | +103.601 | -15.328 | -13.345 | -11.282 |
| kiepe-353.11-03 | 0.57858 | +23.023 | +155.000 | -21.684 | -18.837 | -15.872 |
| kiepe-353.11-04 | 0.93380 | +24.169 | +166.866 | -22.639 | -19.678 | -16.591 |
| kiepe-353.11-05 | 1.45820 | +25.056 | +181.642 | -23.517 | -20.476 | -17.302 |
| kiepe-353.11-06 | 2.04360 | +25.884 | +200.840 | -24.234 | -21.136 | -17.897 |
| kiepe-353.11-07 | 2.72890 | +27.004 | +234.368 | -24.888 | -21.734 | -18.430 |
| kiepe-353.11-08 | 4.93900 | +31.560 | +749.414 | -26.970 | -23.660 | -20.165 |
| kiepe-353.11-09 | 6.69990 | +37.541 | +1290.394 | -28.813 | -25.383 | -21.732 |
| kiepe-353.11-10 | 8.55030 | +49.798 | +1700.015 | -30.963 | -27.406 | -23.582 |
| kiepe-373.26-02 | 0.17556 | +1.621 | +44.859 | -14.259 | -13.223 | -12.147 |
| kiepe-373.26-03 | 0.39475 | +5.026 | +84.799 | -23.944 | -22.058 | -20.101 |
| kiepe-373.26-04 | 0.50979 | +5.661 | +92.663 | -25.741 | -23.699 | -21.580 |
| kiepe-373.26-05 | 0.79506 | +6.427 | +103.551 | -28.076 | -25.841 | -23.520 |
| kiepe-373.26-06 | 1.36920 | +7.160 | +115.589 | -30.023 | -27.632 | -25.147 |
| kiepe-373.26-07 | 2.13360 | +7.749 | +128.037 | -31.272 | -28.790 | -26.206 |
| kiepe-373.26-08 | 3.31710 | +8.429 | +150.159 | -32.563 | -30.004 | -27.334 |
| kiepe-373.26-09 | 4.43780 | +9.189 | +183.946 | -33.530 | -30.917 | -28.184 |
| kiepe-373.26-10 | 5.88470 | +10.472 | +278.885 | -34.647 | -31.973 | -29.164 |
| kiepe-373.26-11 | 7.12800 | +11.723 | +407.067 | -35.666 | -32.945 | -30.078 |
| kiepe-373.26-12 | 8.18690 | +12.940 | +519.315 | -36.598 | -33.841 | -30.927 |
| kiepe-373.26-13 | 9.25760 | +14.492 | +623.479 | -37.551 | -34.759 | -31.798 |
| kiepe-393.17-02 | 0.20454 | +4.674 | +11.558 | +2.039 | +2.214 | +2.394 |
| kiepe-393.17-03 | 0.61990 | -7.937 | +47.179 | -28.752 | -27.376 | -25.953 |
| kiepe-393.17-04 | 0.84651 | -3.187 | +65.107 | -28.721 | -27.038 | -25.295 |
| kiepe-393.17-05 | 1.53450 | -7.768 | +68.714 | -35.637 | -33.811 | -31.918 |
| kiepe-393.17-06 | 4.23030 | -10.250 | +87.663 | -41.411 | -39.423 | -37.354 |
| kiepe-393.17-07 | 6.32260 | -13.053 | +102.503 | -44.753 | -42.775 | -40.711 |

## 3. Start B

B = **+0.013262879176919628** fails first at **313.20 K row 09**, x_CO₂ = 0.00713, observed 1.8344 MPa. Its cold result reports the same missing vapor branch, with the sole stable root **21998.64698493 mol/m³** above a negative-slope sample **9527.92539088 mol/m³**. Eight-level continuation does not recover it. Row 09 instead has a converged dense coexistence solution at **40.95471966 MPa**, densities **55133.20108/21998.64698 mol/m³**, raw residual **5.51e-14**. This is +2132.59% relative to observation, outside the source pressure range.

All five 313.20 K rows 09–13 are unavailable at B; rows 02–08 and all 27 higher-temperature rows solve. Thus B has **34/39** coverage. Mean absolute errors on the seven available low-temperature rows are 331.34%; on the complete 353.11/373.26/393.17 K isotherms they are **531.35/227.70/63.79%**. These partial values are not complete-start scores. The campaign never evaluated B because A stopped qualification first.

## 4. Isolating the refreshed association

Both comparison cases use **k_ij = −0.0242**, the adopted new water, and otherwise identical quantities. The old reciprocal cross energy/volume is 862.8424 K/0.0461035; the refreshed pair is 878.3248982254499 K/0.0376197279502706. Thus energy rises **1.7944%** while volume falls **18.4016%**. This probe changes the cross edges only; it does not restore the old water.

Both association cases have 35/39 coverage under the original phase declaration, with low-temperature rows 10–13 unavailable even after continuation. Among the same available rows, refreshed association raises predicted pressure by:

| Isotherm K | Matched available/declared rows | Mean relative pressure increase | Range |
|---|---:|---:|---:|
| 313.20 | 8/12 | 8.46474% | 7.61153…9.74338% |
| 353.11 | 9/9 | 9.47048% | 5.17321…17.50221% |
| 373.26 | 12/12 | 7.87086% | 3.03589…11.76892% |
| 393.17 | 6/6 | 5.37488% | 0.48649…8.09248% |

The old association already overpredicts the eight available 313.20 K rows by 51.86–62.73%; the refreshed association gives 63.42–78.59%. At row 09, pressure changes **2.98518705 → 3.27604511 MPa**. Therefore the refresh accounts for part of the increase but does not explain all of the start-A discrepancy or cure the failing branch. The refresh has a much larger relative effect on the dense row-10 continuation: **14.48691691 → 24.33284351 MPa**, a **67.9643%** increase at identical −0.0242. Both of those dense pressures remain outside the source measurement range and are separate diagnostics, not qualified vapor predictions.

All row-by-row association comparisons follow; U retains the missing vapor observation rather than using its dense counterpart.

| Row | Old P MPa | Refreshed P MPa | Refreshed/old pressure shift % |
|---|---:|---:|---:|
| kiepe-313.20-02 | 0.14440382 | 0.15539516 | +7.61153 |
| kiepe-313.20-03 | 0.37901746 | 0.40923390 | +7.97231 |
| kiepe-313.20-04 | 0.62085688 | 0.67145362 | +8.14950 |
| kiepe-313.20-05 | 0.87433600 | 0.94695139 | +8.30520 |
| kiepe-313.20-06 | 1.11984103 | 1.21447207 | +8.45040 |
| kiepe-313.20-07 | 1.40665927 | 1.52794143 | +8.62200 |
| kiepe-313.20-08 | 1.79272912 | 1.95163018 | +8.86364 |
| kiepe-313.20-09 | 2.98518705 | 3.27604511 | +9.74338 |
| kiepe-313.20-10 | U | U | — |
| kiepe-313.20-11 | U | U | — |
| kiepe-313.20-12 | U | U | — |
| kiepe-313.20-13 | U | U | — |
| kiepe-353.11-02 | 0.14757893 | 0.15521350 | +5.17321 |
| kiepe-353.11-03 | 0.66432157 | 0.71235453 | +7.23038 |
| kiepe-353.11-04 | 1.07870174 | 1.16045462 | +7.57882 |
| kiepe-353.11-05 | 1.69116223 | 1.82514151 | +7.92232 |
| kiepe-353.11-06 | 2.37848812 | 2.57489123 | +8.25748 |
| kiepe-353.11-07 | 3.19267086 | 3.46908902 | +8.65790 |
| kiepe-353.11-08 | 5.89625711 | 6.50507412 | +10.32548 |
| kiepe-353.11-09 | 8.19626999 | 9.22789189 | +12.58648 |
| kiepe-353.11-10 | 10.92212699 | 12.83374104 | +17.50221 |
| kiepe-373.26-02 | 0.17320743 | 0.17846581 | +3.03589 |
| kiepe-373.26-03 | 0.39320087 | 0.41483454 | +5.50194 |
| kiepe-373.26-04 | 0.50866217 | 0.53899352 | +5.96296 |
| kiepe-373.26-05 | 0.79456361 | 0.84674815 | +6.56770 |
| kiepe-373.26-06 | 1.37068120 | 1.46834526 | +7.12522 |
| kiepe-373.26-07 | 2.13915229 | 2.30076646 | +7.55506 |
| kiepe-373.26-08 | 3.33041867 | 3.59975017 | +8.08702 |
| kiepe-373.26-09 | 4.46623460 | 4.84995369 | +8.59156 |
| kiepe-373.26-10 | 5.95206798 | 6.50729267 | +9.32827 |
| kiepe-373.26-11 | 7.24191694 | 7.97202195 | +10.08165 |
| kiepe-373.26-12 | 8.35121476 | 9.25683147 | +10.84413 |
| kiepe-373.26-13 | 9.49487041 | 10.61231421 | +11.76892 |
| kiepe-393.17-02 | 0.21307586 | 0.21411245 | +0.48649 |
| kiepe-393.17-03 | 0.54606621 | 0.57097160 | +4.56087 |
| kiepe-393.17-04 | 0.77815395 | 0.81998842 | +5.37612 |
| kiepe-393.17-05 | 1.33288854 | 1.41621333 | +6.25145 |
| kiepe-393.17-06 | 3.53509465 | 3.79958590 | +7.48187 |
| kiepe-393.17-07 | 5.08995352 | 5.50185692 | +8.09248 |

## 5. Smallest correct remedy

Recommend an **owner-approved design amendment to start generation**, followed by normal full-39 qualification and fitting: use the eight-row provisional estimate and a separately qualified neighboring interaction as the two Stage 2 starts. The tested **−0.046912921483332176** and **−0.048912921483332176** both give 39/39 cold solutions with unchanged phase declarations and tolerances. Preserve the original A/B failures as evidence; use all 39 rows in every final fit and replay. The eight-row diagnostic result is only a starting vector, never the accepted binary endpoint. Implement the already allowed bounded continuation for later start/endpoint qualification where useful, but do not expect continuation alone to repair the present A/B root restriction.

This requires an amendment because accepted §2 specifically names A/B and requires both to qualify. It requires neither restoring old association nor dropping rows nor inventing an accuracy cutoff. A final all-row optimizer may still encounter branch-restricted trial states; the current probes establish feasible starts, not a guaranteed complete optimizer trajectory or endpoint.

If the intended calculation must also evaluate dense incipient CO₂-rich states at A/B, send Engine the exact reproduction above: immutable wheel; serialized A start/reference; row 10 T/feed; original zero-amount incipient phase; and the `vapor` rejection beside the converged `liquid` declaration and identical-state warm-start rejection. Ask whether `vapor` is deliberately limited to the low-density root or should admit this dense fluid branch. The evidence identifies a **phase-root selection limitation**; it does not establish an error in the EOS or nonlinear equations. Simply relabeling the phase in the campaign would change declared phase behavior and needs an explicit decision and phase-stability assessment. No Engine report was written and no remedy was implemented here.

## Sources read and limits

Kiepe (2002), [DOI 10.1021/ie020154i](https://doi.org/10.1021/ie020154i), original Zotero PDF `P9HDI8CX/WYBWWKE8`, SHA-256 `8e93b3922f4a0b5cb1001efb9b5d97e07fc5cd9b80d0c1e57a967fea21898f51`: read Experimental §2.2, Table 1 printed p.4394, data reduction pp.4394–4395, and Results §3. The exact Table 1 temperatures/compositions/pressures match the diagnostic inputs. The worktree has no literature shelf; the main checkout's shelf/index is available. Kiepe has no Markdown companion, so its actual PDF was read using local text extraction without conversion or source writes. Kiepe's static synthetic measurements and data reduction concern coexisting fluids; the pure-component supercritical temperature alone is not a proof of no mixture coexistence.

Pabsch (2020), [DOI 10.1021/acs.jced.0c00704](https://doi.org/10.1021/acs.jced.0c00704), methods/parameter sections, Table 2, Eqs.15–18, binary-data comparison and fitting results/Tables5–6: read the existing indexed shelf copy and verified it byte-for-byte against current Zotero `TBPJLBZT` (SHA-256 `21f91300e2a7de10a295667cabe521d2b729b283a20a9b48021d04c2c710d190`). Its source parameterization uses temperature-dependent interactions conditioned on its own pure quantities. This diagnosis preserves the accepted constant-interaction experiment and does not recommend a new source parameterization or validation standard. No exact source equation was changed or newly transcribed.

The results are **numerical verification and conditional comparisons to calibration data**, not independent physical validation. Neither global tangent-plane stability nor the mixture critical locus nor parameter uncertainty was calculated. Positive pressure-density slopes and small equilibrium residuals verify the returned local states only. No fitted full-39 endpoint, derivative qualification, replay, or investigator adoption follows from this scratch subset fit. Failure at original A/B is not proof that a constant k_ij model cannot be calibrated. Conversely, all-row availability at the new starts does not prove a sufficiently accurate all-isotherm fit exists. The large temperature-dependent residual pattern remains to be assessed by the authorized full-data estimation.

## Work limits and retained evidence

Measured CPU inside all probe scripts is **47.063097 CPU-s**, summed active wall time **47.353166 s**; longest measured batch **10.161779 s**. Conservatively charge **60 CPU-s** including interpreter/import work, the one rejected optional-kind declaration, and wheel checking; this is below the 300 CPU-s limit. Every probe command had a 60-second outer wall timeout, ran at nice level 10, and used single-threaded numerical libraries (one native fit worker). No limit was extended.

`row-results.csv` preserves 273 requested case/row evaluations, including every unavailable pressure. `A/B/fitted/lower/upper/old/newrounded.json` preserve final per-row values; `*-calls.json` preserve all cold and continuation attempts. `fit8.json` retains the native subset fit; `dense-calls.json`, `root-calls.json`, `root-scan.json`, and `association-dense-calls.json` retain the discriminating dense-root results. `*-timing.json`, wheel checking, exact issue/source reads, and probe scripts remain in this scratch directory. No live notebook or accepted parameter record was updated.
