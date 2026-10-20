# #197 Stage 3 Writer handoff

Writer implementation is complete in the authorized worktree on `build-197-manuscript-generators`, based on `ed43f9e1fbd63fc22a6b8bccb5635c45d2d385a6`. Independent manuscript reviews and owner review remain open. No external publication or GitHub write occurred.

## File-by-file changes

| File under docs/scientific/latex | Change |
| --- | --- |
| `main.tex` | Title, abstract, current A7 question and compact results; five reviewed figures and main-table inputs integrated through the sections. |
| `sections/introduction.tex` | Density/phase question and contributions; Zhang, Nasrifar, Lloret and Najafloo source-based positioning. |
| `sections/epc_saft_equation_of_state.tex` | A7 temperature-dependent interactions, sizes, density/temperature permittivity law, association inputs and shifted reaction-coordinate conventions. |
| `sections/data_methods.tex` | Eight disjoint groups and observation roles; heat/density/Cp operators, weighted objective, sequential single-start fits, finite search, conditional covariance and numerical verification. |
| `sections/mea_system_modeling_results.tex` | Local A6–A7 phase/density trade-off first; all three density failures; fitted native-unit deviations; five generated figures; comparisons and limitations. |
| `sections/conclusion.tex` | Joint-calibration result and finite-state wording, with density, local-fit, uncertainty, data-access and process-use limits. |
| `sections/nomenclature.tex` | Current observation, dielectric, fitting and phase notation; F1–F6 removed from current-model nomenclature. |
| `sections/data_code_availability.tex` | A7 DOI pending, exact promoted/Engine identities and local staging; earlier F1 deposit distinguished; approved declarations retained. |
| `supplement.tex` | S1–S9 rewritten; separate predecessor studies, complete density/carbonate/phase/covariance inputs; phase tables placed in landscape without edits; source corrections and S8 historical-inventory clarification. |
| `tables/literature_model_comparison.tex` | Authored comparison table: Zhang and Nasrifar added, Lloret heat comparison included, Najafloo ambiguity preserved, current A7 roles specified. No accuracy ranking. |
| `references.bib` | Approved cited-snapshot script refresh from existing export. Added Yang2024, removed Held2008 and archerDielectricConstantWater1990; no existing-entry field drift. |
| `source_log.md` | Promotion statement, retained evidence map, exact software identities, literature passages read, bibliography diff and R2/R5 inheritance history. |
| `submission/chemrxiv.md` | A7 title/abstract and local submission fields; DOI pending and prior F1 release distinguished. |
| `submission/cover_letter.md` | A7 question, results and claim limits for author review. |
| `submission/highlights.txt` | Five A7 highlights, lengths74/61/80/79/75 characters. |
| `submission_metadata.yml` | A7 identities, current PDF hash, pending DOI and review/publication gates; historical F1 deposit nested separately. |
| `submission_readiness.md` | Rewrite-specific mechanical checks and open reviews replace historical ticks; retained-inventory inconsistency explicit. |
| `builds/verification-receipt.json` | Main-PDF input and output hashes written by the build/freshness command. |
| `builds/197-displayed-number-sources.md` | Authored-number source locators, every numerical generated-table row and every figure-input row locator. |
| `builds/197-writer-handoff.md` | This file-by-file and claim-limit handoff. |

## Mandatory limits and additional owner conditions

