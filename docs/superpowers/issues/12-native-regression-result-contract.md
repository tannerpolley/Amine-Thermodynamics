# Adopt the split-package ePC-SAFT reactive-regression contract

**GitHub Issue:** https://github.com/tannerpolley/MEA-Thermodynamics/issues/12
**GitHub Milestone:** Phase 3 Ionic Regression
Parent Issue: https://github.com/tannerpolley/MEA-Thermodynamics/issues/6
**Source Spec:** docs/superpowers/specs/2026-07-13-native-regression-result-contract-design.md
**Source Plan:** docs/superpowers/plans/2026-07-13-native-regression-result-contract-plan.md
**Labels:** superpowers:issue, kind:deliverable, area:regression, priority:submission-blocker, status:blocked, type:analysis
Sub-Issue Role: leaf
Executable: true
**Goal Command:** /goal Adopt and prove the public split-package ePC-SAFT reactive-regression contract without weakening the stable integration lane.

## Outcome Summary

**Outcome Source:** docs/superpowers/plans/2026-07-13-native-regression-result-contract-plan.md#outcome-proof
**Intent:** Move MEA from the legacy monolithic regression surface to an admitted, public, fail-closed split-package contract.
**Target Output:** Compatibility matrix, stage-approved clean upstream admission receipt, versioned adapter/schema, adversarial tests, reduced public smoke, and final pinned integration receipt.
**Owner:** Cross-repo integration maintainer.
**Interface:** Installed public clean provider/regression package APIs through one approved MEA adapter.
**Cutover:** Preserve the pinned `epcsaft` 1.5.2 final lane until the admitted split-package contract passes the reduced smoke and final-mode checks.
**Replaced Path:** Retire root-package regression calls, private imports, opportunistic field access, and implicit status coercion at cutover.
**Acceptance Proof:** Capability report admits the required reactive target families and native hot loop; known result fixtures map correctly; malformed results fail; the public reduced smoke writes no curated files.
**Stop Criteria:** Stop on missing upstream admission, shared mutable checkout use, private API dependence, unknown result semantics, or incomplete row diagnostics.
**Avoid:** No downstream optimizer, compatibility shim, silent default, or success inference from finite values.

## Acceptance Criteria

- [ ] Record the legacy-to-split-package compatibility matrix and preserve a passing pinned stable lane during migration.
- [ ] Obtain upstream public admission for generic coupled reactive pressure/speciation regression with a native Ceres hot loop and supported derivatives.
- [ ] Validate the admitted request/result/status schema, including termination, evaluations, parameter movement, active bounds, row diagnostics, and source/target summaries.
- [ ] Run a reduced public-API smoke in an explicit development worktree, then pass final validation from a released or immutable pinned source.

## Blocked by

- A stage-approved runtime-slice plan in the ePC-SAFT migration control plane.
- Clean `ePC-SAFT/ePC-SAFT-regression` is currently a governance-only skeleton with no admitted production capability.

## Historical evidence

- https://github.com/tannerpolley/ePC-SAFT-lab/issues/468 records the original request but is not an actionable production dependency.

## Non-goals

- Execute the full coupled MEA fit.
- Import private upstream modules or preserve both package architectures behind a permanent compatibility layer.
- Consume the ePC-SAFT lab or another mutable checkout as manuscript evidence.

## Proof Oracle

- Upstream capability report, public API tests, and immutable source receipt.
- Focused adversarial adapter tests and reduced public regression receipt.
- `uv run python scripts/check_epcsaft_integration.py --mode final`
