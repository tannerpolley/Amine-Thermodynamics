# Phase 3 Upstream Authority Rebaseline Design

## Context

MEA Phase 3 currently treats `ePC-SAFT/ePC-SAFT#468` as the upstream execution blocker for Issues #12 and #13. The repository behind that tracker was subsequently renamed and transferred to `tannerpolley/ePC-SAFT-lab`. The lab preserves historical implementation and tracker evidence, but current ecosystem doctrine explicitly denies it production release, roadmap, and issue-intake authority.

The clean `ePC-SAFT/ePC-SAFT-regression` repository is the permanent owner for target contracts, native Ceres fitting, fit diagnostics, and regression results. It is presently a governance-only skeleton. The migration control plane reports that provider promotion has not started, so no stage-approved regression transfer plan or clean reactive-regression capability exists.

MEA's pinned `epcsaft` 1.5.2 source at commit `9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785` remains immutable historical runtime evidence for the current fixed-parameter evaluation. That pin does not make the lab a clean production owner and does not admit real regression execution.

## Goals

- Make every active MEA Phase 3 dependency point to the current ePC-SAFT authority model.
- Preserve the pinned 1.5.2 fixed-evaluation lane and its passing final integration proof.
- Reclassify lab issue #468 as historical design evidence rather than an actionable production dependency.
- Define the future reactive-regression dependency as a stage-approved vertical slice owned by clean `ePC-SAFT-regression`.
- Keep the downstream regression execution gate closed until an immutable clean-package capability receipt satisfies every existing predicate.
- Repair stale tracker state caused by completed Issue #11.

## Non-goals

- Do not execute a reduced or full coupled regression.
- Do not change parameter values, target membership, grouped split membership, readiness hashes, analysis outputs, figures, or manuscript scientific claims.
- Do not create clean upstream source, package metadata, tests, issues, or capability claims before the migration control plane authorizes the stage-owned transfer.
- Do not rewrite the pinned dependency URL or package version in this rebaseline; the immutable commit remains the current historical evaluation lane.
- Do not convert the lab into a production dependency or active tracker.

## Alternatives

- **Update only the old issue URL:** rejected because a correct link to the lab would still misrepresent historical tracker evidence as present production authority.
- **Proceed against lab issue #468:** rejected because the lab no longer owns issue intake, roadmap state, production packages, or capability admission.
- **Remove all upstream references and continue locally:** rejected because optimizer ownership, derivative guarantees, and result contracts belong upstream; a downstream optimizer would violate the established architecture.
- **Selected — authority rebaseline:** preserve the historical lane, identify the clean permanent owner and migration gate, keep execution fail-closed, and make the MEA tracker describe that dependency accurately.

## Selected Design

One atomic MEA change updates the cross-repository coordination note, Phase 3 issue mirrors, milestone roadmap, dependency documentation, and active GitHub issue bodies. Historical issue #468 remains linked as provenance at `tannerpolley/ePC-SAFT-lab#468`, but active blocker text names the clean `ePC-SAFT-regression` vertical slice and its prerequisite stage-approved migration plan.

The readiness receipt remains the executable downstream authority. `upstream_execution_admitted` stays `false`, and `require_regression_execution_admitted()` continues rejecting every attempted fit. No clean upstream issue is created as part of this task because the clean repository contract forbids executable work before an approved transfer plan.

The same tracker pass closes the completed Phase 2 workstream if its only child, Issue #11, is closed and its acceptance evidence remains present. Issue #18 stops naming completed Issue #11 as a blocker but remains blocked by Issue #14. These mutations are read back from GitHub after writing.

## Ownership and Interfaces

- **MEA-Thermodynamics:** owns canonical observations, target construction, frozen splits, downstream admission checks, validation gates, artifacts, and manuscript claim boundaries.
- **ePC-SAFT migration control plane:** owns the temporary sequence and authorization for clean runtime-slice promotion.
- **Clean `ePC-SAFT`:** will own admitted provider inputs, EOS/state/property behavior, CppAD substrate, and provider SDK after promotion.
- **Clean `ePC-SAFT-regression`:** will own the future target contract, native Ceres residual/Jacobian loop, fit result/status schema, diagnostics, and capability report after an accepted promotion receipt.
- **ePC-SAFT lab:** remains historical provenance and transitional runtime authority for unpromoted slices; it is not an active production or tracker owner.

