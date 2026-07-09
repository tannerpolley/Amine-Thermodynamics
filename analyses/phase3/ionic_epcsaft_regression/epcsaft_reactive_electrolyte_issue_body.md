# Generalize Reactive Electrolyte Equilibrium Sweeps And Regression, Using MEA-CO2-H2O As A Case Study

## Summary

The new electrolyte bubble-pressure and reactive-speciation APIs are a major step forward. They make it possible to start replacing the legacy MEA workflow with a physically coupled ePC-SAFT calculation:

```text
T, loading, solvent composition
  -> reactive speciation with ePC-SAFT activities
  -> electrolyte bubble pressure with neutral vapor species
  -> vapor composition and CO2 partial pressure
```

The MEA-CO2-H2O system is a useful first serious case study because it combines:

- a neutral solvent/reactant basis;
- multiple liquid-only ionic species;
- charge neutrality;
- several coupled reactions;
- very low to high CO2 partial pressures;
- ordered loading/temperature sweeps;
- parameters that need to be fit against the final observable, not only against isolated pure-component or fixed-composition properties.

The package should not add an MEA-only solver. The general improvement should be a composable framework for **reactive electrolyte equilibrium sweeps and coupled regression**, with MEA as one validation configuration.

## Why A Coupled Objective Is Needed

For MEA-CO2-H2O, the measured Jou target is CO2 partial pressure. That target is not a direct function of one fixed liquid composition. It depends on the whole thermodynamic chain:

```text
record: T, loading, MEA wt%
  -> material totals
  -> chemical equilibrium / true-species liquid composition
  -> ePC-SAFT activity coefficients
  -> electrolyte bubble pressure
  -> vapor composition
  -> CO2 partial pressure residual
```

Fitting only pure parameters or fixed-composition fugacity/activity targets can improve a lower-level property while worsening the actual observable. In the MEA repo this showed up directly:

- individual state, activity, reactive-speciation, and bubble-pressure calls can work;
- successful single points can be reasonably close;
- the full Jou grid is not robust yet when run as a prediction/regression workflow.

The regression objective should match the prediction path. Otherwise the model is tuned at the wrong layer.

## Current MEA Case-Study Evidence

From the MEA-Thermodynamics branch:

```text
<repo-worktree>
branch: codex/epcsaft-with-electrolyte-born-terms
```

Relevant command:

```bash
$env:UV_CACHE_DIR = "$PWD/.uv-cache"
uv run python -m MEA.epcsaft_ionic.plot_results
```

Current package-backed path:

```text
solve_reactive_speciation(...)
  then mixture.equilibrium(kind="electrolyte_bubble_pressure", ...)
```

Full-grid result with the current fitted parameter CSV:

```text
pressure successes: 22/161
speciation successes: 66/74
raw pressure median |log10(model/data)| on successes: 4.042
```

Representative 20-point grid with literature/default seed parameters:

```text
pressure successes: 14/20
median |log10(model/data)| on successes: 0.368
max |log10(model/data)| on successes: 0.676
reaction residuals on successful points: generally around 1e-7
```

That means the new package APIs are useful and physically meaningful, but the workflow still needs better continuation, batch solving, diagnostics, and coupled regression support before it can approve a full reactive electrolyte VLE model.

## General Capability Request

Add a generic framework for ordered or batched reactive electrolyte equilibrium calculations and regression.

This should support systems like:

- aqueous amines such as MEA, MDEA, DEA, AMP;
- sour-gas absorption systems;
- salt + solvent + volatile gas systems;
- ionic-liquid solvent blends;
- other electrolyte systems where reactions and phase equilibrium are coupled.

MEA should be treated as a first validation case, not as a hard-coded package path.

## Proposed Generic API Concepts

### 1. Equilibrium sweep / batch API

Yes: it would be very helpful if phase-equilibrium and related methods could take a suite or array of inputs and automatically solve them as a sweep.

Many thermodynamic workflows are not isolated points. They are ordered curves:

