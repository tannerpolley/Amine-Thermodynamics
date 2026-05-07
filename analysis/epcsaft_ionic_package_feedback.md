# ePC-SAFT Package Feedback For MEA-CO2-H2O Ionic VLE Approval

## Context

This MEA-Thermodynamics branch now has a runnable full ionic MEA-CO2-H2O
workflow in `MEA.epcsaft_ionic`. It uses the full true-species vector:

```text
CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-, H3O+, OH-
```

The workflow enables the current advanced Born options from the local ePC-SAFT
runtime:

```python
{
    "elec_model": {
        "rel_perm": {"rule": "empirical", "differential_mode": "numerical"},
        "born_model": {
            "d_Born_mode": 3,
            "solvation_shell_model": True,
            "dielectric_saturation": True,
            "mu_born_model": {
                "differential_mode": "numerical",
                "comp_dep_delta_d": True,
            },
        },
    },
}
```

The MEA repo can now:

- build an ionic dataset under `data/epcsaft_datasets/MEA_CO2_H2O_ionic_fit/`;
- fit MEA, MEAH+, MEACOO-, HCO3-, selected binary interactions, and fitted
  `d_born` values using public ePC-SAFT state/activity/fugacity calls;
- regenerate ionic pressure and speciation diagnostic plots;
- run the full project export pipeline successfully.

The remaining blocker is not file organization or a missing MEA-side script. The
remaining blocker is that the ePC-SAFT package does not expose the ionic VLE /
bubble-pressure and reactive speciation APIs needed to make this workflow
"approve" as a thermodynamic model rather than a diagnostic scaffold.

## 2026-05-06 Retest After New Package Equilibrium APIs

The package has since added the key API surface requested in the first pass:

```text
epcsaft.ElectrolyteBubbleOptions
epcsaft.ElectrolyteBubbleResult
epcsaft.electrolyte_bubble
mixture.equilibrium(kind="electrolyte_bubble_pressure", ...)
epcsaft.ReactionDefinition
epcsaft.ReactiveSpeciationOptions
epcsaft.ReactiveSpeciationResult
epcsaft.solve_reactive_speciation(...)
mixture.equilibrium(kind="chemical_equilibrium", ...)
epcsaft.regression.fit_mea_co2_h2o_electrolyte(...)
```

These additions materially improve the MEA integration. A representative
MEA-CO2-H2O calculation now succeeds with package-backed activity-coupled
speciation plus electrolyte bubble pressure:

```text
T=40 C, alpha=0.353, obs=0.0851 kPa, pred=0.2316 kPa, log10 error=0.435
T=80 C, alpha=0.5785, obs=235 kPa, pred=378 kPa, log10 error=0.207
T=120 C, alpha=0.639, obs=2804 kPa, pred=3827 kPa, log10 error=0.135
reaction residuals are generally near 1e-7 for successful points
```

However, this is not yet a robust approval-grade package workflow for the full
MEA Jou grid:

```text
Full package-backed plot with the old fitted parameter CSV:
  pressure successes: 22/161
  speciation successes: 66/74
  raw pressure median |log10(model/data)| on successes: 4.04

Representative 20-point grid with literature/default seeds:
  pressure successes: 14/20
  median |log10(model/data)| on successes: 0.368
  max |log10(model/data)| on successes: 0.676
```

The current remaining blocker has shifted from "missing API" to "API robustness,
continuation, diagnostics, and coupled regression ergonomics."

## Current Package Improvement Notes

### Electrolyte bubble pressure root finding

Most failed MEA pressure points now fail in `electrolyte_bubble_pressure`, often
with:

```text
electrolyte bubble pressure could not bracket a pressure root
electrolyte bubble pressure did not converge
```

Observed behavior in low-pressure MEA cases:

- the objective can change sign or approach a small residual, but bisection can
  collapse to a repeated pressure such as `6332.8125 Pa`;
- the method uses pressure-space bisection over very wide pressure spans, which
  is fragile for sub-kPa CO2 partial pressures and water/MEA-dominated vapor;
- diagnostics include long vapor histories, but the summarized failure payload
  does not directly expose the best pressure, best objective, or closest
  partial pressures in a compact field.

