# Dilute neutral bubble: evaluation-only evidence

The existing native partial-pressure observation is supported at the fixed
stage-2 inputs, with CO₂–MEA intercept and slope both zero. All 66 declarations
(22 distinct source states at liquid CO₂ mole fractions 1e-5, 1e-6 and 1e-7)
return Available with requested equilibrium tolerance met. No fit ran.

The [design addendum](/home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/tmp/joint-design/amendment-4-addendum-dilute-bubble.md)
owns the proposed observation and remaining design decisions. The
[data owner](../../../../../../data/reference/MEA/physical_solubility/README.md)
owns the measured-density conversion, raw tables, uncertainties and sources.
The earlier [preflight stop](../README.md) is historical and unchanged.

`summary.json` contains the numerical comparisons. `inputs.json` retains the
66 declarations; `results.json` retains native predictions, raw compiled
residuals, phases, pressure-density derivatives and solved-state diagnostics.
`target-inputs.json` and `target-replay.json` retain a separate-process cold
replay of 22 source-transformed targets at epsilon=1e-5. `initial-probe.json`
retains the first 313.15 K, 30% MEA, epsilon=1e-6 call. It is an additional
diagnostic state, not a source observation.

The selected epsilon=1e-5 gives pCO₂=565.458365–2244.447500 Pa,
P=2329.641493–57404.683320 Pa and Hx_model=5.65458e7–2.24445e8 Pa.
The largest relative Hx change to the next decade is 8.75251e-5, below 1e-4.
Max raw residual is 1.57208e-13, max normalization error 2.22045e-16 and
minimum dP/drho 2435.3871 Pa m³/mol. Partial pressure equals P times the
returned vapor CO₂ mole fraction exactly. The replay has zero pressure change
and log-residual identity error 3.33067e-16. No returned branch or root count
is invented when the observation supplies null; explicit phase kinds,
compositions, densities and positive mechanical derivatives are retained.

`pressure-properties.json` retains native liquid log-fugacity pressure actions
and vapor log fugacity coefficients. The liquid partial molar volume inferred
from the native derivative is 32.9614–36.2440 cm³/mol at the bubble and
101325 Pa endpoints. With an assumed absolute envelope 100 cm³/mol, the
Poynting estimate to 101325 Pa is 0.416577%; including the computed gas
coefficient change at fixed bubble-vapor composition gives 0.695049%.
This is conditional on that pressure, gas reference and volume envelope.
It does not establish the unread Xu Table S3's measurement pressures.

`engine-identity.json` was produced by the existing `fit_campaign.verify`.
All 12 installed Engine files match wheel SHA-256
`98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a`,
merged Engine commit `84ca269dfa0c7068417a1c4c326acae276d4d965`.
Direct calls used the task's pinned interpreter through
`uv run --no-project --python tmp/amendment-2-84ca269d/venv/bin/python python`,
from the requested worktree, with `nice -n 10`, `PYTHONPATH=src` and
single-thread BLAS/OpenMP. No Engine checkout was imported. Every numerical
problem used `Problem`, `Amounts`, explicit neutral `Phase` support,
`Free` pressure, `Pinned(0)` vapor, no reactions and row tolerance 1e-10;
`regression.observation(..., 'partial_pressure', phase='V',
species=['carbon-dioxide'], form='log_ratio')` supplied the observation.
`solve_equilibrium` and `compile_problem(...).evaluate(...)` supplied
independent retained state/closure inspection of the declaration.

Measured retained evaluation intervals total 0.771141673 CPU-s. The task
charges 2 CPU-s against the original 120 CPU-s allowance, including the
preliminary property scan and a failed pressure-direction call. Accounting
also charges 100 CPU-s for preparation and reporting, and 1800 active wall-s
including finish allowance. There are zero new executable files or changes;
the gross campaign remains 861/900 lines. No process remains running.

This is numerical verification of a fixed-input calculation plus converted
source estimates. It is neither parameter calibration nor physical
validation. Original start-B, parameter-derivative, dielectric-branch and
gas-free density checks remain unrun. Source pressure/gas transfer and
independent readiness/delivered review remain open. No fit is released.
