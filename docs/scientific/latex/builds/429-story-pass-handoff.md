# Issue 429 story pass: Writer handoff

**Branch and commit.** `issue-429-story-pass`, content commit `32fc154bf` (on top of `6f2039a6f`, branched from `main` at `28a01746f`). Not merged, not pushed.

**Promotion.** The owner's 2026-11-24 decision on #429 promoted the merged studies #420, #421, #422, #423, #425, #426 and #428 at `28a01746f` for this story pass, subject to the claim limits of the Writer brief.

## Plan items

| # | Item | State |
|---|---|---|
| 1 | MDEA phase result under three conditions | Done; 262.862 MPa always stated with its conditions |
| 2 | AMP pair leads | Done in abstract, introduction, Section 4.2, conclusions, highlights |
| 3 | Controlled MDEA transfer as its own subsection | Done (Section 4.3, Table 8) |
| 4 | Pressure metrics on separate bases | Done in text and tables. **Graphical abstract parked** by the owner until #424 and #427 are in; the file is unchanged from `main` and its numbers and MDEA wording are now stale |
| 5 | Standard errors on responsive observations | Done everywhere printed |
| 6 | Cai weight wording | Done |
| 7 | MEA section | Done; the MEA–water figure moved to the supplement |
| 8 | DEA paired table and corrected statements | Done (Table 9) |
| 9 | R4 on the starting-law basis | Done; see open question 1 |
| 10 | Positioning by what transfers | Done |
| 11 | Published comparisons | Done except Hong's own 1.53 % and the Kundu footnote (not verified, so not written) |
| 12 | Data table | Done (Table 2), without a composition column |
| 13 | Reference states, B and λ | Done |
| 14 | Tables S8 and S10 wording | Done |
| 15 | DOIs | Done; all four print |

