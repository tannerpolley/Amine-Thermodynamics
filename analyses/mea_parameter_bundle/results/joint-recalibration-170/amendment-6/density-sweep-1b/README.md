# Amendment 6, step 1b: density-weighted F1 fits and a second density source (#170)

Run 2026-10-19 on Engine wheel `main-21e761c3` (sha256 `d2f61e3a…0357`).

**Authority.** Owner, 2026-10-19: "figure this out and try to solve this discrepancy any means necessary". This lifted the runner stop recorded in `../density-sweep/README.md`.

**Scope.** Larger d_V branch, start A, all declarations, no new campaign code.
- **Fits:** the step-1 fit declarations with `maximum_iterations` raised from 100 to 180.
- **Allowance:** 3,500 compute-wall s and 30,000 CPU-s within the program caps. Step 1b used **1,067.49 s and 9,699.09 CPU-s** over 26 calls (`step-ledger.json`).
- **Reported numbers:** all come from `reduce.py.txt`, which reads retained arrays only, and its output `summary.json`.

## Result

**Weighting density removes the gross loaded-density error at little calibration cost.** The remaining few kg/m³ sit where the two density sources disagree with each other.

| Endpoint (all converged) | Iterations | C149 | C166 | Pressure / species AARD, % | Vinjarapu RMSE, kJ/mol | Amundsen 12 fitted rows, kg/m³ | Amundsen 8 assessment rows | Hartono 32 rows (printed loading) | CO₂-free 5 rows within 0.5 kg/m³ |
|---|---:|---:|---:|---|---:|---|---|---|---:|
| λ = 0 (A4 control) | 84 | 24.561 | 39.690 | 12.76 / 7.17 | 1.515 | −108.2 to −24.3 | — | — | 3 |
| λ = 0.01, Amundsen targets | 101 | 24.586 | 40.743 | 12.36 / 7.12 | 1.789 | −24.4 to −2.8 | — | — | 4 |
| λ = 0.1, Amundsen targets | 75 | 23.472 | 41.361 | 11.82 / 7.05 | 1.879 | −6.07 to +2.51 (6 within 2) | −7.31 to +2.47 (3) | −0.60 to +5.09 (6) | 4 |
| λ = 1, Amundsen targets | 13 | 24.726 | 41.313 | 12.44 / 7.10 | 1.881 | −3.58 to +2.87 (4) | −4.52 to +2.83 (3) | +0.55 to +6.26 (3) | 4 |
| **λ = 1, Hartono targets** | 36 | 24.678 | 41.147 | 12.40 / 7.10 | 1.855 | −9.22 to +0.85 (6) | −10.12 to +1.03 (4) | **−3.42 to +2.05 (27)** | 4 |

- **Notation:** density errors are model minus measurement. Counts in parentheses are rows within ±2 kg/m³. AARD is the average absolute relative deviation; RMSE is the root-mean-square error.
- **C149** is the paper's 149 common rows; **C166** adds the restored species, Jakobsen ratios and heat-capacity rows (Kiepe and density excluded).
- **Heat capacity** is unchanged at every endpoint: +3.31 % at 318 K unloaded.
- **CO₂-free row that misses:** the 25 °C row, at −0.98 to −1.09 kg/m³.

**Ion sizes:**

| Endpoint | MEAH⁺ σ | Carbamate σ |
|---|---:|---:|
| λ = 0.01 | 4.467 Å | 5.8 Å (bound) |
| λ = 0.1 | 4.825 Å | 5.330 Å (both interior) |
| λ = 1 | 4.043 Å | 5.8 Å (bound) |
| Hartono-targeted | 4.164 Å | 5.8 Å (bound) |

Both Born diameters stay at their 5.0 Å bound throughout.

**Reading.**
1. **The gross error came from leaving density out of the fit.** Every joint-refit fit before amendment 6 had density weight 0. Weighting density moves the ion sizes off the λ = 0 pattern and cuts the loaded-density error by one to two orders of magnitude. The common rows stay within about 1 % of λ = 0, and pressure and species improve slightly. Vinjarapu heat worsens from 1.52 to 1.86–1.88 kJ/mol, still below the paper record's 2.13. C166 rises about 4 %.
2. **The two density sources disagree at high loading.** Hartono, Mba & Svendsen 2014 report 30 wt % loaded densities at ±0.02 kg/m³ and ±0.01 loading (Table 3, p. 1810). Linearly interpolated in loading, Amundsen 2009 lies **+0.4 to +1.6 kg/m³** above Hartono at loadings 0.1–0.3 and **+8.5 to +9.1 kg/m³** above at 0.4, at all five shared temperatures.
3. **One model matches either source, not both, where they disagree.**
   - Fitted to Amundsen, it is within −3.6 to +2.9 kg/m³ of Amundsen, but +0.6 to +6.3 above Hartono.
   - Fitted to Hartono, it is within −3.4 to +2.1 of Hartono (27 of 32 within 2 kg/m³). It is also within ±1 kg/m³ of Amundsen at loadings 0.1–0.2, but 3–10 kg/m³ below Amundsen at 0.3–0.4.
   - Hartono's residuals zig-zag by about ±2 kg/m³ across loadings, the size its ±0.01 loading uncertainty implies at about 200 kg/m³ per unit loading.
4. **Linear screens of model-form changes don't close the gap.** These covered free segment counts, untied packing or Debye–Hückel diameters, and the ion-pair k_ij beyond −1 (GPT-6.1 Sol diagnosis rounds 1–2, retained arrays only, `/tmp/density-diag*/`, not committed). None credibly meets ±2 kg/m³ on all 12 Amundsen rows at no more than a 5 % C149 increase. The best small-move screen gives a maximum error of about 2.03 kg/m³. Those are linear predictions; the endpoint-to-endpoint check shows they are unreliable for large moves.

**Not established here.** None of these endpoints is a candidate:
- the flash family, gas-root falsifier and comparison fits have not been run on them;
- they have not been independently reviewed;
- the λ choice is still open.

The Hartono rows are a **diagnostic transcription**, not adopted data (`hartono-check/rows.json`). Its printed loadings and the CO₂ mole fractions printed beside them imply loadings that differ by 0.006–0.012, which is about 1–2.5 kg/m³ at the density slope. Both readings were evaluated (`hartono_x3` in `summary.json`), and adopting the data must resolve which is right.

## Checks

- **Iteration path:** deterministic. The λ = 0.01 rerun with 180 iterations retraced the step-1 run's first 101 iteration costs exactly (largest difference 0.0) and converged at iteration 101.
- **Endpoint replays:**

  | Endpoint | Rows | Largest weighted-row difference |
  |---|---:|---:|
  | λ = 1 | 217 | 5.3e-12 |
  | λ = 0.1 | 217 | 6.4e-12 |
  | λ = 0.01 | 217 | 1.0e-11 |
  | Hartono fit | 201 shared objective rows | 2.2e-12 |

- **Start release tests** pass at every declared λ, including the Hartono-target start (augmented condition 4,055).
- **Assessment rows:** the 8 unfitted Amundsen rows (40 and 80 °C) and the Hartono rows were evaluated in the 16 direct-row slots, since `stage6_rows` asserts that count. Fitted rows placed in the same calls reproduce the endpoint evaluations exactly.
- **CO₂-free rows:** evaluated with the existing `fit_observations.stage2_rows` and `predict` path. This was a one-off disclosed scratch call, and its text is kept in `unloaded-eval-scratch.py.txt`.
- **Not run:** independent centered-difference derivative checks.
