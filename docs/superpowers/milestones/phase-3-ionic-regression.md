# Phase 3 Ionic Regression

## Purpose

Complete the ionic ePC-SAFT evidence chain: parameter evidence, package-native regression integration, train/validation checks, sensitivity diagnostics, promotion gates, and manuscript-ready result boundaries.

## GitHub Milestone

`Phase 3 Ionic Regression`

## Related Specs

Future specs live in `docs/superpowers/specs` and should link back to this page when they define native regression target rows, fitted parameter windows, approval gates, or final promotion criteria.

## Related Plans

Future plans live in `docs/superpowers/plans` and should link back to this page when they sequence ionic-regression implementation, cross-repo ePC-SAFT coordination, or artifact promotion.

## Related Issues

- [#3 Rescope MEA-Thermodynamics to use ePC-SAFT native C++ regression only](https://github.com/tannerpolley/MEA-Thermodynamics/issues/3)
- [#6 Phase 3: Coupled pressure/speciation regression and publishable manuscript artifact gate](https://github.com/tannerpolley/MEA-Thermodynamics/issues/6)

## Success Criteria

- `analyses/phase3/ionic_epcsaft_regression` remains the canonical Phase 3 analysis root.
- Ionic parameter evidence, train/validation split outputs, sensitivity results, and residual figures are generated through repeatable scripts.
- Production fitting delegates optimization to upstream `ePC-SAFT`; this repo records target rows, package results, validation metrics, and manuscript evidence.
- Promotion gates block manuscript status upgrades until package-reported convergence and artifact completeness checks pass.
