# B1: Hartono N₂O vapor nonideality bound (#170, amendment 4)

Researched 2026-10-16; computation reproduced independently by the
orchestrator (scratch script `/tmp/b1-virial/b1_vapor.py`, sha256
`34ab7e9a…df6697`, stdlib only, reproducible from the equations below).

## Result

For the seven unloaded 30 wt % Hartono SI Table S2 rows, the N₂O vapor
fugacity term plus the 0.416577 % liquid Poynting bound stays **at most
0.943 %** (row 2, widest envelope), below the 1 % B1 limit. **B1 stays open**:
the bound holds only under conditions 1–3 below, which need the Hartono,
Juliussen & Svendsen 2008 apparatus paper (J. Chem. Eng. Data 53, 2696–2700,
doi:10.1021/je800409d; closed access, not yet in Zotero).

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
| B11, N₂O | Lemmon & Span 2006 EOS (J. Chem. Eng. Data 51, 785), zero-density limit B = (1/ρc) Σ over d=1 terms n τ^t; Tc 309.52 K, ρc 10270 mol/m³; terms (n, t): (0.88045, 0.25), (−2.4235, 1.25), (0.38237, 1.5), (0.13122, 2.375), (−0.23263, 3.5), (−0.00042859, 6.5) | coefficients via CoolProp `dev/fluids/NitrousOxide.json` (sha256 `85127436…6be`); primary paper not read | NIST WebBook isotherms agree within 0.07 cm³/mol; Crusius et al. 2015 (J. Chem. Phys. 142, 244307) ab initio values 1.7–2.8 cm³/mol more negative |
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
