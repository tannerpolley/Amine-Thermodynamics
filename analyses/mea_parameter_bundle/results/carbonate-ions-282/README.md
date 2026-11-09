# Water–HCO₃⁻ and water–CO₃²⁻ anchored to sodium-salt osmotic data (issue 282): F1 failed, MEA refit not run

**Result.** The salt reference is not established on the selected record's water model, so falsifier F1 fails and the issue stops before its step 3. On one combined parameter document:
- **Na₂CO₃.** Water–CO₃²⁻ reproduces the Peiper & Pitzer Na₂CO₃ osmotic coefficients with an AARD of **5.11 %**, against the 1.5 % limit.
- **Bounds.** Two of the five fitted coefficients end on their −1 lower bounds: the water–Na⁺ constant (1a) and the water–CO₃²⁻ constant (1c).
- **NaHCO₃.** Water–HCO₃⁻ fits the NaHCO₃ rows with an AARD of 0.163 % and interior coefficients. Its value at 313.15 K is **0.171**, below the 0.5 falsification level.

Per the issue's F1 branch:
- No MEA refit runs on an unestablished anchor.
- The leverage check (step 3), the MEA refit and F2 (steps 4–5) and the MDEA transfer (step 6) are **not run because F1 failed**.
- No alternating or joint salt fit was run; the issue does not authorize one.

Nothing is adopted: `selected-current-best-parameters.json`, the Engine pin, `docs/scientific/latex/` and `analyses/_cse-manuscript.json` are unchanged.