Recommended package changes:

- solve the pressure root in `log(P)` rather than linear pressure;
- track and return the best evaluated point on failure;
- include `best_P`, `best_objective`, `best_y_vap`, `best_partial_pressures`,
  and `best_fugacity_residual_norm` in `SolutionError.diagnostics`;
- add optional continuation seed support across a loading/temperature series;
- add a relaxed diagnostic result mode that returns the best point with
  `success=False` instead of throwing, so outer regression loops can keep a
  fixed residual vector without expensive exception handling.

### Reactive speciation continuation and soft acceptance

The new native chemical-equilibrium path is very useful. Successful MEA points
close reaction residuals near `1e-7`. Remaining failures are often close enough
to be diagnostically useful, for example residual norms around `3e-7` to
`9e-7` against a strict `1e-7` tolerance.

Recommended package changes:

- expose continuation/warm-start helpers for ordered loading grids;
- optionally return a structured `ReactiveSpeciationResult(success=False, ...)`
  when finite best states exist, instead of only throwing `SolutionError`;
- provide separate tolerances for mass balances, charge balance, and reaction
  residuals;
- compactly expose `best_x`, `best_activity_coefficients`, and per-residual
  names in failure diagnostics.

### Coupled MEA regression target

`fit_mea_co2_h2o_electrolyte(...)` is now public, but it still fits the pure
parameter benchmark terms. The MEA application needs a public helper for the
coupled objective:

```text
loading + T + apparent totals
  -> reactive speciation
  -> electrolyte bubble pressure
  -> CO2 partial pressure residual
  -> optional speciation residuals
  -> optional binary interaction and d_born fitting
```

Recommended package changes:

- add a public regression term for `electrolyte_bubble_pressure`;
- allow fitting selected binary interactions alongside pure ion parameters;
- support fixed/fitted masks for `m`, `s`, `e`, `d_born`, and selected `k_ij`;
- provide a batch evaluator for many MEA records that reuses continuation seeds;
- guarantee fixed-length residual vectors even when individual records fail.

### Performance and optimizer ergonomics

Wrapping `solve_reactive_speciation` and `electrolyte_bubble_pressure` inside
SciPy finite-difference least-squares is very slow from the MEA repo. A small
10-record/10-record/8-evaluation optimization was interrupted after several
minutes. The package should provide a faster batch regression path or native
objective evaluation for this workflow.

Recommended package changes:

- add batch evaluation for repeated MEA rows;
- expose warm-start state reuse between records;
- expose native residual-vector callbacks where possible;
- add concise progress diagnostics for long regressions;
- include an opt-in MEA Jou-grid regression benchmark in the ePC-SAFT test suite.

## Current MEA-Side Evidence

From this worktree:

```powershell
uv run python -m MEA.epcsaft_ionic.regress_parameters
uv run python -m MEA.epcsaft_ionic.plot_results
uv run python -m unittest tests.test_epcsaft_ionic tests.test_nine_species_chemistry -v
uv run python MEA\run_plot_exports.py
```

Fresh results:

```text
Ionic regression optimizer: success True, xtol termination
Fit subset VLE median |log10(model/data)|: 3.29331 -> 0.91663
All VLE pressure successes: 161/161
All speciation activity evaluations: 74/74
Raw all-VLE pressure median |log10(model/data)|: 1.04110
Calibrated all-VLE pressure median |log10(model/data)|: 0.28006
```

Generated artifacts:

```text
out/plots/MEA/epcsaft_ionic/pressure/ionic_epcsaft_co2_pressure.png
out/plots/MEA/epcsaft_ionic/speciation/ionic_epcsaft_speciation_activity.png
out/epcsaft/ionic_regression/ionic_parameter_regression_summary.json
out/epcsaft/ionic_regression/ionic_evaluation_summary.json
out/epcsaft/ionic_regression/ionic_pressure_comparison.csv
out/epcsaft/ionic_regression/ionic_speciation_activity_residuals.csv
```

The calibrated pressure curve is useful evidence that the data plumbing and
parameter sensitivity are real. It is not a substitute for an ePC-SAFT ionic VLE
solver.

