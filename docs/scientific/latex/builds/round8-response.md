# Round-8 referee comments: response

Manuscript: “Thermodynamics of CO₂-loaded aqueous amines with ePC-SAFT: monoethanolamine calibration, transfer to DEA, MDEA and AMP, and phase stability”, branch `issue-429-story-pass`, issue #429.

Locators refer to the PDFs built in this revision (main text 30 pages, supplement 59 pages). “S” numbers are supplement sections and tables. Status words: **Addressed**, **Partly**, **Open**, **Not adopted**.

Evidence: the fixed-reference study of #440 (`analyses/fixed_reaction_reference/manuscript-handoff.json` and `notebook.qmd`, merged to main at `5023dbc44`). The investigator promoted that notebook on 2026-11-25 for this prose pass, subject to its recorded dispositions: the MDEA fit is provisional, every endpoint misses the strict projected-gradient check, C6 is open, and the open and undecided keys are stated as limits.

## What changed in this revision

1. **One Gibbs energy.** Every reaction reference is now at 100 kPa, and all four models were refitted that way. Eq. 9 (§2.3) shows why ∂G*/∂P = V_EOS: dP_src/dP = 0. §2.3 and §2.4 give the finite-difference verification at named states (S3, Table S32). The comparison with system-pressure references is a supplement sensitivity (S3), following the owner's decision.
2. **Multistart.** MEA, DEA and AMP (free slope) each have three distinct admitted starts that tie. The fixed-slope AMP fit has two minima, 76.23 (reported) and 2741.26. The MDEA fit is provisional. No endpoint meets the strict projected-gradient criterion (§3.3, §5.4, S4, Table S31).
3. **Phase results.** DEA has confirmed splits at feeds 32, 41, 42 and 43, and feed 31 is unresolved. MDEA has no confirmed split, and the 204 and 263 MPa cases are unresolved. AMP has no descent at 666 bubble-scaled states; its six measured-pressure controls are reported separately (§4.3, S7).
4. Every entry of `440-rebind-prose-gaps.md` is applied in the main text, supplement, highlights, preprint abstract and cover letter.

## Astra

| Item | Status | Response and locator |
|---|---|---|
| A1 Eq. 9 vs Eq. 12 | Addressed | The construction changed: every reference is at 100 kPa, so the chain term vanishes. §2.3 gives the potential (G* = G_EOS + RT Σ nᵢ bᵢ(T, P_src)), its pressure derivative (Eq. 9) and what each property comes from. §2.4 says what Eq. 12 holds fixed: P and n, with re-solved equilibrium at the same feed. Finite differences at one fitted state of each amine and at the 204 MPa MDEA inventories agree within their error estimates (§2.3, §2.4, S3, Table S32). The MEA and DEA volume estimates are 9–11 % of V_EOS, and the text says so. Effect on observables: §2.3 gives one sentence; S3 gives the paired fitted deviations (at most 0.23 points, MDEA at a different local endpoint) and the phase cases that change. |
| A2 AMP search pressures | Addressed | §4.3 and the Fig. 8 caption now say the 666 searches use pressures scaled to each fit's bubble pressure. The six measured-pressure recalculations are given separately: four unresolved and two with no descent for the free slope; three and three for the fixed slope (S7, Table S43). The Fig. 8 caption no longer says the adopted model “has none” without that scope. The highlight and abstract now state 18 Hartono pressures at 373–393 K and 40 Tong pressures at 313–393 K. Table 8 names each comparison fit. |
| A3 MDEA counts | Addressed | The introduction, abstract, §4.3 and the conclusions agree: no confirmed MDEA split. The 17.401/17.600 endpoint dependence is replaced by the #440 multistart (§3.3, S4). The 204.054 MPa and 262.862 MPa cases are unresolved under the fixed reference (§4.3, S7). The “4.19 MPa” claim was wrong as a maximum and is removed. §4.3 and S7 now name the subset: the highest pressure of any search at a measured state, 14.46 MPa, the bubble pressure calculated at Ermatchkov Table 6 row 13. |
| A4 Reproducibility | Partly | The availability statement now says that 1.3.1 and 1.3.0 were used, that the deposit holds both builds and their source revisions, and that 1.3.2 was not used and its reproduction is untested. The DOI stays a placeholder (constraint of this stage). Open: (i) no reproduction with 1.3.2 was run; (ii) the public tag `v1.3.1` (commit `1b46e57ce8`) is not the commit behind the 1.3.1 build (`05e94210`, which is on public `main`). The deposit software index must name the build revision, not the tag. |
| Minor: salt agreement | Addressed | §2.2 now says that the 0.16 % and 5.1 % reproduce Peiper–Pitzer values at prescribed ionic compositions, with ideal CO₂ subtraction and conditional on the bounds. The six charge-closure refusals are named there and in S1.3. |
| Minor: DEA wording | Addressed | The abstract, the highlight, §4.3, §5.4 and the conclusions use the wording that the single-liquid calculation matches the density while the model's own phase calculation favors two liquids, contrary to treating the samples as one liquid. The ion-rich fraction is now 9.73 %, at the 30 wt %, 0.50 feed (§4.3, S7). |
| Minor: Kuranov and Ma'mun | Addressed | §5.2 gives Kuranov as matched by count only and listed without ranking: 4.35 % on 82 rows matched by row, of which 70 were fitted. Ma'mun is 38.66 % here against 21.03 % for Baygi and Pahlavanzadeh's PC-SAFT, which fitted no ternary data (§5.2, §4.1.5). |
| Minor: S7.3 slope statement | Addressed | S7.3 now opens “Two separate changes each remove the splits, so neither is identified as their cause” and gives both. §4.3 gives both changes and says that suppressing a split need not improve the pressure fit. |

