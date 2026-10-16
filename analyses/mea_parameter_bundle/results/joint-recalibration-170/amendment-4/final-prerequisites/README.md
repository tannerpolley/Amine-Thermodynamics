# Amendment 4 final prerequisites: stop at Hartono source transfer

**No neutral or reacting fit ran.** The numerical dilution, density, derivative,
dielectric and local-information checks pass at the two declared starts. The
required combined Hartono source-pressure/gas-reference transfer bound of 1%
is **unestablished for all seven observations**. This fails the prerequisite
for launching a fit; it is not a computed transfer above 1% or a physical
falsification of the neutral formulation.

The calculation uses gas-free MEA mass fraction 0.30, Hartono SI targets over
298.35–360.25 K, and the fixed stage-2 neutral parameters. These are numerical
verification results, conditional on the selected SI representation and N₂O
analogy. They provide neither fitted parameters nor physical validation.

## Decision and documentation correction

The supplied 16 October 2026 decision is retained in
[design-correction.json](design-correction.json): apply r2 C1 verbatim, compute
the stated prerequisites, release the neutral fits only when all pass, and
require no further design-review round. This task adds no acceptance condition.

C1 is applied verbatim in the data owner's README and the worktree-local copy
`tmp/joint-design/amendment-4-addendum-dilute-bubble.md`. The explicitly supplied
external binding documents remain read-only to honor the instruction to work
only in this worktree. The committed correction record retains both exact
addendum substitutions, original/corrected hashes, and this scope distinction
for the parent. The settled SI choice governs this evaluation; Table 11
reconciliation is a disclosed limitation, not the stopping criterion.
Historical numerical results and source CSV values remain unchanged.

## Prerequisites and retained numbers

[Numerical summary](numerical-summary.json) retains all columns, singular
values, centered differences, source rows and precise stopping evidence.

| Prerequisite | Result | Numbers and limits |
|---|---|---|
| B1: Hartono source pressure and gas reference | **Fail: bound unestablished** | 0/7 source mappings qualified; combined effect unavailable, required ≤1% for every row |
| B2: start-B dilution | **Pass at required sentinels** | At 298.35 and 360.25 K, relative Hx changes from 1e-5 to 1e-6 are 8.1576212846e-5 and 8.2870906190e-5, both ≤1e-4; select epsilon=1e-5 |
| B2: exact gas-free density comparison | **Pass** | Maximum relative change 4.8883340424e-6 at epsilon=1e-5 over both starts and sentinels, below 1e-4 |
| B2: centered/native derivatives | **Pass** | Both coordinates, both starts, steps 0.01/0.005; maximum absolute difference 2.2775600850e-12 and relative difference 4.6163819334e-9, below 1e-8 absolute / 1e-5 relative |
| B2: dielectric equality | **Pass** | Maximum weighted-residual difference exactly 0 at both starts; required ≤1e-8 |
| B2: cold replay of corrected source targets | **Pass** | A separate process reloads the frozen source CSV targets/weights and JSON parameter inputs and reconstructs the same declarations; 37 retained JSON records agree exactly, including all seven distinct observations; prediction difference 0 Pa |
| B3: identification at start A | **Pass** | Rank 2, condition 5.4990993135; singular values 0.8510736045 and 0.1547660000 |
| B3: identification at start B | **Pass** | Rank 2, condition 5.4990225194; singular values 0.8488106803 and 0.1543566475 |
| B4: current allowance | **Pass for the next neutral call** | Charged CPU + 7680 + 17950.44 = 77468.048914 CPU-s; active wall + 240 + 1950.38 = 19995.890576 s, below 144000 / 21600 caps; no call launched because B1 is unmet |

At start B the second adjacent dilution changes are 1.1397248323e-5 and
8.5357791688e-6. The exact gas-free liquid densities are
44180.31795081578 and 42661.708023261745 mol/m³ at the cold and hot sentinels;
they are identical for A/B and the two dielectric branches. The stored 32
states all meet the requested tolerance. Maximum raw equilibrium residual is
6.5725203058e-14, maximum normalization error is 2.2204460493e-16, and minimum
native dP/drho is 2478.2255988543 Pa m³/mol. Densities are positive, liquid
density exceeds vapor density, liquid amount is 1 mol, and vapor amount is 0.
Phase support and branch declarations are explicit; no root count is invented.

The first corrected pressure target is 1512.989044998163 Pa. The two 312.65 K
rows remain separate targets, 1955.4710393002865 and 1956.59056735379 Pa,
with weights 33.33333333333333 each. The remaining five weights are
66.66666666666666; total weight is 399.99999999999994.
The two scaled information columns use scales 0.01 and 10 K, relative singular
cutoff 1e-14, and condition limit 1e4. Correlations at A/B are 0.4942569599 /
0.4949616715; weakest optimizer directions are (-0.1075509947,-0.9941995693)
and (-0.1077580902,-0.9941771442). These are local sensitivity diagnostics,
not fitted uncertainties.

