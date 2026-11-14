# Issue 347 — Part I major revision delivery

The manuscript now presents the adopted F2 MEA calibration as one snapshot, with fixed-parameter comparisons against data seen during development. It answers what agreement survives literature reaction laws and reduced adjustable freedom, establishes phase behavior before loaded-property interpretation, and reports the remaining errors directly. This is the implementor delivery for the independent science and story reviews; it is not final scientific acceptance or submission.

The owner promoted notebook commit `d73b90cc6ae00962dc34f77252bbcf54eeff430e` on 2026-11-14 for the Part I major revision in Fluid Phase Equilibria, reporting F2 calibration and fixed-parameter comparisons subject to prior data use, conditional uncertainty, finite searches, worsened comparisons, source-correlation ranges and nonunique split attribution. No fit or model calculation was rerun here. All generated values and figures use retained files at that commit. The adopted parameter document has SHA-256 `ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed`; the Engine wheel is the retained `391dfe5d` build with SHA-256 `0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b`.

## Required items

All items are implemented, with the item-20 absence recorded below. Their acceptance remains subject to the named reviews.

| #347 item | Disposition and location |
|---|---|
| 1 | F2 species, interactions, fixed reaction laws, source-specific errors and conditional errors replace the earlier fit. Main Tables 1, 4–5, 7–8 and supplement tables are generated from promoted results. |
| 2 | Main Table 6 gives F0/F1/F2/F3/F4/F4-0/F5 restrictions, parameter counts, bound counts, costs and fitted/not fitted deviations. The text interprets cumulative restrictions rather than isolated physical effects. |
| 3 | Main Tables 9–10 replace the blanket no-common-data statement with identical-row comparisons, explicit roles and qualifications for uncertain published row membership. Both specified worsened comparisons are visible. |
| 4 | Main Eq. 30 defines the penalty and its weight and scales. Section 3.4 gives pressure rules, missing-search treatment and retreat; F2 required neither penalty stage nor retreat. |
| 5 | Section 4.2 precedes loaded properties. Böttinger's homogeneous-liquid observation is bounded to its measured subset. Figure 2 shows the coupled split energy balance and the text rejects unique microscopic attribution. |
| 6 | Section 3 and supplement S2 disclose weight/scale origins and unrecorded rationales. Main Table 3 and supplement Table S4 provide reproduction values. |
| 7 | Dedicated subsection 2.1, “ePC-SAFT contributions,” contains numbered hard-chain, dispersion, association, Debye–Hückel, corrected Born and permittivity equations. Permittivity is a closure, not an extra additive energy. |
| 8 | Main sequence is Introduction → Thermodynamic model → Data and parameter estimation → Results and discussion → Conclusions. Results follow the requested subsystem, phase, property, concentration, parameter, literature and scope order. |
| 9 | The abstract opens with the question and reduced-fit answer; the introduction ends with the answer and scope. |
| 10 | Main Table 11 gives the exact shared coefficients, with R1–R3 linked to Table 1; model and supplement specify topology, fixed fields and standard states. The conclusion names weak bicarbonate–water, dielectric and reaction-law transfer assumptions. |
| 11 | The three roles fitted / not fitted / comparison only are defined once in Section 3.1. Earlier data use is separate from role. No present Part I comparison qualifies as comparison only because all were seen during development. |
| 12 | Development chronology and internal labels are replaced by their scientific meanings. F0–F5 are explicit table identifiers. Reproduction-table quantities use scientific names and species symbols. |
| 13 | Conditions and figure labels use kelvin. Original article titles in references are preserved. |
| 14 | Split interpretation is coupled and nonunique. Carbonate and high-temperature caloric discussions give supported dependencies and state that the comparisons do not isolate a unique cause. General caveats are gathered in Section 4.7. |
| 15 | The abstract stands alone, is below 250 words, and gives six selected numerical results with a bounded conclusion. |
| 16 | Five highlights are each below 85 characters; five keywords remain. |
| 17 | Nomenclature precedes references and includes symbols, units, sub/superscripts, acronyms and first-use equations or text locations. |
| 18 | The exact requested generative-AI declaration heading appears, with author direction and responsibility described accurately. |
| 19 | Availability text is complete except deposit DOI and access route assigned to #206. |
| 20 | `builds/fpe-submission/` was already absent at branch creation and remains absent. No stale folder needed deletion; #206 owns the rebuilt outward package. |
| 21 | Replotted Figure 4 removes the empty legend entry and colliding inline label, and supplies kelvin, species charges and liquid-mole-fraction units. |
| 22 | Figure 2 supplies phase-split evidence; Figure 7 compares measured and calculated pressures at 15 and 45 wt% using retained same-state calculations, without inventing continuous curves. |
| 23 | Body error values carried by tables are removed; the standalone abstract retains selected results. Sparse interaction matrices become compact lists, and unused table columns are removed. Conditions needed to interpret figures remain in captions. |

