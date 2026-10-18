# B1: Hartono N₂O vapor nonideality bound (#170, amendment 4)

Researched 2026-10-16; computation reproduced independently by the
orchestrator (scratch script `/tmp/b1-virial/b1_vapor.py`, sha256
`34ab7e9a…df6697`, stdlib only, reproducible from the equations below).
Closed 2026-10-17 on the 2008 apparatus paper; see the last section.

## Result

**B1 passes after a vapor-side correction of the targets.** The first bound
below (0.943 %) treated the source pressure as y·P. Hartono, Juliussen &
Svendsen 2008 (J. Chem. Eng. Data 53, 2696–2700, doi:10.1021/je800409d; Zotero
`YV8V38QI`, PDF `D667FF2D`, sha256 `e5fa375d…b5b3e2`) defines it instead as
P_R − P_S° (Eq. 5). On that basis the N₂O–water cross coefficient enters at
full strength and the uncorrected transfer reaches 1.38 % (row 7, widest
envelope). The design permits a source-supported thermodynamic correction:
each target is multiplied by f_N₂O/pN. With signs kept, the transfer left
after it is at most **0.36–0.51 % for rows 1–6 and 0.83 % for row 7**, inside
the 1 % rule. Details are in the last section; the table below is the
superseded y·P bound, kept for the record.

| Row | T/K | pN₂O/kPa | \|φ−1\| central % | env A % | env B % | + liquid, central % | env A % | env B % |
|---|---|---|---|---|---|---|---|---|
| 1 | 298.35 | 61.64 | 0.3423 | 0.3798 | 0.4104 | 0.7603 | 0.7980 | 0.8287 |
| 2 | 312.65 | 87.87 | 0.4249 | 0.4765 | 0.5239 | 0.8433 | 0.8951 | 0.9427 |
| 3 | 312.65 | 71.71 | 0.3468 | 0.3922 | 0.4314 | 0.7648 | 0.8104 | 0.8498 |
| 4 | 322.25 | 62.61 | 0.2760 | 0.3217 | 0.3591 | 0.6937 | 0.7396 | 0.7771 |
| 5 | 331.75 | 71.29 | 0.2873 | 0.3418 | 0.3871 | 0.7051 | 0.7598 | 0.8053 |
| 6 | 341.25 | 48.52 | 0.1790 | 0.2182 | 0.2519 | 0.5963 | 0.6357 | 0.6695 |
| 7 | 360.25 | 60.76 | 0.1889 | 0.2424 | 0.2888 | 0.6062 | 0.6600 | 0.7066 |

"Central" is the worst case over solvent vapor pressure 0 ≤ p_s ≤ p_sat,water(T)
(201 points). Envelope A also varies B11 ± 10 %, B12 × 0.5–2 and B22 ± 5 %;
envelope B uses B11 ± 25 cm³/mol with the same B12 and B22 ranges. Combined
values are exp(|ln φ| + 0.00415711969) − 1.

## Equations and coefficients

With P = pN₂O + p_s, y1 = pN₂O/P, y2 = 1 − y1 (N₂O = 1, water = 2):
ln φ1 = (2(y1 B11 + y2 B12) − B_mix) P/(RT), B_mix = y1² B11 + 2 y1 y2 B12 + y2² B22,
R = 8.314462618 J mol⁻¹ K⁻¹.

| Coefficient | Basis | Locator | Check |
|---|---|---|---|
| B11, N₂O | Lemmon & Span 2006 EOS (J. Chem. Eng. Data 51, 785), zero-density limit B = (1/ρc) Σ over d=1 terms n τ^t; Tc 309.52 K, ρc 10270 mol/m³; terms (n, t): (0.88045, 0.25), (−2.4235, 1.25), (0.38237, 1.5), (0.13122, 2.375), (−0.23263, 3.5), (−0.00042859, 6.5) | coefficients via CoolProp `dev/fluids/NitrousOxide.json` (sha256 `85127436…6be`); primary paper not read | NIST WebBook (same equation) agrees within 0.07 cm³/mol, which checks the transcription only; Crusius et al. 2015 (J. Chem. Phys. 142, 244307) ab initio values are 1.7–2.8 cm³/mol more negative only under a swapped-exponent reading of its ambiguous printed Eq. 10, and its Fig. 5 experimental values lie about 2–12 cm³/mol above them; the Dymond et al. 2002 compilation was not read |
| B22, water | Harvey & Lemmon 2004 (J. Phys. Chem. Ref. Data 33, 369) Eq. 6, Table 4 | p.372 | reproduces Table 5 at 300–400 K; below 300 K (row 1) outside its recommended range, IAPWS-95 gives −1236.1 vs −1195.6 cm³/mol |
| B12, N₂O–water | **Estimate**: CO₂–water analog, Hellmann 2019 (Fluid Phase Equilib. 485, 251) Table 1 semiclassical values, interpolated in (1/T, ln\|B\|) | §4.1, Table 1 | no measured or evaluated N₂O–water value found |
| p_sat, water | IAPWS-IF97 Eq. 30, Table 34 | pp.34–35 | Table 35 check values asserted; 62.799 kPa at 360.25 K |

