# Selected Held-vector assessment

The selected vector passes the specified fitted-density, CO2-free density and aggregate heat gates. Report-only concentration-transfer, Matin pool and carbonate-share discrepancies remain large. This is an assessment of a fitted vector; non-fitted rows are predictions. It is not physical validation or parameter adoption.

Parameter SHA-256: `ceefc95cd051fb291e0c08675c4cb6f159bf10dca0116ef1251ba78c243f79c7`. Engine wheel SHA-256: `d2f61e3a5961b859151fbe0487f4ab633405b11620d9dd64682656a68a110357`. The installed wheel comes from merged Engine commit `21e761c318c2ac5b555a245365c844d38a93e4cb`. `provenance.json` binds the parameter document, declaration, native fit, selection scores and accepted design; `input-hashes.json` binds source tables and producers.

## Density

| Cohort | Available / requested | Bias (kg/m3) | RMSE (kg/m3) | AARD (%) | Disposition |
|---|---:|---:|---:|---:|---|
| Amundsen2009 | 103/103 | -2.79864 | 4.95827 | 0.300909 | report only |
| Amundsen2009 loaded | 68/68 | -3.52152 | 5.85461 | 0.367274 | report only |
| Amundsen2009 unloaded | 35/35 | -1.39419 | 2.39883 | 0.171969 | report only |
| Amundsen fitted 15 | 15/15 | -0.738972 | 2.1001 | 0.157973 | pass 15/15 within 2s |
| Amundsen source-conflict five | 5/5 | -8.58214 | 8.64635 | 0.794864 | report only |
| Amundsen CO2-free gate five | 5/5 | 0.0171505 | 0.354223 | 0.0290012 | pass 5/5 within 1.0 kg/m3 |
| Hartono2014 | 40/40 | 1.79141 | 3.53349 | 0.244551 | report only |
| Hartono fitted 32 | 32/32 | 0.469182 | 1.68835 | 0.144107 | pass 32/32 within 2s |
| Hartono loading 0.50 eight | 8/8 | 7.08034 | 7.14323 | 0.646326 | report only |
| Han2012 | 67/67 | 0.132501 | 7.54853 | 0.445186 | report only |
| Han2012 loaded | 50/50 | 0.105467 | 8.72484 | 0.577892 | report only |
| Han2012 unloaded | 17/17 | 0.212015 | 0.823851 | 0.0548737 | report only |

All 210 density rows are available. `density.csv` gives predictions, signed errors, source uncertainties, propagated residual scales where defined, and row identities. All 47 loaded objective densities were replayed through `stage6_rows` (which also calls `stage2_rows`) using the exact explicit parameter document and analytical feeds. The five CO2-free gate rows were evaluated through `unloaded_density_problem`, the same producer used by `stage2_rows`; their source IDs are explicitly mapped to the AMU-DENS fit IDs in `verification.json`. All 52 agree with their native-fit predictions within 1e-8 kg/m3. Other loaded rows use the existing source-feed and native density route; unloaded rows use exact zero analytical carbon, with protonation retained. Seven neat-MEA states use native pure-MEA support. Amundsen/Hartono pressure is assumed 100000 Pa; Han uses each stated source pressure. No empirical volume translation is applied.

The five excluded source-conflict rows are Amundsen states 063, 068, 073, 078 and 082. Their signed errors range from -10.3235 to -7.71234 kg/m3. They remain outside the objective and gate. Loaded Amundsen uncertainties outside the adopted scale table remain unbound; general source estimates are retained as such. The gate uses the adopted propagated s values, not a universal 2 kg/m3 limit.

Hartono loading-0.50 is assessment-only (eight rows). Its printed uncertainty and adopted composition assumption are retained without assigning a new propagated fitting scale. Han is assessment-only: 6/50 loaded and 9/17 unloaded errors fall within the stated combined density uncertainties; 12/50 and 13/17 fall within the stated expanded uncertainties. These are counts against source uncertainty fields, not adoption gates.

## Hilliard heat capacity

Exactly 7 mol MEA/kg water, 101325 Pa, loadings 0/0.358. Cp is per kg complete loaded analytical feed. The final conversion uses the molar masses declared in the parameter document. The helper uses a slightly different hard-coded mass vector; its original values, the frozen-source intermediate conversion, and the final mass conversion are retained in `cp-summary.json`. No Engine action or equation was changed.

