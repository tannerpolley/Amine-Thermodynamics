# Reproducibility and Dependency Note

## Current status

This checkout currently uses a development ePC-SAFT source path in `pyproject.toml` and `uv.lock` so the local MEA/ePC-SAFT co-development workflow remains runnable on this machine.

Local Windows paths also appear in runtime fallback modules and helper scripts that are development-facing, not manuscript text. The LaTeX source files under `docs/latex/sections/` do not depend on `C:\Users\...` paths.

Current check on 2026-05-13:

- The lockfile path `C:\Users\Tanner\.codex\worktrees\epcsaft-dev\ePC-SAFT` is not present.
- The shared checkout `C:\Users\Tanner\Documents\git\ePC-SAFT` is present.
- `pyproject.toml` and `uv.lock` both point `epcsaft` at the missing worktree-backed path.
- `uv run python scripts/check_epcsaft_integration.py --mode dev --self-only` fails during package metadata generation until the missing dev worktree is restored or the dependency is repinned.

Package-dependent Phase 2/3 execution is therefore gated behind one of these unblock actions:

1. Restore the dev worktree at `C:\Users\Tanner\.codex\worktrees\epcsaft-dev\ePC-SAFT`.
2. Repin `epcsaft` to a stable Git ref, release, or approved local package source and refresh `uv.lock`.

After the dependency is restored or repinned, rerun from this repository root:

```powershell
Test-Path C:\Users\Tanner\.codex\worktrees\epcsaft-dev\ePC-SAFT
uv sync
uv run python scripts/check_epcsaft_integration.py --mode dev --self-only
uv run python scripts/check_epcsaft_integration.py --mode dev
uv run python scripts/check_epcsaft_integration.py --mode final
```

Only after those pass should a GoalBuddy run attempt package-dependent Phase 2/3 figure regeneration, coupled pressure/speciation validation, or final manuscript/archive acceptance checks.

## Clean-checkout strategy

For a portable clean checkout, use one of these modes:

- `stable`: install `epcsaft` from a pinned Git ref or released package and run `uv run python scripts/check_epcsaft_integration.py --mode stable`.
- `dev`: use the explicit local worktree-backed path documented in the repo-local instructions and run `uv run python scripts/check_epcsaft_integration.py --mode dev`.
- `final`: use a released, tagged, pinned, or repo-owned `epcsaft` input and run `uv run python scripts/check_epcsaft_integration.py --mode final`.

Final manuscript, report, and archive results must not depend on a mutable shared checkout.

## Do not move into ePC-SAFT

Keep MEA-specific data curation, target manifests, pressure/speciation validation splits, manuscript figures, and interpretation in this repository. Only generic EOS, equilibrium, regression, and dataset-schema capabilities belong upstream.
