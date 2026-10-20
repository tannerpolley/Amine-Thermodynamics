# Accepted A7 endpoint: full assessment and gas-root falsifier

The endpoint is the owner-accepted second restricted fit (#170 comment 6298116916),
`../restricted-2/fit/usable-budget-endpoint.json`, SHA-256 `e234e860…`, on Engine
8298c602 (wheel `8897a0ca…85b3`). It has no resolved descent at the 73 family points.
Three 353.15 K loaded densities miss the 2s gate, and that miss is disclosed as a limitation
(`../restricted/README.md`). This is an assessment of a fitted vector: non-fitted rows
are predictions. It is numerical evidence, not physical validation or adoption.

Producers are unchanged copies of `amendment-6/selected-assessment/assess.py.txt` and
`reduce.py.txt`. The changes are this record's paths, its SHA-256, one solved-state
T/P read for the scalar Engine interface, a C149 cross-check against this endpoint's
gate score, and budget accounting from `../step-ledger.json`. Values are in
`summary.json`, `verification.json` and the per-row CSV files. A6 is the
retained selected Held vector assessed in `amendment-6/selected-assessment/`.

## Gates and assessment rows

| Quantity | A7 accepted | A6 selected | Role |
|---|---:|---:|---|
| Amundsen fitted 15 densities within 2s | 14/15 (gate fails) | 15/15 | gate, disclosed |
| Hartono fitted 32 densities within 2s | 30/32 (gate fails) | 32/32 | gate, disclosed |
| Amundsen CO₂-free five, all \|e\| ≤ 1.0 kg/m³ | pass, RMSE 0.341 | pass, 0.354 | gate |
| Vinjarapu 8 heats RMSE, kJ/mol | 1.835 (≤ 3.13, pass) | 1.822 | gate |
| Arcis 14 heats RMSE, kJ/mol | 8.114 (≤ 9.36, pass) | 8.050 | gate; outside the objective |
| Common 149-target cost | 23.866 | 24.923 | gate ≤ 35.26 |
| All 210 densities: Amundsen 103 / Hartono 40 / Han 67 RMSE, kg/m³ | 6.42 / 2.42 / 5.91 | 4.96 / 3.53 / 7.55 | report |
| Hartono loading 0.50 (8) RMSE, kg/m³ | 3.23 | 7.14 | report |
| Amundsen source-conflict five RMSE, kg/m³ | 10.27 | 8.65 | report; excluded from fit |
| Hilliard Cp error at 318.15 K α 0 / α 0.358; 353.15 K α 0 / α 0.358 | +5.53 / +2.57 / +1.15 / −2.13 % | +5.04 / +2.57 / +0.75 / −1.55 % | report |
| Pressure AARD: canonical 159 / packet 79 / Wagner 23, % | 20.55 / 15.47 / 15.45 | 20.86 / 15.79 / 20.10 | report |
| Concentration transfer 70 (15 and 45 wt %) AARD, % | 43.52 | 168.71 | report |
| Canonical 100–120 °C (54) pressure AARD, % | 24.35 | 24.51 | report |
| Matin 19 species pools AARD, % | 67.48 | 66.79 | report |
| Jakobsen carbonate share, mean calc/obs (10 states) | 0.073 | 0.083 | report |

All 210 densities, 22 heats, 4 Cp states and 375 admitted states are available, with no
failed evaluation. Three canonical states above 393.15 K are inadmissible, as in A6. The
318.15 K unloaded Cp is outside 3 %, as it is for A6. Heats are the integral addition
enthalpy with a zero-loading reference. The Arcis gate applies to the combined 14 rows.

## Gas-root falsifier

`../gas-root/run-2/gas-root.json`: **pass**. The state is 318.15 K, 3699.0803800848512 Pa,
α 0.25557798094241313. Both native density-root requests return the same sole ionic
root, denser than the newly solved liquid, so no separate stable ionic gas root exists. The
physical solve and the 10⁻⁶–100 mol/m³ dilution scan completed. The first attempt
(`../gas-root/run/`, 5.65 wall-s) stopped at an input path the copy had not updated
(`engine-decomposition.csv`), before witness evaluation, root requests, dilution scanning and the physical
solve; Engine initialization and problem compilation had already occurred. It is retained and charged.

## Numerical verification

| Check | Value |
|---|---|
| 47 declared loaded densities plus 5 exact-zero-carbon rows against the fit's native predictions | max \|Δ\| 1.2 × 10⁻¹¹ kg/m³ |
| Vinjarapu heats against native | max \|Δ\| 4.2 × 10⁻⁹ J/mol (scaled 1.4 × 10⁻¹²) |
| Hilliard Cp against native, mass converted | max \|Δ\| 3.3 × 10⁻¹⁴ kJ/(kg K) |
| Common 149 cost against the endpoint's 307-row gate score | equal within 10⁻⁸ (23.86596394718697) |
| 375 states: max stationarity / material / charge residual | 2.2 × 10⁻¹² / 8.5 × 10⁻¹³ mol / 2.1 × 10⁻¹³ mol |

The release derivative tests, the 307-row cold replay, the ties and the 39 Kiepe residual
checks belong to the fit (`../restricted-2/release/`, `../restricted-2/replay/`).

## Compute

Stage final-evidence (reserve 1,950.38 / 9,200): two gas-root attempts 5.65 + 6.10
wall-s; seven assessment calls 105.63 wall-s / 274.96 CPU-s. The stage total is
117.38 / 286.59. All A7 calls total 1,614.64 wall-s / 3,544.75 CPU-s, charged to the
program ledger at integration.

Not done: adoption. The notebook section is integrated; delivered review r1 corrections are applied.
