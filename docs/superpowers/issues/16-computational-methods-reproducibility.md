# Document computational methods and reproducibility

GitHub source: https://github.com/tannerpolley/MEA-Thermodynamics/issues/16

## Parent

- #15

## What to build

Document the algorithms, initialization, continuation, numerical limits,
tolerances, failure semantics, immutable package identity, and claim boundary
actually used by the fixed-parameter evaluation.

## Acceptance criteria

- [x] Record the executed ideal and activity-based solver contracts.
- [x] Identify immutable `epcsaft` 1.5.2 commit `9f51afd`.
- [x] Mark the coupled pressure/speciation objective as prospective.
- [ ] Pass final integration and deterministic manuscript build on the closing
  pull-request head.

## Blocked by

None. Future parameter-regression methods remain owned by #6 and #12-14.
