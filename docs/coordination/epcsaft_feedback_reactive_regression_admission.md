# Upstream request: admit generic native coupled reactive regression

## Downstream repository

- Repository: `tannerpolley/MEA-Thermodynamics`
- Current immutable evaluation source: monolithic `epcsaft` 1.5.2 at Git commit `9f51afd`
- Historical request: https://github.com/tannerpolley/ePC-SAFT-lab/issues/468
- Future production owner: `ePC-SAFT/ePC-SAFT-regression`
- Current authority gate: a stage-approved runtime-slice plan in the ePC-SAFT migration control plane

## Authority status

The repository and tracker that originally owned issue #468 were renamed and transferred to `tannerpolley/ePC-SAFT-lab`. The lab retains that issue as historical design evidence, but it does not own current issue intake, roadmap state, production distributions, or clean capability admission.

Clean `ePC-SAFT/ePC-SAFT-regression` is the permanent regression owner and is currently a governance-only skeleton. Migration Phase 5 provider promotion has not started, so a new clean regression issue or implementation is premature until the migration control plane approves the owning slice. MEA must keep execution fail-closed in the meantime.

## Command

Current downstream final-lane proof:

```bash
uv run python scripts/check_epcsaft_integration.py --mode final
```

The future reduced clean-package reproduction must use only installed public provider, regression, and capability-report APIs from immutable refs. Its exact command belongs in a stage-approved upstream spec once those public entrypoints are admitted.

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
- Clean `ePC-SAFT-regression` is a governance-only skeleton and does not expose a public production capability for coupled reactive pressure/speciation regression.
- Current equilibrium public scope is insufficient to infer this regression surface, and private implementation modules are not a downstream contract.

## Expected behavior

After stage approval and provider promotion, the public clean regression package should admit a generic coupled reactive problem and report:

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
uv run pytest tests/test_reactive_speciation_numerics.py tests/test_phase2_numerics.py -q
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

Historical lab issue #468 referenced earlier lab dependencies:

- https://github.com/tannerpolley/ePC-SAFT-lab/issues/330
- https://github.com/tannerpolley/ePC-SAFT-lab/issues/451

These links preserve provenance only. They do not schedule clean production work. The actionable upstream gate is a stage-approved transfer plan owned by the migration control plane, followed by an accepted clean-package promotion receipt.
