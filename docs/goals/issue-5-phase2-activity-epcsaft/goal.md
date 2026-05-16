# Goal: Implement MEA-Thermodynamics Issue #5 Phase 2 Activity ePC-SAFT

## GitHub Issue

- https://github.com/tannerpolley/MEA-Thermodynamics/issues/5

## Objective

Implement issue #5 in MEA-Thermodynamics as a reproducible Phase 2 true-species activity-based ePC-SAFT workflow for MEA-CO2-H2O. The workflow must document the species basis, reaction-constant convention, package dependencies, parameter artifact, missing-data mitigations, and validation outputs before solver-heavy or final-regression work is claimed.

## Original Request

Begin planning for Phase 2 implementation using GoalBuddy, go to GitHub, and begin implementing all steps explicitly on issue #5.

## Intake Summary

- Input shape: `specific`
- Audience: user, MEA-Thermodynamics maintainers, manuscript workflow agents
- Authority: `requested`
- Proof type: `artifact`
- Completion proof: issue #5 acceptance criteria are mapped to repo artifacts, the Phase 2 workflow can generate documented data/figure outputs or records exact package/data blockers, and validation passes without Phase 3 regression claims.
- Likely misfire: implementing a solver-looking local workaround or undocumented constants path instead of a convention-safe, package-boundary-safe Phase 2 workflow tied to one parameter artifact.
- Blind spots considered: package API support may be incomplete; reaction constants may not be safely convertible; pH and ionic activity data may be validation-only or missing; MEA `f_solv` cannot be promoted from pressure data alone; Phase 2 must not drift into global Phase 3 fitting.
- Existing plan facts: preserve the issue #5 implementation tasks and acceptance criteria; use the true species basis CO2, MEA, H2O, MEAH+, MEACOO-, HCO3-, CO3^2-, H3O+, OH- with volatile vapor species CO2, H2O, MEA; record every reaction constant basis; document unsupported package dependencies instead of hiding them downstream.

## Goal Kind

`specific`

## Current Tranche

Create the Phase 2 board and implement the first explicit, reviewable work package: design document, dependency matrix update, reaction-constant basis artifact, parameter artifact scaffold, and analysis scaffold. Continue afterward into data generation and figures only when the convention and package contracts are explicit.

## Non-Negotiable Constraints

- Do not fabricate data.
- Do not silently convert apparent reaction constants into thermodynamic activity constants.
- Do not fit all parameters or claim final global regression.
- Do not create MEA-specific public APIs in `epcsaft`.
- Keep direct `epcsaft` interactions behind approved runtime or diagnostic modules.
- Use one Phase 2 parameter artifact for pressure, speciation, residual, and comparison outputs.
- Document package dependencies and blockers loudly instead of adding fragile downstream workarounds.
- Keep Phase 3 regression claims out of Phase 2 artifacts and manuscript language.

## Canonical Board

Machine truth lives at:

`docs/goals/issue-5-phase2-activity-epcsaft/state.yaml`

If this charter and `state.yaml` disagree, `state.yaml` wins for task status, active task, receipts, verification freshness, and completion truth.

## Run Command

```text
/goal Follow docs/goals/issue-5-phase2-activity-epcsaft/goal.md.
```

## PM Loop

On every `/goal` continuation:

1. Read this charter.
2. Read `state.yaml`.
3. Re-check GitHub issue #5 if the requested scope or comments may have changed.
4. Work only on the active board task.
5. Write a compact task receipt and update the board.
6. Advance to the next largest safe Worker package unless a phase, risk, rejected-verification, ambiguity, or final-completion audit is due.
7. Finish only with a Judge/PM audit receipt that maps receipts and validation back to issue #5 and records `full_outcome_complete: true`.