| T (K) | Loading | Observed Cp | Equilibrium Cp | Frozen Cp | Error (%) | Numerical checks |
|---:|---:|---:|---:|---:|---:|---|
| 318.15 | 0.0 | 3.7195 | 3.9069087 | 3.90689496 | +5.03855 | pass |
| 318.15 | 0.358 | 3.3675 | 3.45420541 | 3.43302731 | +2.57477 | pass |
| 353.15 | 0.0 | 3.8566 | 3.88562657 | 3.8855324 | +0.752647 | pass |
| 353.15 | 0.358 | 3.4707 | 3.41674199 | 3.38673688 | -1.55467 | pass |

Cp units are kJ/(kg K). All six evaluations pass the re-solved total-enthalpy checks at 0.1/0.05 K, including the required error decrease. Both zero-loading states pass the 1e-6 versus 1e-7 proxy comparison (relative differences 2.24988e-07, 2.61288e-07). Three of four states are within 3% of the observed Cp; the 318.15 K unloaded state is outside. Cp adequacy is report-only. Per-step enthalpies, residuals, proxy feeds and mass bases are retained. No pure-water sweep was run; complete #189 input-identity reuse was not independently established by this subtask.

## Integral heats

| Cohort | Available / requested | Bias (kJ/mol CO2) | AARD (%) | RMSE (kJ/mol CO2) | Gate |
|---|---:|---:|---:|---:|---|
| Vinjarapu2024 | 8/8 | 0.337216 | 1.91821 | 1.82153 | pass; ceiling 3.13 |
| Arcis2011 | 14/14 | 7.11314 | 7.66728 | 8.05036 | pass; ceiling 9.36 |
| Arcis2011 at 510000.0 Pa | 8/8 | 10.1413 | 10.7747 | 10.259 | pressure subset; report only |
| Arcis2011 at 1030000.0 Pa | 6/6 | 3.07557 | 3.52409 | 3.29999 | pressure subset; report only |

All 22 heat rows are available. Negative integral addition enthalpy releases heat; the reference is zero loading. Vinjarapu is fitted; Arcis is outside the objective and was previously accessed. The Arcis gate applies to the combined 14-row RMSE, not separately to its pressure subsets. `heats.csv` retains all errors and IDs.

## Pressure and pooled species

| Cohort | Available | AARD (%) | Mean ln(calc/obs) | Mean signed relative error (%) |
|---|---:|---:|---:|---:|
| canonical | 159 | 20.86162 | -0.12512566 | -8.300975 |
| packet | 79 | 15.79345 | 0.016851758 | 3.804043 |
| transfer | 70 | 168.7131 | -0.10090179 | 97.06037 |
| wagner | 23 | 20.10415 | -0.23079503 | -20.10415 |
| canonical 100-120 C | 54 | 24.51233 | -0.10454222 | -5.90264 |
| packet 100-120 C | 20 | 25.37196 | 0.073473023 | 11.76852 |
| canonical 100-120 C Jou1995 100 C | 10 | 18.18194 | 0.068996209 | 9.4271 |
| canonical 100-120 C Jou1995 120 C | 10 | 32.56198 | 0.077949837 | 14.10993 |
| canonical 100-120 C Mamun2005 120 C | 19 | 23.14027 | -0.26526499 | -23.14027 |
| canonical 100-120 C Xu2011 100 C | 8 | 26.50193 | -0.30605018 | -22.8039 |
| canonical 100-120 C Xu2011 120 C | 7 | 23.50658 | 0.053385146 | 9.711924 |
| packet 100-120 C Jou1995 100 C | 10 | 18.18194 | 0.068996209 | 9.4271 |
| packet 100-120 C Jou1995 120 C | 10 | 32.56198 | 0.077949837 | 14.10993 |
| Wagner near 353.15 K | 11 | 25.47501 | -0.2956337 | -25.47501 |
| Wagner near 392.15 K | 12 | 15.18086 | -0.17135959 | -15.18086 |
| transfer 15 wt% | 33 | 281.8668 | 1.2759132 | 281.8668 |
| transfer 45 wt% | 37 | 67.7921 | -1.3288719 | -67.76702 |
| Matin 19 pools | 19 | 66.78818 | -1.2218114 | -66.78818 |

