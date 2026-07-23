# MEA Reaction and Sentinel Primary-Source Audit

Scope:
- Verify the primary reaction equations, coefficient values, reference-state conventions, and temperature ranges needed by the MEA chemical-equilibrium lane.
- Verify one pressure/temperature loading sentinel and the oxazolidone onset evidence.
- Use local primary PDFs or their source-faithful local Markdown renderings only. No parameter regression is performed here.

Evidence rules:
- Values transcribed from a primary table are marked `verified`.
- A later paper that reproduces or changes an earlier value is recorded separately; it is not silently treated as an erratum.
- A missing local primary file is recorded as `unresolved`, even when a later primary paper quotes its value.

## Source fingerprints

| Source | Local file | SHA-256 | Printed locators used |
| --- | --- | --- | --- |
| Austgen, Rochelle & Chen (1991), *Ind. Eng. Chem. Res.* 30, 543--549 | Zotero storage key `UNTA6KIT` (PDF) | `8c0a6a57e5bf9e28b1f9da8022d54290506fe04b4286b6494ef8a44fd924f8db` | Standard states and reactions, pp. 545--546; Table V, p. 547 |
| Tong et al. (2012), *Int. J. Greenhouse Gas Control* 6, 37--47 | Zotero storage key `2SVMJQ58` (PDF) | `78af3d67d58ff610dcc7c34fd55a75763470b7cd5bac0f3e39c256c7d7ffd61c` | Reactions and definitions, p. 43 (Eqs. 5--9); Table 5, p. 44 |
| Böttinger, Maiwald & Hasse (2008), *Fluid Phase Equilibria* 263, 131--143 | Zotero storage key `TJCRKTFQ` (PDF) | `dd0c6986cbd058ec0a2343ac5097439862281492cd2dac01823144233f0fc0f4` | Chemistry, p. 133 (Eqs. I--VI); fitted-constant conventions, p. 138; Table 5, p. 138; onset discussion, p. 141 |
| Böttinger Markdown rendering | Zotero storage key `TJCRKTFQ` (MMD) | `b9643df4c5606e79136dff0ddff9db5adbcd4481a2ebb2f06dc15b19cb3f074d` | Same printed locators as PDF; used for equation text search |
| Wong et al. (2015), *Int. J. Greenhouse Gas Control* 39, 139--147 | Zotero storage key `FHFPHJDQ` (PDF) | `312ea8218c98bf6b78289c5f43baf4e524442efd3943f1dfaf74270ff1292954` | Table 5, p. 146; 1-bar caveat and Fig. 8 discussion, p. 146 |
| Wong Markdown rendering | Zotero storage key `2A27TJTN` (Markdown) | `28925dbc6b8764a55b86c6e901e1a2e9043a2b49a680efc3d428bd3c1dc7fb98` | Same printed locators as PDF |
| Nasrifar & Tafazzol (2010), *Ind. Eng. Chem. Res.* 49, 7620--7628 | Zotero storage key `3G4FGGY4` (PDF) | `29165d43cf374760cc17a730d92e15ed77a9e969af1f3355a1ca39a275f7110f` | Table 1 and reactions, printed p. 7621 |
| Nasrifar Markdown rendering | Zotero storage key `FVFWT3P9` (Markdown) | `7a8b1f03a9445615c0aa991ad0d3fd85f8085b8bee23d4f45214c1685b270976` | Same printed locators as PDF |

The identical Nasrifar Markdown rendering is also retained at `MEA-Thermodynamics/docs/papers/md/Nasrifar and Tafazzol - 2010 - Vapor-liquid equilibria of acid gas-aqueous ethanolamine solutions us.md` (same SHA-256).

## Austgen 1991: reaction directions, standard states, and Table V

`verified`: Austgen et al. state that water and alkanolamine are solvents whose standard states are the pure liquids at system temperature and pressure. Ionic solutes and molecular solutes (H2S and CO2) use an ideal, infinitely dilute aqueous-solution reference at system temperature and pressure. Their equations (1)--(2) give the resulting unsymmetric normalization: solvent activity coefficients approach one at solvent-rich composition, while solute activity coefficients use the infinite-dilution aqueous reference. They explicitly state that this convention permits use of aqueous-phase literature equilibrium constants while the solution is treated as a solvent mixture (printed pp. 545--546).

`verified`: Austgen writes the acid/base chemistry as dissociation, with H3O+ as the proton carrier (printed p. 546):

