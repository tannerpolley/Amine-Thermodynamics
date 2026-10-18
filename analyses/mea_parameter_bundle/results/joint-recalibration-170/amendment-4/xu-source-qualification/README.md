# Xu & Wang 2018 N₂O rows: source pressure/gas-reference qualification (#170, amendment 4)

Researched 2026-10-18 (owner away; every choice below is reversible). Stdlib
computation only; no Engine call and no fit.

## Result

**All 16 MEA-only Xu rows meet B1 on the same terms as Hartono.** Xu, Wang &
Chen 2013 (the apparatus Xu 2018 refers to) obtains the N₂O pressure as the
measured total minus the measured solvent pressure. That is the Hartono 2008
Eq. 5 basis. The vapor-side correction f_N₂O/pN is 0.9940–0.9949, and
after it the signed transfer is −0.21 to +0.63 %. The largest per-row bound is
**0.64 %**, inside the 1 % rule. Uncorrected, 15 of 16 rows exceed 1 % in the
widest coefficient envelope (up to 1.23 %), so the correction is required, as
it was for Hartono.

This clears the gate that made Xu comparison-only ("until Table S3 and its
pressure/gas reference are verified", addendum lines ~120–235). It does not
make Xu agree with Hartono. At the released Hartono-only pair the model is
−7.1 to +23.2 % from the B1-corrected Xu targets, against at most 1.41 % from
Hartono. Whether Xu rows enter the fit is the orchestrator's decision, and no
fit was run (see the last section).

## Sources read

| Source | Zotero (parent / PDF), sha256 | Read |
|---|---|---|
| Xu, Wang & Chen 2013, J. Chem. Eng. Data 58, 1633, doi:10.1021/je301371p | `JFF3PK44` / `WJ8UVRHC`, `bb0e3270…ecd50` | Experimental Section, "Solubility of N₂O", Figure 1, Eqs. 2–4 p.1634; Eqs. 5–7, Table 2 and calibration text p.1635 (page images) |
| Xu & Wang 2018, J. Chem. Eng. Data 63, 2708, doi:10.1021/acs.jced.8b00070 | `4TDQZ354` / `S5PK66RR`, `62cd127f…92641` | §2.3 and Eqs. 2–8 p.2710; water-check sentence p.2711; Table 4 p.2711; Table 8 p.2715 (page images) |
| Xu & Wang 2018 supporting information | `4TDQZ354` / `9JKXQ7ID`, `b14f133e7a18db22d8ebaa5d81845430ce6a4f77b9fcadfeb8f45fc016c85071` | Complete (2 pages): Tables S1–S2 PDF p.1, Table S3 PDF p.2 (page images; MEA block also at 200 dpi) |

The abbreviated SI hash first written in `../b1-vapor-bound/README.md`
(`…5c85071`) had one wrong character and is corrected there; the full value is
above and in `sources.json`.

## Xu 2013 measurement method

| Question | What the source says | Locator |
|---|---|---|
| N₂O pressure | "After the solution reached vapor liquid equilibrium at set temperature, the pressure inside of the reactor, P1,N₂O, was recorded", then N₂O was added. Eq. 4 is printed as P_N₂O = P1,N₂O − P2,N₂O, with P2,N₂O "the total pressure of reactor after reaching equilibrium". As printed the sign is inverted; physically P_N₂O = P2 − P1. | p.1634 left/right columns, Eq. 4; p.1635 first line |
| Solvent pressure | P1 is measured in the evacuated reactor at the set temperature before N₂O is added. Its values are not printed. The reactor is "vacuumed until the pressure was less than 1 kPa" and the solution is then sucked in, so any residual gas is inside P1 and is subtracted. | p.1634 |
| Gas EOS, tank | Eq. 2: n_added = (V_V/R)(P_V1/(T_V1 z1) − P_V2/(T_V2 z2)); "The compressibility factor was calculated using the Peng−Robinson equation of state." | p.1634, Eq. 2 and following sentence |
| Gas EOS, reactor | Eq. 3: n_g = P_N₂O(V_R − V_S)/(z_N₂O R T_R), with z the N₂O compressibility after equilibrium (pure N₂O at its partial pressure). Eqs. 5–7: n_l = n_added − n_g, C = n_l/V_S, P_N₂O = H C. | p.1634 Eq. 3; p.1635 Eqs. 5–7 |
| Volumes | V_V = 2.186·10⁻³ m³ (water fill); V_R = 5.628·10⁻⁴ m³, "measured by adding into it a known amount of N₂O from the holding vessel"; solvent "around half of reactor". | p.1634 |
| Transducers | "two pressure transducers (Druck PTX 7515 with uncertainty 0.2 % of full scale (200 kPa))" for the reactor and the vessel | p.1634 |
| Calibration | Water and 30 mass% MEA agree with the literature "within 3 % when less than 313.15 K", and differ by about 7 % from Versteeg & van Swaaij at 323.15 and 333.15 K. Table 2 P_N₂O values (111–182 kPa) vary irregularly with T, which suggests separate charges in 2013. | p.1635, Table 2 and text |

**Xu 2018's own description** (§2.3 p.2710) says the apparatus "was reformed
from that of Xu et al.,16" (the 2013 paper): a quartz glass reactor, a gas tank and an
MFC. Its volumes are V_tank = 2.214·10⁻³ m³ (water fill) and
V_reactor = 5.439·10⁻⁴ m³, the latter "calculated from the pressures inside the
reactor before and after adding N₂O". About 120 g of absorbent are weighed in,
the reactor is sealed and evacuated, and "when the vapor liquid equilibrium at
the set temperature in the reactor was reached, N₂O was injected". The tank
amount uses Peng–Robinson (Eqs. 2–5), and n_g comes "from the equilibrium
partial pressure of N₂O in the reactor with the Peng−Robinson equation". The
2018 paper does not print the subtraction, the solvent pressures, the tank
fill or the transducer range. **The Eq. 4 basis therefore reaches the 2018 rows
through the citation, an inference consistent with the 2018 text, not a
2018 statement.**

Supporting inference: Table S2's water H at 333.15 K is 2.9 % below Versteeg
Eq. 5. If P3 were the total pressure, the 19.9 kPa water vapor would be counted
as N₂O both in P3 and in n_g. The reported H would then be high by more than
P/pN = 1.17, so the true value would sit about 17 % or more below Versteeg.

## Table S3 transcription and checks

The 16 MEA-only P3/x3 pairs (x₂ = 0.0394, 0.0870, 0.1456, 0.2197;
293.15–323.15 K) are now in
`data/reference/MEA/physical_solubility/Xu_2018_N2O_solubility.csv`, in the
same `P_N2O_reported_kPa`, `x_N2O_reported` and `supplement_*` fields the
Hartono rows use. The checks:

- **Transcription:** all 16 pairs match the SI text layer by script, and were
  read against the page image at 200 dpi.
- **Uncertainties** (Table S3 footnote): u(x₂) = 0.0002, u(T) = 0.1 K,
  u(p3) = 0.1 kPa, u_r(x₃) = 0.03.
- **Table 8 against S3:** Table 8 H times the measured gas-free molar density
  (Table 4) is −0.56 to +0.25 % from S3's direct P3/x3. Equivalently,
  P3/(c x₃/(1−x₃)) is −0.29 to +0.52 % from Table 8. That is above the printed
  rounding of about 0.2 %, but far below Hartono's 0.85–3.09 % Table 11/SI
  difference. The two Xu representations agree.
- **P3 range:** 84.8–105.9 kPa. The x₂ = 0.2197 column falls from 105.9 to
  100.4 kPa between 303.15 and 313.15 K; Table 8 uses the same values.

**Internal consistency, not part of B1.**

- **Charges:** within a composition P3 rises smoothly with T, which suggests
  one charge heated stepwise (not stated). The ideal-gas total N₂O implied by
  the printed P3 and x₃ falls by 1.1–2.9 % from 293.15 to 323.15 K at
  x₂ = 0.0394–0.1456. At x₂ = 0.2197 it falls by 9 % between 303.15 and
  313.15 K, a recharge or loss that the paper does not describe.
- **Gas-side sensitivity:** with 120 g in a 543.9 cm³ reactor, the gas holds
  5.4–9.1 times the dissolved N₂O. A 1 % error in the gas-side amount therefore
  moves x₃ by 5–9 %. Hartono's ratio is 1.9–4.4.
- **Water check:** Table S2's water values lie −2.8, +7.2, −3.7, +5.2 and
  −2.9 % from Versteeg Eq. 5 at 293–333 K. The sign alternates, so this is
  scatter rather than a trend; §2.3 p.2711 reports "less than 7.2%".

## B1 transfer on the Eq. 4 basis

The calculation follows the Hartono closure in `../b1-vapor-bound/README.md`
term by term:

- **Vapor model:** a second-virial N₂O + water gas. The water fugacity is fixed
  by the liquid, including its Poynting change and N₂O dilution, so
  ln(f₁/pN) ≈ B11c₁ + 2B12c₂.
- **Coefficients:** the same B11, B22, B12 and their envelopes (B11 ±10 % and
  ±25 cm³/mol, B12 × 0.5–2, B22 ±5 %).
- **Solvent pressure:** P_S° is the model's CO₂-free solvent pressure (dilute
  bubble pressure minus its CO₂ partial pressure, from
  `neutral-fit-superseded/A/evaluation.json` `start.predictions[7:]`), within
  ±10 %. It includes the model's MEA vapor.
