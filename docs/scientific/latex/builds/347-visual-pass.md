# Part I visual pass, 16 November 2026

The Part I tables and all eight figures were checked for print legibility,
chemical notation, numerical alignment, units, series meaning and caption
agreement. Presentation changes use existing retained values only. No model,
fit, new source adoption or Part II edit was performed. The independent visual,
science-name and reader-story checks remain with the parent and owner.

## New PDF pages

Main remains 24 pages. Supplement remains 9 pages. Page numbers below refer to
these new PDFs. Raster comparison detects changes on main pages 6--24 and
supplement pages 5, 7 and 8; the remaining pages are pixel-identical at 100 dpi.

| Main page | Change |
|---|---|
| 6 | Table 1: single math equilibrium glyph; stoichiometry and coefficients in two stacked panels; decimal-aligned coefficient columns without digit grouping; readable caption. All 20 values preserve exact pre-pass decimal values. |
| 7 | Table 2: replaces the development name in its caption; text flows from the taller Table 1. |
| 8 | Parameter-estimation paragraph defines the seven descriptive calibration names and their cumulative restrictions; “starts” becomes initial parameter vectors. Equation 27 moves lower on the page. |
| 9 | Earlier shared set / present model names in phase-method paragraph; Table 3 and surrounding text move with pagination. Table 3 values and formatting unchanged. |
| 10 | Figure 1: STIX serif text and math, larger labels, pressure-series dash distinction; surrounding text uses reader names. |
| 11 | Figure 2: serif text; legend reads “Present model, frozen compositions”; caption and phase discussion use descriptive names. Table 4 moves to page 12. |
| 12 | Figure 3: serif text, mathematical chemical subscripts, common temperature colors and distinct model dashes. Table 4: “Observations” header; AARD rounded directly from retained rows to three significant figures (31.2, 9.25, 21.0, 14.4, 33.5, 25.8). |
| 13 | Figure 4: serif text and chemical math; common temperature colors and temperature dashes above bubble pressure, dotted below-bubble portions preserved. Caption explains the same phase distinction. Table 5 moves here unchanged. |
| 14 | Table 6: reader-facing “Present” / “Present role” headers and descriptive row names; numeric cells unchanged. The table now fits on one page. |
| 15 | Figure 5: serif text and chemical math; distinct temperature colors and pressure dashes. Caption uses present model. |
| 16 | Figure 6: serif text and chemical math, common temperature colors and distinct dashes. |
| 17 | Figure 7: serif text; common temperature colors and symbol sizes identify temperature in grayscale; open circles remain observations and crosses source-state calculations. Table 7 uses descriptive calibration rows and a wrapping first column; comparison prose uses the same names. |
| 18 | Tables 8 and 9 retain all values and formatting; neighboring uncertainty and comparison text shifts. |
| 19 | Table 10: descriptive model rows and caption, numeric cells unchanged; surrounding comparison and limitations use reader names. |
| 20 | Table 11 and conclusion text shift; values and formatting unchanged. |
| 21 | Table 11 continuation and end matter shift; content unchanged. |
| 22 | Nomenclature shifts; content unchanged. |
| 23 | References shift; content unchanged. |
| 24 | References shift; content unchanged. |

| Supplement page | Change |
|---|---|
| 5 | Table S5 caption replaces the internal parameter name; values unchanged. Table S4 unchanged. |
| 7 | Figure S1 uses STIX serif text and chemical math, larger labels; same 47 discrete predictions and correlated intervals. Table S8 unchanged. |
| 8 | “Starts” becomes initial compositions; phase explanation and shared-input paragraph use present model. |

## Numerical and source checks

`347-visual-values.json` records all 20 Decimal comparisons for Table 1, the
six unrounded AARD reductions and new Table 4 displays, unchanged numeric cells
in other renamed tables, all 54 prior retained-input hash checks, final PDF
hashes, page counts and the protected-path comparison.

