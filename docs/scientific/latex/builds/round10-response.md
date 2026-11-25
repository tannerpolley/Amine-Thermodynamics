# Round-10 referee comments: response

Manuscript: “Thermodynamics of CO₂-loaded aqueous amines with ePC-SAFT: monoethanolamine calibration, transfer to DEA, MDEA and AMP, and phase stability”, branch `issue-429-story-pass`, issue #429.

Locators refer to the PDFs built in this revision (main text 32 pages, supplement 64 pages). “S” numbers are supplement sections and tables. Status words: **Addressed**, **Partly**, **Open**.

Evidence: the round-10 study (`analyses/round_10/manuscript-handoff.json` and `notebook.qmd`, commit `609adcc26`). **Promotion is not yet given.** On 2026-11-25 the investigator was asked to promote that commit for this pass and answered “keep working on this”. The investigator also directed that failing calculations must not appear in the manuscript as if they were acceptable (see “Owner direction” below). The K1–K4 text is drafted on the unmerged branch from those records and must not be treated as accepted until promotion. No calculation was run in this pass, and no generated display or script was edited.

## Owner direction (new, open)

On 2026-11-25 the owner rejected the word “provisional” for the MDEA fit, and the reporting of 62 of 63 drawn MDEA starts as failed evaluations, without a diagnosed cause. The owner asked why the bubble calculations fail.

The #440 records (`analyses/fixed_reaction_reference/notebook.qmd`, “MDEA fit limits” and “Replacement starts”) give only failure categories:
- **Starts B and C:** at the Merkley 1.121 MPa state, B gives bubble pressures of 24.4–186.6 kPa at all 30 loading nodes, and C gives more than 1,962 kPa at every admitted node.
- **60 replacement draws:**
  - 28 equilibrium solves stopped without converging (`LOCAL_INFEASIBILITY`, “contraction absent”);
  - 24 saturation searches found no admissible root (loading 1.05, no resolved root, or slope reversal);
  - 5 stopped at the iteration limit;
  - 3 were ill-conditioned.
- **LHS-53** was the only evaluable draw.

The notebook records “feasibility undecided”. It is not established whether these are solver failures or parameter sets that have no root at those states. Finding out is a diagnosis stage, not Writer work. Until it is done, the MDEA wording stays as drafted: “provisional” appears 12 times in the prose and 8 times in generated tables. That wording does not meet the owner's direction.

## Calculations and displays

| Item | Status | Response and locator |
|---|---|---|
| K1 Endpoint spread | Partly (MDEA open per owner direction) | **§4.2.4, new last paragraph; Table S51; §S4; §5.4; Conclusions.** Across the tied endpoints, AARD differs by at most 0.0004 percentage points (MEA; A, B, LHS-21), 0.0014 (DEA; A, B, C) and 0.0002 (AMP; A, LHS-06, LHS-45). On the same rows the reported endpoint deviates from the measurements by 0.6–206 %. Each difference is more than 1,000 times smaller than the deviation; the smallest ratio is 1,468, for the single Hilliard row. The largest single-row change is 0.0036 % of the measured value. MDEA: both A continuations agree with A within 0.0002 percentage points on Kuranov, Ermatchkov and Carson. LHS-53 is reported as a separate basin (objective 48386.5 against 15.609; Kuranov 64 %, Carson 320 %), not as a competing fit. S4 says that the 59.6 and 307 percentage-point MDEA spreads measure the distance to that basin. §5.4: parameter uncertainty remains unquantified. |
| K2 MEA parents, AMP outcomes | Addressed | **§4.3 (first paragraph) and §S7:** 2,484 liquid states with one unfinished search. At the 162 L–V states, 149 pass as liquid plus vapor and 13 as one liquid. The measured screen finished 246 of 321. The AMP per-control categories are in Table 9 (rebuilt display) and §4.3: none of the six has a confirmed second liquid. Four are vapor-directed: Hartono r9 passes L+V, and three keep the unlabelled vapor root. Two have no descent. The same wording is in the abstract, Fig. 8 caption, §S7 (Table S43 text), the conclusions and the cover letter. |
| K3 DEA bulk density | Addressed | **§4.3 DEA paragraph and §S7:** one liquid gives 0.113 %, and two liquids combined with additive volumes give 0.155 % (Table S48). Both reproduce the measured densities, and the two-liquid result is not closer, so density cannot tell the cases apart. 101.325 kPa is called the assigned pressure in §4.3 and §S7. The α = 0.50 restart and neighbor-start tests are stated to hold at the reported endpoint only. “The density measurements do not establish the number of phases” is kept. |
| K4 MDEA bubble pressures | Addressed (drafted) | **§4.3 MDEA paragraph and §S7:** at 8 of the 10 measured-pressure descents (Zheng rows 1 and 3–5 and the four Sobrino states) the model bubble pressure exceeds the imposed pressure. Examples are Zheng 5 at 7.48 against 2.57 MPa and Sobrino at 0.19 against 0.100 MPa. There a vapor-directed descent is the expected partial vaporization. This is stated as support, not proof. Zheng 2 is borderline (1.194 against 1.190 MPa). Zheng 6 (4.19 MPa) was refused as infeasible, with scaled residual 0.100 against 10⁻¹⁰, and is unevaluated. §S7 states that the 17 assigned-pressure states were not recalculated. |

## Text items