- (1a) `2 H2O <-> H3O+ + OH-` (water autoionization);
- (2a) `H2O + H2S <-> H3O+ + HS-`;
- (3a) `H2O + HS- <-> H3O+ + S2-`;
- (4a) `CO2 + 2 H2O <-> H3O+ + HCO3-`;
- (5a) `H2O + HCO3- <-> H3O+ + CO3^2-`;
- (6a) `H2O + RR'R''NH+ <-> H3O+ + RR'R''N` (for MEA, MEAH+ dissociation);
- (7a) `RNHCOO- + H2O <-> RNH2 + HCO3-` (carbamate reversion/hydrolysis).

`verified`: Table V (printed p. 547) defines `ln K = C1 + C2/T + C3 ln(T) + C4 T`, labels equilibrium constants as mole-fraction based, and gives the following MEA-relevant rows:

| Reaction | C1 | C2 | C3 | C4 | Temperature range in source |
| --- | ---: | ---: | ---: | ---: | --- |
| (1a) water | 132.899 | -13445.9 | -22.4773 | 0 | 0--225 °C |
| (4a) CO2 to bicarbonate | 231.465 | -12092.10 | -36.7816 | 0 | 0--225 °C |
| (5a) bicarbonate to carbonate | 216.049 | -12431.70 | -35.4819 | 0 | 0--225 °C |
| (6a) MEA protonated-amine dissociation | 2.1211 | -8189.38 | 0 | -0.007484 | 0--50 °C |
| (7a) MEA carbamate reversion | 2.8898 | -3635.09 | 0 | 0 | 25--120 °C |

`verified`: Austgen says the MEA protonated-amine constant in Table V was corrected to the pure-amine reference state using an estimated infinite-dilution MEA-in-water activity coefficient. The MEA carbamate stability/reversion value in Table V was fitted on CO2--amine--water VLE data; it is not a direct pure-carbamate measurement.

`verified outside Zotero`: The original Bates & Pinching (1951) PDF is not
present in local Zotero storage, but the official NIST PDF at
`https://nvlpubs.nist.gov/nistpubs/jres/46/jresv46n5p349_A1b.pdf` was inspected
directly. Its SHA-256 is
`aff8621efd41dbce106bb189fd104840a1513d9d163f4f57dfb1abbf53a30db1`.
Page 349 gives
`-log10 K = 2677.91/T + 0.3869 + 0.0004277 T`; the methods define the
thermodynamic dissociation of monoethanolammonium using molal activities and
zero-ionic-strength extrapolation.

## Nasrifar & Tafazzol 2010: later mole-fraction table and the R2 discrepancy

`verified`: Nasrifar & Tafazzol Table 1 (printed p. 7621) states `ln(k_i^x) = A + B/T + C ln(T) + D T`, labels the constants as mole-fraction based, and gives 273--498 K for reactions 1--3. Their printed reaction equations use the same directions as Austgen for water, CO2-to-bicarbonate, bicarbonate-to-carbonate, and MEAH+ dissociation. Their MEA carbamate row is reaction 9, `MEACOO- + H2O <-> MEA + HCO3-`, with 298--393 K.

The five entries relevant to the nine-species MEA system are:

| Local reaction label | Nasrifar reaction | A | B | C | D | Source range |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| R1 | `2 H2O <-> H3O+ + OH-` | 132.899 | -13445.9 | -22.4773 | 0 | 273--498 K |
| R2 | `CO2 + 2 H2O <-> H3O+ + HCO3-` | **231.456** | -12092.1 | -36.7816 | 0 | 273--498 K |
| R3 | `HCO3- + H2O <-> H3O+ + CO3^2-` | 216.049 | -12431.7 | -35.4819 | 0 | 273--498 K |
| R5 | `MEAH+ + H2O <-> MEA + H3O+` | 2.1211 | -8189.38 | 0 | -0.007484 | 273--323 K |
| R4 | `MEACOO- + H2O <-> MEA + HCO3-` | 2.8898 | -3635.09 | 0 | 0 | 298--393 K |

`verified discrepancy`: Austgen's original 1991 Table V prints R2's A coefficient as **231.465** (printed p. 547), whereas Nasrifar's later primary Table 1 prints **231.456** (printed p. 7621). The difference is 0.009 in A (a roughly 0.9% multiplicative change in K) and is numerically small but scientifically material for source identity. The current MEA-Thermodynamics source-verification manifest adopts the later Nasrifar value as `231.456`; it should be recorded as a later transcription/value choice, not asserted as a proven correction to the 1991 table unless an erratum or original typesetting record is found.

