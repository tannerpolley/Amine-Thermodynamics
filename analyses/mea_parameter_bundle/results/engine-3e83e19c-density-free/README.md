# Density-free conditional reference on Engine 3e83e19c

**The reported candidate passes all six limits.** The single-start five-coordinate
fit converged and is usable after nine iterations. Its dimensionless native cost
is 23.775639474323388, down from 23.860996312136727. All 149 objective rows are
available and finite. The endpoint replay costs 23.77563947432554, differing from
the native result by 2.1529444893531036e-12. No limit, bound, start, fixed
coefficient or model choice was changed to obtain this decision.

Authority: [issue #213](https://github.com/tannerpolley/Amine-Thermodynamics/issues/213),
based on merged #212 at `0ee4705`. The starting candidate is
`../engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json`,
SHA-256 `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91`.
Engine commit `3e83e19ccc771b51d8ebc038931ab25192f4c5b5` supplies the only wheel,
SHA-256 `0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`.
The installed package was verified byte for byte against it; no Engine source
checkout was imported. The main checkout's prepared virtual environment and
wheel storage supply the ignored local runtime, with project imports from this
issue worktree.

## Method and quantities

[The declaration](spec.json) fixes all parameters except four constant
interactions and the MEAH⁺–water reciprocal-temperature slope about 313.15 K.
It preserves the candidate's full Born, permittivity and reaction declarations,
using the reported-fit bounds and heat-170 coordinate scales. All 149 ordered
base targets, observations, residual scales and weights are retained. The fit
uses ordinary weighted least squares, half the squared weighted residual sum,
with 180 maximum iterations, function/parameter/gradient tolerances
`1e-6` / `1e-10` / `1e-8`, and a native elapsed-time limit of 600 s.
There is one start, copied byte for byte into [start.json](start.json).

[The native result](run/reference/candidate/native-fit.json),
[endpoint](run/reference/candidate/parameters.json),
[timing](run/timing.csv) and [summary](summary.json) retain the numerical result.
The native fit took 9.487051981006516 wall seconds and 187.84040500000003 CPU
seconds, using 32 requested process workers with native thread pools at one.
The five fitted values and units are in [parameters.csv](parameters.csv).
The MEAH⁺–water and carbamate–MEAH⁺ constant interactions reach their lower bounds.

[Reference quantities](reference-quantities.json) are evaluated on exactly
47 pressures, 94 species fractions, 8 Vinjarapu heats and 14 separate Arcis
heats. Pressure and species average absolute relative deviations are
11.898355269557591% and 7.090199842730563%. Vinjarapu and Arcis heat root-mean-square
errors are 1.8225957856620474 and 8.070718549141134 kJ/mol CO₂.
[The base replay](reference-base-replay.json) retains the 149 fitted quantities;
[the Arcis replay](reference-arcis-replay.json) retains the 14 non-fitted heats
at 322.5 K and 0.51/1.03 MPa. Every prediction is available, finite and meets
its requested tolerance. Arcis rows never enter the fit or common cost.

[limits.json](limits.json) owns the six unrounded limits, their definitions,
hashed inputs, candidate values and signed margins (limit minus candidate).
The definitions are 1.10 times the common cost, two percentage points above
each pressure/species deviation, 1 kJ/mol CO₂ above each heat error, and 1.05
times the refitted constant-interaction Cai cost, 91.29322049026165.
Candidate reduction selects the exact base IDs before summarizing #212's
307-row replay. Arcis values come from its retained display errors and RMSE;
Cai cost comes from its retained score. [Candidate quantities](candidate-quantities.json)
retain the reduced result. All margins are positive; comparisons use the stored
binary floating-point values without display rounding. A scalar table in the
[notebook](../../joint-recalibration/index.qmd#density-free-213) answers this
acceptance question; curves would not clarify it.

## Execution and limits

The fit ran once in transient user unit `issue213-fit.service`, invocation
`1a2953bd56d844268f0d5f619f48892e`, with `Nice=10`. Waiting used
`systemctl --user is-active`; no process was killed. [Commands](commands.json)
and [provenance](provenance.json) record the producer identities, exact commands,
package versions, hashes and timings. Fixed calculations also used `nice -n 10`
and `python -I`. There are 80 gross added executable lines against `0ee4705`,
including the producer docstring, imports and all branches; no persistent test
was added.

The first reduction attempt selected no Arcis rows because the new selector
expected an `arcis` prefix, while the source IDs are DOI locators. Its 149-row
replay and empty Arcis file remain under [analysis-attempt-1](analysis-attempt-1/),
with the exact error and original producer hash. The selector was replaced by
the existing producer's non-Vinjarapu selection, and an exact 14-row assertion
was added. Only fixed replay and reduction were repeated; the fit was never
repeated. The final-source analysis command has its own measured wall time in
[analysis-timing.json](analysis-timing.json).

This fit is a comparison reference calibrated to the same 149 quantities
without density data, conditional on the candidate's other parameters. It is
not an independent model. The results are calibration statistics and numerical
verification, with no propagation of measurement, parameter or model-form
uncertainty and no physical validation or process-use qualification. Passing
makes the candidate ready for adoption by the one-wheel paper-evidence package,
together with the density requirements judged in #212 and the phase rebuild;
this issue makes no parameter adoption. Generators, manuscript files and the
selected record are unchanged. Independent delivered review and investigator
promotion for manuscript use remain open. The notebook was rendered only under
`/tmp`; the preview service on port 8770 was untouched.
