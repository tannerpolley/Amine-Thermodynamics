# Manuscript Submission

## Purpose

Keep the LaTeX manuscript, figure set, source log, and final validation gates aligned so the paper can be submitted with traceable analysis evidence.

## GitHub Milestone

`Manuscript Submission`

## Related Specs

- `docs/superpowers/specs/2026-07-13-manuscript-package-release-workstream-design.md`
- `docs/superpowers/specs/2026-07-13-computational-methods-reproducibility-design.md`
- `docs/superpowers/specs/2026-07-13-submission-metadata-archive-design.md`
- `docs/superpowers/specs/2026-07-13-publication-figures-editorial-design.md`
- `docs/superpowers/specs/2026-07-13-final-submission-readiness-gate-design.md`

## Related Plans

- `docs/superpowers/plans/2026-07-13-manuscript-package-release-workstream-plan.md`
- `docs/superpowers/plans/2026-07-13-computational-methods-reproducibility-plan.md`
- `docs/superpowers/plans/2026-07-13-submission-metadata-archive-plan.md`
- `docs/superpowers/plans/2026-07-13-publication-figures-editorial-plan.md`
- `docs/superpowers/plans/2026-07-13-final-submission-readiness-gate-plan.md`

## Related Issues

- [#15 Manuscript package and release workstream](https://github.com/tannerpolley/MEA-Thermodynamics/issues/15)
- [#16 Document computational methods and reproducibility](https://github.com/tannerpolley/MEA-Thermodynamics/issues/16)
- [#17 Complete submission metadata, licensing, and archival records](https://github.com/tannerpolley/MEA-Thermodynamics/issues/17)
- [#18 Complete publication figures, tables, layout, and editorial polish](https://github.com/tannerpolley/MEA-Thermodynamics/issues/18)
- [#10 Final cross-workstream submission readiness gate](https://github.com/tannerpolley/MEA-Thermodynamics/issues/10)

#10 is an independent blocked-by gate. It does not parent scientific or manuscript-package implementation issues.

## Success Criteria

- `docs/latex` uses the curated PDF figure artifacts where the manuscript expects publication-ready figures.
- Manuscript language reflects the actual validated artifact status and package-reported fit status.
- `docs/latex/source_log.md` records source, figure, and parameter-evidence changes that support manuscript claims.
- Final work passes `uv run python scripts/validate_project.py confidence` and the required ePC-SAFT final integration check before submission.
- Author-controlled metadata, licensing, release, and archival actions remain HITL until explicitly approved.
