# Part I visual pass: fix round 2

The owner's 2026-11-16 removal decision supersedes the proposed trial-phase
classification correction. The paper no longer presents the discarded
unpenalized comparison fit. Retained results, the generated split-energy PDF
and its producer are unchanged. Story corrections T1--T3 are applied; T4 is
dropped with the supplementary comparison account. Science, story and visual
rechecks remain open.

## Removed manuscript content

| File | Removed content |
| --- | --- |
| `main.tex` | Complete abstract sentence beginning “An unpenalized comparison fit instead shows liquid-phase instability”. The Ma'mun cost sentence remains unchanged. |
| `sections/mea_system_modeling_results.tex` | Entire `P:results-phase-split` paragraph: the discarded fit's instability count, distinction from the earlier shared set, strongest split, water fractions, Figure 2 reference and fixed-phase explanation. |
| Same file | Figure `fig:split-energy`, including its image inclusion, caption and label. The generated image file is retained. |
| Same file | Entire `P:results-phase-cause` paragraph: Born/dispersion interpretation, contribution rankings, microscopic-cause statement and fixed-parent caveat. |
| Same file | Entire `P:results-phase-probes` paragraph (four sentences), now referring to the removed fit: the isolated parameter substitutions, held diameters, assessment limits and non-unique sufficient changes. |
| Same file | Dependent clause in `P:results-limits` about the false comparison split and its microscopic cause. The finite-search/global-proof limitation remains. |
| `sections/conclusion.tex` | Sentence about the unpenalized comparison fit's opposing energy terms. |
| `supplement.tex` | Three comparison-classification sentences and the library-recheck provenance sentence from `P:supplement-phase-method`. |
| Same file | Entire `P:supplement-phase-cause` paragraph: fixed-phase energy evaluation, equilibrium caveat, diameter probe, interaction probe and covariance caveat. |
| Same file | Split-energy units sentence from `P:supplement-phase-census`; “and split interpretation” in the S6 heading; unused `sec:s-probes` and `sec:s-fits` aliases. |
| `tables/phase_search_summary.tex` | Entire unused generated display, including all seven data rows (six temperatures and the total), caption and label. |
| `tables/supplement_phase_family.tex` | Entire unused generated display, including all 32 split rows, caption and label. |

Neither deleted table was included by the current manuscript entrypoints, so
neither had a table number in the preceding PDFs. Their retained calculation
inputs remain in `analyses/`. All remaining table files, including Table 7 and
the Table 1 precision note, are byte-identical to `dcdf176`.

## Retained result and literature rationale

The adopted-model statement retains 1908 liquid-grid states, 576 intermediate
liquid states, 162 liquid--vapor states and 6121 transferred trial compositions,
with no detected instability. Böttinger's homogeneous-liquid observation in
its measured subset remains. No new physical result or model calculation is
introduced.

The single added rationale sentence cites `Held2014`, Section 2.4. Zotero
parent `3DIW87Q5`, Markdown `TZJJENHW`, DOI `10.1016/j.cherd.2014.05.017`.
The supporting passages are lines 268 and 403--405 of the hash-verified
`literature/Held2014--TZJJENHW.md` in the main checkout and its current Zotero
companion. Held et al. discuss inconsistent liquid--liquid demixing caused by
ion-parameter choices in aqueous salt solutions. This is a modeling precedent,
not an assertion of measured MEA demixing.

Peiper--Pitzer uses Zotero parent `2WXLNT7C`, PDF `X8GEDSJ2`, citation key
`peiperThermodynamicsAqueousCarbonate1982`, Table 6, DOI
`10.1016/0021-9614(82)90078-7`. One entry was copied verbatim from the existing
canonical Better BibTeX export. Existing bibliography entries are unchanged.
The three italic names now match Table 7 exactly, and the literature-law
sentence uses the requested comma construction.

## Dependencies reported without changing their meaning

- Section 3.4 still describes searches for each fitted set, supplied trial
  compositions, the stability penalty and segment shortening. Those methods
  also explain the retained restriction sequence and earlier shared set.
- The earlier shared set remains defined as stability-penalized; it is the
  distinct calibration retained in Table 7 and the abstract's cost statement.
- S6 still defines the liquid--vapor pressure grid using a fixed reference
  bubble pressure “from the comparison calculation” and says every compared
  parameter set uses the same physical states. This is a remaining provenance
  dependency; no adopted-model bubble pressure was substituted for it.
- The results heading still says “Phase stability of the fitted models”.
- Nomenclature still defines the stability-penalty symbols used by Section
  3.4. No nomenclature row was exclusive to the removed energy figure.
- The retained figure producer still includes the discarded-fit legend for
  its archived split-energy output, as requested. The paper does not include it.

## Figure numbering

| Old main figure | New figure | Content |
| --- | --- | --- |
| 1 | 1 | MEA--water bubble temperature |
| 2 | Removed | Split-energy comparison |
| 3 | 2 | Loaded-MEA pressure |
| 4 | 3 | Speciation |
| 5 | 4 | Integral absorption heat |
| 6 | 5 | Density |
| 7 | 6 | Other MEA concentrations |

Supplement Figure S1 is unchanged. LaTeX owns the numbering and references.

## Verification

Builds use the existing latexmk/pdfLaTeX route through `agent-heavy` in a
background shell. `347-visual-r2-checks.json` records final page counts, PDF
hashes, font checks, build warnings, the unchanged remaining tables and
figures, bibliography equality and the temporary Part II comparison.
The displayed-number check, prose check, freshness results and raw layout
reports accompany this handoff. Final raster comparison and inspection are
recorded in the same checks file.
