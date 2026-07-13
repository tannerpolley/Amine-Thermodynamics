# Phase 2 Activity ePC-SAFT

## Purpose

Maintain the true-species activity-based ePC-SAFT workflow that evaluates MEA speciation and pressure behavior before the full ionic regression stage.

## GitHub Milestone

`Phase 2 Activity ePC-SAFT`

## Related Specs

- `docs/superpowers/specs/2026-07-13-phase2-model-comparison-workstream-design.md`
- `docs/superpowers/specs/2026-07-13-controlled-model-comparison-metrics-design.md`

## Related Plans

- `docs/superpowers/plans/2026-07-13-phase2-model-comparison-workstream-plan.md`
- `docs/superpowers/plans/2026-07-13-controlled-model-comparison-metrics-plan.md`

## Related Issues

- [#5 Activity-model comparison and metric integrity workstream](https://github.com/tannerpolley/MEA-Thermodynamics/issues/5)
- [#11 Establish controlled Phase 1/2 model comparison and metric integrity](https://github.com/tannerpolley/MEA-Thermodynamics/issues/11)

## Success Criteria

- `analyses/phase2/activity_epcsaft` remains the canonical Phase 2 analysis root.
- The generated problem definition records the true-species basis and reaction rows used by the activity workflow.
- Pressure, speciation, and source-resolved residual tables stay separated so manuscript claims can distinguish measured targets from balance-inferred quantities.
- Phase 2 plots and data snapshots pass the repo validation command.
- Phase 1/2 comparisons use identical experimental records, disclose rejected rows and uncertainty coverage, and are reproduced from saved paired data.
