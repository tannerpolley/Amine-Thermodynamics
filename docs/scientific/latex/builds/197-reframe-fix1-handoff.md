# Issue 197 reframe fix round 1: writer handoff

Main: 18 pages, SHA-256 `eaa423b44b5eeaeeaec7c6e345f5614bf4436bee057ff2c194d4446f41536789`.
Supplement: 22 pages, SHA-256 `494ee52685120dd4a9603bd7d2c69ef3cbfcab9191a499828920aa7ef4e3be50`.

Both PDFs are in this directory as `main.pdf` and `supplement.pdf` (ignored build products). Reproduction uses the explicit epoch in `197-reframe-fix1-build-checks.json`.

## Finding dispositions

| Finding | Disposition | Locations relative to repository root |
|---|---|---|
| Astra 1 | Applied: both generated density-domain cells corrected to 20–100 wt%. | `docs/scientific/latex/scripts/final_rerun_tables.py:431`; `docs/scientific/latex/tables/current_data_inventory.tex:104`; `docs/scientific/latex/tables/supplement_data_roles.tex:111` |
| Astra 2 | Applied verbatim: calculated pressures are the subject of the 46–70% discrepancy. | `docs/scientific/latex/sections/mea_system_modeling_results.tex:21` |
| Opus M1 | Applied verbatim; duplicate results answer deleted and the six-sentence conclusion appears once. | `docs/scientific/latex/sections/conclusion.tex:3`; `docs/scientific/latex/sections/mea_system_modeling_results.tex:163` |
| Opus M2 | Applied; species caption says long-dashed to distinguish the below-bubble segments from species-specific dashes required by S7. | `docs/scientific/latex/sections/mea_system_modeling_results.tex:45`; `docs/scientific/latex/sections/mea_system_modeling_results.tex:109` |
| Opus M3 | Applied verbatim: six source deviations and all 159 counts; obsolete supplement pointer removed. | `docs/scientific/latex/sections/mea_system_modeling_results.tex:20` |
| Opus M4 | Applied with A2: bound locations and choice, density tradeoff, homogeneous-liquid context, extended search and finite-search limits. | `docs/scientific/latex/sections/mea_system_modeling_results.tex:125`; `docs/scientific/latex/sections/mea_system_modeling_results.tex:149`; `docs/scientific/latex/supplement.tex:311` |
| Opus M5 | Applied: comparison/reported/density-free fit names, one definition, revised captions and data roles; obsolete data-use column removed. | `docs/scientific/latex/supplement.tex:300`; `docs/scientific/latex/scripts/final_rerun_tables.py:293`; `docs/scientific/latex/scripts/final_rerun_tables.py:338` |
| Opus S1 | Applied verbatim: common thermodynamic basis, MEA carbamate chemistry and phase-search motivation. | `docs/scientific/latex/sections/introduction.tex:13`; `docs/scientific/latex/sections/introduction.tex:21`; `docs/scientific/latex/sections/introduction.tex:29` |
| Opus S2 | Applied as A1 directs; Astra 2 replaces the first proposed sentence and source/model states are explicit. | `docs/scientific/latex/sections/mea_system_modeling_results.tex:23` |
| Opus S3 | Applied verbatim: five non-fitted 353.15 K species states and their errors. | `docs/scientific/latex/sections/mea_system_modeling_results.tex:53` |
| Opus S4 | Applied verbatim: Matin species deviations and high-loading free-MEA underprediction. | `docs/scientific/latex/sections/mea_system_modeling_results.tex:59` |
| Opus S5 | Applied verbatim: practical property scope and remaining discrepancies; the required preceding scope sentences remain. | `docs/scientific/latex/sections/mea_system_modeling_results.tex:117`; `docs/scientific/latex/sections/mea_system_modeling_results.tex:118` |
| Opus S6 | Applied with A3: plain-language abstract, 133 searched states through 393.15 K; 227 rendered words. | `docs/scientific/latex/main.tex:97`; `docs/scientific/latex/main.tex:100` |
| Opus S7 | Applied: logarithmic minor-species panels, distinct line patterns, maxima moved into caption and duplicate prose removed. | `analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py:87`; `analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py:91`; `docs/scientific/latex/sections/mea_system_modeling_results.tex:45` |
| Opus S8 | Applied: Xu star and neutral square fit-status keys. Optional lower-axis-limit change not taken. | `analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py:18`; `analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py:80` |
| Opus S9 | Applied with A2 and S14: pressure fractions, six temperatures, excluded crosses and updated caption/pointer. | `analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py:216`; `docs/scientific/latex/sections/mea_system_modeling_results.tex:137` |
| Opus S10 | Applied: all three identified caption bookkeeping sentences removed. | `docs/scientific/latex/sections/mea_system_modeling_results.tex:11`; `docs/scientific/latex/sections/mea_system_modeling_results.tex:36`; `docs/scientific/latex/sections/mea_system_modeling_results.tex:81` |
| Opus S11 | Applied: repeated prose cut, explicit 307-quantity enumeration and generated table wording revised. | `docs/scientific/latex/sections/data_methods.tex:5`; `docs/scientific/latex/sections/mea_system_modeling_results.tex:88`; `docs/scientific/latex/sections/mea_system_modeling_results.tex:61`; `docs/scientific/latex/scripts/final_rerun_tables.py:453` |
| Opus S12 | Applied with existing citations retained: non-fitted/not-blind and candidate-acceptance roles spelled out. | `docs/scientific/latex/sections/data_methods.tex:22`; `docs/scientific/latex/sections/mea_system_modeling_results.tex:76`; `docs/scientific/latex/scripts/final_rerun_tables.py:431` |
| Opus S13 | Applied: two duplicated rows removed and pressure subset renamed Hilliard and Jou pressures. | `docs/scientific/latex/scripts/final_rerun_tables.py:332`; `docs/scientific/latex/tables/supplement_outside_fit.tex:82` |
| Opus S14 | Applied: supplement follows actual first citation, new source-conventions citation, bound-choice and density-free sections last, correlation-table pointer fixed. | `docs/scientific/latex/supplement.tex:41`; `docs/scientific/latex/sections/data_methods.tex:19`; `docs/scientific/latex/supplement.tex:177`; `docs/scientific/latex/supplement.tex:295`; `docs/scientific/latex/supplement.tex:326` |
| Opus O4 | Applied verbatim: Najafloo cell states the methods/conclusion discrepancy. | `docs/scientific/latex/scripts/final_rerun_tables.py:476` |
| Opus O5 | Applied: lower pressure axis states the relative-deviation formula. | `analyses/mea_parameter_bundle/scripts/render_manuscript_figures.py:75` |
| A1 | Applied verbatim: Astra pressure attribution followed by state-specific Aronu/Hilliard/model comparison. | `docs/scientific/latex/sections/mea_system_modeling_results.tex:22`; `docs/scientific/latex/sections/mea_system_modeling_results.tex:23` |
| A2 | Applied: both searches, 81 declared/21 excluded/60 admitted extension states, 133 total, confirmations, frozen pressures and one six-temperature figure. | `docs/scientific/latex/sections/mea_system_modeling_results.tex:131`; `docs/scientific/latex/sections/mea_system_modeling_results.tex:150`; `docs/scientific/latex/supplement.tex:222`; `docs/scientific/latex/tables/phase_extension.tex:82` |
| A3 | Applied: abstract, conclusion and property-scope paragraph consistent with extended phase-search claims and limits. | `docs/scientific/latex/main.tex:100`; `docs/scientific/latex/sections/conclusion.tex:13`; `docs/scientific/latex/sections/mea_system_modeling_results.tex:117` |
| A4 | Applied: all three replacement split inputs, changed success/diagnostic rows and phase labels; different-build caption removed. Old Table S10 is now Tables S21–S22 after reordering. | `docs/scientific/latex/scripts/final_rerun_tables.py:408`; `docs/scientific/latex/tables/supplement_phase_family.tex:107`; `docs/scientific/latex/tables/supplement_phase_family.tex:104` |
| A5 | Applied: identities stated once in Data and Code Availability, pointers in methods and supplement, original conditional-error provenance retained. | `docs/scientific/latex/sections/data_code_availability.tex:6`; `docs/scientific/latex/sections/data_methods.tex:73`; `docs/scientific/latex/supplement.tex:227` |