All 375 admitted states are available: 123 packet, 159 canonical pressure, 70 transfer, and 23 Wagner states. The packet includes 79 pressure targets. The 54 canonical high-temperature rows comprise 18 nominal-100 C and 36 nominal-120 C rows; the separate 20-row packet cohort comprises ten plus ten. The source identities returned by the existing producer label all 20 packet rows Jou1995. Canonical/packet overlap is retained and is not independent replication. Individual pressure errors and signed biases in Pa are in `state-targets.csv` and `state-summary.json`; source/temperature reductions use the retained nominal cohorts while preserving measured temperatures.

The explicitly inadmissible canonical rows are vle_obs_0286 (393.55 K), vle_obs_0287 (394.15 K), and vle_obs_0288 (394.95 K). They are not included in the 159 or high-temperature reductions. No admitted case is unavailable or dropped.

All 19 Matin pools are x(HCO3-) + x(CO3^2-), including state 016 at printed loading 0.455 with the corrected request. Pool cost is 33.5122148575 in the existing residual convention. On the same vector, common149 cost is 24.9230852708, pressure AARD 12.4736694% and species AARD 7.14513803%. The pool is report-only and outside F1 fitting; these numbers describe the selected vector's calibration/pool trade-off. No F4/F5 or no-heat comparison was selected here.

## Jakobsen carbonate share

All ten corrected liquid-only 101325-Pa calculations are available. Each uses w=0.2714274817259226 and its printed loadNMR. The share is n(CO3^2-)/[n(CO2)+n(MEACOO-)+n(HCO3-)+n(CO3^2-)]. The observed share is calculated directly from the printed species, with historical maxload-based membership preserved.

| Cohort | Available | Calc/obs minimum | Calc/obs maximum |
|---|---:|---:|---:|
| all ten | 10 | 0.00633595385 | 0.350313127 |
| historical nine | 9 | 0.0145532845 | 0.350313127 |
| previously excluded 40 C maxload 0.21 | 1 | 0.00633595385 | 0.00633595385 |

The historical nine states are 009-013, 017, 019-021; the separately displayed 40 C/maxload-0.21 state is 018. Fitted ratio state 011 overlaps this set; state 022 is outside. Approximate dilution, mole-for-mole D2O-as-water, omitted dioxane, inferred loadNMR and the unresolved source denominator remain the accepted limitations. No nominal-state interpolation is used. The first ten bubble-template attempts were superseded and retained under `superseded-carbonate-bubble/`; final reductions read only the fixed-pressure replay.

## Numerical evidence and handoff

Measured Engine-call total: **93.76 wall-s, 274.74 CPU-s**, including initial and superseded attempts. The allocation is 1000 wall-s / 2000 CPU-s. `calls.json` owns the call accounting; every call has a GNU-time JSON and execution log. Exact declared density replay differs from the vector's native fit by at most 1.81899e-12 kg/m3. Heat replay differs by at most 2.96859e-08 J/mol. All four mass-converted Cp values match their native-fit predictions within 1e-10 kJ/(kg K). Across 375 state checks, maximum stationarity residual is 7.10543e-13, maximum material residual 7.13207e-13 mol and maximum charge residual 2.27275e-13 mol. These are finite-state numerical checks, not evidence of global stability or physical validation.

Primary files: `summary.json`, `density.csv`, `density-summary.json`, `cp.csv`, `cp-summary.json`, `heats.csv`, `heat-summary.json`, `state-targets.csv`, `state-summary.json`, `carbonate-share.csv`, `carbonate-summary.json`, `verification.json`, `calls.json`, `provenance.json`, `input-hashes.json`. Raw per-row results, numerical evidence, exact carbonate requests, exclusions, logs and superseded attempts are retained alongside them. Disclosed one-off drivers are `assess.py.txt`, `run-budget.py.txt`, and `reduce.py.txt`.

The final driver separates density, calorics (heats only), cp, states, carbonate and declared-density modes so a fresh replay has one owner per cohort. Historical call logs include the earlier combined modes; their superseded rows remain separate. Reproduction uses the pinned interpreter and environment captured in calls.json, through run-budget.py.txt; reduction uses system Python and never imports the Engine.

Not done: paired with/without-heat assessment (no explicit comparison vector supplied); complete historical #189 pure-water qualification input binding; parent-owned notebook integration, independent review, and investigator promotion. Phase-family and gas-root work is outside this subtask. Every requested selected-vector cohort has a usable explicit-document producer and was evaluated. No campaign producer, fit, external ledger or Git state was edited. Only selected-assessment/ was written.
