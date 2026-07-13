# Coupled Regression and Parameter Promotion Design

## Context

The current MEAH+ and MEACOO- values are provisional fixed inputs from a historical calculation. A full model paper requires a reproducible current multi-observable regression and an explicit promotion decision.

## Goals

- Preregister target sets, parameter window, bounds, scaling, regularization, split, metrics, budgets, and stopping rules.
- Execute the package-native coupled pressure/speciation fit from a clean pinned environment.
- Promote one immutable parameter artifact only when convergence, improvement, row coverage, bounds, plausibility, and artifact checks pass.

## Non-goals

- Do not tune acceptance criteria after seeing results.
- Do not promote trace-only or pressure-only fits.
- Do not overwrite curated artifacts from smoke or failed runs.

## Alternatives

- Retain provisional parameters: incompatible with the selected full-model endpoint.
- Fit only pressure: underidentifies reactive speciation.
- Selected: preregistered joint pressure/speciation fit with immutable promotion gate.

## Selected design

One signed-off problem definition drives a package-native run. Candidate outputs remain run-local. The promotion checker compares initial/final objectives, row success, source metrics, speciation metrics, bounds, parameter movement, and provenance before copying approved values into the curated parameter artifact.

## Interfaces

- Inputs: validated native contract, canonical targets, parameter evidence, preregistration JSON.
- Outputs: immutable run bundle, candidate parameter set, promotion decision, curated artifact only on pass.
- Parent: Phase 3 workstream; blocked by native-result contract; blocks independent validation.

## Data flow

Freeze preregistration → hash inputs → execute fit → validate package result → compute approval evidence → promote or reject → record hashes.

## Error handling

Reject nonconvergence, zero evaluation, objective non-improvement, missing rows, disallowed active bounds, implausible parameters, mutable dependencies, or hash changes.

## Testing and proof

- Synthetic pass/fail promotion fixtures.
- Reduced smoke cannot touch curated artifacts.
- Full run receipt includes exact status, evaluations, runtime, hashes, metrics, and parameter deltas.
- Approval check must pass before successor work starts.

## Risks

- The fit may be expensive or nonidentifiable; that is a scientific result and blocks promotion.
- Regularization can dominate sparse targets; report objective components separately.

## Unresolved decisions

Exact compute budget is set during plan execution from measured reduced-run throughput without weakening the preregistered scientific gates.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Fit scope | User-selected full-model paper | Joint pressure and speciation regression. | Makes MEA-ion parameters reproducible and claimable. | No | regression owner |
| Promotion | Scientific audit | Promote only a converged, improved, plausible, fully evidenced candidate. | Keeps failed runs out of publication artifacts. | No | parameter-provenance maintainer |
| Compute budget | Runtime evidence | Size the budget from reduced-run throughput while retaining all gates. | Makes execution practical without redefining success. | Yes | regression owner |