- **Liquid term:** 0 to 100 cm³/mol × (pN + 0.1 P_S°)/RT.
- **Model term:** the model's own ln φ_CO₂ at its bubble state.
- **Third virial:** the 1.5e-3 allowance, scaled by c₂² relative to Hartono's
  row 7.

| T/K | x(MEA) | P3/kPa | 10⁶x₃ | P_S°/kPa | ln(f/pN) | Uncorrected, central / widest | Left after correction, signed | **Bound** | n_gas/n_liq | δ lowest fill / 200 kPa |
|---|---|---|---|---|---|---|---|---|---|---|
| 293.15 | 0.0394 | 91.6 | 484 | 2.24 | -0.00556 | 0.94 / 1.08 % | -0.124 to +0.504 % | **0.506 %** | 5.41 | 0.39 / 0.90 % |
| 293.15 | 0.0870 | 84.8 | 465 | 2.12 | -0.00516 | 0.87 / 1.00 % | -0.114 to +0.469 % | **0.471 %** | 5.77 | 0.38 / 0.98 % |
| 293.15 | 0.1456 | 93.1 | 513 | 1.96 | -0.00560 | 0.95 / 1.08 % | -0.119 to +0.511 % | **0.512 %** | 6.42 | 0.46 / 1.04 % |
| 293.15 | 0.2197 | 101.2 | 628 | 1.76 | -0.00603 | 1.02 / 1.16 % | -0.124 to +0.551 % | **0.552 %** | 6.46 | 0.50 / 1.01 % |
| 303.15 | 0.0394 | 96.3 | 405 | 4.07 | -0.00550 | 0.94 / 1.10 % | -0.142 to +0.536 % | **0.538 %** | 6.57 | 0.49 / 1.05 % |
| 303.15 | 0.0870 | 89.2 | 401 | 3.85 | -0.00510 | 0.87 / 1.02 % | -0.130 to +0.500 % | **0.501 %** | 6.80 | 0.47 / 1.11 % |
| 303.15 | 0.1456 | 97.4 | 458 | 3.56 | -0.00548 | 0.94 / 1.10 % | -0.133 to +0.538 % | **0.540 %** | 7.26 | 0.54 / 1.14 % |
| 303.15 | 0.2197 | 105.9 | 576 | 3.21 | -0.00587 | 1.01 / 1.17 % | -0.136 to +0.576 % | **0.578 %** | 7.11 | 0.57 / 1.08 % |
| 313.15 | 0.0394 | 100.7 | 348 | 7.08 | -0.00554 | 0.95 / 1.15 % | -0.167 to +0.577 % | **0.579 %** | 7.73 | 0.61 / 1.19 % |
| 313.15 | 0.0870 | 93.4 | 351 | 6.69 | -0.00515 | 0.88 / 1.07 % | -0.153 to +0.539 % | **0.541 %** | 7.86 | 0.58 / 1.24 % |
| 313.15 | 0.1456 | 101.0 | 443 | 6.20 | -0.00544 | 0.94 / 1.13 % | -0.154 to +0.571 % | **0.573 %** | 7.53 | 0.60 / 1.16 % |
| 313.15 | 0.2197 | 100.4 | 509 | 5.58 | -0.00533 | 0.92 / 1.11 % | -0.145 to +0.561 % | **0.563 %** | 7.38 | 0.59 / 1.15 % |
| 323.15 | 0.0394 | 105.0 | 300 | 11.85 | -0.00572 | 0.97 / 1.23 % | -0.205 to +0.633 % | **0.635 %** | 9.05 | 0.78 / 1.36 % |
| 323.15 | 0.0870 | 97.4 | 313 | 11.20 | -0.00532 | 0.90 / 1.15 % | -0.188 to +0.592 % | **0.594 %** | 8.90 | 0.72 / 1.38 % |
| 323.15 | 0.1456 | 105.1 | 405 | 10.38 | -0.00555 | 0.95 / 1.19 % | -0.185 to +0.620 % | **0.622 %** | 8.29 | 0.72 / 1.26 % |
| 323.15 | 0.2197 | 104.5 | 460 | 9.34 | -0.00540 | 0.94 / 1.16 % | -0.173 to +0.605 % | **0.607 %** | 8.22 | 0.72 / 1.25 % |