This is calibration and numerical verification against model-derived reference values (Peiper & Pitzer's Pitzer-model tables), not validation.

## Inputs and method

- **Engine.** `main` `bc7794731e94be961d16028d3f4880c6718a93ad`, wheel SHA-256 `8b9609d4c8908d9397833988158f525c92dd28e3bcf7333f4c3b33c48db99069`, installed in this worktree only. Every JSON result records the wheel.
- **Script.** [`carbonate_ions_282.py`](../../scripts/carbonate_ions_282.py): `qualify | salt | scan | leverage | anchors | fit | assess | select`. It imports `stable_refit_255.py` unchanged. Only `qualify`, `salt` and the diagnostic `scan` were run (see [logs/](logs/)).
- **Water and electrolyte model.** The selected record (`00e77608…`) reduced to water, Na⁺, Cl⁻, HCO₃⁻, CO₃²⁻ and OH⁻.
  - Na⁺ (2.8232 Å, 230 K) and Cl⁻ (2.7560 Å, 170 K) come from Held 2014 Table 2, strategy 2. They follow the record's ion conventions: packing diameter 0.88σ, Debye–Hückel diameter σ, Born diameter σ (a design choice), solvation factor 1 and ionic-region relative permittivity 8.
  - Cross interactions from Held 2014 Table 3: Na⁺–Cl⁻ 0.317, Na⁺–HCO₃⁻ −0.514, Na⁺–CO₃²⁻ −1.000 and Na⁺–OH⁻ 0.649. Cl⁻–water is −0.25.
  - HCO₃⁻, CO₃²⁻, OH⁻ and every other ion–water value are the record's.
- **Laws.** Each fitted law is $k(T)=a_0+a_1(T-298.15\ \mathrm K)$, in the Engine's `polynomial-plus-reciprocal-temperature` form with no 1/T term.
  - Water–Na⁺ holds Held's slope, $a_1=-0.007981$ K⁻¹.
  - Bounds (design choices): $a_0\in[-1,1]$ and $a_1\in[-0.02,0.02]$ K⁻¹. Starts are Held's values at 298.15 K: 0.00046, 0.00 and −0.25.
- **Data** ([inputs/](inputs/)).
  - [Hamer & Wu 1972 Table 16](inputs/hamer-wu-1972-nacl.csv): NaCl at 298.15 K, 0.1–1.0 mol/kg; residual scale 0.003.
  - [Peiper & Pitzer 1982 Table 6(a–e)](inputs/peiper-pitzer-1982-table6.csv): rows at 0.01–1.0 mol/kg nominal and 278.15–318.15 K, residual scale 0.01. That is 45 NaHCO₃ and 45 Na₂CO₃ fitted rows, plus 45 mixed rows as a comparison.
- **Transcription.** Both tables were transcribed from the page images of the Zotero PDFs, not from the Markdown reading copies. Hashes:
  - Peiper & Pitzer `8d713ff2…9702` (attachment X8GEDSJ2);
  - Hamer & Wu `a20e0029…4ca6` (attachment 5RS9QAMK).
- **Transcription checks.**
  - Each Peiper & Pitzer row is checked against its own printed water activity: $\phi=-\ln a_w/(M_w\sum_j m_j)$ agrees within print rounding at 133 of 135 rows. The other two, NaHCO₃ at 278.15 K and 0.1 and 0.8 mol/kg, sit at 1.10× and 1.07× the rounding bound. Both match the PDF text layer, so they are kept as printed.
  - The 45 NaHCO₃ rows also match the independent #122 transcription, `data/reference/MEA/observations/ionic_activity/peiper_pitzer_1982_nahco3_osmotic.csv`, exactly.
- **Observable.**
  - NaCl uses the formula path, `regression.electrolyte(kind="osmotic_coefficient")`.
  - Carbonate rows use `regression.mixture_osmotic_coefficient` at the printed equilibrium ionic composition, with Na⁺ nominal and the minor anion set by charge balance (CO₃²⁻ for NaHCO₃ rows, OH⁻ for Na₂CO₃ rows).
  - The largest charge adjustment is 4×10⁻⁴ mol/kg.
  - Dissolved CO₂ is removed as ideal: $\phi_\mathrm{ion}=(\phi\sum m-m_\mathrm{H_2X})/\sum_\mathrm{ions}m$. Its largest share of Σm is 0.78 %, at 318.15 K and 1.0 mol/kg NaHCO₃.
  - Six mixed rows are unavailable, because charge closure gives a negative OH⁻.
  - At the fitted laws the formula path and the full-composition path give the same NaCl Φ within 2×10⁻¹⁶.
- **Cascade.** Each fit uses the Engine's least squares (`regression.fit`), run in order:
  - (1a) water–Na⁺ $a_0$ on NaCl;
  - (1b) water–HCO₃⁻ $a_0,a_1$ on NaHCO₃, with (1a) held;
  - (1c) water–CO₃²⁻ $a_0,a_1$ on Na₂CO₃, with (1a) and (1b) held.

  F1 is then scored on one combined document that holds all three final laws.

**Qualification (Method 1)** ([qualification/summary.json](qualification/summary.json)): the final set and the #255 candidate replay on this wheel with relative row and cost differences of 0.0 against the retained #255 rows (`qualification/final-replay.json`, `wide/replay.json`): 307/307 rows available, costs 148.883260 and 148.510546. Passed.

## Salt fits

| Fit | Iterations | Cost (start → end) | Endpoint | On a bound | Replay vs fit |
|---|---:|---|---|---|---:|
| [1a water–Na⁺](salt/1a-sodium.json) | 2 | 5035.6 → 110.80 | $a_0=-1.000$ | $a_0$ (lower) | 0 |
| [1b water–HCO₃⁻](salt/1b-bicarbonate.json) | 5 | 5.582 → 0.6067 | $a_0=0.11173$, $a_1=3.9312\times10^{-3}$ K⁻¹ | none | 1.3×10⁻¹¹ |
| [1c water–CO₃²⁻](salt/1c-carbonate.json) | 10 | 1025.3 → 411.79 | $a_0=-1.000$, $a_1=1.9631\times10^{-3}$ K⁻¹ | $a_0$ (lower) | 1.1×10⁻¹¹ |

**F1 on the combined document** ([salt/summary.json](salt/summary.json), [φ residuals](salt/phi-residuals.csv)):

| Rows | n | AARD % | Max % | AARD by T (278 / 288 / 298 / 308 / 318 K) | Gate |
|---|---:|---:|---:|---|---|
| NaCl, 298.15 K | 10 | 1.514 | 1.68 | — | no AARD gate; $a_0$ on bound fails F1 |
| NaHCO₃ | 45 | **0.163** | 0.47 | 0.225 / 0.121 / 0.129 / 0.113 / 0.228 | ≤ 1.5 %: pass |
| Na₂CO₃ | 45 | **5.111** | 8.28 | 4.62 / 5.13 / 5.36 / 5.35 / 5.09 | ≤ 1.5 %: **fail** |
| mixed (comparison) | 39 | 2.561 | 6.30 | 3.42 / 2.61 / 2.43 / 2.37 / 2.23 | not fitted |

The F1 gates:
- coefficients interior: **fail** (1a and 1c $a_0$ at −1);
- NaHCO₃ AARD: pass;
- Na₂CO₃ AARD: **fail**;
- water–HCO₃⁻ at 313.15 K = 0.171 < 0.5: the compensation hypothesis is not falsified by this criterion.

**F1 outcome: failed.**

**Fitted laws** ([salt/laws.csv](salt/laws.csv), 278.15–393.15 K in 5 K steps):

| Law (about 298.15 K) | About the record's 313.15 K | Value at 313.15 K |
|---|---|---:|
| water–Na⁺: $-1.000-0.007981\,(T-298.15)$ | $-1.11972-0.007981\,(T-313.15)$ | −1.1197 |
| water–HCO₃⁻: $0.11173+3.9312\times10^{-3}(T-298.15)$ | $0.17069+3.9312\times10^{-3}(T-313.15)$ | **0.1707** |
| water–CO₃²⁻: $-1.000+1.9631\times10^{-3}(T-298.15)$ | $-0.97055+1.9631\times10^{-3}(T-313.15)$ | −0.9706 |

The comparison curves are Held 2014 (HCO₃⁻ 0.00, CO₃²⁻ −0.25) and Wangler 2018 Table 6, read as polynomial orders. At 313.15 K, Wangler gives −0.100; the final set's bicarbonate–water k is 0.727 and the #255 candidate's 1.0. Extrapolated, the 1b law reaches 0.328 at 353.15 K and 0.485 at 393.15 K, against Wangler's −0.300 and −0.700.

![Left three panels: Peiper & Pitzer and Hamer & Wu osmotic coefficients on the ionic basis (points) and the combined-document model at the same rows (lines), by temperature. Right: fitted water–anion laws over 278–393 K with the fitted range shaded, against Held 2014, Wangler 2018, the final set and the #255 candidate.](salt/phi-molality.png)

**Why the anchor fails (diagnostics, not a fix).**
- **Direction toward the bound.** At 298.15 K, lowering the water–Na⁺ or water–CO₃²⁻ intercept through the five tested values (−1, −0.5, 0, 0.5 and 1), with the other coefficients fixed, raises φ toward the reference values at every sampled molality. This supports the direction toward the lower bound for those rows; it does not establish global optimality of the full temperature-dependent fit. ([salt/sensitivity.json](salt/sensitivity.json), `scan`, no fit.)
  - NaCl at 0.4 mol/kg: φ goes 0.790 → 0.905 as water–Na⁺ $a_0$ goes from +1 to −1, against 0.920 observed.
  - Na₂CO₃ at 0.1 mol/kg and 298.15 K: water–CO₃²⁻ $a_0$ moves φ only from 0.748 to 0.764, against 0.817.
- **Na₂CO₃ is low before k matters.**
  - The deficit is −1.1 % at 0.01 mol/kg, where k has almost no lever.
  - It grows to −8.1 % at 0.2 mol/kg, then shrinks to −4.0 % at 1.0 mol/kg.
  - This is consistent with the 2:1 electrostatic and Born treatment on this water, and with the fixed Na⁺–CO₃²⁻ = −1.000 (a bound value in Held 2014), carrying most of the error rather than water–CO₃²⁻. That is an inference: no term-by-term decomposition was run.
- **NaCl stays low at the bound.** It is −1.06 % at 0.1 mol/kg and −1.68 % at 0.5 mol/kg with water–Na⁺ at −1.
- **The water-model mismatch.** The record's water (m = 1.253, u/k = 432.4 K, ε^AB/k = 1757 K) differs from the Fuchs water that Held's ion parameters were fitted with. The Born-diameter choice for Na⁺/Cl⁻ is not from a source.

**Consequence.** The 1b water–HCO₃⁻ law (0.171 at 313.15 K) fits NaHCO₃ well. However, it is conditional on a water–Na⁺ value pinned at its bound, so it is not an established salt anchor; the issue's F1 rule treats it that way. Whether to revise the salt-reference design is the owner's decision. Options include the Na⁺/Cl⁻ Born diameter, refitting Na⁺–CO₃²⁻, a wider k range or a different Na⁺ reference. This build makes no such change.

## Steps not run

| Step | Status |
|---|---|
| 3. Leverage check (MEAH⁺–HCO₃⁻ ±0.1) | not run because F1 failed |
| 4. MEA refit, both starts; anchor qualification and retreat | not run because F1 failed |
| 5. Assessment against #255 criteria 1–3 (F2); carbonate and pool comparisons | not run because F1 failed |
| 6. MDEA transfer (frozen R2; refit R2) | not run because F1 failed; with no MEA candidate, the fitted-R2 case does not exist |

The code for steps 3–5 is in the script (`leverage`, `anchors`, `fit`, `assess`, `select`), which refuses to run unless `salt/summary.json` records F1 as passed. It has not been executed.

## Limits

- The Peiper & Pitzer values are Pitzer-model reference values (their §§2–4), not raw measurements.
- Dissolved CO₂ is treated as ideal in the φ conversion, and the printed compositions are charge-closed.
- With one chloride salt, the water–anion values depend on:
  - the Cl⁻–water = −0.25 convention;
  - Held's Na⁺ slope;
  - the Na⁺/Cl⁻ Born diameter.
- Na⁺–HCO₃⁻, Na⁺–CO₃²⁻ and Na⁺–OH⁻ are Held values fitted with the Fuchs water.
- The salt laws are fitted at 278–318 K; their values above 318 K are extrapolations.
- The fitted salt laws describe the salt data on this water model only, and were never used in an MEA calculation here.