## Reproduction Of The Package-Level Blocker

The public state API works for the 9-species liquid state and provides
fugacity/activity coefficients. The public TP flash path rejects the same
ion-containing mixture before any VLE calculation:

```powershell
$env:UV_CACHE_DIR = "$PWD\.uv-cache"
@'
import numpy as np
from MEA.epcsaft_ionic.model import FIT_DATASET_DIR, SPECIES, load_vle_targets
from MEA.epcsaft_runtime import ADVANCED_BORN_USER_OPTIONS, load_epcsaft

epcsaft = load_epcsaft()
target = load_vle_targets(1)[0]
params = epcsaft.get_prop_dict(
    FIT_DATASET_DIR,
    SPECIES,
    target.x,
    target.T,
    user_options=ADVANCED_BORN_USER_OPTIONS,
)
mixture = epcsaft.ePCSAFTMixture.from_params(params, species=SPECIES)
print("species:", SPECIES)
print("charges:", np.asarray(params["z"], dtype=float).tolist())
print("x_sum:", float(np.sum(target.x)))
try:
    result = mixture.equilibrium(kind="tp_flash", T=target.T, P=target.P, z=target.x)
    print("tp_flash result:", result)
except Exception as exc:
    print(type(exc).__name__ + ":", str(exc).splitlines()[0])
'@ | uv run python -
```

Observed output:

```text
species: ('CO2', 'MEA', 'H2O', 'MEAH+', 'MEACOO-', 'HCO3-', 'CO3^2-', 'H3O+', 'OH-')
charges: [0.0, 0.0, 0.0, 1.0, -1.0, -1.0, -2.0, 1.0, -1.0]
x_sum: 1.0
InputError: Neutral equilibrium does not support ion-containing mixtures.
```

The source-side reason is explicit in
`C:/Users/Tanner/Documents/git/ePC-SAFT/src/epcsaft/equilibrium.py`:

```text
line 752: def _reject_ion_containing_mixture(mixture: Any) -> None:
line 755:     raise InputError("Neutral equilibrium does not support ion-containing mixtures.")
line 1848: def tp_flash(...)
```

That is correct for the neutral TP flash backend, but it means the MEA repo has
no public package API for the actual ionic CO2 partial-pressure problem.

## Why The Current MEA Fit Cannot Approve Scientifically

The MEA repo currently computes pressure as a liquid CO2 fugacity-pressure
diagnostic:

```text
P_CO2 ~= x_CO2 * phi_CO2_liq * P_liq
```

That is useful for checking sensitivity and relative trends, but it does not
solve:

- incipient vapor composition;
- vapor/liquid fugacity equality;
- nonvolatile ion partition constraints;
- electroneutral liquid constraints during phase equilibrium;
- pressure as an unknown bubble condition;
- speciation and activity coefficients in one coupled solve.

The current speciation activity plot evaluates the measured/reconciled
true-species state with ePC-SAFT activity coefficients. It does not yet solve a
new activity-coupled speciation state because that would require a stable package
contract for repeatedly evaluating electrolyte states inside a reactive
equilibrium solver and, ideally, derivative or robust failure diagnostics.

The consequence is visible in the current metrics: all calculations run, but raw
pressure error remains high and activity reaction residuals remain large.

## Package Changes Needed

### 1. Public ionic bubble-pressure / incipient-vapor API

Add a public API for electrolyte systems where ions remain in the liquid phase
and neutral volatile components can appear in vapor. For this MEA system the
minimum useful target is:

```python
mixture.equilibrium(
    kind="electrolyte_bubble_pressure",
    T=T,
    x_liq=x_true_species,
    volatile_species=["CO2", "H2O", "MEA"],
    vapor_species=["CO2", "H2O", "MEA"],
    nonvolatile_species=["MEAH+", "MEACOO-", "HCO3-", "CO3^2-", "H3O+", "OH-"],
    options=...,
)
```

Required result fields:

```text
success
message
P
y_vap
x_liq
ln_phi_liq
ln_phi_vap
fugacity_residual
fugacity_residual_norm
charge_residual
diagnostics
```