| Limit | Implementation file:line | How it is met |
| --- | --- | --- |
| Calibration and prior data access | `sections/data_methods.tex:21`; `sections/mea_system_modeling_results.tex:52`; `sections/mea_system_modeling_results.tex:109`; `sections/mea_system_modeling_results.tex:124` | Fitted deviations are calibration; Wagner/transfer retain prior access; Arcis is an acceptance check. |
| Finite phase wording and domain | `sections/mea_system_modeling_results.tex:6`; `sections/mea_system_modeling_results.tex:10`; `supplement.tex:94` | Verbatim finite-search wording; only specified T/P/loading states. No claim above333.15K/alpha.5 or at353.15K density failures; two-phase is not two liquids. |
| Fits and sampled bounds | `sections/data_methods.tex:106`; `sections/data_methods.tex:108` | Two sequential restricted fits, each one start; no global optimum or stable-box certificate. |
| Conditional uncertainty | `sections/data_methods.tex:133`; `sections/data_methods.tex:135`; `sections/data_methods.tex:136` | Ten free/rankten/sixbounds/297dof; fixed weights/inputs/bounds and local linearization; no measurement uncertainty or prediction intervals. |
| Three density failures | `sections/mea_system_modeling_results.tex:21`; `sections/mea_system_modeling_results.tex:27`; `sections/data_methods.tex:68`; `sections/data_methods.tex:69` | Amundsen081:-5.52kg/m3,-2.28s;Hartonoalpha.29:-4.16,-2.05s;alpha.39:-4.41,-2.43s.2s is not95%;source boundary unresolved. |
| Verification versus validation | `sections/data_methods.tex:141`; `sections/data_methods.tex:142`; `sections/data_methods.tex:143` | 375 states with residual≤2.2e-12; separate153-identity replay. Neither validates phase behavior or absorber/stripper performance. |
| Kiepe and Cai | `sections/mea_system_modeling_results.tex:45`; `sections/mea_system_modeling_results.tex:46` | Fixed CO2–water check, cost≈.0007; Cai≈62% cost is an objective statement, not relative accuracy. |
| Other discrepancies | `sections/mea_system_modeling_results.tex:79`; `sections/mea_system_modeling_results.tex:115`; `sections/mea_system_modeling_results.tex:127` | Cp at318.15K,45wt% transfer,Matin pool and all ten carbonate shares visible; no historical-nine removal. |
| Local endpoint trade-off | `sections/mea_system_modeling_results.tex:16`; `sections/mea_system_modeling_results.tex:17` | Only these A6/A7 endpoints; no minimum unavoidable penalty or isolated Born/heat effect. |
| F1 separation and identity | `supplement.tex:43`; `supplement.tex:57`; `supplement.tex:60` | F1–F6 with-heat study and F1–A7 comparison separate. Original wheel preserved. F1 phase values absent. |
| Pending A7 release | `sections/data_code_availability.tex:3`; `supplement.tex:189`; `submission_metadata.yml:68` | A7 DOI pending. Old DOI is F1 only; staging and omitted dependencies identified. |
| S8 retained inventory | `supplement.tex:158`; `supplement.tex:165`; `supplement.tex:166`; `supplement.tex:167` | Generated inventory/generator unchanged; superseded extraction/pressure notes explicitly corrected. Other pressures remain row-specific; no pressure-density magnitude bound. |
| Yang citation boundary | `sections/epc_saft_equation_of_state.tex:74`; `sections/epc_saft_equation_of_state.tex:86` | Yang2024§2.1Eqs1a/2a/2b supports functional form only; own A7 parameter values and branch come from retained inputs. |

## Displayed-number sources

The full number→retained-file:line list is `builds/197-displayed-number-sources.md`. Its first table covers authored numerical statements and rounding, followed by all numerical rows in the fourteen reviewed generated tables and all input row locators for the five figures. Their original provenance comments/JSON retain raw-input hashes. No generated display, generator or retained numerical evidence was edited. No Engine calculation was run.

## Literature read and gaps

The full passages-read record is `source_log.md`, Literature read and source checks. Required primary passages:

- Zhang2011: Zotero PDFM3QDCZM7, §§2.1–2.4,3.1–3.3,Tables6/9/10,Fig6,pp68–74. Table9 contains fitted data; Table10 contains parameters, so the authored outside-fit cell cites Fig6 reaction-law comparisons.
- Nasrifar2010: local MarkdownFVFWT3P9/currentPDF3G4FGGY4,§§3–4,6–7,Tables2–3.
- Najafloo2018: localMarkdown7GCRH2RE,§§2,3.1–3.3,4,Tables1–5. Broader data-use wording in its conclusion remains ambiguous relative to its parameter-estimation methods.
- Lloret2017: ZoteroPDFM9UK6V4P,§§4.4–4.7,5,Table5,Eq26,Figs9–11,pp527–531.
- Yang2024: ZoteroPDFPELWE2BT,§2.1,Eqs1a/2a/2b,PDFp4; own A7 coefficient values are not attributed to Yang.
- Other passages read: Böttinger§3/§§5–6/Table3; Jakobsen calibration experiments/TablesA1–A2; Baygi§3/Eq6/Tables2–3; AkulaEq34/§4.2; Uyan/Wangler/Cleeton parameter-estimation/results; FigielModelParameters/Eqs5–12 and2026correctedEq7; Perdomo§§2.2–2.3/4.3.3; Chremos§3.6/Figs11–12; BülowTables1–3; Vinjarapu§§1.1.1/2.2/3.1/Table4; Arcis§2.4/Table5. Exact identities are in source_log.