## Future Upstream Admission Boundary

The downstream gate may become eligible only after immutable clean-package evidence proves:

- coupled reactive pressure and speciation target support;
- a production native Ceres hot loop;
- exact CppAD-backed residual Jacobians for every admitted target family;
- explicit weights, bounds, scales, and parameter-family identities;
- structured termination, evaluation, parameter movement, active-bound, residual-block, row, source, and target-family diagnostics;
- explicit rejection of unsupported, malformed, nonfinite, and partial-row outcomes; and
- a reduced public fixture plus installed-artifact receipt from immutable package sources.

MEA then validates the admitted public API through its existing fail-closed adapter, reduced smoke, and final integration checker before any full fit or parameter promotion.

## Error Handling

- Treat a historical lab issue, source path, or capability payload as provenance only; never infer current clean-package admission from it.
- Stop if active documentation names contradictory production owners.
- Stop if a proposed edit changes the pinned package identity, readiness source hashes, split hash, target roles, or execution boolean.
- Stop if GitHub write-back leaves a stale closed blocker or changes a scientific issue's dependency ordering.
- Stop if final integration no longer proves the immutable 1.5.2 evaluation lane.

## Testing and Proof

- Focused text assertions prove active coordination and issue documents distinguish historical lab evidence from clean production ownership.
- Readiness regeneration or comparison proves `upstream_execution_admitted=false`, split hash `e7bc893dab825007d009260d2c1f6f5dd42e75ebddbdb4972d52a5ec4f0c1aa0`, and existing source hashes remain unchanged.
- `uv run pytest tests/test_epcsaft_ionic_native_regression.py tests/test_regression_readiness.py -q` proves the downstream execution gate and readiness contract.
- `uv run python scripts/check_epcsaft_integration.py --mode final` proves the pinned historical evaluation lane remains reproducible.
- Structured GitHub read-back proves Issues #12-#14 name the current authority boundary, Issue #5 no longer remains open behind completed #11, and Issue #18 depends only on open Issue #14.

## Acceptance Criteria

- No active MEA project document treats lab issue #468 as an actionable production dependency.
- Active Phase 3 documents name clean `ePC-SAFT-regression` as the future regression owner and the migration transfer plan as the next upstream authority gate.
- The immutable `epcsaft` 1.5.2 pin remains unchanged and passes final integration.
- The readiness decision remains `preregistration_ready_upstream_execution_blocked`; the execution boolean, split hash, target roles, and source hashes are unchanged.
- No clean upstream issue or capability claim is created without stage authorization.
- Live GitHub issue state and local roadmap documents agree about completed Issue #11 and the remaining Phase 3 dependency chain.

## Risks

The clean ecosystem may choose different public names or package sequencing when transfer work begins. MEA therefore records ownership, evidence requirements, and failure boundaries now while deferring exact clean API field names until an accepted upstream spec and receipt exist.

## Decision Ledger

| Decision | Source | Answer | Impact | Deferred? | Risk owner |
| --- | --- | --- | --- | --- | --- |
| Current manuscript runtime | MEA immutable integration receipt | Preserve `epcsaft` 1.5.2 at `9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785`. | Keeps current fixed-evaluation evidence reproducible. | No | MEA integration maintainer |
| Historical tracker | Lab authority purge and ecosystem doctrine | Treat `tannerpolley/ePC-SAFT-lab#468` as historical provenance only. | Prevents work from being routed to a retired tracker owner. | No | Cross-repo maintainer |
| Future regression owner | Ecosystem doctrine revision 2 | Clean `ePC-SAFT/ePC-SAFT-regression`. | Preserves one production owner for Ceres regression. | No | Upstream regression owner |
| First upstream action | Migration control-plane status | Require a stage-approved transfer plan before clean implementation or issue intake. | Avoids creating unauthorized clean-package work. | No | Migration owner |
| Downstream admission | Existing readiness builder and gate | Keep execution blocked until immutable clean capability evidence satisfies every predicate. | Prevents scaffolding or historical capability from enabling fitting. | No | MEA integration maintainer |
| Exact clean API schema | Future stage-owned upstream design | Defer public names and fields until accepted upstream evidence exists. | Avoids fictional downstream contracts. | Yes | Upstream regression owner |
