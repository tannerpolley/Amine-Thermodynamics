# Phase 3 Ionic Regression

## Purpose

Complete the ionic ePC-SAFT evidence chain: parameter evidence, package-native regression integration, train/validation checks, sensitivity diagnostics, promotion gates, and manuscript-ready result boundaries.

## GitHub Milestone

`Phase 3 Ionic Regression`

## Related Specs

- `docs/superpowers/specs/2026-07-13-phase3-regression-validation-workstream-design.md`
- `docs/superpowers/specs/2026-07-13-native-regression-result-contract-design.md`
- `docs/superpowers/specs/2026-07-13-coupled-regression-parameter-promotion-design.md`
- `docs/superpowers/specs/2026-07-13-independent-validation-identifiability-design.md`
- `docs/superpowers/specs/2026-07-14-data-acquisition-regression-readiness-design.md`
- `docs/superpowers/specs/2026-07-16-phase3-upstream-authority-rebaseline-design.md`

## Related Plans

- `docs/superpowers/plans/2026-07-13-phase3-regression-validation-workstream-plan.md`
- `docs/superpowers/plans/2026-07-13-native-regression-result-contract-plan.md`
- `docs/superpowers/plans/2026-07-13-coupled-regression-parameter-promotion-plan.md`
- `docs/superpowers/plans/2026-07-13-independent-validation-identifiability-plan.md`
- `docs/superpowers/plans/2026-07-14-data-acquisition-regression-readiness-plan.md`
- `docs/superpowers/plans/2026-07-16-phase3-upstream-authority-rebaseline-plan.md`

## Related Issues

- [#6 Native regression and independent validation workstream](https://github.com/tannerpolley/MEA-Thermodynamics/issues/6)
- [#12 Finalize the native regression result and status contract](https://github.com/tannerpolley/MEA-Thermodynamics/issues/12)
- [#13 Execute coupled regression and promote eligible parameters](https://github.com/tannerpolley/MEA-Thermodynamics/issues/13)
- [#14 Prove independent validation and parameter identifiability](https://github.com/tannerpolley/MEA-Thermodynamics/issues/14)
- [#22 Rebaseline Phase 3 upstream authority](https://github.com/tannerpolley/MEA-Thermodynamics/issues/22)

Historical issue #3 is superseded by #6 and #12; its discussion remains in GitHub history.

## Frozen Readiness Inputs

- Target admission: `data/reference/MEA/manifests/target_admission_manifest.csv`
- Grouped split: `data/reference/MEA/manifests/grouped_split_manifest.csv`
- Readiness receipt: `analyses/phase3/ionic_epcsaft_regression/results/readiness/regression_readiness_summary.json`
- Split hash: `e7bc893dab825007d009260d2c1f6f5dd42e75ebddbdb4972d52a5ec4f0c1aa0`

The receipt is preregistration-ready but execution-blocked: the pinned public package supports pressure/speciation target construction, while Issue #12 still gates the required production native Ceres hot loop and derivative/result contract.

## Upstream Authority Status

- The current `epcsaft` 1.5.2 pin is immutable historical evaluation evidence.
- `tannerpolley/ePC-SAFT-lab#468` preserves the original request but is not an actionable production dependency.
- Clean `ePC-SAFT/ePC-SAFT-regression` is the future production owner and is currently a governance-only skeleton.
- The next upstream gate is a stage-approved runtime-slice plan in the ePC-SAFT migration control plane; no clean regression issue or capability may be inferred before that approval.

## Success Criteria

- `analyses/phase3/ionic_epcsaft_regression` remains the canonical Phase 3 analysis root.
- Ionic parameter evidence, train/validation split outputs, sensitivity results, and residual figures are generated through repeatable scripts.
- Production fitting delegates optimization to upstream `ePC-SAFT`; this repo records target rows, package results, validation metrics, and manuscript evidence.
- Promotion gates block manuscript status upgrades until package-reported convergence and artifact completeness checks pass.
- Reserved-evidence validation and practical-identifiability checks pass before predictive manuscript claims are promoted.
- Training and validation identities come from the frozen grouped manifest; no runtime source-name selector may redefine them.