## Checks and reproduction

All builds and figure generation ran through `agent-heavy` and completed before delivery. The main PDF is `builds/main.pdf` (24 pages), and the supplement is `builds/supplement.pdf` (8 pages). PDF hashes and log checks are in `347-build-checks.json`. Both PDFs are retained with this delivery.

The numerical check in `347-number-sources.json` maps claim groups to SHA-256 identities for 48 retained inputs. Generated table headers also list their verified input hashes. The table generator's `--check` compares all 19 generated tables with exact regenerated output. It verifies each consumed input against Git bytes at the promoted commit before reduction. The figure generator performs the same verification and evaluates no model. Its retained input manifest is `347-figure-hashes.json`.

The emphasized checks include F0/F2 Ma'mun AARD 19.43/33.47 percent; 2026/F2 heat RMSE 29.49/31.77 kJ/mol CO2 on 20 common 393.15-K intervals; 49 dispersion-dominant and 2 Born-dominant energy changes; the 54 comparison descents; 6121 final supplied trial compositions; the molality completion applied once; and 47 pressure intervals in the conditional-uncertainty figure. Source conditions, fitted-state counts, objective scales and shared values remain attached to their retained owners. The generator does not substitute aggregate comparisons with different data roles for a model ranking.

The normal presentation commands, from the repository root, are:

```sh
agent-heavy uv run --no-sync python docs/scientific/latex/scripts/final_rerun_tables.py
agent-heavy uv run --no-sync python docs/scientific/latex/scripts/final_rerun_tables.py --check
agent-heavy uv run --no-project --with matplotlib==3.10.9 python docs/scientific/latex/scripts/f2_figures.py
```

Compile the supplement, main, supplement and main in that order with `latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=builds` from `docs/scientific/latex/`, inside one `agent-heavy` shell. The cross-document order resolves references without calling submission packaging code.

The final logs contain no undefined reference/citation, overfull box, missing glyph or font warning; neither PDF uses Type 3 fonts. The raw conservative layout reports are retained at `347-qa-delivery/{main,supplement}/report.json`. The main report retains its automated fail status for a superscript bounding-box overlap at Eq. 27 on page 8. Full-page inspection shows separate, legible mathematical glyphs: disposition **exact/keep**. Equation bounding boxes and small text clearances produce the other warnings. This manual disposition does not turn the raw automated status into a pass. All color pages were inspected at full-page scale during the revision, affected final pages were reinspected, and the grayscale figures were inspected.

The deterministic prose check passes (`347-prose-check.txt`). The writer's final `cse:prose` cohesion inspection is **Clear**, with complete coverage of 83 paragraph identifiers and the assembled-source identity in `347-prose.md`. Corrections include the superseded penalty-based argument, alternate role labels, an overbroad homogeneity claim, unsupported comparison of single-parameter probes with conditional errors, code-style quantity labels, repeated table errors, and weak transitions. The prose inspection is not either independent delivered review.

Executable changes are confined to `docs/scientific/latex/scripts/` and remain below the 200 gross-added-line budget; exact composition is recorded in `347-change-accounting.json`. No numerical owner file, source-data file, Engine specification, bibliography or protected `analyses/_cse-manuscript.json` was changed. The shared-value table was generated from #341, without the rejected sodium-salt bicarbonate substitution.

## Source reading and open gates

Read: #347 in full, #337 rules and owner comments, #259, scientific README/CONTEXT, CSE writing/prose/LaTeX references and BANNED, and the applicable manuscript model rule. Three approved xhigh prewriting structure reviews were considered. Primary-source reading included the closest MEA papers and the relevant explicit-ion, Born and phase-method sources; the prewriting reports provide detailed locators and reading-copy checks.

The original November 13 referee reports were not found in the suggested directory or exposed issue attachments. The directory contained the October 8 presentation study. The rewrite therefore follows the complete #347 requirements and #337 accepted decisions; the original-report retrieval gap remains disclosed for later review.

Still open: independent xhigh science review, independent xhigh story review, the high-effort fix round if those reviews identify defects, and owner review of the built PDF. Deposit DOI and access route belong to #206. No Overleaf, Zenodo, submission, merge or other outward action was taken. The draft PR references #347 without closing it.
