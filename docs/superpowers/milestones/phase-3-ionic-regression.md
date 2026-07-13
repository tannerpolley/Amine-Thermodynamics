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

## Related Plans

- `docs/superpowers/plans/2026-07-13-phase3-regression-validation-workstream-plan.md`
- `docs/superpowers/plans/2026-07-13-native-regression-result-contract-plan.md`
- `docs/superpowers/plans/2026-07-13-coupled-regression-parameter-promotion-plan.md`
- `docs/superpowers/plans/2026-07-13-independent-validation-identifiability-plan.md`

## Related Issues

- [#6 Native regression and independent validation workstream](https://github.com/tannerpolley/MEA-Thermodynamics/issues/6)
- [#12 Finalize the native regression result and status contract](https://github.com/tannerpolley/MEA-Thermodynamics/issues/12)
- [#13 Execute coupled regression and promote eligible parameters](https://github.com/tannerpolley/MEA-Thermodynamics/issues/13)
- [#14 Prove independent validation and parameter identifiability](https://github.com/tannerpolley/MEA-Thermodynamics/issues/14)

Historical issue #3 is superseded by #6 and #12; its discussion remains in GitHub history.

## Success Criteria

- `analyses/phase3/ionic_epcsaft_regression` remains the canonical Phase 3 analysis root.
- Ionic parameter evidence, train/validation split outputs, sensitivity results, and residual figures are generated through repeatable scripts.
- Production fitting delegates optimization to upstream `ePC-SAFT`; this repo records target rows, package results, validation metrics, and manuscript evidence.
- Promotion gates block manuscript status upgrades until package-reported convergence and artifact completeness checks pass.
- Reserved-evidence validation and practical-identifiability checks pass before predictive manuscript claims are promoted.
