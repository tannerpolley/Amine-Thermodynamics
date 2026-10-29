# Candidate AMP CO2 partial-pressure campaigns

Issue #229, 2026-10-29. Recommend reserving **all Kundu et al. (2003)
Tables 1–3** as one campaign, subject to owner approval of its pressure-error
treatment and pass limit. Do not use it for calibration, ion selection,
coordinate selection, bounds or starts. Reading/transcribing the published
observations here is preparation; no candidate model has been scored.

| Candidate and primary locator | Conditions and observation basis | Uncertainty and admission |
|---|---|---|
| Kundu, Mandal & Bandyopadhyay 2003, DOI [10.1021/je0201626](https://doi.org/10.1021/je0201626), Experimental pp.789–790, Tables 1–3 p.790 | 18,25,30 mass% stock AMP (nominal 2.0,2.8,3.4 mol/L); T=303,313,323 K, with only 303 K for 2 M. Measured CO2 partial pressure in kPa and loading mol CO2/mol AMP. Atmospheric total pressure; gas chromatography measures equilibrium gas composition; acidulation/evolved gas measures loading. 51 pairs: 7+25+19. Actual table range 3.20–94.0 kPa and loading 0.412–0.966. | T measurement ±0.1 K, control ±0.2 K; total-pressure accuracy ±0.2 kPa; loading method accuracy ±2%, reproducibility within 2%, estimated solubility error about ±2%. These are not a stated combined uncertainty for pCO2. No gas-composition calibration uncertainty was found in the Experimental section. Pressure scale remains to be approved. Original PDF and tables verified. |
| Dash, Samanta & Bandyopadhyay 2011, DOI [10.1016/j.jct.2011.03.016](https://doi.org/10.1016/j.jct.2011.03.016), JCT 43,1278–1285, publisher abstract | 298–328 K; pCO2 about 0.4–1500 kPa; aqueous AMP 2.2–4.9 mol/dm³. Abstract explicitly identifies CO2 partial pressure. | Full methods/tables and uncertainty not obtained or checked. Loading denominator and stock/loaded concentration convention remain unverified. Candidate only; no rows transcribed. Shares authors with Kundu, so apparatus/data overlap must be checked before treating the two as independent blocks. |
| Pahlavanzadeh, Nourani & Saber 2011, DOI [10.1016/j.jct.2011.05.032](https://doi.org/10.1016/j.jct.2011.05.032), JCT 43,1775–1783, publisher abstract | 293–323 K; pCO2 17.47–69.87 kPa; AMP 1–4 M; measured loading reported in abstract. | Full methods, exact loading/concentration bases and uncertainty unverified. Candidate only. This exact title/DOI is not assigned to the unresolved Jahangiri filename lead. |
| Hartono et al. 2021, DOI [10.1016/j.fluid.2021.113235](https://doi.org/10.1016/j.fluid.2021.113235), *New solubility and heat of absorption data…* | Existing public scoping map lists AMP partial-pressure and separate total-pressure leads; paper identity resolved, exact measurement tables not read here. | Conditions and uncertainties remain the explicitly unchecked leads in `../data-map.md`; none is upgraded from that inventory. Proposed calibration source, so prefer another campaign for the primary test. |
| Chen and Jahangiri filename leads in `../data-map.md` | Bibliographic mapping to exact original measurement paper still unresolved. | No claim of verified conditions, pressure basis or uncertainty; no acquisition or transcription. |

Tong 2012 Table 4 remains a separate **total-pressure** comparison; it is not
eligible as a measured CO2 partial-pressure campaign. A model-subtracted
solvent pressure does not change the measurement's identity.

## Selected transcription and recommendation limits

`kundu-tables-1-3.csv` transcribes the public PDF, p.790 (PDF page 2), checked
visually against the page. It retains table/isotherm/row identity and the
printed precision. Stock mass percentages come from the abstract p.789;
nominal molarities are table labels. No density-based conversion is performed.
The complete source campaign is recommended, including all concentrations;
if a temperature/composition restriction is adopted later, record it before
fitting and keep the unused rows outside model selection.

Its temperatures lie within the measured Hamborg range, and its 30 mass%
stock overlaps the intended AMP solvent. Kundu reports its own experimental campaign and is recommended as a candidate whole-campaign hold-out. Independence from the eventual Hartono calibration packet remains to be verified when its source rows and measurement provenance are admitted.

A cross-paper duplicate check is still required on the eventual calibration packet. The 51 table rows
are observations, not 51 statistically independent experiments.

The ±2% statement concerns solubility/loading. It must not be used as a 2%
relative pCO2 uncertainty or adopted as a model-accuracy limit. Freeze the
pressure metric, residual scale, loading-error treatment and numerical limit
with the owner before fitting. This recommendation neither transfers the
MEA/MDEA 24.2% limit nor claims physical validation of an AMP model.

Zotero selected campaign: new parent `BRW2JUBY`, verified 8-page PDF `33276JDA`.
The other candidates were not added; acquisition approval was limited to the
selected campaign. Their abstracts support discovery only.