Values used, in cm³/mol, from row 1 to row 7:
- B11: −133.08, −120.27, −120.27, −112.56, −105.53, −99.04, −87.43;
- B22: −1195.6, −951.3, −951.3, −827.0, −726.8, −644.1, −517.0;
- B12: −180.8, −158.7, −158.7, −146.2, −135.1, −125.3, −108.4.

Truncation after the second virial coefficient changes ln φ by at most 6e-6 for pure N₂O, checked against the full Lemmon & Span equation.

## Model-side term

The fit compares the target with the model's partial-pressure Henry ratio at its dilute bubble point. Write H^p = H^f/φ^V, apply the analogy to the fugacity Henry constants, and assume the model's H^f is correct. The logarithmic bias is then:

ln target − ln model = V̄ΔP/RT − ln φ_N₂O(exp) + ln φ_CO₂,model(P_b) + (water-ratio term)

- **Liquid term V̄ΔP/RT.** It is non-negative, because P_exp > P_b and V̄ > 0.
- **Source N₂O vapor term −ln φ_N₂O(exp).** It is positive.
- **Model term ln φ_CO₂,model(P_b).** It is negative at every retained bubble state, from −3.8e-5 to −8.4e-4 (`dilute-bubble/pressure-properties.json`, `vapor_log_phi_CO2`). It can only reduce the bound and is not added.
- **The 101325 Pa frozen-vapor values** belong to a different diagnostic and stay excluded, as the final-prerequisites README already states.

This sign argument is the orchestrator's derivation. The Versteeg water-ratio term belongs to the unchanged analogy (Eq. N2O-4) and is outside B1.

## Conditions and open items

Superseded for conditions 1, 3 and 4 by the closure section below: on the Eq. 5 basis B12 enters at full strength, so condition 4's break-even no longer holds.

1. **The vapor is N₂O plus water only, and pN₂O is a true N₂O partial pressure.**
   - The 2008 paper must say whether pN₂O equals the total pressure minus the solvent vapor pressure, and where that vapor pressure comes from.
   - Supporting inference: Hartono's kH divided by Versteeg's water value varies smoothly, from 1.15 at 298 K to 0.89 at 360 K. Counting water vapor as N₂O would give a factor of about 5 at 360 K.
2. **The solvent vapor pressure is at most the pure-water saturation pressure.**
3. **x_N₂O carries no hidden ideal-gas error.** If it comes from a gas-phase mole balance using the ideal-gas law, that is a separate error of similar size (up to about 0.4 % for row 2). This bound does not cover it. The 2008 paper must say how x_N₂O was obtained.
4. **B12 is within × 0.5–2 of the CO₂–water analog.** To break even, B12 would have to be about 3.7 times more negative, in row 7.
5. **Not quantified:**
   - the third virial coefficients C112 and C122 (an assumed |C122| ≤ 3|C_ww| gives at most about 1.5e-3 in ln φ, row 7);
   - MEA vapor;
   - the nonzero-loading pair repeat. Loaded rows reach pN₂O 95.15 kPa, and CO₂ enters the vapor there.

## Closure on the 2008 apparatus paper (2026-10-17, corrected 2026-10-18)

Hartono 2014 §2.2 p.1809 refers its N₂O procedure to this paper (its ref. 18).
Read: Experimental Section and Eqs. 1–6 pp.2696–2697, Table 1 p.2697. An
independent review of the first version (Opus, 2026-10-18) found that it had
applied the y·P bound to the Eq. 5 quantity; this section is the correction.