```text
T fixed, loading increasing
T fixed, composition changing
pressure fixed, salt molality changing
temperature sweep at fixed composition family
```

The package should expose a general sweep interface that knows it is solving a related sequence and can reuse previous answers.

Possible API shape:

```python
results = mixture.equilibrium_sweep(
    kind="reactive_electrolyte_bubble_pressure",
    points=[
        {"T": 313.15, "totals": ..., "initial_x": ..., "target": ...},
        {"T": 313.15, "totals": ..., "initial_x": ..., "target": ...},
        ...
    ],
    reactions=reactions,
    balances=balances,
    vapor_species=["CO2", "H2O", "MEA"],
    nonvolatile_species=[...],
    options=...,
    continuation="auto",
)
```

Important behavior:

- detect that points are an ordered sweep;
- use the previous successful `x_liq`, vapor composition, pressure, and phase/bubble result as warm starts;
- support bidirectional retries when a middle point fails;
- record failed points without losing the full result array shape;
- return compact per-point diagnostics.

This should be generic. It should not assume MEA, CO2, or any specific reaction set.

### 2. Composable reactive electrolyte bubble workflow

The package currently has the pieces:

- `solve_reactive_speciation(...)`;
- `electrolyte_bubble_pressure(...)`;
- `ReactionDefinition`;
- `ReactiveSpeciationOptions`;
- `ElectrolyteBubbleOptions`.

The MEA workflow needs a composition of those pieces:

```text
material totals + reactions
  -> activity-coupled speciation result
  -> electrolyte bubble pressure result
  -> selected vapor partial pressure target
```

Possible generic API shape:

```python
result = epcsaft.solve_reactive_electrolyte_bubble(
    species=species,
    mixture_factory=mixture_factory,
    T=T,
    P_seed=P_seed,
    balances=balances,
    totals=totals,
    reactions=reactions,
    initial_x=initial_x,
    vapor_species=vapor_species,
    nonvolatile_species=nonvolatile_species,
    speciation_options=...,
    bubble_options=...,
)
```

Required result fields:

```text
success
message
x_liq
activity_coefficients
reaction_residuals
mass_balance_residuals
charge_residual
P_total
y_vap
partial_pressures
fugacity_residual
fugacity_residual_norm
state_failure_count
diagnostics
```

### 3. Fixed-shape diagnostic results

Regression and sweeps need fixed-length outputs. Exceptions are fine for direct single-point calls, but batch/regression workflows need structured failed results.

Recommended option:

```python
options = ReactiveElectrolyteOptions(error_mode="result")
```

Then failed points return:

```text
success=False
message=...
best_x_liq if finite
best_P if finite
best_residuals if finite
penalty_residuals
diagnostics
```

This avoids brittle outer loops where exception handling changes residual-vector length.

### 4. Generic coupled regression terms

The package should provide reusable regression terms rather than a hard-coded MEA regressor.

Generic target examples:

```text
target kind: vapor_partial_pressure
target species: CO2
observed: P_CO2
model path: reactive_speciation -> electrolyte_bubble_pressure
```

```text
target kind: species_composition
target phase: liquid
observed: x_i for selected species
model path: reactive_speciation
```

```text
target kind: reaction_residual
model path: reactive_speciation
```

Possible API shape:

```python
problem = epcsaft.regression.ReactiveElectrolyteFitProblem(
    species=species,
    records=records,
    balances=balances,
    reactions=reactions,
    targets=[
        VaporPartialPressureTarget(species="CO2", column="P_CO2"),
        LiquidCompositionTarget(species=["MEA", "MEAH+", "MEACOO-", "HCO3-"]),
    ],
    fit_parameters=[
        PureParameter("MEAH+", "d_born"),
        PureParameter("MEACOO-", "d_born"),
        BinaryInteraction("CO2", "MEA", "k_ij"),
    ],
)
```

The MEA repo could then configure this general problem without the package knowing MEA chemistry internally.

