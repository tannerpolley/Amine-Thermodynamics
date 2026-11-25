# Round-8 referee comments: response

Manuscript: “Thermodynamics of CO₂-loaded aqueous amines with ePC-SAFT: monoethanolamine calibration, transfer to DEA, MDEA and AMP, and phase stability”, branch `issue-429-story-pass`, issue #429.

Locators refer to the PDFs built in this revision (main text 30 pages, supplement 56 pages). “S” numbers are supplement sections and tables. Status words: **Addressed**, **Partly**, **Open**, **Not adopted**.

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
| A2 AMP search pressures | Addressed | §4.3 and the Fig. 8 caption now say the 666 searches use pressures scaled to each fit's bubble pressure. The six measured-pressure recalculations are given separately: four unresolved and two with no descent for the free slope; three and three for the fixed slope (S7, Table S43). The Fig. 8 caption no longer says the adopted model “has none” without that scope. The highlight and abstract now state 18 Hartono pressures at 373–393 K and 40 Tong pressures at 313–393 K. Table 8 is generated; see display request D1. |
| A3 MDEA counts | Addressed | The introduction, abstract, §4.3 and the conclusions agree: no confirmed MDEA split. The 17.401/17.600 endpoint dependence is replaced by the #440 multistart (§3.3, S4). The 204.054 MPa and 262.862 MPa cases are unresolved under the fixed reference (§4.3, S7). The “4.19 MPa” claim was wrong as a maximum and is removed. §4.3 and S7 now name the subset: the highest pressure of any search at a measured state, 14.46 MPa, the bubble pressure calculated at Ermatchkov Table 6 row 13. |
| A4 Reproducibility | Partly | The availability statement now says that 1.3.1 and 1.3.0 were used, that the deposit holds both builds and their source revisions, and that 1.3.2 was not used and its reproduction is untested. The DOI stays a placeholder (constraint of this stage). Open: (i) no reproduction with 1.3.2 was run; (ii) the public tag `v1.3.1` (commit `1b46e57ce8`) is not the commit behind the 1.3.1 build (`05e94210`, which is on public `main`). The deposit software index must name the build revision, not the tag. |
| Minor: salt agreement | Addressed | §2.2 now says that the 0.16 % and 5.1 % reproduce Peiper–Pitzer values at prescribed ionic compositions, with ideal CO₂ subtraction and conditional on the bounds. The six charge-closure refusals are named there and in S1.3. |
| Minor: DEA wording | Addressed | The abstract, the highlight, §4.3, §5.4 and the conclusions use the wording that the single-liquid calculation matches the density while the model's own phase calculation favors two liquids, contrary to treating the samples as one liquid. The ion-rich fraction is now 9.73 %, at the 30 wt %, 0.50 feed (§4.3, S7). |
| Minor: Kuranov and Ma'mun | Addressed | §5.2 gives Kuranov as matched by count only and listed without ranking: 4.35 % on 82 rows matched by row, of which 70 were fitted. Ma'mun is 38.66 % here against 21.03 % for Baygi and Pahlavanzadeh's PC-SAFT, which fitted no ternary data (§5.2, §4.1.5). |
| Minor: S7.3 slope statement | Addressed | S7.3 now opens “Two separate changes each remove the splits, so neither is identified as their cause” and gives both. §4.3 gives both changes and says that suppressing a split need not improve the pressure fit. |

## Sol