For this repo, even an incipient-vapor calculation returning only `P_CO2` and
diagnostics would be enough to replace the current liquid-fugacity proxy.

### 2. Public reactive speciation solver hook

Expose a package-supported way to solve species mole fractions from:

- total MEA balance;
- total CO2 loading / carbon balance;
- total water balance;
- electroneutrality;
- reaction equilibrium constants;
- ePC-SAFT activity coefficients.

Minimum useful API shape:

```python
epcsaft.solve_reactive_speciation(
    mixture_factory=...,
    T=T,
    P=P,
    totals={"MEA_total": ..., "CO2_total": ..., "H2O_total": ...},
    reactions=[...],
    initial_x=...,
    user_options=ADVANCED_BORN_USER_OPTIONS,
)
```

Required diagnostics:

```text
success
message
x
activity_coefficients
mass_balance_residuals
charge_residual
reaction_residuals
state_failure_count
```

The MEA repo has enough chemistry equations to provide the reaction definitions,
but it should not be responsible for guessing how the native electrolyte state
backend behaves during repeated nonlinear solves.

### 3. Regression API coverage for MEA electrolyte datasets

The source checkout currently contains
`_fit_mea_co2_h2o_pure_parameter_benchmark`, but the installed uv environment
does not expose it:

```text
has benchmark helper False
regression helpers []
```

Please either:

- make the benchmark helper public and installable in the package build; or
- provide a stable public replacement for fitting MEA/MEAH+/MEACOO-/HCO3-
  pure parameters, `d_born`, and binary interactions against mixed
  pressure/activity targets.

Useful public API:

```python
epcsaft.regression.fit_mea_co2_h2o_electrolyte(...)
epcsaft.regression.write_fit_result(...)
```

It should support:

- Born SSM+DS with fitted `d_born`;
- pressure/fugacity targets;
- activity or mean ionic activity targets;
- bound handling;
- fixed versus fitted parameter masks;
- failure diagnostics per record.

### 4. Better Python 3.13 build reliability

This MEA branch uses Python 3.13 via uv. When trying to rely on newer source
features, rebuilding the ePC-SAFT extension may be required. The package should
support a reliable Windows uv build path for this workflow, ideally with:

```powershell
uv sync
uv run python scripts\build_epcsaft.py
uv run python -c "import epcsaft; import epcsaft.regression"
```

If full C++ rebuilds are memory-heavy on this machine, the package should expose
a lower-memory build profile or document the exact required build command.

## Acceptance Target For The MEA Repo After Package Work

Once the package exposes the APIs above, the MEA repo should be able to replace
the current calibrated diagnostic pressure layer with a true package-backed
ionic VLE result.

Suggested first acceptance gate:

```text
uv run python -m MEA.epcsaft_ionic.regress_parameters
uv run python -m MEA.epcsaft_ionic.plot_results
uv run python -m MEA.epcsaft_ionic.approval_check
```

Proposed initial thresholds:

```text
pressure_success_count == pressure_count
speciation_success_count == speciation_count
raw_pressure_median_abs_log10_error <= 0.30
max finite raw_pressure_abs_log10_error <= 1.0
median absolute reaction ln residual <= 2.0 for each modeled reaction
no calibrated pressure correction required for approval
```

Those thresholds are intentionally less strict than the legacy six-species
PC-SAFT benchmark, but they would be enough to show that the ionic ePC-SAFT
workflow is solving the right thermodynamic problem instead of only producing a
diagnostic trend.

## Files In MEA Repo To Revisit After Package Work

```text
MEA/epcsaft_ionic/model.py
MEA/epcsaft_ionic/regress_parameters.py
MEA/epcsaft_ionic/plot_results.py
tests/test_epcsaft_ionic.py
out/epcsaft/ionic_regression/ionic_evaluation_summary.json
```

Likely MEA-side changes after package improvements:

- replace `predict_co2_pressure_kPa` liquid-fugacity proxy with package ionic
  bubble pressure;
- replace fixed/reconciled speciation target evaluation with activity-coupled
  speciation solves;
- remove or demote the current calibrated pressure correction;
- add an approval check that fails when the package-backed raw model does not
  meet the thresholds above.