`verified provenance`: Nasrifar explicitly cites Austgen et al. (1991) as the source family for this table. The later paper is therefore a primary reproduction/selection, not an independent reaction-constant measurement.

## Tong 2012 and Aroua 1999: molality-basis carbamate reversion

`verified`: Tong et al. define the MEA reactions on p. 43 (Eqs. (5)--(9)) using molalities and activity coefficients:

- `K1 = m_OH- m_H+ gamma_OH- gamma_H+`;
- `K2 = (m_HCO3- m_H+ gamma_HCO3- gamma_H+) / (m_CO2 gamma_CO2)` for `CO2 + 2 H2O <-> H3O+ + HCO3-` in their simplified notation;
- `K3 = (m_CO3^2- m_H+ gamma_CO3^2- gamma_H+) / (m_HCO3- gamma_HCO3-)`;
- `K4 = (m_MEA m_H+ gamma_MEA gamma_H+) / (m_MEAH+ gamma_MEAH+)`;
- `K5 = (m_MEA m_HCO3- gamma_MEA gamma_HCO3-) / (m_MEACOO- gamma_MEACOO-)` for **`MEACOO- + H2O <-> MEA + HCO3-`**.

Tong's Eq. (12) is `ln K = a_i/(T/K) + b_i ln(T/K) + c_i(T/K) + d_i`. Table 5 (printed p. 44) gives for MEA:

| Constant | a | b | c | d | Range | Cited source |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| K1 | -13445.9 | -22.4773 | 0 | 140.932 | 273--498 K | Edwards et al. (1978) |
| K2 | -12092.1 | -36.7816 | 0 | 235.482 | 273--498 K | Edwards et al. (1978) |
| K3 | -12431.7 | -35.4819 | 0 | 220.067 | 273--498 K | Edwards et al. (1978) |
| K4, MEA | -17.3 | 0 | 0.05764 | -38.846 | 293--353 K | Hamborg & Versteeg (2009) |
| K5, MEA | -1545.3 | 0 | 0 | 2.151 | 293--323 K | **Aroua et al. (1999)** |

The Table 5 footnote says K5 was converted from the original correlation to Tong's Eq. (12) form. Tong's paper is the available local primary evidence for the converted coefficients; the original Aroua et al. (1999) PDF is **not** present in local Zotero storage and remains unresolved here.

`basis warning`: Tong's K5 is molality/activity-coefficient based and is not interchangeable with Austgen/Nasrifar's mole-fraction-based R4. The older retained ideal-speciation value `A=-1.8652, B=-1545.3` was described as a conversion from molality to mole fraction; this audit does not validate that conversion. The later Nasrifar/Austgen R4 (`2.8898, -3635.09`) is a different source/reference convention and must not be mixed with Tong K5 without an explicit standard-state transformation.

## Böttinger 2008: fitted molality convention and oxazolidone onset

`verified`: Böttinger's chemistry section (printed p. 133, Eqs. I--VI) uses:

- `H2O <-> H+ + OH-`;
- `CO2 + H2O <-> H+ + HCO3-`;
- `HCO3- <-> H+ + CO3^2-`;
- protonated amine dissociation `R''R'RNH+ <-> H+ + R''R'R'N`;
- carbamate formation from bicarbonate, `R'RNH + HCO3- <-> R'RNCOO- + H2O`;
- oxazolidone formation, `R'RNH + CO2 <-> R'-OXA + H2O`.

Thus Böttinger's carbamate reaction is the reverse direction of Austgen/Nasrifar/Tong's carbamate **reversion/hydrolysis** reaction. Any reaction-basis import must reverse both stoichiometric signs and `ln K` for this pair.

`verified`: Böttinger's Section 4 (printed p. 138) states that all ionic and molecular solute activity coefficients are molality based with an infinite-dilution-in-water reference; water uses a Raoult normalization. Their Eq. (2) uses
`ln(K_R) = A_R + B_R/(T/K) + C_R ln(T/K) + D_R(T/K) + E_R/(T/K)^2`.

`verified`: Böttinger Table 5 (printed p. 138) reports:

- MEA protonated-amine dissociation (IV): `A=-0.8909`, `B=-6166.11`, `D x 10^4=-9.8482`, source `[28]` (Bates & Pinching 1951);
- MEA carbamate formation (V): `A=-6.6203`, `B=3255.31`, `D x 10^4=-4.564`, source `this work`;
- MEA oxazolidone formation (VI): `A=-29.0365`, `B=6822.9`, `D x 10^4=361.0`, source `this work`.

