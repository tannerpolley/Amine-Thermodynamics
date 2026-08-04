# Multisource R4 correlation diagnostic

This analysis tests whether refitting the four coefficients in

\[
\ln K_4(T)=A+B/T+C\ln(T)+DT
\]

can explain the admitted MEA--H2O--CO2 pressure data when the full-polar M5
EOS model and the public homogeneous chemical-equilibrium solver are held
fixed. It is excluded from the manuscript and does not promote parameters.

The analysis-local partition contains 72 pressure-training rows and 49 reserved
rows; it does not modify the canonical 147-training/220-validation project
split.
Training uses the Hilliard 313.15 K campaign and the Jou 313.15--393.15 K
campaigns with equal total weight per source/temperature group. Loading is a
state input, not a regression target. Four training states and one reserved
state fail the installed Provider/Equilibrium acceptance path and remain in
`results/r4_state_failures.csv` rather than receiving replacement values.

One exact-sensitivity, column-scaled Gauss--Newton update reduces the
group-normalized training log10-pressure RMSE from 1.6584 to 1.3953 and the
reserved RMSE from 2.1777 to 1.5336. The fitted coefficients are numerically
unstable: the scaled Jacobian condition number is 3.43e5 and the raw condition
number is 1.26e9. Residuals remain strongly loading-dependent, while R4 and R5
have nearly indistinguishable pressure sensitivities. Selected ionic EOS
coordinates also move pressure by comparable or larger amounts. These results
reject an R4-only explanation; they do not establish a new reaction
correlation.

The retained evidence is deliberately small:

- `figures/r4_diagnostic/output/r4_correlation_fit_rows.csv`: measured and
  modeled pressure rows;
- `results/r4_correlation_fit_parameters.csv`: literature and fitted values;
- `results/r4_correlation_fit_metrics.csv`: grouped residual metrics;
- `figures/r4_diagnostic/output/r4_reaction_sensitivity_rows.csv` and
  `r4_eos_sensitivity_rows.csv`: confounding evidence;
- `results/r4_state_failures.csv`: rejected states;
- `results/r4_correlation_fit_receipt.json`: compact run and identity summary;
- three PNG figures with editable Matplotlib sidecars for pressure parity,
  residual structure, and sensitivity.

The full campaign is not runnable in the repository's locked ePC-SAFT 1.5.2
environment. Set `MEA_R4_PYTHON` to an isolated Python 3.13 interpreter that
contains the exact candidate wheels recorded in the receipt (EOS wheel SHA-256
`1622162b929cb8cd1a10d7c582a6b913babb8580a9f2188ee4fdf324d92f2772`;
Equilibrium wheel SHA-256
`397f0745fc692d33ea3a2d855a33346c516038bfd221798bc05f8ca02fde9b77`).
The runner checks both complete identities before evaluating a state:

```bash
PYTHONPATH=src "$MEA_R4_PYTHON" analyses/phase3/r4_correlation_diagnostic/scripts/run_analysis.py
PYTHONPATH=src uv run --no-sync python analyses/phase3/r4_correlation_diagnostic/scripts/render_figures.py
PYTHONPATH=src uv run --no-sync python analyses/phase3/r4_correlation_diagnostic/scripts/validate_results.py
```

The candidate wheels are external upstream build products and are not vendored
or added to the project lock. If they are unavailable, the full campaign is
intentionally unavailable; rendering and retained-result validation remain
runnable from the normal repository environment. The full numerical campaign
is expensive and is not part of the default test suite.
