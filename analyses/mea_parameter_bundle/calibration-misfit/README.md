# pCO2 calibration misfit: diagnosis and a candidate ionic refit

2026-09-23. This work continues the PR #101 diagnosis in
`../results/runs/pco2-calibration-misfit/`. #101 found that the misfit is mainly one loading shape
(−0.21 in ln below loading 0.2, +0.75 at 0.3–0.5, −0.51 above 0.55) that the R2, R4 and R5
constants cannot span. It named the EOS/ionic parameters as the next test. This folder runs that
test and a bounded refit.

The adopted record `results/selected-current-best-parameters.json` (`868a5018…`) is **unchanged**.
The refit results are candidate files only. The current refit C (Engine `1303c119`, packet v5
association terms, Engine fitter, five starts) is in "Refit C on Engine `1303c119`" below; the
sections before it are old-pin (`b66c7b96`) results.

## Outcome

1. **Leading explanation: the adopted ionic parameters were never fitted to pCO2 or to speciation on the current
   formulation.** The three ion–water k_ij that the refits fit (MEAH⁺, MEACOO⁻ and HCO₃⁻ with water) are
   zero. The trace ions carry transferred values: CO₃²⁻–water −0.25, H₃O⁺–water +0.25 and OH⁻–water −0.25.
   - The MEAH⁺/MEACOO⁻ size, energy and Born values come from a historical speciation-only fit on the
     retired 1.5.2 runtime (22 rows; `../ionic-speciation-fit/index.qmd`).
   - The HCO₃⁻/CO₃²⁻ values are transferred diagnostics.
   - The adoption fit scored only 5 pCO2 rows and moved only reaction enthalpies (#101).
2. **The pCO2 misfit and a speciation misfit are consistent with one shared cause: the unfitted
   ionic non-ideality.** At loading 0.3–0.5 the adopted model shifts carbon out of carbamate into
   bicarbonate and carbonate:
   - Carbamate is under-predicted by about 17% (Böttinger 2008) and 21% (Matin 2012) on average,
     and by up to 35%.
   - The model puts 5–24% of dissolved carbon in CO₃²⁻ at 20–40 °C. Jakobsen 2005 NMR gives 1–3%,
     a 5–13× excess (table below). Jakobsen is not in any objective, so it is the out-of-objective
     check.
   - The equilibrium identity a(CO2) ∝ a(MEAH⁺)·a(HCO₃⁻)/a(MEA) links the two misfits. An excess of
     HCO₃⁻ at 0.3–0.5 is consistent with the pCO2 over-prediction there. That identity is not proof
     of causation, and activity coefficients were not decomposed. The mechanism also does not
     explain the pCO2 under-prediction below loading 0.2, where the carbonate excess is
     proportionally largest.
3. **The ionic, MEA–water and R4 coordinates can express the loading shape; the CO2-side parameters
   cannot.** Of the 24 coordinates tested:
   - The CO2–water k_ij and the CO2 dispersion energy shift pCO2 uniformly and leave speciation
     unchanged.
   - The CO2–MEA k_ij has no pCO2 effect, because a(CO2) is pinned by the reactions.
   - These have loading-dependent effects:
     - the carbamate–water, bicarbonate–water and MEAH⁺–MEACOO⁻ k_ij;
     - the MEAH⁺–water k_ij (U-shaped);
     - the R4 intercept (changes sign; the refit leans on it);
     - the neutral MEA–water k_ij, the strongest shape lever.
4. **Refit A** fits five ionic/reaction coordinates to pCO2 and speciation jointly, with the 80 °C
   isotherm held out:
   - pCO2 RMS ln over all six sources falls from 0.532 to 0.329 (AARD 52% → 27%).
   - The held-out 80 °C isotherm falls from 0.525 to 0.208. That is an **interpolation** test,
     because 80 °C lies between the calibrated 60 and 100 °C isotherms.
   - Five of six sources improve, including three never fitted (Idris, Aronu, Xu). **Mamun 2005
     (120 °C, not fitted) worsens** from 0.254 to 0.380. Mamun is the only high-temperature
     extrapolation evidence.
5. **Warning: the reaction chemistry is compensating.** Three of five coordinates sit on their
   bounds:
   - The R4 intercept is at its lower bound (ln K4 lowered by 0.50, a factor of 1.65 in K4,
     carbamate made more stable). That bound is wider than #101's nominal ±0.3.
   - HCO₃⁻–water k_ij is at +0.30.
   - MEAH⁺–MEACOO⁻ k_ij is at −0.30.

   The R4 intercept correlates at −0.97 with the MEAH⁺–MEACOO⁻ k_ij and +0.97 with the carbamate–water
   k_ij. The smallest normalized singular value is 0.09. The data cannot separate the carbamate
   reaction constant from the carbamate ion interactions: the fit uses R4 as a free knob to absorb
   what the ionic model lacks. The candidate improves the fit. It does not identify the physics.

## Evidence

### Six-source pCO2 and the refit partition (wheel `b66c7b96…`, Engine `443a9da4`)

RMS of ln(pred/obs); AARD in parentheses. "Canonical" rows are the 161 active 30 wt% rows, built as
`../scripts/generate_figure_data.py` builds them.

| scope | n | adopted | candidate A |
|---|---:|---:|---:|
| all six sources | 160 / 161 | 0.532 (52%) | 0.329 (27%) |
| Hilliard 2008 (calibration) | 30 | 0.584 (69%) | 0.262 (24%) |
| Jou 1995 (calibration except 80 °C) | 48 | 0.601 (57%) | 0.326 (30%) |
| Idris 2014 (not fitted) | 9 / 10 | 0.640 (85%) | 0.226 (21%) |
| Aronu 2011 (not fitted) | 36 | 0.506 (41%) | 0.349 (22%), mean −0.245 |
| Xu 2011 (not fitted) | 18 | 0.440 (49%) | 0.379 (35%) |
| Mamun 2005 (not fitted) | 19 | **0.254 (21%)** | **0.380 (29%), mean −0.347** |
| packet calibration pCO2 | 68 | 0.602 | 0.311 |
| packet validation pCO2, 80 °C (Jou; `reserved_validation`) | 11 | 0.525 | 0.208 |
| packet calibration speciation (both solved) | 112 | 0.398 | 0.272 |
| packet validation speciation, 80 °C (Böttinger) | 11 | 0.147 | 0.133 |

Speciation scores here compare the NMR "HCO₃⁻" with model HCO₃⁻ + CO₃²⁻ (see Refit A), not the
packet's HCO₃⁻-only mapping, so they are not comparable with the notebook's speciation statistics.

The adopted model is the one the notebook reports (Mamun 0.25, Xu 0.44, Aronu 0.51, Hilliard 0.585,
Jou 0.60, Idris 0.64–0.66). The adopted model fails 1 canonical row (Idris `vle_obs_0166`) and 3 speciation
states that the candidate solves. `probe.py` builds the canonical rows with the same nearest-template
rule as `generate_figure_data.py`, but it cold-starts the adopted solves and warm-starts the
candidate solves from them. The figure-data generation (`generate_figure_data.py`) instead uses cached cross-state anchors, so its
failure set can differ.

### Carbonate fraction of dissolved carbon (Jakobsen 2005 NMR, 30 wt%)

| T, loading | Jakobsen | adopted | candidate A |
|---|---:|---:|---:|
| 20 °C, 0.11 | 0.009 | 0.118 | 0.027 |
| 20 °C, 0.25 | 0.021 | 0.170 | 0.044 |
| 20 °C, 0.40 | 0.027 | 0.240 | 0.077 |
| 40 °C, 0.11 | 0.010 | 0.054 | 0.013 |
| 40 °C, 0.29 | 0.014 | 0.083 | 0.024 |
| 40 °C, 0.40 | 0.019 | 0.105 | 0.034 |

The candidate cuts carbonate 3–5×, but it stays 1.3–3× above Jakobsen. The NMR split is inferred
from the fast-exchange HCO₃⁻/CO₃²⁻ shift. Matin et al. put that inferred split's error at
10–12% mean and up to 34% (2012, p. 6616). One Jakobsen row (40 °C, 0.21, 0.119) is an outlier.
Wong 2015 Raman (30 °C) gives about 5% carbonate at loading 0.13 and 0.43 (Fig. 8, digitized). No
30 °C model states were evaluated, so Wong is quoted, not scored.

### Sensitivities (`sensitivity-states.csv`)

Forward differences of d ln(prediction)/d(parameter) at the adopted record, one row per state and
target, 24 coordinates. Steps: 0.01 for k_ij, 2% for the other EOS/ionic coordinates, 0.05 in
ln K for reactions. Each perturbed solve is warm-started from the adopted solution. Mean
d ln pCO2 per unit parameter, by loading bin (<0.2, 0.2–0.3, 0.3–0.5, 0.5–0.55, ≥0.55):

| coordinate | per-bin slope |
|---|---|
| MEA–water k_ij | +29, +26, +12, +5, +2 |
| carbamate–water k_ij | −4.7, −2.8, 0.0, +1.0, +1.2 |
| bicarbonate–water k_ij | −0.06, −0.12, −0.55, −1.2, −1.6 |
| MEAH⁺–MEACOO⁻ k_ij | +0.4, +1.0, +1.1, +0.5, −0.1 |
| MEAH⁺–water k_ij | −3.6, −2.7, −1.7, −2.4, −3.1 |
| CO2–water k_ij | +18 in every bin (uniform) |
| R4 intercept (ln K) | +0.92, +0.81, +0.31, −0.24, −0.49 |
| R2 intercept, R5 (ln K) | ≈ −1, ≈ +1 in every bin (as in #101) |

The Debye–Hückel and Born diameters, the ion dispersion energies and both permittivities have
small effects over plausible ranges. The Born term largely cancels against the
infinite-dilution-in-water reference, and so do the ion–water interactions of the trace ions.
Setting CO₃²⁻–water k_ij from −0.25 to 0 changes pCO2 RMS by only 0.01.
`speciation-states.csv` holds the adopted carbon and amine distribution per state. Both files were
produced on wheel `762dd326…` (recorded in their rows), which gives results identical to `b66c7b96…`
on these states.

### Refit A (`refit.py`, `refit-A-identifiability.csv`)

**Coordinates and bounds:**

- Carbamate–water, MEAH⁺–water and HCO₃⁻–water k_ij, each within ±0.3.
- MEAH⁺–MEACOO⁻ k_ij, within ±0.3.
- The R4 intercept, within ±0.5 ln K.

This follows the ion–water k_ij convention of Held-type ePC-SAFT (see Literature).

**Partition:**

- Calibration: every packet state except 80 °C that the adopted model solves: 68 pCO2 rows
  (Hilliard; Jou at 40/60/100/120 °C) and 112 speciation rows (Böttinger, Matin), 180 residuals
  in all. The three adopted-model failures (Böttinger 042 and 046, Matin 016) are not in the
  objective.
- Validation: the whole 80 °C isotherm (11 Jou pCO2 rows, `reserved_validation` in the grouped split
  file, plus 5 Böttinger states). Aronu, Idris, Mamun and Xu enter no objective.

**Objective:**

- pCO2: ln(pred/obs)/0.3, with 0.3 being the #101 data floor.
- Species: (pred − obs)/(0.1·obs + 0.001).
- The NMR "HCO₃⁻" observation is compared with model HCO₃⁻ + CO₃²⁻, the one fast-exchange carbon
  pool. Matin's value is computed assuming carbonate is negligible (2012, Eq. 19b). This mapping
  differs from the packet's HCO₃⁻-only mapping, and changing the packet is an owner decision.

**Solver and stopping:**

- Trust-region least squares, with forward differences at the sweep steps.
- A state that fails at a trial point keeps its adopted residual.
- Stopped under the owner's rule at iterate 13: below 2% relative drop in calibration pCO2 RMS
  per iteration (0.317 → 0.312 → 0.311). This is not an optimizer optimum; three coordinates are
  at bounds.
- Part 1 (four iterations, `max_nfev` 10) ran on wheel `762dd326` and was stopped at an evaluation
  boundary for the rebase. Part 2 restarted on `b66c7b96` from part 1's best point:
  `@0.0007023682593133643`, `@-0.2096295233737498`, `@0.2988551751685706`,
  `@-0.29557764994923635`, `@1.016844054303057`, in coordinate order.
- On the 120 packet states the two wheels give identical results (fresh solves: |Δln pCO2| = 0,
  |Δx| = 0).

| coordinate | adopted | candidate A | SE | at bound |
|---|---:|---:|---:|:--:|
| carbamate–water k_ij | 0 | −0.0037 | 0.066 | |
| MEAH⁺–water k_ij | 0 | −0.2118 | 0.026 | |
| HCO₃⁻–water k_ij | 0 | +0.3000 | 0.089 | yes |
| MEAH⁺–MEACOO⁻ k_ij | −0.0020 | −0.3000 | 0.150 | yes |
| R4 intercept `a` (ln K4) | 1.5050 | 1.0050 | 0.326 | yes (−0.5) |

The standard errors come from the linearized Jacobian at iterate 7, over the 180 objective
residuals, with residual variance 0.86.
They are not valid at the bounds and understate the correlated uncertainty.
`candidate-refit-a-parameters.json` (SHA-256 `4f31b348…7734`) holds these five values; R4's
`b_k` keeps its source provenance. Loaded directly (`python candidate.py --check`), it reproduces
the refit predictions to 2e-11 in ln pCO2 and 2e-13 in mole fraction.

### Refit C with the incumbent's fitted R4 (`refit.py` at `e522dc4`, `refit-C.json`)

**Correction (2026-09-28, independent review of PR #106):** this run and every later refit C up to
`be1036b` did **not** hold R4 at its source correlation. `refit.py` passed the incumbent record's fitted R4
(`a` = 1.505015, `b_k` = −1317.049 K) to every problem, and `candidate.py` wrote the same R4 into the
records. The source is `a` = 2.151, `b_k` = −1545.3 K (Tong 2012 via Aroua 1999,
`data/reference/MEA/manifests/chemical_reaction_source_contract.json`). The results below are retained as
"refit C with the incumbent's fitted R4". Refit C with the source R4 is in its own section below.

Owner decision of 2026-09-23 (#96, #107): refit with the R4 intercept at its Tong 2012 / Aroua 1999
value, and adopt only if the fit holds (the run below did not do this; see the correction). Adoption rule: the 161-row pCO2 AARD must be at most 35 %,
keeping at least 70 % of refit A's 52 → 27 % gain, and Mamun 2005 at 120 °C must not degrade
against the adopted record's RMS ln of 0.254.

**Coordinates and bounds:**

- The four refit-A k_ij, each within ±0.3, started from refit A's values.
- A 1/T slope on MEAH⁺–water k_ij, within ±300 K, with T_ref 313.15 K. Its form is the one the record
  already uses for CO2–MEA.
- Intended: R4 fixed at `a` = 2.151 (source). Run: R4 at the incumbent's `a` = 1.505015, `b_k` = −1317.049 K.

The partition, objective and HCO₃⁻ + CO₃²⁻ mapping are the same as refit A's. The mapping is the
#109 decision (Matin 2012, Eqs. 18–19b).

**Solver and stopping:**

- Part 1 stopped after iteration 1 because the process was killed. Calibration pCO2 RMS ln went from
  0.523 to 0.445.
- Part 2 restarted from part 1's iteration-1 point.
- The run stopped at iteration 2 under the 2 % pCO2-RMS rule: 0.445 → 0.444. The objective cost fell
  2.3 % (126.9 → 124.0) in that step, so the optimizer had not reached an optimum.

| coordinate | adopted | refit A | refit C | SE (C) | at bound (C) |
|---|---:|---:|---:|---:|:--:|
| carbamate–water k_ij | 0 | −0.0037 | +0.0748 | 0.019 | |
| MEAH⁺–water k_ij | 0 | −0.2118 | −0.2329 | 0.018 | |
| MEAH⁺–water 1/T slope (K) | 0 | 0 | −155.6 | 66 | |
| HCO₃⁻–water k_ij | 0 | +0.3000 | +0.2957 | 0.020 | near (+0.3) |
| MEAH⁺–MEACOO⁻ k_ij | −0.0020 | −0.3000 | −0.3000 | 0.048 | **yes (−0.3)** |
| R4 intercept `a` | 1.5050 | 1.0050 | 1.5050 (incumbent, fixed) | | |

The standard errors come from the final forward-difference Jacobian over the 180 objective
residuals. They are not valid at the active MEAH⁺–MEACOO⁻ bound. The column-normalized singular values
are 1.48, 1.06, 0.89, 0.72 and 0.62. The largest correlation is +0.48, between carbamate–water and
the slope. Holding R4 removed refit A's −0.97 R4 correlation, but the cation–anion bound is still
active.

**pCO2 by source** (ln(pred/obs); the 80 °C Jou rows are held out; Aronu, Idris, Mamun and Xu enter no
objective):

| source | n | adopted AARD / bias / RMS | refit A | refit C |
|---|---:|---|---|---|
| all six (161) | 161 | 52 % / +0.147 / 0.532 (n = 160) | 27 % / −0.025 / 0.329 | **37 %** / +0.097 / 0.400 |
| Hilliard 2008 (fitted) | 30 | 69 % / +0.364 / 0.584 | 24 % / +0.130 / 0.262 | 50 % / +0.350 / 0.445 |
| Jou 1995 (fitted except 80 °C) | 48 | 57 % / +0.050 / 0.601 | 30 % / +0.125 / 0.326 | 40 % / +0.098 / 0.428 |
| Aronu 2011 (not fitted) | 36 | 41 % / −0.005 / 0.506 | 22 % / −0.245 / 0.349 | 27 % / −0.057 / 0.368 |
| Idris 2014 (not fitted) | 10 | 85 % / +0.584 / 0.640 (n = 9) | 21 % / +0.107 / 0.226 | 59 % / +0.442 / 0.493 |
| Xu 2011 (not fitted) | 18 | 49 % / +0.318 / 0.440 | 35 % / +0.021 / 0.379 | 32 % / +0.124 / 0.340 |
| Mamun 2005, 120 °C (not fitted) | 19 | 21 % / −0.027 / **0.254** | 29 % / −0.347 / 0.380 | 19 % / −0.218 / **0.299** |
| 80 °C held-out isotherm (Jou) | 11 | 47 % / −0.137 / 0.525 | 17 % / +0.014 / 0.208 | 30 % / −0.052 / 0.341 |

**Speciation** (AARD / RMS ln): calibration 36 % / 0.398 (adopted, n = 112), 12 % / 0.265 (A, n = 120),
14 % / 0.301 (C, n = 120); 80 °C holdout 11 % / 0.147, 11 % / 0.133, 9 % / 0.103. Carbonate share of
dissolved carbon against Jakobsen 2005 NMR at 20 and 40 °C, loading 0.11–0.40: adopted 5–13× the
measured share, refit A 1.3–3.0×, refit C 1.2–2.8×. One point is excluded from these ratios: 40 °C,
loading 0.21, measured 0.119, which is out of line with its neighbours. Wong 2015 (about 5 % at 30 °C)
is quoted, not scored, because no 30 °C model states exist.

**Solver status:** refit C solves 123/123 packet states and 161/161 pCO2 states. On every row the
requested tolerance is met, material and charge balances close within 1e-7, and the maximum
stationarity residual is 6.8e-13. The adopted record fails 3 packet states and 1 pCO2 state
(`variant-scores.csv`, column `failures`).

**Outcome: refit C fails both adoption conditions.** Its 161-row AARD is 37 % (limit 35 %), and
Mamun's RMS ln rises from 0.254 to 0.299. This first-stop point is not adopted. It is a calibration result;
Aronu, Idris, Mamun and Xu are predictions of other 30 wt% sources, and the 80 °C isotherm is an
interpolation test.

### Refit C with the incumbent's fitted R4, run on to the iteration cap (`refit-C-converged.json`)

This run started from the refit-C first-stop point. Bounds, residual weights and the calibration set
are unchanged. It used `least_squares` default tolerances, capped at 6 iterations
(`refit.py --iterations=6`).

- **Stop:** the 6-iteration cap (status −2), with 8 function evaluations. No `least_squares` tolerance
  was met, and the 2 % rule was not applied.
- **Stall:** calibration pCO2 RMS ln per iteration was 0.4432, 0.4457, 0.4466, 0.44676, 0.446763 and
  0.446763. The last three changes are 1.6e-4, 5e-6 and 2e-7. The objective cost fell from 124.0 to 121.4
  because speciation improved while pCO2 rose slightly. The iterate stopped moving with two
  coordinates at bounds.

| coordinate | first stop | this run | SE | at bound |
|---|---:|---:|---:|:--:|
| carbamate–water k_ij | +0.0748 | +0.1069 | 0.026 | |
| MEAH⁺–water k_ij | −0.2329 | −0.2414 | 0.034 | |
| MEAH⁺–water 1/T slope (K) | −155.6 | −140.5 | 12.9 | |
| HCO₃⁻–water k_ij | +0.2957 | **+0.3000** | 0.108 | **yes (+0.3)** |
| MEAH⁺–MEACOO⁻ k_ij | −0.3000 | **−0.3000** | 0.048 | **yes (−0.3)** |

- **Identification:** the column-normalized singular values are 1.41, 1.16, 0.95, 0.82 and **0.31**. The
  first-stop point's smallest was 0.62.
- **Correlations:** the largest is −0.86, between MEAH⁺–water and HCO₃⁻–water. HCO₃⁻–water correlates
  +0.76 with carbamate–water. The standard errors are not valid at the two active bounds.

| pCO2, ln(pred/obs) | n | pre-refit AARD / bias / RMS | this run |
|---|---:|---|---|
| all six sources | 161 | 52 % / +0.147 / 0.532 (n = 160) | **38 %** / +0.079 / 0.410 |
| Hilliard 2008 (fitted) | 30 | 69 % / +0.364 / 0.584 | 50 % / +0.326 / 0.448 |
| Jou 1995 (fitted except 80 °C) | 48 | 57 % / +0.050 / 0.601 | 42 % / +0.084 / 0.433 |
| Aronu 2011 (not fitted) | 36 | 41 % / −0.005 / 0.506 | 27 % / −0.085 / 0.388 |
| Idris 2014 (not fitted) | 10 | 85 % / +0.584 / 0.640 (n = 9) | 57 % / +0.428 / 0.480 |
| Xu 2011 (not fitted) | 18 | 49 % / +0.318 / 0.440 | 33 % / +0.132 / 0.349 |
| Mamun 2005, 120 °C (not fitted) | 19 | 21 % / −0.027 / **0.254** | 21 % / −0.244 / **0.332** |
| 80 °C held-out isotherm (Jou) | 11 | 47 % / −0.137 / 0.525 | 32 % / −0.078 / 0.356 |
| Akula 2023a-comparable set | 106 | 58 % / +0.237 / 0.535 | 39 % / +0.139 / 0.410 |

- **Speciation (AARD / RMS ln):** calibration 36 % / 0.398 (pre-refit, n = 112) and 14 % / 0.341
  (n = 120); 80 °C holdout 11 % / 0.147 and 9 % / 0.103.
- **Carbonate share against Jakobsen 2005:** 0.9–2.5× the measured share (pre-refit 5–13×), excluding
  the out-of-line 40 °C, loading 0.21 point.
- **Solver status:** 123/123 packet and 161/161 pCO2 states solve. On every row the tolerance is met,
  balances close within 1e-7, and the maximum stationarity residual is 5.7e-13.

**Akula 2023a-comparable set:** 30 wt% rows from Aronu, Hilliard, Jou and Xu at loading ≤ 0.5 and
40–120 °C. The number is the mean absolute relative pCO2 error at measured loading. Akula 2023a
reports 40.5 % for its eNRTL model fitted to its own 30 mass % data. That paper is not on the local
reading shelf, so the definition and value are taken from
`docs/ePC-SAFT/amine-epcsaft-model-hierarchy-literature-review.md` (Akula Fig. 4) and have not been
re-read. Akula's rows are not these rows, and Hilliard and Jou are calibration rows here.

**Adoption (owner decisions, #107):** on 2026-09-24 the owner chose this run as the exploratory
incumbent even though it misses the pre-set rule:

- The 161-row AARD is 38 %, above the 35 % limit.
- Mamun's RMS ln rose from 0.254 to 0.332 (AARD 21 % in both).
- MEAH⁺–MEACOO⁻ sits at −0.3 and HCO₃⁻–water at +0.3.

On 2026-09-28 the owner replaced that with: the paper is written on refit C, refit on the current
Engine, not adopted on this pin. `results/selected-current-best-parameters.json` stays `868a5018…`.
The refit-C record (`4c1bff04…`) is written by `candidate.py refit-C-converged.json OUT`; the #108
composition-transfer prediction used it (`../composition-transfer/README.md`).

The canonical rule is merged (#109, main `0be3ad4`): `data/reference/MEA/manifests/speciation_linear_coefficient_rules.csv`
maps the Matin 2012 and Böttinger 2008 HCO₃⁻ targets to HCO₃⁻ + CO₃²⁻, applied to the membership file by
`scripts/build_canonical_cheq_dataset.py`. The calibration state packet (`86f60041`) predates it and still maps
them to HCO₃⁻ alone, so `compare.pooled_species` applies the pool for this analysis. The notebook statistics
(`generate_figure_data.py`) have not been regenerated from the new membership.

### Refit C with the incumbent's fitted R4 on Engine `1303c119`, packet v5 terms (2026-09-28)

Relabelled by the correction above: every fit, score and record in this section used the incumbent's
fitted R4, not the source R4. The files are `refit-C-incumbent-R4-multistart.json`,
`refit-C-incumbent-R4-iterations.csv` and `refit-C-incumbent-R4-parameters.json` (`039ddaba…`), whose
`purpose` field wrongly says "R4 at its source value". Its variants are `incumbent-R4-C-*` in
`refit-C-scores.csv`. That record's per-row residuals and Jacobian were not retained, so its conditional
standard errors, correlations and singular values below cannot be rebuilt from retained files.

Owner decision 2026-09-28 (#107): refit C on the current Engine before any adoption. The paper is
written on refit C, and a later model replaces it only by rules fixed in advance.

**Pin and association terms.**

- Wheel `f66d972c032ce709ada69e8d8177e195c7e416800757663b7420c22bda5f6328`, Engine
  `1303c119e4a21ba31e46596fe62ee3fdfe4cc253` (`../scripts/shared_evaluation.py`).
- The selected record carries its own association topology. It is the Engine packet v3 topology:
  MEA 2B volume 0.03747 and the `arithmetic-energy-geometric-volume` MEA–water rule. A new wheel
  alone therefore does not bring in Engine #164 or #166.
- `candidate.py --packet-v5` writes `pre-refit-packet-v5-parameters.json` (`562b5976…`):
  - the pre-refit record `868a5018…` with the topology of Engine packet
    `mea-co2-h2o-nine-species-estimation/5` (fingerprint `76315ac4…`, `parameters.json` `1ba95275…`);
  - MEA κ = 0.036287 (#166) and the `wolbach-sandler` MEA–water rule (#164);
  - the Baygi 2015 source and a packet source entry.
- The script checks both input hashes and asserts that the MEA self-volume is the only coefficient
  value that changes. `probe.py`'s base record `RECORD` is this file, so every score and fit below
  uses packet v5 terms. The selected record is unchanged.

**Baseline shift** (pre-refit record; `probe.py` outputs; the maxima are the `max |d …| vs …` rows of `refit-C-scores.csv`):

| change | max \|Δln pCO2\| | max \|Δx\| | solved (packet / pCO2) |
|---|---:|---:|---|
| wheel `b66c7b96` → `f66d972c`, packet v3 terms | 2.8e-11 | 1.9e-13 | 120 → 123 / 160 → 161 |
| packet v3 → v5 terms, wheel `f66d972c` | 3.5e-3 | 7.6e-6 | 123 / 161 |

- The wheel change is a numerical identity on the rows both wheels solve. Its only effect is that
  the old pin's four failures (Böttinger 042 and 046, Matin 016, `vle_obs_0166`) now solve.
- Packet v5 moves pCO2 by 0.12 % on average and at most 0.35 % (`vle_obs_0225`, 120 °C, loading
  0.011). The 180-row refit cost goes from 471.113 to 471.283. The 161-row AARD goes from 52.0 %
  (160 rows) to 52.5 % (161 rows); the extra row is Idris `vle_obs_0166` at +125 % (pCO2 144 Pa against 64 Pa).

**Fit.** `refit.py` calls `epcsaft.regression.fit`: Ceres Levenberg–Marquardt with exact implicit
derivatives, including the `k_ij_reciprocal_temperature_slope` family and the `partial_pressure`
observation in `log_ratio` form. It reuses the construction of Engine
`analyses/2026-mea-reactive-fit-timing/scripts/run.py`. It replaces the scipy forward-difference
path; the old `refit.py` and `identifiability.py` are in Git history (`e522dc4`).

- Coordinates, bounds, scales, rows and weights are refit C's:
  - four k_ij within ±0.3;
  - the MEAH⁺–water 1/T slope within ±300 K (T_ref 313.15 K);
  - R4 intended at its source value, run at the incumbent's fitted value;
  - 180 rows: every packet state except 80 °C and `compare.EXCLUDED`, the three states the pre-refit
    record failed on the old pin.
- Every state is declared from the pre-refit solve's liquid anchor.
- Limits: 100 iterations, 7200 s; tolerances are the Engine's `FIT_*` defaults.

**Multistart** (`refit-C-incumbent-R4-multistart.json`, `refit-C-incumbent-R4-iterations.csv`; every start converged with "function tolerance reached"
and no trial failures):

| start | start point (4 k_ij; slope, K) | initial cost | final cost | iterations | fit time |
|---|---|---:|---:|---:|---:|
| pre-refit | 0, 0, 0, −0.0020; 0 | 471.283 | 121.4524670 | 57 | 3067 s |
| C, incumbent R4, old pin | 0.1069, −0.2414, 0.3, −0.3; −140.47 | 121.453 | 121.4524671 | 4 | 234 s |
| all zero | 0, 0, 0, 0; 0 | 472.759 | 121.4524670 | 57 | 2974 s |
| seed 1 | 0.0071, 0.2703, −0.2135, 0.2692; −112.90 | 2124.746 | 121.4524670 | 56 | 3138 s |
| seed 2 | −0.1430, −0.1209, 0.1885, −0.2449; 60.06 | 540.012 | 121.4524670 | 58 | 3284 s |

- **Spread across the five starts:** at most 1.5e-8 in any k_ij and 1.0e-5 K in the slope; final costs
  agree to 3e-8. Seeds are `numpy.random.default_rng(1)` and `(2)`, uniform inside the bounds.
- **Per-iteration wall time:** median 53–56 s per start. The host load average was 5–7 from other
  processes on 2 CPUs.
- **Plateau:** the long starts spend about 26 iterations at cost 121.643 before the active set is
  rebuilt and the cost drops to 121.452. This is the Engine's bounded-fit round converging to its
  1e-12 function tolerance before the bound set changes. It is an efficiency observation; the
  result is unaffected.

| coordinate | pre-refit | C, incumbent R4 (`b66c7b96`, v3) | C, incumbent R4 (`f66d972c`, v5) | conditional SE | at bound |
|---|---:|---:|---:|---:|:--:|
| carbamate–water k_ij | 0 | +0.10691 | +0.10725 | 0.018 | |
| MEAH⁺–water k_ij | 0 | −0.24144 | −0.24143 | 0.018 | |
| MEAH⁺–water 1/T slope (K) | 0 | −140.47 | −141.25 | 66 | |
| HCO₃⁻–water k_ij | 0 | +0.3000 | **+0.3000** | withheld | **yes (+0.3)** |
| MEAH⁺–MEACOO⁻ k_ij | −0.0020 | −0.3000 | **−0.3000** | withheld | **yes (−0.3)** |

**Identifiability at the best point:**

- **Engine covariance:** withheld as `active_bound`. HCO₃⁻–water and MEAH⁺–MEACOO⁻ end on their bounds
  from all five starts, including seed 1, which started MEAH⁺–MEACOO⁻ at +0.27. This shows only the
  bounded result; where an unbounded optimum lies is not established.
- **Singular values:** the Engine reports rank 5; its scaled optimizer-space singular values are
  0.927, 0.643, 0.252, 0.181 and 0.092, with variance factor 1.388. The column-normalized singular
  values of the weighted Jacobian are 1.53, 1.18, 0.89, 0.64 and 0.28. Old C's were 1.41, 1.16,
  0.95, 0.82 and 0.31.
- **Conditional standard errors:** the SE column holds the three free coordinates only. They are
  conditional on the two bound coordinates held fixed, with residual variance 1.372 over 177
  degrees of freedom. They understate the joint uncertainty.
- **Correlations among the free coordinates:** carbamate–water with slope +0.48, MEAH⁺–water with
  slope +0.36, carbamate–water with MEAH⁺–water −0.13.

**Checks:**

- `compare.py` scores the new point from `probe.py` records at cost 121.45247, equal to the Engine fit.
  It scores old C on the new pin at 121.45329, the Engine's initial cost from that start.
- `refit-C-incumbent-R4-parameters.json` (`039ddaba…`, written by `candidate.py`, not adopted) reproduces
  the probe-override solves to 8e-14 in ln pCO2 and 3e-16 in mole fraction (`record-replay-check.csv`).

**Scores** (`refit-C-scores.csv`, `refit-C-states.csv`). pCO2 is AARD / mean ln / RMS ln.
Aronu, Idris, Mamun and Xu enter no objective, and the 80 °C isotherm is held out.

| scope | n | pre-refit, new pin (v5) | C, incumbent R4 (`b66c7b96`, v3) | C, incumbent R4 (`f66d972c`, v5) |
|---|---:|---|---|---|
| all six sources | 161 | 52.5 % / +0.153 / 0.534 | 37.6 % / +0.079 / 0.410 | **37.7 %** / +0.080 / 0.410 |
| Hilliard 2008 (fitted) | 30 | 69.1 % / +0.365 / 0.585 | 49.7 % / +0.326 / 0.448 | 49.8 % / +0.326 / 0.448 |
| Jou 1995 (fitted except 80 °C) | 48 | 56.9 % / +0.051 / 0.601 | 41.7 % / +0.084 / 0.433 | 41.8 % / +0.084 / 0.433 |
| Aronu 2011 | 36 | 41.4 % / −0.004 / 0.505 | 27.5 % / −0.085 / 0.388 | 27.5 % / −0.085 / 0.388 |
| Idris 2014 | 10 | 89.3 % / +0.608 / 0.660 | 56.9 % / +0.428 / 0.480 | 57.0 % / +0.428 / 0.480 |
| Xu 2011 | 18 | 48.8 % / +0.319 / 0.440 | 33.4 % / +0.132 / 0.349 | 33.4 % / +0.132 / 0.349 |
| **Mamun 2005, 120 °C** | 19 | 20.7 % / −0.026 / 0.253 | 21.4 % / −0.244 / 0.332 | **21.3 %** / −0.244 / 0.332 |
| **Akula 2023a-comparable** (Aronu, Hilliard, Jou, Xu; loading ≤ 0.5) | 106 | 58.0 % / +0.239 / 0.535 | 39.2 % / +0.139 / 0.410 | **39.3 %** / +0.139 / 0.410 |
| 80 °C held-out isotherm (Jou) | 11 | 46.5 % / −0.135 / 0.525 | 32.2 % / −0.078 / 0.356 | 32.2 % / −0.078 / 0.356 |
| speciation, calibration | 120 | 36.0 % / 0.395 | 14.3 % / 0.341 | 14.3 % / 0.341 |
| speciation, 80 °C held out | 11 | 10.9 % / 0.147 | 8.7 % / 0.103 | 8.7 % / 0.103 |
| carbonate / Jakobsen 2005 (9 points) | 9 | 5.0–12.7× | 0.98–2.49× | 0.98–2.48× |
| #108 rows, **second look**, 15 wt% | 33 | – | 87.8 % / +0.535 / 0.656 (one-time) | 87.8 % / +0.536 / 0.656 |
| #108 rows, **second look**, 45 wt% | 37 | – | 23.3 % / −0.180 / 0.351, 36/37 (one-time) | 23.3 % / −0.182 / 0.350, 37/37 |

- **Speciation:** AARD / RMS ln over the HCO₃⁻ + CO₃²⁻ pool, as refit.py scores it; n = 120 on the
  new pin, 112 for old-pin pre-refit.
- **Carbonate:** the ratio of model to measured carbonate share of dissolved carbon. The 40 °C,
  loading 0.21 point (0.12× for both refits) is excluded as out of line. Wong 2015 (about 5 % at
  30 °C) is quoted, not scored, because there are no 30 °C states.
- **#108 rows:** `../composition-transfer/second-look-incumbent-R4-scores.csv`. They are not an untouched test
  (see `../composition-transfer/README.md`).
- **Solver status:** every variant on the new pin solves 123/123 packet and 161/161 pCO2 states. The
  tolerance is met, balances close within 1e-7, and the maximum stationarity residual is 1.1e-12
  or smaller.

**Literature, like-for-like on Mamun 2005** (n = 19, 120 °C, 30 mass %, pCO2 at measured loading;
`docs/ePC-SAFT/amine-epcsaft-model-hierarchy-literature-review.md`):

- Zhang 2011 eNRTL: 13.5 %. This is a calibration residual (Table 9).
- Baygi 2015 PC-SAFT with ideal ions: 21.03 % (Table 5). It is a prediction, but K(R4, R5) were
  chosen for fit.
- Najafloo 2018 SAFT-HR: 39.96 % (Table 5).
- Refit C with the incumbent's R4 (not fitted to Mamun): 21.3 %, with a −0.244 mean ln bias (pCO2 about 22 % low on
  average).
- Akula 2023a eNRTL, fitted, pooled over its 30 mass % subset at loading ≤ 0.5 (Fig. 4): 40.5 %.
  Against the comparable 106 rows here, that refit gives 39.3 %. Akula's rows are not these rows,
  and Hilliard and Jou are calibration rows here.

**Outcome:**

- Refit C with the incumbent's R4, through the Engine fitter with packet v5 terms on the new pin, reproduces the old-pin run
  to within 3.4e-4 in any k_ij and 0.8 K in the slope. Every score moves by 0.1 percentage point or
  less.
- The #107 pre-set rule is still missed: the 161-row AARD is 37.7 % against a 35 % limit, and
  Mamun's RMS ln rises from 0.253 to 0.332 against the pre-refit record.
- Two coordinates remain on their bounds from every start.
- The point is reproducible across five starts. It is a bounded optimum, not an interior one.

## Literature comparison

A Luna literature pass read local transcriptions. Zotero was unavailable, so the locators below are
from those transcriptions.

- No explicit-electrolyte ePC-SAFT model of MEA–CO2–H2O was found. The explicit reactive ePC-SAFT
  studies are MDEA systems:
  - Uyan 2015, §§3–4.
  - Wangler 2018, §§4–6, Table 11.
  - Bülow 2021, Theory and Tables 1–3.

  They take ion diameters and ion–ion terms from Held 2014 osmotic/density fits. They fit water–ion
  k_ij (MDEAH⁺, HCO₃⁻) to osmotic coefficients. They do not fit to reactive pCO2, and they predict
  pCO2 at about 19–36% ARD. Uyan and Wangler use no Born term.
- PC-SAFT MEA models with ideal chemistry (γ = 1) predict Jou/Hilliard at 43/35% AAD (Fakouri Baygi
  2015, Table 5) and 50/43% (Najafloo 2018, Table 5). Hilliard's eNRTL fit reaches 30% on Hilliard
  and 14% on Jou (Hilliard 2008, Table 13.4-6). The adopted model (69%/57%) is worse than
  ideal-chemistry PC-SAFT on the same two sources. The candidate (24%/30%) is in the eNRTL range.
- Data: Hilliard reports its 40/60 °C data as consistent with Jou (§2.4.3). Dugas & Rochelle 2009 find
  higher pressures above loading about 0.45 (Fig. 4). Jayarathna 2013 finds a non-directional 40 °C
  source offset. There is no established Jou bias. #101's floor of 0.2–0.4 in ln stands.

## Alternative explanation still open: the water and MEA–water model

The strongest shape lever is the MEA–water k_ij (above). Its value −0.0735 is owned by the neutral
MEA–water VLE refit, and refit A held it fixed.

Engine #140 / MEA PR #103 found two further problems:

- Model pure-water Cp is 12–15% below IAPWS-95, and solution Cp is 8–14% below Weiland 1997 and
  Hilliard 2008.
- Model Cp falls with temperature while the data rise.

That is independent evidence that the water/neutral model and its temperature dependence are
imperfect. It does not directly set pCO2 at fixed temperature, and #101 attributes only about 12% of
the pCO2 residual to temperature. Two things remain untested:

- whether part of the loading shape belongs to the neutral model rather than the ionic parameters;
- whether Mamun's 120 °C degradation reflects the missing temperature dependence of the ion k_ij.

## Limits

- The candidate is a calibration result. The 80 °C holdout is an interpolation test, and the
  four unfitted sources are other laboratories on the same 30 wt%, 40–120 °C domain. None of it
  tests other solvent concentrations.
- Three coordinates are at bounds. The R4 shift of −0.5 ln K is outside what has been checked
  against the Tong/Aroua source, whose uncertainty is not transcribed. Mamun and Aronu move to a
  negative mean bias.
- The ion k_ij have no temperature dependence.
- Carbonate is still over-predicted.
- The HCO₃⁻ + CO₃²⁻ mapping for Matin and Böttinger is the merged canonical rule (#109). The
  calibration packet used here predates it; see the note above.
- One refit design was run. B and further ablations were stopped by owner instruction.

## Reproduce

Run single-threaded (`OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`). The pinned wheel
must be installed; `probe.py` checks it. Solve caches and logs live in
`../results/runs/calibration-misfit/` (ignored).

```sh
python candidate.py --packet-v5 ENGINE_PACKET_V5/parameters/parameters.json  # pre-refit-packet-v5-parameters.json
python probe.py RUNS/f66-v5.jsonl; python probe.py RUNS/canon-f66-v5.jsonl --canonical      # pre-refit, packet v5
python probe.py RUNS/f66-v3.jsonl --record=../results/selected-current-best-parameters.json  # packet v3 terms
python refit.py                     # five starts -> refit-C-multistart.json (a named start re-runs only that start)
python probe.py RUNS/newC-f66-v5.jsonl <id=value ...>; python probe.py RUNS/canon-newC-f66-v5.jsonl --canonical <id=value ...>
python candidate.py refit-C-multistart.json refit-C-engine-parameters.json    # lowest-cost start; not adopted
python candidate.py --check refit-C-engine-parameters.json RUNS/newC-f66-v5.jsonl
python compare.py --out=refit-C-engine pre-refit-b66-v3=ADOPTED.jsonl,CANON-ADOPTED.jsonl ... new-C-f66-v5=...
cd ../composition-transfer && python transfer.py --out=second-look new-refit-C=../calibration-misfit/refit-C-engine-parameters.json
```

Old-pin commands (refit A, first-stop and capped refit C, `sensitivity.py`) ran the scipy `refit.py`
and `identifiability.py` at `e522dc4`.

Retained files:

- `refit-C-multistart.json`: every start with its start point, costs and wall time per iteration,
  active bounds, Engine covariance status and singular values, conditional standard errors,
  correlations and the 180 weighted residuals.
- `refit-C-engine-scores.csv`, `refit-C-engine-states.csv`: the tables in the new section, for six
  variants: pre-refit and old C on `b66c7b96`; pre-refit with v3 and v5 terms, old C and new C on
  `f66d972c`.
- `pre-refit-packet-v5-parameters.json`, `refit-C-engine-parameters.json` (not adopted).
- Old pin: `variant-scores.csv`, `variant-states.csv`, `refit-C.json`, `refit-C-converged.json`,
  `sensitivity-states.csv`, `speciation-states.csv`, `refit-A-identifiability.csv`,
  `candidate-refit-a-parameters.json`.

Rows carry the wheel, parameter and script SHA-256.