These are molality-reference fitted constants and are not the Austgen/Nasrifar mole-fraction constants.

`verified onset`: In the MEA results discussion (printed p. 141), Böttinger reports that at approximately `0.5 mol_CO2/mol_MEA`, free molecular amine has fallen nearly to zero and carbamate concentration begins to decline at higher loading; above approximately `0.5 mol_CO2/mol_MEA`, **2-oxazolidone is present in quantifiable amounts**. At loadings above approximately `0.7`, molecular CO2 is also present. The paper studied MEA at 0.2 and 0.3 g/g initial amine, 293--353 K, and pressures 5--25 bar (abstract and experimental section).

This is an onset/eligibility boundary, not proof that every Böttinger point above 0.5 has a separately measured oxazolidone concentration in the current MEA-Thermodynamics CSV. The species tables report an `x_OXA` column, but any reuse must preserve the source's molar-fraction basis and the measured-vs-inferred row status.

## Wong 2015: pressure/temperature loading sentinel

`verified`: Wong et al. Table 5 (printed p. 146) reports 30 mass% MEA CO2 loading by two methods at 303.15, 313.15, and 323.15 K over nominal pressures from 1 to 60 bar. At **313.15 K and 1.0 bar**, the first listed row is:

| T | P | Calculated loading | Predicted loading | MSE x 10^-3 |
| ---: | ---: | ---: | ---: | ---: |
| 313.15 K | 1.0 bar | **0.150 mol CO2/mol MEA** | 0.144 | 0.033 |

The 0.150 value is the pressure-drop/Raman “Calculated” result; it is not the 0.144 model prediction. The paper's p. 146 text says the 1-bar rows were produced by injecting small CO2 batches to obtain low loadings and explicitly warns that the 1-bar readings had not reached the highest equilibrium capacity at that pressure. Therefore this row is suitable as a fixed-T,P **loading/mechanical sentinel** only, not as a saturation-capacity claim.

`verified limitation`: Wong's species-distribution Fig. 8 is at 303.15 K and 30% MEA, and the source says its pressure/loading sequence was performed in batches. The paper does not map a unique pressure to each Fig. 8 species point. The 313.15 K/1-bar Table 5 row therefore cannot be paired with a species vector from Fig. 8.

## Canonical-use consequences

1. Preserve reaction direction, basis, and reference identity as separate fields. In particular, do not mix Tong/Aroua molality K5 with Nasrifar/Austgen mole-fraction R4 without a proven conversion into the Provider Helmholtz reference basis.
2. Record the R2 coefficient as a source conflict: Austgen 1991 prints `231.465`; Nasrifar 2010 prints `231.456`. The new source contract selects the original Austgen value; the legacy Phase 2 manifest retains the later Nasrifar value and must not describe it as a proven correction.
3. Keep R5/Bates source coverage at 273--323 K unless an independent direct source is admitted. The official NIST primary PDF supplies the admitted equation even though Zotero does not contain a local copy.
4. Keep Tong/Aroua K5 coverage at 293--323 K. Do not extrapolate it to 333.15 or 353.15 K without a new source.
5. Treat Böttinger's `alpha approximately 0.5` oxazolidone onset as an exclusion/extension boundary. High-loading data without an oxazolidone species and balance record are not source-complete nine-species targets.
6. Wong 313.15 K, 1 bar, calculated loading `0.150` can be used as a source-bound sentinel for a fixed-T,P loading check, with the batch/non-capacity caveat retained. It does not close the row-specific pressure gap for Böttinger/Jakobsen/Matin speciation vectors.

## Unresolved primary-source items

- Local Zotero search did not contain the Bates & Pinching (1951) PDF or
  Markdown; the official NIST PDF was independently verified and fingerprinted
  as recorded above.
- Local Zotero search did not contain Aroua, Benamor & Haji-Sulaiman (1999), *J. Chem. Eng. Data* 44, 887--891. Tong Table 5 is the available primary paper for the converted molality coefficients.
- No source in this audit transforms the mole-fraction or molality constants into the installed Provider's exact Helmholtz standard-state vector. That conversion remains a required Equilibrium/Provider contract test.
- Böttinger and Wong give different observable bases (true mole fractions versus mol/kg/Raman calibration) and different temperature/pressure protocols. They must not be joined by inferred row pressure or denominator conversion.
