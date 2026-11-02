# AMP carbamate law: sources other than Ciftja 2014

Source assessment for #234, 2026-11-02. It extends
[carbamate-law.md](carbamate-law.md) and uses its hydrolysis definition and
activity identity unchanged:

$$K_h(T)=\frac{a_{\rm AMP}a_{\rm HCO_3^-}}{a_{\rm AMPCOO^-}a_w},\qquad
K_h=\frac{1}{q}\frac{\gamma_{\rm AMP}\gamma_{\rm HCO_3^-}}{\gamma_{\rm AMPCOO^-}a_w}.$$

No fitting, Engine calculation or code was run. The numbers marked
*hand arithmetic* below evaluate the printed correlations or convert their
bases. They check transcriptions and put the sources side by side; they are not
new results.

## Result

Three published AMP carbamate laws with a temperature dependence exist besides
Ciftja 2014. Each was estimated inside its own activity-coefficient model, and
none comes from a measurement of the carbamate's temperature dependence:

1. **Xu et al. 1992 / Silkenbäumer et al. 1998.** Xu back-calculated the
   constant at 40, 50 and 100 °C from a Deshmukh–Mather fit to solubility
   (VLE) data. Silkenbäumer's van 't Hoff line (Table 5, reaction IV) reproduces
   those three values. Tong 2012 reuses that line as its K5,AMP.
2. **Mehdizadeh et al. 2013.** An extended UNIQUAC (e-UNIQUAC) model takes its
   temperature dependence from DFT with SM8T solvation calculations, anchored
   to the experimental MEA value. Its absolute value was fitted partly to the
   Ciftja 2011 speciation (p.180; Table 4, p.177); the slope stays computed.
3. **Hartono et al. 2020.** An eNRTL model fits its carbamate constant to VLE
   data only, 293–393 K. Hartono 2021 reuses it unchanged.

At 298.15 K, on one molality basis, these model constants and the apparent NMR
ratios span a factor of about 40 (0.0075 to 0.32 kg/mol; table below). Their
hydrolysis enthalpies at 298 K range from 17 to 36 kJ/mol. That spread is what
the activity identity predicts: each value absorbs its own model's γ ratio.
None can be moved into ePC-SAFT as a model-independent thermodynamic law.

**Recommendation: the block remains** for the design's fixed, verified
temperature law (`../design-draft-amp.md`, line 70: slope "fixed to a verified
source law"). No source independent of the Ciftja NMR rows measures how the
AMP carbamate equilibrium changes with temperature. The available slopes
disagree by a factor of two. Ciftja 2014 is still the only multi-temperature
measurement (25–45 °C).

If the owner chooses to proceed before Ciftja 2014 is read, the
best-supported **apparent constant with a stated activity treatment** is
Hartono 2020's K_C, converted to hydrolysis with Hartono's own K_HCO3−
(conversion below). Its basis is eNRTL, mole fraction, 293–393 K VLE. It was not
fitted to NMR, yet by eye it follows the Ciftja 2014 speciation at 298–318 K
(Fig. 7a, p.14). It would serve as an initial value, with its offset as the
fitted law coordinate. It has two costs:

- Hartono's parameter regression data include Kundu 2003 and Dash 2011 (Table 2, refs
  [31,32]). The Kundu hold-out recommended in
  [partial-pressure-campaigns.md](partial-pressure-campaigns.md) would then
  no longer be independent of the slope source.
- Its slope reflects eNRTL and its K_HCO3−, not a carbamate measurement.

The Xu/Silkenbäumer law avoids both Kundu and the NMR data but rests on older
VLE and a residual carbamate (see the table). Choosing either is an owner
decision. Neither is supported here as a verified law.

## Candidate sources