- **Correction:** multiply each Xu CO₂ Hx target by exp(ln(f/pN))
  (`correction_factor_on_H`, 0.9940–0.9949), as the released fit does for
  Hartono.
- **Bound composition:** the liquid term dominates the bound (0.35–0.42 %,
  positive), followed by the B11/B12 envelope. Xu's temperatures are low, so
  the water and third-virial terms are smaller than Hartono's.
- **B22 below 300 K:** the 293.15 K rows lie further below Harvey & Lemmon's
  300 K check range than Hartono's row 1. Widening B22 to ±10 % changes no bound
  by more than 6e-5 percentage points.
- **Check:** the replayed Hartono rows reproduce `../b1-vapor-bound/transfer.json`
  exactly. For row 1 the first-order form B11c₁ + 2B12c₂ gives −0.005569,
  against −0.00556 from the full solution.

**Peng–Robinson residual δ (outside B1, as for Hartono).** δ is computed with
`residual.py`'s formula, using the 2018 volumes, V_S = 120 g / Table 4 density
and the tank at an assumed 295.15 K. On that basis the source's x₃ is too high,
and its H too low, by:

- 0.38–0.78 % at the lowest possible fill (the tank ends at the reactor
  pressure);
- 0.90–1.38 % at a 200 kPa fill;
- 2.1–3.2 % at 400 kPa and 4.5–7.0 % at 800 kPa;
- 1 % at a fill of 159–216 kPa.

