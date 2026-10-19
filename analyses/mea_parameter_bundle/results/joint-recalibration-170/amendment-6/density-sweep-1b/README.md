# Amendment 6, step 1b: density-weighted F1 fits and a second density source (#170)

Run 2026-10-19 on Engine wheel `main-21e761c3` (sha256 `d2f61e3a…0357`).

**Authority.** Owner, 2026-10-19: "figure this out and try to solve this discrepancy any means necessary". This lifted the runner stop recorded in `../density-sweep/README.md`.

**Scope.** Larger d_V branch, start A, all declarations, no new campaign code.
- **Fits:** the step-1 fit declarations with `maximum_iterations` raised from 100 to 180.
- **Allowance:** 3,500 compute-wall s and 30,000 CPU-s within the program caps. Step 1b used **1,067.49 s and 9,699.09 CPU-s** over 26 calls (`step-ledger.json`).
- **Reported numbers:**
  - the endpoint tables, densities and the source disagreement come from `reduce.py.txt`, which reads retained arrays only, and its output `summary.json`;
  - the replays, the determinism check and the linear screens come from the checks below and from `linear-screens/`.

## Result

**Weighting density cuts the loaded-density error by one to two orders of magnitude. No endpoint passes the existing density gate.**

| Endpoint (all converged) | Iterations | C149 | C166 | Pressure / species AARD, % | Vinjarapu RMSE, kJ/mol | Amundsen 12 fitted rows, kg/m³ | Amundsen 8 assessment rows | Hartono 32 rows (printed loading) | CO₂-free 5 rows within 0.5 kg/m³ |
|---|---:|---:|---:|---|---:|---|---|---|---:|
| λ = 0 (A4 control) | 84 | 24.561 | 39.690 | 12.76 / 7.17 | 1.515 | −108.2 to −24.3 | — | — | 3 |
| λ = 0.01, Amundsen targets | 101 | 24.586 | 40.743 | 12.36 / 7.12 | 1.789 | −24.4 to −2.8 | — | — | 4 |
| λ = 0.1, Amundsen targets | 75 | 23.472 | 41.361 | 11.82 / 7.05 | 1.879 | −6.07 to +2.51 (6 within 2) | −7.31 to +2.47 (3) | −0.60 to +5.09 (6) | 4 |
| λ = 1, Amundsen targets | 13 | 24.726 | 41.313 | 12.44 / 7.10 | 1.881 | −3.58 to +2.87 (4) | −4.52 to +2.83 (3) | +0.55 to +6.26 (3) | 4 |
| **λ = 1, Hartono targets** | 36 | 24.678 | 41.147 | 12.40 / 7.10 | 1.855 | −9.22 to +0.85 (6) | −10.12 to +1.03 (4) | **−3.42 to +2.05 (27)** | 4 |

- **Notation:** density errors are model minus measurement. Counts in parentheses are rows within ±2 kg/m³. AARD is the average absolute relative deviation; RMSE is the root-mean-square error.
- **C149** is the paper's 149 common rows; **C166** adds the restored species, Jakobsen ratios and heat-capacity rows. Kiepe and density are excluded, and each value comes from the fit's own `native.json`.
- **The existing gate: no endpoint passes.** Across the 20 Amundsen loaded rows within ±2 kg/m³: λ = 0.1 gets 9 of 20, λ = 1 (Amundsen targets) 7, and λ = 1 (Hartono targets) 10. Every new endpoint passes 4 of the 5 CO₂-free rows; the 25 °C row is −0.98 to −1.03 kg/m³.
- **Heat capacity:**
  - *Unloaded:* nearly unchanged, at +3.313 % (λ = 0) and +3.317 % (λ = 0.1) at 318 K.
  - *Loaded:* it changes. At 318 K and loading 0.358 the error goes from +1.548 % to +2.201 % at λ = 0.1.

**Ion sizes:**

| Endpoint | MEAH⁺ σ | Carbamate σ |
|---|---:|---:|
| λ = 0.01 | 4.467 Å | 5.8 Å (bound) |
| λ = 0.1 | 4.825 Å | 5.330 Å (both interior) |
| λ = 1 | 4.043 Å | 5.8 Å (bound) |
| Hartono-targeted | 4.164 Å | 5.8 Å (bound) |

Both Born diameters stay at their 5.0 Å bound throughout.

**Reading.**
1. **The gross error came from leaving density out of the fit.** Every joint-refit fit before amendment 6 had density weight 0. Weighting density cuts the loaded-density error by one to two orders of magnitude. The trade-off against λ = 0, for the λ = 0.1 and λ = 1 endpoints:

   | Measure | Change |
   |---|---|
   | C149 | −4.4 % (λ = 0.1), +0.5 % and +0.7 % (λ = 1) |
   | C166 | +3.7 to +4.2 % |
   | Pressure and species AARD | slightly better |
   | Vinjarapu RMSE | **+22 to +24 %** (1.515 → 1.855–1.881 kJ/mol; the paper record has 2.13) |

   "Little calibration cost" holds only for the aggregate costs, and comes with that heat penalty.
