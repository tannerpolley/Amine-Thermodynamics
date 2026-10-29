# Downstream acceptance of Engine d5138209

All three downstream acceptance checks pass. The orchestrator clarified that
energy equality means absolute differences no larger than 1e-10 near zero,
with unchanged classifications. Refits may proceed. Engine #911 is left to
the orchestrator; it does not block the clarified acceptance.

The issue branch includes main 430c9c9 (merge 7d3ded9), preserving the
91f8cc7 continuation of db33c11. The isolated worktree `.venv` consumes the
retained immutable wheel identified in `runtime.json`. The release checksum,
GitHub asset digest and tag target were checked. All installed package and
bundled-library bytes equal the wheel. The root dependency pins are unchanged.

## Phase acceptance (a): passes under the clarified energy comparison

Each historical endpoint has 754 searched state records. Zero-loading trials
use carbon-free supports; the density threshold remains 0.10. Counts are
records, including repeated physical states for different observations.

| Quantity | A1 | B1 |
|---|---:|---:|
| Dense split states | 0 | 0 |
| Gas evolution states | 42 | 40 |
| Reconstruction trials | 0 | 0 |
| Other unresolved states | 0 | 0 |
| Ambiguous densities | 0 | 0 |
| Other trials checked against old wheel | 6430 | 6434 |
| Changed classifications | 0 | 0 |
| Energy values differing under exact comparison | 99 | 122 |
| Maximum absolute change in ΔG/RT | 1.8189894e-12 | 1.8189894e-12 |
| Maximum relative change in ΔG/RT | 6.8585036e-7 | 1.2495957e-8 |
| Trials exceeding 1e-8 relative change | 11 | 10 |

The largest absolute energy change is below the clarified 1e-10 limit.
All classifications are unchanged; both searches pass. Relative error near
zero is retained as diagnostic context and is not the acceptance criterion.
Per-trial before/after evidence is in `{A1,B1}/acceptance.json`. Full searches
are in `{A1,B1}/phase.json.gz`; raw and compressed hashes are registered in
`../../compressed-evidence.json`.

## Capped-heat acceptance (b): passes

`capped-heat-acceptance.json` retains eight A1/B1 start-state replays and four
A1 branch checks at 333.15 K / 20 wt% and 388.71 K / 40 wt%, at 1121000 Pa.
The source caps 0.50 and 0.25 exercise the uncapped branch; 1.25 and 0.75
force saturation truncation. All twelve heat values agree with the retained
direct saturation-plus-heat references within 4.7895022e-13 relative (limit
1e-8). Both branches pass nine-coordinate central differences with optimizer
steps 0.003 and 0.001. All 72 central-difference comparisons pass; the worst relative error across
both declared steps is 2.1699834e-6 (limit 1e-5). Both step results are retained. All eight actual source-cap start states remain untruncated.

These checks verify numerical calculations, not physical validation. The
saturation search has 30 nodes from 0.05 to 1.50 mol/mol; its uniqueness is
limited to that search. No new fit, switch encounter, root refusal, outside-fit
statistic, Wangler sensitivity or bicarbonate/control fit was computed.

Acceptance (c) passes: both 61-row pressure replays agree within 9.33e-15
relative; all 2354 binary phase searches have zero liquid splits or unresolved
trials, all mixing scans are miscible, and the Cp and eight amended Carson
checks pass. See `prefit-acceptance.json` and row-level retained evidence.
Both variants' selected endpoints and transfer verdicts remain pending refits.
Independent delivery review has not run.

Reproduce with the worktree interpreter, without changing root pins:

```bash
agent-heavy nice -n 10 .venv/bin/python -I analyses/mdea_mea_workflow/scripts/accept_engine_delivery.py
agent-heavy nice -n 10 .venv/bin/python -I analyses/mdea_mea_workflow/scripts/accept_capped_heat.py
```

The phase calculation uses at most 16 processes; the heat calculation has
12 independent jobs. Each process has one BLAS thread. No Engine source or
main-checkout file was edited.

The initial Engine #911 example mislabeled `fit:126:1` as 20 wt%.
Its retained declaration is 333.15 K / 40 wt%; the trial index and energy
values were correct. The orchestrator owns further #911 communication.
