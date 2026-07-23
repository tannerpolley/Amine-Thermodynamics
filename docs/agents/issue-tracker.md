# Issue Tracker

GitHub Issues in `tannerpolley/MEA-Thermodynamics` are authoritative for
current work. Read existing issues, dependencies, pull requests, and repository
evidence before publishing or changing tracker state.

## Project Truss contracts

A governed root specification uses:

1. Problem Statement
2. Solution
3. User Stories
4. Implementation Decisions
5. Testing Decisions
6. Out of Scope
7. Further Notes

An executable leaf uses:

1. Parent
2. What to build
3. Acceptance criteria
4. Blocked by

Use native GitHub parent/sub-issue and blocked-by relationships when
available. One mergeable implementation unit should be one leaf. GitHub
becomes authoritative immediately after publication; do not create a second
local lifecycle ledger.

Preserve existing labels. Do not infer lifecycle state from legacy
`status:*` labels: derive readiness from the issue contract, dependencies,
claims, pull requests, CI, and verification evidence.

## Repository ownership

MEA-Thermodynamics owns application chemistry, datasets, target construction,
parameter-evidence records, validation artifacts, and manuscript claims. The
Provider owns EOS evaluation, typed parameter and applicability schemas, and
derivatives. Equilibrium owns reaction/balance constraints, Ipopt execution,
and equilibrium certificates. Regression owns parameter optimization.
