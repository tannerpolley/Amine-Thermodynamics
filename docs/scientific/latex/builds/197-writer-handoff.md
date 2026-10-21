# #197 Write fix round 2 handoff

Fix round 2 is applied locally. The confirming check, owner review and merge remain open; issue #197 is not complete. This record supersedes the round 1 build/page-count handoff and does not authorize publication or submission.

Branch: `issue-197-stage-3-rewrite-the-mea-manuscript-5`.
Worktree: `/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.worktrees/issue-197-stage-3-rewrite-the-mea-manuscript-5`.
The clean main-based worktree started at `ff8c84e34d55ab3c515e3ebe8b1653816e3ddc3c` and merged `issue-197-stage-3-rewrite-the-mea-manuscript` without conflict in `c6b87a52d4b135bf0aa3d63eb3983f322cdfe363`; `ea401614668f96aca9b4614cc9a11a00f93024e3` is an ancestor. Ignored review/release records were copied from that worktree. All subsequent writes occurred here. The notebook paragraph from `ff8c84e` is preserved without a round 2 edit.

The controlling records are `tmp/joint-design/write-review-story-r2.md` and `write-review-numbers-r4.md`. The r4 science ruling governs conflicts. The live #197 body was reread before handoff and is unchanged, SHA-256 `f4acadc97f2ebd3da2ccc9b963cc399bad923ae579d50847b37399de7e50595b`. The owner already promoted notebook commit `8f40c125e5945ac785cc0ad1889fc79bea2096c9` for the joint-calibration/finite-phase-test manuscript with the stated limitations. This round applies the accepted wording and citations; it does not replace the pending independent confirmation of their support.

No Engine calculation, retained-evidence change, selected-parameter edit or notebook edit occurred. The selected record remains SHA-256 `e234e8601ebc47b3dec25383ee0a0a8029cabb9f7f92c87866f595c505c7e58e`.

## Item-by-item application

Paths in the table are relative to `docs/scientific/latex/`, except the review record. The machine-readable application and location records are `tmp/joint-design/r2-fix-application.json` and `r2-item-locations.json`.

| Item | Application | File:line | Detail |
| --- | --- | --- | --- |
| 1 | applied verbatim | `sections/data_methods.tex:7`; `sections/data_methods.tex:22`; `sections/data_methods.tex:48`; `sections/data_methods.tex:73`; `sections/data_methods.tex:81`; `sections/data_methods.tex:122`; `sections/data_methods.tex:128`; `sections/data_methods.tex:145`; `sections/data_methods.tex:151`; `sections/epc_saft_equation_of_state.tex:41`; `sections/epc_saft_equation_of_state.tex:87`; `sections/mea_system_modeling_results.tex:6`; `sections/mea_system_modeling_results.tex:10`; `sections/mea_system_modeling_results.tex:23`; `sections/mea_system_modeling_results.tex:30`; `sections/mea_system_modeling_results.tex:54`; `sections/mea_system_modeling_results.tex:118`; `sections/mea_system_modeling_results.tex:146`; `sections/mea_system_modeling_results.tex:151`; `sections/nomenclature.tex:34`; `supplement.tex:103`; `supplement.tex:168`; `supplement.tex:188`; `supplement.tex:189` | All named supplement section references explicitly say Section; Table S3 is retained. |
| 2 | applied verbatim | `sections/data_methods.tex:8` |  |
| 3 | applied verbatim | `sections/conclusion.tex:17`; `sections/data_methods.tex:30`; `sections/introduction.tex:58`; `sections/mea_system_modeling_results.tex:116`; `sections/mea_system_modeling_results.tex:165`; `supplement.tex:67` |  |
| 4 | applied verbatim | `sections/data_code_availability.tex:6`; `supplement.tex:185` |  |
| 5 | applied verbatim | `sections/data_methods.tex:151` |  |
| 6 | applied verbatim | `sections/epc_saft_equation_of_state.tex:119`; `supplement.tex:155` |  |
| 7 | applied verbatim | `sections/epc_saft_equation_of_state.tex:127` |  |
| 8 | applied verbatim | `sections/data_methods.tex:47` |  |
| 9 | applied verbatim | `sections/data_methods.tex:108` | Also the exact r4 correction 5 sentence. |
| 10 | amended per r4 | `sections/data_methods.tex:123` | The three r4 correction 4 sentences replace the story sentence; subsequent limitations remain. |
| 11 | applied verbatim | `sections/data_methods.tex:128` |  |
| 12 | applied verbatim | `sections/mea_system_modeling_results.tex:30`; `sections/mea_system_modeling_results.tex:71`; `sections/mea_system_modeling_results.tex:77` |  |
| 13 | applied verbatim | `submission/cover_letter.md:7` |  |
| 14 | applied verbatim | `submission/cover_letter.md:9`; `submission/cover_letter.md:13` | Includes the exact private-Engine disclosure from r4 correction 7. |
| 15 | applied verbatim | `submission/highlights.txt:1`; `submission/highlights.txt:2` |  |
| 16 | applied verbatim | `submission/chemrxiv.md:23` |  |
| 17 | amended per r4 | `scripts/final_rerun_tables.py:40` | Whole-cell guard before parts = re.split; the proposed global regex is excluded. |
| 18 | applied verbatim | `scripts/final_rerun_tables.py:223`; `scripts/final_rerun_tables.py:288`; `scripts/final_rerun_tables.py:292` |  |
| 19 | applied verbatim | `scripts/final_rerun_tables.py:156` |  |
| 20 | applied verbatim | `scripts/final_rerun_tables.py:153` |  |
| 21 | applied verbatim | `scripts/final_rerun_tables.py:168` |  |
| 22 | amended per r4 | `scripts/final_rerun_tables.py:138`; `supplement.tex:209` | Locator table and collector removed; sources() retained; two r4 correction 1 sentences inserted after S10 attribution. |
| `flag2` | applied verbatim from r4 | `scripts/final_rerun_tables.py:31` | Single ORIGIN entry; fitted/tied precedence retained. |
| `flag3` | applied verbatim from r4 | `sections/epc_saft_equation_of_state.tex:41` | Complete water-parameter sentence. |
| `flag6` | applied verbatim from r4 | `supplement.tex:122` | First two S5 sentences replaced by the five ruled sentences; remaining paragraph retained. |
| `Gibbs-unit` | applied verbatim from r4 | `scripts/final_rerun_tables.py:311` | Exact extensive Gibbs-difference unit substring; no numerical change. |
| Story optional suggestions | not applied (optional) | `tmp/joint-design/write-review-story-r2.md` | All optional suggestions excluded. |