| Source and Zotero key | Reaction as written | K basis and activity treatment | T range | Data behind it; uncertainty | Independent of Ciftja NMR? | Verdict |
|---|---|---|---|---|---|---|
| Xu, Wang, Otto & Mather 1992, Chem. Eng. Process. 31, 7–12, DOI [10.1016/0255-2701(92)80002-K](https://doi.org/10.1016/0255-2701(92)80002-K); `TR8F3BZW` (new) | Eq. 7, p.8: RNHCOO− + H2O ⇌ RNH2 + HCO3−. Reports formation Kc = 1/K7 | Eq. 8: K = ∏(m_iγ_i)^ν, molality; extended Debye–Hückel γ (Eq. 11; Table 1 β, p.10). Water activity is set to its mole fraction (p.9). Kc in kg/mol (Table 2 note), so water is left out of Kc | Table 2, p.11: Kc = 0.034, 0.024, 0.0089 kg/mol at 40, 50, 100 °C | VLE only: Yang 1982 (unpublished Exxon report), Roberts & Mather 1988, Teng & Mather 1989/1990 (p.9). Carbamate is not an equilibrium equation in the solved model: four equilibria (Eqs. 3–6) and three balances (Eqs. 12–14) fix seven species (p.9), so carbamate closes the CO2 balance from measured loading and pressure. No uncertainty stated | Yes | Origin of the only literature AMP temperature law. Model-bound, residual-derived apparent constant |
| Silkenbäumer, Rumpf & Lichtenthaler 1998, Ind. Eng. Chem. Res. 37, 3133–3141, DOI [10.1021/ie970925w](https://doi.org/10.1021/ie970925w); `LCSF9UWQ` (new) | Table 5, p.3138, reaction IV: RNH2 + HCO3− ⇌ RNHCOO− + H2O, ln K = 2546.2/(T/K) − 11.555 | Eq. 1, p.3136: K_R = ∏a_i^ν. Footnote a marks only reactions III and V as molarity, so IV is molality. Silkenbäumer's own γ are Pitzer (Eq. 5), but the constant was not refitted | Not stated for IV. The model correlates 313–353 K data (p.3138) | "K_IV from Xu et al. (1992)" (p.3136). *Hand arithmetic:* the line gives 0.0326, 0.0253, 0.0088 kg/mol at 313.15, 323.15, 373.15 K against Xu's 0.034, 0.024, 0.0089 | No new data | Fit through Xu's values. Implied ΔH(formation) = −21.2 kJ/mol |
| Tong et al. 2012, IJGGC 6, 37–47, DOI [10.1016/j.ijggc.2011.11.005](https://doi.org/10.1016/j.ijggc.2011.11.005); `5FB2UHQZ` | Reaction VI, §3.1: RNHCOO− + H2O ⇌ RNH2 + HCO3−; Eq. 9 has **no water activity** | Molality with γ (Table 5 caption) | Table 5 says 298–313 K, which does not match Xu's 313–373 K | Table 5: a = −2546.2, d = 11.555, cited to Silkenbäumer | No new data | Same law reversed; its stated range is not supported by the origin |
| Mehdizadeh et al. 2013, IJGGC 18, 173–182, DOI [10.1016/j.ijggc.2013.06.002](https://doi.org/10.1016/j.ijggc.2013.06.002); `PUBW7JJT` (new) | Eq. 7, p.176: H2O + AMPCOO− ⇌ AMP + HCO3− (K5) | e-UNIQUAC; Gibbs minimization in mole fractions (Eq. 9, p.176). R1–R3 constants from Austgen 1989 (Table 2), i.e. a mole-fraction scale. The solute standard state for K5 is not stated in the text read | DFT/SM8T over 273–373 K (§2, p.173) | Table 2 row 5, p.176: ln K5 = 32.81533 − 3296.4017/T − 4.14489 ln T. The DFT reaction free energy is shifted +4.49 kcal/mol to match MEA experiment (§5.1, p.177). "The slope … is kept but the absolute value … is considered as a parameter" (p.178). Fig. 13 (p.180) shows the fitted curve on the DFT points. The absolute value was fitted partly to the Ciftja 2011 speciation (p.180; Table 4, p.177), compared at 25 °C in Fig. 14. *Hand arithmetic:* ln K5 = −1.857 at 298.15 K, matching Table 5's −1.1 kcal/mol; ΔH_h = +17.1 kJ/mol at 298 K | Slope: yes (computational). Offset: partly tied to Ciftja 2011 | Computed slope only; absolute level anchored to MEA. Not a measured law |
| Hartono et al. 2020, Fluid Phase Equilib. 511, 112485, DOI [10.1016/j.fluid.2020.112485](https://doi.org/10.1016/j.fluid.2020.112485); `IPHHHPBL` (new) | Eq. 13, p.10: AMP + H2O + CO2 ⇌ AMPCOO− + H3O+ (K_C) | eNRTL; "mole fraction basis" (Table 12a, p.10). An asymmetric reference state is footnoted for K_AMP only; inferred, not stated, for K_C | VLE 293–393 K (Table 2, p.3) | Table 12a reaction 5 (signs checked on the page image): A = −14.0057, B = 2623.735, C = −1.8581, D = 0. Fitted in the ternary parameter regression to its own and literature VLE (p.10), including Kundu [32] and Dash [31]. "The speciation data were not used in the fitting" (p.14); Fig. 7a nevertheless shows the model against Ciftja 2014 at 298, 308, 318 K. No parameter uncertainty given | Yes, but it uses the Kundu hold-out | Best available apparent law; model-bound |
| Hartono et al. 2021, Fluid Phase Equilib. 550, 113235, DOI [10.1016/j.fluid.2021.113235](https://doi.org/10.1016/j.fluid.2021.113235); `JJXAM5ET` (new) | Same K_AMPCO2− | Table 23 row 10 repeats the 2020 coefficients, cited to [10] = Hartono 2020; "used without refitting" (abstract) | — | — | — | Not a separate source |
| Sherman 2016 dissertation (UT Austin), Ch. 5; `B7FH9RP9`. Journal version DOI [10.1021/acs.iecr.6b03009](https://doi.org/10.1021/acs.iecr.6b03009) not read | Eq. 5.1, p.86: 2AMP + CO2 ⇌ AMPCOO− + AMPH+ | Aspen asymmetric eNRTL. AMPCOO− ΔG°f,aq = −4.574×10⁸ and ΔH°f,aq = −7.50×10⁸ J/kmol (p.94–95; Table 5.12, p.113; signs checked on the page image). Other carbamate parameters left at defaults (p.86) | 25–45 °C | Fitted to 183 Ciftja 2014 NMR points; ARD 12.9%. Ciftja 2011 excluded as "inconsistent" (p.86). Table 5.4 (p.96): at 40 °C, 4.8 m AMP, Kc must change by 35 to shift VLE by 5% ARD (MEA: 2.4). The Ch. 4 note (p.50) says a 2PE carbamate enthalpy could not be estimated from the AMP NMR "due to the narrow temperature range measured" | **No:** fitted to Ciftja 2014 | Circular for this repository. Its K_h also needs Aspen databank properties not listed in the thesis |
| Bosch, Versteeg & van Swaaij 1990, Chem. Eng. Sci. 45, 1167–1173, DOI [10.1016/0009-2509(90)87110-E](https://doi.org/10.1016/0009-2509(90)87110-E); `RTLVD8PP` (new) | Nomenclature, p.1173: K = [AMPCOO−]/([AMP][HCO3−]) | Concentration, no activity correction | 298 K only | Table 4, p.1169: 4.8×10⁻⁵ m³/mol (0.048 L/mol), estimated inaccuracy 20%. Fitted from absorption rates at very low loading. The authors say the constant should preferably come from equilibrium experiments (p.1169) | Yes | Single-temperature kinetic estimate; no temperature dependence |
| Chakraborty, Astarita & Bischoff 1986, Chem. Eng. Sci. 41, 997–1003, DOI [10.1016/0009-2509(86)87185-8](https://doi.org/10.1016/0009-2509(86)87185-8); `FIJKHPCK` (new); Ciftja 2011 ref. 1 | Eq. 1, p.999: Kc = [RNHCOO−]/([RNH2][HCO3−]) | Concentration, no activity correction | 42 °C only (p.998) | 13C NMR: no carbamate peak at 2.5 M AMP, loading 0.65; detection about 0.10 M from a model carbamate (Figs. 2–3). Hence Kc ≤ 0.1 L/mol (p.999) | Yes | Upper bound only |
| Sartori & Savage 1983, Ind. Eng. Chem. Fundam. 22, 239–249, DOI [10.1021/i100010a016](https://doi.org/10.1021/i100010a016); `WIQYC5RB` (new) | Eq. 4, p.240: Kc = [R2NCOO−]/([R2NH][HCO3−]) | Concentration, no activity correction | 40 °C only | Table IV, p.244: AMP Kc < 0.1 by 13C NMR (Melchior 1975, not available). The VLE model agrees with data "if AMP is assigned … Kc of 0.1" (p.245) | Yes | Upper bound only |
| Fernandes et al. 2012, J. Chem. Thermodyn. 54, 183–191, DOI [10.1016/j.jct.2012.03.030](https://doi.org/10.1016/j.jct.2012.03.030); `Q6XFPTKI` | Eq. 3, p.184: RNH2 + HCO3− ⇌ RNHCOO− + H2O (water omitted from K9) | Molarity, Debye–Hückel corrected to zero ionic strength (Eq. 12, p.186) | 288–318 K for amines that form carbamate | 1H NMR titrations at 0.04 M amine. **No AMP carbamate detected**; detection limit about 0.5% of the major peaks (§2.2, p.185); AMP absent from Table 1 | — | No AMP value. Useful as the method standard: thermodynamic K and ΔH (MEA: −18 kJ/mol formation, Table 1) need dilute titrations |
| Gupta & Svendsen 2020, IJGGC 98, 103061, DOI [10.1016/j.ijggc.2020.103061](https://doi.org/10.1016/j.ijggc.2020.103061); `6X54BH32` (new) | Reaction 5: carbamate formation | Computed absolute ΔG (DFT/composite with four solvation models) | 273–373 K | Table 8: AMP ΔG(298 K) = +7.10 (ESS), +8.53 (PCM), +7.12 (SM8T), +10.93 (DivCon) kcal/mol. The authors' own MEA values span −0.50 to +7.88. The authors call the constants qualitative (pp. 6, 8, 11). AMP temperature gradients appear only graphically (Fig. 9) | Yes | Not usable quantitatively |
| Kundu, Mandal & Bandyopadhyay 2003, J. Chem. Eng. Data 48, 789–796, DOI [10.1021/je0201626](https://doi.org/10.1021/je0201626); `BRW2JUBY` | Modeling, Eqs. 1–3 (p.790–791) and Table 4 (p.792). The liquid holds only AMP, H2O, AMPH+ and HCO3− (p.791) | — | — | — | — | No carbamate law |

## The same constants on one basis

Formation constant at 298.15 K on the repository basis
`aqueous-molality-infinite-dilution-water-v1` (m° = 1 mol/kg,
M_w = 0.01801528 kg/mol; `docs/coordination/greenfield-migration.md`).
*Hand arithmetic.* Mole-fraction model constants use the standard-scale offset
ln K_h,m = ln K_h,x + Δν_solute·ln(1/M_w), with Δν_solute = +1 for hydrolysis
(+4.0165). This assumes AMP is an infinitely dilute solute in that model,
which the sources do not state for K_C or K5. Apparent NMR ratios use the
finite-composition relation q_m = q_x·x_w·M_w with x_w ≈ 0.86–0.92 (Ciftja
2011 Table 2 composition).

| Source | γ treatment inside the number | Formation K at 298 K, kg/mol | Hydrolysis ΔH at 298 K, kJ/mol |
|---|---|---|---|
| Ciftja 2011, mole-fraction apparent 0.47 (Table 2, p.618) | none | ≈0.0075 | — |
| Ciftja 2014, log Kc = 0.56 as quoted by Sherman (p.62, basis labels inconsistent in the thesis) | none | ≈0.058 (secondary) | — |
| Ciftja 2014 Eq. 19 at I→0, primary (#238, [ciftja-2014.md](ciftja-2014.md)) | empirical ionic-strength extrapolation | ≈0.76 | +20.8, falling to +19.0 at 318 K |
| Bosch 1990 (molarity) | none | 0.048 L/mol | — |
| Chakraborty 1986 / Sartori 1983, 42 / 40 °C | none | ≤ 0.1 L/mol | — |
| Xu 1992 / Silkenbäumer 1998, extrapolated below 313 K | extended Debye–Hückel | 0.049 | +21.2 (constant) |
| Mehdizadeh 2013 | e-UNIQUAC | 0.115 | +17.1 |
| Hartono 2020, via its own K_HCO3− (ln K_h,x = −2.866) | eNRTL | 0.32 | +35.8, falling to +14.0 at 373 K |

The model constants span a factor of 6.5 and the measured ratios a factor of 8.
The enthalpies differ by a factor of two. A single law cannot satisfy every
source, and the identity in `carbamate-law.md` explains why: each model's γ
ratio differs.

## Can a source be converted without a circular fit?

**The algebra, yes:**

- **Xu/Silkenbäumer:** ln K_h,m = −2546.2/(T/K) + 11.555. This is already on
  the molality scale. Water activity is uncertain: Xu omits it from Kc but sets
  a_w = x_w elsewhere, while Silkenbäumer Eq. 1 includes a_w. A ±0.1 change in
  ln K at 30 mass% remains unresolved.
- **Hartono:** ln K_h,x = ln K_HCO3−(Table 12a, row 2) − ln K_C(row 5)
  = 245.4707 − 14715.835/T − 34.9235 ln T, then +4.0165 for molality.
  Hartono's own K_HCO3− must be used, not the repository's R2 law. Otherwise
  the subtraction transfers a different CO2 standard state into a
  CO2-independent reaction.
- **Mehdizadeh:** ln K_h,x from Table 2 row 5, then +4.0165, under the same
  solute assumption.

None of these needs a fit to NMR rows, and Xu/Silkenbäumer and Hartono use no
NMR at all.

**The thermodynamics, no:** each constant is a parameter of its source's γ
model. Inserting it into ePC-SAFT with different γ changes the predicted
speciation by the γ-ratio factor in the identity. The size of that factor is
unknown until ePC-SAFT AMPCOO− parameters exist. VLE determines the AMP
carbamate only weakly (Sherman Table 5.4), so a VLE-fitted K_C mostly reflects
the eNRTL parameterization rather than carbamate evidence.

## Findings that affect the design

- **The two Ciftja datasets disagree.** For 30 mass% AMP at 25 °C, Ciftja 2011
  Table 2 gives x(AMPCOO−) ≈ 1.6–4.8×10⁻⁴. Ciftja 2014, as plotted by Hartono
  2020 Fig. 7a and Sherman Fig. 5.3, shows about 2–3×10⁻³ at 25–45 °C.
  Sherman excluded 2011 as inconsistent (p.86). The design's plan to use
  Ciftja 2011 "as earlier speciation evidence" (`../design-draft-amp.md`,
  line 84) needs this conflict resolved, not only overlap checked.
- **Hold-out independence.** Hartono 2020 fitted its parameters to data including Kundu 2003 and Dash 2011.
  Any Hartono-derived law makes those campaigns calibration-dependent.
- **Ciftja 2011's stated constant.** The repository's carbamate note records
  Ciftja's own mole-fraction value 0.47 (§5.2, p.618). Its definition
  (Eq. 7, p.616) omits water and activity coefficients, as already recorded.

## Ciftja 2011 leads, resolved

| Ref. | Lead | Outcome |
|---|---|---|
| 1 | Chakraborty 1986 | Read: upper bound ≤ 0.1 L/mol at 42 °C; no temperature dependence |
| 7 | Jakobsen 2005, Ind. Eng. Chem. Res. 44, 9894–9903 | Local shelf copy `Jakobsen2005--SIZRW28I.md` read: MEA, BEA and MDEA only; no AMP. Ciftja cites it for method and activity models (p.616) |
| 10 | Wang 2001, MSc thesis, University of Canterbury | Not found online; unreadable |
| 13 | Deshmukh & Mather 1981 | A generic model. Its AMP application with a carbamate constant is Xu 1992 (read) |

## Unread or unreadable

- Ciftja 2014 full text (`HBBD5J2B`), which the owner is obtaining. Its values
  quoted here are secondary (Sherman, Hartono). *Read in #238 from
  `PUUFV6NX`/`FBQ5R6DR`; see [ciftja-2014.md](ciftja-2014.md).*
- Wang 2001 thesis; Melchior 1975 NMR (source of Sartori's Table IV); Yang 1982
  Exxon report (Xu's data).
- Sherman et al. 2016 Ind. Eng. Chem. Res. paper (the thesis was read
  instead). Aspen databank formation properties needed to turn Sherman's
  ΔG°f/ΔH°f into K_h.
- Supporting information for Hartono 2020 and Gupta 2020 (Gupta's AMP
  gradients are only plotted).
- Park et al. 2002, McCann et al. 2009 and Perinu et al. 2014 were cited by
  the sources above (a model estimate, an AMP non-detection, and linear
  alkanolamines respectively) but not read. Dash 2011's eNRTL model was not
  read.
- Standard state of AMP in Hartono's K_C and Mehdizadeh's K5. The +4.0165
  offset above assumes an infinitely dilute solute.

The private CESAR-1 repository was used only as an index of published
sources. It pointed to no AMP carbamate law beyond Ciftja; nothing from it is
recorded here.

## Zotero

New items in collection `8RZP275E`, each with a PDF: Silkenbäumer 1998
`LCSF9UWQ`, Xu 1992 `TR8F3BZW`, Ciftja 2011 `N3M32YAK`, Mehdizadeh 2013
`PUBW7JJT`, Hartono 2020 `IPHHHPBL`, Hartono 2021 `JJXAM5ET`, Chakraborty
1986 `FIJKHPCK`, Sartori & Savage 1983 `WIQYC5RB`, Bosch 1990 `RTLVD8PP`,
Gupta & Svendsen 2020 `6X54BH32`. PDF keys and SHA-256 hashes of every PDF read
for this note are appended to `pdf-identities.json`.