### 5. Parameter masks across pure and interaction parameters

MEA needs to fit a controlled subset of parameters:

```text
MEA: m, s, e, possibly association terms
MEAH+: s, e, d_born
MEACOO-: s, e, d_born
HCO3-: s, e, d_born
selected k_ij pairs
```

But the general package need is broader:

- fit selected pure parameters;
- fit selected Born parameters;
- fit selected binary interaction parameters;
- keep all other parameters fixed;
- provide bounds and priors/regularization;
- write results back to a user-owned dataset.

### 6. Better bubble-pressure numerics

Observed failure modes in MEA:

```text
electrolyte bubble pressure could not bracket a pressure root
electrolyte bubble pressure did not converge
```

Helpful general improvements:

- solve pressure in `log(P)` rather than linear `P`;
- track best finite point during bracketing and bisection;
- return `best_P`, `best_objective`, `best_y_vap`, `best_partial_pressures`, and `best_fugacity_residual_norm`;
- support continuation seeds for `P`, `y_vap`, and previous liquid composition;
- make low-pressure volatile-gas cases stable without enormous vapor histories.

### 7. Better reactive-speciation continuation

Successful MEA points close reaction residuals very well, but some points fail despite being close to tolerance.

Helpful general improvements:

- expose warm-start/continuation helpers for ordered grids;
- allow separate tolerances for mass balance, charge balance, and reaction residuals;
- return named reaction residuals instead of only ordered lists;
- expose best finite `x`, activity coefficients, and residuals when strict convergence fails.

### 8. Performance improvements for optimization loops

Calling reactive speciation plus bubble pressure inside Python/SciPy finite-difference least-squares is too slow for practical parameter regression.

Helpful general improvements:

- batch evaluation over many records;
- warm-start reuse across rows;
- native residual-vector evaluation where possible;
- optional parallel evaluation where continuation is not needed;
- progress diagnostics for long regressions;
- caching/reuse for repeated parameter/property lookups.

## Suggested Acceptance Tests In ePC-SAFT

Add package tests that are generic but use MEA-like fixtures.

### Unit/API tests

- reactive electrolyte bubble single point returns a complete structured result;
- failed bubble point can return best finite diagnostic result when requested;
- ordered sweep reuses previous solutions and returns one result per input point;
- named reaction residuals are available;
- fixed-shape residual vector is produced even with failed records.

### MEA-like integration tests

Use a small fixture, not the full Jou grid:

```text
3 temperatures
3 loadings each
9 species
5 reactions
CO2/H2O/MEA vapor species
liquid-only ionic species
```

Acceptance:

```text
all result objects returned
no residual-vector shape changes
successful points have finite P_CO2 and finite x_liq
reaction residuals close for successful speciation points
continuation path solves more points than cold isolated solving
```

### Optional heavy benchmark

Gate a heavier real MEA regression behind an environment variable:

```bash
EPCSAFT_RUN_MEA_REACTIVE_VLE=1
```

This can use Jou-style CO2 pressure data and speciation targets to verify the end-to-end coupled regression path.

## Why This Is General

The requested package layer is not:

```text
fit_MEA_CO2_H2O()
```

It is:

```text
reactive electrolyte equilibrium sweep
  + generic target definitions
  + generic parameter masks
  + robust diagnostics
  + batch/continuation evaluation
```

MEA-CO2-H2O is simply the first demanding case study that shows why those abstractions are needed.

## Related Local MEA Files

The MEA branch currently has the case-study integration in:

```text
src/MEA/epcsaft_ionic/model.py
src/MEA/epcsaft_ionic/plot_results.py
src/MEA/epcsaft_ionic/regress_parameters.py
tests/test_epcsaft_ionic.py
analyses/phase3/ionic_epcsaft_regression/epcsaft_ionic_package_feedback.md
```

Once this package work exists, the MEA repo can remove diagnostic workarounds and make package-backed reactive electrolyte VLE the approval path.

