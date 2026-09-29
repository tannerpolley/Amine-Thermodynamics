# Model D (#121)

Base: the packet v5 record `../calibration-misfit/pre-refit-packet-v5-parameters.json` (`562b5976…`) on Engine wheel
`f66d972c…` (commit `1303c119`), read through `shared_evaluation.parameter_mapping`, as refit C and C_src were.
Nothing here is adopted; `results/selected-current-best-parameters.json` is unchanged (#107).

- **Simple model D** (owner decisions 20–22, 2026-09-29): refit C_src's setup with wider bounds (S1), then 1/T
  slopes (S2) only if S1 fails, in two Born forms. Decision 23 then changed the calibration set and pass rule.
- **Checks N1 and N2** (decisions 1–13, before decision 20): the earlier binary-data route, stopped at N1. They
  remain the evidence that the Born form matters (last sections).

## Simple model D: setup

- **Born forms.** (i) SSM+DS, c_shell = c_dielectric = 1: the base record as loaded (the record omits both keys and
  `parameter_mapping` fills (1, 1); Figiel 2025). (ii) original Born, c_shell = c_dielectric = 0, written explicitly:
  `born-0-0-packet-v5-parameters.json` (`f5831262…`, `candidate.py --born-0-0`; only those two keys differ). The
  Engine accepts (0, 0) for every coordinate fitted here.
- **S1 coordinates and bounds** (T_ref 313.15 K): carbamate–water and HCO₃⁻–water k_ij ±0.5; MEAH⁺–water k_ij
  ±0.5 and its 1/T slope ±1000 K; MEAH⁺–MEACOO⁻ k_ij [−1, +1]. Scales 0.01 and 10 K.
- **Unchanged from C_src (`8ceddf7`):** R4 at its source correlation (a = 2.151, b_k = −1545.3 K), R1–R3 and R5 as
  recorded; weights (pCO2 ln(pred/obs)/0.3; species (pred − obs)/(0.1 obs + 0.001)); the HCO₃⁻ + CO₃²⁻ pool
  (`compare.pooled_species`); the 80 °C isotherm held out; the fixed CO₃²⁻, H₃O⁺, OH⁻, MEA–water and CO₂–water
  values; `epcsaft.regression.fit` (Ceres Levenberg–Marquardt, exact implicit derivatives), 100 iterations, 7200 s.
- **Starts:** C_src's (pre-refit ionic values; the incumbent-R4 C optimum), C_src's optimum, and
  `numpy.random.default_rng(1)` and `(2)` uniform in the box. A start with k(T) ≥ 1 at a domain end is reported and
  not run (the Engine refuses it).
- **Scripts:** `fit.py` (designs, starts, k(T)) calls `../calibration-misfit/refit.py`; `candidate.py` writes the
  records on their recorded base; `probe.py` solves, `compare.py` scores; `../composition-transfer/transfer.py`
  scores the #108 rows; `nahco3.py` the NaHCO₃ check.
- **Compute:** single-threaded, the two Born forms as two concurrent processes on a 2-CPU host shared with other
  jobs; 440–663 s per S1 start.

## Old rule (all temperatures, Mamun gate): S1 results

Rule of decisions 20–22 (the #107 gates): G1 161-row pCO2 AARD ≤ 35 %; G2 Mamun 2005 RMS ln ≤ 0.254; G3 numerical
completeness. Objective: C_src's 180 rows (68 pCO2 at 40, 60, 100, 120 °C; 112 speciation). Superseded by decision
23 (next section); kept as the record. Files: `1-1-S1-*`, `0-0-S1-*` (multistart, iterations, Jacobian, parameters),
`old-rule-scores.csv`, `old-rule-states.csv`, `second-look-S1-*.csv`, `nahco3-*.csv`.

**Fits** (every run start converged, "function tolerance reached", no trial failures):

| | (i) SSM+DS | (ii) original Born |
|---|---|---|
| cost, 180 rows (C_src 112.705) | 55.018167 | 48.894326 |
| starts agreeing | 4 of 5; spread ≤ 1.3e-6 in any k_ij | 5 of 5; spread ≤ 1.4e-7 |
| failed start | seed 1: initial evaluation failed (Böttinger 049 equilibrium solve, 200 iterations, residual 2.4) | – |
| carbamate–water k_ij | +0.04144 (SE 0.021) | −0.07076 (SE 0.021) |
| MEAH⁺–water k_ij | −0.26273 (SE 0.023) | +0.14668 (SE 0.026) |
| MEAH⁺–water 1/T slope | −196.4 K (SE 50) | −123.8 K (SE 43) |
| HCO₃⁻–water k_ij | +0.24796 (SE 0.077) | +0.49885 (SE 0.080; 0.001 inside +0.5) |
| MEAH⁺–MEACOO⁻ k_ij | −0.71527 (SE 0.029) | **−1.0, active bound** (cost falls outward) |
| MEAH⁺–water k(T), 293.15 / 353.15 / 393.15 K | −0.306 / −0.192 / −0.135 | +0.120 / +0.191 / +0.227 |
| admissible | yes | yes |
| Engine covariance | available, rank 5 | withheld (`active_bound`), rank 5 |
| Engine scaled singular values | 0.921, 0.583, 0.274, 0.175, 0.095 | 0.942, 0.616, 0.268, 0.182, 0.084 |
| column-normalized singular values | 1.54, 1.14, 0.92, 0.63, 0.30 | 1.55, 1.16, 0.90, 0.64, 0.24 |
| largest correlation | MEAH⁺–water / HCO₃⁻–water −0.81 | the same pair, −0.89 (conditional) |

SE: (i) full; (ii) conditional on the bound coordinate, residual variance over 176 degrees of freedom.

**Scores** (AARD / mean ln / RMS ln):

| scope | n | C_src | (i) S1 | (ii) S1 |
|---|---:|---|---|---|
| **G1: all six sources** (≤ 35 %) | 161 | 34.8 % / +0.067 / 0.388 | **23.0 %** / −0.180 / 0.350 | **22.8 %** / −0.132 / 0.320 |
| **G2: Mamun 2005, 120 °C** (RMS ≤ 0.254) | 19 | 18.5 % / −0.204 / 0.293 | 34.7 % / −0.433 / **0.448** | 31.8 % / −0.389 / **0.406** |
| Hilliard 2008 (fitted) | 30 | 44.6 % / +0.291 / 0.413 | 10.2 % / −0.050 / 0.137 | 12.7 % / +0.015 / 0.151 |
| Jou 1995 (fitted except 80 °C) | 48 | 40.0 % / +0.076 / 0.422 | 17.0 % / +0.021 / 0.218 | 20.1 % / +0.031 / 0.253 |
| Aronu 2011 | 36 | 25.6 % / −0.104 / 0.372 | 34.7 % / −0.423 / 0.509 | 29.5 % / −0.349 / 0.428 |
| Idris 2014 | 10 | 49.1 % / +0.374 / 0.431 | 21.2 % / −0.185 / 0.295 | 19.2 % / −0.068 / 0.216 |
| Xu 2011 | 18 | 32.2 % / +0.129 / 0.342 | 26.0 % / −0.178 / 0.397 | 25.5 % / −0.140 / 0.373 |
| 40–80 °C rows (the decision 23 rule) | 104 | 38.1 % / +0.096 / 0.414 | 21.2 % / −0.178 / 0.339 | 20.8 % / −0.122 / 0.302 |
| 80 °C held-out isotherm (Jou) | 11 | 31.6 % / −0.089 / 0.358 | 10.2 % / −0.071 / 0.155 | 12.4 % / −0.078 / 0.199 |
| Akula 2023a-comparable | 106 | 36.4 % / +0.127 / 0.387 | 21.5 % / −0.147 / 0.330 | 21.1 % / −0.091 / 0.294 |
| speciation, calibration | 120 | 14.5 % / 0.347 | 14.3 % / 0.344 | 11.6 % / 0.199 |
| speciation, 80 °C held out | 11 | 8.9 % / 0.103 | 9.9 % / 0.118 | 7.7 % / 0.096 |
| carbonate / Jakobsen 2005 | 9 | 1.05–2.37× | 1.23–2.49× | 1.40–4.14× |
| #108 rows, second look, 15 wt% | 33 | 83.5 % / +0.513 / 0.634 | 75.3 % / +0.446 / 0.602 | 70.7 % / +0.431 / 0.573 |
| #108 rows, second look, 45 wt% | 37 | 22.2 % / −0.184 / 0.349 | 46.2 % / −0.562 / 0.873 | 46.9 % / −0.388 / 0.743 |
| NaHCO₃ φ, Peiper & Pitzer 1982 (report only) | 60 | 4.17 % (max 16.8 %) | 4.03 % (max 16.3 %) | 0.51 % (max 2.9 %) |

- **G3:** every variant solves 123/123 packet and 161/161 pCO2 states; tolerance met, balances within 1e-7, maximum
  stationarity 1.0e-12 (i) and 4.0e-13 (ii). Starts agree as in the fit table.
- **Outcome under the old rule: both forms pass G1 and G3 and fail G2**, so S2 was started. S2 was stopped by
  decision 23 before it finished; its partial results were discarded and are not reported.
- **Mamun, like-for-like** (n = 19, 120 °C, 30 mass %): Zhang 2011 eNRTL 13.5 % (calibration), Baygi 2015 21.03 %,
  Najafloo 2018 39.96 %; C_src 18.5 %; (i) 34.7 %; (ii) 31.8 %, both about 30–35 % low on average. Akula 2023a pooled:
  40.5 %, against 21.5 % and 21.1 % on the comparable rows here (Akula's rows are not these rows; Hilliard and Jou
  are calibration rows here).
- **Speciation** is AARD / RMS ln over the HCO₃⁻ + CO₃²⁻ pool. **Carbonate:** model over measured share of dissolved
  carbon at 20 and 40 °C, loading 0.11–0.40, excluding the out-of-line 40 °C, loading 0.21 point.
- **#108 rows:** second look; not untouched: these rows were scored in #106.
- **NaHCO₃ φ** (`nahco3.py`): Na⁺ from Figiel 2025 Table 3 (σ 2.8232 Å, u/k 230 K, d_Born 3.445 Å), packing 0.88σ,
  Na⁺–water −0.3 (Figiel Table 5, 298.15 K, not refitted), Na⁺–HCO₃⁻ −0.514 (Held 2014 Table 3), each fitted
  HCO₃⁻–water value; 278.15–318.15 K, 0.001–1 mol/kg, against φ^st. An indicative outside check, not a gate.

## Checks N1 and N2 (decisions 1–13, before decision 20)

The work stopped at N1, before B1, B2 or any ternary fit, and no parameter was fitted.

### N1: NaCl counter-ions (`n1-nacl.csv`)

NaCl osmotic coefficient at 298.15 K and 0.101325 MPa, against Hamer & Wu 1972 Table 16 at 0.1–5 mol/kg (21 rows).
Na⁺ and Cl⁻ come from Held 2014 Tables 2–3 in Held's convention: packing 0.88σ, Debye–Hückel and Born σ.

| Born form of the electrolyte family | NaCl φ ARD (limit 3.5 %) | max \|φ(Born) − φ(no Born)\| (limit 1e-10) |
|---|---:|---:|
| as loaded, c_shell = c_dielectric = 1 (the form refit C and C_src used) | **25.42 %** | **0.720** at 5 mol/kg |
| c_shell = c_dielectric = 0 (the form #121's model section states; diagnostic) | 1.242 % | 4.9e-13 |
| Born off (Debye–Hückel only) | 1.242 % | — |

- **Finding.** #121 states the base uses "original Born, with c_shell = c_dielectric = 0". The record omits
  both coefficients, and `shared_evaluation.MODEL_RUNTIME_DEFAULTS` fills (1, 1). This matches the Engine's own
  resolution rule for documents without them: water declares f_solv = 1.5 (Engine `docs/science/full-eos.md` §7).
- **Why E3 fails for (1, 1).** In the Engine's Born term (`born.hpp`), the outer-shell diameter
  D_i = d_i^Born[1 + c_shell(f_mix − 1)/|z_i|] uses f_mix = Σ x_k f_k / Σ x_k over every component with
  f_k > 0, ions included (f = 1). D_i therefore changes with the salt fraction, so the Born energy is not linear
  in the ion amounts. It then contributes to ln a_w: φ falls from 0.940 to 0.768 at 1 mol/kg.
- **Outcome under #121.** The N1 Born invariant is a shared step (outcome 1), and the 25.4 % ARD is a
  counter-ion agreement failure (outcome 2). Both stop all work and go to the owner.
- **Locator defect.** #121 names Engine packet `hamer-wu-1972-aqueous-alkali-halides/1` for the φ values, but
  that packet holds only γ±. `hamer-wu-1972-nacl-osmotic.csv` carries Hamer & Wu Table 16's φ and γ± columns
  from the reading copy `literature/Hamer1972--VYE43TLN.md`.
  - All 21 γ± values equal the packet's NaCl rows.
  - All 21 φ values are reproduced by Hamer & Wu Eq. (3.11) with the printed NaCl constants
    (B* = 1.4495, β = 2.0442e-2, C = 5.7927e-3, D = −2.8860e-4, A = 0.5108) within 5e-4, the printed rounding.
  - The Zotero PDF is not in local storage.

### N2: the E4 transformation (`n2-nacl.csv`; base record as loaded, NaCl)

| Check | Limit | Result |
|---|---|---|
| (i) ln a_w: `Reference.activity` vs ln φ_w^V,pure − ln φ_w^L,pure at p_b | 1e-8 | 1.2e-9, 8.2e-11, 1.4e-10; **2.25e-8 at 298.15 K, 1 mol/kg** |
| (ii) \|ln a_w(p_b) − ln a_w(0.101325 MPa)\| | 1e-5 | ≤ 6.6e-7 (estimate: 7e-7 at 1 and 4e-6 at 3 mol/kg) |
| (iii) Approximation B correction terms at the NaCl p_b | report | 5.9e-5 to 1.37e-4 per mol/kg (estimate: 5e-5 to 1.6e-4) |
| (iii) gate: \|B_w,model − B_ref\| ≤ 0.3·\|B_ref − v_w^L\| | ratio ≤ 0.3 | **0.746, 0.491, 0.346** at 298.15, 318.15, 333.15 K |
| (iv) `pressure` Jacobian in k(Cl⁻–water) and its 1/T slope vs central differences, 318.15 K | 1e-5 relative | ≤ 6.8e-8; solve residuals 3.8e-15 and 2.8e-14 |

- **(i) diagnosis.** ln a_w from the mixture's own fugacity coefficient on polished liquid roots equals the E4
  identity within 9.5e-10 at every state (`identity_minus_mixture_fugacity`). The 2.25e-8 difference is in the
  `Reference.activity` value.
  - The Engine's liquid root at a few kPa meets its density criterion (DENSITY_ROOT_RESIDUAL 1e-12), yet leaves
    P(ρ) about 1.1e-8 (relative) off the requested pressure, which moves ln φ_L by about 1.1e-8.
  - `binary.polished_state` polishes the density by Newton steps on P(ρ). The pure-water ln φ difference then
    varies by about 1e-9, against 2e-8 unpolished.
  - #121 uses `Reference.activity` only in checks, but it names (i) a stop condition.
- **(iii) B_w.** The model's water B_w is −2.180, −1.344 and −0.980 L/mol at 298.15, 318.15 and 333.15 K, from
  RT ln φ_w^V/p at 1 Pa; the values at 10 and 100 Pa agree within 3.1e-5 relative. IAPWS G11-15 Eq. (5) gives
  −1.241, −0.895 and −0.723 L/mol.
  - It reproduces the guideline's Table 7 at 200, 300 and 400 K within 7e-10.
  - Document SHA-256 `00fbe4df…dec8f`, as decision 10 records.
  - v_w^L uses standard liquid densities 997.05, 990.21 and 983.20 kg/m³.
  - Under #121, an N2(iii) failure stops Route B and goes to the owner.
- **The Engine accepts the ionic bubble point** (the capability #121 lists as not established) when the
  document holds only the solution's species. A record with absent species (zero feed) is refused as
  "rank-deficient declared equations", even for pure water, so `binary.document` reduces the record to water
  and one salt.

### Files and commands (N1, N2)

- `binary.py`: the reduced salt–water document (base record + Held Na⁺/Cl⁻), E2 compositions, the E4 identity
  and target pressure, `Reference.activity`, and the bubble point with the vapor limited to water.
- `checks.py`: N1 and N2, writing `n1-nacl.csv` and `n2-nacl.csv`.

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python checks.py n1
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python checks.py n2
```

The pinned wheel must be installed; `probe.py` checks it. The IAPWS document is fetched to the ignored
`../results/runs/model-d/` only to read it; Eq. (5) is transcribed in `checks.b_ww_iapws`.