Pending sentences: one after the controlled MDEA transfer (#424) and one after the estimation paragraph (#427), italic and bracketed, each marked `% PENDING` in the source.

## Decisions where the plan left room

- Results order is AMP, controlled MDEA, MDEA phases, DEA, then a Discussion section; `STYLE.md` has a new "Story pass" row and notes on the eight rows it amends.
- The Ermatchkov comparison is in the comparison section only.
- The bibliography gained one entry, Austgen et al. 1989, copied from the Zotero export by the repository script. A full regeneration would rewrite about 1,580 lines, and it fails because stale `builds/part2*.aux` files cite a key absent from the export.
- Optional MDEA process context was not added.

## Numbers

`docs/scientific/latex/builds/429-story-pass-number-sources.md` lists every added or changed number with its record and says which are machine-checked.

## Build and checks

- `scripts/build_manuscript.sh`: passes. Main 33 pages, supplement 35; no undefined references or citations; no overfull boxes in either log.
- `dea_displays.py --check`, `final_rerun_tables.py --check` and `--reference-states --check`: pass, including every prose-string check.
- `python3 scripts/check_private_source.py`: passes. The CSE prose check passes.
- Main text 10,749 words; abstract 250 words; highlights at most 83 characters.

## Open questions

1. Table S20 gives the #413 DEA A₄ bounds, 4.192 to 10.192. On the starting-law level basis at 313.15 K, these are −3 to +3 (#426 control C4).
2. Austgen 1989 has no PDF in Zotero; its sentence states only what the abstract supports.
3. The split of citations between Perdomo 2025 and the reacting-constraint papers follows the plan; I did not re-read those papers.
4. The exact Figiel average is still unevaluated.
5. The cover letter and preprint abstract were synchronized; the suggested-referee file was not touched.

## First action for the post-draft checks

Read `builds/main.pdf` front to back as a fresh referee and grade each section, starting with whether Sections 4.2 and 4.3 support the abstract's two claims from the tables alone; then spot-check the unchecked rows of the number-sources file.

## Fix round 1

**Commit.** `315d30063` on `issue-429-story-pass` (on `89445aae4`). Not merged, not pushed. Applies the post-draft numbers-and-citations check and the story check; where they overlapped, the numbers check was used.

**Outside-fit pressures (numbers item 1).** Fixed in the producers: `final_rerun_tables.py` (Table 8) and `dea_displays.py` (Table 10 and the prose checks, now also covering the preprint abstract and the cover letter). Recomputed count-weighted from the per-source records; every value equals the check list.

| Model | Observable (N) | Values | Record |
|---|---|---|---|
| MDEA, k = 0.7650 / 0.1325 / 1.0 | total P outside the fit (54: Kamps 28, Kuranov 413 K 11, Sedighi 15) | 38.75 / 32.99 / 38.65 % | `shared-bicarbonate-417/mdea-comparison.json.gz` |
| same | p(CO₂) outside the fit (121: Ermatchkov 101, Xiao 20) | 20.07 / 33.62 / 20.05 % | same |
| MDEA model (Table 10) | total P; p(CO₂) | 38.75 (54); 20.07 (121) | `bounded-binary-411/data-rows.json` |
| AMP model (Table 10) | total P (63: Hartono 18, Tong 40 loaded, Tong 5 CO₂-free); p(CO₂) (51, Kundu) | 26.18; 47.02 % | `slope-150/data-rows.json` |

The producers assert that the five MDEA sets reproduce the pooled 175-row value (25.83 %) and that the reported-model rows reproduce both retained summaries.

**Applied.** All items of the numbers check, plus all items of the story check that the numbers check did not replace: story 2 (conclusion, supplement), 5, 6 (conclusion), 7, 8, 9, 10, 11 and 12. No sentence still calls the slope a sufficient cause. The MEA and DEA cells of Table 10 now also carry the p(CO₂) label.

**Not applied as written.**
- Story 1, 3 and 4, and story 6 in `main.tex`: the numbers-check text was used.
- Story 2's change to the section reference: it went with its own clause, which the numbers check replaced; the parenthetical reference stays.

**Consequential edits.**
- "The phase searches do." became "The phase searches separate them.", because the sentence before it changed.
- The preprint abstract mirrors the new `main.tex` abstract sentence.
- The cover letter drops "within the tolerance of the MEA fit". Its "The fitted data do not distinguish the two" now uses the numbers-check wording.

**Section 5.2 densities (story flag).** The numbers agree with Table S8; the denominators were unnamed. The 0.4 % is the AARD of 26 densities: 15 loaded Han, 3 CO₂-free Han and 8 CO₂-free Sobrino. The 1.3 % is the AARD of 15 heat capacities. The "0.6 % low" is the mean signed deviation of the 15 loaded Han densities (−0.55 %). Source: `stripper-temperature-409/band-table.csv`. The sentence now names the 15, 26 and 15, and a prose check covers it.

**Other findings.**
- The worked-split source the numbers check proposed (`reference-states-428/amp.json`) gives the state and the 0.0188 mol. Its `uncertainty` is 1.83e-10, a different quantity. The printed 2.8e-9 is `numerical_error_over_RT_mol` of the same grid state in `retransfer-412-f2-05e94210/main/phase-classification-1.json.gz`. The number-sources file names both.
- Table 2 temperatures come from `paper-evidence-341/objective-declarations.json`: Jakobsen 293.15–313.15 K, CO₂-free density 298.15–353.15 K. The "---" note was removed.
- The 23 + 4 split of the 27 MDEA states was confirmed in `phase-search-421/measured-phase.json`.

**Build and checks.**
- `scripts/build_manuscript.sh` passes. Main has 33 pages and the supplement 35. Neither has undefined references or overfull boxes.
- `dea_displays.py --check`, `final_rerun_tables.py --check` and `--reference-states --check` pass. So do `check_private_source.py` and the CSE prose check; its STYLE.md:66 advisory concerns a file this round did not touch.
- Visual check: the AMP split sentence and Fig. 7 share page 15, and Tables 6 and 7 follow on page 16.
- The graphical abstract is identical to `main`.

**Open questions.**
- The numbers check supplied Hong's 1.53 % (§3.2, Table 3), the Kundu Table 10 footnote and the Mac Dowell §III.B.1 wording. I did not re-read those sources; there is no local copy. I checked Perdomo 2023 App. D, and it supports the new sentence.
- The abstract and highlights now use "AARD" without defining it there. This is the numbers-check wording; the owner may prefer "average deviation".
- Open questions 2–5 above are unchanged.


## Round-3 text pass

**Basis.** The round-3 text list of 2026-11-24 (owner decisions), drawn from the four condensed referee reports (Astra 4/5, Sol, Opus and Fable 3/5). No calculation was run and no retained record was edited. Calculations wait for #432; each place that needs one keeps its existing text and carries a `% TODO #432 Qn` comment. The added and moved numbers are in the "Round-3 text pass" section of `429-story-pass-number-sources.md`. `STYLE.md` has a new "Round-3 text pass" row recording the owner decisions this pass applies.

### Items applied

| # | Item | Where |
|---|---|---|
| 1 | The 262.9 MPa split is out of the abstract, the highlights, Table 10 (row and footnote removed in the producer), the conclusions and Section 5.2. The main text keeps one sentence ("not globally free of calculated splits"), and the full calculation stays in Section S7.1. | `main.tex`; `dea_displays.py` (Table 10); §4.4; `conclusion.tex`; §5.2 |
| 2 | Abstract rewritten around one message (phase searches separate calibrations that pressure deviations do not). It has 8 numbers (10.3, 10.5, 73, 353, 20.1, 11.2, 20.1, 33.6), about 190 words, no layered caveats, the DEA negative result, and the testbed use. The preprint abstract mirrors it, and the cover letter follows. Limitations are gathered in §5.5. The §5.1 sentence repeating the Table 10 deviations, the §4.3 caveat list and the conclusion's caveat sentence are removed. | `main.tex`, `chemrxiv.md`, `cover_letter.md`, §4.3, §5.1, §5.5, conclusions |
| 3 | Highlights: highlight 2 now says "above 353 K, top temperature of fitted loaded pressures". Highlight 4 has the p(CO₂) tradeoff (20.1→11.2 %, 20.1→33.6 %; 85 characters, the Elsevier limit). Highlight 5 is the DEA negative result. | `highlights.txt` |
| 4 | Table S5: the DEA δh is −11968.4 J/mol on the starting-law basis, labelled like the AMP row; the producer asserts that the record row it replaces is 0. Table 7: the "R4 change at 313.15 K" rows became footnote c on A₄ (−1.309 ± 0.618, +1.233 ± 0.265). Table S20 keeps the level rows as bounds. | `dea_displays.py` |
| 5 | DEA stated as a negative result and §4.5 shortened (retitled "a negative result for the water–DEA binary"); also in the abstract, introduction, conclusions and highlight 5. | §4.5 |
| 6 | MDEA–water bound treated as a model-form limitation: §4.4 (unbounded fit converges inside a gap; linear-in-T law about 423 K against 1/T about 313.15 K, with no physical basis beyond placing the bound; "must not be used above about 423 K"), §5.4 (new paragraph), §5.5 and conclusions. | §4.4, §5.4, §5.5 |
| 7 | Physical plausibility: Hartono 2021 and Tong 2012 were read and report no phase state, so "no report of a second liquid was found". The AMP splits are judged to be artefacts of the extrapolated interaction. The ion-rich liquid is described as resembling a concentrated salt solution, and solid precipitation is stated to be outside the analysis (§4.2, §5.5). Tsanas et al. 2022 is cited for a real split in a loaded amine solvent located by a VLE-fitted eNRTL. | §4.2, §5.5 |
| 8 | Hong: the main text has one sentence with Hong's own 1.53 % (verified: their §3.2 and Table 3, against Aspen HYSYS output, with a weight fitted at each state) and "present implementation … at fixed pathway weight". The evaluation stays in S10, which now opens with the same label. | §5.3, S10 |
| 9 | Literature (all verified in Zotero copies): Rodríguez 2012, graphical only on Jou (MEA) and Kuranov (MDEA), no loaded-system deviation (§5.1, §5.4); Tong 2012 quasi-chemical AMP, 1.9 % in loading (§3.4); Böttinger 2008 extended Pitzer DEA speciation, with constants refitted to the NMR (§5); Aronu 2011 extended UNIQUAC, 24.3 % overall p(CO₂), no per-concentration value (abstract, §4.2). Table 11's caption now says the Kuranov identity rests on count, and the text carries Uyan's 22.9 % against Wangler's recalculated 34.4 %. | §4.1.4, §4.2, §4.5, §5.3; `dea_displays.py` |
| 10 | Exclusion rationale, new paragraph §3.1 `P:methods-selection`. AMP loaded pressures were restricted to the measured R5 range (declaration filter T ≤ 353.5 K). DEA's 394 K isotherm lies above the then-declared 393.15 K end of the shared R2 domain (`historical-f0.qmd`). Kuranov 413 K loaded rows were set aside as extrapolation in the #222 design. The text says plainly that "the exclusions follow no common rule". It also covers MEA (30 wt % only), DEA (one source, with methane) and MDEA/AMP (total pressure only). | §3.1 |
| 11 | Model-choice notes, one line each in §5.5: MEAH⁺–MEACOO⁻ k on its bound as a possible stand-in for ion pairing; the −0.998 MEA ion-diameter correlation; the cation–CO₂ k and the MDEAH⁺ energy; the CO₂ permittivity coefficients set in this work; no dielectric decrement; the arbitrary MEA permittivity pair; chain versus sphere cations. | §5.5 |
| 12 | Jakobsen: the carbonate share comes from the chemical shift of the merged ¹³C bicarbonate/carbonate signal (fast exchange), calibrated against standards; the authors call carbonate "most likely overpredicted" (p. 9895). The Tong MEA R4 is Aroua et al. 1999's titration constant extrapolated to zero ionic strength, i.e. measured, not model-regressed (Tong Table 5, p. 44; Aroua Eq. 14). | §4.1.2, §2.4 |
| 13 | DEA tie rule: §3.3 now says the two DEA solutions agree within optimizer tolerance and that the outside-fit pressures had been inspected before the lower one was reported, so they are development data for that choice. | §3.3 + TODO Q8 |
| 14 | 27 MDEA states: 23 shown by the search's own trials, four only by an earlier trial composition; a two-phase calculation converges at 16 of 27 (prose-checked against `phase-search-421/measured-phase.json`). Kuranov 81/82 is left as TODO Q8. | §4.4 |
| 15 | Figures, all through producers: Fig. 2 log–log parity with a 1:1 line; Fig. 5 colored by temperature, filled if fitted (fitted rows matched by id); Fig. 7 R5 line drawn on top (black, zorder 4) and Hartono/Tong measured states as plus signs; Figs 8 and 10 legend titles ("Temperature …; filled: fitted"); Fig. 10 log loading axis; Fig. 13 colored by temperature with a color bar. Table 10 header definitions moved to footnotes a–d. Eq. 6 states the L/mol → m³ conversion. No near-empty page remains (every page has more than 80 words). Captions updated. | `dea_displays.py`, `f2_figures.py` |
| 16 | Data availability: the version and solver bookkeeping moved verbatim into the deposit README (`scripts/stage_manuscript_deposit.py`, new "Package versions and linear solvers" section). The stager now also deposits `shared-bicarbonate-417/{mea,mdea,reported-mdea}/` (the three Table 8 MDEA fits), so the text can say the deposit holds both AMP fits and all three. The DOI placeholder is kept. | `data_code_availability.tex`, stager |

### Deferred to #432 (TODO locations)

| Question | Location | Reason |
|---|---|---|
| Q1: AMP fits at identical absolute pressures | `transfer_results.tex`, §4.2 after the worked split | The grid pressures are multiples of each fit's own bubble pressure. The text now says so but has no paired values. |
| Q3: conditions of the two k = 0.1325 splits, and the 0.7650 / 1.0 sets at those states | `main.tex` abstract; `transfer_results.tex` §4.3 | "Introduces" was dropped from the abstract ("its searches confirm calculated splits"). The pairing needs the calculation. |
| Q8: second DEA solution and the tie rule actually used | `data_methods.tex` `P:methods-starts` | Record read pending. |
| Q8: Kuranov 81/82 accounting | `transfer_results.tex` §5.3 | Table 11 says 70 fitted + 12 not fitted = 82. The 12th (a 393.16 K row, per the MDEA notebook) is not yet stated in the text. |

Not on the text list and therefore not addressed: Q2 (free-slope fit at 373–393 K), Q4 (P_src), Q5 (pH), Q6, Q7, and the #427/#424 pending sentences, which are unchanged.

### Build and checks

- `scripts/build_manuscript.sh`: passes. Main 33 pages, supplement 35; no undefined references or citations; 0 overfull boxes in either log. A first build added one overfull box in Table 10; the column widths were reduced to fix it.
- `dea_displays.py --check` (25 displays, 99 sources, every prose string), `final_rerun_tables.py --check` (18 tables) and `--reference-states --check`: pass.
- `python3 scripts/check_private_source.py`: passes.
- CSE `check_prose.py`: one hit ("regression") fixed. The remaining STYLE.md:67 advisory is the existing row flagged in fix round 1.
- The graphical abstract is identical to `main`.
- `figures/generated/pressure-uncertainty.pdf` came out byte-different when `f2_figures.py` was rerun. It is not used by either document, so it was restored to the committed version; the cause of the byte difference was not investigated.

### Open questions

1. Privat, Gani and Jaubert 2010 and the Polishuk papers on SAFT artefacts are not in the Zotero library, so they are not cited. Should they be acquired and read for §5.5?
2. Mouhoubi et al. 2020 (eNRTL predicts DEEA–MAPA demixing) is in Zotero but not in the `.bib` files. It is not cited; Tsanas 2022 carries the point.
3. Aroua's R4 constant is on a molar (dm³/mol) basis, while Tong's Table 5 caption says mol/kg. Since Δν(solutes) = +1 for R4, the basis difference is about ln ρ_w ≈ 0.01. This was not checked against the Engine declaration.
4. Jakobsen et al. judge their carbonate "most likely overpredicted". This bears on the carbonate deficit (§4.1.2); the text now cites it, but the deficit's attribution is unchanged.
5. No record was found giving a reason why the MEA 15/45 wt % pressures were not fitted. The text describes only their use.
6. Highlight 4 is exactly 85 characters, the Elsevier limit.
7. The judgement that the AMP splits are artefacts is the Writer's wording of the owner's request. The owner should confirm it before submission.

## Text pass 4 (round-3 evidence)

**Basis.** The text-pass-4 Writer brief of 2026-11-24: the merged #432 round-3 handoff (`analyses/round_3/manuscript-handoff.md`), the #432 reference-pressure correction, the #433 AMP split diagnosis (`analyses/mea_parameter_bundle/results/split-diagnosis-433/README.md`) with the owner's decision on its wording, and the research child's SAFT-precedent list. No calculation was run and no retained record was edited. Every new number is in the "Text pass 4" section of `429-story-pass-number-sources.md`; `STYLE.md` has a new "Text pass 4 (AMP split status)" row.

### Applied

| Item | Where |
|---|---|
| Q1: both AMP fits at equal absolute pressures (14 of 15 confirmed vs none; the second fit's descent at the worked state is toward a vapor, below its own 1.238 MPa bubble pressure) | §4.2; S7.3 |
| Q2: the 18 Hartono and 25 Tong pressures at 373–393 K, one liquid, all underpredicted (28.1/25.3 vs 28.3/25.5 %); two-liquid set lowest at Hartono row 9 and Tong row 9; two-liquid bubble pressures below the measured ones; the four Tong readback misses and the Tong row 13 failure stated as such | §4.2; S7.3 |
| Q3: conditions and ΔG/RT of the two k = 0.1325 splits; the 0.7650 and 1.0 sets converge to one liquid with no descent and no two-liquid result; the abstract now says "two calculated splits at states where none was found with the original value" (mirrored in the preprint abstract and cover letter) | abstract; §4.3; S7.1 |
| Q4: R1–R3 reference states at the system pressure, R4–R5 at 0.1 MPa; 1.734 MPa only as the S15 example. Table S15 prints R1 and R3 on the common-molality basis of Eq. S-conversion (the producer now writes `tables/mea_reference_state.tex` and asserts that ln K + Γ equals the #428 value; the #428 file is untouched). One sentence gives the 100 kPa alternative | Section 2, nomenclature, S3, Table S15 |
| Q5: carbonate-pool split at 8 Jakobsen states and the pH comparison against Hessen Fig. 6 and Matin Fig. 1, with the unreported electrode pressure and activity scale and the R1/R2 pH difference; no attribution | S2.2 |
| Q6: S14 certificate (residuals; smallest TPD +0.0307 over five starts, +0.0382 on the vapor branch) | S3 |
| Q7: search recall 93/93, 0 new in 573; 57 keys without archived pressure reported as not compared | S7.1 |
| Q8: DEA tie (costs, tolerance, second solution's parameters, deviations and phase result; its outside-fit deviations were not retained); Kuranov 82 = 66 + 4 fitted, 11 + 1 not fitted, 22.1 vs 19.1 %; water fit conditions and deviations | Section 3; S7.2; §5.3; S1.2 |
| #433: "judged to be artefacts" replaced by one sentence (calculated predictions of the free-slope fit, controlled by the fitted AMPH⁺–water temperature coefficient, neither confirmed nor excluded by any measurement used). Supplement: term curvatures, slope-only control, exact Figiel Eq. 9 average (0.64 %), Born-off result, and the 262.9 MPa MDEA case (composition, curvature terms, Born-off unresolved). §5.4 now says the exact average was evaluated only at the worked AMP split | §4.2, §5.4; S7.1, S7.3 |
| SAFT precedents: Privat 2010, Yelash 2005, Polishuk 2010, Ascani and Held 2021, Yang 2024 (one sentence) followed by "The calculated AMP and MDEA splits are predictions of the stated models, and no measurement used here tests them." | §5.5 |
| `references.bib` refreshed with `scripts/cited_bibliography.py`, run on `main.aux` and `supplement.aux` only (a scratch copy, because the ignored stale `builds/part2*.aux` would otherwise be read). Output: 100 entries; the 7 keys owned by `transfer_sources.bib` were removed so each key has one owner, leaving 93. The refresh adds the four new SAFT entries, drops 24 uncited entries, and updates the others to the current Zotero export | `references.bib` |

### Build and checks

- `scripts/build_manuscript.sh`: passes. Main 34 pages, supplement 37; no undefined references or citations; 0 overfull boxes in either log; BibTeX 0 warnings.
- `dea_displays.py --check`: 25 displays, 106 source files, every prose string, including a new "Round-3 calculations" block that rebuilds the new checked numbers from `analyses/round_3/results/` and asserts the Q1 counts, the Q2 sign, and the Q3 outcomes of the 0.7650 and 1.0 sets.
- `final_rerun_tables.py --check` (18 tables) and `--reference-states --check`: pass.
- `check_private_source.py`: passes. CSE `check_prose.py`: terminology passes; the STYLE.md:67 advisory is the existing one.
- No `TODO #432` remains. The graphical abstract is identical to `main`.
- Not done: a page-by-page visual read of the rebuilt PDFs.

### Open

1. Kuranov row 72 (393.16 K, 1.205 MPa) is not fitted (`kuranov-published-422/kuranov-rows.json` group `Kuranov-393K`) and is in no group of `shared-bicarbonate-417/mdea-comparison.json.gz`, whose Kuranov groups are 66 loaded, 11 at 413 K and 4 binary; it is therefore outside the 54 + 121 outside-fit pressures of Table 8. No retained record gives the reason it was left out of both. The text states the count only.
2. The water fit's "23 heat capacities" is a constant written in `analyses/round_3/records.py`, not counted from fit rows.
3. Hartono and Svendsen 2009 is cited only through Hessen et al.'s Fig. 6; the pH points are figure read-offs.
4. The previous open questions 1 (SAFT artefact papers), 4 (exact Figiel average) and 7 (artefact wording) are closed by this pass; the others are unchanged.

## Revision pass (adopted #435 models, round-4 referees)

Stage handoff of the Writer, 2026-11-24. Branch `issue-429-story-pass`; issue [#429](https://github.com/tannerpolley/Amine-Thermodynamics/issues/429). Not merged.

### What this stage did

The manuscript keeps its story and title: MEA calibration, transfer to DEA, MDEA and AMP, phase stability. The archived reframe (tag `archive/429-diagnostic-reframe`) is not used for framing or prose; its display producers (`dea_displays.py`, `final_rerun_tables.py`, `cited_bibliography.py`) were reused because they generate the adopted numbers, and their prose-check block was rewritten for this text.

- **Models.** Every number is from the adopted #435 records (`analyses/mea_parameter_bundle/results/salt-anchored-435/manuscript-handoff.md`). The shared water–bicarbonate and water–carbonate interactions are fixed from sodium-salt osmotic data (Section 2.2, S1.3); the fits with the MEA-fitted value 0.765 are the comparison (“MEA-fitted shared set”, Table 8).
- **AMP.** The model is the fit to all 105 loaded pressures with the slope fitted (−52.0 ± 63 K). The first fit and its 73 splits are one finding in Section 4.3; the −150 K fit is a sensitivity in S7.3.
- **Structure.** Results: 4.1 MEA, 4.2 transfer (DEA, MDEA, AMP, effect of the salt-fixed interactions), 4.3 phase stability; Section 5 “Discussion”. Moved to the supplement: the carbonate-share, density, 15/45 wt % pressure, pressure-residual and water–DEA binary figures, the DEA binary table, the table of MDEA fits at other water–bicarbonate values and the Hong stability claim.
- **Length.** Main text 33 → 27 pages; six body sections 11,016 → 9,065 words. Supplement 35 → 47 pages.
- **Decisions recorded.** `docs/scientific/writing/STYLE.md`, row “Revision pass (adopted salt-anchored models)”.

### Evidence and verification status

- `scripts/build_manuscript.sh`: passes; no undefined references or citations, no overfull boxes, BibTeX without warnings.
- `dea_displays.py --check` (27 displays, 154 source files, every prose string), `final_rerun_tables.py --check` and `--reference-states --check`: pass.
- `scripts/check_private_source.py`: passes. CSE `check_prose.py` on the sources and submission files: terminology passes; the STYLE.md advisories are the existing ones.
- `submission/graphical_abstract.tex` is identical to `main`. `references.bib` was regenerated with `scripts/cited_bibliography.py` (seven entries added).
- Referee response: `docs/scientific/latex/builds/round4-response.md`, every major and minor comment of the four round-4 reports.
- Numbers: `429-story-pass-number-sources.md`, section “Revision pass”.
- Not verified by this stage: no calculation was run; the prose check covers the headline numbers, not every number in the supplement text. The CSE `BANNED.md` is the plugin's file; the repository has none of its own.

### Open questions

1. #424 (shared parameters released) and #427 (multistart) remain open and are stated as limits.
2. The deposit DOI is a placeholder; the graphical abstract was not updated to the adopted models.
3. Not calculated for the adopted models: a reweighted MDEA refit, the AMP search above 393.15 K, the reference-pressure comparison at the 121.3 MPa MDEA split, the electrode pH comparison, the eigenvalue test and slope profile for the AMP model, fixed-pressure recovery of the 222 unfinished MDEA searches at measured states.
4. The AMP carbamate inputs are those of the MEA fit with the MEA-fitted shared set, not of the MEA model.
5. The MDEA and AMP pressure figures are scatter panels without temperature coding; Fig. 8 has no companion panel.
6. STYLE.md keeps a 2026-11-19 row saying the MEA–water figure stays in the main text; it was already in the supplement at the start of this stage and was left there.

### First action for the next stage

Read `builds/main.pdf` as a fresh referee against `round4-response.md`, starting with Sections 4.2.4 and 4.3, and decide whether the open items of point 3 need calculations before submission.

## Round-7 prose pass (Writer, 2026-11-25)

**Basis.** Owner adoptions of 2026-11-25 on #429. #435 stays the MEA model. The adopted receivers are the broadened DEA fit, the pressure-weighted salt MDEA fit and the corrected-input AMP fit. Numbers come from `analyses/round_7/manuscript-handoff.json` and its result records. No calculation was run, and no display or script was edited.

**What changed.**
- **Prose-gap list.** All 71 entries of `436-rebind-prose-gaps.md` are resolved in the main text, supplement, preprint abstract, cover letter and highlights, including the AMP donor statement at `transfer_results.tex:219`. The deposit sentence now carries a `% PENDING` comment: `scripts/stage_manuscript_deposit.py` does not yet stage the round-7 fits.
- **DEA failures.** Weiland et al. measured densities of a single liquid at four states: 298.15 K, 30 wt% at α 0.45 and 40 wt% at 0.40, 0.45 and 0.50. At all four the broadened DEA fit confirms a liquid–liquid split. These are reported as model failures in the abstract, highlight 4, §4.3, §5.4 and the conclusions. One more descent is unresolved, and one search is unfinished.
- **MEA.** §4.1.5 states that the full-weight expanded fit is a sensitivity, with its gains and costs and the source conflict. The Jou value is 46.8 kPa at α 0.349, and the Ma'mun value is 83.6 kPa at α 0.350, read from `Combined_VLE.csv`. The owner's 82.8 kPa is an interpolation and was not used. §4.1.5 also gives the Kim 393 K heats from Table S10. §5.4 says the model does not support regeneration-duty estimates. §5.2 says Ma'mun is underpredicted at every point.
- **121 MPa.** §4.3 and S3 state the reference convention. The split is confirmed with tracking references. At 100 kPa the case is unresolved. The pressure-tracking correction is −15.7 % of the EOS volume.
- **Round 6.** The new `round6-response.md` covers all four reports.
- **§4.2.4.** Retitled “Shared interactions and calibration choices”. It compares the adopted fits with the first fits and states the MDEA shared-set result under both weightings.

**Checks.**
- `scripts/build_manuscript.sh` passes: main 28 pages, supplement 49, no undefined references or citations, no overfull boxes.
- `dea_displays.py --check` passes (32 displays, prose strings included), as do `final_rerun_tables.py --check` (21 tables) and `analyses/round_7/handoff.py --check` (1061 quantities).
- `check_private_source.py` passes. The CSE prose terminology check passes; the STYLE.md advisories are the existing ones.
- `cited_bibliography.py` reproduces `references.bib` unchanged.
- The graphical abstract is untouched.

**Open.**
1. Should the deposit stager include the round-7 fits before submission?
2. Fig. 4 (DEA) still mixes solid and dashed model lines, which the caption no longer explains. The figure producer should state the line-style meaning or drop it.
3. The MDEA trial-phase classification at the 25 measured descent states was not repeated for the adopted model. Its trial branches now read “mixed”, “vapor” or “none”. S7.1 says this. A by-source table of deviations at these states is still requested by referees.
4. The adopted MDEA split at 204.054 MPa has no reference-convention test.
5. `429-story-pass-number-sources.md` was not extended for this pass. Every new number is cited in `round6-response.md`, or comes from the record keys of the prose-gap list.
6. #424, #427 and the DOI remain open.

**Next stage.** Run a fresh referee round on `builds/main.pdf` and `builds/supplement.pdf`, starting with §4.3 (DEA failures) and §4.2.4.

## Round-8 prose pass (Writer, 2026-11-25)

**Basis.** The investigator promoted the round-8 notebook (`analyses/round_8/notebook.qmd`, main `5953bd802`, #439) on 2026-11-25 for this prose pass, subject to each item's recorded disposition: C1, C4 and C6 narrowed; the DEA caloric step spread and the 100 kPa control at 204.054 MPa unresolved. `origin/main` was merged first. No calculation was run, and no generated display or script was edited. Every item of the round-7 referee list is answered in `round7-response.md`, with locators.

**What changed.**
- **C1.** New Eq. 9 in §2.3 relates ∂G*/∂P to V_EOS, with R1–R3 tracking. §2.4 adds the caloric check: 3×10⁻⁸ to 7×10⁻⁶ kJ/mol amine at the 0.01 K step, with the DEA step dependence unresolved. S3 gives the sizes at four fitted states and at the 204.054 MPa split, the chain terms, and the 100 kPa control (unresolved).
- **C2.** The MDEA model has two confirmed splits, 204.054 MPa (grid) and 262.862 MPa (targeted). This now appears in the abstract, §4.3, the conclusions and S7.1. The 25 measured descents are classified for the reported model: all point toward a vapor, below the model bubble pressure.
- **C3 / T1.** DEA four-row density AARD 0.148 % (0.447 % on 44 rows); row-31 split fractions, densities and compositions. The Weiland method (hydrometers; samples mixed from unloaded and CO₂-saturated portions) was verified in the Zotero PDF, p. 378.
- **C4.** The AMP model confirms 0 of 6 measured-state splits; 4 are unresolved and 2 have no descent. Main text now covers the R5 continuation (93/93 → 0/93), credits the removal to the refit as performed, and rewrites the "no warning" sentence.
- **C5.** S1.3 gives the salt target, residuals and the six charge-closure refusals. S4.1 gives the MDEA 2×2 on identical rows. The Carson trade-off (5.12 → 18.69 %) now sits beside the pressure gain.
- **C6.** S4 compares the two low MDEA endpoints. §5.4 limits the MDEA statements to the reported endpoint.
- **C7.** Kuranov is matched by row (ours) and by count (published). Kamps is compared on the 27 common rows, and the missing row (Ermatchkov Table 6 row 13; bubble calculation at its iteration limit) is named. The Hong equal-fugacity label is in §5.2 and S9.
- **T2, T3, T5, T6, T7** applied. **T10** was already in place.
- The abstract is 250 words and every highlight is at most 82 characters. The graphical abstract is identical to `main`.

**Checks.**
- `scripts/build_manuscript.sh` passes: main 30 pages, supplement 51, no undefined references, no overfull boxes.
- These pass: `dea_displays.py --check` (32 displays, prose strings), `final_rerun_tables.py --check` and `--reference-states --check`, `analyses/round_7/handoff.py --check`, `analyses/round_8/handoff.py --check` and `check_private_source.py`.
- The CSE prose check passes on terminology. The STYLE.md advisories are the existing ones.
- `cited_bibliography.py` reproduces `references.bib` unchanged.

**Open.**
1. Display requests, each with its record key, are in the last table of `round7-response.md`: Table 8 MDEA split count, an MDEA outcome table, an MDEA 2×2 table, a salt-residual figure, Table 9 and Hong headings, Figs 5–6 and 8, and the Kiepe marks in Tables 2, S14 and S19 (T4, T8, T9).
2. #424, #427 and the DOI remain open. The deposit stager does not include the round-7 fits.
3. No unfitted comparison-pressure state was evaluated for the C1 correction size.
4. `429-story-pass-number-sources.md` was not extended. Every new number traces to the round-8 record keys in `round7-response.md`.

**Next stage.** A fresh four-referee round on `builds/main.pdf` and `builds/supplement.pdf`. Start with §2.3 Eq. 9, §4.3 and S7.1, then decide which display requests to build first.

## Round-9 prose pass: fixed 100 kPa references (Writer, 2026-11-25)

**Basis.** The investigator promoted the #440 notebook (`analyses/fixed_reaction_reference/notebook.qmd`, main `5023dbc44`) on 2026-11-25 for this prose pass, subject to its recorded dispositions: the MDEA fit is provisional, every endpoint misses the strict projected-gradient check, C6 is open, and the open and undecided keys are stated as limits. No calculation was run. Numbers come from `manuscript-handoff.json`, the #440 result records and the rebound displays. Two owner decisions were taken in this stage, both through the question tool:
- The comparison with system-pressure references is a supplement sensitivity. The main text gives one sentence. This is recorded in `STYLE.md`, row “Reaction-reference convention”.
- Only the expected prose strings of the `dea_displays.py` prose check were updated, and they are now read from the #440 records.

**What changed.**
- **Prose gaps.** All entries of `440-rebind-prose-gaps.md` are applied, in the main text, supplement, highlights, preprint abstract and cover letter. Three rows had no prose number to change: supplement 374 (a figure environment), and the Böttinger and restriction-sequence displays, which are generated.
- **Model and methods (A1/S1).**
  - §2.3 states the fixed 100 kPa convention. It rewrites Eq. 9 so that the pressure derivative of G* is V_EOS, and it says which property comes from G*.
  - §2.3 and §2.4 give the C1 numerical verification at named states (S3, Table S32), including the MEA and DEA envelope caveat.
  - One main-text sentence and one S3 paragraph give the system-pressure sensitivity.
- **Multistart (S4).** The new treatment is in §3.3, §5.4 and S4: three tied starts, the AMP fixed-slope minima, MDEA provisional, and the gradient misses stated plainly.
- **Phase results.**
  - DEA: feeds 32, 41, 42 and 43 confirmed, feed 31 unresolved, plus one unresolved Lawson–Garst state.
  - MDEA: no confirmed split, and the 204 and 263 MPa cases unresolved.
  - AMP: the 666 bubble-scaled states are separated from the six measured-pressure controls everywhere.
  - Hartono 18 at 373–393 K and Tong 40 at 313–393 K.
  - Both split-removal changes are stated, and suppression need not improve the pressure fit.
- **Other round-8 items.** Salt qualification and Wangler positioning in §2.2. Kuranov is unranked. Hong failures are attributed to the reconstruction. Ma'mun is 38.66 % against 21.03 %. The 14.46 MPa subset is named. Version and reproduction wording are in the availability statement.
- **Abstract and highlights.** Both are rewritten. The abstract is 248 words by `wc` on the PDF text, which counts “%” and “CO2 )” as separate tokens. Every highlight is at most 84 characters. The graphical abstract is untouched.

**Checks.**
- `scripts/build_manuscript.sh` passes: main 30 pages, supplement 56, no undefined references or citations, and no overfull boxes.
- These pass: `dea_displays.py --check` (35 displays, 168 sources, prose strings), `final_rerun_tables.py --check` (21 tables), `analyses/round_7/handoff.py --check`, `analyses/round_8/handoff.py --check`, `analyses/fixed_reaction_reference/handoff.py --check` (2619 quantities) and `check_private_source.py`.
- The CSE prose check passes on terminology. The STYLE.md advisories are the existing ones.
- `cited_bibliography.py` reproduces `references.bib` byte for byte against the current Zotero export, so no entry changed.

**Response.** `round8-response.md` answers every item of `r8-items.md` with a locator or states why it stays open. Display requests D1–D8 are listed there.

**Open.**
1. Display requests D1–D8: Table 8 rows, the AMP six-row control table, a salt worked row, the Hong table heading, Kiepe labels, MDEA descent compositions, start IDs, and the remaining “tracking” labels in Table 9 and S44.
2. A4: the DOI is a placeholder. Reproduction with 1.3.2 was not run. The public tag `v1.3.1` is not the commit behind the 1.3.1 build (`05e94210`, on public `main`).
3. S1: continuation of the aqueous reference roots below water saturation is not described, because no record was found.
4. C6, the same-band endpoint spread, is stated as a limit (§5.4).
5. S7: the deposit stager predates the adopted fits.
6. The 132-row Hong table carries a column of 22.59 % next to the MEA model's 25.06 %. The caption does not say which fit that column is, and the C7 handoff key labels 22.59 as tracking. If it is the MEA model with system-pressure references, it differs by 2.5 points from the fixed-reference value on unfitted pressures, which is larger than the fitted-pressure sensitivity quoted in §2.3. This was not investigated.
7. The statement that the Austgen-type correlations depend on temperature only rests on Eq. 10's form. The low-pressure origin of their data was not re-read.

**Next stage.** A fresh four-referee round on `builds/main.pdf` and `builds/supplement.pdf`. Start with §2.3–2.4 and S3 (C1), §3.3 and S4 (multistart), and §4.3 and S7 (phase).

## Round-10 prose pass: round-9 referee items (Writer, 2026-11-25)

**Basis.** On 2026-11-25 the investigator promoted the round-9 notebook (`analyses/round_9/notebook.qmd`, commit `517d0b982`) for this prose pass. The promotion is subject to its limits: the MDEA fit is provisional, the MDEA alternative with the MEA-fitted shared set stopped at its iteration limit, phase identities hold only for the tested declarations and starts, and experimental confirmation of phase identity is open. No calculation was run, and no generated display or script was edited. `round9-response.md` answers every item of the round-9 list with a locator.

**What changed.**
- **DEA (§4.3).** The worked split at 30 wt % and α 0.50 is in the text, with Table S48 cited for all four certificates and for the B matrix of Eq. 17. The daughter restart coalesces and the neighboring-state start reproduces the split; the text says both. The density measurements do not establish the phase count.
- **AMP (§4.3).** The 2.037 MPa common-pressure control and the six measured-pressure controls are in the text, citing Table 10. §4.3 ends on the measured-pressure outcome and the slope control, without “remedy”.
- **MDEA.**
  - §3.3 gives 63 tested draws, one evaluable, and the endpoint from inherited start A.
  - The stopping tests are separated from the projected-gradient criterion.
  - §4.3 gives attempted and completed search counts and the 27 states (10 measured, 17 assigned pressures).
  - The 204 and 263 MPa controls are out of the main evidence.
- **Shared set (§4.2.4).** The 100 kPa sensitivity (Tables S49–S50) is a new last paragraph. The historical trade-off is marked as arising under system-pressure references.
- **Other changes.**
  - Eq. 9: the follow-on sentence names the additional reference-derivative term.
  - C1 wording, with 10.5 % and 8.9 %, is in the abstract and conclusions.
  - Hong reconstruction outcomes are only in S9.
  - The introduction positions Tsanas et al. and Rodríguez et al.
  - Also changed: Kiepe 268 of 307; the MEA 321/246 screen; the AMP 270/6 terms; the salt zero-species rows; Fig. 7 and S41 brackets as numerical resolution; the deposit package description.
- **Abstract.** 250 words by `wc` on the PDF text, with each observable named. The preprint abstract and cover letter are synced. The highlights and graphical abstract are unchanged.

**Checks.** `scripts/build_manuscript.sh` passes: main 31 pages, supplement 62, no undefined references or citations and no overfull boxes. These pass: `dea_displays.py --check`, `final_rerun_tables.py --check` and `--reference-states --check`, the round-7, round-8, #440 and round-9 `handoff.py --check`, and `check_private_source.py`. The CSE prose check passes on terminology.

**Bibliography.** `cited_bibliography.py` gives the same entries and fields as the committed `references.bib`. The current Zotero export now ends each entry's last field with a comma, and adopting that would change the line whose hash `check_private_source.py` pins, so the committed file is kept. Whoever owns that check should update the pinned hash before the next refresh.

**Open.**
1. R5 deposit (owner): build the reproducibility package for the referee packet. The DOI is assigned at submission. The `% PENDING` comment in the availability section stays until the contents are confirmed.
2. Display requests D1 (Table S32 definitions and pressure type) and D2 (move Table 10 into §4.3).
3. The bibliography trailing-comma format against the pinned private-source line hash.
4. Items carried from earlier rounds: C6 endpoint spread, the 1.3.2 reproduction, and the v1.3.1 tag.

**Next stage.** A fresh four-referee round on `builds/main.pdf` and `builds/supplement.pdf`, starting with §4.3 (DEA worked split, AMP controls), §3.3 and §4.2.4.

## Round-11 prose pass: round-10 referee items (Writer, 2026-11-25)

**Basis.** The evidence is the round-10 study (`analyses/round_10/notebook.qmd` and `manuscript-handoff.json`, commit `609adcc26`). It is **not promoted**: asked on 2026-11-25, the investigator answered “keep working on this”. The investigator also directed that nothing that fails, such as 62 of 63 MDEA drawn starts failing at their first evaluation, may appear in the paper as acceptable. The investigator rejected the word “provisional”. No calculation was run in this pass, and no generated display or script was edited. `round10-response.md` answers every item of `r10-items.md` with a locator or the reason it stays open.

**What changed.**
- **K1.** §4.2.4 has a new last paragraph with Table S51, and §S4 and §5.4 are updated. The tied MEA, DEA and AMP endpoints differ by at most 0.0004, 0.0014 and 0.0002 percentage points in AARD. Each difference is more than 1,000 times smaller than the deviation from the measurements. The two MDEA continuations agree within 0.0002 points. LHS-53 is reported as a separate, much worse basin.
- **§4.2.4.** The section now opens with the matched 100 kPa comparison and states its weights, bounds and stopping. The Table 8 comparison fits follow, then the MDEA weighting reading.
- **Phase results.**
  - K2: the MEA parent counts (149 and 13), and the AMP outcome wording in the abstract, §4.3, Fig. 8, §S7, the conclusions and the cover letter.
  - K3: DEA bulk density, 0.113 % for one liquid against 0.155 % for two, with the pressure called assigned.
  - K4: MDEA bubble pressures at the 10 measured-pressure descents.
- **Literature (§5.2).**
  - The section now leads with Ma'mun and Ermatchkov and gives each model's fit or development role.
  - Kamps is shown on 28 and on 27 rows, and the count-matched Kuranov values are listed unranked.
  - The DEA excess-enthalpy sign comparison and Smith et al. are added. Smith et al. was read in the Zotero PDF, and its Zotero metadata was corrected.
- **Other text items.**
  - The abstract and conclusions give the C1 resolutions against the observed differences, and §2.3 gives the full values.
  - §2.4 has the AMP zero caloric reference.
  - The availability statement gives the wheel first, the check name and both DEA identifiers.
  - Also done: Eq. 17 definitions, highlight 1, the Kiepe count in §3.1, the 0.070 ratio in §5.3, and the Fig. 7 bracket.
- **Abstract.** 250 words by `wc` on the PDF text. The preprint abstract and cover letter are synced, and the graphical abstract is identical to `main`.

**Checks.**
- `scripts/build_manuscript.sh` passes: main 32 pages, supplement 64, no undefined references or citations, no overfull boxes.
- These pass: `dea_displays.py --check` (43 displays), `final_rerun_tables.py --check` and `--reference-states --check`, the round-7, round-8, #440, round-9 and round-10 `handoff.py --check`, and `check_private_source.py`.
- The CSE prose check passes on terminology.
- `references.bib` was regenerated with `cited_bibliography.py` and gained only `smithGibbsEnergyMinimization`.

**Open.**
1. **MDEA start failures (owner direction).** Diagnose why 62 of 63 drawn MDEA starts fail at their first evaluation. The #440 notebook says “feasibility undecided”. B and C miss the 1.121 MPa target. Of the 60 replacement draws, 28 are equilibrium non-convergence, 24 have no admissible saturation root, 5 hit the iteration limit and 3 are ill-conditioned. Then decide the MDEA wording. “Provisional” remains 12 times in the prose and 8 times in tables.
2. **Promotion** of `609adcc26` for K1–K4.
3. **Display requests** D1–D4 (`round10-response.md`).
4. The stopping status of the Table 8 system-pressure comparison fits is not in any promoted record.
5. **Deposit.**
   - The README ID fix (`17c122356`) is on `main` and not merged here.
   - The deposit lacks the round-10 records.
   - The DOI is assigned at submission.

**Next stage.** The orchestrator routes item 1 to a diagnosis stage (`cse:diagnose`). Its first action is to reproduce LHS-15 (equilibrium non-convergence) and LHS-57 (saturation slope reversal) on the study wheel, and to separate solver failure from an absent root. A Writer then applies the resulting MDEA wording, and then a fresh referee round follows.
