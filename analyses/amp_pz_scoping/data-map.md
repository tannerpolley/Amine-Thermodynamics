# AMP, PZ and blend source inventory

Research snapshot for [#227](https://github.com/tannerpolley/Amine-Thermodynamics/issues/227), 2026-10-29. This is a candidate-source inventory, not fit admission. No private measurements or parameter values are retained. CESAR-1 was inspected read-only at the supplied commit `f24611b95a0fa62bd41b99c1bfd8d700fc6ddd2a`; nothing from it was executed. Counts below count CSV records, not independent experiments. Concatenations, individual figures and repeated Hartono files can overlap: **do not sum them as independent observations**.

Stage key: (a) pure PC-SAFT; (b) unloaded VLE; (c) unloaded permittivity; (d) reaction constants; (e) loaded pressure; (f) speciation; (g) absorption heat; (h) loaded density; (i) loaded heat capacity; (j) earlier SAFT. Unloaded Cp is supporting evidence, not stage (i).

## Subsystem × stage

| Subsystem | a | b | c | d | e | f | g | h | i | j |
|---|---|---|---|---|---|---|---|---|---|---|
| AMP–water | Pakravesh SI / Ayad lead | Hartono; Pappa | Hsieh, checked | Hamborg, checked methods | — | — | — | — | — | Pakravesh; Ayad |
| AMP–CO2–water | inherited | inherited | inherited | Hamborg; Ciftja apparent law | Chen; Dash; Hartono; Jahangiri; Kundu; Tong | Ciftja | Arcis lead | gap | gap | no loaded ePC-SAFT source verified |
| PZ–water | gap | Hartono; Hilliard; Nguyen | gap | Hamborg, checked methods | — | — | — | — | — | gap |
| PZ–CO2–water | inherited gap | inherited | inherited gap | Ermatchkov carbamate lead | Derks; Dugas; Kamps; Xu; Hilliard | Ermatchkov | Liu; Hartono | gap | Hilliard | no loaded ePC-SAFT source verified |
| AMP–PZ–water | single-amine sets needed | Hartono | gap | single-amine constants | — | — | — | — | — | no applicable blend SAFT source verified |
| AMP–PZ–CO2–water | inherited | inherited | inherited gap | single-amine constants / activity coupling | Brúder; Dash; Hartono; Jahangiri; Li | gap | Hartono | gap | gap | no applicable blend SAFT source verified |

A gap means no admissible dataset established by this bounded survey, not no published data. A law's methods being checked does not make its numerical coefficients ready for execution.

## Paper-checked measurement blocks outside the private transcription inventory

| Subsystem; stage | Published source and exact locator | Conditions and basis | Count | Check |
|---|---|---|---:|---|
| AMP–water; c | Hsieh, Chen & Li 2007, DOI 10.1021/je600515j, Table 2 p.620 | pure AMP, 303.15–328.15 K; relative permittivity | 6 | checked against the paper (Table 2, PDF 8X653CVB) |
| AMP–water; c | Hsieh 2007, Table 5 p.622 | unloaded x(AMP)=0.2,0.4,0.6,0.8 at six temperatures, 303.15–328.15 K | 24 | checked against the paper (Table 5, PDF 8X653CVB) |
| AMP–CO2–water; e | Tong et al. 2012, DOI 10.1016/j.ijggc.2011.11.005, Table 4 p.43 | 30 mass% unloaded AMP; five isotherms 313.2–393.2 K; **total** P, loading mol CO2/mol AMP; solvent-vapor baseline rows included | 45 total: 40 loaded + 5 unloaded baselines | checked against the paper (Table 4 and §2; PDF 2SVMJQ58); do not call P partial pressure |
| AMP–CO2–water; f | Ciftja et al. 2011, DOI 10.1016/j.egypro.2011.01.096, Table 2 p.618 and §2 | 30 wt% stock AMP, 25 °C; loading 0–0.62 mol CO2/mol AMP; NMR mole fractions, added D2O/internal standard | 7 including unloaded row | checked against the paper (Table 2, author-uploaded full text); not verification of the 57-row private file |

Hsieh methods p.619 specify composition uncertainty ±1.5×10⁻4 mole fraction; Table 2 gives replicate standard deviations, not a blanket expanded uncertainty. Tong §2.3 reports loading repeatability below 1.5% and discusses systematic error; those are not a universal pressure residual scale. Ciftja separates overlapping protonation signals with pH and literature constants: split species are model-assisted, not independent NMR observations.

AMPH+ dissociation: use Hamborg & Versteeg 2009 Table 1 (p.1320), the correlation form ln K = A/T + B + C ln T in Eq.21 (p.1319), and the 24 AMP experimental runs in Table 16 (p.1325). Table 4 describes DMMEA; Eq.35/Table 15 do not provide the AMP dissociation law. The source uses hydronium, explicit water activity, and an infinite-dilution molality standard state. Transcribe the AMP measurements and establish the numerical correlation and its uncertainty before adoption. Document the mapping into the Engine reaction-reference convention, including water factors, standard pressure, direction, and temperature domain; verify source reference values and reciprocal constants for reversed reactions.

Hamborg & Versteeg 2009: DOI 10.1021/je800897v; parent D9KXSKLR, PDF 334KGLPV. PZ Tables 9, 10 and 16 require an explicit group-to-reaction mapping checked against named stoichiometry; that mapping remains unresolved. These reaction-equilibrium measurements are excluded from the four measurement-block count.

## CESAR-1 index entries

**Every condition and count in this table is “CESAR-1 transcription only, unchecked”.** Header temperature units are preserved: a bare `temperature` is not assumed to mean kelvin. Ranges are file summaries only. Composition is the column's printed basis; whether it refers to unloaded stock, final loaded liquid, molecules or amine sites must be checked in the paper. All rows remain unscored. Source attribution is a filename lead where year/title is unresolved.

| Subsystem; stage | Published-source lead / index filename | CSV rows | Header-based conditions / composition | Basis to verify | Check |
|---|---|---:|---|---|---|
| AMP–CO2–water; e | `chen_AMP_CO2_loading.csv` | 13 | T (K): 313–373; AMP Molality: 4.8–4.8 | CO2 Loading; P_CO2 (kPa) | CESAR-1 transcription only, unchecked |
| AMP–CO2–water; f | `ciftja_et_al_AMP_CO2_H2O_speciation.csv` | 57 | T (K): 298.15–318.15; AMP Mass Fraction: 0.3–0.3 | CO2 Loading; x_AMP/AMPH^+; x_AMPCOO^-; x_HCO3^-/CO3^2- | CESAR-1 transcription only, unchecked |
| AMP–CO2–water; e | `dash_AMP_CO2_loading.csv` | 166 | T (K): 298–328; AMP Molarity (mol/L total): 2.5–4.9; AMP Molality: 3.16–8.81 | P_CO2 (kPa); CO2 Loading | CESAR-1 transcription only, unchecked |
| AMP–CO2–water; e | `hartono_et_al_AMP_CO2_H2O_P_CO2.csv` | 109 | T (K): 313–353; AMP Mass Fraction: 0.009–0.268; AMP Molarity: 0.1–3 | P_CO2 (kPa); CO2 Loading | CESAR-1 transcription only, unchecked |
| AMP–CO2–water; e | `hartono_et_al_AMP_CO2_H2O_P_CO2_2.csv` | 82 | T (K): 313–353; AMP Mass Fraction: 0.09–0.268; AMP Molarity: 1–3 | P_CO2 (kPa); CO2 Loading | CESAR-1 transcription only, unchecked |
| AMP–CO2–water; e | `hartono_et_al_AMP_CO2_H2O_P_total.csv` | 50 | T (K): 353–393; AMP Molarity: 0.1–3; AMP Mass Fraction: 0.009–0.268 | P_total (kPa); CO2 Loading | CESAR-1 transcription only, unchecked |
| AMP–CO2–water; e | `jahangiri_AMP_CO2_partial_pressure.csv` | 36 | T (K): 293.15–323.15; AMP Mass Fraction: 0.0897–0.272 | P_CO2 (kPa); CO2 Loading | CESAR-1 transcription only, unchecked |
| AMP–CO2–water; e | `kundu_et_al_2003_loading.csv` | 51 | T (K): 303–323; AMP Molarity: 2–3.4 | P_CO2 (kPa); CO2 Loading | CESAR-1 transcription only, unchecked |
| AMP–PZ–CO2–water; e | `brueder_CO2_partial_pressure.csv` | 49 | T (C): 40–120; AMP Molarity: 3–3; PZ Molarity: 1.5–1.5 | P_CO2 (kPa); CO2 Loading | CESAR-1 transcription only, unchecked |
| AMP–PZ–CO2–water; e | `dash_40_CO2_partial_pressure.csv` | 169 | T (K): 303–323; AMP Mass Fraction: 0.32–0.4; PZ Mass Fraction: 0–0.08 | CO2 Loading; P_CO2 (kPa) | CESAR-1 transcription only, unchecked |
| AMP–PZ–CO2–water; e | `dash_AMP_PZ_CO2_partial_pressure.csv` | 158 | T (K): 298–328; AMP Mass Fraction: 0.22–0.28; PZ Mass Fraction: 0.02–0.08 | CO2 Loading; P_CO2 (kPa) | CESAR-1 transcription only, unchecked |
| AMP–PZ–CO2–water; e | `hartono_CO2_partial_pressure.csv` | 43 | T (K): 313–353; AMP Molarity: 3–3; PZ Molarity: 1.5–1.5 | P_CO2 (kPa); P_CO2_uncertainty (kPa); CO2 Loading; CO2 Loading Uncertainty | CESAR-1 transcription only, unchecked |
| AMP–PZ–CO2–water; e | `hartono_P_total.csv` | 257 | T (K): 313–393; AMP Molarity: 0.5–4; PZ Molarity: 0.5–4; Calculated AMP Molality: 0.8–6.7; Calculated PZ Molality: 0.8–6.1 | P_total (kPa); P_total_uncertainty; CO2 Loading; CO2 Loading Uncertainty | CESAR-1 transcription only, unchecked |
| AMP–PZ–CO2–water; e | `hartono_P_total_second_dataset.csv` | 19 | T (K): 373–393; AMP Molarity: 3–3; PZ Molarity: 1.5–1.5 | P_total (kPa); P_total_uncertainty; CO2 Loading; CO2 Loading Uncertainty | CESAR-1 transcription only, unchecked |
| AMP–PZ–CO2–water; g | `hartono_dh_abs.csv` | 194 | temperature: 313–353; AMP molarity: 0.5–4; PZ molarity: 0.5–4 | dH_abs; dH_uncertainty; loading; loading_uncertainty | CESAR-1 transcription only, unchecked |
| AMP–PZ–CO2–water; e | `jahangiri_AMP_PZ_CO2_partial_pressure.csv` | 84 | PZ Molarity (mol/L): 0.1–0.3; PZ Molality: 0.12–0.5; AMP Molarity (mol/L): 1–4; AMP Molality: 1.12–6.73; T (K): 293–323 | CO2 Loading; P_CO2 (kPa) | CESAR-1 transcription only, unchecked |
| AMP–PZ–CO2–water; e | `li_AMP_PZ_CO2_loading.csv` | 78 | T (C): 20–160; T (K): 293–433; AMP Molality: 2.3–4; PZ Molality: 2–5 | CO2 Loading; P_CO2 (kPa) | CESAR-1 transcription only, unchecked |
| AMP–PZ–water; b | `hartono_AMP_PZ_H2O_VLE_data.csv` | 36 | T (C): 59.96–100.02; T (K): 333.11–373.17 | P (kPa); x_AMP; x_PZ | CESAR-1 transcription only, unchecked |
| AMP–water; b | `hartono_et_al_AMP_H2O_Txy.csv` | 26 | T (C): 59.97–100.02; T (K): 333.12–373.17 | P (kPa); x_AMP | CESAR-1 transcription only, unchecked |
| AMP–water; b | `pappa_et_al_AMP_H2O_Pxy.csv` | 21 | T (K): 364.45–418.05 | P (kPa); x_AMP | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; e | `derks_loading.csv` | 58 | molality_PZ: 0.2–0.6; temperature: 25–70 | loading; pressure_CO2 | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; e | `dugas_table_4_5.csv` | 43 | PZ_molality: 2–12; temperature: 40–100 | CO2_loading; CO2_partial_pressure | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; f | `ermatchkov_et_al_2003.csv` | 121 | temperature: 283.15–333.15; nominal_molality_PZ: 0.1–1.46 | moles_PZ_dissolved; moles_CO2_dissolved; moles_PZ_plus_deuterons; moles_monocarbamate; moles_bicarbamate | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; g | `hartono_table_15.csv` | 26 | temperature: 313–353 | dH_abs; dH_uncertainty; loading; loading_uncertainty | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; i | `hillard_PZ_Cp_concatenated.csv` | 102 | PZ_molality: 2–3.6; temperature: 39.9087–119.955 | CO2_loading; Cp_mass | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; e | `hillard_PZ_loading_concatenated.csv` | 56 | PZ_molality: 0.9–5; temperature: 40–60 | CO2_loading; CO2_partial_pressure | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; e | `hillard_figure_14-3-2.csv` | 14 | temperature: 40–60 | CO2_loading; CO2_partial_pressure | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; supporting PZ volatility in loaded solution | `hillard_figure_14-3-3.csv` | 30 | PZ_molality: 0.9–5 | CO2_loading; PZ_partial_pressure | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; supporting PZ volatility in loaded solution | `hillard_figure_14-3-4.csv` | 31 | PZ_molality: 0.9–5 | CO2_loading; PZ_partial_pressure | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; e | `hillard_figure_14-5-1.csv` | 9 | temperature: 40–60 | CO2_loading; CO2_partial_pressure | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; e | `hillard_figure_14-5-3.csv` | 11 | temperature: 40–60 | CO2_loading; CO2_partial_pressure | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; e | `hillard_figure_14-5-4.csv` | 11 | temperature: 40–60 | CO2_loading; CO2_partial_pressure | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; e | `hillard_figure_14-5-5.csv` | 11 | temperature: 40–60 | CO2_loading; CO2_partial_pressure | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; i | `hillard_figure_14_5_30.csv` | 51 | temperature: 39.9087–119.917 | CO2_loading; Cp_mass | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; i | `hillard_figure_14_5_32.csv` | 51 | temperature: 39.96–119.955 | CO2_loading; Cp_mass | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; i | `hillard_figure_14_5_34.csv` | 51 | temperature: 39.9684–119.986 | CO2_loading; Cp_mass | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; i | `hillard_figure_14_5_36.csv` | 51 | temperature: 39.9628–119.95 | CO2_loading; Cp_mass | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; e | `kamps_table_3.csv` | 94 | PZ_molality: 1.995–3.964; temperature: 313.13–393.15; CO2_molality: 0–5.369 | pressure_total | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; g | `liu_dH_abs.csv` | 58 | temperature: 40–80 | loading; dH_abs | CESAR-1 transcription only, unchecked |
| PZ–CO2–water; e | `xu_2011_table_1_PZ.csv` | 159 | PZ_molality: 4.93–8; temperature: 81–191.8 | CO2_loading; CO2_partial_pressure; pressure_total | CESAR-1 transcription only, unchecked |
| PZ–water; supporting unloaded Cp | `chen_et_al_2010_54_59_table_2.csv` | 44 | temperature: 303.2–353.2 | x_PZ; cp; cp_excess | CESAR-1 transcription only, unchecked |
| PZ–water; b | `hartono_et_al_2013_PZ_T_x_y.csv` | 24 | temperature: 59.95–100.03 | pressure; mole_frac_liq_PZ; mole_frac_vap_PZ | CESAR-1 transcription only, unchecked |
| PZ–water; b | `hillard_2008_figure_9_2_1.csv` | 35 | temperature: 113–199 | x_PZ | CESAR-1 transcription only, unchecked |
| PZ–water; b | `hillard_2008_figure_9_2_2.csv` | 42 | molality_PZ: 0.9–5; temperature: 32.7142–63.4095 | pressure_PZ | CESAR-1 transcription only, unchecked |
| PZ–water; supporting unloaded Cp | `hillard_2008_figure_9_2_3.csv` | 34 | molality_PZ: 2–3.6; temperature: 39.9751–119.958 | see source | CESAR-1 transcription only, unchecked |
| PZ–water; b | `nguyen_dissertation_2013_PZ_H2O_pressure_table_3_3_1.csv` | 7 | temperature: 40–70 | pressure_PZ; pressure_H2O | CESAR-1 transcription only, unchecked |
| PZ–water; b | `nguyen_dissertation_2013_PZ_H2O_pressure_table_5_3_3.csv` | 5 | temperature: 50–70 | pressure_PZ; pressure_H2O | CESAR-1 transcription only, unchecked |
| AMP–PZ–CO2–water; g | `hartono_table_18.csv` | 41 | temperature: 313–353 | dH_abs; dH_uncertainty; loading; loading_uncertainty | CESAR-1 transcription only, unchecked |

`hartono_table_15.csv`: PZ–CO2–water; stage (g), absorption heat. Its headers are dH_abs and associated uncertainty/loading fields; it is not a pressure dataset.

`hillard_figure_14-3-3.csv` and `hillard_figure_14-3-4.csv`: supporting PZ volatility data in loaded solution; the indexed observable is PZ partial pressure, not stage-(e) CO2 pressure.

Paper-checked measurement blocks comprise Hsieh Table 2, Hsieh Table 5, Tong Table 4, and Ciftja 2011 Table 2: four blocks from three papers. Hamborg supplies separately checked reaction-equilibrium evidence and is excluded from this four-block count. The 48 CESAR-1 CSV entries remain unchecked against their original papers.

## Missing papers, unread sources and source limits

Read-only live Zotero searches covered Ciftja, Hartono, Pappa, Jahangiri, Kundu, Dash, Brúder/Bruder, Ermatchkov, Hilliard, Nguyen, Ayad, Chen, Li and Liu, as well as AMP and piperazine titles. Project Companion search returned no AMP-specific curated source match; live library results were therefore checked. No items were added.

No matching original was found for these indexed sources: Ciftja 2011 and 2014; the Hartono AMP-water, PZ-water (2013), blend VLE and loaded-pressure/heat papers; Pappa AMP-water; Chen AMP loading and Chen 2010 PZ-water Cp; Dash AMP and AMP/PZ; Jahangiri AMP and AMP/PZ; Kundu 2003 (DOI 10.1021/je0201626); Brúder blend pressure; Ermatchkov, Pérez-Salado Kamps & Maurer 2003, *Chemical equilibrium constants for the formation of carbamates in (carbon dioxide + piperazine + water) from 1H-NMR-spectroscopy*, JCT 35, 1277–1289; the PZ-specific Kamps pressure paper; Xu 2011; Liu PZ absorption heat; Nguyen 2013 dissertation; Ayad et al. 2023, JC.E.D. 68, 2789–2806. Exact year/title/DOI resolution is still needed for the ambiguous filename leads, including Li's AMP/PZ data. An author surname alone does not establish bibliographic identity or absence.

The library's Hilliard thesis DNQUPRMT is the 2008 *A Predictive Thermodynamic Model for an Aqueous Blend of Potassium Carbonate, Piperazine, and Monoethanolamine for Carbon Dioxide Capture from Flue Gas*. It was found, but its PZ tables/figures were not checked here. Dugas/Rochelle 2011 is present as NDJWMT4H, DOI 10.1021/je101234t, **with correction TINYKLZD, DOI 10.1021/je400717h**. Check both before using the private table; the correction was not audited here. Tong, Hsieh, Hamborg and Pakravesh are present. Pakravesh's main paper was read; the numeric PC-SAFT supporting table was not independently verified from a local supplement.

Ciftja 2011 was read from the author's uploaded full text at [ResearchGate](https://www.researchgate.net/publication/251711690_Study_on_carbamate_stability_in_the_AMPCO2H2O_system_from_13C-NMR_spectroscopy), §§2–6 and Table 2. Ciftja 2014, DOI 10.1016/j.ces.2013.12.028, is a separate temperature-dependent study and remains missing/unread; its 57 private rows are not replaced by the 2011 table. The publisher fetch was unavailable. No new source file was retained.

The main-checkout literature shelf exists and was read-only. Baygi2015, Uyan2015, Wangler2018 and Pakravesh2025a copies match their indexed current Zotero Markdown SHA-256 values. Hsieh PDF 8X653CVB, Tong PDF 2SVMJQ58, Hamborg PDF 334KGLPV and Pakravesh PDF TTAMHITN were resolved through live Zotero. Paper text, not a source title or a prior answer, supports the checked rows. No measurement table is copied into this directory.

## Evidence standard inherited from #220

The DEA readiness review blocked execution for a wrong EOS family, circular reaction constants fitted to the same NMR data, unresolved pressure selection and too many free coordinates. The AMP design therefore cannot treat a SAFT-VR/CPA set as PC-SAFT, fit an apparent NMR constant as independent evidence, select a hold-out after fitting, or infer identifiability from a successful optimizer. See [design draft](design-draft-amp.md) for the remaining preparation gates.

## Closest modeling practice read for this draft

Baygi & Pahlavanzadeh 2015 (DOI 10.1016/j.cherd.2014.07.017), pure-parameter and binary/ternary VLE results, Tables 2–3: PC-SAFT pure MEA association alternatives are fitted to saturation data and binary interactions to unloaded VLE; loaded pressure is then compared without ternary fitting. That study uses ideal chemical speciation and does not establish transfer of the present Born/electrolyte model. Uyan 2015 (DOI 10.1016/j.fluid.2015.02.026), §4, Tables 1,3–4, uses explicit species activities and source reaction laws for MDEA. Wangler 2018 (DOI 10.1016/j.fluid.2017.12.033), model/parameter-estimation and results sections, fits selected ion–water interactions to osmotic coefficients and compares gas solubility/heat outside that fitted property. These papers use different fitted information and domains; none supplies an AMP acceptance tolerance. The source-family/convention checks follow that distinction; the frozen shared species and phase classifier are repository choices, not a literature consensus. No numerical AMP pressure acceptance limit is adopted. Pakravesh 2025 §2.2 and the results/conclusions compare neutral pure/binary/ternary properties across EOS families; they do not establish reactive AMP/PZ pressure or ion parameters.
