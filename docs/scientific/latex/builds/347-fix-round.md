# PR 358 — required review corrections

This high-effort fix round applies the science review's five required corrections and the story review's R1–R25 to initial head `1cf9bbdb0a696f39ab7b989aa9866f6fb434b25c`. Both full review messages and the R17 follow-up were read through `t3_thread_read`. Science takes precedence; judgment calls and optional notes were skipped. The promoted evidence remains notebook commit `d73b90cc6ae00962dc34f77252bbcf54eeff430e`, for the Part I F2 calibration with fixed-parameter comparisons and the six owner limits. No fitting or model calculation was performed.

## Correction disposition

| Correction | Disposition | Applied content |
|---|---|---|
| Science 1 | Applied verbatim | Hilliard sealed-pan pressure is unreported; atmospheric pressure is assigned for calculations. |
| Science 2 | Applied verbatim | Hartono printed-loading convention and unresolved mole-fraction inconsistency. |
| Science 3 | Applied verbatim | Cited Weiland/Concepción table rows, results conditions sentence, and Concepción bibliography entry. Generator preserves both rows. |
| Science 4 | Applied verbatim | Inventory caption separates roles from inspection and parameter selection; generator updated. |
| Science 5 | Applied verbatim | Kim final-loading ceiling and the two inconsistent observations, followed by precise alternative exclusions. |
| R1 | Applied verbatim | Abstract. A word-hyphenation declaration permits the longer replacement to fit the journal column without changing its wording. |
| R2 | Applied verbatim | Highlights 3–5. |
| R3 | Applied with factual correction | “independent reaction measurements” replaced by “source reaction laws”; all other replacement wording is unchanged. |
| R4 | Applied verbatim | Introduction answer paragraph. |
| R5 | Applied verbatim | Contribution blocks moved; duplicate sentences removed; specified nomenclature pointers updated. Equations unchanged. |
| R6 | Applied verbatim | One fixed-literature-law statement replaces the repetition. |
| R7 | Applied verbatim | Restriction definitions moved to methods and cost comparison interpreted in results. |
| R8 | Applied verbatim | Objective-weight wording in methods and supplement. |
| R9 | Applied verbatim | Trial-composition origin in methods and supplement. |
| R10 | Applied verbatim | Segment shortening and F0/F2 penalty distinction. |
| R11 | Applied verbatim | Reproduction paragraph and table moved before the stability subsection; replacement sentences inserted. |
| R12 | Superseded by science | Science 4 supplies the caption. |
| R13 | Applied verbatim | Supplied-trial statement and no-penalty result. |
| R14 | Applied verbatim | Unpenalized comparison fit distinguished from F0. |
| R15 | Applied verbatim | Frozen-parent qualification. |
| R16 | Applied verbatim | Pressure result before the figure reference. |
| R17 | Applied verbatim | Comparison table moved; model names and Kim sentences replaced; producer caption updated. The follow-up changes only the review's problem statement. |
| R18 | Superseded by science | Science 3 supplies the cited property labels and bibliography. |
| R19 | Applied verbatim | Integral-heat figure caption roles. |
| R20 | Applied verbatim | Concentration-transfer data-use sentence. |
| R21 | Applied verbatim | Within-source correlated errors replace ambiguous campaign dependence in results and supplement. |
| R22 | Applied verbatim | Identical-observation published-model comparison. |
| R23 | Applied verbatim | Scope and limitations, including the numerical owner limits. |
| R24 | Applied verbatim | Separate nomenclature paragraphs. |
| R25 | Applied verbatim | Shared-table sentence. |

## Verification of the story's factual additions

The new `347-fix-checks.json` retains SHA-256 identities for 54 unique input/source files verified against Git bytes at the promoted commit. The initial 48-input hash check and exact regeneration of all 19 tables were rerun. The additional factual checks are:

