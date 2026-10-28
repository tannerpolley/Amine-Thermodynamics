# Unloaded MDEA–water heat capacity at the A1 endpoint (diagnosis)

Diagnosis only. Nothing was fitted or adopted. No frozen #222 choice, MEA record or manuscript was changed. The run used Engine 3e83e19c (wheel SHA-256 0d08dff9…6804), through `/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I`. Base commit: 526ba08.

## Result

**Cause (a numerical model result, established by a one-change probe).** The +19 to +28 % over-prediction of unloaded Weiland 1997 Cp comes from the **reciprocal-temperature slope of k(MDEA–water)**, s = −94.37 K at A1, in the law k(T) = k₀ + s(1/T − 1/313.15 K).
- **The probe.** Only s was set to 0, with A1's k₀ kept. The error falls from +18.8 / +24.3 / +26.8 % to −2.5 / −1.9 / −2.5 % at 30 / 40 / 50 wt%.
- **The term that changes.** The whole difference sits in the dispersion residual Cv: 83.96 → 65.70 J/mol/K at 30 wt%. The hard-chain and association terms change by less than 0.15 J/mol/K.
- **Excess Cp.** The model's excess Cp falls from 25.0 / 33.0 / 40.5 to 5.5 / 7.4 / 9.2 J/mol/K. The apparent measured value is 4.2 / 4.3 / 5.3 J/mol/K.

**Mechanism (follows from the equations; not separately tested).**
- With this law, the cross-dispersion energy carries a factor (1 − k₀ + s/T_ref)/T − s/T². The −s/T² part adds a Helmholtz term whose residual Cv is not zero.
- With s < 0, the MDEA–water attraction strengthens as T falls. The mixing energy therefore rises with T, which gives a positive excess Cp that scales roughly as 1/T².
- The measured error has the same shape. Against Concepción 2023, A1's over-prediction is 25 % at 293 K and 5.7 % at 353 K (40 wt%).

**Not the cause:**
- **Water:** model Cp is −1.5 % against IAPWS-95 at 298.15 K, which acts in the opposite direction.
- **Pure MDEA:** the model under-predicts it by 15.6 %, also in the opposite direction.
- **Association:** the association excess is −1.2 J/mol/K.
- **The other parameters:** κ, MDEA association energy ±10 % and the ideal-gas Cp choice each move the error by ≤ 4 points. The ideal-gas change and turning cross-association off both make it worse.

**Why the slope sits there (evaluation at fixed k₀, not a refit).**
- Setting s = 0 raises the Kim 2008 bubble-pressure AARD from 0.50 % to 4.5 %, with the item-(k) k₀ kept.
- It raises the Sobrino 0.1 MPa unloaded-density cost from 1274 to 6635 at the frozen 0.5 kg/m³ scale and weight 10. The mean residual moves from +0.06 to +1.59 kg/m³.
- These agree with the earlier attribution fits: without Cp the fit chose s = −175.6 K; without density it chose s = −17.1 K.
- **Inference:** with one reciprocal-T law, the temperature dependence that Kim VLE and Sobrino density ask for brings an excess Cp 5–9 times the measured value. That is the conflict behind A1's bound pressure. Whether a k₀ refit at s = 0 recovers part of the VLE/density fit was not tested.

**Not resolved.** With s = 0, the model under-predicts Concepción Cp increasingly with temperature: −1.8 % at 293 K, falling to −12.3 % at 353 K (40 wt%). So s = 0 matches 298 K, but it does not reproduce the temperature trend. The second deficiency behind this was not diagnosed.

## 1. Reproduction (`reproduction.csv`)

