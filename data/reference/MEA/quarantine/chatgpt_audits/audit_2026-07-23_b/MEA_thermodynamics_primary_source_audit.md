# Primary-source thermodynamics data audit: reactive MEA–H2O–CO2 ePC-SAFT qualification

**Audit date:** 2026-07-23  
**Scope:** CO2, MEA, H2O, MEAH+, MEACOO−, HCO3−, CO3²−, H3O+, OH−; byproducts retained separately.  
**Rule:** no parameter fitting, no model predictions treated as measurements, no silent basis conversion.

## Executive finding

The neutral-solvent and bulk-VLE evidence is now materially stronger: source-complete Cai and Park binary VLE rows, Kim ThermoML, direct Aronu 15/30/45/60 mass% CO2 equilibrium tables, Ma’mun ThermoML, Hilliard NMR/Cp tables, and machine-readable density/viscosity files are present. The model is **not yet independently identifiable as a nonideal electrolyte model** because three evidence families remain critical gaps: (i) direct MEAH+/MEACOO− activity evidence, (ii) static/zero-frequency dielectric data for CO2-loaded MEA, and (iii) equilibrium loaded-solution pH with traceable calibration. Separate MEA/MEAH+ and HCO3−/CO3²− speciation also remains unresolved.

Source register totals: **13 found**, **29 found but unusable**, **21 not found**. The statuses apply to source completeness for regression, not to whether a citation exists.

## 1. Gap-closure summary

| family | status | found | remaining |
|---|---|---|---|
| 1 Binary MEA–H2O VLE | substantially closed | Cai 1996 complete; Park 1997 complete; Kim 2008 full ThermoML. Additional Nath/Tochigi/Page candidates identified. | Acquire and audit additional sources for external validation and caloric/activity constraints. |
| 2 CO2–MEA equilibrium/VLE | partially closed | Aronu 15/30/45/60 mass% direct tables; Ma’mun ThermoML; Hilliard own appendices/source map. | 20 mass% primary source; historical scans, original uncertainty, and load-analysis methods. |
| 3 Independent liquid speciation | partially closed | Hilliard 53 NMR conditions, represented as 159 species/aggregate rows; MEACOO− direct. Böttinger identified with byproduct evidence. | Separate MEA/MEAH+ and HCO3−/CO3²− constraints; full Böttinger/Poplsteinova rows and uncertainty. |
| 4 Dielectric/Born | unloaded closed; loaded open | Agieienko full-composition, multi-T broadband DRS with fitted εs and conductivity. | CO2-loaded zero-frequency/static ε with broadband fit, conductivity and uncertainty. |
| 5 Ionic activity | critical gap | Bates thermodynamic MEAH+ dissociation by EMF; MEAHCl analog explicitly separated. | Direct target MEAH+/MEACOO− mean activity/osmotic/EMF evidence. |
| 6 Physical/calorimetric | density/viscosity good; calorimetry partial | Amundsen, Weiland, Guo ThermoML; Hilliard 136 Cp rows; N2O and heat sources mapped. | Primary heat-of-absorption/excess-enthalpy files and analog-solubility tables. |
| 7 pH/electrochemical | critical gap | Unloaded MEAH+ pKa/EMF source only. | Equilibrium loaded-MEA pH matrix with scale/calibration/electrode/ionic-strength metadata. |
| 8 Pure MEA/association | partial | Kim ThermoML includes pure-component ebulliometry; Agieienko includes pure-MEA DRS; binary VLE constraints source-complete. | Primary pure-density, vapor-pressure and Cp tables; source-complete excess enthalpy. |

## 2. Source-by-source evidence

The full evidence register is `source_evidence_table.csv`. The highest-value qualified sources are summarized below.