2. **The two density sources disagree at high loading.** Hartono, Mba & Svendsen 2014 report 30 wt % loaded densities at ±0.02 kg/m³ and ±0.01 loading (Table 3, p. 1810). Amundsen 2009 lies above Hartono by:

   | Loading | Amundsen − Hartono, kg/m³ |
   |---:|---|
   | 0.1 | +0.42 to +1.09 |
   | 0.2 | +0.68 to +1.00 |
   | 0.3 | +1.30 to +1.56 |
   | 0.4 | **+8.50 to +9.07** |

   These are at all five shared temperatures, using linear interpolation in Hartono's loading (`summary.json` → `source_disagreement`). A local quadratic changes the 0.4 value by only 0.03–0.06 kg/m³ (delivered review).
3. **These fits follow the source they are given.**
   - Fitted to Amundsen, the λ = 1 model is within −4.52 to +2.87 kg/m³ of Amundsen, but +0.6 to +6.3 above Hartono.
   - Fitted to Hartono, it is within −3.42 to +2.05 of Hartono and about ±1 kg/m³ (−1.00 to +1.03) of Amundsen at loadings 0.1–0.2, but 3–10 kg/m³ below Amundsen at 0.3–0.4.
   - **Source disagreement does not explain every remaining error.** At 50 °C and loading 0.2, the Amundsen-targeted λ = 1 fit is off by +2.88 kg/m³ while the sources differ by only 0.68. At loading 0.4 the sources differ by more than 4 kg/m³, so no single density can meet ±2 against both there. That does not establish that the model form cannot do better elsewhere.
   - **Hartono's residual zig-zag** (about ±2 kg/m³ across loadings) is consistent in scale with its ±0.01 loading uncertainty (about 200 kg/m³ per unit loading). That is not demonstrated to explain the pattern, and a temperature trend also remains: −3.42 kg/m³ at 80 °C, loading 0.29.
4. **Linear screens of model-form changes,** from retained arrays, are in `linear-screens/` (rounds 1 and 2, with scripts and outputs). They covered free segment counts, untied packing or Debye–Hückel diameters, the ion-pair k_ij beyond −1, and Born bounds.
   - With diameter moves capped at 0.3 Å and k_ij moves at 0.1, the smallest maximum Amundsen density error at a C149 at most 5 % above the λ = 1 endpoint is **2.03 kg/m³**. Against the λ = 0 control's C149, it is **2.04 kg/m³** (`round2/cost-cap.csv`, `round2/common-cap.json`).
   - These are linear predictions. The endpoint-to-endpoint check (`round2/endpoint-validity.json`) shows they are unreliable for large moves, and they do not establish that a nonlinear fit can't do better.

**Not established here.** None of these endpoints is a candidate:
- the flash family, gas-root falsifier, comparison fits and independent derivative checks have not been run;
- λ is not chosen.

The Hartono rows are a **diagnostic transcription**, not adopted data (`hartono-check/rows.json`). Its printed loadings and the loadings implied by its printed CO₂ mole fractions differ by 0.0058–0.0122, which is about 1–2.5 kg/m³ at the density slope. Both readings were evaluated (`hartono_x3` in `summary.json`); adoption must resolve which is right. The owner decided on 2026-10-19 (#170 comment 6275729199) to judge density against both sources by their uncertainties; that gate has not yet been evaluated.

## Checks

- **Iteration path:** deterministic. The λ = 0.01 rerun with 180 iterations retraced the step-1 run's first 101 iteration costs exactly (largest difference 0.0) and converged at iteration 101.
- **Endpoint replays:**

  | Endpoint | Rows | Largest weighted-row difference |
  |---|---:|---:|
  | λ = 1 | 217 | 5.3e-12 |
  | λ = 0.1 | 217 | 6.4e-12 |
  | λ = 0.01 | 217 | 1.0e-11 |
  | Hartono fit | 201 shared objective rows | 2.2e-12 |

- **Hartono-fit heat-capacity rows:** they have no retained endpoint replay, because the evaluation chunks used those slots for density rows.
- **Start release tests** pass at every declared λ, including the Hartono-target start (augmented condition 4,055).
- **Assessment rows:** the 8 unfitted Amundsen rows (40 and 80 °C) and the Hartono rows were evaluated in the 16 direct-row slots, since `stage6_rows` asserts that count. Fitted rows placed in the same calls reproduce the endpoint evaluations exactly.
- **CO₂-free rows:** evaluated with the existing `fit_observations.stage2_rows` and `predict` path. This was a one-off disclosed scratch call, and its text is kept in `unloaded-eval-scratch.py.txt`.
- **Not run:** independent centered-difference derivative checks.
