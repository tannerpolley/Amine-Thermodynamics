# B1: Hartono N₂O vapor nonideality bound (#170, amendment 4)

Researched 2026-10-16; computation reproduced independently by the
orchestrator (scratch script `/tmp/b1-virial/b1_vapor.py`, sha256
`34ab7e9a…df6697`, stdlib only, reproducible from the equations below).
Closed 2026-10-17 on the 2008 apparatus paper; see the last section.

## Result

**B1 passes on materiality, after a vapor-side correction of the targets
(orchestrator decision 2026-10-18, owner away; reversible).** The first bound
below (0.943 %) treated the source pressure as y·P. Hartono, Juliussen &
Svendsen 2008 (J. Chem. Eng. Data 53, 2696–2700, doi:10.1021/je800409d; Zotero
`YV8V38QI`, PDF `D667FF2D`, sha256 `e5fa375d…b5b3e2`) defines it instead as
P_R − P_S° (Eq. 5). On that basis the N₂O–water cross coefficient enters at
full strength and the uncorrected transfer reaches 1.42 % (row 7, widest
envelope). The design permits a source-supported thermodynamic correction:
each target is multiplied by f_N₂O/pN, and the transfer uncertainty left after
it is 0.39–0.60 % for rows 1–6 and **1.023 %** for row 7. That residual moves
the neutral pair less than the Table 11 source difference the design already
accepts. Details are in the last section; the table below is the superseded
y·P bound, kept for the record.

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
exactly at second-virial level per row (`transfer.json`):

| Row | T/K | P_b/kPa | ln(f₁/pN) | Uncorrected, central / widest | Left after correction: vapor | liquid | model | third virial | **bound** |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 298.35 | 3.79 | −0.00388 | 0.64 / 0.77 % | 0.130 % | 0.250 % | 0.008 % | 0.001 % | **0.389 %** |
| 2 | 312.65 | 7.57 | −0.00503 | 0.85 / 1.05 % | 0.198 % | 0.341 % | 0.013 % | 0.003 % | **0.557 %** |
| 3 | 312.65 | 7.57 | −0.00428 | 0.71 / 0.89 % | 0.182 % | 0.279 % | 0.013 % | 0.003 % | **0.479 %** |
| 4 | 322.25 | 11.84 | −0.00398 | 0.64 / 0.86 % | 0.216 % | 0.238 % | 0.019 % | 0.008 % | **0.483 %** |
| 5 | 331.75 | 18.08 | −0.00459 | 0.73 / 1.01 % | 0.282 % | 0.265 % | 0.029 % | 0.017 % | **0.594 %** |
| 6 | 341.25 | 27.10 | −0.00422 | 0.60 / 0.94 % | 0.335 % | 0.181 % | 0.042 % | 0.037 % | **0.597 %** |
| 7 | 360.25 | 57.40 | −0.00623 | 0.85 / 1.42 % | 0.562 % | 0.222 % | 0.084 % | 0.150 % | **1.023 %** |

- **Correction:** each primary target is multiplied by exp(ln(f₁/pN)) at
  central coefficients and p_s = P_b (factors 0.9938–0.9961).
- **Vapor residual:** largest change over B11 ±10 % and ±25 cm³/mol,
  B12 × 0.5–2, B22 ±5 % and p_s ±10 %. B12 × 2 dominates at row 7.
- **Liquid term:** 0 to 100 cm³/mol × (pN + 0.1 P_b)/RT, the experiment's
  pressure above the model's bubble pressure (replaces the 101325 Pa value).
- **Model term:** −ln φ_CO₂ of the model at its bubble state
  (`dilute-bubble/pressure-properties.json`).
- **Third virial:** the 1.5e-3 allowance above at row 7, scaled by c₂².
- **Uncorrected:** rows 2, 5 and 7 exceed 1 % in the widest envelope, and row 7
  is 0.85 % centrally, as the review reported.

**Materiality (the basis of the decision).** Refitting the neutral pair with
every corrected target moved by ± its full bound (`transfer.json`
sensitivity; all plus, all minus, and the two temperature tilts) moves k(313 K)
by at most 0.0011 and b by at most 6.8 K. Replacing the SI basis by the Table
11 basis, a source difference the design accepts as a disclosed limitation,
moves them by 0.0037 and −12.3 K. The conditioning standard errors at the
declared weights are 0.0136 and 64 K. Row 7's 0.023-point excess is therefore
smaller in effect than an accepted limitation; the decision is reversible
before any adoption.

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
3 % duplicate agreement does not bound it. It is carried as a disclosed,
unbounded source limitation, like the Table 11 difference, outside the
pressure/gas-reference transfer that B1 bounds (orchestrator decision,
2026-10-18).

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
sha256 `b14f133e…5c85071`) gives P3 = 84.8–105.9 kPa for the MEA-only rows,
but its §2.3 p.2710 defines P3 only as the "equilibrium partial pressure of
N₂O" and defers the apparatus to Xu, Wang & Chen 2013 (doi:10.1021/je301371p,
not in Zotero); Xu stays comparison-only.

Computation: `tmp/b1-2008/eq5.py` and `tmp/b1-2008/residual.py` (scratch,
stdlib; hashes in `transfer.json`; both import the B1 script above).