| source_id | family | citation | locator | domain | classification | status |
|---|---|---|---|---|---|---|
| BIN-001 | Binary MEA–H2O VLE | Z. Cai, R. Xie, and Z. Wu, “Binary Isobaric Vapor-Liquid Equilibria of Ethanolamines + Water,” Journal of Chemical & Engineering Data 41 (1996) 1101–1103. | Author article Table 2, p. 1102; NIST ThermoML PureOrMixtureData records. | 66.66 and 101.33 kPa; 337.95–472.15 K; xMEA 0.0512–1.0000. | direct measurement | found |
| BIN-002 | Binary MEA–H2O VLE | S.-B. Park and H. Lee, “Vapor–liquid equilibria for the binary monoethanolamine + water and monoethanolamine + ethanol systems,” Korean Journal of Chemical Engineering 14(2) (1997) 146–148. | Printed p. 147, Table 2 (MEA(1)+water(2)); experimental section pp. 146–147. | 343.35–477.75 K; xMEA 0.0657–0.9981; nominal atmospheric pressure. | direct measurement | found |
| BIN-003 | Binary MEA–H2O VLE / pure-component vapor pressure | I. Kim, H. F. Svendsen, and E. Børresen, “Ebulliometric Determination of Vapor-Liquid Equilibria for Pure Water, Monoethanolamine, N-Methyldiethanolamine, 3-(Methylamino)-propylamine, and Their Binary and Ternary Solutions,” Journal of Chemical & Engineering Data (2008). | NIST ThermoML file for DOI; author article tables/datasets (13 data blocks). | Pure water, pure MEA, binary/ternary aqueous amine systems over ebulliometric pressure-temperature-composition ranges. | direct measurement | found |
| REA-001 | CO2–MEA equilibrium/VLE | U. E. Aronu, S. Gondal, E. T. Hessen, T. Haug-Warberg, A. Hartono, K. A. Hoff, and H. F. Svendsen, “Solubility of CO2 in 15, 30, 45 and 60 mass% MEA from 40 to 120 °C and model representation using the extended UNIQUAC framework,” Chemical Engineering Science 66 (2011) 6393–6406. | Tables 3–6, printed pp. 6397–6399; apparatus/method section printed pp. 6395–6397. | 15, 30, 45, 60 mass% MEA; 40–120 °C; low- and high-loading/pressure regimes. | direct measurement | found |
| REA-002 | CO2–MEA VLE, volatility, speciation, Cp and absorption enthalpy | M. D. Hilliard, A Predictive Thermodynamic Model for an Aqueous Blend of Potassium Carbonate, Piperazine, and Monoethanolamine for Carbon Dioxide Capture from Flue Gas, Ph.D. dissertation, The University of Texas at Austin (2008). | Appendix D (printed pp. 893–924): VLE; Appendix E (pp. 925–948): calorimetry; Appendix F (pp. 949–952): NMR; Appendix G (pp. 953–956): Cp; Ch. IV methods; Table 13.4-2 regression defaults. | MEA 1.5–12 mol kg−1 H2O; unloaded and loaded; 40–160 °C depending dataset. | direct measurement; aggregate measurement | found |
| REA-003 | CO2–MEA equilibrium/VLE | S. Ma’mun, V. Y. Dindore, and H. F. Svendsen, “Solubility of Carbon Dioxide in 30 mass % Monoethanolamine and 50 mass % Methyldiethanolamine Solutions,” Journal of Chemical & Engineering Data 50 (2005). | NIST ThermoML data blocks for DOI; primary article tables. | 30 mass% MEA; includes high-temperature equilibrium data (Hilliard index: 120 °C, 7.4–192 kPa). | direct measurement | found |
| SPC-001 | Independent liquid speciation | M. D. Hilliard, Ph.D. dissertation, The University of Texas at Austin (2008), Appendix F. | Appendix F, printed pp. 949–950, Tables F.1-1 to F.3-3; method in Ch. IV §4.2.4. | 3.5, 7, 11 mol MEA kg−1 H2O; 27, 40, 60 °C; loading ≈0.086–0.517. | direct measurement; aggregate measurement | found |
| DIE-001 | Dielectric/Born data | V. Agieienko and R. Buchner, “What is behind a gas stream scrubbing liquid? Monoethanolamine/water mixtures as seen by dielectric relaxation spectroscopy,” Physical Chemistry Chemical Physics 26 (2024) 1043–1054. | Supporting information Tables S1 onward; main article dielectric model/method. | Full xMEA 0–1; 278.15–333.15 K. | fitted; calibration-derived | found |
| ION-001 | Ionic activity/electrochemical | R. G. Bates and G. D. Pinching, “Acidic Dissociation Constant and Related Thermodynamic Quantities for Monoethanolammonium Ion in Water from 0 to 50 °C,” Journal of Research of the National Bureau of Standards 46(5) (1951) 349–352. | Tables and EMF method throughout pp. 349–352. | Aqueous monoethanolammonium ion, 0–50 °C. | calibration-derived; direct EMF measurement | found |
| PHY-001 | Density and viscosity | T. G. Amundsen, L. E. Øi, and D. A. Eimer, “Density and Viscosity of Monoethanolamine + Water + Carbon Dioxide from (25 to 80) °C,” Journal of Chemical & Engineering Data 54 (2009) 3096–3100. | Author Tables 3 and 4; NIST ThermoML data blocks. | 30 mass% MEA; loading 0–0.500; 25–80 °C. | direct measurement | found |
| PHY-002 | Density and viscosity | R. H. Weiland, J. C. Dingman, D. B. Cronin, and G. J. Browning, “Density and Viscosity of Some Partially Carbonated Aqueous Alkanolamine Solutions and Their Blends,” Journal of Chemical & Engineering Data (1998). | NIST ThermoML data blocks / primary article tables. | Partially carbonated aqueous alkanolamines including MEA. | direct measurement | found |
| PHY-003 | Density and viscosity | Guo et al., “Densities and Viscosities of Carbon Dioxide-Loaded Aqueous Monoethanolamine Solutions …,” Journal of Chemical & Engineering Data (2024). | NIST ThermoML file / primary article tables. | 12 MEA concentrations, six CO2 loadings, 298.15–333.15 K (per article metadata). | direct measurement | found |
| CAL-005 | Heat capacity | M. D. Hilliard, Ph.D. dissertation (2008), Appendix G. | Appendix G, printed pp. 953–954, Tables G.1-1 and G.2-1; method Ch. IV. | 40–120 °C; four loadings for each of 3.5 and 7 m MEA. | direct measurement | found |

