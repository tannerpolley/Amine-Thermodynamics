# ePC-SAFT Feedback: Issue #5 Phase 2 Activity Solver

## Downstream Context

Repository: `MEA-Thermodynamics`

Downstream issue: `tannerpolley/MEA-Thermodynamics#5`

Upstream tracking issue: `tannerpolley/ePC-SAFT#115`

Downstream evidence comment: https://github.com/tannerpolley/ePC-SAFT/issues/115#issuecomment-4457708894

## Verified Local Inputs

Austgen 1991 Table V verifies the Phase 2 MEA reaction constants on an unsymmetric mole-fraction activity basis:

- solvents use pure-liquid standard states,
- ionic and molecular solutes use ideal infinitely dilute aqueous solution reference states,
- equilibrium constants use products of `x_i gamma_i`,
- R1-R5 coefficients are available on the H3O+ reaction basis,
- protonated MEA dissociation is corrected to the pure amine reference state.

## Pinned Package State

Pinned dependency:

```text
epcsaft @ git+https://github.com/tannerpolley/ePC-SAFT.git@e9510abae528016bd2513f12069fc0534b252bea
```

`uv run python scripts\check_epcsaft_integration.py --mode final` passes, but a Phase 2 activity-coupled speciation smoke using the promoted Austgen constants fails before producing equilibrium rows:

```text
backend_unavailable: analytic/CppAD/implicit chemical-equilibrium residual jacobian is unavailable for activity- or concentration-coupled standard states.
```

## Required Upstream Contract

Issue #5 needs a generic package route that can solve the MEA true-species reaction set with fixed thermodynamic activity constants and ePC-SAFT activity coefficients without adding a downstream MEA-owned nonlinear solver. Once upstream issue #115 lands, MEA-Thermodynamics should repin `epcsaft`, rerun final integration, then generate `phase2_equilibrium_results.csv`, parity tables, metrics, and figures from the Phase 2 analysis.
