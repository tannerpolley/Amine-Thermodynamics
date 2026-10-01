# Pending 80 °C wording: assessment (A) or prediction (B)

Not `\input` anywhere. The leak-free 80 °C experiment of issue #140 decides
which variant applies. Paste one variant per span, then delete this file.

- **A (assessment).** 80 °C is outside the present five-coordinate fit, but its
  data informed earlier model development: the inherited R2/R5 shifts and the
  173.44 K CO2 dispersion energy. Numbers are the retained corrected-loading
  values (issue #140 body): 21 canonical rows 20.27 %, 11 Jou 1995 targets
  9.24 %, 19 rows without the two shift-anchor targets 21.83 %.
- **B (prediction).** A frozen restored-source record whose loaded-solution
  parameters were fitted only to loaded-solution data at or below 60 °C,
  conditional on the binary CO2–water (Kiepe, 313–393 K) and MEA–water
  (Cai, 363–432 K) interactions and on fixed historical SSM+DS, dielectric and
  association choices; scored once on the 21 canonical 80 °C rows and on 11
  never-accessed Wagner 2013 rows near 353 K. Every result is a `[[...]]`
  placeholder.

Line numbers refer to commit `bbb20ab` plus the abstract edit in the working
tree. Spans where A needs no change are marked "A: unchanged".

## Open points before pasting B

1. `references.bib` has no Kiepe or Wagner 2013 entry. Add them through
   `cse:zotero`, then replace `[[CITE_KIEPE]]` and `[[CITE_WAGNER2013]]`.
2. `[[CO2_EPS_K]]`: the issue #140 readiness review records the published
   169.21 K value replacing 173.44 K; confirm against the frozen record.
3. B assumes the selected record (13.53/8.28 % fit, Born-form comparison,
   transfer and 100–120 °C numbers) stays the paper's main record and the
   restored-source record is reported as the 80 °C prediction. If the
   restored-source record replaces it, every fitted number in the abstract,
   Results, tables and figures changes, which this file does not cover.
4. `\cref{fig:pressure}` shows the selected record. A B figure for the
   restored-source record needs a regenerated figure (outside this file).
5. `submission_metadata.yml:2` (`scientific_lane: scoped_predictive_nine_species_epcsaft`)
   is an identifier, not prose. Change it under A only if nothing reads it.

## Abstract word budget

Counting rule: whitespace-separated words of the rendered abstract; a number
and its unit count as two words (`9.24 %`, `80 °C`), `et al.` as two,
hyphenated and en-dash compounds (`five-coordinate`, `20–60`) as one, a
parenthesized abbreviation as one. Each `[[...]]` placeholder counts as one
word (it becomes one number).

The abstract outside the 80 °C sentences is 198 words, so the 80 °C sentences
may use at most 52. Current: 48 (total 246). A: 52 (total 250). B: 51 (total 249).

## 1. Title, `main.tex:56`

Current:

```latex
\title[mode = title]{\texorpdfstring{A nine-species ePC-SAFT model for \ce{CO2} solubility in 30 wt\% aqueous monoethanolamine: Born-form comparison and prediction at \SI{80}{\degreeCelsius}}{A nine-species ePC-SAFT model for CO2 solubility in 30 wt\% aqueous monoethanolamine: Born-form comparison and prediction at 80 °C}}
```

A:

```latex
\title[mode = title]{\texorpdfstring{A nine-species ePC-SAFT model for \ce{CO2} solubility in 30 wt\% aqueous monoethanolamine: Born-form comparison and assessment at \SI{80}{\degreeCelsius}}{A nine-species ePC-SAFT model for CO2 solubility in 30 wt\% aqueous monoethanolamine: Born-form comparison and assessment at 80 °C}}
```

B: unchanged.

## 2. PDF metadata title, `main.tex:95`

Current:

```latex
    pdftitle={A nine-species ePC-SAFT model for CO2 solubility in 30 wt\% aqueous monoethanolamine: Born-form comparison and prediction at 80 °C},
```

A:

```latex
    pdftitle={A nine-species ePC-SAFT model for CO2 solubility in 30 wt\% aqueous monoethanolamine: Born-form comparison and assessment at 80 °C},
```

B: unchanged.

## 3. Submission metadata title, `submission_metadata.yml:40-41`

Current:

```yaml
title: >
  A nine-species ePC-SAFT model for CO2 solubility in 30 wt% aqueous
  monoethanolamine: Born-form comparison and prediction at 80 degC
```

A:

```yaml
title: >
  A nine-species ePC-SAFT model for CO2 solubility in 30 wt% aqueous
  monoethanolamine: Born-form comparison and assessment at 80 degC
```

B: unchanged.

## 4. Submission metadata claim, `submission_metadata.yml:3-10`

Current:

```yaml
scientific_claim: >
  Nine-species SSM+DS ePC-SAFT record 9055458d for 30 wt% aqueous MEA, fitted
  to 142 ternary pressure and speciation targets at 20-60 degC; outside the
  current fit, the 11 Jou 1995 targets at 80 degC (vle_obs_0203-0213) give
  pressure AARD 9.24 % and all 21 canonical rows 20.27 % (tests outside the
  present fit, not data unseen during model development); Born-form ranking depends on the role of Matin 2012 titration
  bicarbonate. Transfer, 100-120 degC, bound, carbonate, density/Cp and probe
  limits are reported; no physical validation.
```

A:

```yaml
scientific_claim: >
  Nine-species SSM+DS ePC-SAFT record 9055458d for 30 wt% aqueous MEA, fitted
  to 142 ternary pressure and speciation targets at 20-60 degC; assessed
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
  interactions, predicts 80 degC pressure with AARD [[AARD_21]] % on 21
  canonical rows and [[AARD_WAGNER_11]] % on 11 never-accessed Wagner 2013
  rows near 353 K; Born-form ranking depends on the role of Matin 2012
  titration bicarbonate. Transfer, 100-120 degC, bound, carbonate,
  density/Cp and probe limits are reported; no physical validation.
```

## 5. Cover-letter title, `submission/cover_letter.md:5-6`

Current:

```text
Please consider the manuscript "A nine-species ePC-SAFT model for CO2 solubility in 30 wt%
aqueous monoethanolamine: Born-form comparison and prediction at 80 °C" for publication in
```

A:

```text
Please consider the manuscript "A nine-species ePC-SAFT model for CO2 solubility in 30 wt%
aqueous monoethanolamine: Born-form comparison and assessment at 80 °C" for publication in
```

B: unchanged.

## 6. Cover-letter 80 °C sentences, `submission/cover_letter.md:15-21`

Current (from `"Predictive"` to `as the manuscript states.`):

```text
"Predictive" in the manuscript
has a limited meaning: calculation outside the current fit. At 80 °C, the model reproduces
the 11 Jou 1995 pressure targets with an average absolute relative deviation of 9.24 %, and
all 21 canonical pressure rows at that temperature with 20.27 %. These are tests outside the
present (142-target, five-coordinate) fit, not data unseen during model development: inherited
reaction shifts and the fixed CO2 dispersion energy were chosen against sets that included
80 °C data, as the manuscript states.
```

A:

```text
At 80 °C, outside
the current fit, the model reproduces the 11 Jou 1995 pressure targets with an average absolute
relative deviation of 9.24 %, all 21 canonical pressure rows at that temperature with 20.27 %,
and the 19 rows not used for the inherited reaction shifts with 21.83 %. These comparisons are
an assessment, not a prediction: inherited reaction shifts and the fixed CO2 dispersion energy
were chosen against sets that included 80 °C data, as the manuscript states.
```

B:

```text
"Prediction" in the
manuscript has a limited meaning: calculation at 80 °C from a record whose loaded-solution
parameters were fitted only to loaded-solution data at or below 60 °C, conditional on binary
CO2–water and MEA–water interactions fitted to data up to 393 K and 432 K and on fixed
historical choices of the Born, dielectric and association terms. Scored once after freezing,
that record gives a pressure average absolute relative deviation of [[AARD_21]] % on the 21
canonical rows at 80 °C and [[AARD_WAGNER_11]] % on 11 Wagner 2013 rows near 353 K that were
not accessed during model development. The selected record's 80 °C values (9.24 % on the 11
Jou 1995 targets, 20.27 % on all 21 rows) are tests outside its fit, not data unseen during
model development, as the manuscript states.
```

## 7. Abstract 80 °C sentences, `main.tex:77-79`

Current (48 words):

```latex
Prediction here means calculation outside the current fit.
For the 11 Jou 1995 targets at \SI{80}{\degreeCelsius}, the pressure AARD is 9.24\,\%; all 21 canonical rows at \SI{80}{\degreeCelsius} give 20.27\,\%.
These are tests outside the present (142-target, five-coordinate) fit, not data unseen during model development.
```

A (52 words; replaces all three lines):

```latex
At \SI{80}{\degreeCelsius}, outside the present five-coordinate fit, the pressure AARD is 9.24\,\% for the 11 Jou 1995 targets and 20.27\,\% for all 21 canonical rows.
These data informed earlier model development, so the comparison is an assessment; the 19 rows not used for inherited reaction shifts give 21.83\,\%.
```

B (51 words; replaces all three lines):

```latex
Prediction here means calculation from loaded-solution parameters fitted only to $\le$\SI{60}{\degreeCelsius} data, with binary \COtwo--water and \MEA--water interactions fitted up to \SI{432}{\kelvin}.
Scored once, the pressure AARD is [[AARD_21]]\,\% on 21 canonical rows at \SI{80}{\degreeCelsius} and [[AARD_WAGNER_11]]\,\% on 11 held-out Wagner 2013 rows near \SI{353}{\kelvin}.
```

## 8. Introduction scope sentence, `sections/introduction.tex:30`

Current:

```latex
This work presents a nine-species ePC-SAFT model of \COtwo solubility and speciation in 30 wt\% \MEA, fitted to pressure at 40 and \SI{60}{\degreeCelsius} and speciation at 20--\SI{60}{\degreeCelsius}, and tested at \SI{80}{\degreeCelsius} outside the present fit.
```

A:

```latex
This work presents a nine-species ePC-SAFT model of \COtwo solubility and speciation in 30 wt\% \MEA, fitted to pressure at 40 and \SI{60}{\degreeCelsius} and speciation at 20--\SI{60}{\degreeCelsius}, and assessed at \SI{80}{\degreeCelsius} outside the present fit.
```

B:

```latex
This work presents a nine-species ePC-SAFT model of \COtwo solubility and speciation in 30 wt\% \MEA, fitted to pressure at 40 and \SI{60}{\degreeCelsius} and speciation at 20--\SI{60}{\degreeCelsius}, and uses a record frozen on loaded-solution data at or below \SI{60}{\degreeCelsius} to predict the \SI{80}{\degreeCelsius} pressure.
```

## 9. Introduction definition, `sections/introduction.tex:32`

Current:

```latex
Prediction here means calculation outside the current fit; it does not mean prediction of the ternary system from pure-component and binary information alone, as in the MDEA studies above.
```

A:

```latex
Assessment here means comparison with measurements outside the current fit that informed earlier model development; it is not prediction of the ternary system from pure-component and binary information alone, as in the MDEA studies above.
```

B:

```latex
Prediction here means calculation at \SI{80}{\degreeCelsius} from loaded-solution parameters estimated only from loaded-solution data at or below \SI{60}{\degreeCelsius}.
It is conditional on binary \COtwo--water and \MEA--water interactions fitted at 313--\SI{393}{\kelvin}~\cite{[[CITE_KIEPE]]} and 363--\SI{432}{\kelvin}~\cite{caiBinaryIsobaricVaporLiquid1996}, and on fixed historical SSM+DS, dielectric and association choices; it is not prediction of the ternary system from pure-component and binary information alone, as in the MDEA studies above.
```

## 10. Data roles, `sections/data_methods.tex:25-26`

Current:

```latex
Two kinds of inherited values described below were estimated partly on 80\,\si{\degreeCelsius} data.
The 80\,\si{\degreeCelsius} targets therefore test conditions outside the present fit, not data unseen during model development.
```

A: unchanged.

B (append after line 26):

```latex
A second, restored-source record excludes those values and every other 80\,\si{\degreeCelsius} observation from estimation and selection, and was frozen before one 80\,\si{\degreeCelsius} evaluation (\cref{sec:results-80c}).
```

## 11. Restored-source record, new paragraph after `sections/data_methods.tex:65`

A: none.

B (new paragraph):

```latex
% P:methods-05b
The restored-source record returns R2 and R4 to their source correlations, takes R5 from [[R5_SOURCE]], and uses the published \COtwo dispersion energy of \SI{[[CO2_EPS_K]]}{\kelvin}.
Its loaded-solution parameters were fitted only to loaded-solution data at or below \SI{60}{\degreeCelsius}, and its weights and selection were frozen before any \SI{80}{\degreeCelsius} calculation.
The binary \COtwo--water and \MEA--water interactions keep their fits to binary data at 313--\SI{393}{\kelvin}~\cite{[[CITE_KIEPE]]} and 363--\SI{432}{\kelvin}~\cite{caiBinaryIsobaricVaporLiquid1996}.
```

## 12. Results 80 °C heading, `sections/mea_system_modeling_results.tex:74`

Current:

```latex
\subsection{Prediction at 80 \texorpdfstring{\si{\degreeCelsius}}{°C}, outside the current fit}\label{sec:results-80c}
```

A:

```latex
\subsection{Assessment at 80 \texorpdfstring{\si{\degreeCelsius}}{°C}, outside the current fit}\label{sec:results-80c}
```

B:

```latex
\subsection{Prediction at 80 \texorpdfstring{\si{\degreeCelsius}}{°C} from a record fitted up to 60 \texorpdfstring{\si{\degreeCelsius}}{°C}}\label{sec:results-80c}
```

## 13. Results 80 °C opening paragraph, `sections/mea_system_modeling_results.tex:76-80`

Current:

```latex
The \SI{80}{\degreeCelsius} isotherm is excluded from the current five-coordinate, 142-target fit.
For the 11 Jou 1995 targets at \SI{80}{\degreeCelsius} (packet targets \texttt{vle\_obs\_0203}--\texttt{vle\_obs\_0213})~\cite{Jou1995}, the selected record gives a pressure AARD of 9.24\,\%, a mean \(\ln(p_{\mathrm{calc}}/p_{\mathrm{obs}})\) of \(-0.017\) and a root-mean-square \(\ln(p_{\mathrm{calc}}/p_{\mathrm{obs}})\) of 0.117 (\cref{fig:pressure}).
The canonical calculation gives the same 9.24\,\% on these 11 targets.
All 21 canonical pressure rows at \SI{80}{\degreeCelsius}, which add 10 measurements of Aronu et al.~\cite{Aronu2011}, give 20.27\,\% with a mean \(\ln(p_{\mathrm{calc}}/p_{\mathrm{obs}})\) of \(-0.199\), so the added rows are under-predicted.
For the 11 packet species targets at \SI{80}{\degreeCelsius}, the AARD is 11.15\,\% for SSM+DS and 7.36\,\% for Original Born (\cref{fig:speciation}).
```

A (line 76 replaced; one sentence added after line 79; other lines unchanged):

```latex
The \SI{80}{\degreeCelsius} isotherm is excluded from the current five-coordinate, 142-target fit, but its data informed two fixed inputs (below), so these comparisons assess the selected record rather than predict.
For the 11 Jou 1995 targets at \SI{80}{\degreeCelsius} (packet targets \texttt{vle\_obs\_0203}--\texttt{vle\_obs\_0213})~\cite{Jou1995}, the selected record gives a pressure AARD of 9.24\,\%, a mean \(\ln(p_{\mathrm{calc}}/p_{\mathrm{obs}})\) of \(-0.017\) and a root-mean-square \(\ln(p_{\mathrm{calc}}/p_{\mathrm{obs}})\) of 0.117 (\cref{fig:pressure}).
The canonical calculation gives the same 9.24\,\% on these 11 targets.
All 21 canonical pressure rows at \SI{80}{\degreeCelsius}, which add 10 measurements of Aronu et al.~\cite{Aronu2011}, give 20.27\,\% with a mean \(\ln(p_{\mathrm{calc}}/p_{\mathrm{obs}})\) of \(-0.199\), so the added rows are under-predicted.
Without \texttt{vle\_obs\_0206} and \texttt{vle\_obs\_0211}, which set the inherited reaction shifts, the remaining 19 rows give 21.83\,\%.
For the 11 packet species targets at \SI{80}{\degreeCelsius}, the AARD is 11.15\,\% for SSM+DS and 7.36\,\% for Original Born (\cref{fig:speciation}).
```

B (new opening paragraph inserted before line 76; current lines 76-80 follow as the selected-record paragraph):

```latex
% P:results-09a
The restored-source record (\cref{sec:data-methods}) was frozen before any \SI{80}{\degreeCelsius} calculation and scored once.
On all 21 canonical pressure rows at \SI{80}{\degreeCelsius} it gives a pressure AARD of [[AARD_21]]\,\%, a mean \(\ln(p_{\mathrm{calc}}/p_{\mathrm{obs}})\) of [[MEAN_LN_21]] and a root-mean-square \(\ln(p_{\mathrm{calc}}/p_{\mathrm{obs}})\) of [[RMS_LN_21]], against 20.27\,\% for the selected record.
On the 11 Jou 1995 targets it gives [[AARD_JOU_11]]\,\%, and on the 19 rows without the two former reaction-shift anchors [[AARD_19]]\,\%, against 21.83\,\% for the selected record.
On 11 Wagner 2013 rows near \SI{353}{\kelvin}~\cite{[[CITE_WAGNER2013]]}, not accessed before scoring, it gives [[AARD_WAGNER_11]]\,\%.
These values are predictions in the sense of \cref{sec:introduction}: they are conditional on the binary \COtwo--water and \MEA--water interactions and on the fixed SSM+DS, dielectric and association choices.
```

## 14. Pressure figure caption, `sections/mea_system_modeling_results.tex:86`

Current: "the \SI{80}{\degreeCelsius} panel is a test outside the present (142-target, five-coordinate) fit, not data unseen during model development, and its 11 Jou 1995 targets ..."

A: unchanged (already assessment framing).

B: unchanged while the figure shows the selected record (open point 4).

## 15. Results inherited-input paragraph, `sections/mea_system_modeling_results.tex:94-98`

Current:

```latex
The \SI{80}{\degreeCelsius} comparisons are tests outside the present (142-target, five-coordinate) fit, not data unseen during model development.
Two fixed inputs used \SI{80}{\degreeCelsius} data (\cref{sec:data-methods}).
The inherited R2 and R5 reaction shifts were estimated in September 2026 on a set that included \texttt{vle\_obs\_0206} and \texttt{vle\_obs\_0211}, two of the 11 Jou 1995 targets.
The fixed \COtwo dispersion energy of \SI{173.440}{\kelvin} was chosen on 2 September 2026 against a set that included 21 pressure rows and 11 species targets at \SI{80}{\degreeCelsius}.
Prediction here therefore means calculation outside the current fit, as defined in \cref{sec:introduction}.
```

A (lines 94 and 98 replaced; 95-97 unchanged):

```latex
The \SI{80}{\degreeCelsius} comparisons are tests outside the present (142-target, five-coordinate) fit, not data unseen during model development.
Two fixed inputs used \SI{80}{\degreeCelsius} data (\cref{sec:data-methods}).
The inherited R2 and R5 reaction shifts were estimated in September 2026 on a set that included \texttt{vle\_obs\_0206} and \texttt{vle\_obs\_0211}, two of the 11 Jou 1995 targets.
The fixed \COtwo dispersion energy of \SI{173.440}{\kelvin} was chosen on 2 September 2026 against a set that included 21 pressure rows and 11 species targets at \SI{80}{\degreeCelsius}.
The \SI{80}{\degreeCelsius} results are therefore an assessment, as defined in \cref{sec:introduction}, not a prediction.
```

B (line 94 and line 98 replaced; 95-97 unchanged):

```latex
The selected record's \SI{80}{\degreeCelsius} comparisons are tests outside the present (142-target, five-coordinate) fit, not data unseen during model development.
Two fixed inputs used \SI{80}{\degreeCelsius} data (\cref{sec:data-methods}).
The inherited R2 and R5 reaction shifts were estimated in September 2026 on a set that included \texttt{vle\_obs\_0206} and \texttt{vle\_obs\_0211}, two of the 11 Jou 1995 targets.
The fixed \COtwo dispersion energy of \SI{173.440}{\kelvin} was chosen on 2 September 2026 against a set that included 21 pressure rows and 11 species targets at \SI{80}{\degreeCelsius}.
The restored-source record replaces both inputs, so only its \SI{80}{\degreeCelsius} values are predictions in the sense of \cref{sec:introduction}.
```

## 16. Residual-table note, `tables/residual_summary.tex:6`

Current: "Rows marked outside fit are tests outside the present (142-target, five-coordinate) fit, not data unseen during model development; ..."

A: unchanged.

B: unchanged if the table keeps only the selected record; adding restored-source rows needs a regenerated table (open point 3).

## 17. Conclusion 80 °C sentences, `sections/conclusion.tex:5-6`

Current:

```latex
At \SI{80}{\degreeCelsius}, outside the current fit, the model reproduces the 11 Jou 1995 targets with an AARD of 9.24\,\% and all 21 canonical rows with 20.27\,\%.
These are tests outside the present (142-target, five-coordinate) fit, not data unseen during model development: inherited reaction shifts used two of the 11 targets, and the fixed \COtwo dispersion energy was chosen against a set that included \SI{80}{\degreeCelsius} data.
```

A:

```latex
At \SI{80}{\degreeCelsius}, outside the current fit, the model reproduces the 11 Jou 1995 targets with an AARD of 9.24\,\%, all 21 canonical rows with 20.27\,\% and the 19 rows not used for inherited reaction shifts with 21.83\,\%.
These comparisons are an assessment, not a prediction: inherited reaction shifts used two of the 11 targets, and the fixed \COtwo dispersion energy was chosen against a set that included \SI{80}{\degreeCelsius} data.
```

B:

```latex
A restored-source record, fitted only to loaded-solution data at or below \SI{60}{\degreeCelsius} and frozen before evaluation, predicts the \COtwo pressure at \SI{80}{\degreeCelsius} with an AARD of [[AARD_21]]\,\% on all 21 canonical rows and [[AARD_WAGNER_11]]\,\% on 11 Wagner 2013 rows near \SI{353}{\kelvin} not accessed during model development.
The prediction is conditional on binary \COtwo--water and \MEA--water interactions fitted up to 393 and \SI{432}{\kelvin} and on fixed historical SSM+DS, dielectric and association choices; the selected record's 9.24 and 20.27\,\% are tests outside its fit, not data unseen during model development.
```

## 18. Highlight, `submission/highlights.txt:1` (Elsevier limit 85 characters)

Current (77 characters):

```text
9.24 % AARD on 11 Jou 1995 CO2 pressures at 80 °C, outside the 142-target fit
```

A (74 characters):

```text
80 °C assessment outside the fit: 9.24 % AARD on 11 Jou 1995 CO2 pressures
```

B (74 characters with a five-character value such as `12.34`):

```text
Record fitted at ≤60 °C predicts 80 °C CO2 pressure: [[AARD_21]] % AARD, 21 rows
```