## Exact source-transfer gap

Hartono SI Table S2 p.10 reports partial N₂O pressures, in row order,
**61640, 87870, 71710, 62610, 71290, 48520 and 60760 Pa**, with liquid N₂O
mole fractions **0.000301, 0.000320, 0.000261, 0.000193, 0.000187, 0.000111
and 0.000109**. The two 312.65 K source pressures are distinct and are retained
as separate mappings. None is substituted for total liquid pressure.

The hash-matched Hartono article, §2.2 p.1809, refers the apparatus procedure
to Hartono, Juliussen and Svendsen 2008, reference 18; it does not itself
supply the required N₂O gas-fugacity mapping. Its §3.3/Table 11 p.1813 and SI
Table S2 p.10 were inspected. Versteeg §§2.1–2.2/Eqs.3–6 pp.29–30 were also
read. The live library search returned five Hartono records and no 2008
apparatus paper. No contents are inferred for that missing paper. The local
literature shelf is absent; existing Zotero PDFs were used and their three
hashes checked against the data owner.

The pinned MEA parameter declaration contains no nitrous-oxide component.
Its native CO₂ vapor properties cannot establish N₂O fugacity by substitution.
No justified source total-pressure/composition envelope and corresponding
N₂O vapor-fugacity correction was established from these inspected inputs.
Accordingly, every combined-transfer field is null, with its cause retained.
The older 0.695049% CO₂ bubble-to-atmosphere diagnostic is not used for B1.
No ideal-gas coefficient, second bubble-pressure constraint, new gas model,
new source acquisition, or altered analogy is introduced to obtain a pass.

## Fits and matched comparisons

Neutral starts A/B remain **unrun as fits**. There is no estimate of
k_ij(313.15 K), b, their uncertainties, endpoint rank/condition, interiority,
convergence, active bounds, endpoint replay, or endpoint pressure transfer.
The Hartono 10% mean / 20% maximum falsifier is **untested**.
For orientation only, starting predictions against the seven SI rows give
35.8833270144% mean / 37.4241363248% maximum error at A, and
9.0149938730% / 22.1830500324% at B. Starts are not fitted endpoints.
Xu fitted comparison errors are unavailable; all 16 Xu fitting weights remain
zero and no source-pressure qualification is claimed for them.

The larger-d_V control and neutral-fixed arm are both unrun: neither C166 nor
C149 exists for either arm, so the 10% / 1% comparison is inconclusive.
Convergence, active bounds, endpoint Kiepe invariance and fitted Cp are
uncomputed. The smaller-d_V pair is also unrun and inconclusive. Historical
amendment-3 seed values are not relabeled as amendment-4 endpoints.

## Ledger, code and handoff

[Accounting](accounting.json) starts with 51527.608914 CPU-s and
12405.510576207005 active wall-s, then debits the recorded addendum task
102 CPU-s / 1800 s, a conservative correction/readiness charge of
100 CPU-s / 1800 s, and this task's 108 CPU-s / 1800 s. Total charge is
**51837.608914 CPU-s / 17805.510576207005 active wall-s**. Remainders are
**92162.391086 CPU-s / 3794.489423792995 active wall-s**. The unchanged
mandatory-check reserve is 17950.44 CPU-s / 1950.38 wall-s. Earlier excluded
idle remains 5215.0172 s; earlier unknown overhead is not asserted zero.

The 8 CPU-s evaluation charge covers all four completed numerical commands,
two startup-only failures, identity checks and reductions; their completed
whole-command CPU sum is 4.29 s. This is below both the current task's 300
CPU-s maximum and the remaining original 118 CPU-s allowance. Including the
prior 2 CPU-s charge leaves 110 CPU-s of the original 120. No neutral or
reactive fit time is charged as executed work.

[Change accounting](change-accounting.json) reports **30 added / 0 removed
executable lines**, task ceiling 30, campaign **891/900**. Numerical work uses
existing Engine equations, equilibrium solving and exact differentiation;
there is no local fitter or Engine edit. Wheel SHA-256 is
`98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a`;
all 12 installed Engine files match. Available memory at admission was
22817898496 bytes, above the 32-worker estimate 8589934592 bytes. Commands
start with `nice -n 10` and single-thread BLAS. Thirty-two native workers are
admitted for fitting; direct observation differentiation does not expose a
worker-count control or returned actual count, so 32-worker execution is not
claimed for these evaluations.

The notebook and root index rendered with the existing guarded static command,
with document execution disabled and the new linked results included as resources.
The missing Snakemake executable/workflow prevents the managed presentation
refresh; no model ran during rendering. Delivered independent inspection
remains with the parent; no adoption or manuscript promotion is claimed.
No subagent, external write, push, merge, GitHub write, server action, preview
service action, idle answer wait, or process termination occurred. Every
command ran in the requested worktree, and no numerical process remains.