| State, 298.15 K | Observed, J/g/K | A1, fitted equilibrium | A1, frozen | Item-(k) pre-fit, frozen |
|---|---:|---:|---:|---:|
| 30 wt% | 3.787 | 4.5055 (+19.0 %) | 4.4982 (+18.8 %) | 4.3353 (+14.5 %) |
| 40 wt% | 3.585 | 4.4757 (+24.8 %) | 4.4564 (+24.3 %) | 4.2662 (+19.0 %) |
| 50 wt% | 3.407 | 4.3559 (+27.9 %) | 4.3214 (+26.8 %) | 4.1188 (+20.9 %) |
| 60 wt%, outside fit | 3.174 | — | 4.0864 (+28.7 %) | 3.8871 (+22.5 %) |

- **The two A1 columns.** The fitted-equilibrium values are the A1 `fit.json` predictions. "Frozen" means a neutral liquid with no reactions, from `Mixture.state`. The 0.2–0.8 % gap between them is attributed to the reaction-shift part of the equilibrium Cp in an unloaded solution (inference; not separated).
- **The item-(k) pre-fit** differs from A1 only in k(MDEA–water): (−0.18179, −75.54 K).
- **The Concepción 2023 rows** (Table 6, 0.1 MPa, 10–40 wt%, 293–353 K) are in the same file.

## 2. Term decomposition (`decomposition.csv`, `excess-cp-composition.csv`)

All values are at 298.15 K and 101325 Pa, on the liquid root, in J/mol/K.
- **Additive terms.** The residual Cv of each term, Cv_X = −R(2T ∂a_X/∂T + T² ∂²a_X/∂T²), is taken at fixed ρ and x from the Engine's per-term `hard_chain`, `dispersion` and `association` values. The derivatives are central differences with ΔT = 0.05 K.
- **Coupling.** The non-additive coupling is Cp − Cv − R = T(∂P/∂T)²_ρ/(ρ²(∂P/∂ρ)_T) − R, built from the per-term pressure derivatives.
- **Closure.** The sum matches the Engine's `residual_isobaric_heat_capacity` within 8.3×10⁻⁸ relative.

| A1 state | Cp | Ideal gas | Hard chain Cv | Dispersion Cv | Association Cv | Coupling, Cp−Cv−R |
|---|---:|---:|---:|---:|---:|---:|
| Pure water | 74.21 | 33.59 | −65.67 | 76.26 | 36.10 | −6.07 |
| 30 wt% | 108.72 | 41.36 | −47.16 | 83.96 | 33.83 | −3.27 |
| 40 wt% | 121.55 | 45.27 | −40.35 | 85.58 | 33.00 | −1.95 |
| 50 wt% | 135.25 | 50.35 | −33.05 | 86.25 | 32.08 | −0.37 |
| Pure MDEA | 230.61 | 161.21 | 32.46 | 6.52 | 18.69 | 11.74 |
| 30 wt%, s = 0 | 89.26 | 41.36 | −47.02 | 65.70 | 33.84 | −4.61 |

The excess over a mole-fraction average of the model's own pure liquids is broken down below.

| State | Hard chain | Dispersion | Association | Coupling | Total excess Cp |
|---|---:|---:|---:|---:|---:|
| A1, 30 / 40 / 50 wt% | +12.5 / +16.3 / +19.7 | **+11.9 / +15.7 / +19.2** | −1.2 / −1.5 / −1.7 | +1.7 / +2.5 / +3.4 | 25.0 / 33.0 / 40.5 |
| s = 0, 30 / 40 / 50 wt% | +12.7 / +16.5 / +19.9 | −6.3 / −8.1 / −9.7 | −1.2 / −1.5 / −1.7 | +0.4 / +0.6 / +0.7 | 5.5 / 7.4 / 9.2 |
| Apparent measured | | | | | 4.2 / 4.3 / 5.3 |

**Observation, not diagnosed.** The hard-chain excess of about +12.5 J/mol/K does not depend on the slope. It sits alongside large opposing hard-chain and dispersion Cv in pure water (−65.7 and +76.3), which is consistent with water's temperature-dependent segment diameter. With s = 0 it is partly cancelled by a negative dispersion excess. This may bear on the unresolved temperature trend.

