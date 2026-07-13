# Upstream request: admit generic native coupled reactive regression

## Downstream repository

- Repository: `tannerpolley/MEA-Thermodynamics`
- Current stable package source: monolithic `epcsaft` 1.5.2 at Git commit `9f51afd`
- Upstream issue: https://github.com/ePC-SAFT/ePC-SAFT/issues/468
- Upstream milestone: `M5 - Regression`

## Command

Current downstream final-lane proof:

```bash
uv run python scripts/check_epcsaft_integration.py --mode final
```

The reduced split-package reproduction should use only public provider, equilibrium, regression, and capability-report APIs from immutable refs. The exact command belongs in the upstream spec once those public entrypoints are admitted.

## Minimal reproduction

Construct a small source-bearing reactive-electrolyte problem with:

- pressure and species-molality target families in the same objective;
- explicit residual weights, parameter bounds, scales, and parameter-family names;
- a reduced subset of the downstream nine-species chemistry and ten-parameter window;
- requested native Ceres execution with supported CppAD or implicit Jacobians;
- structured row, residual-block, source, and target-family diagnostics.

The production downstream proof later expands to 161 pressure rows plus 74 speciation rows. The upstream fixture should remain small and generic while exercising the same public contract.

## Observed behavior

- The pinned monolithic package exposes `fit_reactive_electrolyte_parameters`, but its capability report identifies Python-orchestrated bounded Gauss-Newton behavior and does not prove a native optimization hot loop.
- The split provider/equilibrium/regression architecture does not currently expose a public production capability for coupled reactive pressure/speciation regression.
- Current equilibrium public scope is insufficient to infer this regression surface, and private implementation modules are not a downstream contract.

## Expected behavior

The public regression package should admit a generic coupled reactive problem and report:

- native Ceres ownership of the optimization hot loop;
- the supported CppAD or implicit-Jacobian derivative path;
- explicit initial and final objective values;
- convergence/success and termination reason;
- evaluation and iteration counts;
- initial/final parameter values, movement, bounds, scales, and active-bound flags;
- residual-block norms and complete row diagnostics, including failed rows;
- source- and target-family summaries for pressure and speciation;
- exact provider/equilibrium/regression versions or immutable source refs.

Unsupported target families, derivative modes, or incomplete diagnostics must fail explicitly rather than degrade to a Python callback, alternate optimizer, or partial result.

## Why upstream

Optimizer ownership, derivative support, public request/result schemas, capability reporting, and native runtime guarantees are reusable package responsibilities. MEA should supply targets and acceptance evidence through a stable public API, not duplicate the numerical engine or import private upstream modules.

## Downstream validation commands

```bash
uv run pytest tests/test_epcsaft_ionic_native_regression.py
uv run python scripts/check_epcsaft_integration.py --mode final
```

## Acceptance criteria

- [ ] An upstream spec and plan define the generic reactive problem and public package ownership boundaries.
- [ ] The capability report admits coupled reactive pressure/speciation residual blocks, a native Ceres hot loop, and the supported derivative path.
- [ ] Public API tests cover converged, nonconverged, unsupported, malformed, nonfinite, and partial-row outcomes.
- [ ] The structured result exposes every diagnostic needed for downstream preregistration, promotion, and validation without private imports.
- [ ] A reduced public-API fixture passes from immutable package sources and records their identities.
- [ ] The downstream MEA receipt passes against released or immutable pinned packages before manuscript results are considered final.

## Upstream dependency context

This request is blocked by the current public equilibrium/admission and regression readmission foundations:

- https://github.com/ePC-SAFT/ePC-SAFT/issues/330
- https://github.com/ePC-SAFT/ePC-SAFT/issues/451

These links document prerequisites; they do not imply that either issue already schedules or delivers the reactive regression capability requested here.