| Item | Status | Response and locator |
|---|---|---|
| S1 Source of each property | Addressed | §2.3: compositions minimize G*, densities come from V_EOS and enthalpies from Eq. 12, and with fixed references all three are derivatives of G*. §2.4 says what Eq. 12 holds fixed. The “single Helmholtz energy” sentence of §1 is now accurate under the fixed reference. Checks at the decisive phase cases: the 204 MPa MDEA parent and both inventories are in S3 and Table S32. The 263 MPa case was recalculated under the fixed reference: a descent remains and its phase identity is unresolved (§4.3, S7). **Open:** continuation of the aqueous reference roots below water saturation is not described; no record of it was found in the #440 evidence. |
| S2 AMP six-row table | Partly | The screen and the controls are now separated everywhere (abstract, §4.3, Fig. 8 caption, S7). Table S43 is the generated table of fixed-reference phase controls. The full six-row table (T, feed, imposed P, model bubble P, trial initialization, ΔG, error, outcome for both fits) is display request D2. The S7.3 slope statement is aligned with R5 (see Astra minor). |
| S3 DEA wording | Addressed | Used in the abstract, highlight 4, §4.3, S7 and the conclusions. The text says that no phase-state measurement is claimed to contradict the splits. |
| S4 Local-fit sensitivity | Addressed within the #440 runs | §3.3 and S4: three distinct starts tie for MEA, DEA and AMP; the fixed-slope AMP fit has two minima; MDEA is provisional with one evaluable drawn start. The endpoint stationarity measure is reported (no endpoint meets 10⁻⁸; replayed descent steps are consistent with the function tolerance except for MDEA). Tied endpoints agree on the decisive DEA and AMP phase cases (S4). **Open (C6):** the spread of predictions among tied endpoints has not been compared with deviations from measurements in the same operating bands; §5.4 states this as a limit. Table S31 (starts) is generated. |
| S5 Salt | Partly | §2.2 now describes the fit at prescribed compositions with ideal CO₂ subtraction and puts the qualification beside 0.16 % and 5.11 %. The six refusals are given separately. §2.2 now positions the fit against Wangler et al. (as S1.3 did). **Open:** the representative reconstructed row with source columns is display request D3. |
| S6 Literature | Addressed | Kuranov values are listed without ranking (§5.2, S8). The Hong 131/132 local failures are attributed to our reconstruction in §5.2, S9 and the opening of S9; the reconstruction was checked against one model curve and differs measurably from their Fig. 5. The heading of the Hong table (now Table S47; the referee's S42) is display request D4. |
| S7 Deposit | Open | The availability text keeps its `% PENDING` note: the deposit stager predates the adopted fits. Processed row IDs, roles, weights, parameter vectors, version-pinned commands, per-state search results, the DEA, AMP and MDEA replays and the MDEA failure categories (229 of 1564 measured-state searches unfinished, 14.6 %) are for the deposit build, not this prose pass. |
| Minor: “58 hotter” | Addressed | Removed from the abstract, highlights, conclusions, preprint abstract and cover letter. |
| Minor: Kiepe | Partly | §3.3 states that 268 of the 307 rows respond. Consistent Kiepe labels in Tables 2, S14 and S19 are display request D5. |
| Minor: Table 8 comparison fits | Partly | §4.2.4 names each comparison fit and its convention (the DEA 36.63 % is the 30-pressure Lawson–Garst fit, 42.75 % is the 90-pressure model). Naming them in the table rows is display request D1. |
| Minor: S15/S39 MDEA descents (referee numbering) | Partly | S7 now lists the 27 MDEA descent states by temperature and pressure and by trial-endpoint label. Per-state composition and source-row columns, and source versus assigned (Böttinger cell) pressures, are display request D6. Sobrino Table 5 is not addressed: I could not identify the requested change from the item alone. |
| Minor: Fig. 7 423 K limit | Addressed | The caption and §4.3 attach the bound to the CO₂-free binary; the onset brackets were updated (423.16250–423.16875 K at 1.466 MPa). |
| Minor: S29 MEA start IDs | Open | Table S31 (generated) lists MEA starts A, B, C (no endpoint) and LHS-21. Linking each to its initial vector is display request D7. |

## Display requests (generated displays and scripts were not edited except as noted)

| ID | Display | Request | Record |
|---|---|---|---|
| D1 | Table 8 (`amine-summary.tex`) | Name each comparison fit in its row (MEA-fitted shared set; DEA 30-pressure fit; MDEA with MEA weights; AMP with earlier carbamate inputs) and replace “historical” in the caption with “with system-pressure references”. | `tables/amine-summary.tex` producer |
| D2 | New supplement table | Six AMP measured-pressure controls × two fits: T, feed, imposed P, model bubble P, trial initialization, ΔG/RT, numerical error, outcome. | `AMP_{free,fixed}/A` controls; `C4 AMP_* selected experimental phase counts` |
| D3 | S1.3 | One reconstructed Peiper–Pitzer row with source columns and the target equation evaluated. | `salt.json.gz` |
| D4 | Table S47 (Hong comparison) | Heading “reconstruction of the Hong et al. model”. | `supplement-hong-comparison.tex` producer |
| D5 | Tables 2, S14, S19 | One Kiepe label. | producers |
| D6 | Table S42 (MDEA phase outcomes) | Composition and source row per descent; source vs assigned pressure. | `MDEA/screen/selected/declared/summary.json.gz:classifications` |
| D7 | Table S31 | Distinct start IDs linked to initial vectors. | handoff `fit_attempts`, `<design> start screening` |
| D8 | Tables 9, S44 | Replace “tracking” with “system-pressure references” in row labels and captions (Table 9 rows “This work, tracking, …”; S44 caption). | producers |

The prose-check block of `dea_displays.py` was changed with owner approval: only its expected prose strings, which are now read from the #440 records.
