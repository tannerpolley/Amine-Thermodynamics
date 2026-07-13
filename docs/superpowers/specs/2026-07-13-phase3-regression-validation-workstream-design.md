# Phase 3 Regression and Validation Workstream Design

## Context

GitHub issues #3 and #6 overlapped heavily. Most downstream native-regression scaffolding exists, but no completed promoted coupled fit exists: the current global summary reports `success=false` and `nfev=0`. MEA currently pins monolithic `epcsaft` 1.5.2 while upstream is moving to provider/equilibrium/regression packages whose public regression surface does not yet admit the required coupled reactive pressure/speciation problem.

## Goals

- Retain #6 as the Phase 3 workstream parent.
- Replace the overlap with three ordered children: split-package adoption contract, coupled fit/promotion, and independent validation/identifiability.
- Close #3 as superseded only after its remaining contract work is represented by a validated child.
- Require public upstream capability admission and immutable split-package proof before Phase 3 closeout.

## Non-goals

- Do not run downstream SciPy optimization.
- Do not promote trace-only carbonate scans as the final parameter set.
- Do not allow manuscript fit claims before all three children pass.

## Alternatives

- Keep #3 and #6 as peers: rejected because ownership and completion criteria overlap.
- Merge all Phase 3 work into one child: rejected because API integration, fitting, and validation have different proof.
- Selected: #6 parent with three dependency-ordered children.

## Selected design

Child 1 preserves the stable lane while obtaining upstream admission and adopting the public split-package request/result contract. Child 2 preregisters and executes the multi-observable fit, then promotes only an approved result. Child 3 freezes validation infrastructure before fitting and evaluates the immutable candidate afterward. #6 closes only after all three receipts and the final immutable-source integration proof are valid.

## Interfaces

- Inputs: ePC-SAFT pinned API, native problem artifacts, pressure/speciation targets, parameter evidence, approval checks.
- Outputs: updated #6 mirror/body, three child relationships, dependency graph, and Phase 3 closeout receipt.
- Downstream consumers: comparison work, computational methods, figures, and final readiness gate.

## Data flow

1. Obtain upstream admission and verify the public split-package contract and structured result schema.
2. Execute the preregistered fit and create a candidate promotion receipt.
3. Run independent validation and identifiability gates on the immutable candidate.
4. Promote or reject; propagate only approved artifacts downstream.

## Error handling

Stop on absent upstream admission, private API use, package mismatch, nonconverged status, mutable dependency state, active-bound violations, missing validation split, or artifact hash drift.

## Testing and proof

- Child-specific focused tests and validators.
- Upstream capability report and public API receipt.
- Final integration check in `final` mode from released or immutable package sources.
- Immutable problem/result/parameter hashes and clean promotion receipt.
- GitHub hierarchy and dependencies match the local mirrors.

## Risks

- Upstream admission timing may delay execution; stable-lane maintenance and downstream preregistration can continue without inventing the missing contract.
- Runtime cost may be high; preregistration must define budgets without weakening convergence proof.
- Identifiability may fail even when optimization converges; the validation child owns that distinction.

## Unresolved decisions

No paper-scope decision remains. Failure to meet Phase 3 gates blocks the selected full-model paper rather than silently reframing it.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Phase 3 parent | User-approved distributed hierarchy | Keep #6 and replace #3 overlap with three children. | Separates architecture, fitting, and validation ownership. | No | Phase 3 maintainer |
| Paper endpoint | Native user selection | Require a full model-development result. | Phase 3 is a submission blocker. | No | corresponding author |
| Promotion order | Scientific audit | Contract, then fit, then independent validation. | Prevents unvalidated parameters from entering the manuscript. | No | regression maintainer |
