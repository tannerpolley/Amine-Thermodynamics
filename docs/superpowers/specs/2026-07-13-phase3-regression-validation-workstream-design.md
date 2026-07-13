# Phase 3 Regression and Validation Workstream Design

## Context

GitHub issues #3 and #6 overlap heavily. Most downstream native-regression scaffolding exists, but no completed promoted coupled fit exists: the current global summary reports `success=false` and `nfev=0`. The user selected a full model-development paper, making reproducible fitting and validation mandatory.

## Goals

- Retain #6 as the Phase 3 workstream parent.
- Replace the overlap with three ordered children: native result contract, coupled fit/promotion, and independent validation/identifiability.
- Close #3 as superseded only after its remaining contract work is represented by a validated child.

## Non-goals

- Do not run downstream SciPy optimization.
- Do not promote trace-only carbonate scans as the final parameter set.
- Do not allow manuscript fit claims before all three children pass.

## Alternatives

- Keep #3 and #6 as peers: rejected because ownership and completion criteria overlap.
- Merge all Phase 3 work into one child: rejected because API integration, fitting, and validation have different proof.
- Selected: #6 parent with three dependency-ordered children.

## Selected design

Child 1 finalizes package-result/status semantics and the downstream adapter. Child 2 preregisters and executes the multi-observable fit, then promotes only an approved result. Child 3 evaluates reserved data, identifiability, uncertainty, parameter plausibility, and robustness. #6 closes only after all three receipts are valid.

## Interfaces

- Inputs: ePC-SAFT pinned API, native problem artifacts, pressure/speciation targets, parameter evidence, approval checks.
- Outputs: updated #6 mirror/body, three child relationships, dependency graph, and Phase 3 closeout receipt.
- Downstream consumers: comparison work, computational methods, figures, and final readiness gate.

## Data flow

1. Verify the package contract and structured result schema.
2. Execute the preregistered fit and create a candidate promotion receipt.
3. Run independent validation and identifiability gates on the immutable candidate.
4. Promote or reject; propagate only approved artifacts downstream.

## Error handling

Stop on package mismatch, nonconverged status, mutable dependency state, active-bound violations, missing validation split, or artifact hash drift.

## Testing and proof

- Child-specific focused tests and validators.
- Final integration check in `final` mode.
- Immutable problem/result/parameter hashes and clean promotion receipt.
- GitHub hierarchy and dependencies match the local mirrors.

## Risks

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