## Sol

| Item | Status | Response and locator |
|---|---|---|
| S1 Source of each property | Addressed | §2.3: compositions minimize G*, densities come from V_EOS and enthalpies from Eq. 12, and with fixed references all three are derivatives of G*. §2.4 says what Eq. 12 holds fixed. The “single Helmholtz energy” sentence of §1 is now accurate under the fixed reference. Checks at the decisive phase cases: the 204 MPa MDEA parent and both inventories are in S3 and Table S32. The 263 MPa case was recalculated under the fixed reference: a descent remains and its phase identity is unresolved (§4.3, S7). The aqueous reference-root probe is supplied below for the Writer. |
| S2 AMP six-row table | Addressed | Table S43 gives the six measured-pressure rows, each with paired results for the two slopes. The abstract, §4.3, Fig. 8 caption and S7 distinguish these controls from the bubble-scaled screen. |
| S3 DEA wording | Addressed | Used in the abstract, highlight 4, §4.3, S7 and the conclusions. The text says that no phase-state measurement is claimed to contradict the splits. |
| S4 Local-fit sensitivity | Addressed within the #440 runs | §3.3 and S4: three distinct starts tie for MEA, DEA and AMP; the fixed-slope AMP fit has two minima; MDEA is provisional with one evaluable drawn start. The endpoint stationarity measure is reported (no endpoint meets 10⁻⁸; replayed descent steps are consistent with the function tolerance except for MDEA). Tied endpoints agree on the decisive DEA and AMP phase cases (S4). **Open (C6):** the spread of predictions among tied endpoints has not been compared with deviations from measurements in the same operating bands; §5.4 states this as a limit. Table S31 (starts) is generated. |
| S5 Salt | Addressed | §2.2 describes the fit at prescribed compositions with ideal CO₂ subtraction and puts the qualification beside 0.16 % and 5.11 %. S1.3 shows the worked Peiper–Pitzer row and target calculation. The six refusals are given separately. |
| S6 Literature | Addressed | Kuranov values are listed without ranking (§5.2, S8). The Hong 131/132 local failures are attributed to our reconstruction in §5.2, S9 and the opening of S9; the reconstruction was checked against one model curve and differs measurably from their Fig. 5. Table S47 names the reconstruction. |
| S7 Deposit | Open | The availability text keeps its `% PENDING` note: the deposit stager predates the adopted fits. Processed row IDs, roles, weights, parameter vectors, version-pinned commands, per-state search results, the DEA, AMP and MDEA replays and the MDEA failure categories (229 of 1564 measured-state searches unfinished, 14.6 %) are for the deposit build, not this prose pass. |
| Minor: “58 hotter” | Addressed | Removed from the abstract, highlights, conclusions, preprint abstract and cover letter. |
| Minor: Kiepe | Addressed | §3.3 states that 268 of the 307 rows respond. Tables 2, S14 and S19 name Kiepe et al. and mark the pressures as fitted beforehand or constant in the reactive objective. |
| Minor: Table 8 comparison fits | Addressed | §4.2.4 and Table 8 name each comparison fit and its convention. The DEA 36.63 % is the 30-pressure Lawson–Garst fit and 42.75 % is the 90-pressure model. |
| Minor: S15/S39 MDEA descents (referee numbering) | Partly | S7 now lists the 27 MDEA descent states by temperature and pressure and by trial-endpoint label. Table S42 gives the composition, source row and pressure basis for each state. Sobrino Table 5 is not addressed: I could not identify the requested change from the item alone. |
| Minor: Fig. 7 423 K limit | Addressed | The caption and §4.3 attach the bound to the CO₂-free binary; the onset brackets were updated (423.16250–423.16875 K at 1.466 MPa). |
| Minor: S29 MEA start IDs | Addressed | Table S31 links each start ID to its vector, including MEA start C, which has no endpoint. |