| Item | Status | Locator |
|---|---|---|
| AMP wording everywhere | Addressed | Abstract; §4.3; Fig. 8 caption; §S7; Conclusions; cover letter; preprint abstract. Table 9 already carried the categories. |
| §4.2.4 order, weighting, convention, stopping | Partly | §4.2.4 now opens with the matched 100 kPa same-weight comparison (Table S49). It states its weights and bounds and its stopping: the MEA alternative stopped on function tolerance; the MDEA alternative stopped at the iteration limit, with projected gradient 0.012. The Table 8 comparison fits follow, with the system-pressure convention and the weighting of each. **Open:** the stopping status of the system-pressure comparison fits of Table 8 is not in any promoted record, so it is not stated. |
| Table 7 MDEA standard errors | Partly | §4.2.2 now says that the MDEA standard errors are local Jacobian sensitivities at the endpoint. The Table 7 note is generated (D1). The owner direction may change this wording. |
| §5.2 row-aligned lead and roles | Addressed | §5.2 opens with Ma'mun (19 rows) and Ermatchkov (101 rows) and gives the fit or development role of each model. The Ermatchkov data helped choose the initial MDEA parameters, so that comparison is not a blind test. |
| Kuranov count-matched values | Addressed | §5.2, second paragraph: 4.35 % matched by row. The published values are listed unranked and identified by count only. |
| Kamps 27 vs 28 | Addressed | §5.2: the published sets give 1.9 and 3.5 % on 28; the MDEA model gives 14.76 % on the same 28 and 11.93 % on 27, with the 28th row identified. |
| DEA H^E sign in §5.2 | Addressed | §5.2, AMP/DEA paragraph: Horstmann et al. fitted H^E and bubble pressures together and report no deviation, so the comparison is one of sign. The measured H^E are negative, and the DEA model gives positive values. |
| Smith et al. | Addressed | §5.2, last paragraph, citing `smithGibbsEnergyMinimization`. Read in the Zotero PDF (key BUWD3C5J, attachment NMDERX46): §4.3 gives exact conversions of K and μ° across molality, mole-fraction and molarity (Eqs. 34–37); §7 says that co-fitting K or standard-state properties with activity parameters to the same pCO₂ data gives non-unique, compensating parameterizations. The text links this to the common molality basis (§2.3) and to the DEA R4/carbamate correlation of 0.976. The Zotero record was corrected (title markup, journal, ISSN) and filed in the project collection; `references.bib` was regenerated and gained only this entry. |
| Abstract Ermatchkov denominator | Addressed | Abstract: “29.21 % from 101 unfitted Ermatchkov CO₂ partial pressures”. |
| Resolution vs observed difference | Addressed | Abstract: the difference is at most a relative 1.4×10⁻⁵, at resolutions of 0.12–10.5 %. §2.3 gives +1.40×10⁻⁵ for MEA, −3.77×10⁻⁶ for DEA and below 10⁻⁷ for AMP and MDEA, against 10.5, 8.9, 0.46 and 0.12 %. The conclusions say that the MEA and DEA checks exclude only larger differences. |
| AMP enthalpy check reference | Addressed | §2.4: for AMP the check uses neutral caloric reference functions declared zero, and a constant shift of that reference changes both enthalpies alike. Source: the round-8 notebook, where a 1000 J/mol shift leaves the residual unchanged within 2.2×10⁻⁶ J/mol, and the gauge in `reference_derivatives.py`. |
| Deposit ID vs source row | Partly | The availability statement says that deposit ID 32 is processed source row 33 (IDs zero-based) and that source row 32 is the adjacent unresolved state at α = 0.45. Table S48 already gives both. The deposit README fix is on `main` at `17c122356`, which is **not merged** into this branch. |
| Carbonate ratio 0.070 | Addressed | §5.3, electrostatic paragraph. |
| C1 name; wheel first | Addressed | The availability statement names “the Gibbs pressure- and temperature-derivative check” (the only place “C1” appeared) and now lists the archived wheels before the parameter vectors, the examples and the public release. “Manifest” became “checksum list”. |
| Eq. 17 definitions | Addressed | §3.4 after Eq. 17: g = G*/n on the true-species basis. w_i > 0 applies to the species allowed in the trial phase. Liquid trials also satisfy the reaction equilibria of Eq. 7, which do not arise in a neutral vapor. |
| Highlight 1 | Addressed | “MEA ePC-SAFT water, CO₂ and inorganic-ion parameters held fixed for DEA, MDEA and AMP” (85 characters). |
| Kiepe labels | Partly | §3.1 states that the 39 Kiepe pressures were fitted beforehand and are a constant contribution, leaving 268 responsive of 307. This agrees with §3.3 and §S4. The Table 4 role cell “fitted” is generated (D2). |
| Fig. 7 bracket | Addressed | In §4.3 and the Fig. 7 caption, 1.466 MPa now sits with the onset bracket, described as the numerical resolution of the binary calculation. |

## Display requests

| ID | Display | Request |
|---|---|---|
| D1 | Table 7 note | Describe the MDEA standard errors as local Jacobian sensitivities at the reported endpoint. Wording depends on the owner direction above. |
| D2 | Table 4, Kiepe row | Role “fitted beforehand; constant in objective” instead of “fitted”, matching Table 2. |
| D3 | “Provisional” labels | Eight cells or notes in Tables 8 and 10 and S31, S38, S42 and the MDEA weighting table. Change them after the MDEA diagnosis decides the wording. |
| D4 | Table S49 caption | “historical MEA-fitted shared interactions” uses development wording that STYLE.md excludes. Use “MEA-fitted shared interactions”. |
