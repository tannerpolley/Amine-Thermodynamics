# Issue #151: partial execution, code-budget pause

The five 84-state evaluations completed without an unavailable state. N1 reproduced the three retained costs. The checks-first decomposition candidate passed N2–N7, N5a and N9, and the absolute-pressure portion of N8. This does not complete the Born-off mechanism study: C1/C2, the pressure-difference portion of N8, H1/H2/C statistics, and numerical CSV exports are not implemented. No manuscript display or notebook section was produced. No numerical tolerance was changed and no fit was run.

## Retained numerical evidence

`evaluations.json` retains the five costs, pressure/species costs, 142 weighted residuals and maximum stationarity errors. All 420 states and their full evaluator diagnostics remain in ignored `runs/*-states.jsonl`; `inputs.json` records their hashes. The original Born replay differed from its reference cost by 9.379164112033322e-13; the adopted and Born-off-refit costs matched exactly.

`checks.json` retains the checks' maximum errors and locations, and all 25 sentinel estimates at h and h/2 with their differences. Passing maxima in dimensionless ln units were:

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

## Exact stopping point and budget request

`activity_contributions.py` is an incomplete 230-line candidate, not a delivered implementation. Its numerical run exited with code 1 at the explicit final `RuntimeError` saying C1/C2, falsifiers and table export are not implemented. No numerical assertion failed. The render function is untested and cannot run without the missing CSVs. The candidate currently accumulates long-format values in memory but does not export them; only check values are retained from the decomposition run. Additional corrections are required for full long-CSV species split coverage, no-refit output selection and explicit coverage reporting.

Only 20 lines remain under the approved 250 gross added executable-line ceiling. Remaining work foreseeably needs about 130 additional or revised lines: C1 and C2 including difference N8 and coordinate-zero checks (about 50); H1/H2/C with tie, population and undefined-statistic rules and pressure-cost attribution (about 40); long CSV retention/coverage corrections and failure-safe final export (about 20); rendering completion and verification (about 20). These are estimates, not an approved new budget. A proposed revised ceiling is 380 lines in the same single script. No existing numerical driver was edited, and no superseded implementation exists to remove. Compression, weaker checks or moving executable code into generated files would not justify fitting the remaining work into 20 lines.

Pause for the owner to approve a revised ceiling or reduce scope. A further decomposition run would also be needed after implementation to retain the numerical CSVs and verify the added checks; no further run was started. This partial tree has not been independently reviewed or promoted for manuscript use.

## Execution and provenance

`inputs.json` records the exact wheel SHA-256 28181e72e429c6e87fc6361082af1a7b21c8747e76bda65a1c30abb4a97402f2, source commit 8c670d3a, input and script hashes, and read-only use of the #141 interpreter while importing this #151 worktree's analysis code. The two Born-off-without-refit mappings were written with `p1.without_born`. The #141 matching branch baselines were read, not changed. No distribution metadata was changed and no Engine source checkout was imported.

`execution-commands.json` records each numerical command, environment, 2 GiB address-space limit, wall time and host numerical jobs observed before it. Evaluations used 120.903 s wall time in total; the checks-first run used 49.579 s. All six commands ran sequentially, single-threaded, with at most one other numerical Python job observed. CPU time was not measured. Numerical timeouts were 600 s per evaluation and 1800 s for decomposition.

The worktree has no `literature/` shelf. No new literature-backed claim was made; the accepted issue's equations and independent reference values were used. No notebook render was attempted because the Born-off mechanism result and requested retained displays are incomplete. All writes remain in the authorized #151 worktree, and delivery is local commits only.