No unread required Zhang/Nasrifar/Najafloo/Lloret/Yang passage remains. Missing local Zhang/Lloret/Chremos reading copies were resolved through their existing Zotero PDFs, read-only. Unchanged historical inventory rows and unchanged background literature claims retain earlier source support; this Writer handoff does not assert a new reading of every source in that historical inventory. Najafloo data-use ambiguity and Amundsen uncertainty-boundary ambiguity remain explicit scientific limitations, not invented resolutions.

## Bibliography refresh

Approved command: `python scripts/cited_bibliography.py > references.bib`, run from the manuscript directory after main/supplement `.aux` files existed. The existing `~/Zotero/exports/references.bib` was read only. Added: `Yang2024`. Removed after dropped citations: `Held2008`, `archerDielectricConstantWater1990`. Existing-entry field drift: none. Missing keys: none. No central export refresh, Zotero edit or hand edit of references.bib.

## Builds, inspection and freshness

- Main: `UV_NO_SYNC=1 nice -n 10 bash scripts/build_manuscript.sh`, passed;31pages. Normal uv invocation cannot find the pinned wheel at its worktree path, so the authorized UV_NO_SYNC fallback was used.
- Supplement: explicit `TEXINPUTS='./styles//:' nice -n 10 latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=builds supplement.tex`, passed;35pages.
- Final main and supplement logs: zero LaTeX warnings,overfull/underfull boxes,undefined references andundefined citations. BibTeX:zero warnings. Earlier intermediate missing citations were resolved by the approved snapshot refresh.
- Freshness: `UV_NO_SYNC=1 uv run python scripts/check_manuscript_freshness.py`, passed for main. It does not itself certify supplement compilation or A7 source provenance.
- Both PDFs inspected page by page in color; changed pages reinspected after final edits. Five data-figure pages and rotated/text pages also checked in grayscale. No clipped, overflowing or overlapping display found. Figure1/2/4 source/species/loading identity uses color; grayscale retains model/observation marker distinctions, and exact values remain in tables/CSVs.
- Stale-claim search for F6,Born-off,1,749,twelve-run,149 targets,five parameters,no-heat,translation coefficient:only F6 in the explicitly historical S1 study. No F1 phase result retained.
- `main.pdf` SHA-256`3a2ca047db38c6e2105e57307eb2ce9b8e330e05946de1b12d1c5b8acd369796`; scanner candidates`{('warning', 'tight_text_clearance'): 148, ('warning', 'text_graphic_overlap'): 2, ('error', 'text_overlap'): 1}`.
- `supplement.pdf` SHA-256`8557adbb184a6e3ce299d38b36c3edf27862f9bf565279b52b6a0b2629bb152f`; scanner candidates`{('warning', 'tight_text_clearance'): 24, ('warning', 'text_near_page_edge'): 643}`.

The main scanner calls equation12 superscripts an overlap and flags fraction rules on pages3–4; visual inspection rejects those candidates. Conservative clearance warnings and supplement edge warnings from rotated pages remain in the raw scanner reports. Those automated reports are not described as passing. Logs/renders: `tmp/joint-design/writer-pdf-qa/`, `tmp/joint-design/writer-main-build-final.log`, `tmp/joint-design/writer-supplement-build-final.log`, `tmp/joint-design/writer-freshness-final.log`.

## Open items

The retained-inventory inconsistency remains: generated S8 inventory still has old Hilliard extraction and F1-only Amundsen pressure notes. Approved preceding corrections supply four fitted Hilliard rows,103Amundsen rows at100000Pa,other pressures row-specific,and matched68 F1/A7 pressures101325/100000Pa without a derivative/magnitude bound. Reviewers can decide whether a later inventory-generator correction is warranted.

Independent number/claim and reader-story reviews, their accepted fixes, owner review,A7 DOI publication,and any Overleaf/preprint/journal action remain outside this Writer completion. No review or publication readiness is inferred from historical ticks.
