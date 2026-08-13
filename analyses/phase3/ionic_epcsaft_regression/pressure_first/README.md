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

The first screening calculation is a fixed-pressure liquid-fugacity residual:
experimental total pressure is supplied to that model, so it is not a pressure
prediction. A one-parameter, two-row exact-Jacobian screen completed from three
starts at `k_ij(CO2,water) = 0.0074095449`; all starts reached the same
parameter-space basin. This value remains diagnostic because the provisional
row scale is not source uncertainty and the screen does not predict pressure.

The pressure diagnostic declares exactly one reacting liquid and one incipient
neutral vapor. The homogeneous owner certifies the nine-species liquid; the
bubble owner solves only vapor composition and pressure, without phase-count
search or liquid-root rediscovery. The retained Hilliard 17 wt% MEA, 40 °C
subset contains six independently closed predicted `P_CO2` points with exact
parameter derivatives and complete local certification. The curve is still
non-promotable because it uses the fixed-pressure screening parameter and only
one source/temperature/concentration campaign.

The historical 1,022-second coupled timeout and 3,810-second interrupted fit
remain negative evidence for the superseded general-coexistence route; they are
not the current execution path.

Commands:

```bash
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/build_packet.py
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/evaluate_closure_points.py
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/run_fixed_pressure_fit.py
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/run_reactive_bubble_diagnostic.py
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/summarize_results.py
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/render_figures.py
```