## 3. Pure MDEA (`pure-mdea.json`)

**Reference.**
- None of the primary pure-MDEA liquid Cp sets is in Zotero.
- The reference used is the Neumann et al. 2022 Helmholtz equation of state (Zotero CA5R9QN8; Eqs. 5–7, Tables 8–10). Its liquid Cp is fitted to Zhang et al. 2002, a DSC study with a stated 2 % uncertainty. The authors give a 4 % guideline against the seven literature sets.
- The implementation reproduces the Table 11 test pressures and sound speeds within 7.6×10⁻⁷.
- This is a correlation of the measurements, not a measurement.

| T, K | Neumann Cp | Model Cp | Model − Neumann | Neumann ideal / residual | Model ideal / residual |
|---|---:|---:|---:|---:|---:|
| 298.15 | 273.2 | 230.6 | −15.6 % | 189.2 / 84.0 | 161.2 / 69.4 |
| 313.15 | 281.0 | 237.1 | −15.6 % | 198.8 / 82.2 | 167.6 / 69.5 |
| 333.15 | 291.4 | 245.8 | −15.6 % | 211.0 / 80.3 | 176.2 / 69.7 |
| 353.15 | 301.7 | 254.6 | −15.6 % | 222.7 / 79.0 | 184.7 / 69.9 |

- **Where the deficit sits.** Of the −42.6 J/mol/K deficit at 298 K, −28.0 comes from the Wangler ideal-gas Cp and −14.6 from the residual part. With the Neumann ideal-gas Cp, the model's pure MDEA is −5.3 % (258.6).
- **Densities.** Model 1030.8 kg/m³ against Neumann 1034.8 at 298 K.
- **Apparent measured excess Cp.** This is Weiland Cp × molar mass minus the mole-fraction average of Neumann MDEA and IAPWS-95 water: +4.2 / +4.3 / +5.3 / +4.6 J/mol/K at 30–60 wt%. The 4 % Neumann guideline adds about ±0.7 to ±2 J/mol/K, scaled by x_MDEA.
- **Missing sources, with DOIs:**

| Source | DOI or citation |
|---|---|
| Zhang, Hawrylak, Palepu and Tremaine 2002 (excess Cp of water + MDEA, and pure MDEA) | 10.1006/jcht.2002.0937 |
| Chiu, Liu and Li 1999 | 10.1021/je980217x |
| Chen, Shih and Li 2001 | 10.1021/je0000367 |
| Maham et al. 1997 | 10.1039/a607568a |
| Mundhwa and Henni 2007 | 10.1021/je0604232 |
| Hawrylak et al. 2006 | Zh. Khim. Termodin. Termokhim. 38, 988–1007; no DOI located |

- **Not inspected.** Weiland 1997 has no pure-MDEA Cp rows. The Zhang et al. 2002 excess-Cp data could not be compared directly.

## 4. Sensitivities (`sensitivity.csv`)

Each case is one change from A1: frozen Cp at 298.15 K, error against Weiland (%), and the shift in density from A1 (kg/m³).

| Case | 30 wt% | 40 wt% | 50 wt% | 60 wt% (outside fit) | Δρ at 30 / 50 wt% | Pure MDEA Cp |
|---|---:|---:|---:|---:|---:|---:|
| A1 | +18.8 | +24.3 | +26.8 | +28.7 | — | 230.6 |
| Ideal-gas Cp: Neumann | +20.6 | +26.9 | +30.3 | +33.2 | 0 / 0 | 258.6 |
| MDEA association energy ×0.9 | +19.0 | +24.6 | +27.3 | +29.4 | −0.15 / −0.35 | 234.9 |
| MDEA association energy ×1.1 | +18.6 | +24.0 | +26.4 | +28.2 | +0.11 / +0.25 | 226.3 |
| κ unconverted, 0.123858 | +18.7 | +24.3 | +26.8 | +28.7 | +0.01 / +0.02 | 229.9 |
| **k slope 0, k₀ kept** | **−2.5** | **−1.9** | **−2.5** | **−2.3** | −0.86 / −1.37 | 230.6 |
| k slope at Kim value, −75.54 K, k₀ kept | +14.5 | +19.0 | +20.9 | +22.5 | −0.17 / −0.27 | 230.6 |
| Item-(k) k₀ and slope | +14.5 | +19.0 | +20.9 | +22.5 | −0.05 / −0.07 | 230.6 |
| Cross-association off (diagnostic) | +22.5 | +29.0 | +32.4 | +35.3 | −1.25 / −2.24 | 230.6 |
| Two changes: slope 0 + Neumann ideal-gas Cp | −0.6 | +0.7 | +0.9 | +2.2 | −0.86 / −1.37 | 258.6 |

