# pCO2 calibration misfit: diagnosis and a candidate ionic refit

2026-09-23. This work continues the PR #101 diagnosis in
`../results/runs/pco2-calibration-misfit/`. #101 found that the misfit is mainly one loading shape
(−0.21 in ln below loading 0.2, +0.75 at 0.3–0.5, −0.51 above 0.55) that the R2, R4 and R5
constants cannot span. It named the EOS/ionic parameters as the next test. This folder runs that
test and a bounded refit.

The adopted record `results/selected-current-best-parameters.json` (`868a5018…`) is **unchanged**.
The refit result is a candidate file only.

## Outcome

1. **Leading explanation: the adopted ionic parameters were never fitted to pCO2 or to speciation on the current
   formulation.** Every ion–water k_ij is zero:
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
candidate solves from them. The figure pipeline instead uses cached cross-state anchors, so its
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
  manifest, plus 5 Böttinger states). Aronu, Idris, Mamun and Xu enter no objective.

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
- The HCO₃⁻+CO₃²⁻ observation mapping is a proposal. The Böttinger label is unresolved (Wong 2015 vs
  Aronu 2011).
- One refit design was run. B and further ablations were stopped by owner instruction.

## Reproduce

Run single-threaded (`OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`). The pinned wheel
must be installed; `probe.py` checks it. Solve caches live in `/tmp`.

```sh
python sensitivity.py                      # 24-coordinate sweep -> sensitivity-states.csv, speciation-states.csv
python refit.py A 'pair/carbamate-anion/water/k_ij@-0.3@0.3' 'pair/protonated-monoethanolamine/water/k_ij@-0.3@0.3' \
  'pair/bicarbonate-anion/water/k_ij@-0.3@0.3' 'pair/carbamate-anion/protonated-monoethanolamine/k_ij@-0.3@0.3' \
  'reaction:R4:correlation:a@1.005@2.005'  # log: /tmp/cm/refit-A.jsonl
python identifiability.py /tmp/cm/refit-A.jsonl /tmp/cm/base-b66.jsonl 7 <the five identities>
python candidate.py                         # candidate-refit-a-parameters.json
python candidate.py --check                 # file vs probe overrides, four states
python probe.py /tmp/cm/base-b66.jsonl; python probe.py /tmp/cm/canon-base.jsonl --canonical
python probe.py /tmp/cm/best.jsonl <id=value ...>; python probe.py /tmp/cm/canon-best.jsonl --canonical <id=value ...>
python compare.py adopted=/tmp/cm/base-b66.jsonl,/tmp/cm/canon-base.jsonl candidate-A=/tmp/cm/best.jsonl,/tmp/cm/canon-best.jsonl
```

Retained files:

- `variant-scores.csv`: the tables above.
- `variant-states.csv`: every observed/predicted pair for both variants.
- `sensitivity-states.csv`, `speciation-states.csv`, `refit-A-identifiability.csv`.
- `candidate-refit-a-parameters.json`.

Rows carry the wheel, parameter and script SHA-256. The refit log itself is scratch and is not
retained.
