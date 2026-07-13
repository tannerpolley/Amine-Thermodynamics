# Split-Package Reactive Regression Contract Design

## Context

MEA currently passes final integration against the monolithic `epcsaft` 1.5.2 package pinned at commit `9f51afd`. That package exposes a reactive fitting entrypoint, but its capability report identifies a Python-orchestrated bounded Gauss-Newton path rather than a native hot loop. Upstream development is separating provider, equilibrium, and regression packages; its present public regression surface does not yet admit the coupled reactive pressure/speciation problem required by this manuscript. The shared upstream checkout is also mutable and must not become evidence.

## Goals

- Preserve the reproducible 1.5.2 stable lane while mapping every consumed capability to the split-package architecture.
- Obtain an upstream, public, capability-reported contract for generic coupled reactive pressure/speciation regression.
- Require native Ceres orchestration, supported CppAD or implicit derivatives, explicit status/failure semantics, and complete diagnostics.
- Cut MEA over through one fail-closed adapter only after a reduced public smoke and immutable final-source proof pass.

## Non-goals

- Do not execute the full scientific fit in this issue.
- Do not make MEA-specific data or species part of the generic upstream API.
- Do not use private imports, a dirty shared checkout, a downstream optimizer, or a permanent dual-architecture shim.

## Alternatives

- Treat legacy 1.5.2 fields as the final contract: rejected because it locks the manuscript to an architecture and optimizer path upstream is replacing.
- Build reactive regression downstream: rejected because numerical ownership belongs upstream.
- Follow unreleased private modules: rejected because the result would not be reproducible or supportable.
- Selected: stable-lane preservation plus explicit upstream admission and a single public split-package cutover.

## Selected design

First create a compatibility matrix covering provider inputs, equilibrium targets, regression problem construction, derivatives, status, diagnostics, provenance, and package identity. File a minimal generic upstream admission request backed by a reduced MEA-shaped fixture. Development validation runs only from one explicit ePC-SAFT worktree. Once upstream admits the capability, implement a versioned MEA adapter that validates the public request and structured result, rejects unknown or partial states, and writes run-local artifacts. Cut over only when the reduced smoke and final immutable-source integration receipt pass; then remove legacy root-package access rather than retaining compatibility branches.

## Required upstream contract

- Coupled reactive pressure and speciation residual blocks with explicit weights, bounds, scaling, and parameter families.
- Native Ceres hot loop with supported CppAD or implicit Jacobians and no Python callback in the optimization loop.
- Explicit initial/final objective, convergence and termination status, evaluation counts, parameter movement, active bounds, residual-block norms, row diagnostics, and source/target-family summaries.
- Public capability-report admission, public API tests, and release or immutable Git reference suitable for downstream final-mode proof.

## Interfaces

- Inputs: compatibility matrix, reduced source-bearing reactive fixture, parameter definitions, execution options, and immutable package identities.
- Output: validated result/status adapter, run-local diagnostics, upstream receipt, and migration receipt.
- Parent: Phase 3 workstream (#6); successor: coupled regression execution (#13).

## Data flow

Inventory legacy consumption → map split-package owners → publish upstream admission request → validate admitted public capability in a dev worktree → implement fail-closed adapter → run reduced smoke → pin immutable source → cut over and remove legacy path.

## Error handling

Fail on absent capability admission, private API use, mutable or shared source state, missing result fields, unknown status, nonfinite values, inconsistent parameter names, incomplete row diagnostics, or any attempted curated overwrite.

## Testing and proof

- Compatibility-matrix completeness and no-private-import tests.
- Contract fixtures for converged, nonconverged, malformed, nonfinite, and partial-row outcomes.
- Reduced real-package public smoke with exact package/ref metadata and zero curated diff.
- Final integration check from a released or immutable pinned split-package source.

## Risks

Upstream admission may arrive in stages or change field names. The issue remains blocked until the public capability and schema are real; MEA must not guess them.

## Unresolved decisions

Exact split-package callable names, result fields, capability keys, and first admissible immutable versions remain upstream-owned decisions. They are locked only after public admission and tests exist.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Stable baseline | Current final integration receipt | Preserve pinned monolithic 1.5.2 until cutover proof passes. | Keeps current work reproducible while upstream evolves. | No | cross-repo integration maintainer |
| Future architecture | Upstream package roadmap and source audit | Adopt provider/equilibrium/regression public packages. | Prevents cementing a retired root API. | No | cross-repo integration maintainer |
| Optimizer owner | Repository architecture | ePC-SAFT owns optimization; MEA owns targets and evidence. | Avoids duplicated numerical ownership. | No | upstream regression maintainer |
| Exact public schema | Upstream admission | Defer field names until capability and API tests exist. | Prevents a fictional downstream contract. | Yes | upstream regression maintainer |
| Cutover | Cross-repo integration policy | One fail-closed adapter, then delete the legacy path. | Avoids permanent compatibility complexity. | No | MEA adapter maintainer |