| Condition | What the 2008 paper says | Outcome |
|---|---|---|
| 1. pN₂O is a true N₂O partial pressure | Eq. 5: P_N₂O = P_R − P_S°, the measured total reactor pressure minus the solvent vapor pressure, "directly measured at the desired temperature before adding N₂O" (p.2697). The solvent was first degassed by vacuum to about 2 kPa at ambient temperature (p.2696). | Not y·P. The transfer is recomputed for the Eq. 5 quantity and corrected below. |
| 2. Solvent vapor pressure ≤ pure-water saturation | P_S° is measured but not printed. | Estimated by the model's own dilute-bubble pressure P_b (±10 %); the 0 ≤ p_s ≤ p_sat sweep is also retained. |
| 3. No hidden gas-law error in x_N₂O | Eqs. 1–4: N₂O added from the gas-holding vessel's pressure drop with compressibility factors z₁, z₂; N₂O left in the reactor gas from P_N₂O(V_R − V_S)/(z RT_R); the sentence after Eq. 2 names Peng–Robinson for z (that z₁, z₂ also come from it is inferred; Xu & Wang 2018 §2.3 states it for the same kind of gas tank). | Not met as a bound: no ideal-gas law, but the Peng–Robinson residual δ below is unbounded because the fill pressure is not printed. |

**Vapor term on the Eq. 5 basis.** With the water fugacity fixed by the liquid
(including its Poynting change and N₂O dilution), the N₂O–water cross
coefficient cancels between P_R and P_S° to first order, so
P_R − P_S° = c₁RT(1 + B11c₁): Eq. 2's pure-N₂O compressibility is the right
form for the gas balance (misses ≤ 1.04e-5). The same identity gives the
fugacity: ln(f₁/pN) ≈ B11c₁ + 2B12c₂, with B12 at full strength. Solved
exactly at second-virial level per row (`transfer.json`; the release review
reproduced rows 2 and 7 independently):

| Row | T/K | P_S°/kPa | ln(f₁/pN) | Uncorrected, central / widest | Left after correction, signed | **Bound** |
|---|---|---|---|---|---|---|
| 1 | 298.35 | 2.81 | -0.00373 | 0.62 / 0.74 % | -0.093 to +0.355 % | **0.355 %** |
| 2 | 312.65 | 6.31 | -0.00487 | 0.83 / 1.01 % | -0.144 to +0.509 % | **0.511 %** |
| 3 | 312.65 | 6.31 | -0.00412 | 0.69 / 0.86 % | -0.128 to +0.431 % | **0.432 %** |
| 4 | 322.25 | 10.37 | -0.00381 | 0.62 / 0.82 % | -0.148 to +0.422 % | **0.422 %** |
| 5 | 331.75 | 16.42 | -0.00442 | 0.71 / 0.97 % | -0.199 to +0.513 % | **0.514 %** |
| 6 | 341.25 | 25.24 | -0.00405 | 0.59 / 0.90 % | -0.244 to +0.488 % | **0.489 %** |
| 7 | 360.25 | 55.16 | -0.00605 | 0.83 / 1.38 % | -0.510 to +0.829 % | **0.832 %** |

- **Correction:** each primary target is multiplied by exp(ln(f₁/pN)) at
  central coefficients (factors 0.9940–0.9963).
- **Solvent pressure:** P_S° is estimated by the model's CO₂-free solvent
  pressure, the dilute-bubble pressure minus its CO₂ partial pressure, within
  ±10 %. The first statement used the bubble pressure itself, which included
  0.97–2.2 kPa of CO₂; the effect on the factors was about 1.6e-4.
- **Signed range** of ln target − ln model left after the correction:
  - vapor deviation over B11 ±10 % and ±25 cm³/mol, B12 × 0.5–2, B22 ±5 %
    and P_S° ±10 % (B12 × 2 dominates at row 7), both signs;
  - liquid term 0 to 100 cm³/mol × (pN + 0.1 P_S°)/RT, positive (replaces the
    101325 Pa value);
  - the model's ln φ_CO₂ at its bubble state, a fixed negative value
    (`dilute-bubble/pressure-properties.json`);
  - third-virial allowance ±1.5e-3 at row 7, scaled by c₂².
- **Magnitude sum:** adding every term as a magnitude gives 0.37–0.57 % and
  1.002 % at row 7; the first corrected statement (1.023 %) did that, and the
  release review pointed out that the model term only reduces the bias.
- **Uncorrected:** rows 2 and 7 exceed 1 % in the widest envelope.

**Sensitivity of the neutral pair** (`transfer.json`, refits at the released
settings). Moving every target to either end of its signed range, or tilting
the ends with temperature, moves k(313.15 K) by at most 0.0010 and b by at most
4.4 K. The Table 11 basis, a source difference the design accepts as a
disclosed limitation, moves them by 0.0037 and −12.3 K. The conditioning
standard errors at the declared weights are 0.0136 and 64 K.