The table producer's existing nine-significant-figure reaction-coefficient
rule is unchanged. Added trailing zeros are exact display equalities; no claim
of additional measured precision is made. Table 4's three-significant-figure
rule is the only new rounding. All 152 numeric cells in the five other renamed
tables keep their exact spelling. The existing displayed-number command is
`python docs/scientific/latex/scripts/final_rerun_tables.py --check`: 19 tables,
20 promoted input identities checked. All 54 inputs in the preceding
`347-fix-checks.json` also remain byte-identical.

Figure regeneration uses `scripts/f2_figures.py`, which reads the retained CSV
and JSON values, verifies them against the investigator-promoted commit, and
makes no Engine import or model call. It ran through
`uv run --no-project --with matplotlib python .../f2_figures.py` because this
worktree lacks the pinned Engine wheel required to initialize its project
virtual environment. This isolated presentation environment changes no project
dependency declaration. Plot values and selection are unchanged.

The name-to-restriction mapping and exact record locators are in
`source_log.md`. No calibration code remains in extracted Part I or supplement
text. R1--R5, cited experimental table labels A1--A2, Kim's experimental run 2,
and exact software identifiers in the availability/provenance paragraphs remain
because they identify scientific reactions, source locations or reproduction
inputs. No internal issue number or script filename appears in scientific text.

## Build and visual checks

The existing journal pdfLaTeX/latexmk route is preserved. Builds run in a
background shell using `AGENT_HEAVY_CORES=8 AGENT_HEAVY_MIN_GB=12 agent-heavy`,
with main and supplement rebuilt until cross-references settle. No class,
shared chemical macro or bibliography changes were needed.

Before: 24 + 9 pages, with no material log or font warnings reported by the
preceding `347-fix-checks.json`. After: 24 + 9 pages, no overfull boxes,
unresolved references/citations, missing glyphs or font warnings. `pdffonts`
reports embedded Type 1 and TrueType vector fonts only, zero Type 3 fonts.
The main freshness command passes. Its command-line selector does not accept the Part I supplement; the same recorder-based input and build validation functions are used directly for that document, with the result recorded in `347-visual-values.json`. A forced supplement rebuild avoids a timestamp-only stale-input report after byte-identical figure regeneration.

The deterministic CSE prose check passes for the modified scientific sources,
tables and source log. All color pages were inspected at 100 dpi (full page,
without thumbnail reduction); changed figure pages were also checked in
grayscale. Final heat, density, species and concentration figures were
reinspected after their style corrections.

Raw automated layout results are in `347-visual-qa/`: main has 152 findings (raw fail), supplement 34 (raw review). The existing conservative
Equation 27 superscript bounding-box overlap on main page 8 is retained as a raw
error, not relabeled as a machine pass. The calc/obs superscripts and baseline
are visually separate and readable. Other text-to-vector warnings concern
fractions, sums and superscripts in equations on pages 3, 5, 8 and 9; manual
disposition is exact/keep. Tight text-clearance warnings do not represent
visible collisions. Supplement warnings concern small text clearances only.
The automated report is evidence alongside the manual inspection, not proof of
scientific validation.

Checked and left unchanged: main Tables 3, 5, 8, 9 and 11; supplement Tables
S1--S4 and S6--S8; all scientific quantities, source roles, curve domains,
source-state predictions and uncertainty definitions. No figure producer
required a calculation rerun. No TikZ/PGFPlots diagram is included in Part I.

## Part II, read only

Protected directories, entrypoints, chemistry macros and bibliography files
have an empty diff from `7f6e29e`; Part II PDFs were not rebuilt. Source matches
reported only: `tables/part2/fit-starts.tex` and `shared-sensitivity.tex` retain
A3 in captions/rows, and `sections/part2/model.tex` plus
`pz-reaction-directions.tex` use mhchem equilibrium arrows. The current compiled
Part II PDFs contain no F0--F5 or A3 matches in extracted text; the A3 matches
are in source tables outside that rendered selection. No claim of a Part II
visual defect is made without a separate page inspection.
