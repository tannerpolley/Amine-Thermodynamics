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