The values are larger than Hartono's at equal fill because more N₂O sits in the
gas.

Two points differ from Hartono:

- **Possible fill cap:** the 2013 transducers had a 200 kPa full scale. If the
  2018 tank kept that transducer, which is not stated, δ ≤ 1.38 %.
- **Volume calibration:** both papers calibrate V_reactor with N₂O through the
  same Peng–Robinson balance, and the error this puts into the volume partly
  cancels δ. Suppose the calibration used the same fill and charge on an empty
  reactor (an illustration only; its conditions are not printed). δ is then
  −0.01 to −0.14 % at the lowest fill, −0.05 to −0.23 % at 200 kPa and
  −0.34 to −1.12 % at 800 kPa.

δ is therefore neither sign-definite nor bounded from the printed information.
Like Hartono's δ, it is carried as a disclosed source limitation outside the B1
transfer. Applying the Hartono disposition (orchestrator, 2026-10-18) to Xu is
itself an orchestrator decision.

## Qualification conditions

| Condition (B1 record) | Xu evidence | Outcome |
|---|---|---|
| 1. P3 is a true N₂O partial pressure, total minus solvent pressure | Xu 2013 Eq. 4 p.1634 (sign as printed inverted); 2018 §2.3 p.2710 refers to it and injects after solvent VLE at the set temperature | Met by citation; the 2018 subtraction is inferred, not printed |
| 2. Solvent pressure | Measured (2013), not printed | Model P_S° ±10 %, plus a 0 ≤ p_s ≤ p_sat,water sweep (retained) |
| 3. Gas law in the mole balance | Peng–Robinson for the tank and the reactor gas (2018 Eqs. 2–5 p.2710; 2013 Eqs. 2–3 p.1634); the pure-N₂O z at P3 is the right first-order form on this basis | No ideal-gas law. The PR residual δ is unbounded (fill and calibration not printed); disclosed limitation |
| 4. B12 within × 0.5–2 of the CO₂–water analog | Unchanged estimate | Inside the envelope |
| 5. Not quantified | MEA vapor beyond the model's own solvent pressure (x₂ ≤ 0.2197); for a one-charge temperature series, how the solvent pressure was obtained at the later temperatures; evaporation during 2018's evacuation of the loaded absorbent | Disclosed |

