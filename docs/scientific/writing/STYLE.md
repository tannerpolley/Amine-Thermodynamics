# Standing editorial decisions

Project-wide choices apply to both parts, both supplements and their figures.
This combined round supersedes the earlier Table 1 nine-significant-figure main-text instruction: the extra digits now appear in the supplement. The earlier restriction on Part II and bibliography edits applied only to the completed Part I visual pass.

Issue discussions record the owner directions; dates below are message dates, not adoption dates inferred from a draft.

| Scope | Standing owner decision | Authority |
| --- | --- | --- |
| All four documents | Present one snapshot of the best results and text; omit superseded results and mixed parameter generations. | 2026-10-01, local `docs/.codex-journal/user_preferences.md`: “The manuscript is one snapshot of the best results and text”. |
| All four documents | Omit discarded parameter sets. The approved restriction-sequence comparison remains within scope. | 2026-11-16, [#347 owner decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/347#issuecomment-6931657641): “why would we want to write about 54 failing states for a parameter set that has been discarded?” The same message explicitly keeps Table 7. |
| Prose, captions, legends, axes and tables | Replace development labels, including F-codes and A-codes, with the quantities or model choices they describe. | 2026-11-16, [#387](https://github.com/tannerpolley/Amine-Thermodynamics/issues/387): “I see stuff like F2 in figure 2 label and I have no idea what F2 is supposed to mean ... is this not development jargon?” |
| Software descriptions | Do not call the software “engine”. Name the package and version in reader-facing availability statements; keep hashes in repository records. | 2026-10-27, [#387](https://github.com/tannerpolley/Amine-Thermodynamics/issues/387): “our own word”. Package/version and repository-only hash directions: paraphrase of the 2026-11-16 owner brief for this combined round. |
| All calculations reported in the papers | Use one identified package build for all calculations; keep its immutable identity in repository records. | 2026-10-23, [#387](https://github.com/tannerpolley/Amine-Thermodynamics/issues/387): paraphrase, “Everything in the paper is calculated from one identified wheel” is the issue's summary, not a recovered verbatim owner quotation. |
| Both main texts | Each part stands alone. Supply needed content rather than replacing it with a bare pointer to the supplement or companion paper. | 2026-11-13, [#387](https://github.com/tannerpolley/Amine-Thermodynamics/issues/387): paraphrase of the recorded owner decision; the issue names bare “see Supplement §…” / “see Part 1” pointers. |
| Main-text tables | Use at most four decimal places; report fitted diameters in Table 3 to five significant figures. Retain further precision in the supplement. | 2026-10-27 and 2026-10-28, [#387](https://github.com/tannerpolley/Amine-Thermodynamics/issues/387): paraphrase of the recorded precision decision. |
| All figures | Each figure must show a useful, distinct comparison. | 2026-11-06, [#387](https://github.com/tannerpolley/Amine-Thermodynamics/issues/387), Figure 7: “worthless ... they all look the same”; 2026-10-28 Figure 9 direction is paraphrased there as unclear. |
| Data used in the series | Use only open, published data. | 2026-11-16, [#345 owner decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/345#issuecomment-6932433233): “the series is to use only open, published data.” Quotation is from the issue's record of the owner decision. |

| Correctable limitations | Fix limitations that can be corrected before refitting rather than presenting them as permanent limits. | 2026-10-13, local `docs/.codex-journal/user_preferences.md`: “The paper states no limitation that can be fixed; fix it before the refit instead of documenting it.” |
| Scientific figures | Prefer claim-led figures; observations are points and model lines require retained continuous calculations. Tables carry exact values. | Undated standing preferences, local `docs/.codex-journal/user_preferences.md`: “Prefer claim-led figures as the primary display of scientific results”; “Plot observations as points and model results as continuous lines only when retained calculations support that continuity.” |

## Part I

Sources: `docs/scientific/latex/main.tex`; `docs/scientific/latex/sections/*.tex`; `docs/scientific/latex/figures/`.

| Scope | Standing owner decision | Authority |
| --- | --- | --- |
| Series role | Part I establishes the MEA calibration before transfer to other amines in Part II. | 2026-11-12 and 2026-11-13, [#387](https://github.com/tannerpolley/Amine-Thermodynamics/issues/387): paraphrase of its series-role summary (“MEA benchmark paper”); the current Part I title uses calibration. |

## Part I supplement

Sources: `docs/scientific/latex/supplement.tex`; `docs/scientific/latex/tables/supplement_*.tex`; other tables included by that source.

| Scope | Standing owner decision | Authority |
| --- | --- | --- |
| Parameter tables | Retain the additional numerical precision omitted from the main text. | 2026-10-27 and 2026-10-28, [#387](https://github.com/tannerpolley/Amine-Thermodynamics/issues/387): paraphrase of “with more precision in the supplement”. |

## Part II

Sources: `docs/scientific/latex/part2.tex`; `docs/scientific/latex/sections/part2/`; `docs/scientific/latex/tables/part2/`; `docs/scientific/latex/figures/part2/`.

| Scope | Standing owner decision | Authority |
| --- | --- | --- |
| Series role and literature | Transfer Part I's workflow with the same overall structure and an amine-focused literature review. | 2026-11-12 and 2026-11-13, [#387](https://github.com/tannerpolley/Amine-Thermodynamics/issues/387): paraphrase of the recorded owner decision. |
| Amine scope and order | Cover DEA (secondary), MDEA (tertiary) and AMP (hindered primary), after Part I's MEA; remove piperazine from the paper and retain its analyses. | 2026-11-16, [#337 owner decisions](https://github.com/tannerpolley/Amine-Thermodynamics/issues/337#issuecomment-6932434220): “Piperazine is dropped from Part II.” Classes are recorded in the same-day #345 decision. |

## Part II supplement

Sources: `docs/scientific/latex/part2_supplement.tex`; `docs/scientific/latex/sections/part2/supplement.tex`; included `docs/scientific/latex/tables/part2/` tables.

| Scope | Standing owner decision | Authority |
| --- | --- | --- |
| Amine scope | Supplement the DEA, MDEA and AMP paper; exclude piperazine material. | 2026-11-16, [#337 owner decisions](https://github.com/tannerpolley/Amine-Thermodynamics/issues/337#issuecomment-6932434220): “The #348 Part II text loses its piperazine placeholder and mentions in the same manuscript round as #387.” Scope to both supplements is paraphrased from the owner brief. |
