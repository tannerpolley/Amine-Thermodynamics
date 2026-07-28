# Suggested Commands

- Install locked test environment: `uv sync --locked --group test`
- Lint: `uv run ruff check src scripts analyses tests`
- Environment diagnosis: `uv run python scripts/doctor.py`
- Fast project validation: `uv run python scripts/validate_project.py quick`
- Scientific confidence validation: `uv run python scripts/validate_project.py confidence`
- Regenerate canonical analysis data: `uv run python scripts/generate_all_analysis_data.py`
- Render figures from existing result tables: `uv run python scripts/render_all_plots.py`
- Build deterministic manuscript PDF: `bash scripts/build_manuscript.sh`
- Verify manuscript freshness: `uv run python scripts/check_manuscript_freshness.py`
- Verify final pinned provider integration: `uv run python scripts/check_epcsaft_integration.py --mode final`
- Repository cleanup audit: `bash "$HOME/.codex/hooks/codex-cleanup.sh" --repo-root .`
- Check Serena memory references after memory edits: `serena memories check`
