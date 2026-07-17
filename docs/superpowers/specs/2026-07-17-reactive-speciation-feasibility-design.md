# Reactive Speciation Feasibility Design

**Decision date:** July 17, 2026

**Status:** Approved cheap experiment

## Outcome

Determine whether MEA can own a small, application-specific reactive-state solver while delegating every thermodynamic activity evaluation to the clean `epcsaft` provider. The experiment is successful only if it can construct the existing nine-species MEA system through public provider interfaces, establish an explicit activity convention, solve the existing eight-equation equilibrium-and-balance system, and compare the result with the immutable `epcsaft` 1.5.2 evaluation lane.

This is a diagnostic reference oracle and seed generator. It is not a regression engine, a parameter-promotion path, or evidence that the clean upstream regression capability is admitted.

## Ownership boundary

- MEA owns the reaction network, apparent-component balances, electroneutrality equation, representative states, initial guesses, solver acceptance, and comparison receipt.
- The clean provider owns EOS evaluation and residual chemical-potential or fugacity-coefficient output.
- The clean regression package remains the owner of eventual native Ceres optimization, exact residual Jacobians, and complete regression diagnostics.
- Generic reactive-equilibrium capability remains a future upstream concern; this experiment implements only the fixed MEA system.

The experiment does not change `upstream_execution_admitted`, promote parameters, modify frozen readiness hashes, or replace the immutable 1.5.2 final-evaluation lane.

## Scientific model

The state vector is the existing nine true-species basis:

`CO2`, `MEA`, `H2O`, `MEAH+`, `MEACOO-`, `HCO3-`, `CO3^2-`, `H3O+`, and `OH-`.

Eight reduced log-ratio variables generate positive, normalized mole fractions through a softmax. The residual vector contains five reaction-equilibrium residuals plus carbon loading, water-to-amine, and electroneutrality residuals. Phase 1 ideal Smith-Missen results supply the nominal initial guesses. The experiment repeats each state from deterministic perturbations of that seed.

The thermodynamic boundary is a narrow evaluator protocol:

```text
evaluate(temperature_K, pressure_Pa, mole_fractions) -> ActivityState
```

`ActivityState` must contain finite log activities in the exact mole-fraction activity convention required by the frozen reaction constants, the provider evaluation count, and sufficient diagnostics to reject an undefined phase or activity mapping.

## Activity-convention gate

The provider adapter must derive the reaction activities from a documented public provider quantity and prove that its standard state matches the existing mole-fraction-basis equilibrium constants. Agreement cannot be created with fitted reaction offsets, per-species shifts, or undocumented conversions.

If the clean provider does not expose enough public information to establish that mapping, the experiment stops at that gate and records the missing capability. That fail-closed result is useful: it identifies the smallest upstream contract needed before the lightweight solver can be scientifically compared.

## Five experiment tasks

1. Construct the nine-species MEA parameterization through the clean provider's public parameter interface, using an explicitly non-authoritative experiment fixture with source hashes.
2. Obtain finite activities or chemical potentials and validate their convention before using them in reaction residuals.
3. Solve the eight-equation MEA system at three representative 30 wt% MEA states using the Phase 1 result as the nominal seed.
4. Compare every composition component and every reaction/balance residual with the pinned `epcsaft` 1.5.2 lane.
5. Repeat each solve from deterministic perturbed seeds and record convergence, provider evaluations, elapsed time, and solution spread.

The representative states are fixed at 313.15 K and loadings 0.20, 0.40, and 0.60 mol CO2 per mol MEA. Pressure is taken from the pinned reference evaluation for each state when that lane supplies it; the receipt records the exact pressure used.

## Artifacts and acceptance

The implementation lives in a focused MEA module rather than expanding the regression module. Unit tests cover solver behavior with a controlled evaluator and the fail-closed activity gate. An analysis script produces a machine-readable receipt containing repository and provider identities, fixture hashes, state definitions, activity convention, residuals, composition differences, seed-repeat statistics, timing, and conclusion.

The experiment may conclude either:

- **feasible:** all five tasks run through public interfaces, activities have a proven convention, all accepted solutions meet the existing residual tolerance, and repeated seeds converge consistently; or
- **blocked:** the receipt names the first unmet scientific or provider-contract condition and includes all evidence gathered before it.

Neither conclusion changes regression readiness or supports parameter promotion. Manuscript claims remain bound to the existing final integration and submission gates.
