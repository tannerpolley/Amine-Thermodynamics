# Pending 80 °C wording: test outside the fit (A) or extrapolation outside the fit (B)

Not `\input` anywhere. The 80 °C experiment of issue #140 decides which variant
applies. Paste one variant per span, then delete this file.

Neither variant uses "prediction". In FPE ePC-SAFT papers, prediction means no
parameter adjusted to the target mixture (Uyan 2015, Wangler 2018); both records
here are fitted to ternary data, so the manuscript defines its terms in
`P:introduction-05`.

- **A (test outside the fit).** 80 °C is outside the present five-coordinate
  fit, but its data informed earlier model development: the inherited R2/R5
  shifts and the 173.44 K CO2 dispersion energy. Numbers are the retained
  corrected-loading values (issue #140 body): 21 canonical rows 20.27 %, 11 Jou
  1995 targets 9.24 %, 19 rows without the two shift-anchor targets 21.83 %.
- **B (extrapolation outside the fit).** A frozen restored-source record whose
  loaded-solution parameters were fitted only to loaded-solution data at or
  below 60 °C, conditional on the binary CO2–water (Kiepe, 313–393 K) and
  MEA–water (Cai, 363–432 K) interactions and on fixed historical SSM+DS,
  dielectric and association choices; extrapolated once to the 21 canonical
  80 °C rows and to 11 never-accessed Wagner 2013 rows near 353 K. Every result
  is a `[[...]]` placeholder.

The title, PDF title, submission-metadata title, cover-letter title and the
Results heading ("Temperature and concentration outside the present fit") are
set by the owner and are the same under A and B. Spans are located by
paragraph identifier; "A: unchanged" means the current text already is A.

## Open points before pasting B

1. `references.bib` has no Kiepe or Wagner 2013 entry. Add them through
   `cse:zotero`, then replace `[[CITE_KIEPE]]` and `[[CITE_WAGNER2013]]`
   (Wagner 2013 DOI 10.1021/je301030z, from `data/reference/MEA/manifests/source_status_manifest.csv` on branch `work/mea-30wt-data-inventory`).
2. `[[CO2_EPS_K]]`: the issue #140 readiness review records the published
   169.21 K value replacing 173.44 K; confirm against the frozen record.
3. B assumes the selected record (13.53/8.28 % fit, Born-form comparison,
   sensitivity section, transfer and 100–120 °C numbers) stays the paper's
   main record and the restored-source record is reported only for 80 °C. If
   the restored-source record replaces it, every fitted number in the
   abstract, Results, tables and figures changes, which this file does not
   cover.
4. `\cref{fig:pressure}` shows the selected record. A B figure for the
   restored-source record needs a regenerated figure (outside this file).
5. `submission_metadata.yml:2` (`scientific_lane: scoped_predictive_nine_species_epcsaft`)
   is an identifier, not prose. Rename it under either variant only if nothing
   reads it.

## Abstract word budget

Counting rule: whitespace-separated words of the rendered abstract; a number
and its unit count as two words (`9.24 %`, `80 °C`), `et al.` as two,
hyphenated and en-dash compounds (`five-coordinate`, `20–60`) as one, a
parenthesized abbreviation as one. Each `[[...]]` placeholder counts as one
word. Limit 250. The rendered abstract is 246 words, of which the
tests-outside-the-fit sentence is 47, so a replacement may use at most 51.
A: 47 (unchanged). B: 50 (total 249); the Wagner 2013 value stays in the body.

## 1. Abstract, `main.tex`, `P:abstract-01`, seventh sentence

Current:

```latex
Outside the present fit, the pressure AARD is 9.24\,\% for 11 Jou 1995 targets at \SI{80}{\degreeCelsius}, whose data informed fixed inputs, 26.44\,\% for 57 rows at 100--\SI{120}{\degreeCelsius}, and 75.95 and 46.15\,\% for 33 and 37 rows at 15 and 45 wt\% \MEA.
```

A: unchanged (the sentence already discloses that the 80 °C data informed
fixed inputs; under A, the 19-row value enters the Results and Conclusions).

B (51-word limit; 50 words):

```latex
At \SI{80}{\degreeCelsius}, a record fitted only to loaded-solution data at $\le$\SI{60}{\degreeCelsius} extrapolates with a pressure AARD of [[AARD_21]]\,\% on 21 rows; the selected record gives 26.44\,\% for 57 rows at 100--\SI{120}{\degreeCelsius} and 75.95 and 46.15\,\% for 33 and 37 rows at 15 and 45 wt\% \MEA.
```

## 2. Introduction terms, `sections/introduction.tex`, `P:introduction-05`

A: unchanged.

B (new sentence after "…they are extrapolations."):

```latex
A second record, whose loaded-solution parameters were fitted only to loaded-solution data at or below \SI{60}{\degreeCelsius}, is extrapolated to \SI{80}{\degreeCelsius}; it is conditional on binary \COtwo--water and \MEA--water interactions fitted at 313--\SI{393}{\kelvin}~\cite{[[CITE_KIEPE]]} and 363--\SI{432}{\kelvin}~\cite{caiBinaryIsobaricVaporLiquid1996}, and on fixed historical SSM+DS, dielectric and association choices.
```

## 3. Data roles, `sections/data_methods.tex`, `P:methods-03`

Current (last two sentences):

```latex
Two kinds of inherited values described below were estimated partly on 80\,\si{\degreeCelsius} data.
The 80\,\si{\degreeCelsius} targets therefore test conditions outside the present fit, not data unseen during model development.
```

A: unchanged.

B (append):

```latex
A second, restored-source record excludes those values and every other 80\,\si{\degreeCelsius} observation from estimation and selection, and was frozen before one 80\,\si{\degreeCelsius} evaluation (\cref{sec:results-80c}).
```

## 4. Restored-source record, new paragraph after `P:methods-05`

A: none.

B (new paragraph):

```latex
% P:methods-05b
The restored-source record returns R2 and R4 to their source correlations, takes R5 from [[R5_SOURCE]], and uses the published \COtwo dispersion energy of \SI{[[CO2_EPS_K]]}{\kelvin}.
Its loaded-solution parameters were fitted only to loaded-solution data at or below \SI{60}{\degreeCelsius}, and its weights and selection were frozen before any \SI{80}{\degreeCelsius} calculation.
The binary \COtwo--water and \MEA--water interactions keep their fits to binary data at 313--\SI{393}{\kelvin}~\cite{[[CITE_KIEPE]]} and 363--\SI{432}{\kelvin}~\cite{caiBinaryIsobaricVaporLiquid1996}.
```

## 5. Results 80 °C opening, `sections/mea_system_modeling_results.tex`, `P:results-09`

A (first sentence replaced; one sentence added after the 21-row sentence; other sentences unchanged):

```latex
The \SI{80}{\degreeCelsius} isotherm is excluded from the current five-coordinate, 142-target fit, but its data informed two fixed inputs (below), so these comparisons test the selected record outside its fit and are not predictions.
```

```latex
Without \texttt{vle\_obs\_0206} and \texttt{vle\_obs\_0211}, which set the inherited reaction shifts, the remaining 19 rows give 21.83\,\%.
```

B (new paragraph inserted before `P:results-09`; the current paragraph follows as the selected-record paragraph):

```latex
% P:results-09a
The restored-source record (\cref{sec:data-methods}) was frozen before any \SI{80}{\degreeCelsius} calculation and evaluated once at \SI{80}{\degreeCelsius}.
On all 21 canonical pressure rows at \SI{80}{\degreeCelsius} it gives a pressure AARD of [[AARD_21]]\,\%, a mean \(\ln(p_{\mathrm{calc}}/p_{\mathrm{obs}})\) of [[MEAN_LN_21]] and a root-mean-square \(\ln(p_{\mathrm{calc}}/p_{\mathrm{obs}})\) of [[RMS_LN_21]], against 20.27\,\% for the selected record.
On the 11 Jou 1995 targets it gives [[AARD_JOU_11]]\,\%, and on the 19 rows without the two former reaction-shift anchors [[AARD_19]]\,\%, against 21.83\,\% for the selected record.
On 11 Wagner 2013 rows near \SI{353}{\kelvin}~\cite{[[CITE_WAGNER2013]]}, not accessed before evaluation, it gives [[AARD_WAGNER_11]]\,\%.
These values are extrapolations outside the fit: no \SI{80}{\degreeCelsius} observation entered the record, but they remain conditional on the binary \COtwo--water and \MEA--water interactions and on the fixed SSM+DS, dielectric and association choices.
```

## 6. Results inherited-input paragraph, `P:results-10`

A: unchanged.

B (first and last sentences replaced; middle sentences unchanged):

```latex
The selected record's \SI{80}{\degreeCelsius} comparisons are tests outside the present (142-target, five-coordinate) fit, not data unseen during model development.
```

```latex
The restored-source record replaces both inputs, so only its \SI{80}{\degreeCelsius} values are extrapolations free of \SI{80}{\degreeCelsius} data.
```

## 7. Conclusion, `sections/conclusion.tex`, `P:conclusion-01`, third and fourth sentences

Current:

```latex
At \SI{80}{\degreeCelsius}, outside the current fit, the model reproduces the 11 Jou 1995 targets with an AARD of 9.24\,\% and all 21 canonical rows with 20.27\,\%.
These are tests outside the present (142-target, five-coordinate) fit, not data unseen during model development: inherited reaction shifts used two of the 11 targets, and the fixed \COtwo dispersion energy was chosen against a set that included \SI{80}{\degreeCelsius} data.
```

A:

```latex
At \SI{80}{\degreeCelsius}, outside the current fit, the model reproduces the 11 Jou 1995 targets with an AARD of 9.24\,\%, all 21 canonical rows with 20.27\,\% and the 19 rows not used for inherited reaction shifts with 21.83\,\%.
These comparisons are tests outside the fit, not predictions: inherited reaction shifts used two of the 11 targets, and the fixed \COtwo dispersion energy was chosen against a set that included \SI{80}{\degreeCelsius} data.
```

B:

```latex
A restored-source record, fitted only to loaded-solution data at or below \SI{60}{\degreeCelsius} and frozen before evaluation, extrapolates the \COtwo pressure to \SI{80}{\degreeCelsius} with an AARD of [[AARD_21]]\,\% on all 21 canonical rows and [[AARD_WAGNER_11]]\,\% on 11 Wagner 2013 rows near \SI{353}{\kelvin} not accessed during model development.
The extrapolation is conditional on binary \COtwo--water and \MEA--water interactions fitted up to 393 and \SI{432}{\kelvin} and on fixed historical SSM+DS, dielectric and association choices; the selected record's 9.24 and 20.27\,\% are tests outside its fit, not data unseen during model development.
```

## 8. Cover letter, `submission/cover_letter.md`, contribution 3

Current:

```text
3. It tests the record outside the fit. At 80 °C, the 11 Jou 1995 pressure targets give an
   average absolute relative deviation of 9.24 %, and all 21 canonical rows give 20.27 %;
   inherited reaction shifts and the fixed CO2 dispersion energy were chosen against sets that
   included 80 °C data, as the manuscript states.
```

A:

```text
3. It tests the record outside the fit. At 80 °C, the 11 Jou 1995 pressure targets give an
   average absolute relative deviation of 9.24 %, all 21 canonical rows 20.27 %, and the 19
   rows not used for the inherited reaction shifts 21.83 %; inherited reaction shifts and the
   fixed CO2 dispersion energy were chosen against sets that included 80 °C data, as the
   manuscript states.
```

B:

```text
3. It extrapolates to 80 °C a record whose loaded-solution parameters were fitted only to
   loaded-solution data at or below 60 °C, conditional on binary CO2–water and MEA–water
   interactions fitted up to 393 K and 432 K and on fixed historical Born, dielectric and
   association choices. Evaluated once after freezing, it gives a pressure average absolute
   relative deviation of [[AARD_21]] % on the 21 canonical rows at 80 °C and
   [[AARD_WAGNER_11]] % on 11 Wagner 2013 rows near 353 K not accessed during model
   development. The selected record's 80 °C values (9.24 % on the 11 Jou 1995 targets, 20.27 %
   on all 21 rows) are tests outside its fit, not data unseen during model development.
```

## 9. Submission metadata claim, `submission_metadata.yml`, `scientific_claim`

A:

```yaml
scientific_claim: >
  Nine-species SSM+DS ePC-SAFT record 9055458d for 30 wt% aqueous MEA, fitted
  to 142 ternary pressure and speciation targets at 20-60 degC; tested
  outside the current fit at 80 degC, the 11 Jou 1995 targets
  (vle_obs_0203-0213) give pressure AARD 9.24 %, all 21 canonical rows
  20.27 % and the 19 rows without the two reaction-shift anchors 21.83 %
  (80 degC data informed earlier model development); Born-form ranking
  depends on the role of Matin 2012 titration bicarbonate. Transfer,
  100-120 degC, bound, carbonate, density/Cp and probe limits are reported;
  no physical validation.
```

B:

```yaml
scientific_claim: >
  Nine-species SSM+DS ePC-SAFT record 9055458d for 30 wt% aqueous MEA, fitted
  to 142 ternary pressure and speciation targets at 20-60 degC. A frozen
  restored-source record [[RECORD_ID]], with loaded-solution parameters fitted
  only to loaded-solution data at or below 60 degC and conditional on
  CO2-water (Kiepe, 313-393 K) and MEA-water (Cai, 363-432 K) binary
  interactions, extrapolates 80 degC pressure with AARD [[AARD_21]] % on 21
  canonical rows and [[AARD_WAGNER_11]] % on 11 never-accessed Wagner 2013
  rows near 353 K; Born-form ranking depends on the role of Matin 2012
  titration bicarbonate. Transfer, 100-120 degC, bound, carbonate,
  density/Cp and probe limits are reported; no physical validation.
```

## 10. Highlight, `submission/highlights.txt:1` (Elsevier limit 85 characters)

Current (77 characters):

```text
9.24 % AARD on 11 Jou 1995 CO2 pressures at 80 °C, outside the 142-target fit
```

A (68 characters):

```text
80 °C test outside the fit: 9.24 % AARD on 11 Jou 1995 CO2 pressures
```

B (71 characters with a five-character value such as `12.34`):

```text
Fitted at ≤60 °C, extrapolated to 80 °C: [[AARD_21]] % pressure AARD, 21 rows
```

## Spans unchanged under both variants

- Residual-table note, `tables/residual_summary.tex`: unchanged while the
  table keeps only the selected record (open point 3).
- Pressure figure caption, `fig:pressure`: unchanged while the figure shows
  the selected record (open point 4); the figure itself is flagged for
  regeneration after the #138 loading correction.