## Generator Build evidence

The existing table generator remains the single owner, called by the manuscript/supplement inputs and the standalone proof. This round replaces labels and deletes the unused source-locator collector and its table; `sources()` still returns provenance and qualifications. The parameter-value and figure owners remain unchanged.

Before editing, `r2-baseline-tables.json`, `r2-baseline-table-rows.json` and `r2-baseline-number-tokens.json` captured every generated table and its number tokens. `r2-baseline-reconciliation.json` captured the generator's complete printed reconciliation. All fourteen fragments preserve their quantitative cells (`r2-numeric-content-equality.json`). Every number token in every retained data/header row also agrees after normalizing the approved inherited-provenance label change (`r2-all-row-number-equality.json`); the deleted locator table is the sole removed table. Approved captions, labels and whole-cell `\mbox{}` guards change no sign or digit. Both post-edit reconciliation outputs equal the baseline exactly.

Two runs of both generators reproduce all 25 files byte for byte. Their hashes are in `tmp/joint-design/determinism.json`. The exact r4 guard passed an in-memory comparison for four negative forms and eleven nonnegative/identifier/range/chemistry examples. All six complete r4 prose replacement blocks match the review verbatim (`r2-verbatim-checks.json`). The figures did not change.

The final generated-table proof was compiled twice from `docs/scientific/latex/` with the requested `TEXINPUTS='./styles//:' nice -n 10 pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../../../tmp/joint-design/latex-check ../../../tmp/joint-design/latex-check/generated-tables.tex` command, through `agent-heavy`: **34 pages**, zero LaTeX warnings, overfull/underfull boxes, missing glyphs or undefined references/citations. Logs: `r2-table-compile1.log` and `r2-table-compile2.log`. The new Jakobsen citation required the cited bibliography in the proof. Two proof inputs use landscape pages to keep the boxed numeric cells separate; the source fragments and scientific wording were not altered for that layout. The overview and enlarged proof pages 11 and 33 show complete numbers and separate cells. The conservative proof scanner reports `review`, with 236 rotation/clearance candidates and no errors; those are not a scanner Pass.

