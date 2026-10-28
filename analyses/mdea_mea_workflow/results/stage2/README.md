# Stage 2: bound-active endpoints stopped by phase checks

The notebook owns interpretation. `summary.json` records the objective-preferred A1/B1 candidates and the absence of a phase-qualified representative. No outside-fit data or follow-up refits were evaluated. `liquid-witnesses.csv` retains the quantitative stopping evidence; each endpoint directory retains replay, 324 phase-search records, local sensitivity, numerical checks and bounded phase diagnosis.

Use the fresh worktree at base 799f9f3. The existing `fit_mdea.run(label)` produced A3, B1 and B3; A1 was reused. Do not invoke fit_mdea.py's historical main loop, which retains its superseded bound stop. Reproduction of the checks uses:

```bash
nice -n 10 agent-heavy /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/scripts/stage2.py check A1 A3 B1 B3
nice -n 10 agent-heavy /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/scripts/stage2.py sensitivity A1 A3 B1 B3
nice -n 10 agent-heavy /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/scripts/stage2.py diagnose A1 A3 B1 B3
nice -n 10 agent-heavy /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/scripts/stage2.py numerical A1 A3 B1 B3
```

One runner transports existing objective/problem declarations and calls the Engine. No equations, generic fitting mechanics or phase-search algorithm were copied into the application. `prepare.write` remains the single output owner. The stage-2 runner adds no fallback, retry budget or changed tolerance. No existing owner was retired because the added responsibility is the previously missing stage-2 evidence orchestration. The approved gross executable ceiling is 600 lines against 799f9f3. Actual gross executable additions: **219 lines**, zero removed, in the one new runner; below the approved 600-line ceiling. `change-accounting.json` records the final tree. Its “other” category contains the generated JSON/CSV numerical evidence; it is not additional runtime code. Tests are the requested replay, conservation, phase and derivative checks; no interface-test suite was added.

The initial phase dispatch attempted to pickle native reaction objects; dispatch was corrected to pass indices into fork-inherited declarations. The first two-liquid diagnostic called the existing helper, whose post-solve stability search raised `stability correction destroys positive support`; the retained diagnostic instead reports the native two-liquid solve directly, without claiming a stable final assemblage. The reported finite descending witness remains the phase falsifier. The first accounting command found no repository-local script; the installed CSE script is used for the final accounting.

The 324 per-endpoint phase records include duplicate physical states shared by distinct residuals. All available rows are retained, including unresolved trial messages, refused roots and vapor descent. Gate failure counts include unresolved cases and are not counts of experimentally established phase changes. The full-support zero-loading phase calls are not all admitted. The positive finite-loading Merkley liquid witnesses independently suffice for the stop.

Presentation registration and refresh are confined to this worktree. No main-checkout files are written. Independent review remains open; no subagents were permitted, and no adoption, manuscript promotion, merge or push was performed.

Native refresh synchronized the worktree site index, then stopped because `snakemake` is absent. Direct `quarto render mdea_mea_workflow/notebook.qmd --to html` from this worktree’s `analyses/` directory succeeded. It rendered the retained report only, without model calculations. The generated HTML is retained at `analyses/_site/mdea_mea_workflow/notebook.html`; the full site refresh remains incomplete.
