# Item (l): linear MDEA–water law with Neumann ideal-gas heat capacity

**Return to Design.** At the Kim-only endpoint, unloaded Cp at 298.15 K is
5.21060% above Weiland 1997 at 60 wt% MDEA (3.339384 versus 3.174 J/g/K).
The requested stop rule is error above 5% at 298 K; it includes the requested
30–60 wt% check and supplies no exemption for the 60 wt% outside-fit row.
The 30–50 wt% errors remain below 5%. No joint fit ran. No amended stage-2
starts were built and no Carson searches ran. Independent review remains open.

## Scope and basis

This worktree began clean on the task branch at main commit 8c12392. Only
item (l) was executed. The issue body and comments read on 2026-10-28 are
retained here. The existing analysis scripts are reused by `run.py`; importing
`fit_mdea.py` supplies declarations and does not invoke its joint-fit entry.
All new files are confined to this directory. No MEA parameter record,
manuscript, frozen ionic choice, Zotero record or main-checkout file changed.

Engine 3e83e19ccc771b51d8ebc038931ab25192f4c5b5 was read using
`git -C /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/upstream/ePC-SAFT show 3e83e19c:<path>`:
`engine/docs/equations.md`, section `pair_parameter_temperature_law`;
`engine/src/epcsaft/parameters.py` (scalar law grammar);
`engine/src/epcsaft/regression.py` (coefficient-family resolution); and
`engine/tests/regression/test_temperature_laws.py` (declaration example).
No Engine source was imported. `runtime.json` records the installed wheel
SHA-256 and a byte comparison of installed epcsaft files with that wheel.

The pair is declared as k(T) = k0 + c1(T − 313.15 K), with powers 0 and 1
only, and no reciprocal term. Both coefficients use the Engine's
`temperature_law_coefficient` family. Admission and coefficient resolution
succeeded without a workaround. `binary-endpoint.json` retains the declaration
in its full parameter document; calculations restrict it to MDEA and water.

The primary ideal-gas Cp cubic is reused exactly from
`results/diagnosis-unloaded-cp/summary.json`. The original Neumann et al. 2022
PDF (Zotero CA5R9QN8, attachment 4V38X73R) was read at Eq. 5 / Table 8 and
section 4, pp. 11–13. The coefficients 4, 31.94, 29.98 and characteristic
temperatures 800 and 2382 K agree. The EOS ideal part was adjusted with
nonideal experimental data; the authors cannot assign reliable uncertainty
to its ideal-gas Cp. The application anchor h = s = 0 at 313.15 K replaces
the paper's normal-boiling-point anchor. `ideal-gas-check.json` verifies both
zero anchors and maximum relative cubic error 0.000129658 over 293–423 K
on a 0.1 K grid. `physical-ideal-gas-calorics.json` is the amended primary;
`wangler-sensitivity.json` retains the previous primary as sensitivity.

## Criterion (1): Kim-only pre-fit passes

All 61 Kim 2008 Table 8 observations use bubble-pressure log ratios, weight 1,
with the existing item-(k) equilibrium formulation and optimizer controls.
k0 has the MEA bound [−0.5, 0.5]. c1 has bound [−0.01, 0.01] K⁻¹, a
**diagnostic computational bound**, not an experimentally established range
or a physical prior. Coordinate scales are 0.01 and 0.001 K⁻¹.

| Initialization | Endpoint k0 | Endpoint c1, K⁻¹ | Pressure AARD, % | Objective |
|---|---:|---:|---:|---:|
| −0.1818, 0 | −0.179727220278 | 0.000616832401403 | 0.467970997 | 0.00102129887812 |
| −0.15, 0 | −0.179727229069 | 0.000616832507328 | 0.467970997 | 0.00102129887811 |

Both converge in two iterations with zero trial failures and no active bounds.
Absolute endpoint differences are 8.79097e−9 in k0 and 1.05925e−10 K⁻¹ in c1,
below 1e−4 and 1e−6 K⁻¹. Both scaled Jacobians have rank 2. Primary initial
singular values are [0.867251170, 0.0874684681]; primary endpoint values are
[0.863796309, 0.0873033842]. Secondary endpoint values are
[0.863796309, 0.0873033842]. Full Jacobians, weak right-singular vectors,
residuals, predictions, bounds and controls are retained in the fit files.
These are calibration and numerical-identification evidence, not independent
physical validation or a guarantee of joint-fit identification.

## Criterion (3): endpoint property comparisons; stop triggered

