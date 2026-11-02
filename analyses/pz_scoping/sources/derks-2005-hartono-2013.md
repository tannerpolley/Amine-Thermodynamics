# Derks 2005 and Hartono 2013

Checked 2026-11-02 for [#240](https://github.com/tannerpolley/Amine-Thermodynamics/issues/240). No measurement table is copied here; values quoted are single locators, ranges or hand checks. Arithmetic marked "hand check" was done in scratch files outside the repository and is not retained code. PDF hashes are in [pdf-identities.json](pdf-identities.json).

What was read:

- Derks, Dijkstra, Hogendoorn & Versteeg 2005, AIChE J. 51, 2311, DOI 10.1002/aic.10442. Zotero parent `7BYDJFRT`, PDF `MTKZ5MEF`, 17 pages: introduction, experimental section, chemical-equilibrium section and Table 1 (pp.2311–2314), model parameters (Tables 4–7, pp.2316–2318), Tables 8–9 (p.2318), experimental and modelling results with Tables 10–12 (pp.2319–2322), conclusions (p.2322). Tables 8 and 9 were checked against the rendered page image. Figures 4–12 were not digitized. The nomenclature, literature-cited pages and appendix were not read.
- Hartono, Saeed, Ciftja & Svendsen 2013, Chem. Eng. Sci. 91, 151, DOI 10.1016/j.ces.2013.01.015. Zotero parent `5KUR8PRH`, PDF `SEPZQIPE`, all 11 pages. Table 6 was checked against the rendered page image. The Supplementary Material (Figs. S1–S7) was not obtained.
- Kim, Svendsen & Børresen 2008, J. Chem. Eng. Data 53, 2521, DOI 10.1021/je800290k (Zotero `97LARJKT`, PDF `4SMCK4SC`, already in the library). This is the ebulliometer method Hartono cites for the procedure (§2.2, p.152). Read only its apparatus and uncertainty paragraphs (pp.2526 and 2528).
- Fosbøl, Neerup, Arshad, Tecle & Thomsen 2011, J. Chem. Eng. Data 56, 5088, DOI 10.1021/je200959m. Hartono fitted its freezing points. Acquired for this issue (Zotero `BXZRGU3H`, PDF `VVP244A8`). Read: abstract, introduction and the titles of Tables 1–3 (pp.5090–5092) only.

## Derks 2005: CO2 in dilute aqueous PZ

**Property.** CO2 partial pressure P_CO2 (kPa) over loaded aqueous PZ, against loading in mol CO2 per mol PZ, i.e. per molecule (Tables 8–9, p.2318). No total pressure and no speciation is reported.

**Methods (pp.2312–2313).** University of Twente. Two setups, with the split at a CO2 partial pressure of 25 kPa:

- *Below 25 kPa, "continuous" setup (Fig. 1).* About 1.6 L of liquid in a stirred reactor is batch with respect to the liquid. N2 and CO2 flow continuously, set by mass-flow controllers and presaturated. Equilibrium is reached when the inlet and outlet gas compositions agree. The outlet CO2 is measured by an IR analyser. A liquid sample is then titrated for PZ (0.1 N HCl) and analysed for total CO2 by desorption and titration.
- *Above 25 kPa, "batch" setup (Fig. 2).* About 2 L of degassed solution is used. Pure CO2 is fed from a calibrated gas vessel. P_CO2 is the final reactor pressure minus the vapor pressure of the unloaded solution, measured beforehand. This assumes the solution vapor pressure does not change with loading (p.2313). Loading comes from the pressure drop in the gas vessel; in some runs it was also analysed as in the continuous setup. PZ was titrated afterwards.

The tables do not say which setup produced each row. Hand check: 17 of the 58 rows are at or above 25 kPa, so these are presumably from the batch setup, an inference from the 25 kPa split.

**Basis.** Nominal molar concentrations, "0.2 and 0.6 molar" (abstract), "200 and 600 mol m⁻³" (p.2313) and "0.6 kmol m⁻³" (p.2319). The tables print only the nominal value; the titrated PZ concentration of each experiment is not printed. No solution density is given. Hand check: at an assumed density of 1.00 kg/L, 0.2 M ≈ 0.2035 mol/kg and 0.6 M ≈ 0.633 mol/kg water. This matches the 0.2–0.63 m that Ermatchkov 2006 Table 5 lists for this source. A 0.5 % change in density changes these molalities by about 0.5 %.

**Conditions and rows.** Temperatures 25, 40 and 70 °C (298, 313, 343 K; Table 12). Table 8 (0.6 M) has 12 rows at each temperature, 36 in total. Table 9 (0.2 M) has 9, 6 and 7 rows, 22 in total. That gives **58 rows**, the count #237 indexed. Hand check:

- P_CO2 spans 0.27–111.37 kPa; loading spans 0.36–1.23 mol CO2/mol PZ.
- 31 rows are at or below 0.9 mol/mol PZ. 12 rows are above 1.0 mol/mol PZ, where CO2 beyond the amine capacity is carried by bicarbonate and physical solution.
- In three places a lower printed loading carries a higher pressure than its neighbour: 0.6 M at 40 °C (0.99 → 26.52 kPa, 0.98 → 39.61 kPa); 0.6 M at 70 °C (0.71 → 4.53 kPa, 0.68 → 5.34 kPa); 0.2 M at 25 °C (0.99 → 5.38 kPa, 0.98 → 8.50 kPa). These are inside the stated 4 % loading uncertainty, near loading 1 where log P rises steeply with loading.

**Uncertainty (p.2319).** "Estimated (based on propagation of error) at 4 % in loading and 5 % in CO2 partial pressure". Temperature uncertainty is not stated. Near 1 mol/mol PZ a 4 % loading error moves P_CO2 by more than a factor of two. Hand check: 0.6 M at 25 °C goes from 10.92 kPa at 0.98 to 26.87 kPa at 1.02.

**Other data in the paper.** None new:

- No physical-solubility or N2O measurement.
- The pH and conductivity comparisons (Figs. 11–12) use Kaganoi's 0.6 M data read from Bishnoi & Rochelle's graphs (p.2321).
- The PZ–water binary was fitted to Dortmund-UNIFAC pseudo-data, because "there are no (useful) binary (VLE) data for systems with PZ" (p.2317). The model therefore uses no PZ-volatility measurement.

The companion paper Derks, Kleingeld, van Aken, Hogendoorn & Versteeg 2006, CES 61, 6837 (kinetics; cited by Hartono 2013) was not checked for N2O data.

**How the authors used the rows (pp.2321–2322; Table 12).**

- Aroua & Mohd Salleh (Derks ref. 4) was excluded as inconsistent with Bishnoi 2000 and this work (p.2319).
- The rest was screened. Rows deviating from a preliminary model by more than a factor of two were dropped, "some data measured in the loading range around 1". That left 153 of 170 rows.
- Of this work's rows, 21 of 22 (0.2 M) and 30 of 36 (0.6 M) were kept. The 7 dropped rows are not identified.
- Their electrolyte-EoS fit (seven ionic parameters) gives 16.4 % and 19.9 % average absolute deviation on the kept rows. Yi 2024 fitted all 58 rows at 27.9 % (Table 3).
- Their consistency checks: Fig. 4 shows agreement with Bishnoi & Rochelle 2000 at 0.6 M, 313 and 343 K. Table 10 (p.2321) checks against Kamps 2003 at 313 K: P_CO2 rises with PZ concentration at fixed loading.

**Equilibrium constants (Table 1, p.2314), a side check.**

- K III–K VI are Hetzer 1968 and Ermatchkov 2003 laws converted to the mole-fraction scale. PZH₂²⁺ is neglected (p.2314).
- Hand check: the constant terms differ from the molality-scale values in the Kamps 2003 note by ln 55.51 = 4.0165. For example, K IV is −8.635 + 4.0165 = −4.6185, and K V is −3.655 + 4.0165 = 0.3615. This confirms the sign convention used in [chemistry](../chemistry.md).
- K VI prints C1 = 3443.1, where Kamps 2003 Table 1 and ln 10 × 1517.0 give 3493. Derks's own K(313 K) = 8.8 × 10¹⁰ matches 3493.1 (e^25.20) and not 3443.1 (e^25.04 = 7.5 × 10¹⁰). The printed 3443.1 is therefore a typographical error. It does not affect this repository, which takes the laws from Ermatchkov 2003 directly.

**Independence.**

- *Lab and method.* Twente. The lab, apparatus and method are independent of UT Austin (Hilliard, Dugas, Xu, Bishnoi) and of Kaiserslautern (Ermatchkov, Kamps).
- *Concentration.* Its 0.2–0.63 m lies below every proposed calibration block: Hilliard D.5 starts at 0.89 m and the Ermatchkov 2003 NMR goes up to 1.48 mol/kg.
- *Temperature.* 298 K lies below the 313 K lower end of Hilliard D.5 and inside the 283–333 K carbamate-law domain. 343 K lies inside the Hamborg P1/P2 domain.

### Recommended role

Score Derks 2005 as a **secondary dilute-edge comparison**:
- whole campaign, all 58 rows;
- chosen before any fit;
- reported apart from the Ermatchkov 2006 falsifier.

Not as the primary hold-out, because:

1. It is outside the calibrated concentration range. It tests concentration extrapolation, not the absorber state.
2. At the source's 4 % loading uncertainty the rows near 1 mol/mol PZ carry little pressure information. Report the 12 rows above 1.0 mol/mol PZ separately, and include the loading uncertainty in the residual scale: σ_lnP² = 0.05² + (∂lnP/∂α · 0.04α)². A pressure-only 5 % scale would overweight those rows.
3. Above 25 kPa, P_CO2 depends on a vapor-pressure subtraction that assumes the solvent vapor pressure is independent of loading. This is small at 0.2–0.6 M, but it is model input, not measurement.
4. The concentrations are nominal molarities. Converting them needs an assumed density, and the per-experiment titrated values are not printed.
5. The authors' screen removed 7 unidentified rows, so their 16 % deviation is not a whole-campaign number. Do not reproduce their screen; Yi's 27.9 % on all 58 rows is the whole-campaign reference.

Bishnoi & Rochelle 2000 (0.6 M, 313 and 343 K) overlaps Derks at 0.6 M. Together they give a two-lab check at the dilute edge.

## Hartono 2013: PZ–water, AMP–water and AMP–PZ–water VLE

**Method (§2, p.152).** NTNU. A modified Swietoslawski ebulliometer measures P–T–x–y at fixed temperature; the procedure follows Kim et al. 2008 (§2.2).
- *Binary PZ–water.* A 40 wt % solution, kept at 45 °C because it solidifies at room temperature, was fed and then diluted step by step.
- *Sampling and analysis.* Liquid and vapor condensate were sampled at each equilibrium. Total amine was titrated: 0.1 M H2SO4 for the liquid, 0.01 M H2SO4 for the condensate (§2.1, §2.4).
- *Ternary.* Total amine came from titration, and the AMP/PZ ratio from ¹H-NMR. About 10 wt % D2O was added to the NMR sample only, as the lock solvent. It is not in the VLE solution.

**Basis.** Liquid and vapor mole fractions of total (stoichiometric) amine. The authors treat the solution as molecular. They estimate protonated amine below 6–8 % at infinite dilution, and lower at higher concentration (§3, p.152). P is the total pressure in kPa.

The activity coefficients in their analysis (Eq. 1) use DIPPR saturation pressures for PZ, extrapolated below the PZ melting point. **Score y·P and P, not γ**: γ depends on that extrapolated subcooled vapor pressure.

**Uncertainty.** The paper gives no T, P, x or y uncertainty for the binary data. From the same apparatus in Kim 2008:
- T ±0.05 K and P ±0.3 kPa (p.2526);
- titration repeatability better than 1 % relative, but "not possible to analyze the samples in the very low concentration range with titration" (p.2528);
- in very dilute liquid (x < 0.01), a vapor mole-fraction uncertainty of ±0.001 gives ±50 % in γ (p.2528).

Hartono gives two more: the NMR repeatability is below 2 %, and the NMR detection limit is ±0.0001 mole fraction for both amines (p.152). Printed vapor fractions have four decimals. At y = 0.0004 the rounding alone is ±12.5 %.

### PZ–H2O (Table 6, p.156)

24 rows: 8 at 60 °C, 10 at 80 °C, 6 at 100 °C (59.95–100.03 °C). This matches the 24 points in Table 8 (p.157), the 24 points Yi fitted, and the 24-row CESAR-1 file.

Hand check of the ranges:
- x_PZ = 0.0237–0.1177, which is 1.35–7.41 mol PZ/kg water;
- y_PZ = 0.0004–0.0067;
- P = 16.3–98.5 kPa;
- P_PZ = y·P runs from 7.5 Pa (60 °C) to 577 Pa (100 °C, 7.1 m). Every row is above 7 Pa.
- The printed k = y/x reproduces y/x in every row.

One row is an outlier: 79.97 °C, x = 0.0472, y = 0.0020, k = 0.0424. Its neighbours at 0.0408 and 0.0564 have k = 0.0196 and 0.0195, and its P_PZ (89.6 Pa) is about twice the trend of its neighbours (36 and 49 Pa).

At 60 °C the three most dilute rows (1.86, 2.25 and 2.73 m) all print y = 0.0004 (P_PZ 7.5–7.7 Pa). At four printed decimals the table cannot resolve the change in P_PZ across them.

The authors' fits (Table 8, p.157) also used 35 total-pressure points of Wilson & Wilding (112.9 and 198.8 °C, Fig. 6b) and 12 freezing points of Fosbøl 2011. Yi counts 33 Wilson & Wilding points; the difference is not resolved. Hartono's reference list gives the identity: H.L. Wilson & W.V. Wilding, 1994, "Vapor Liquid and Liquid–Liquid Equilibrium Measurements on Twenty Two Binary Mixtures", in *Experimental Results for DIPPR 1990–1991 Projects on Phase Equilibria and Pure Component Properties*, pp.63–115 (p.161). The text also cites it once as 1990 (p.159).

**Comparison with Hilliard D.2 at 60 °C (hand check).** Hilliard App. D.2 (PDF pp.968–969) is the only overlap: both sets have rows within 1 K of 60 °C. Hartono's P_PZ is quoted with its four-decimal rounding band.

| PZ (mol/kg) | Hilliard D.2 P_PZ (Pa), 59.98–60.73 °C | Hartono Table 6 P_PZ (Pa), 59.95–60.07 °C |
|---|---|---|
| 1.8–2.0 | 6.8, 6.8, 7.6 | 7.7 [6.7–8.6] at 1.86 m |
| 2.5 | 7.6, 10.1 | 7.6 and 7.5 at 2.25 and 2.73 m |
| 3.6 | 11.4, 11.6 | 9.3 at 3.35 m, 12.7 at 4.03 m |
| 5.0 | 17.2 | 19.7 [18.8–20.6] at 4.88 m |

The two methods (hot-gas FTIR at UT; ebulliometer and titration at NTNU) agree at 60 °C within the stated rounding and the scatter between Hilliard's repeat runs, which is up to 30 % at 2.5 m.

The rejection of D.2 needs a correction:
- Yi 2024 rejected D.2 because its PZ partial pressures are "lower than 1 Pa", at the FTIR detection limit (SI p.1).
- By hand count, 2 of the 46 D.2 rows are below 1 Pa: 0.49 and 0.56 Pa, at 0.9 m and 35–36 °C. Ten rows are below 2 Pa. The values span 0.49–23.8 Pa.
- Hartono's own remark (p.159) is that some Hilliard/Nguyen points at different concentrations show "about the same partial pressure of Pz at the same temperature", possibly from low FTIR sensitivity. Hartono's 60 °C rows show the same flat pattern at their print resolution.
- So the detection-limit concern bears on the low-temperature, low-concentration end of D.2, not on the whole table.

### Is Hartono a better PZ–water calibration than Hilliard D.2?

Recommendation, for owner decision: **calibrate PZ–water on Hartono 2013 Table 6 and use Hilliard D.2 as the low-temperature comparison, not as calibration.**

- Use y_PZ·P and P on each row as the observations. P carries the water-activity information. Exclude the 80 °C x = 0.0472 row and report it separately (23 rows). Include the ±0.00005 rounding of y in the residual scale.
- *For Hartono.*
  - Every P_PZ is at least 7 Pa, measured by a different method.
  - It reaches 7.4 m, the concentration of interest for concentrated PZ.
  - It gives y and total P on the same rows.
  - An independent eNRTL fit accepted it (Yi, 9.0 %).
- *Against using it alone.* Its 60–100 °C range lies above the 40 °C absorber temperature. A PZ–water k anchored at 313.15 K would be extrapolated 20 K below the data. Either set the reference temperature inside the data (for example 353.15 K) or accept a correlated k and slope.
- *Hilliard D.2 as a comparison.* Kept apart from the calibration, its 33–63 °C rows test that downward extrapolation with another lab and method. Report its rows below 2 Pa (10) separately.
- *Alternative.* Calibrate jointly on both sets, with Hilliard rows below 2 Pa excluded. That uses all temperatures but leaves no independent PZ-volatility test.

### AMP–H2O (Table 3, p.154)

26 rows: 9 at 60 °C, 6 at 80 °C, 11 at 100 °C (59.97–100.02 °C). Same method, titration only. Hand check of the ranges: x_AMP = 0.0228–0.3023, y_AMP = 0.0023–0.0309, P = 15.1–98.9 kPa. The authors fitted these together with Belabbaci 2010 (80 total-pressure points), Mathonat 1997 excess enthalpy (16) and Fosbøl 2011 freezing points (14) (Table 5). The AMP saturation pressure is their own Antoine fit to literature data (Eq. 2, p.152; 20–165 °C, 3.5 % average relative deviation).

### AMP–PZ–H2O (Table 9, p.159)

36 rows: 7 at 60 °C, 8 at 70 °C, 7 at 80 °C, 7 at 90 °C, 7 at 100 °C. Hand check of the ranges: x_AMP = 0.0116–0.0992, x_PZ = 0.0101–0.0474, P = 17.0–98.5 kPa.
- The vapor PZ fraction is 0.0001–0.0043. Two rows sit at the 0.0001 NMR detection limit.
- One row (79.98 °C, x_AMP = 0.0351, x_PZ = 0.0359) has y_PZ = 0.0043 and k_PZ = 0.1198, about four times the other 80 °C rows.
- The authors call the data "quite scattered, particularly for the vapor phase" (p.160). Their models miss γ_PZ by 41–47 % with or without an AMP–PZ parameter (Tables 10, 12), and the fitted AMP–PZ parameters "have no statistical significance" (p.160).

For the blend, the AMP vapor fraction and the total pressure are the usable observables. The PZ vapor fraction is supporting only.

## Fosbøl 2011 (identity and scope only)

Freezing-point depression and solubility in PZ–water, AMP–water and AMP–PZ–water at atmospheric pressure (abstract, p.5088):
- 86 data points in total, up to 90 °C;
- solid phases PZ·6H2O, PZ·½H2O and anhydrous PZ;
- Table 1 (PZ–water, p.5090), Table 2 (AMP–water, p.5091), Table 3 (AMP–PZ–water, p.5092).

Its introduction quotes Rosso & Carbonnel: eutectics at 1 °C (ice/hexahydrate) and 33 °C (hexahydrate/hemihydrate), and a peritectic at 58 °C (hemihydrate/anhydrous PZ) (p.5088). The lab (DTU) is independent of Hilliard's DSC (App. I.1). It is a second unloaded-SLE source for the [solid gate](solid-phase.md).

Its references 9 and 10 (p.5093) give the identity behind the "Bishnoi 2002 solid solubility" lead: Bishnoi's 2000 UT dissertation and Bishnoi & Rochelle 2002, Ind. Eng. Chem. Res. 41, 604. Neither was acquired or read here. The tables were not transcribed.
