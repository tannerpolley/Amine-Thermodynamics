# Standing editorial decisions

Project-wide choices apply to both parts, both supplements and their figures.

Issue discussions record the owner directions; dates below are message dates, not adoption dates inferred from a draft.

| Scope | Standing owner decision | Authority |
| --- | --- | --- |
| All four documents | The manuscript is one snapshot of the best results and text: no "historical" results or labels, no mixed data or parameter generations. Rerun the full evidence suite once, on the final data and parameter set, rather than repeatedly. | owner preference journal (`docs/.codex-journal/user_preferences.md`), 2026-10-01; transcribed into STYLE.md 2026-11-16. |
| All four documents | Omit discarded parameter sets. The approved restriction-sequence comparison remains within scope. | 2026-11-16, [#347 owner decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/347#issuecomment-6931657641): “why would we want to write about 54 failing states for a parameter set that has been discarded?” The same message explicitly keeps Table 7. |
| Prose, captions, legends, axes and tables | Replace development labels, including F-codes and A-codes, with the quantities or model choices they describe. | 2026-11-16, [#387](https://github.com/tannerpolley/Amine-Thermodynamics/issues/387): “I see stuff like F2 in figure 2 label and I have no idea what F2 is supposed to mean ... is this not development jargon?” |
| Software descriptions | Name the epcsaft package, version 1.3.0, and cite the archive deposit. Its software index identifies the exact build file and SHA-256; no hashes appear in the paper. Do not call the software “engine”. | owner decision, 2026-11-16 (question tool), “Version + deposit”. |
| All calculations reported in the papers | Use one identified package build for all calculations; keep its immutable identity in repository records. | 2026-10-23, [#387](https://github.com/tannerpolley/Amine-Thermodynamics/issues/387): paraphrase, “Everything in the paper is calculated from one identified wheel” is the issue's summary, not a recovered verbatim owner quotation. |
| Both main texts | Each part stands alone. Supply needed content rather than replacing it with a bare pointer to the supplement or companion paper. | 2026-11-13, [#387](https://github.com/tannerpolley/Amine-Thermodynamics/issues/387): paraphrase of the recorded owner decision; the issue names bare “see Supplement §…” / “see Part 1” pointers. |
| Main-text tables | Use at most four decimal places, except fitted segment diameters, which keep five significant figures (the owner’s “Table 3”, Part I Table 3 again since the reference values moved to the supplement on 2026-11-19). Full precision in the supplement applies to coefficient and parameter tables only (for example, Part I Tables 1, 3, 4 and 10 and Part II Tables 1 and 3); full result and deviation values belong in the archived data deposit. | [#387](https://github.com/tannerpolley/Amine-Thermodynamics/issues/387), 2026-10-27/28 precision decision (paraphrase); owner decision, 2026-11-16 (question tool), “Parameter tables only”. |
| All figures | Each figure must show a useful, distinct comparison. | 2026-11-06, [#387](https://github.com/tannerpolley/Amine-Thermodynamics/issues/387), Figure 7: “worthless ... they all look the same”; 2026-10-28 Figure 9 direction is paraphrased there as unclear. |
| Data used in the series | Use only open, published data. | 2026-11-16, [#345 owner decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/345#issuecomment-6932433233): “the series is to use only open, published data.” Quotation is from the issue's record of the owner decision. |
| Correctable limitations | The paper states no limitation that can be fixed; fix it before the refit instead of documenting it. | owner preference journal (`docs/.codex-journal/user_preferences.md`), 2026-10-13; transcribed into STYLE.md 2026-11-16. |
| Scientific figures | Prefer claim-led figures as the primary display of scientific results; retain tables for exact values and provenance. | owner preference journal (`docs/.codex-journal/user_preferences.md`), undated; transcribed into STYLE.md 2026-11-16. |
| Counts in prose, both parts | Journal style: words for one to nine without a unit (“all three amines”, “one split”), numerals for 10 and above and with units. This replaces #348 item 18 (“numerals for counts”). | OWNER DECISION 2026-11-19 (question tool), [#337](https://github.com/tannerpolley/Amine-Thermodynamics/issues/337#issuecomment-7022176829), item 2. |
| Story, both parts | Tell the result, not the path to it: “we don't want to get lost in the weeds… focus on the result and not the path to the result.” Search bookkeeping, tables read back row by row and procedure narration go to the supplement or out. | Owner direction relayed in the 2026-11-19 Writer brief (quotation); scope in [#337](https://github.com/tannerpolley/Amine-Thermodynamics/issues/337#issuecomment-7022176829), item 1. |
| Phase-stability terms, both parts | A negative tangent-plane distance confirmed by a Gibbs-energy decrease is a “detected instability” (not “descent”). The line-interpolation procedure is named once and plainly, as interpolation between parameter sets (not “retreat”, not “segment shortening”). | Settled terms in the 2026-11-19 Writer brief for the [#337](https://github.com/tannerpolley/Amine-Thermodynamics/issues/337#issuecomment-7022176829) simplification round (paraphrase). |
| Section order, both parts | Results order: fitted parameters and their uncertainty, then phase stability, then the loaded-solution results. Parameter uncertainty is part of the parameters section. | OWNER DECISION 2026-11-19 (question tool), [#337](https://github.com/tannerpolley/Amine-Thermodynamics/issues/337#issuecomment-7022176829), item 4 (“in both papers”). |
| Scientific figure series | Plot observations as points and model results as continuous lines only when retained calculations support that continuity. | owner preference journal (`docs/.codex-journal/user_preferences.md`), undated; transcribed into STYLE.md 2026-11-16. |

## Part I

Sources: `docs/scientific/latex/main.tex`; `docs/scientific/latex/sections/*.tex`; `docs/scientific/latex/figures/`.

| Scope | Standing owner decision | Authority |
| --- | --- | --- |
| Series role | Part I establishes the MEA calibration before transfer to other amines in Part II. | 2026-11-12 and 2026-11-13, [#387](https://github.com/tannerpolley/Amine-Thermodynamics/issues/387): paraphrase of its series-role summary (“MEA benchmark paper”); the current Part I title uses calibration. |
| Shared-parameter table | One row per shared species; rows that repeat other tables or follow a rule go to the table note and the supplement's unrounded tables. This changes the form of #347 item 10. After the reference values moved, it is Part I Table 10, and Part II cites it as such. | OWNER DECISION 2026-11-19 (question tool), [#337](https://github.com/tannerpolley/Amine-Thermodynamics/issues/337#issuecomment-7022176829), item 3; table number: owner answer on the Writer's question prompt, 2026-11-19, “Renumber to Table 10”. |
| Reference values | The reference values for checking an implementation are in the supplement, not the main text. | OWNER DECISION 2026-11-19 (question tool), [#337](https://github.com/tannerpolley/Amine-Thermodynamics/issues/337#issuecomment-7022176829), item 3. |
| Figure 1 | The MEA–water bubble-temperature figure stays in the main text. | OWNER DECISION 2026-11-19 (question tool), [#337](https://github.com/tannerpolley/Amine-Thermodynamics/issues/337#issuecomment-7022176829), item 3. |

## Part I supplement

Sources: `docs/scientific/latex/supplement.tex`; `docs/scientific/latex/tables/supplement_*.tex`; other tables included by that source.

| Scope | Standing owner decision | Authority |
| --- | --- | --- |
| Numerical display | Apply the project-wide main-text and supplementary precision decision above. | Project-wide Main-text tables row. |

## Part II

Sources: `docs/scientific/latex/part2.tex`; `docs/scientific/latex/sections/part2/`; `docs/scientific/latex/tables/part2/`; `docs/scientific/latex/figures/part2/`.

| Scope | Standing owner decision | Authority |
| --- | --- | --- |
| Series role and literature | Transfer Part I's workflow with the same overall structure and an amine-focused literature review. | 2026-11-12 and 2026-11-13, [#387](https://github.com/tannerpolley/Amine-Thermodynamics/issues/387): paraphrase of the recorded owner decision. |
| Amine scope and order | Cover DEA (secondary), MDEA (tertiary) and AMP (hindered primary), after Part I's MEA; remove piperazine from the paper and retain its analyses. | 2026-11-16, [#337 owner decisions](https://github.com/tannerpolley/Amine-Thermodynamics/issues/337#issuecomment-6932434220): “Piperazine is dropped from Part II.” Classes are recorded in the same-day #345 decision. |
| Title | Keep “DEA, MDEA and AMP” in the Part II title; do not spell the amine names out. | owner answer on the Part II Writer's question prompt, 2026-11-17, as recorded in the [#348 completion comment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/348#issuecomment-6965576845) and relayed by the repository orchestrator (paraphrase). |
| Shared-parameter sensitivity | Part II does not compare against Part I's less restricted calibration: no comparison column, results sentence or methods mention, so every Part II number comes from one calculation build. | owner answer on the Part II Writer's question prompt, 2026-11-19: “Drop from Part II”. |
| Software version | Part II names the epcsaft package, version 1.3.1, the version of its calculations; the general software-description rule above otherwise applies. | owner decision, 2026-11-17 (paraphrase, as relayed for the Part II Writer). Part I's wording is unchanged in this round. |
| AMP reporting | The converged unpenalized fit is the AMP result; the stability-constrained alternative is shown beside it in the same tables and paragraphs, so that either can be the primary fit without restructuring. The exception to the penalty procedure is stated openly, and the text says where the splits lie, not what causes them. | OWNER DECISION 2026-11-19 (question tool), “Unpenalized + stable shown”, [#344](https://github.com/tannerpolley/Amine-Thermodynamics/issues/344#issuecomment-7019544983). |
| MDEA reporting | Report the binary-penalty result, the one liquid–liquid split at a loaded state and the vapor-directed calculations as limits; state openly that no penalized fit was made for the loaded states. | OWNER DECISION 2026-11-19 (question tool), [#343](https://github.com/tannerpolley/Amine-Thermodynamics/issues/343#issuecomment-6998481156) (paraphrase). |
| Phase-stability method | The main text keeps a self-contained summary of the phase-stability method; the detail of the stability penalty and of the interpolation between parameter sets goes in the Part II supplement. | owner answer on the Part II Writer's question prompt, 2026-11-17, as recorded in the [#348 completion comment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/348#issuecomment-6965576845) and relayed by the repository orchestrator (paraphrase). The 2026-11-19 wording of the terms follows the project-wide row above. |
| Abstract | No search bookkeeping. It carries the Ermatchkov MDEA comparison (15.36% against 16.8% for published set I, which also predicts those pressures) and states that the Ermatchkov data helped choose the initial MDEA parameters, so the comparison is not a blind test. | OWNER DECISION 2026-11-19 (question tool), [#337](https://github.com/tannerpolley/Amine-Thermodynamics/issues/337#issuecomment-7022176829), item 4. |
| Summary table by amine | Keeps its columns and values; only plain-language header or note wording may change. | OWNER DECISION 2026-11-19 (question tool), [#337](https://github.com/tannerpolley/Amine-Thermodynamics/issues/337#issuecomment-7022176829), item 4. |
| DEA carbamate-hydrolysis enthalpy increment | The fitted-parameter table keeps the increment on its zero basis (measured from the final correlation) and explains that in the note; no value relative to the starting correlation is displayed. | Owner answer on the Writer's question prompt, 2026-11-19: “Keep the zero basis, explain it”. |

## Part II supplement

Sources: `docs/scientific/latex/part2_supplement.tex`; `docs/scientific/latex/sections/part2/supplement.tex`; included `docs/scientific/latex/tables/part2/` tables.

| Scope | Standing owner decision | Authority |
| --- | --- | --- |
| Amine scope | Supplement the DEA, MDEA and AMP paper; exclude piperazine material. | 2026-11-16, [#337 owner decisions](https://github.com/tannerpolley/Amine-Thermodynamics/issues/337#issuecomment-6932434220): “The #348 Part II text loses its piperazine placeholder and mentions in the same manuscript round as #387.” Scope to both supplements is paraphrased from the owner brief. |
| Recalculation check | The recalculation check of the fitted predictions is stated once, in the Part II supplement only. | owner answer on the Part II Writer's question prompt, 2026-11-17, as recorded in the [#348 completion comment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/348#issuecomment-6965576845) and relayed by the repository orchestrator (paraphrase). |
