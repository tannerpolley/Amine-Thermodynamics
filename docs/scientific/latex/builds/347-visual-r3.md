# Part I visual pass: fix round 3

This revision applies only the owner's approved round-3 items on `69b7e3c`.
No retained numbers, figures, producers, table contents, chemistry macros or
bibliography entries change. The two specified Part II sentences are the only
Part II source edits. All four PDFs are rebuilt through `agent-heavy`.

| Item | File | Applied change |
| --- | --- | --- |
| Science 1 | `supplement.tex` | Uses the two prescribed sentences: pressure fractions are fixed search inputs, and the adopted parameters use the 162 prescribed states without recomputing their pressures. |
| Visual 2 | `sections/data_methods.tex` | Adds `\needspace{36\baselineskip}` immediately before Table 2, using the existing package. Caption and complete table start on page 7; text and columns are unchanged. |
| Story 3, heading | `sections/mea_system_modeling_results.tex` | Uses “Phase stability of the adopted model” and preserves `sec:phase-method`. |
| Story 3, paragraph | Same file | Uses the three prescribed sentences in order: literature rationale, Böttinger observation with its domain limit, and the adopted-model result tied to Section 3.4. The following 6121-composition sentence is unchanged. |
| Part II 4, introduction | `sections/part2/introduction.tex` | Replaces the discarded-fit claim with the exact Held2014 rationale and Part I Section 3.4 reference. |
| Part II 4, methods | `sections/part2/methods.tex` | Replaces only the prescribed penalty explanation with “a calculated second liquid” and Part I Section 3.4. |

Böttinger retains the existing `Bottinger2008` key and Section 3 locator.
`Held2014` resolves in the Part II bibliography. No bibliography refresh or
entry edit was needed.

`347-visual-r3-checks.json` records final page counts and hashes, warnings,
vector fonts, citation and source-scope checks, freshness, raster comparisons
against `7f6e29e` and `69b7e3c`, and manual inspection. The displayed-number
and prose logs and raw layout reports accompany it. Science, story and visual
focused confirmations remain open before merge.