**Superseded decision.** Before the signed bound, an orchestrator decision
(2026-10-18, owner away) passed row 7's 1.023 % on this materiality
comparison. With signs kept no override is needed; the comparison remains
supporting evidence.

**Peng–Robinson residual δ in the source concentration.** Peng–Robinson's
implied second virial coefficient B = b − a/RT for N₂O (T_c 309.52 K,
p_c 7.245 MPa, ω 0.162) is 11.2–11.9 cm³/mol more negative than Lemmon &
Span. It overstates both N₂O amounts, the vessel-side one most, so the source's
x_N₂O is too high and its H too low by δ, which depends on the unprinted fill
pressure (vessel at an assumed 295.15 K; V_S = V_R/2 as printed "around half"):

| Row | T/K | n_gas/n_liquid | δ, lowest fill | δ, 400 kPa fill | δ, 800 kPa fill | Fill for δ = 1 % |
|---|---|---|---|---|---|---|
| 1 | 298.35 | 1.87 | 0.16 % | 0.98 % | 2.05 % | 409 kPa |
| 2 | 312.65 | 2.40 | 0.27 % | 1.11 % | 2.39 % | 364 kPa |
| 3 | 312.65 | 2.40 | 0.22 % | 1.14 % | 2.42 % | 355 kPa |
| 4 | 322.25 | 2.77 | 0.23 % | 1.29 % | 2.70 % | 319 kPa |
| 5 | 331.75 | 3.18 | 0.31 % | 1.41 % | 2.97 % | 295 kPa |
| 6 | 341.25 | 3.56 | 0.30 % | 1.60 % | 3.30 % | 260 kPa |
| 7 | 360.25 | 4.35 | 0.57 % | 1.85 % | 3.85 % | 230 kPa |

"Lowest fill" ends the transfer at the reactor pressure (slightly understated:
the vessel must end above it); 800 kPa is the full scale of the paper's larger
transducer. δ is a systematic error in the source's own concentration, so the
3 % duplicate agreement does not bound it. Its sign is opposite to the applied
correction (−0.37 to −0.60 %): at the lowest fill it offsets part of it (row 7
almost all), and at fills above about 300–400 kPa the net source bias raises
H. Refitting with every target raised by δ moves the neutral pair by +0.0005 /
−1.7 K (lowest fill), +0.0027 / −4.9 K (400 kPa) and +0.0056 / −9.9 K
(800 kPa) in k / b, comparable at most to the Table 11 limitation. δ is carried
as a disclosed, unbounded source limitation outside the pressure/gas-reference
transfer that B1 bounds. This reverses condition 3 as first written and is an
orchestrator decision (2026-10-18, owner away) for the owner to ratify.

**The paper's water check.** Its Table 1 N₂O-in-water constants against
Versteeg & van Swaaij 1988 Eq. 5 (the N₂O water correlation the analogy uses):
−1.8 to +5.5 % at 298–333 K, and −4.9, −7.2, −8.3 and −7.2 % at 342.7, 343.5,
353.3 and 353.4 K. Versteeg's own 353 K point lies about 3 % below its Eq. 5,
so against that point the 353.3 K value is about −4.8 %; the paper itself calls
the agreement very good. 360.25 K is beyond the check. δ has the same sign and
grows with temperature, so it may explain part of the deficit (not tested).
This is source bias to report with the falsifier result.

**Still not quantified:** MEA vapor, and the nonzero-loading pair repeat
(condition 5). Xu & Wang 2018's Table S3 (supporting information now in hand,
sha256 `b14f133e…16c85071`) gives P3 = 84.8–105.9 kPa for the MEA-only rows,
but its §2.3 p.2710 defines P3 only as the "equilibrium partial pressure of
N₂O" and defers the apparatus to Xu, Wang & Chen 2013 (doi:10.1021/je301371p,
not in Zotero); Xu stays comparison-only. *Update 2026-10-18:* Xu 2013 is now
read (Zotero `JFF3PK44`/`WJ8UVRHC`); the same B1 check for the 16 Xu rows is in
`../xu-source-qualification/README.md`.

Computation: `tmp/b1-2008/eq5.py`, `residual.py` and a copy of the B1 script
(`b1_vapor.py`), ignored scratch, stdlib; hashes in `transfer.json`. They are
not versioned because the campaign code ceiling stands at 999 of 1,000 lines;
the equations above define every number.
