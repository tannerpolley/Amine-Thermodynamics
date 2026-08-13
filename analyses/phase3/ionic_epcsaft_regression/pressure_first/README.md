# Pressure-first reactive-VLE diagnostic

This Issue #13 slice freezes the 121 source-resolved candidate CO2-pressure
rows before any pressure fit. The current reaction-correlation and retained
parameter domains admit 44 rows at 313.15 K; 77 rows remain non-scoring domain
challenges.

The diagnostic lane uses a preregistered log10-pressure scale because the
numeric source uncertainties are not transcribed. It is not an uncertainty
model and cannot promote parameters. The promotion lane still requires the
coupled nonideal reactive-bubble owner, complete row evaluation, identifiable
parameters, and all numerical and physical gates.

The fallback calculation is a fixed-pressure ideal-vapor closure screen: it
compares liquid CO2 fugacity with the observed partial pressure. Experimental
total pressure is supplied to the model, so the liquid fugacity is not a
predicted partial pressure and no predictive pressure curve is claimed.

The retained nonlinear regression attempt is a negative runtime result. A
one-parameter, two-row exact-Jacobian fit was terminated after 3,810 seconds
inside a native owner callback, without a `FitResult` or fitted parameter. The
single retained closure point therefore reports the unfitted preregistered
origin and a local linear sensitivity only.

Commands:

```bash
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/build_packet.py
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/evaluate_closure_points.py
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/summarize_results.py
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/render_figures.py
```