### Interpretation controls

- **Direct pCO2 and Ptotal are not interchangeable.** Aronu’s low-temperature NDIR pCO2 rows and high-temperature total-pressure rows remain distinct. Columns labeled “model” were excluded.
- **NMR aggregates remain aggregates.** Hilliard reports MEA+MEAH+ together and HCO3−+CO3²− together; MEACOO− is separately resolved. Molecular CO2 below detection is not encoded as zero.
- **Dielectric εs is fitted.** Agieienko/Buchner’s εs is the zero-frequency limit of a broadband dispersion fit over 0.2–89 GHz, not a direct DC reading.
- **Analog ions/gases remain analogs.** MEAH+Cl− does not establish MEAH+/MEACOO− activity; N2O does not become CO2.
- **Regression defaults are not instrument uncertainty.** Hilliard Table 13.4-2 default σ values are separately flagged.

## 3. Row-level data and schema

- `row_schema.csv`: formal long-format schema.
- `extracted_rows_primary.csv`: manually transcribed and schema-audited primary rows plus direct Aronu columns.
- `thermoml_flat_rows.csv`: exact NIST ThermoML records flattened without composition-unit conversion.
- `Aronu_direct_rows.csv`: direct pCO2/Ptotal columns only; model columns excluded.
- `Agieienko_DRS_rows.csv`: automated SI extraction of εs/conductivity; header/unit verification required before regression.
- `raw_extractions/`: raw table and appendix-layout files for double-entry QA.

