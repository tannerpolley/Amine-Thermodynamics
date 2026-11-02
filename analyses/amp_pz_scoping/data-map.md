# AMP, PZ and blend source inventory

Research snapshot for [#227](https://github.com/tannerpolley/Amine-Thermodynamics/issues/227), 2026-10-29. This is a candidate-source inventory, not fit admission.

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

## Paper-checked measurement blocks

| Subsystem; stage | Published source and exact locator | Conditions and basis | Count | Check |
|---|---|---|---:|---|
| AMP–water; c | Hsieh, Chen & Li 2007, DOI 10.1021/je600515j, Table 2 p.620 | pure AMP, 303.15–328.15 K; relative permittivity | 6 | checked against the paper (Table 2, PDF 8X653CVB) |
| AMP–water; c | Hsieh 2007, Table 5 p.622 | unloaded x(AMP)=0.2,0.4,0.6,0.8 at six temperatures, 303.15–328.15 K | 24 | checked against the paper (Table 5, PDF 8X653CVB) |
| AMP–CO2–water; e | Tong et al. 2012, DOI 10.1016/j.ijggc.2011.11.005, Table 4 p.43 | 30 mass% unloaded AMP; five isotherms 313.2–393.2 K; **total** P, loading mol CO2/mol AMP; solvent-vapor baseline rows included | 45 total: 40 loaded + 5 unloaded baselines | checked against the paper (Table 4 and §2; PDF 2SVMJQ58); do not call P partial pressure |
| AMP–CO2–water; f | Ciftja et al. 2011, DOI 10.1016/j.egypro.2011.01.096, Table 2 p.618 and §2 | 30 wt% stock AMP, 25 °C; loading 0–0.62 mol CO2/mol AMP; NMR mole fractions, added D2O/internal standard | 7 including unloaded row | checked against the paper (Table 2, author-uploaded full text) |
| AMP–water; b | Hartono, Saeed, Ciftja & Svendsen 2013, DOI 10.1016/j.ces.2013.01.015, Table 3 p.154; method §2 p.152 (Zotero `5KUR8PRH`, PDF `SEPZQIPE`; added under #240) | Ebulliometer P–T–x–y at 59.97–100.02 °C (9/6/11 rows at 60/80/100 °C); total amine in liquid and vapor condensate by acid titration; x_AMP 0.0228–0.3023, y_AMP 0.0023–0.0309, P 15.1–98.9 kPa | 26 | checked against the paper (#240, [PZ source note](../pz_scoping/sources/derks-2005-hartono-2013.md#amph2o-table-3-p154)) |
| AMP–PZ–water; b | Hartono 2013, Table 9 p.159; ¹H-NMR AMP/PZ ratio plus titration (§2.3–2.4, p.152) | Ebulliometer P–T–x–y at 60, 70, 80, 90, 100 °C (7/8/7/7/7 rows); x_AMP 0.0116–0.0992, x_PZ 0.0101–0.0474, P 17.0–98.5 kPa; y_PZ 0.0001–0.0043 | 36 | checked against the paper (#240). Two y_PZ values sit at the 0.0001 NMR detection limit; one 80 °C row has k_PZ about four times its neighbours; the authors call the vapor data scattered (p.160) and miss γ_PZ by 41–47 % (Tables 10, 12). Usable observables: y_AMP and P; y_PZ supporting only |

Hsieh methods p.619 specify composition uncertainty ±1.5×10⁻4 mole fraction; Table 2 gives replicate standard deviations, not a blanket expanded uncertainty. Tong §2.3 reports loading repeatability below 1.5% and discusses systematic error; those are not a universal pressure residual scale. Ciftja separates overlapping protonation signals with pH and literature constants: split species are model-assisted, not independent NMR observations.

AMPH+ dissociation: use Hamborg & Versteeg 2009 Table 1 (p.1320), the correlation form ln K = A/T + B + C ln T in Eq.21 (p.1319), and the 24 AMP experimental runs in Table 16 (p.1325). Table 4 describes DMMEA; Eq.35/Table 15 do not provide the AMP dissociation law. The source uses hydronium, explicit water activity, and an infinite-dilution molality standard state. Transcribe the AMP measurements and establish the numerical correlation and its uncertainty before adoption. Document the mapping into the Engine reaction-reference convention, including water factors, standard pressure, direction, and temperature domain; verify source reference values and reciprocal constants for reversed reactions.

Hamborg & Versteeg 2009: DOI 10.1021/je800897v; parent D9KXSKLR, PDF 334KGLPV. PZ Tables 9, 10 and 16 require an explicit group-to-reaction mapping checked against named stoichiometry; that mapping remains unresolved. These reaction-equilibrium measurements are excluded from the four measurement-block count.


Paper-checked measurement blocks comprise Hsieh Table 2, Hsieh Table 5, Tong Table 4, Ciftja 2011 Table 2, and (added under #240) Hartono 2013 Tables 3 and 9: six blocks from four papers. Hartono 2013 Table 6 (PZ–water, 24 rows) is recorded in the [PZ data map](../pz_scoping/data-map.md). Hamborg supplies separately checked reaction-equilibrium evidence and is excluded from this four-block count.

## Missing papers, unread sources and source limits

Read-only live Zotero searches covered Ciftja, Hartono, Pappa, Jahangiri, Kundu, Dash, Brúder/Bruder, Ermatchkov, Hilliard, Nguyen, Ayad, Chen, Li and Liu, as well as AMP and piperazine titles. Project Companion search returned no AMP-specific curated source match; live library results were therefore checked. No items were added.

No matching original was found for these sources: Ciftja 2011 and 2014; the Hartono blend loaded-pressure/heat papers (the AMP-water, PZ-water and AMP–PZ–water VLE paper, Hartono 2013, has since been read under #240); Pappa AMP-water; Chen AMP loading and Chen 2010 PZ-water Cp; Dash AMP and AMP/PZ; Jahangiri AMP and AMP/PZ; Kundu 2003 (DOI 10.1021/je0201626); Brúder blend pressure; Ermatchkov, Pérez-Salado Kamps & Maurer 2003, *Chemical equilibrium constants for the formation of carbamates in (carbon dioxide + piperazine + water) from 1H-NMR-spectroscopy*, JCT 35, 1277–1289; the PZ-specific Kamps pressure paper; Xu 2011; Liu PZ absorption heat; Nguyen 2013 dissertation; Ayad et al. 2023, JC.E.D. 68, 2789–2806. Exact year/title/DOI resolution is still needed for the unresolved sources, including Li's AMP/PZ data. An author surname alone does not establish bibliographic identity or absence.

The library's Hilliard thesis DNQUPRMT is the 2008 *A Predictive Thermodynamic Model for an Aqueous Blend of Potassium Carbonate, Piperazine, and Monoethanolamine for Carbon Dioxide Capture from Flue Gas*. It was found, but its PZ tables/figures were not checked here. Dugas/Rochelle 2011 is present as NDJWMT4H, DOI 10.1021/je101234t, **with correction TINYKLZD, DOI 10.1021/je400717h**. Check both before using the published table; the correction was not audited here. Tong, Hsieh, Hamborg and Pakravesh are present. Pakravesh's main paper was read; the numeric PC-SAFT supporting table was not independently verified from a local supplement.

Ciftja 2011 was read from the author's uploaded full text at [ResearchGate](https://www.researchgate.net/publication/251711690_Study_on_carbamate_stability_in_the_AMPCO2H2O_system_from_13C-NMR_spectroscopy), §§2–6 and Table 2. Ciftja 2014, DOI 10.1016/j.ces.2013.12.028, is a separate temperature-dependent study. It was missing here and has since been read in #238 ([source note](sources/ciftja-2014.md)); its SI Tables S1–S3 are transcribed publicly, and the 2011 table is recommended for exclusion. The publisher fetch was unavailable. No new source file was retained.

The main-checkout literature shelf exists and was read-only. Baygi2015, Uyan2015, Wangler2018 and Pakravesh2025a copies match their indexed current Zotero Markdown SHA-256 values. Hsieh PDF 8X653CVB, Tong PDF 2SVMJQ58, Hamborg PDF 334KGLPV and Pakravesh PDF TTAMHITN were resolved through live Zotero. Paper text, not a source title or a prior answer, supports the checked rows. No measurement table is copied into this directory.

## Evidence standard inherited from #220

The DEA readiness review blocked execution for a wrong EOS family, circular reaction constants fitted to the same NMR data, unresolved pressure selection and too many free coordinates. The AMP design therefore cannot treat a SAFT-VR/CPA set as PC-SAFT, fit an apparent NMR constant as independent evidence, select a hold-out after fitting, or infer identifiability from a successful optimizer. See [design draft](design-draft-amp.md) for the remaining preparation gates.

## Closest modeling practice read for this draft

Baygi & Pahlavanzadeh 2015 (DOI 10.1016/j.cherd.2014.07.017), pure-parameter and binary/ternary VLE results, Tables 2–3: PC-SAFT pure MEA association alternatives are fitted to saturation data and binary interactions to unloaded VLE; loaded pressure is then compared without ternary fitting. That study uses ideal chemical speciation and does not establish transfer of the present Born/electrolyte model. Uyan 2015 (DOI 10.1016/j.fluid.2015.02.026), §4, Tables 1,3–4, uses explicit species activities and source reaction laws for MDEA. Wangler 2018 (DOI 10.1016/j.fluid.2017.12.033), model/parameter-estimation and results sections, fits selected ion–water interactions to osmotic coefficients and compares gas solubility/heat outside that fitted property. These papers use different fitted information and domains; none supplies an AMP acceptance tolerance. The source-family/convention checks follow that distinction; the frozen shared species and phase classifier are repository choices, not a literature consensus. No numerical AMP pressure acceptance limit is adopted. Pakravesh 2025 §2.2 and the results/conclusions compare neutral pure/binary/ternary properties across EOS families; they do not establish reactive AMP/PZ pressure or ion parameters.

## Update for #240 (2026-11-02)

Hartono 2013 is one paper with three ebulliometer blocks: PZ–water (Table 6), AMP–water (Table 3) and AMP–PZ–water (Table 9). For AMP–water, the uncertainty comes from the same apparatus in Kim et al. 2008 (Zotero `97LARJKT`): T ±0.05 K and P ±0.3 kPa (p.2526), titration repeatability better than 1 % (p.2528). Hartono's own AMP vapor pressure is an Antoine fit to literature data (Eq. 2, p.152), not a measurement; score y_AMP·P and P, not γ. Fosbøl et al. 2011 (Zotero `BXZRGU3H`, added) holds unloaded AMP–water (Table 2, p.5091) and AMP–PZ–water (Table 3, p.5092) freezing points and solubilities; Hartono fitted 14 AMP points from it. Its tables were not transcribed. No AMP or blend role is proposed here; the AMP draft keeps its own data roles.
