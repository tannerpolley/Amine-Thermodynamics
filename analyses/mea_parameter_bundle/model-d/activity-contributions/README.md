# Issue #151: stopped at the C2 fixed-pressure density solve

The five 84-state evaluations completed without an unavailable state. N1 reproduced the three retained costs. After the owner raised the ceiling to 380 lines, the completed decomposition candidate reached C2 without a numerical assertion failure, but the pinned Engine could not solve one prescribed single-coordinate fixed-pressure intervention. The study stopped there, before C1, the N8 differences, falsifier statistics and numerical CSV export. These calculations are implemented but not verified end to end. No manuscript display or notebook section was produced. No tolerance, numerical start, parameter bound or chemistry was changed and no fit was run.

## Retained numerical evidence

`evaluations.json` retains the five costs, pressure/species costs, 142 weighted residuals and maximum stationarity errors. All 420 states and their full evaluator diagnostics remain in ignored `runs/*-states.jsonl`; `inputs.json` records their hashes. The original Born replay differed from its reference cost by 9.379164112033322e-13; the adopted and Born-off-refit costs matched exactly.

`checks.json` retains the original checks-first run's maximum errors and locations, and all 25 sentinel estimates at h and h/2 with their differences. The resumed run passed those assertions, plus the new Born-off zero assertions, before the C2 exception; its in-memory maxima were not checkpointed before that exception. The table below therefore reports the original retained values, not newly measured maxima for the resumed source. `checks.json` distinguishes both executions. Passing retained maxima in dimensionless ln units were:

| Check | Maximum error | Approved tolerance | Coverage |
|---|---:|---:|---|
| N2 | 2.1316282072803006e-14 | 1e-12 | 31,369 scalar-sum checks, including perturbations |
| N3 | 2.3740030883345753e-6 | 1e-5 | 1,651 difference evaluations, including pure-water references |
| N4 | 3.186414687661454e-9 | 1e-5 | 1,651 difference evaluations |
| N5 | 1.2626987455632843e-8 | 1e-6 | R1–R5, all five records, grouped by temperature |
| N5a | 4.7061831054406866e-7 | 1e-6 | All 420 solved states |
| N6 | 4.60637902377492e-7 | 1e-6 | Two Born-on records |
| N7 | 3.410605131648481e-13 | 1e-10 | 168 Born-on states; Born-off invariance is not separately asserted |
| N8, absolute only | 2.3765570977829498e-7 | 1e-6 | 240 pressure states across five records; differences pending |
| N9 | 1.7783464372200797e-6 | 1e-5 | Five sentinel states per record, all terms and species |

The N6 salt-free, 30 wt% MEA–water values at 313.15 K, referenced to pure water, were:

| Ion | SSM+DS Born ln gamma* | Original Born ln gamma* |
|---|---:|---:|
| MEAH+ | -0.14529715721809566 | +0.4191672137863236 |
| MEACOO- | -0.14497542388559737 | +0.41823904652449073 |
| H3O+ | -0.4214845393620976 | +1.2159391374269717 |

These reproduce the accepted hand calculation, including the opposite signs. This is numerical verification of model-internal quantities, not physical validation or a pressure-mechanism conclusion. H1, H2 and C were not computed; they have no disposition, including no invented “not evaluable” outcome. Temperature/loading-third values are unavailable because numerical CSV export has not run.

## Exact stopping point and bounded diagnosis

The numerical failure is reproduced at `vle_obs_0139`, 313.15 K and 8011.150874919407 Pa, with adopted composition held fixed. Moving only MEAH+–water k from -0.37931089293768305 to the retained Born-off-refit value +0.06968817739786343 gives the Engine's `ConvergenceError`: `left_domain`, residual 0.0084948354266894399 versus `DENSITY_ROOT_RESIDUAL` 1e-12, after two iterations; contraction absent, floor 3.5805781949253065e-15 and amplification 1861.6987413317174. At the unchanged adopted density, the intervened EOS returns a finite pressure of 41871040.519260176 Pa and Z=0.3001328900258302. The immutable intervened mapping fingerprint is `sha256:124345c672023a8928d7f86a9ec56e2981692f879d5bd4b894fa607e246433c9`.

`c2-density-failure.json` retains the exact composition, density anchor (53581.33897588033 mol/m³), source-coordinate values, preceding accepted C2 states and coordinate responses, failed attempt and unattempted-state count. Twenty C2 states completed; state 21 failed on its second coordinate, leaving 27 pressure states unattempted. The retained feed ratio at the failed state is 0.49090981819636393 mol CO₂/mol MEA. A read-only reproduction traversed only the existing adopted pressure states in retained order and stopped at the same failure. It used the same fixed-pressure call, anchor, mapping and tolerance. No alternate start, new grid or root-cause fix was attempted. Two preceding diagnostic commands are also retained: the first lacked the module's reaction-matrix binding; the corrected first-state probe showed that the first pressure state was not the failing one. Neither supplies the requested Born-off mechanism result.

The numerical method failed to reach the requested pressure for this intervention. This does not establish physical nonexistence of the liquid root or rejection of a Born hypothesis. Whether the root exists on the intended liquid branch, and whether an approved Engine density method can reach it, remain unresolved. Further diagnosis or a corrected Engine capability returns to the owner through Design; MEA does not repair the Engine's density solver or choose a different numerical start under this issue.

The one script now implements C1/C2, the falsifiers, long-CSV coverage and rendering. The resumed executed version was 349 lines. The retained source adds only failure-preservation writes afterwards: checkpoint core checks before C2, record each intervention before solving, and retain partial diagnostic values on an exception while re-raising it. That final failure-preservation revision was compiled but not numerically rerun. No existing driver was edited and no superseded implementation exists to remove. The final source remains below the owner's 380-line ceiling; `change-accounting.json` gives the count from base `76ea465`.

The render function remains untested because no checked CSVs were produced. C1/N8 differences, H1/H2/C, the display values and notebook section remain unavailable. No notebook render was attempted. This stopped study has not been independently reviewed or promoted for manuscript use.

## Execution and provenance

`inputs.json` records the exact wheel SHA-256 28181e72e429c6e87fc6361082af1a7b21c8747e76bda65a1c30abb4a97402f2, source commit 8c670d3a, input and script hashes, and read-only use of the #141 interpreter while importing this #151 worktree's analysis code. The two Born-off-without-refit mappings were written with `p1.without_born`. The #141 matching branch baselines were read, not changed. No distribution metadata was changed and no Engine source checkout was imported.

`execution-commands.json` records each numerical command, environment, 2 GiB address-space limit, wall time and host numerical jobs observed before it, including diagnostic stdin. Evaluations used 120.903 s wall time; the original checks-first run used 49.579 s; the resumed decomposition used 47.917 s; three diagnostic commands used 0.945, 0.990 and 4.369 s. Total wall time was 224.702 s. CPU time for the resumed run and diagnostics was 54.071 s; earlier CPU times were not measured. All commands ran sequentially and single-threaded, with at most one other numerical Python job observed. Timeouts were 600 s per evaluation/diagnostic command and 1800 s for decomposition.

The worktree has no `literature/` shelf. No new literature-backed claim was made; the accepted issue's equations and independent reference values were used. No notebook render was attempted because the Born-off mechanism result and requested retained displays are incomplete. All writes remain in the authorized #151 worktree, and delivery is local commits only.
