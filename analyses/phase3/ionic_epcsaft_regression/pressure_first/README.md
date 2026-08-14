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

The next bounded ladder screened the smallest supported directions on those
six exact pressure roots. No M0 block passed the combined rank, bounds,
loading-trend, provenance, and model-selection gates. Source-fixed Gross
(2005) quadrupolar M1 was worse than M0 at the exact origin and its local
candidate did not outperform the simpler M0 candidate. Linearized candidates
are sensitivity diagnostics and are not plotted as pressure predictions.

The independent neutral-binary audit extracts all 29 Cai (1996) MEA-water VLE
rows and evaluates the measured states with exactly one declared liquid and
one declared vapor; it performs no reaction solve or phase discovery. The
common current-model source domain admits only three internal rows, all at
66.66 kPa. A one-coordinate exact-Jacobian, three-start fit converges to
`k_ij(MEA,water) = -0.0578253027` with rank 1, condition number 1, and no active
bound, but it is not qualified: its source-limit-normalized RMSE is 7.74, its
composition residual trend is material, and no independent Cai pressure level
is inside the Held-water 0–100 °C qualification range.

Two source-consistent Baygi (2015) models then admit both complete Cai pressure
levels. The 3B-MEA/4C-water fit converges from three starts to
`k_ij = -0.0100202942` (training normalized RMSE 14.57; held-out 15.30); the
3B-MEA/2B-water fit converges to `k_ij = -0.0055392860` (training 12.49;
held-out 16.59). Both are rank 1, condition number 1, interior, and
multistart-consistent, but both fail the preregistered source-scale residual and
composition-trend gates. Neither value is frozen into the reactive model.

Baygi fitted its reported interactions with the paper's Eq. 12 Bubble-T and
Dew-T composition objectives, not fixed-state fugacity-closure residuals. The
smallest unresolved generic capability is therefore a declared-one-liquid,
one-vapor Bubble-T/Dew-T observation family with exact total parameter
derivatives and Regression ownership. Until that source objective can be
reproduced, the neutral interaction remains unqualified and the reactive
reserved rows remain untouched.

The historical 1,022-second coupled timeout and 3,810-second interrupted fit
remain negative evidence for the superseded general-coexistence route; they are
not the current execution path.

Commands:

```bash
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/build_packet.py
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/evaluate_closure_points.py
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/run_fixed_pressure_fit.py
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/run_reactive_bubble_diagnostic.py
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/screen_pressure_parameter_directions.py --config analyses/phase3/ionic_epcsaft_regression/pressure_first/config/pressure_block_ladder.json
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/fit_cai_mea_water_binary.py
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/fit_cai_mea_water_binary.py --config analyses/phase3/ionic_epcsaft_regression/pressure_first/config/cai_baygi_3b2b_binary_fit.json
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/fit_cai_mea_water_binary.py --config analyses/phase3/ionic_epcsaft_regression/pressure_first/config/cai_baygi_3b4c_binary_fit.json
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/summarize_pressure_block_ladder.py
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/summarize_results.py
uv run python analyses/phase3/ionic_epcsaft_regression/pressure_first/scripts/render_figures.py
```
