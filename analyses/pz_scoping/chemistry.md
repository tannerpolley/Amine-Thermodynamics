# Piperazine chemistry to declare before PZ fitting

Research snapshot for [#237](https://github.com/tannerpolley/Amine-Thermodynamics/issues/237), 2026-11-02. It extends the PZ outline in [#227's chemistry](../amp_pz_scoping/chemistry.md#pz) and settles the protonation mapping that record left open. Every constant below is a published source value read from the PDF named in [sources](sources/README.md). None is adopted into an Engine declaration, and none was refitted.

## Species

The six shared species (H2O, CO2, H3O+, OH−, HCO3−, CO3²−) and reactions R1–R3 stay frozen as declared in [#227](../amp_pz_scoping/chemistry.md#shared-species-and-reactions). PZ adds six liquid species:

| Species | Charge | Source naming | Detected by |
|---|---:|---|---|
| PZ | 0 | PIPH2 (Ermatchkov 2003); Pz (Hetzer 1968) | NMR peak 2, lumped with PZH+ and PZH2²+ |
| PZH+ | +1 | PIPH3+ | lumped, peak 2 |
| PZH2²+ | +2 | PIPH4²+; PzH2²+ | lumped, peak 2 |
| PZCOO− | −1 | PIPHCOO− | NMR peaks 1+4, lumped with HPZCOO |
| HPZCOO (H+PZCOO−, zwitterion) | 0 | PIPH2+COO− | lumped, peaks 1+4 |
| PZ(COO)2²− | −2 | PIP(COO−)2 | NMR peak 3, alone |

The peak assignments come from Ermatchkov 2003 §2, Eqs.2–5, p.1281. ¹H-NMR cannot separate protonation states: Ermatchkov checked this with DCl/D2O solutions (§2, p.1279), which gave only one extra peak. Six shared plus six PZ species gives **twelve liquid species**. Proposed vapor support: H2O, CO2, PZ.

## Independent reactions in this repository's hydrolysis form

All five are charge- and element-balanced (hydronium convention, matching R1–R3):

| Our id | Reaction | Source reaction and direction | Source law at 298.15 K |
|---|---|---|---|
| P1 | PZH+ + H2O ⇌ PZ + H3O+ | Hamborg 2009 "second dissociation" (Table 10, Table 16 second block); Hetzer 1968 K2 | ln K = −22.37 (Hamborg Table 10); pK2 = 9.731 (Hetzer Table III) |
| P2 | PZH2²+ + H2O ⇌ PZH+ + H3O+ | Hamborg 2009 "first dissociation" (Table 9, Table 16 first block); Hetzer 1968 K1 | ln K = −12.45 (Hamborg Table 9); pK1 = 5.333 (Hetzer Table III) |
| P3 | PZCOO− + H2O ⇌ PZ + HCO3− | Reverse of Ermatchkov 2003 reaction VI, PIPH2 + HCO3− ⇌ PIPHCOO− + H2O | lg K_VI = 1.52 ± 0.08, so lg K_P3 = −1.52 |
| P4 | HPZCOO + H2O ⇌ PZCOO− + H3O+ | Reverse of Ermatchkov reaction VIII, PIPHCOO− + H+ ⇌ PIPH2+COO− | lg K_VIII = 9.44, so lg K_P4 = −9.44 |
| P5 | PZ(COO)2²− + H2O ⇌ PZCOO− + HCO3− | Reverse of Ermatchkov reaction VII, PIPHCOO− + HCO3− ⇌ PIP(COO−)2 + H2O | lg K_VII = 0.34 ± 0.18, so lg K_P5 = −0.34 |

Do not also impose a CO2-to-carbamate reaction: it follows from R2 and P3. A reversed reaction takes the reciprocal constant (lg K negated). Hamborg Eq.11 (p.1319) writes the dissociation constant with a(H2O) in the denominator and hydronium as product, the same form as P1/P2. Ermatchkov writes H+ (Eq.8, p.1286). Treat those as numerically equal only under the convention μ°(H3O+) = μ°(H+) + μ°(H2O) with the same molality-scale activity coefficient. The repository's R1–R3 mapping record must state that this is its convention before any value is used.

### Group-to-reaction mapping, now settled

The label "first" means opposite things in Hamborg 2009. Its theory section uses Eq.11 for the "first dissociation constant of a diamine", with K1 = a(NH2–R–NH2)·a(H3O+)/[a(NH2–R–NH3+)·a(H2O)] (p.1319, Eqs.6–11). That is the PZH+ step. Eqs.12–17 then describe the "second" constant with the diprotonated species. The tables use the reverse labels:

- Table 9 "first dissociation constant" has ln K1 = −12.45 at 298.15 K, ΔrG° = 30.87 kJ/mol. Its Hetzer column reads −12.28, which equals −ln(10)·5.333. Hetzer's abstract defines K1 as PzH2²+ + H2O = H3O+ + PzH+ (p.2081).
- Table 10 "second dissociation constant" has ln K2 = −22.37, ΔrG° = 55.45 kJ/mol. Its Hetzer column reads −22.41 = −ln(10)·9.731. Hetzer defines K2 as PzH+ + H2O = H3O+ + Pz.
- Table 11 (p.1322) lists "PZ, second group" with pKa 9.71 and "PZ, first group" with pKa 5.41.

Map by the numerical anchor, not by the label: **Table 9 / first block of Table 16 → P2; Table 10 / second block of Table 16 → P1.** The weaker acid step (pKa ≈ 9.7) is P1. Any declaration that keys on Hamborg's words "first" or "second" without this anchor would swap the two constants by about 4.4 decades.

## Constant sources, bases and ranges

| Reaction | Source and locator | Form | Basis | T range (measured) | Uncertainty |
|---|---|---|---|---|---|
| P1, P2 | Hamborg & Versteeg 2009, DOI 10.1021/je800897v; Tables 9–10 p.1321 (correlated values 273–323 K, < 293 K extrapolated); Table 16 continued p.1326, 24 runs each | ln K = A/T + B + C ln T, Eq.21 p.1319; **A, B, C not printed** | molality, infinite dilution, Pitzer Debye–Hückel term only (Appendix A), explicit a(H2O), 1 bar | 293–353 K | ±0.04 in ln K per run (Table 16) |
| P1, P2 | Hetzer, Robinson & Bates 1968, DOI 10.1021/j100852a034; abstract, Table III p.2084, Table V p.2085 | −log K1 = 952.11/T + 4.3919 − 0.007555 T; −log K2 = 1656.59/T + 6.1316 − 0.006556 T | molality, zero ionic strength by extrapolation, Eq.1 p.2083 has no water activity, H2–AgCl cells without liquid junction | 273.15–323.15 K (0–50 °C, 11 temperatures) | fit SD 0.001–0.002 in pK1 (p.2084); pK2 SD 0.0031 |
| P3, P4, P5 | Ermatchkov, Pérez-Salado Kamps & Maurer 2003, DOI 10.1016/S0021-9614(03)00076-4; Table 5 p.1287, Eq.10 p.1286 | lg K = A + B/(T/K); VI: A = −3.750, B = 1570.4; VII: A = −1.587, B = 574.2; VIII: A = 4.354, B = 1517.0 | molality, Pitzer with Debye–Hückel term only (all interaction parameters zero), temperature-independent ΔrH; **fitted to the same 121 NMR rows** in D2O | 283–333 K | per-temperature SD in lg K_VI 0.08–0.16 and lg K_VII 0.16–0.26 (p.1286); none given for VIII |

Checks done by hand against the printed text (no code retained): Hetzer's two correlations reproduce pK1 = 5.333 and pK2 = 9.733 at 298.15 K, against tabulated 5.333 and 9.731. Ermatchkov's Table 5 gives lg K_VI = 1.517 and lg K_VII = 0.339 at 298.15 K, against the stated 1.52 and 0.34 (p.1286). Its ΔrH from Eq.12 is −2.3026·R·B: −30.07, −10.99 and −29.04 kJ/mol for VI, VII and VIII, matching p.1288. The text extraction dropped the minus signs; the signs follow from Eq.10–12 with the Table 5 coefficients.

Limits that block numerical adoption:

- **Hamborg Eq.21 coefficients are not printed.** The tables give rounded correlated values and 24 run values per step, as for AMP in [#229](../amp_pz_scoping/sources/hamborg-table-16.md). A P1/P2 law needs either a transcription and fit of Table 16 with uncertainty, or Hetzer's printed laws. Hetzer covers only 0–50 °C, below the 40–120 °C absorber range. Hamborg Table 9 differs from Hetzer by 1.48 % in ln K1; Table 10 differs by 0.18 % in ln K2 (p.1322). P2 is the less certain step, because its cells contain mixed 1:1 and 1:2 salts.
- **Ermatchkov's carbamate laws are fitted to the NMR rows they would describe.** Fitting procedure: §3, p.1286. Those rows cannot then test the same laws. The laws assume Debye–Hückel-only activities: an ePC-SAFT activity model will not reproduce the same speciation from them unchanged. They cover only 283–333 K. Ermatchkov 2006 (§ "Required thermodynamic properties", p.1791) applies them to 393 K, which is an extrapolation.
- **Solvent isotope.** Ermatchkov measured in D2O (§2, p.1278) and treated the constants as H2O constants. No isotope correction appears in the sections read (§§2–4). The size of that bias is unknown here.
- Bishnoi & Rochelle 2000 (DOI 10.1016/S0009-2509(00)00182-2, Table 2 p.5536) regressed carbamate constants to 17 pressure points (0.6 M PZ) and two NMR points. Ermatchkov 2003 (§4, p.1288, Fig.4) shows they differ "considerably". They are mole-fraction-basis apparent constants: use them as a lead, not a law.
- Hilliard 2008 (thesis DNQUPRMT, §14.3, PDF pp.561–567) regressed carbamate standard-state Gibbs energies and enthalpies simultaneously to pressure, volatility, Cp, NMR and heat data (Table 14.4-2, p.527). He dropped PZH2²+ from his final model (p.506), and he represented the zwitterion as a cation of charge 10⁻⁵ (p.510). These are eNRTL fit outputs, not independent constants.

## Conversion to this repository's reaction-reference convention

All three sources use the molality scale with a 1 mol/kg standard state for solutes and pure liquid water as the solvent reference. Ermatchkov 2006 states this explicitly (p.1790). At infinite dilution, m_i/m° = x_i/(M_w·m°·x_w). For a reaction whose solute stoichiometric sum is Δν, the mole-fraction constant is ln K_x = ln K_m + Δν·ln(M_w·m°). All five PZ reactions have Δν = +1, so ln K_x = ln K_m + ln(0.0180153) = ln K_m − 4.0165. Water's explicit activity factor is unchanged. Recheck this per reaction in the declaration; it is not a blanket offset. Verify one source reference value per reaction and the reciprocal for every reversed direction.

## Species that need a modeling decision

- **Zwitterion HPZCOO.** It is net neutral but carries a full ammonium and a carboxylate charge. In ePC-SAFT it has no Debye–Hückel or Born contribution. The driver's charge check (`src/MEA/solvent_specification.py:111`) accepts charge 0, so no 10⁻⁵ trick is needed. Whether it is volatile is a separate decision; recommend liquid-only.
- **PZH2²+.** Hilliard dropped it below a loading of 0.5 mol CO2/(2 mol PZ) (p.506). Keep it in the chemistry: it adds no fitted constant (P2 comes from a source), and dropping it is a reduction to test, not to assume.
- **Charged-species representation.** PZH+, PZH2²+, PZCOO− and PZ(COO)2²− need the A/B choice from the AMP draft (single sphere versus molecular chain). PZ(COO)2²− and PZH2²+ are the first −2 and +2 amine-derived ions in this repository. No published ePC-SAFT parameters for any PZ ion were found.
