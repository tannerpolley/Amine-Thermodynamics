# Reproducibility and Dependency Note

## Current status

This checkout currently uses a stable pinned Git ePC-SAFT source in `pyproject.toml` and `uv.lock`:

`epcsaft @ git+https://github.com/tannerpolley/ePC-SAFT.git@e9510abae528016bd2513f12069fc0534b252bea`

Local Windows paths previously appeared in runtime fallback modules and helper scripts that are development-facing, not manuscript text. The LaTeX source files under `docs/latex/sections/` do not depend on local user-profile paths.

Current check on 2026-05-15:

- `pyproject.toml` and `uv.lock` point `epcsaft` at the upstream Git commit `e9510abae528016bd2513f12069fc0534b252bea`.
- This keeps the downstream workflow in stable pinned-Git mode while retaining the public API surface required by the current MEA tests.
- `uv run python scripts/check_epcsaft_integration.py` passes in stable mode and reports `source kind: pinned_git`.
- The local `<epcsaft-dev-worktree>` path is not required for routine downstream validation.

Package-dependent Phase 2/3 execution should use stable mode unless intentional upstream/downstream co-development is explicitly requested.

Rerun from this repository root:

```powershell
uv sync
uv run python scripts/check_epcsaft_integration.py
uv run python scripts/check_epcsaft_integration.py --mode final
```

Only after final-mode validation passes should a GoalBuddy run promote package-dependent Phase 2/3 outputs into final manuscript/archive acceptance checks.

## Clean-checkout strategy

For a portable clean checkout, use one of these modes:

- `stable`: install `epcsaft` from a pinned Git ref or released package and run `uv run python scripts/check_epcsaft_integration.py --mode stable`.
- `dev`: use the explicit local worktree-backed path documented in the integration contract only for intentional co-development and run `uv run python scripts/check_epcsaft_integration.py --mode dev`.
- `final`: use a released, tagged, pinned, or repo-owned `epcsaft` input and run `uv run python scripts/check_epcsaft_integration.py --mode final`.

Final manuscript, report, and archive results must not depend on a mutable shared checkout.

## Do not move into ePC-SAFT

Keep MEA-specific data curation, target manifests, pressure/speciation validation splits, manuscript figures, and interpretation in this repository. Only generic EOS, equilibrium, regression, and dataset-schema capabilities belong upstream.
