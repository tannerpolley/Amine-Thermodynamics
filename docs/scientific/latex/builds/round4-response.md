# Round-4 referee comments: response

Manuscript: “Thermodynamics of CO₂-loaded aqueous amines with ePC-SAFT: monoethanolamine calibration, transfer to DEA, MDEA and AMP, and phase stability”, branch `issue-429-story-pass`, issue #429.

Locators refer to the built PDFs of this revision: main text (27 pages) and supplement (47 pages). “S” numbers are supplement sections, tables and figures.

Status words: **Addressed** (changed as asked), **Partly** (changed, with a stated remainder), **Open** (not done, with the reason), **Not adopted** (declined, with the reason).

## What changed in this revision

1. **The reported models are the adopted #435 models.** The shared water–bicarbonate and water–carbonate interactions are fixed from sodium-salt osmotic coefficients (Peiper and Pitzer), so no amine data determine them (Section 2.2, S1.3). The fits made with the interaction fitted to the MEA data (0.765 ± 3.18) are kept as the comparison, called the “MEA-fitted shared set” (Table 8, Section 4.2.4).
2. **The AMP model fits all 105 loaded total pressures**, 313–393 K, with the cation–water temperature slope fitted (−52.0 ± 63 K). The earlier fit to 47 pressures, and the fit with the slope fixed at −150 K, are no longer reported models. The splits of the first fit are reported as one finding in Section 4.3.
3. **The story is unchanged**: MEA calibration, transfer to DEA, MDEA and AMP, phase stability. The question “do near-equal fits predict different phases” is no longer the frame, and no general claim of that kind is made.
4. **The main text is shorter**: 33 → 27 pages, and 11,016 → 9,065 words in the six body sections. Repeated caveats are kept in Section 3.1 and Section 5.4 only.
5. **Three calculations asked for by several referees are still open** by owner decision: the multistart study (#427), the refits with the shared parameters released (#424), and the public data deposit (DOI placeholder). They are named as limits in Section 5.4.

## Astra (4/5, minor revision)

| # | Comment | Status | Response and locator |
|---|---|---|---|
| M1 | Put the equal-pressure AMP comparison (14/15 against 0/15) in the abstract, beside the 73 count; reserve “no instability” for the protocol. | Partly | The pair of fits to 47 pressures is no longer the headline, so the 14/15 comparison is not in the abstract. The equal-pressure test is kept in the form that covers every AMP fit: at 2.037 MPa, above the bubble pressure of all six fits at the worked feed, the first fit splits and none of the other five does (S7.3, Table S30). “No detected instability” is used only for a finished search under the stated protocol (Section 3.4, Section 4.3). |
| M2 | Section 5.4 “model form rather than data” overclaims for the MDEA bound; narrow it to the adopted parameters and starts. | Addressed | The phrase is removed. Section 5.3 now reads “With the adopted MDEA pure-component and association parameters and the starts tried, a fit without the bound converged inside a calculated liquid–liquid gap”. |
| M3 | Explain the assumption that the R1–R3 reference states move with the system pressure, especially for the 203 and 262.9 MPa MDEA splits. | Partly | Section 2.3 states the convention and that all phases compared at one state share one Gibbs energy. S3 gives the recalculation with the references at 0.1 MPa: the AMP worked split (1.212 MPa) and the MDEA split at 1.121 MPa persist; the MDEA split at 203.1 MPa is not confirmed with that convention, so at that pressure the convention is not shown to be immaterial. The comparison was not made for the 121.3 MPa split of the MDEA model (stated in S3). |
| m1 | Table 10 MDEA zero: add the 262.862 MPa split; attach “far above measured” to 203.1 MPa only. | Addressed | Table 8 (the former Table 10) reports one confirmed liquid–liquid split for the MDEA model, at 121.3 MPa. Section 4.3 and S7.1 give its state and say it is about 29 times the highest measured pressure. The 262.862 MPa state belongs to the fit with the MEA-fitted shared set and is unresolved for the MDEA model (Table S30). |
| m2 | “Well determined” → “small conditional standard error”; give 1.023 as the actual objective increase. | Addressed | “Well determined” no longer occurs. Table S24 gives the objective changes 1.023 and 0.024, and S4.1 defines the reference change (2.24, nominal). |
| m3 | One MEA limitation in the abstract. | Addressed | Abstract, third sentence: “its pressures at other concentrations and at stripper temperatures are less accurate”. |
| m4 | Table 11 Kuranov block is count-matched; Hong caveat. | Addressed | Section 5.2: “The published values are identified with these 82 observations by their count only”. The Hong caveat (1.53 % is a fit to simulator pressures) is in Section 5.2; the stability count is in S9. |
| m5 | DOI placeholder; locator for the AMP and MDEA parameter vectors. | Open / Partly | The DOI stays a placeholder until the deposit is made (owner decision). The Data availability section now says which parameter vectors the deposit holds; Table 7 and Table S5 give the values. |
| Data 3→4 | One table of start-by-start results for the headline fits. | Partly | Table S23 lists, for every start of the four fits and of the AMP sensitivity fit, the objective at the start and at convergence. Active bounds are in Table 7 and Table S19. The origin of each starting set is not tabulated; Section 3.3 says the two MEA starts descend from the 16-parameter calibration. |

## Sol (3/5, major revision)

| # | Comment | Status | Response and locator |
|---|---|---|---|
| M1 | Pressure-dependent R1–R3 reference: one potential or a family of fixed-pressure calculations? Its derivative in volume and enthalpy; repeat the fixed-reference comparison at the AMP worked split, the MDEA 1.121 MPa split and one split above 200 MPa. | Partly | The three recalculations were made (#434) and are reported in S3: two splits persist, the 203.1 MPa split is not confirmed. S3 states that either convention gives one composition-independent set of reference potentials at fixed temperature and pressure, and that the choice changes how that set varies with pressure. Its contribution to the volume is not quantified; the effect on one integral heat is given (−81.795 → −81.850 kJ/mol). |
| M2 | Dispersed starts for MEA and the AMP slope; per-observable objective contributions and deviations for both AMP fits, with outside-fit p(CO₂). | Partly / Open | Contributions: Table S13, all four models. AMP deviations by source for the AMP model: Section 4.2.3, Table S11; for the four fits to all loaded pressures: Table S29. A profile of the AMP slope is in S7.3 (made with the MEA-fitted shared set only). Dispersed starts are not done (#427, open by owner decision; Section 5.4). |
| M3 | Paired AMP calculation above both bubble pressures; search starts, root selection and acceptance criteria; map the unfinished MDEA searches against the experimental domain; fixed-pressure recovery; lowest Gibbs energy among combinations. | Partly | Paired calculation: 2.037 MPa (S7.3, Table S30). Unfinished MDEA searches: 1,248 of 11,824, of which 1,026 at grid states and 222 at measured states, by cause (Section 4.3, S7.1). Acceptance tests: S7.1; a confirmed split requires two distinct liquids of lower Gibbs energy (Section 3.4). Not done: fixed-pressure recovery of the unfinished searches near measured conditions, and a comparison of every phase combination at each state. Both are stated: “222 of its 1564 searches at measured states give no result”. |
| M4 | MDEA sensitivity to the water–bicarbonate interaction: p(CO₂) by source and temperature; what else changed; do not claim the cost of fixing the shared set. | Partly | The claim is replaced by a direct paired comparison of two shared sets on identical observations (Table 8, Section 4.2.4), with the 101 Ermatchkov pressures named: 17.9 → 38.4 %. Xiao et al. (20) is in Table S11. The earlier test at 0.1325 and 1.0 is in S4.1 with what was fixed and refitted in the note of Table S24. A split by temperature is not given. |
| M5 | DEA: exact temperature law, bounds and weights of the binary refit; show the refit; or state it as two fits only. | Partly | Stated as two fits only (Section 4.2.1, S2.5). S2.5 gives the law (reciprocal-temperature form, −0.0870 at 365.15 K, coefficient −32.25 K) and Table S14 the deviations of both fits. The bounds and weights of the refit are not listed, and the refit is not drawn in Fig. S7. The comparison was not repeated with the salt-fixed interactions (stated). |
| M6 | Yi et al. 2024 Table 4; Hartono et al. 2020; Kuranov rows provisional; Hong caveat. | Addressed | Section 5.2 and S8 add Yi et al. (15.4 % on 51 Kundu pressures; 8.0 % on 45 Tong pressures) and Hartono et al. 2020 (17.3 and 9.3 %), both fitted to those data, beside 15.6 and 10.5 % for the AMP model. The 45 Tong pressures of Yi et al. are the 40 loaded and five CO₂-free pressures used here (round-5 literature check of the source tables). Kuranov: count-matched only (Section 5.2). Hong: Section 5.2. |
| M7 | Reviewer-accessible deposit with vectors, bounds, starts and state-level search outcomes. | Open | The deposit is not public yet (DOI placeholder, owner decision). Vectors: Tables 3, 4, 7, S5; bounds: Tables S19, S22; starts: Table S23. State-level search outcomes are in the retained records that the deposit will carry. |
| m | “73 in reported searches”, 363.15–393.20 K. | Addressed | Section 4.3 (“among the same 666 states”, 363–393 K); S7.3 gives 363.15–393.20 K. |
| m | 353.22 against 353.00 K. | Addressed | 353.22 K is the upper limit of the measured R5 range of AMP (Table 1); the fitted pressures of the first fit end at the 353 K isotherm. Fig. 8 marks both. |
| m | Section 3.1 cutoff 393.15 K against Table 1 498.15 K. | Addressed | Section 3.1 now says which constants are extrapolated (R4 and R5 above 323.15 K for MEA); Section 5.4 says R4 and R5 are evaluated outside their source ranges for every amine, unlike R1–R3. |
| m | Complete the Kuranov 413 K sentence. | Addressed | Section 3.1: “For MDEA the loaded total pressures of Kuranov et al. at 413 K were set aside as an extrapolation”; result in Section 4.2.2 (3.1 % on 11). |
| m | pH standard-state basis. | Addressed | S2.2: pH from R2 on the common molality basis; the 1.75 difference from R1 at loading 0.30 is a difference of basis. |
| m | Fig. 7 companion panel (AMP content, pressure, completed searches without descent). | Open | Fig. 8 is unchanged apart from its labels. The caption says that states at different contents and pressures project onto one point and that states without a detected instability are not drawn. |
| m | Name R1–R3 in the limitations. | Addressed | Section 5.4, estimation paragraph. |
| m | Borrowed carbamate inputs. | Addressed | S1.4 (parameter text) and Section 5.4: the AMP carbamate inputs are those of the MEA fit with the MEA-fitted shared set and were not updated. |
| m | Bower degree symbol corrupted. | Addressed | Fixed in the bibliography producer; both Bates and Bower titles print the degree sign. |

## Opus (3/5, major revision)

| # | Comment | Status | Response and locator |
|---|---|---|---|
| M1 | Refit AMP with the 373–393 K pressures and a free slope; say that the measured pressures disfavour the split fit; pilot-plant evidence; abstract wording. | Addressed / Partly | This refit is now the AMP model (Section 4.2.3). Section 4.3 states that the first fit underpredicted every measured pressure at 373–393 K (28.1 and 25.3 %) and that fitting them removed the splits; S7.3 keeps the two-liquid bubble pressures (0.2525 against 0.4065 MPa, 0.3291 against 0.6326 MPa). The abstract says “gave calculated splits at 363–393 K; fitting the measured pressures at those temperatures removed them”. Pilot-plant observations are not cited: no such source is in the evidence base, so the text says only that no measurement of liquid–liquid coexistence was used. |
| M2 | Position against stability-aware estimation (Gau et al. 2000; Mitsos et al. 2009; Glass et al. 2018). | Addressed | Introduction (fifth paragraph) and Section 4.3 (last paragraph) cite Mitsos, Bollas, Glass and Gau. The text says stability is checked after the fit here, not imposed. |
| M3 | Water–bicarbonate interaction unidentified; profile likelihood; cross-start check; one split at relevant pressure; independent route through salt data. | Addressed / Partly | The independent route is adopted (Section 2.2, S1.3). Section 2.2 states that the MEA data do not determine the interaction (0.765 ± 3.18). The threshold 1.3987 is replaced by the nominal reference change, 1.92 times the variance factor (S4.1). The cross-start check between the two values was not made. |
| M4 | Pattern “better fit lies near a gap” suggests missing physics; minimum Hessian eigenvalue at fitted states. | Partly | S7.3 gives the lowest eigenvalue at the fitted loaded states for the fits made with the MEA-fitted shared set (positive, minima 0.122–0.439) and −0.083 at the worked split state; it was not calculated for the AMP model. Section 5.3 states that the MDEA binary lies close to a calculated demixing near 423 K and that the linear temperature law has no other physical basis. No missing-physics claim is made. |
| M5 | Cation representations differ; test a single-sphere MDEAH⁺. | Open | Not tested. Stated as a limit in Section 5.4 (“The DEA and MDEA cations are chains and the other amine ions single spheres”) and Section 2.2. |
| M6 | Accuracy against published models; justify 11 against 16 parameters. | Addressed | Section 5.2 and Table 9 state where published models are closer (Ma'mun pressures, Ermatchkov and Kamps pressures) and where the MDEA model is (82 Kuranov pressures, of which it fitted 70). Section 4.1.5 gives the cost of the restrictions on the Ma'mun pressures (19.4, 33.5, 38.4 %) and what they buy. |
| M7 | Report the variance factors of DEA and AMP; repeat the AMP and MDEA pairs with other weights. | Partly / Open | Variance factors: 0.288 (DEA) and 0.737 (AMP), S4. Contributions: Table S13. No reported model was refitted with other weights; Section 4.2.2 and Section 5.4 say so. The only reweighted refit is the MEA Cai test made with the MEA-fitted shared set (S2.3). |
| M8 | Rationale of the hybrid reference in Eq. 8; show that one g underlies the tangent-plane test; pH offset; link between pH and carbonate deficits. | Partly | One Gibbs energy at a state: Section 2.3 and S3. pH: S2.2 (basis offset). A quantitative link between the pH and carbonate deficits is not established; Section 4.1.2 says the cause of the carbonate deficit is unresolved. The electrode comparison was not repeated for the MEA model (S2.2). |
| M9 | Hong stability claim: confirm or move to the supplement. | Addressed | Moved to S9; Section 5.2 keeps only the caveat on the 1.53 %. |
| m | Shorter title. | Not adopted | The title is kept by owner decision. |
| m | “73 of 666 searched states”. | Addressed | Section 4.3. |
| m | Plain highlights. | Addressed | `submission/highlights.txt`, five statements without paired numbers. |
| m | Drop the 39 Kiepe pressures. | Not adopted | They are in the retained MEA fit, respond to none of its parameters and are excluded from the degrees of freedom (Section 3.3); removing them needs a refit and changes no result. |
| m | Hilliard heat-capacity counts. | Addressed | Table S7 now reads 4 fitted / 47 not fitted, as Tables 2 and 5 do (#434 record). |
| m | Table S8: 24.91 % in both bands. | Addressed | Verified from the per-source records: 24.910 % (69 observations) and 24.913 % (66); the agreement is a coincidence. |
| m | Kuranov 393.16 K row. | Open | The reason why that row is outside the fitted set is not recorded in the retained files. |
| m | AMP bounds (δh on its bound, σ on 6.5 Å). | Addressed | Section 4.2.3 and Table 7: the R4 enthalpy increment and the carbamate diameter are both on their lower bounds in the AMP model; bounds in Table S22. Wider bounds were not tested. |
| m | MDEA linear-in-T law against 1/T. | Addressed | Section 2.1 lists the three linear-in-T exceptions; Section 5.3 says the law lets one bound act where the gap first appears and has no other physical basis. |
| m | Search starts per state, including ion-rich starts. | Partly | S7.1 lists the starting compositions it documents (uniform and near-pure neutral species, with the trial compositions of earlier searches added). Whether further ion-rich starts would change an outcome was not tested; the ion-rich second liquid of the first AMP fit was found with these starts. |
| m | Grid by pressure band; 229 unexplained unfinished searches. | Addressed | S7.1 gives every unfinished MDEA search by cause (1,024 / 146 / 71 / 7) and by kind of state (1,026 grid, 222 measured). |
| m | The 27 MDEA states below the bubble pressure are model error; flag them. | Addressed | Now 25 states. Section 4.3: “the values calculated there refer to a liquid that the model does not predict to be stable”; S7.1 lists them. |
| m | Figiel average for MEA and MDEA. | Open | Not evaluated for MEA (S2.2 says so). Tested for the AMP worked split only (S7.3). |
| m | Basis of the CO₂ permittivity coefficients. | Open | Not changed in this revision. |
| m | DEA cross-association; pure-DEA vapor pressure to 458 K. | Open | Not tested. The DEA binary is reported as a negative result (Section 4.2.1). |
| m | Fig. 7 panels. | Open | See Sol. |
| m | Section 5 title “Discussion”. | Addressed | Section 5. |
| m | Consolidate caveats, shorten 20–25 %. | Addressed | 33 → 27 pages; caveats in Sections 3.1 and 5.4. |
| m | References garbled; Hong 2027; how the earlier MEA model differs. | Addressed / Open | Degree signs fixed. The Hong year is that of the library record and was not changed. Introduction, third paragraph, says how the earlier model differs. |
| m | Package versions 1.3.0/1.3.1 against public 1.3.2. | Addressed | Data availability: the four reported models were calculated with 1.3.1, the MEA fits with the MEA-fitted shared set with 1.3.0; 1.3.2 is the public release. |
| m | Table 10 header. | Addressed | Table 8 regenerated with the column of pressure bases named in its notes. |

## Fable (3/5, major revision)

| # | Comment | Status | Response and locator |
|---|---|---|---|
| M1 | Fit the 43 Hartono/Tong pressures at 373–393 K and the Tong pressures at 313–353 K; does the slope become determined; does the split survive; the R5-range rule was not applied to DEA and MDEA. | Addressed | All 105 loaded pressures are fitted. The slope is −52.0 ± 63 K, still not distinguishable from zero (Section 4.2.3); no search detects an instability (Section 4.3). Section 3.1 now says the fitted sets were chosen amine by amine, not by one rule. |
| M2 | Fixed slope chosen by stability; −175 K still has instabilities; ln K5 change removes the split; onset above 393 K; sensitivity to K5, permittivity and Born term. | Partly / Open | The fixed slope is no longer the model; it is a sensitivity (S7.3: +1.33 in the objective, 1.55 standard errors below the fitted slope). The K5 and term tests are those of the first fit (S7.3). The AMP model was not searched above 393.15 K (stated in S7.1). |
| M3 | Weights inconsistent between amines; tabulate contributions; repeat MDEA with pressures weighted; “model form not data” unsupported. | Partly / Open | Section 3.3 says that the scales and weights are assigned and differ between the amines, S2.4 gives the pressure scales and weights (unit scale with weight 100/9 for MEA and MDEA, equivalent to a scale of 0.3; 0.09 and 0.015 with averaging weights for DEA and AMP) and Table S13 the contributions; the 24 CO₂-free densities carry 84 % of the MDEA objective and the loaded pressures 1 %. A reweighted MDEA refit of the reported model was not made (Section 4.2.2, Section 5.4). The unsupported phrase is removed. |
| M4 | MDEA pure parameters not checked against pure-MDEA data; linear-T exception; eight parameters buy nothing over published predictions. | Partly / Open | Linear-T exception: Sections 2.1 and 5.3. Section 5.2 now compares on the 82 Kuranov pressures (8.8 % against 19.7–22.9 % for predictive ePC-SAFT, with 70 of the 82 fitted here) and states that published sets are closer on the Ermatchkov and Kamps pressures. The pure-MDEA check was not made. |
| M5 | Identifiability; fix the water–bicarbonate interaction from bicarbonate-rich data. | Addressed | Adopted (Section 2.2, S1.3), with its limits: two values on bounds, sodium carbonate 5.1 %, data to 318 K (Section 5.4). |
| M6 | Phase search under-described; benchmark on a known split; unphysical MDEA grid states; bilevel estimation literature. | Partly / Open | Method: Section 3.4 and S7.1. Literature: Introduction and Section 4.3. The confirmed MDEA split is at such a grid state (78.6 wt %, loading 1.368, 121.3 MPa) and is described as far outside the measured conditions. No benchmark on a known split was run. |
| M7 | Multistart and released-shared refits are required. | Open | #427 and #424 are open by owner decision. Section 5.4 states both as limits; Section 4.2.4 ends with the released-parameter question. |
| M8 | DEA rests on one 1976 source; standard sets unused. | Open | No data were added. Section 5.4: “The DEA model rests on one source of loaded pressures, measured with methane in the cell”. |
| m | Two reference conventions in Eq. 8. | Addressed | Section 2.3, S3. |
| m | H₃O⁺ Born diameter. | Addressed | S1.2: that of the hydrogen ion in Figiel et al. |
| m | pH and carbonate deficits are one defect. | Partly | See Opus M8. |
| m | Figiel average test for MEA. | Open | See Opus. |
| m | Henry constants against the N₂O analogy. | Open | Not addressed in this revision. |
| m | Held ions reused. | Addressed | S1.2 names the values taken from Held et al. and the two water–anion interactions that are not. |
| m | 1.3987 has no statistical basis. | Addressed | Replaced by the nominal reference change (S4.1), which the text calls nominal because the weights are assigned. |
| m | Section 5.1 generalizes from two cases. | Addressed | Removed. Section 4.3 ends: “The practical lesson is limited to this case”. |
| m | Hilliard counts. | Addressed | See Opus. |
| m | Table S20: A4 redundant. | Not adopted | The note of Table S5 says that A4 and B4 are the final coefficients and not further parameters; the row is kept so that the correlation can be reproduced. |
| m | Hong section disproportionate. | Not adopted | S9 is kept at its length by the standing decision on the Hong comparison; the main text is reduced to one sentence. |
| m | Table 5: lead with Table 11. | Not adopted | The order follows the story: MEA deviations first, published comparisons in the Discussion. |
| m | Twelve-digit objectives. | Partly | Kept only where they show agreement between starts (Table S23, S7.2). |
| m | Section 5 title; Fig. 7; highlights; DOI; package versions; reference 18. | See above | Title, highlights, versions and reference fixed; Fig. 8 and the DOI open. |
| m | Table 1: primary source of R1–R3. | Open | Table 1 cites Austgen et al. for R1–R3 with a note on the range; the primary sources behind that compilation were not added. |

## Misses stated as misses

- DEA fitted pressures worsen with the salt-fixed interactions: 28.5 → 36.6 % (Sections 4.2.1, 4.2.4, 6; abstract in words).
- MDEA CO₂ partial pressures of Ermatchkov et al., not fitted: 17.9 → 38.4 % (Sections 4.2.2, 4.2.4, 5.2, 6).
- MEA pressures of Ma'mun et al. near 393 K: 38.4 % for the MEA model, 33.5 % with the MEA-fitted shared set, 19.4 % for the 16-parameter calibration (Section 4.1.5, Table 9).
- The MDEA model has one confirmed calculated split and 222 unfinished searches at measured states (Section 4.3).
