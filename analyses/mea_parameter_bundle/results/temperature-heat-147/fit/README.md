# Corrected campaign timing stopped before numerical evaluation

The R2 timing job stopped while importing `shared_evaluation.py`: `ModuleNotFoundError: No module named 'MEA'`. The new driver includes the bundle scripts and calibration directories in `sys.path` but omits the repository `src` directory, which owns `MEA.common.mea_source_contracts`. No residual, Jacobian, equilibrium state or fitted parameter was evaluated. The stop-at-first-failure and no-retry rules were applied; no second job was launched. This is a driver prerequisite failure, with no physical-model conclusion.

The exact failed producer is `timing.py`; its full traceback, command and process measurements are in `timing.log`. `timing-failure.json` records the stopping point, input hashes, job controls, eight unstarted fits and unavailable outputs. The read-only inspection verified the qualified wheel and every installed-file hash retained in its wheel identity. The complete live issue body and all 22 comments were read, including the corrected-input amendment and its Ready review.

The intended computation uses the strict 141 targets (47 pressure and 94 species), plus eight frozen Vinjarapu Table 4 rows for the heat branch, on Engine `c1067020`, wheel SHA-256 `e8ad39e0c5d7da471a6d3ace6ff62d60518c57bc1c96fe5198d8bf18747ba8b5`. Heat declarations use 313.15 K, 1.734 MPa, 1 mol feed MEA, 7.911062165006594 mol water, initial carbon exactly zero, the frozen five reactions, and physical thermochemistry. None of these declarations was numerically reached.

## Timing and compute

Neither branch has a complete residual/Jacobian timing. Therefore the eight-fit plus assessment prediction is unavailable and the pre-fit timing gate has not passed. The failed startup consumed 0.17 s elapsed, 0.11 s user CPU and 0.03 s system CPU; maximum process memory was 34,856 KiB. The enclosing job used `agent-heavy --max 2G --timeout 1800s --wait 180`, with OMP, OpenBLAS and MKL threads each set to 1. Exit 1 is the import failure, not an infrastructure exit 137, 124 or 75. No numerical compute was added. Conservatively charging the complete startup to the prior approximate 325.12 s gives about 325.29 s consumed and 50,074.71 s remaining of 50,400 s.

## Fits and selection

| Branch | Form | Start | Outcome | Family costs, parameters, bounds, agreement |
|---|---|---:|---|---|
| No heat | Constant | 1 | Not started | Unavailable |
| No heat | Constant | 2 | Not started | Unavailable |
| No heat | Slope | 1 | Not started | Unavailable |
| No heat | Slope | 2 | Not started | Unavailable |
| Heat | Constant | 1 | Not started | Unavailable |
| Heat | Constant | 2 | Not started | Unavailable |
| Heat | Slope | 1 | Not started | Unavailable |
| Heat | Slope | 2 | Not started | Unavailable |

No branch selection, primary heat record, export/reload/rescore, identification evidence or freeze commit exists. No high-temperature loaded solve was run. No Vinjarapu residual was obtained. The existing qualification values remain their historical numerical verification; they do not substitute for corrected-campaign timing or calibration.

## Section 9.3 assessment

| Requirement | Prespecified limit | Outcome |
|---|---|---|
| Numerical completeness | All required states finite; requested tolerance met; material/charge errors at most 1e-7; stationarity at most 1e-10 | Prerequisite incomplete; no numerical assessment |
| Low-temperature pressure preservation | Cost at most 9.077053756257484 | Unevaluated |
| Low-temperature species preservation | Cost at most 27.33328854377677 | Unevaluated |
| Vinjarapu calibration agreement | Source-scale RMS at most 2; every loading-level absolute mean at most 2 | Unevaluated; raw heat RMSE/bias unavailable |
| Arcis required comparisons | Each of the two 322.5 K groups, 0.51/1.03 MPa (14 rows total): source-scale RMS and absolute mean at most 2 | Unevaluated |
| Mathonat required comparisons | 40/80 degC source-average scaled absolute residual at most 2; last two finite-epsilon estimates differ by at most 0.1 kJ/mol at each source pressure | Unevaluated |
| Transfer of calorimetric improvement | Primary aggregate independent-heat RMS at most control RMS | Unevaluated |
| Canonical 80 degC pressure no-loss | Complete 21-row AARD at most 20.270257% | Unevaluated |
| Identification | Both starts agree; normalized minimum/maximum singular-value ratio at least 1e-8; every absolute uncentered column correlation below 0.95 | Unevaluated |
| Selected slope identification | Full rank, interior slope, projected information fraction greater than sqrt(1-0.95^2) | Unevaluated |
| Effective interaction admissibility | k(T) below 1 at all calibration and assessment endpoints | Unevaluated |

Unavailable numbers cannot be labeled as a numerical or physical pass or fail. The execution prerequisite failed before these assessment conditions could be tested. The 80 degC species, Wagner cohort, 19-row pressure diagnostic, loading-error sensitivities and required endpoint/feed/phase checks remain unevaluated. Xu `vle_obs_0286` through `0288` remain explicitly unevaluated pending the source-backed domain decision. No outside-domain diagnostic was run.

## Code, retained records and delivery boundary

The new 80-line driver owns only #147 declaration, presolve and timing. It reuses `shared_evaluation.py`, the #140 input/coordinate/state checks, `refit.observations()` and native prediction/differentiation. It adds no optimizer, generic numerical method, test or fixture. No existing owner or historical result was removed.

Gross accounting from `76ea465fe1ede72257a809d04fc986489c5267f3`: 485 historical additions plus 80 new lines = **565 of 691**, with no removal credit. The driver is charged conservatively to the 100-line fit integration/selection allocation: 80 used, 20 remaining; assessment has 0 of 100 used. Total ceiling headroom is 126. `gross-line-history.txt` cross-checks the historical 485 with `git log --numstat`; the commit's numstat supplies the new 80. `change-accounting.json` is the complete final-tree CSE report. Its issue-specific executable subtotal is 553 surviving added lines; the 12 historically removed lines explain the difference from 565 gross. Unrelated main integration changes remain visible in that report and are excluded from the issue budget. `code-accounting-147.json` records this reconciliation.

All 242 previously tracked `temperature-heat-147` files were compared byte-for-byte with `a8dd324` and match. The untracked zero-carbon diagnosis directory was not written or staged. The selected current parameters, notebook, inputs and all existing records remain unchanged. No adoption, push, PR or issue edit was performed. No independent delivered review was run by this sole worker.

The direct repair is to add the repository `src` directory to the driver's import path before importing `shared_evaluation`. It is not applied or rerun here because this task explicitly forbids retries after the first failure. Resuming requires authorization for that correction and one replacement R2 timing job; the eight-fit menu, chemistry, scales and numerical tolerances would remain unchanged. Further integration must fit the remaining code allocation or obtain an explicit budget amendment before adding code.

Evidence type: execution evidence only. There is no new calibration, conditional comparison, numerical verification or physical validation result.
