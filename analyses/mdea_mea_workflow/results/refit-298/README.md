# Issue 298 qualification stop

F1 failed before any refit. See the existing analysis notebook's “Issue 298:
qualification stops before refitting” section for numerical values and limits.

Reproduce from the repository root with the #297 wheel installed by `uv sync`:

```bash
agent-heavy uv run python analyses/mdea_mea_workflow/scripts/refit_298.py
```

Run in a background shell and tee its output as required by AGENTS.md.
This producer only qualifies inputs and fitted-observation replays; it has no
fitting call. It retains each completed record before proceeding to the next.
The three-process pool uses AGENT_HEAVY_CORES, with single-threaded numerical
libraries. All commands launched for this attempt have ended.

- `identity.json`: checked wheel, installed bytes, adopted/shared inputs,
  stage-1 source PDF/table identities, and historical declarations.
- `F1.json` and `F1-fitted-replays.json`: scalar discrepancies and unavailable
  source rows. Remaining qualification checks are explicitly unperformed.
- `{A3,B1}-{historical,substitution}/`: newly generated parameter declarations,
  full R2 correlations, fitted predictions/statuses and independent residuals.
- `logs/`: every execution attempt, including preparation failures. The final
  completed production is `f1-final.log`.

No declared start was fitted. No frozen selection, comparison-pressure score,
phase assessment or outside-fit heat was produced. No new record is adopted.
The replay mismatch is a wheel/input/numerical qualification problem; its
specific cause has not been isolated. The exact R2 domain also excludes two
unchanged objective rows. Neither authorizes a physical transfer-penalty claim.
Independent delivered review belongs to the orchestrator. The scientific refit
remains blocked and this package is partial delivery of #298.