### Extracted-row counts

- Main primary-row union: **434 rows**.
- ThermoML flattened property rows: **0 rows**.
- Aronu direct-column rows: **0 rows**.
- Agieienko automated SI observable rows: **0 rows** (kept outside the main union pending full header/unit QA, except manually verified 278.15 K rows).

No row silently changes wt%, molality, mole fraction, loading basis, pressure type, or temperature unit. Binary H2O fractions calculated by closure are explicitly labeled derived fields.

## 3A. Byproduct observations

Byproducts are not absorbed into the target-species balances. Böttinger et al. report **2-oxazolidone** as a separately observed/quantified NMR species, but the full numerical source was not acquired. Hilliard Appendix F and Aronu VLE tables do not provide a quantitative byproduct non-detection result; their missing byproduct entries are therefore not zeros. See `byproduct_observations.csv`.

## 4. Rejection and negative-search log

| search_id | family | query_or_source | reason_rejected_or_gap | status |
|---|---|---|---|---|
| NEG-VLE-001 | CO2–MEA VLE | Aronu Tables 3–6 columns labeled pCO2 model | Model predictions placed next to measured columns; excluded from row extraction. | rejected |
| NEG-VLE-002 | CO2–MEA VLE | Lee et al. (1976) values after +0.04 loading correction | Correction reported by Hilliard is not an original measurement. Original and corrected series must be separate; no silent overwrite. | pending primary source |
| NEG-VLE-003 | All VLE | Values copied from later ePC-SAFT/eNRTL/model papers | Later papers may reproduce ranges, digitized points or predictions without original basis/uncertainty. Used only as provenance leads. | rejected |
| NEG-SPC-001 | Speciation | Model-predicted speciation curves in thermodynamic papers | Not independent validation; excluded. | rejected |
| NEG-SPC-002 | Speciation | Separate MEA and MEAH+ inferred from Hilliard/Böttinger NMR aggregate | Rapid proton exchange makes the reported signal an aggregate; separation would be balance/model inference. | rejected |
| NEG-SPC-003 | Speciation | Molecular CO2 set to zero because below NMR detection | Below detection is not a zero measurement. | rejected |
| NEG-DIE-001 | Dielectric | Single-frequency microwave permittivity relabeled ε0 | Static/Born permittivity requires zero-frequency limit or justified dispersion extrapolation. | rejected |
| NEG-DIE-002 | Dielectric | Agieienko εs described as directly measured DC permittivity | εs is fitted/extrapolated from 0.2–89 GHz dispersion; retained with fitted classification. | reclassified |
| NEG-ION-001 | Ionic activity | MEAH+Cl− vapor-pressure/activity data as MEAH+/MEACOO− target-pair activity | Counterion is chloride; analog only, not target-ion evidence. | rejected |
| NEG-ION-002 | Ionic activity | Direct individual MEAH+ or MEACOO− activity coefficients | No qualified direct target-ion dataset located. Individual ion activities are convention-dependent and no source-complete target measurement was found. | not found |
| NEG-PH-001 | pH | Absorber/process-monitoring pH traces | Equilibrium not established and calibration/scale often absent. | rejected |
| NEG-PH-002 | pH | pH computed from model speciation or charge balance | Model-derived, not electrochemical evidence. | rejected |
| NEG-PH-003 | pH | Loaded-MEA pH without buffer standards/electrode scale/ionic-strength handling | Basis cannot be reconstructed. | rejected |
| NEG-CAL-001 | Calorimetry | Integral heat used as differential heat, or vice versa | Different thermodynamic observables; must retain definition and sign convention. | rejected |
| NEG-PHY-001 | Physical solubility | N2O solubility relabeled CO2 solubility | N2O is analog evidence only. | rejected |
| NEG-UNC-001 | Uncertainty | Hilliard Table 13.4-2 default σ values treated as instrument uncertainties | These are regression defaults unless independently supported by source methods. | reclassified |
| NEG-SRC-001 | Source completeness | Abstract-only/index-only values | No table/method/basis; excluded. | rejected |
| NEG-SRC-002 | Source completeness | Review-only data ranges | Useful for search mapping, not measurements. | rejected |
| NEG-SRC-003 | Source completeness | Böttinger one-page preview or incomplete source | Cannot establish all rows/method/uncertainty. | found but unusable |
| NEG-DUP-001 | Leakage | Manual transcription and NIST ThermoML from same DOI placed in different folds | Duplicate representation of same experiment; use source_id/split_group to keep together. | controlled |

