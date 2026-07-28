# Task Completion

Run evidence proportional to the change; for a full repository completion use:

1. `uv run ruff check src scripts analyses tests`
2. `uv run pytest -q`
3. `uv run python scripts/validate_project.py quick`
4. `uv run python scripts/validate_project.py confidence` when model results, tables, figures, or numerical claims may change.
5. `bash scripts/build_manuscript.sh` and `uv run python scripts/check_manuscript_freshness.py` when manuscript inputs or included figures/tables change.
6. `uv run python scripts/check_epcsaft_integration.py --mode final` before final manuscript/report/archive claims.
7. `bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .` after any file change or task-owned process.

Inspect rendered PDFs/figures visually when layout or visual claims change. Report commands that could not run and remaining scientific uncertainty.
