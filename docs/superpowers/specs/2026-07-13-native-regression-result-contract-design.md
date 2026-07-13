# Native Regression Result Contract Design

## Context

The MEA repository now builds native regression problems and guards production paths against local SciPy optimization, but the remaining #3 scope is the exact package-result/status contract and its downstream consumption.

## Goals

- Pin the ePC-SAFT callable, request schema, result schema, status vocabulary, derivative/runtime metadata, and error mapping.
- Ensure MEA consumes package truth for convergence, active bounds, residuals, parameters, and diagnostics.
- Produce a reduced native smoke receipt without mutating curated artifacts.

## Non-goals

- Do not execute the final scientific fit.
- Do not define independent validation metrics.
- Do not add compatibility fallbacks to old local optimizers.

## Alternatives

- Infer fields opportunistically from package objects: fragile and unauditable.
- Copy upstream optimizer logic downstream: violates ownership.
- Selected: one versioned adapter contract with schema validation and fail-closed status mapping.

## Selected design

The adapter serializes the complete problem, invokes the pinned public package API once, validates a structured result, and writes run-local artifacts. Only explicit converged/success states can proceed to promotion; unknown or partial statuses remain failures.

## Interfaces

- Input: native problem JSON, parameter specs, pinned ePC-SAFT version/commit, execution budget.
- Output: result JSON, residual/row diagnostics, parameter map, active bounds, runtime metadata, adapter receipt.
- Parent: Phase 3 workstream (#6); successor: coupled regression execution.

## Data flow

Build problem → validate schema → call package → validate result → map status → write run-local artifacts → run approval precheck.

## Error handling

Fail on missing fields, unknown status, mutable package state, nonfinite values, inconsistent parameter names, partial row diagnostics, or any attempted curated overwrite.

## Testing and proof

- Contract tests with accepted and adversarial package-result fixtures.
- Test proving no production SciPy optimizer imports.
- Reduced real-package smoke with immutable metadata.
- Final integration checker recognizes the pinned package state.

## Risks

Upstream schema changes can break the adapter; fail closed and require an explicit contract update.

## Unresolved decisions

No unresolved design decision remains; exact upstream field names are discovered from the pinned public API and locked in tests.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Optimizer owner | Existing #3 intent + repository architecture | ePC-SAFT owns optimization; MEA owns targets and evidence. | Eliminates duplicated numerical ownership. | No | cross-repo integration maintainer |
| Status policy | Manuscript audit | Unknown and nonconverged statuses fail closed. | Prevents false promotion. | No | approval-check maintainer |