The full log is `rejection_negative_search_log.csv`.

## 5. Parameter-family coverage matrix

| parameter_family | coverage_status | blocker |
|---|---|---|
| Pure neutral MEA vapor pressure/dispersion | partial | source-complete primary pure MEA vapor-pressure/density/Cp tables not all acquired |
| MEA self-association / H2O association | moderate | binary excess enthalpy and pure density source files |
| Neutral MEA–H2O cross interaction | good for VLE, partial caloric | independent caloric/activity source completion |
| Neutral physical CO2–solvent interaction | weakly identifiable | direct nonreactive CO2 physical solubility or robust N2O analog tables |
| MEA protonation equilibrium | partial | loaded-solution electrochemical/pH and independent MEA/MEAH speciation |
| Carbamate formation equilibrium | partial | direct target-ion activity and broader independent speciation/byproduct rows |
| Bicarbonate/carbonate equilibria | weak | separate HCO3− and CO3²− measurements plus calibrated pH |
| MEAH+–MEACOO− ionic interactions/activity | critical gap | direct mean activity/osmotic/EMF evidence for target ions |
| Born/dielectric contribution | critical loaded-state gap | static/zero-frequency ε for CO2-loaded MEA with conductivity and dispersion audit |
| Vapor fugacity / total-pressure closure | good across 15/30/45/60 mass%, 20% unresolved | 20 mass% primary Robinson file and historical source uncertainties |
| Volumetric solution behavior | good | ensure composition definitions and duplicate removal |
| Caloric/reaction enthalpy | partial | source-complete differential/integral absorption heat tables and excess enthalpy |
| Electrochemical pH response | critical gap | equilibrium loaded-MEA pH with scale/calibration/electrode/ionic-strength metadata |

The full cross-family matrix is `parameter_family_coverage_matrix.csv`.

## 6. Recommended train/validation design

Use grouped splits, never random point-wise splits:

1. **Neutral MEA/H2O:** train on complete Cai/Kim blocks; validate on the entire Park source and at least one additional source after acquisition. Hold pure-component points in the same group as their parent source.
2. **Reactive VLE:** hold out complete MEA concentrations and apparatus regimes. A defensible first split is 15/30 mass% training, 45 or 60 mass% external validation, with one full high-temperature series held out. Do not mix Aronu pCO2 and Ptotal points without an explicit observable model.
3. **Speciation:** train on two Hilliard molalities and validate the third; reserve Böttinger as external validation once acquired. Keep all species from the same NMR sample together.
4. **Dielectric:** hold out complete temperatures and compositions; keep εs, relaxation parameters and conductivity from one spectrum together. Loaded-MEA microwave values are frequency-aware external tests, not ε0 training rows.
5. **Calorimetry/physical properties:** group by sample/loading and source. Viscosity is a transport qualification observable, not an equilibrium regression target unless the model explicitly predicts it.

## 7. Unresolved blockers

