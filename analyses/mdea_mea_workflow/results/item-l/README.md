# Item (l): linear MDEA–water law with Neumann ideal-gas heat capacity

**Return to Design: criterion (4) fails.** Criterion (2) passes all 1,177
binary tangent-plane searches and four convex-hull scans. Nine of ten amended
Carson searches pass; A4 at row 10 has a resolved two-liquid descent,
ΔG/RT = −0.130277337990 versus estimated numerical error 2.64057e−8.
Criterion (3) passes under the owner's 2026-10-28 ≤50 wt% claim-domain reading.
The +5.21060% Cp error at 60 wt% is reported as extrapolation.
The five amended starts are retained but are not qualified for stage 2 as a
set. No joint fit ran. Independent delivered review remains open.

## Scope and basis

This worktree began clean on the task branch at main commit 8c12392. Only
item (l) was executed. The issue body and comments read on 2026-10-28 are
retained here. The existing analysis scripts are reused by `run.py`; importing
`fit_mdea.py` supplies declarations and does not invoke its joint-fit entry.
The continuation starts from a clean worktree at main commit 2987259.
Its changed results are confined to this directory and the analysis notebook. No MEA parameter record,
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

## Criterion (3): endpoint property comparisons; passes within the claim domain

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
The linear law greatly reduces the reciprocal-law Cp discrepancy. Under the
owner reading recorded on issue #222 on 2026-10-28, the 298.15 K gate applies
within ≤50 wt%: the maximum error there is +3.5230%, which passes. The 60 wt%
row remains an extrapolation comparison and does not count against this gate. Concepción's worst
linear-law error is −6.0371% at 353.15 K, 40.01 wt%, a separate limitation
rather than the 298 K stopping trigger.

`cp-comparison.png` shows the requested 298 K error test; each marker is one
retained observation-state prediction, with no interpolation. The shaded
band is the owner's ±5% criterion within ≤50 wt%, not an uncertainty band.
The 60 wt% marker is an extrapolation comparison. `render.py` reads
the CSV only and uses matplotlib; `comparison.html` displays the same PNG.

## Criterion (2): binary liquid miscibility passes

All 1,177 tangent-plane searches complete: 61 at the Kim measured states and
1,116 on the existing 279-point x(MDEA) grid (including pure endpoints) at
293.15, 313.15, 353.15 and 393.15 K, at 101325 Pa for the grid. There are zero
liquid–liquid witnesses and zero unresolved searches. All four Gibbs-mixing
convex-hull scans are miscible. The maximum equilibrium residual is
1.08245e−10 in the Engine's equation residuals. Full trials, compositions,
search work and split checks are retained in `binary-phase-search.json`.

There are 171 searches with vapor witnesses, classified separately under the
owner's item-(k) ruling. Of these, 38 are Kim states; all 38 have positive
model-minus-observed bubble-pressure residuals, with zero sign mismatches
(`vapor-sign-check.json`). Vapor descent does not fail the liquid-miscibility
gate. These finite searches establish numerical evidence at the specified
states and grid, not a proof over every composition or experimental miscibility.

The first execution's dynamic-module pickling failure remains in
`first-attempt.log`. The continuation submits `run.py::phase_check`, a
module-level process entry, and installs the linear-law model in that process.
Search methods, trial sets, tolerances and budgets are unchanged. The binary
pass calculation now counts liquid witnesses only while requiring a converged
liquid, completed search and zero unresolved trials.

## Criterion (4): amended Carson starts fail at A4 row 10

Five parameter documents are retained in `amended-starts/`: A1, A3, A4, B1
and B3. Each differs from its item-(k) document only in the MDEA–water pair:
k0 = −0.17972722027839907 and c1 = 0.000616832401403298 K⁻¹ at 313.15 K.
`hashes.json` binds each document to the common Neumann primary caloric file
and records both `temperature_law_coefficient` coordinate identities and
origins. Those identities resolve through the pinned Engine. A2 and B2 remain
duplicates of A1 and B1 and are not run separately. No other frozen value
changes. Neumann calorics are supplied through `run.py::thermal`.

| Start | Carson row 1 | Carson row 10 |
|---|---|---|
| A1 | no witness | no witness |
| A3 | no witness | no witness |
| A4 | no witness | two-liquid witness |
| B1 | no witness | no witness |
| B3 | no witness | no witness |

All ten liquid solves meet the requested tolerance; all ten searches complete
with zero unresolved trials. The largest equilibrium residual is 3.55272e−13.
A4 row 10 at 298.15 K and 101325 Pa gives ΔG/RT = −0.13027733799026464,
with estimated numerical error 2.6405663928255056e−8. Its admitted split has
liquid amounts 60.1684007 and 0.362303992 mol on the one-mol-MDEA feed basis;
the second liquid has x(water) = 0.236090, x(MDEA) = 0.133162, and
x(MDEAH+) ≈ x(HCO3−) ≈ 0.315366. Both phases are liquid, so this is a gate
failure rather than a separately classified vapor witness. Full compositions
and trial diagnostics are in `amended-carson-search.json`; counts are in
`phase-summary.json`.

The magnitude of the descending split exceeds its numerical error by roughly
4.9 million. This is a numerical phase-instability finding for the declared
A4 model and feed, not observed physical demixing. Per the prescribed stop,
item (l) remains incomplete and stage 2 returns to Design. No new starts,
parameter changes, retry searches or joint fit follow this failure.

## Reproduction and evidence

From this worktree, with no worktree virtual environment:

```bash
nice -n 10 /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/results/item-l/run.py --finish-gates
nice -n 10 /home/tnnrpolley21/Workspaces/Engineering/Amine-Thermodynamics/.venv/bin/python -I analyses/mdea_mea_workflow/results/item-l/render.py
```

`run.log` records the earlier Cp stop; `finish-gates.log` records the continuation
and the A4 phase failure. `--finish-gates` reuses the retained fits and property
comparisons, verifies the pinned wheel and runs only the prescribed phase gates. `input-hashes.json` identifies
source data, source PDFs, reused methods and prior evidence. `file-hashes.json`
identifies the delivered files, excluding itself. The pinned wheel hash is
0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804.

The ignored `literature/` reading shelf is absent from this worktree. No new
literature judgment or source transcription was made in this continuation;
the accepted methods, coefficients and retained comparisons were reused.

Notebook source: `../../notebook.qmd`. The presentation-only site refresh was
attempted with the pinned interpreter and failed because `snakemake` is
unavailable. The notebook source and analysis-site navigation are retained;
the site HTML was not refreshed. No preview service was changed.

Change accounting against 2987259: `run.py` adds 52 executable-file lines and
removes 40; `render.py` adds 4 and removes 3 (comments/blanks included).
The runner owns process submission, liquid-only gate accounting, retained-fit
continuation and amended-start declarations. It reuses the existing scientific
search owners and replaces the superseded Cp stop interpretation. The figure
change restricts the gate band to the claim domain. No numerical method,
search tolerance, physical equation or joint-fit implementation changed.