- **The MDEA association energy** also changes the Wolbach–Sandler cross energy, because the cross edges take it as an input.
- **Over temperature** (`concepcion-trend.csv`, 10–40 wt%, 293–353 K):

| Case | Error range against Concepción 2023 |
|---|---|
| A1 | +1.8 to +25.0 % |
| Item-(k) pre-fit | +0.6 to +19.6 % |
| s = 0 | −0.5 to −12.3 %, more negative as T rises |

- **Consequences of the slope** (`k-setting-consequences.json`):

| k(MDEA–water) setting | Kim AARD | Sobrino density cost |
|---|---:|---:|
| A1 | 1.87 % | 1274 |
| A1 k₀, s = 0 | 4.16 % | 6635 |
| Item-(k) pre-fit | 0.50 % | 1925 |
| Item-(k) k₀, s = 0 | 4.55 % | 6891 |

## 5. Water (`water-iapws.csv`)

The frozen MEA water, against IAPWS-95 at 101325 Pa (retained MEA reference, chemicals 1.5.2):

| T, K | Model − IAPWS-95 |
|---|---:|
| 298.15 | −1.48 % |
| 318.15 | −0.72 % |
| 353.15 | −0.15 % |

Water is not the source: it would bias mixture Cp low by about 1.4 % at 298 K.

## Design options (no decision made)

1. **Fix or bound the MDEA–water reciprocal slope near 0 and refit k₀,** then measure the cost on Kim VLE and Sobrino density. The evaluations here at fixed k₀ give an upper bound on that cost: Kim AARD 4.5 % and a 5× density cost.
2. **Change the k(T) functional form** so that the temperature dependence wanted by VLE and density carries less excess Cp. For example, a linear-in-T k contributes no first-order Cv. This is an inference, not tested.
   - The pinned Engine exposes only `Kij` and `KijReciprocalTemperatureSlope` as Python parameter families.
   - A native string `k_ij_temperature_slope` exists in `libepcsaft_native.so`, but whether a document can declare it is unverified.
   - Any new form is an Engine issue.
3. **Reweight or rescale Cp against density and Kim** in the joint objective, which is an owner trade-off. Or treat Weiland Cp as outside-fit evidence and record the excess-Cp failure as a claim limit.
4. **Address pure-MDEA Cp separately** (−15.6 %). The Neumann ideal-gas Cp makes pure MDEA −5.3 % and, together with s = 0, brings unloaded Cp within −0.6 to +2.2 %. At A1's slope it worsens the mixture.
5. **Diagnose the remaining temperature trend** with s = 0 (−12 % at 353 K) before any adoption. It may involve water's temperature-dependent diameter in the hard-chain excess.

## Reproduce

```
nice -n 10 /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/scripts/diagnose_unloaded_cp.py
```

It runs in about 7 s, serially. `summary.json` records the A1 and item-(k) k values, the Neumann ideal-gas cubic (maximum deviation 1.3×10⁻⁴ over 293–423 K), the decomposition closure, the finite-difference steps and the runtime record. The research notebook was not updated; that is a summarize-stage step.