Neutral, nonreacting liquid-root Cp is evaluated by the existing
`diagnose_unloaded_cp.py` helpers, at 101325 Pa for Weiland and 100000 Pa for
Concepción. Densities use Sobrino's 0.1 MPa states. All observations and
predictions are retained row by row in the comparison CSVs.
The slope-zero control keeps item-(k)'s k0 = −0.181786994679 and changes
only the reciprocal slope to zero and the ideal-gas Cp to Neumann.
The reciprocal comparator is the original item-(k) pair with Wangler Cp.

| Quantity | Item (k), reciprocal + Wangler | Item (l), linear + Neumann | Slope 0 + Neumann |
|---|---:|---:|---:|
| Weiland Cp error, 30 wt%, % | +14.4793 | +0.9541 | −0.6278 |
| Weiland Cp error, 40 wt%, % | +19.0018 | +2.8434 | +0.7060 |
| Weiland Cp error, 50 wt%, % | +20.8909 | +3.5230 | +0.8940 |
| Weiland Cp error, 60 wt%, % | +22.4678 | **+5.2106** | +2.1575 |
| Weiland Cp AARD, four rows, % | 19.2100 | 3.1328 | 1.0963 |
| Concepción Cp AARD, 15 rows, % | 6.1037 | 2.8079 | 4.1403 |
| Concepción Cp error range, % | +0.5938 to +19.5780 | −6.0371 to +2.6567 | −9.0593 to +0.6556 |
| Sobrino density AARD, 24 rows, % | 0.14714 | 0.14894 | 0.28333 |
| Sobrino density mean error, kg/m³ | +0.49117 | +0.40383 | +1.71066 |
| Sobrino density maximum absolute error, kg/m³ | 4.58642 | 4.68326 | 9.79498 |

Concepción Table 6, 0.100 MPa column, was verified against PDF YBQI572A:
10–40 wt%, 293.15–353.15 K, with no 293.15 K point for 29.98 wt%.
The stated expanded relative Cp uncertainty is 1% (k = 2); it is not a fit
weight here. Weiland/Sobrino inputs and previous comparisons are reused
without assigning new uncertainty. The Cp limit is an owner decision and
is applied to the central predictions, without subtracting uncertainty.
Neumann ideal-gas uncertainty remains unquantified. The 60 wt% row lies
outside the ≤50 wt% other-property claim domain but was explicitly requested.
The linear law greatly reduces the reciprocal-law Cp discrepancy; the
remaining errors prevent passing the specified check. Concepción's worst
linear-law error is −6.0371% at 353.15 K, 40.01 wt%, a separate limitation
rather than the 298 K stopping trigger.

`cp-comparison.png` shows the requested 298 K error test; each marker is one
retained observation-state prediction, with no interpolation. The shaded
band is the owner's ±5% criterion, not an uncertainty band. `render.py` reads
the CSV only and uses matplotlib; `comparison.html` displays the same PNG.

## Criteria (2) and (4), amended starts

**Binary miscibility is not fully checked.** Four Gibbs-mixing lower-hull
scans at 293.15, 313.15, 353.15 and 393.15 K found no gap on the existing
item-(k) grid, using the exact linear-law value at each temperature. These
are retained in `mixing-scans.json`. They do not replace the required
Kim-state and composition-grid tangent-plane searches.

On the first execution, the runner advanced past the failed Cp check to
those scans and then failed to submit tangent-plane jobs because the dynamic
`kim` module function could not be pickled. `first-attempt.log` preserves
the exact error. The runner now places the Cp stop immediately after its
comparison and defines a local process entry for any future authorized
phase run. The final replay reproduced the two fits and property results
and stopped at the Cp gate; it did not rerun phase searches. The existing
four hull results therefore belong to the first execution.

**Carson rows 1 and 10 were not run**, and **no amended start documents were
created**, because the failed Cp gate returns to Design. The retained
primary caloric and pair endpoint declarations are evidence only and are
not qualified starts for stage 2. `gate-status.json` records this disposition.
No independent review or parameter promotion occurred.

## Reproduction and evidence

From this worktree, with no worktree virtual environment:

```bash
nice -n 10 /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/results/item-l/run.py
nice -n 10 /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/results/item-l/render.py
```

`run.log` records the final scientific stop. `input-hashes.json` identifies
source data, source PDFs, reused methods and prior evidence. `file-hashes.json`
identifies the delivered files, excluding itself. The pinned wheel hash is
0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804.