## Built displays

| ID | Status | Locator | Retained record |
|---|---|---|---|
| D1 | Built | Table 8. Named comparison fits and reference convention. | `amine-summary.tex` producer and its keyed fit and screen inputs |
| D2 | Built | S7, Table S43. Six measured AMP pressures with paired fits. | Selected `AMP_{free,fixed}/controls/A.json.gz` and corresponding native screen summaries for the bubble pressures |
| D3 | Built | S1.3. Worked sodium bicarbonate row from Peiper–Pitzer Table 6(a), with source columns and the evaluated target equation. | `salt.json.gz:reconstruction` |
| D4 | Built | S9, Table S47. Reconstruction of the Hong et al. model. | Retained Hong comparison rows and fixed-reference MEA predictions |
| D5 | Built | Tables 2, S14 and S19. Consistent Kiepe source and prior-fit role. | Fitted Kiepe rows and objective records |
| D6 | Built | S7, Table S42. Composition and source row for each MDEA descent, with source and search pressures. | `MDEA/screen/selected/declared/summary.json.gz:classifications`, the MDEA manifest and the #421 observation crosswalk |
| D7 | Built | S4, Table S31. Start IDs link to the physical vectors and coordinate order. | Fit attempts, design manifests and replacement-start records |
| D8 | Built | Tables 9 and S44. System-pressure references in the comparison rows, caption and headings. | Matched Kamps pressure populations and MDEA handoff comparisons |

The display check recomputes the displays and checks the full-precision source inventory. Adding 1 kPa to the retained fitted-slope bubble pressure for Hartono row 55 raised `AssertionError: Changed display record: analyses/fixed_reaction_reference/results/AMP_free/screen/selected/native/summary.json.gz`. Restoring the source bytes returned the check to passing.

## Evidence for the Writer

**S1 aqueous references.** At 393.15 K and 100 kPa the solver selects the high-density root with a positive isothermal pressure slope for the aqueous reference. For pure water and the infinite-dilution CO₂ limit, the reference density is 52.4007 kmol/m³ and the liquid is metastable, with a Gibbs energy 2.219 kJ/mol above the vapor root. The liquid density exceeds the calculated isothermal spinodal density by 10.6275 kmol/m³, and its pressure exceeds the model spinodal pressure by 349.671 MPa.

The probe and five reaction-reference readbacks are in [aqueous-reference-roots-429.json](../../../../analyses/fixed_reaction_reference/results/MEA/aqueous-reference-roots-429.json). The record identifies the pinned code for reference-pressure resolution, density selection and root admission. The spinodal is an extrapolation of the equation of state to negative pressure.

**Hong-matched pressure comparison.** On the 132 matched CO₂ partial pressures at nominal 30 wt% MEA, AARD is 22.59% with the MEA-fitted shared set and 24.97% with the salt-anchored fit, both at system-pressure references. Fixing the references at 100 kPa with the salt-anchored parameters held fixed raises AARD by 0.015 points to 24.99%, and refitting raises it another 0.073 points to 25.06%.

The 393.15 K rows account for 1.464 of the 2.472 percentage points between the displayed fits. The largest increase among the 393.15 K loading bands is 20.86 points for the three rows at loading at least 0.5 mol/mol, including 0.53 points from the reference change and refit together. The comparison uses 32 fitted and 100 unfitted rows. The keyed predictions, exact replay of the 24.97% baseline, and temperature and loading breakdown are in [hong-reference-convention-429.json](../../../../analyses/fixed_reaction_reference/results/MEA/hong-reference-convention-429.json).
