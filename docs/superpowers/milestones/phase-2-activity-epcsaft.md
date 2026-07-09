# Phase 2 Activity ePC-SAFT

## Purpose

Maintain the true-species activity-based ePC-SAFT workflow that evaluates MEA speciation and pressure behavior before the full ionic regression stage.

## GitHub Milestone

`Phase 2 Activity ePC-SAFT`

## Related Specs

Future specs live in `docs/superpowers/specs` and should link back to this page when they change the Phase 2 true-species basis, reaction constants, source accounting, or solver contract.

## Related Plans

Future plans live in `docs/superpowers/plans` and should link back to this page when they sequence Phase 2 data generation, residual accounting, or plotting work.

## Related Issues

- [#5 Phase 2: Build true-species activity-based ePC-SAFT speciation and VLE workflow](https://github.com/tannerpolley/MEA-Thermodynamics/issues/5)

## Success Criteria

- `analyses/phase2/activity_epcsaft` remains the canonical Phase 2 analysis root.
- The generated problem definition records the true-species basis and reaction rows used by the activity workflow.
- Pressure, speciation, and source-resolved residual tables stay separated so manuscript claims can distinguish measured targets from balance-inferred quantities.
- Phase 2 plots and data snapshots pass the repo validation command.
