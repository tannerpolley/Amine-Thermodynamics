# Manuscript Submission

## Purpose

Keep the LaTeX manuscript, figure set, source log, and final validation gates aligned so the paper can be submitted with traceable analysis evidence.

## GitHub Milestone

`Manuscript Submission`

## Related Specs

Future specs live in `docs/superpowers/specs` and should link back to this page when they define manuscript claim boundaries, submission checklist changes, or figure/table requirements.

## Related Plans

Future plans live in `docs/superpowers/plans` and should link back to this page when they sequence manuscript revisions, figure replacement, source-log updates, or final validation.

## Related Issues

- [#10 Manuscript Submission: assemble final submission readiness gate](https://github.com/tannerpolley/MEA-Thermodynamics/issues/10)

## Success Criteria

- `docs/latex` uses the curated PDF figure artifacts where the manuscript expects publication-ready figures.
- Manuscript language reflects the actual validated artifact status and package-reported fit status.
- `docs/latex/source_log.md` records source, figure, and parameter-evidence changes that support manuscript claims.
- Final work passes `uv run python scripts/validate_project.py confidence` and the required ePC-SAFT final integration check before submission.
