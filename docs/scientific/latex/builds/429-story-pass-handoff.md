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

1. Table S20 keeps the retained DEA A₄ bounds (2.098 to 8.098) beside level bounds of −3 to +3 on the starting-law basis. I could not reconcile the two from the records.
2. Austgen 1989 has no PDF in Zotero; its sentence states only what the abstract supports.
3. The split of citations between Perdomo 2025 and the reacting-constraint papers follows the plan; I did not re-read those papers.
4. The exact Figiel average is still unevaluated.
5. The cover letter and preprint abstract were synchronized; the suggested-referee file was not touched.

## First action for the post-draft checks

Read `builds/main.pdf` front to back as a fresh referee and grade each section, starting with whether Sections 4.2 and 4.3 support the abstract's two claims from the tables alone; then spot-check the unchecked rows of the number-sources file.
