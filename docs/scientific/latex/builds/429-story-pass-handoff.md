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
