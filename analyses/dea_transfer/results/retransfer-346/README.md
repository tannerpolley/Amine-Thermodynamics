# DEA F2 campaign stopped at required unavailable searches

The first F2 start converged on the Engine optimizer's function tolerance, at
cost 8.033971893124118, for 30 fitted Lawson pressures and 50 fitted Carson
heats. This dimensionless cost is the declared half-sum of weighted squared
residuals. Its seven-iteration history and endpoint are retained in
`f2/start-0/unpenalized/stage-0/`. The cold endpoint replay gives cost
8.03397189312541, a relative difference of approximately 1.61e-13. No
continuation was needed.

The completed first finite search has 363 data-state evaluations and 3,456
grid-state evaluations (four fitted concentrations, nine temperatures from
313.15 to 393.15 K, 48 loading nodes from 1e-5 to 1.167 mol CO2/mol DEA,
and pressure factors 1.05 and 3.0). Of these 3,819 evaluations, 3,764 are
available and 55 are unavailable. No native resolved split was found; this
is a lower bound, not a conclusion that the unavailable states are stable.
Negative optimizer iterates with no resolved descent are not admitted as splits.

The 55 unavailable evaluations are all data states: 50 Carson unloaded
initial states, four Weiland unloaded states, and Lawson Table VIII row
identity `lawson-1976-viii:1:problem`. The first 54 have Engine status
`CentralSolveUnavailable` and cause `failed final trial optimizer or
undetermined evidence: 12`; the Lawson state has the same status and cause
ending `: 1`. Exact identities, declared data-state bindings, raw distances
and Engine messages are retained in `campaign-stop.json` and `f2/search-0.json`.

This is the unavailable-search case covered by shared-route issue 359.
The interrupted process was no longer running on resume. Work stops under
the owner's instruction without restarting the route, fitting the second
start, selecting a start, adding a local alternative, or running a penalty.
The second start's complete 80-row pre-fit replay remains available at cost
14.803952118169988 in `f2/start-checks.json`. It is not a converged fit.

The F0 replay evidence is in `replay.json`. The same-row F0 calculation in
`previous/` reproduces all 80 original fitted predictions exactly and the
cost to 7.59e-13 relative; it also calculates all seven Lawson observations
at 394.26111111111106 K. Its deviation tables keep all 299 role-table rows,
including the 14 unavailable native Horstmann addition-enthalpy predictions.
The separate shared correction in issue 360 owns those binary excess-enthalpy
comparisons. Its first-row direct residual-enthalpy probe is retained; no
local comparison implementation is adopted.

No selected F2 snapshot, conditional standard errors, F2 model curves,
current-result notebook or manuscript promotion is claimed. Issues 359 and
360 block completion; no PR is opened. The input adaptation and these retained
outputs add no executable code. The source check and published-model
comparison limitations are in `source-check.md`.