## What would change in the neutral fit (not run)

**Status quo, the released Hartono-only pair.** The model is −7.1 to +23.2 %
from the B1-corrected Xu targets (mean |error| 10.5 %). Applying the correction
raises each Xu error by 0.52–0.67 percentage points over the uncorrected
comparison in `../neutral-fit/README.md`. Near 30 wt % at 313.15 K the model is
+10.0 % (w = 0.244) and +15.9 % (w = 0.366) from Xu, but within 0.5 % of
Hartono. The two campaigns disagree at nearly the same state by more than ten times
the B1 bound. B1 does not resolve that disagreement.

**Restoring the original A4-4 two-source objective** (design
`amendment-4-neutral-co2-mea.md` A4-4) would change the following:

- **Rows:** the eight Xu rows at x₂ = 0.0870 and 0.1456 (w = 0.244, 0.366)
  return, giving 15 rows and 14 states with equal source weight.
- **Targets:** each Xu target is multiplied by its correction factor
  (0.9944–0.9949 for those rows).
- **Basis choice:** the Xu Hx basis must be selected. One option is Table 8
  times density, the current derived column; the other is S3 direct P3/x₃,
  consistent with the Hartono SI choice. They differ by −0.56 to +0.25 %.
- **Data and pins:** `CO2_physical_from_N2O.csv` needs Xu primary targets and
  weights, which gives a new file hash. That file is pinned in
  `scripts/fit_neutral_co2_mea.py` and in the released fit inputs.
- **Falsifier:** each source must have mean |error| ≤ 10 % and maximum ≤ 20 %.
  At the released pair the eight rows are at 9.57 % mean and 22.0 % maximum
  (323.15 K, w = 0.366), so the per-source maximum already fails there. A
  two-source fit would trade Hartono error for Xu error. Whether any common pair
  passes is unknown without the fit.
- **Temperature trend:** Xu's errors rise with temperature (−7 % to +22 % at
  w = 0.366 from 293 to 323 K). A joint fit would pull b, which Hartono alone
  determines only weakly (conditioning standard error 64 K).

Recommendation (engineering judgment, reversible): keep the Hartono-only
calibration. Retain Xu as a B1-qualified comparison with its correction factors
and its 293–323 K, 12–49 wt % disagreement. If a cross-source test is wanted,
run A4-4 as designed and let its per-source falsifier decide.

## Files

`transfer.json` holds the per-row values, sources, input and producer hashes,
the δ cases, the Table 8/S3 differences and the released-pair errors.

Producer: `tmp/b1-2008/xu_eq5.py` (sha256 `67064ada…14b1d5`). It was adapted
from `eq5.py` and `residual.py` and imports `b1_vapor.py` (`34ab7e9a…df6697`).
It is ignored scratch, stdlib only and not versioned, because the campaign code
ceiling stands at 1,000 of 1,000 lines. The equations above define every
number.
