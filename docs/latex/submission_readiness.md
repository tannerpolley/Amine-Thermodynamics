# Manuscript submission readiness

Scientific lane: fixed-parameter evaluation, not parameter regression.

## Completed locally

- The manuscript reports the immutable `epcsaft` 1.5.2 evaluation lane at Git
  commit `9f51afd0f9c11a6497ddca05c8b2dd0ea0ffa785`.
- Pressure and speciation claims derive from accepted fixed-parameter solver
  rows; failed or best-effort states cannot enter metrics or plots.
- The methods section records initialization, continuation, iteration limits,
  tolerances, damping, pressure bounds, and acceptance semantics for the
  executed ideal and activity-based calculations.
- The coupled objective is explicitly prospective and was not minimized.
- Hajj et al. is described as microwave-frequency measurement with a fitted
  Cole-Cole zero-frequency parameter, not as direct static-permittivity data.
- The current figure set displays the pressure and speciation evidence used by
  the manuscript; no prospective regression figure is presented as a result.

## Human-owned gate

The committed front matter and declarations are transcribed in
`submission_metadata.yml`, but require final corresponding-author
confirmation. The target venue, repository license, release tag, archive
provider, and DOI remain unset. No tag, release, or archive should be published
until those choices are explicit and the final scientific proof oracle passes.

## Final proof oracle

```bash
uv run ruff check src scripts analyses tests
uv run pytest -q
uv run python scripts/validate_project.py confidence
uv run python scripts/check_epcsaft_integration.py --mode final
bash scripts/build_manuscript.sh
```

The final PDF must additionally pass a page-by-page visual review, contain no
undefined citations or references, and expose the approved title, author,
subject, and keywords in its PDF metadata.