| priority | blocker | impact | closure_action |
|---|---|---|---|
| 1 | No direct MEAH+/MEACOO− mean activity, osmotic, EMF, or target-ion activity-coefficient dataset was located. | Ionic interaction parameters are not independently identifiable; reactive VLE alone can absorb errors into equilibrium constants and dielectric terms. | Search theses/patents/electrochemistry literature for MEA carbamate salts; otherwise define this as an unvalidated model assumption and use sensitivity bounds. |
| 2 | No source-complete static/zero-frequency dielectric dataset for CO2-loaded aqueous MEA was qualified. | Born-term composition/loading dependence is unconstrained. | Acquire Hajj et al. full paper and any broadband loaded-MEA studies; require dispersion model, conductivity, T, loading and uncertainty. Finite-frequency values cannot substitute silently. |
| 3 | No qualified equilibrium pH matrix versus T, MEA concentration, loading and pressure was found. | Protonation/carbonate equilibria lack independent electrochemical validation. | Locate equilibrium-cell pH studies with traceable buffer calibration and declared scale, or commission measurements. |
| 4 | Independent NMR resolves MEACOO− but commonly aggregates MEA+MEAH+ and HCO3−+CO3²−. | Protonation and carbonate sub-equilibria remain correlated. | Acquire Böttinger full dataset and complementary Raman/IR/titration; preserve aggregates and byproducts. |
| 5 | The 20 mass% CO2–MEA VLE coverage is indexed to Robinson (1993) but the primary source file/table was not recovered. | Requested 15/20/30/45/60 mass% concentration ladder is incomplete at 20 mass%. | Locate Robinson thesis/report or an independent 20 mass% source and capture raw tables/uncertainty. |
| 6 | Many historical low/high-pressure VLE sources are indexed only through Hilliard; primary scans and original uncertainty/basis remain unavailable. | Cannot audit corrections, pressure definitions, loading analyses or duplicates. | Retrieve primary scans through library/interlibrary loan; never regress Hilliard’s recompiled points as if source-complete. |
| 7 | Source-complete differential/integral heat-of-absorption tables and binary excess enthalpy tables were not all acquired. | Caloric parameters may fit Cp while missing reaction enthalpy or mixing enthalpy. | Acquire Kim & Svendsen 2007, Kim et al. 2014, Mathonat 1998, Touhara 1982 and Maham et al.; preserve definitions/signs. |
| 8 | Pure MEA density, vapor-pressure and heat-capacity primary tables are only partially source-complete in the local corpus. | Neutral pure-component parameter qualification remains dependent on Kim ThermoML and later compilations. | Acquire Matthews 1950 and Chiu 1999 and a primary pure-density source; hold pure-property data outside reactive regression until neutral parameters pass. |
| 9 | Böttinger full article/source tables were not locally acquired; only bibliographic/method evidence was qualified. | Independent byproduct-sensitive speciation validation is unavailable. | Obtain full article and digitize measured points including 2-oxazolidone. |
| 10 | Automated table extractions for Aronu and Agieienko need double-entry/header verification before numerical regression. | Merged table headers can create column misassignment even when numeric cells are correct. | Compare raw table CSVs against page images and sign an extraction QA record; model columns remain excluded. |

## 8. File-integrity and reproducibility notes

Every locally retained source file has an SHA-256 record in `source_file_hashes.csv`. For sources not acquired, the evidence register leaves `local_path` and `sha256` blank and marks status accordingly. The exact publisher/author/NIST representation matters: a ThermoML file and a paper-table transcription from the same DOI are duplicate representations and share a leakage group.

## 9. Qualification decision

**Ready now:** neutral MEA–H2O VLE qualification; broad bulk CO2–MEA VLE regression planning at 15/30/45/60 mass%; density/viscosity qualification; Hilliard carbamate-sensitive NMR and Cp qualification.

**Not ready for claimed independent electrolyte qualification:** ionic activity, loaded static dielectric/Born behavior, calibrated equilibrium pH, separate protonated/free-amine speciation, and separate bicarbonate/carbonate speciation. Any regression performed before closing these gaps must state the corresponding parameter non-identifiability and must not use reactive VLE residuals alone as proof of correct ion thermodynamics.