## Verbatim exceptions and optional work

- S2/M4/S6/S9 use the exact owner adjustments A1–A3; obsolete 73-state-only wording is replaced by the promoted extension. The two required phase-opening sentences and literature phase sentence are preserved.
- M2 says “Long-dashed” for species below-bubble segments because S7 gives species distinct dash patterns; density wording is verbatim.
- S14 uses the actual first-citation order after these edits: model inputs, objective, source conventions, caloric inputs, density scales, conditional errors, source deviations, phase search, diameter probes, density-free fit. Existing section and table numbers are therefore updated; phase search is S8 and old split Table S10 is now Tables S21–S22.
- M5 defines the density-free fit once in S9, its first use within the reordered supplement; S10 refers back without a second definition. Existing literature citations are retained inside replacement sentences.
- Species and phase floats are declared earlier within their same subsections so that the enlarged figures do not leave an avoidable blank page. No plot values or claim order changes.
- The two short Engine commit identifiers in Data and Code Availability are the explicit A5 exception to the original no-identifiers prose rule; the full immutable wheel checksum remains in the evidence record.
- O1–O3 are skipped as instructed. S8’s optional lower-axis-limit suggestion is skipped. No mandatory finding remains unapplied.

## Numbers, evidence and verification

New and changed quantities, populations, rounding and retained paths are in `197-reframe-number-sources.md`, fix-round-1 section. The current numeric audit has 63 checks and 82 hashed inputs, including all 24 generated table files. Previous audits remain evidence for unchanged values. The 39 figure/table/provenance outputs reproduce byte for byte on regeneration (`197-reframe-fix1-generated-check.json`).

Engine 3e83e19ccc771b51d8ebc038931ab25192f4c5b5, wheel SHA-256 0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804, is the merged-main library brought in by d5c9bd1. The fit and conditional statistics retain 8298c602 provenance. No scientific result was recomputed by the writer.

The abstract is 227 rendered words. Both builds have zero overfull boxes and no undefined references/citations or font warnings. Every page was inspected in color and grayscale. Visual QA remains “review”: warnings concern tight table/caption clearance, mathematical fraction bars and the landscape table; manual inspection found no clipping or illegibility. One underfull Uyan bibliography paragraph remains in supplement p. 20 and is readable.

Existing bibliography: 54 entries, 49 cited, no missing keys; file unchanged from 67fd1ea. Original source line endings are preserved. CSE prose check and git diff whitespace check pass.

For new literature wording the writer read Böttinger Table 3, Najafloo Sections 3.1–3.3 and 4, and Neumann Section 4.2, p. 8 (Zotero PDF attachment G3U3WRF8). Neumann describes the homogeneous-liquid density comparisons; the absence of a split counterpart is a limited comparison with those data, not experimental validation of the numerical search. No Zotero edits were made.

## Delivery and remaining gates

This is the implementor’s delivery, with parent independent science and reader-story review still to run. Main d5c9bd1 was merged into the existing feature branch as explicitly instructed; there is no merge into main, push, PR, issue closure, Overleaf synchronization, journal action or DOI action. The CSE Quarto preview service was not touched. No subagents were used. The final response records the fix commit SHA.