- **R1/R4/R7:** `reduced-refit/fit-comparison.csv` gives 16 and 11 fitted parameters, and six and one parameters on bounds for F0 and F2. `parameter-details.csv`, `reduced-refit/README.md` and the reaction source contract establish the two shifted reaction laws and separate Born diameters in F0, and the cumulative F1–F5 definitions. `agreement.csv` confirms the pressure and loaded-density comparisons in Table 6; the not-fitted pressure statement refers to that table's six-source subset, not every other concentration.
- **R22:** `same-data-comparison/published-deviations.json` gives 19 observations and 21.03% Baygi, 39.96% Najafloo, versus 33.47% F2. All three comparison roles are not fitted; no ranking across data roles was introduced.
- **R10/R14:** the #255 README identifies the 16-parameter optimization and penalty stages; `adoption-297/README.md` binds its selected result to F0's `f8f64820...` identity. `split-cause-342/README.md` instead binds the unpenalized comparison to `efb2a9ab...`, distinct from F0 and F2. Reading the historical fitting origin does not substitute its old-wheel numerical results for the promoted same-wheel comparisons.
- **R21:** the retained covariance declaration explicitly assumes independent errors, and the reported covariance uses the diagonal weighted-residual construction. Correlated errors within an experimental source are excluded. The replacement names this exclusion without claiming that such correlations were measured.
- **R23:** matched-score files and `part1-scores.json` confirm the same-19 Ma'mun errors 19.43%/33.47% and the common-20-interval 393.15-K Kim errors 29.49/31.77 kJ/mol CO2. The bibliography identifies the authors as Kim and Svendsen.
- **R3 inference:** F0's lower cost establishes the possible gain from extra freedom, and the shared-parameter export includes R2. The phrase “independent reaction measurements” goes beyond the adopted-source authority: `reaction-source-ranges.csv` and the reaction source contract identify correlations, with unverified underlying measurement coverage. The smallest correction is “source reaction laws.” This is the only factual deviation from the story replacements.
- **R23 inference:** the retained split-energy and single-parameter-probe results show opposing energy terms and more than one sufficient isolated change in finite searches. They do not identify one restricted parameter as the cause of F2's stability. The prescribed inference is retained with the surrounding finite-search and nonunique-cause qualifications.

The Concepción entry's title, authors, year, journal, volume, pages and DOI match `/home/tnnrpolley21/Zotero/exports/references.bib` (brace protection normalized). Only the explicitly requested entry was added; the rest of the committed bibliography is unchanged. Zotero capability was checked through `cse-zotero doctor` before this bounded incorporation.

## Build and checks

Both PDFs and the affected bibliography were rebuilt with `latexmk` through `agent-heavy`, with supplement/main cross-references resolved. Main: 24 pages; supplement: 9 pages. The supplement grows because the required source qualifications and explicit Kim selection now occupy more space. The PDFs and hashes are retained with the fix checks.

The final logs contain no undefined references/citations, overfull boxes, missing glyphs or font warnings. Neither PDF has Type 3 fonts. The deterministic prose check passes. The abstract is 223 words; highlights are 76, 61, 80, 73 and 75 characters. Executable changes from `d73b90c` are 146 gross added lines, entirely within manuscript scripts, below the 200-line budget. The protected manuscript registry is unchanged.

The initial `347-prose.md`, `347-build-checks.json` and `347-revision.md` remain records of the initial delivery, not a current cohesion verdict or current PDF identity. This fix-round record and `347-fix-checks.json` describe the changed text. A focused science re-check and owner PDF review remain open. No optional review suggestion, fit change, outward publication or merge was performed.

The final raw layout reports are retained in `347-fix-qa/`. The main checker still flags the calc/obs superscript bounding boxes in Eq. 27 on page 8; the equation was inspected at full-page size and remains legible (exact/keep). The raw status remains fail, rather than being relabeled pass. The supplement report requests review of small clearances. The changed abstract, comparison-table pages and source-qualification page were inspected, along with the page overview. The longer abstract initially produced an overfull line; a hyphenation declaration fixes it without changing the prescribed words.
