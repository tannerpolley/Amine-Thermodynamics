# AMP protonation source transcription

Issue #229, 2026-10-29. Source: Hamborg & Versteeg (2009), DOI
[10.1021/je800897v](https://doi.org/10.1021/je800897v), Zotero parent
`D9KXSKLR`, PDF `334KGLPV`, 11 pages. The 24 AMP runs in Appendix B,
Table 16, printed p.1325 (PDF page 8), were extracted with Poppler and checked
visually against that page. `hamborg-table-16.csv` retains all six columns.
No private transcription was used.

Temperature is kelvin; ln K and its printed ± uncertainty are dimensionless.
The final two columns are percent deviations in the source's infinite-dilution
extrapolation, **not** uncertainty in a pressure observation. Run 24 has ±0.03;
the other 23 AMP runs have ±0.04. Results and Discussion, pp.1320–1321,
attributes the experimental uncertainty to ±0.5 mV in the two electrode
potentials. It does not specify these as independent one-standard-deviation
errors. Temperature differences between cells above ±0.1 K were excluded
(Experimental, p.1320).

The source convention is infinite-dilution molality for solutes, pure water
for solvent, with pressure dependence neglected at 1 bar (Theory, p.1319,
Eq.18; molarity-to-molality conversion Eq.24, p.1321). For the AMP reaction:

$$\mathrm{AMPH^+ + H_2O \rightleftharpoons AMP + H_3O^+},\qquad
K=\frac{a_{\rm AMP}a_{\rm H_3O^+}}{a_{\rm AMPH^+}a_{\rm H_2O}}.$$

This specializes the named hydronium dissociation convention in the paper;
water must not be dropped when transferring to another activity convention.
The 24 averaged temperatures span 293.12–353.22 K. This source does not
establish a 393 K law.

## Correlation check and its limit

Eq.21, p.1319, is ln K = A/T + B + C ln(T), with T in kelvin.
Table 1, p.1320, prints four correlated AMP values:
(293.00, −22.65), (303.00, −21.95), (318.00, −20.96), (333.00, −20.04).
The first is explicitly marked extrapolated. It also prints ΔG°=55.24 kJ/mol
and ΔH°=52.2 kJ/mol at 298.15 K; Table 11, p.1322, gives pKa=9.68.
**Table 1 does not print A, B and C.**

For a reproducible transcription check only, `check-hamborg.py` reconstructs
Eq.21 by unweighted linear least squares on those four rounded correlated
values. This is an algebraic reconstruction of printed correlation values,
not a fit to the experimental runs, a new reaction-law adoption or an Engine
calculation. It gives A=−3221.33909063 K, B=−68.91165437,
C=10.07991283. The four reconstructed-minus-printed residuals are
−0.000341, +0.000792, −0.000676, +0.000225 in ln K.

`hamborg-correlation-residuals.csv` reports every Table 16 observed-minus-
reconstructed residual, and 100[exp(residual)−1] for the corresponding K
ratio. Mean residual: −0.00327943; RMS: 0.03362197; maximum absolute:
0.06106819 in ln K. These are consistency diagnostics, **not physical
validation**. Some exceed the printed ±0.04; the diagnostic also contains
rounding and reconstruction error, increasingly outside Table 1's 293–333 K
span. It cannot be used to reject a row or declare exact reproduction of the
authors' unrounded correlation. Coefficient recovery from rounded values is
ill-conditioned; the numerical digits identify this calculation only.

The original unrounded A/B/C or an explicitly authorized correlation fit and
its uncertainty are still needed before adopting an executable law. Mapping
to the Engine standard state also remains open. The CSV is a source-preparation
record, not an admitted fitting packet.