The refreshed local release contains **703 checksum entries**, including the bibliography needed by the proof. Existing data/presentation scope is preserved. Both generators ran from a copy in an empty temporary directory, with this worktree's `.venv/bin/python -E -s`. All 25 outputs matched both the worktree bytes and `determinism.json`, the reconciliation matched, checksums passed before/after regeneration, and the isolated copy was deleted. Record: `r2-isolated-release-reproduction.json`.

Gross-added executable lines against `8f40c12`, including comments and blank lines without offsetting deletions: **616 / 700**; 551 lines removed; zero test additions. The three source-file counts are 149/0 (`a7_presentation.py`), 151/210 (`render_manuscript_figures.py`) and 316/341 (`final_rerun_tables.py`), additions/removals respectively. `tmp/joint-design/change-accounting.json` retains the final accounting. No new permanent test or helper was added.

This worktree initially lacked `.venv`; the existing environment was copied here. The pinned wheel path in `pyproject.toml` is absent, so the authorized `UV_NO_SYNC=1` fallback was used for presentation, main build and freshness. No wheel was built and no Engine source imported.

## Builds, bibliography and visual inspection

- `UV_NO_SYNC=1 nice -n 10 agent-heavy bash scripts/build_manuscript.sh`: passed, **25 main pages**, zero LaTeX/BibTeX warnings, undefined citations/references, missing glyphs or underfull boxes. One 1.9224 pt overfull box is the whole negative number in Table 4; its digits and unit remain separate and readable on page 8.
- Explicit `TEXINPUTS='./styles//:' nice -n 10 agent-heavy latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=builds supplement.tex`: passed, **44 supplement pages**, zero LaTeX/BibTeX warnings, undefined citations/references, missing glyphs or overfull boxes. One underfull bibliography hbox, badness 3514, remains on page 44 (Uyan); its text is complete.
- `UV_NO_SYNC=1 uv run python scripts/check_manuscript_freshness.py`: passed. Submission metadata `pdf_sha256`, the actual main PDF and `builds/verification-receipt.json` agree.
- `python scripts/cited_bibliography.py > references.bib` ran only after both auxiliary files existed, from `docs/scientific/latex/`. Added keys: none; removed keys: none; existing-entry drift: none; bibliography bytes unchanged. No hand edits or Zotero writes. Record: `r2-bibliography-changes.json`.
- The repository CSE prose checker passed on changed manuscript/submission prose, all generated tables, the refreshed number-source list and this handoff.

Every page of both final PDFs was inspected in color, with all five main figure pages also inspected in grayscale. Front matter, all section/table references, Table 4 on main page 8, S5 on supplement page 22, S10 on page 33 and the former locator-table position on pages 39–40 were inspected. The binary table is now S15 on pages 39–41. No clipping, missing row or colliding glyph was found. Color continues to encode source/species/loading in Figures 2–4; marker shapes retain measured/calculated and phase categories, and exact values remain in the retained tables.

The main scanner returns `fail` with 152 candidates: 149 clearance warnings, two fraction-rule graphic candidates on page 3 and one equation-superscript overlap candidate on page 7. The latter is a bounding-box false positive; rendered glyphs are separate. The supplement scanner returns `review` with 974 candidates (919 rotated-page edge warnings, 55 clearance warnings). The complete page inspection found no corresponding defect. Reports and color/grayscale rasters are in `tmp/joint-design/r2-pdf-final/`; raw scanner results are retained, not called passing.

Main PDF SHA-256: `6f9e537e108169f993764bd4ade11536733a5ae2737b445d9b65c219b2c041d4`.

Supplement PDF SHA-256: `f418ab73c76f7edc23f05e567a17cc44c80c2bbb56c43c4c75d5dbe14d4c1819`.

Logs: `tmp/joint-design/r2-main-final.log`, `r2-supplement-initial.log`, `r2-freshness-final.log`, `r2-prose-check.log`, `r2-handoff-prose-check.log` and `r2-release-reproduction.log`.

## Remaining gates

The confirming check, owner review and merge remain open. This implementor has not performed the independent confirming review. No merge into main, push, PR, GitHub comment, Overleaf synchronization, submission, deposit or DOI creation occurred. Unrelated untracked figure PDFs were not staged. Optional story suggestions were not applied.

The accepted scientific limits remain: fitted agreement is calibration; comparisons examined during model development and Arcis acceptance checks are not independent validation; the phase search covers its declared finite states; the three fitted-density failures remain failures; conditional errors are not prediction intervals; physical phase/process validation is absent; and the private Engine wheel is an omitted dependency.
