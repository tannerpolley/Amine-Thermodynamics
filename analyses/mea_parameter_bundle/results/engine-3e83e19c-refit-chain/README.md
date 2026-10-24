# MEA association-volume refits on Engine 3e83e19c

**All declared fits and fixed calculations completed their checks; no stop
remains.** The second restricted fit converged and is usable after eight
iterations, with native cost 148.87893934555717. Its fixed replay costs
148.87893934557388 over all 307 rows, 23.860996312136727 over the 149-quantity
group, and 91.87458520309771 for Cai. The density rule and conditional
uncertainty assertions pass. This is a new reported candidate, awaiting the
separate density-free limit comparison and adoption decision.

Authority: [issue #212](https://github.com/tannerpolley/Amine-Thermodynamics/issues/212),
based on main at `3f01bc1`, and the orchestrator's 2026-10-24 continuation
decision. Every calculation uses merged Engine commit
`3e83e19ccc771b51d8ebc038931ab25192f4c5b5`, wheel SHA-256
`0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`.
The MEA self-association volume is fixed at `0.036305439` throughout.
`fit_campaign.verify` checked the installed Engine files byte for byte against
that wheel. No Engine source checkout was imported.

## Fit and reduction results

Costs are dimensionless, one half of the sum of squared weighted residuals.
All four joint fits retain all 307 available, finite objective rows.

| Calculation | Numerical completion | Iterations | Native final cost |
|---|---|---:|---:|
| Neutral MEA–water, start A | Converged, usable; all checks pass | 1 | 91.80963081696791 |
| Neutral MEA–water, start B | Converged, usable; all checks pass | 1 | 91.80963081698934 |
| Stage-5 reduction | 14 rows; rank 2; both roots pass | Direct calculation | 1.9338548589681683 |
| A6 comparison | Converged, usable; fresh information checks pass | 5 | 148.2115075904099 |
| Hartono x₃ sensitivity | Converged, usable; fresh information checks pass | 5 | 148.31366430715744 |
| First restricted fit | Converged, usable; fresh information checks pass | 4 | 149.21952645124134 |
| Second restricted fit | Converged, usable; fresh information checks pass | 8 | 148.87893934555717 |

Stage 2 selected A by its serialization replay cost, 91.80963081696862.
Both starts retain full rank, no active bound, verified equilibrium rows,
positive pressure–density derivatives, nonnegative reduced Hessians, centered
derivative checks and serialization replays. The selected cost is below the
better same-basis start. No constant CO₂–water fit was entered.

Stage 5 preserves the preceding reference's qualified water and CO₂–water
inputs and changes only the MEA association volume and neutral MEA–water
interaction. Its smaller-volume branch is 0.24645459482573953 L/mol and
2436.43575418438 K; its larger-volume branch is 0.7309865858310542 L/mol and
1019.0802597119892 K. The maximum absolute native permittivity replay error
is `2.842170943040401e-14` for both branches, below `1e-10`.

The fixed 307-row replays for both requested fits have every row available,
finite and meeting its requested tolerance. Replay costs differ from their
native fit costs by at most `1.6712e-11` absolute. The other two joint fits'
subgroup costs below are reductions of native weighted residuals.

| Fit | 307-row cost | 149-quantity cost | Cai cost | Basis |
|---|---:|---:|---:|---|
| A6 comparison | 148.21150759040813 | 24.920645016884034 | 91.77764784327805 | Fixed replay |
| Hartono x₃ sensitivity | 148.31366430715744 | 24.91033009406157 | 91.77853317050315 | Native, its own composition basis |
| First restricted | 149.21952645124134 | 24.10250358939657 | 91.88937725031957 | Native |
| New reported candidate | 148.87893934557388 | 23.860996312136727 | 91.87458520309771 | Fixed replay |

## Parameter changes and prepared starts

[parameter-changes.csv](parameter-changes.csv) and
[parameter-changes.json](parameter-changes.json) retain every changed
coefficient against its preceding endpoint, including absolute and signed
relative changes. Relative change means `(refitted - previous)/previous`;
a zero denominator gives an unavailable ratio. The reported candidate is
[the second restricted endpoint](restricted-2/attempt-3/run/fit/usable-budget-endpoint.json),
SHA-256 `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91`.
Its principal changes against the preceding reported fit are:

| Quantity | Previous | New | Absolute change |
|---|---:|---:|---:|
| MEA association volume | 0.036287 | 0.036305439 | +0.000018439 |
| MEA dielectric volume, L/mol | 0.7309888238084122 | 0.7309865858310542 | −0.000002237977358 |
| MEA dielectric temperature, K | 1019.0786110170793 | 1019.0802597119892 | +0.001648694910 |
| MEA–water constant interaction | −0.08990482269248873 | −0.08990160794755829 | +0.00000321474493044 |
| MEA–water reciprocal-temperature slope, K | −8.06991337259403 | −8.057331218929972 | +0.0125821536641 |
| MEAH⁺ dispersion energy divided by Boltzmann constant, K | 177.79505478642625 | 177.89333334239393 | +0.0982785559677 |
| Carbamate segment diameter, Å | 4.866040008417222 | 4.866108647520244 | +0.0000686391030 |
| Carbamate dispersion energy divided by Boltzmann constant, K | 207.27459667183842 | 207.21694618033155 | −0.0576504915069 |
| Bicarbonate–water interaction | 0.725320998100705 | 0.7270558477497251 | +0.00173484964902 |
| Carbamate–water interaction | −0.0038632044486184474 | −0.0036580495327475336 | +0.000205154915871 |

The selected neutral interaction used for the constant-interaction Cai
calculation is −0.08439986221195522, replacing −0.0843938800264997.
It is the stage-2 result; no second Cai fit was performed.

Joint starts preserve observations, scales, ties, controls and physical bounds.
Reaction bounds are rebuilt from the original unshifted boxes using each
endpoint's inherited R2/R5 totals. A6 and x₃ carbamate segment diameters move
from 5.8 to 5.798 Å; the first restricted MEAH⁺ diameter moves from 5.49 to
5.492 Å. Packing and Debye–Hückel ties are reapplied. Born diameters and
interactions are not moved.

The second restricted start is the new first restricted endpoint,
SHA-256 `d0af148a8db25760f541f6c702768d51c7b2e51a38b3a31691034216eccfb858`,
with its own chemistry file. Its inherited totals are R2 =
−1811.930108185226 J/mol and R5 = 10000 J/mol. The MEAH⁺ lower size bound
is 5.35 Å. Re-evaluating the inward rule requires no diameter move, as recorded
in [restricted-2/preparation.json](restricted-2/preparation.json).

## Density and fixed calculations

The reported candidate has **44 of 47 loaded densities within twice their
assigned scale**. Its only misses are the three permitted rows:

| Row | Signed error divided by assigned scale |
|---|---:|
| `Amundsen2009_state_081` | −2.2826989829854005 |
| `Hartono2014_density_80C_alpha0.29` | −2.0543380948137258 |
| `Hartono2014_density_80C_alpha0.39` | −2.430831623760042 |

The largest absolute CO₂-free density error is **0.557484452458425 kg/m³**,
at `AMU-DENS-002` (signed error −0.557484452458425 kg/m³), below 1 kg/m³.
The density rule passes. The comparison fit has all 47 loaded densities within
twice their assigned scales. Scores and row values are in
[displays/reported/score.json](displays/reported/score.json) and
[displays/comparison/score.json](displays/comparison/score.json), with sibling
`full-replay.json` files.

The reported-fit permittivity calculation retains all 14 rows at 298.15 K
and 101325 Pa, explicitly using the new stage-5 rows and reported endpoint.
Its cost is 1.9123762682171106, relative-permittivity RMSE is
0.30144843492606227, and average absolute relative deviation is
0.45273994351848046%. The native solvent-law and pure-water replay checks pass.
[Permittivity rows and summary](displays/permittivity/summary.json) retain the
calculated values and the maximum change from stage 5.

The Cai-only calculation uses the new reported candidate with constant
MEA–water interaction −0.08439986221195522 and zero temperature slope;
all other inputs are retained. All 50 Cai quantities are available. Its cost
is **91.29322049026165**, from
[displays/cai-constant-replay.json](displays/cai-constant-replay.json).

The Arcis comparison uses 14 addition-enthalpy quantities for each fit.
Errors mean predicted minus observed addition enthalpy, in kJ/mol CO₂.

| Fit | Overall RMSE, 14 rows | RMSE at 0.51 MPa, 8 rows | RMSE at 1.03 MPa, 6 rows |
|---|---:|---:|---:|
| New reported candidate | 8.115640714619083 | 10.332399122695893 | 3.3670700883078895 |
| New comparison fit | 8.05184864877517 | 10.260693886454757 | 3.3014396109050015 |

[displays/summary.json](displays/summary.json) retains every Arcis error and
pressure-group bias. Both fits have positive errors at both pressures.
The reused producer also retains its unchanged-water assessment; it performs
no water fit.

The existing conditional-uncertainty calculation passes its asserted active
set **`[1,3,5,7,8,11]`** and free rank **10**, using 307 residuals and 297
degrees of freedom. Standard errors and correlations are in
[displays/conditional/conditional-uncertainty.json](displays/conditional/conditional-uncertainty.json)
and its sibling CSV files. They are conditional on residual weights, fixed
inputs, active bounds and local linearization; they do not establish
measurement-error uncertainty, parameter uniqueness or prediction intervals.

## Interrupted execution and continuation

The original [restricted-2/stop.json](restricted-2/stop.json) and its five
partial derivative evaluations remain unchanged. They record an execution
interruption, with no native information result and no fit launched in that
attempt. The orchestrator explicitly authorized identical re-execution on
2026-10-24, distinguishing it from a numerical retry.

`attempt-2/` retains a launch error: calling the runner directly under
`python -I` could not import its sibling `fit_observations` module. That
launch performed no numerical calculation. The successful
[attempt-3/](restricted-2/attempt-3/continuation.json) loads the existing producer
for its established import paths, then calls `fit_campaign.run` with a byte-identical
copy of the interrupted information declaration. It retains all original start,
chemistry, bounds, controls, budgets and tolerances. The fit declaration adds
only its existing fit case and the new successful information-check binding.
No numerical retry, extra start or enlarged budget was used.

Information, fitting and fixed calculations each ran in transient user unit
`issue212-restricted2.service`, with `Nice=10`. The unit owns Python and `tee`,
so a host-turn interruption cannot terminate their terminal process group.
Each wait used `while systemctl --user is-active --quiet issue212-restricted2;
do sleep 10; done`. No process was killed. Exact unit commands and invocation
identities are retained beside the results. Temporary `restricted-2/spec.json` and
`restricted-2/run` relative links selected the successful attempt for the
existing fixed-calculation producer. They were removed before notebook
validation; the retained results have one owner under `attempt-3/`. No
historical file was overwritten.

## Reproduction, measured computation and limits

The initial executed command records remain beside stage 2, stage 5 and the
three preceding joint fits. The continuation commands are
[the information command](restricted-2/attempt-3/information-command.json),
[the fit command](restricted-2/attempt-3/fit-command.json) and
[the fixed-calculation command](displays/unit-command.json). They use the pinned
wheel environment and `python -I`. New attempts require fresh output paths.
The joint fits used process workers with native BLAS/OpenMP threads at one;
the second restricted declaration retains 32 workers.

| Calculation | Runner wall seconds | Runner CPU seconds |
|---|---:|---:|
| Stage 2 | 4.385524814 | 8.112982 |
| Stage 5 | 0.142625518 | 0.140989 |
| A6, including information | 257.984296032 | 550.000186 |
| Hartono x₃, including information | 254.708852475 | 558.682329 |
| First restricted, including information | 245.751963953 | 500.790417 |
| Second restricted information | 216.648784395 | 214.269162 |
| Second restricted fit | 40.517488697 | 448.441814 |
| Fixed calculations | 31.752910501 | 31.667015 |

The bounded second-restricted information call itself used 216.428083553 s
wall and 213.861734 s CPU, within 300 s / 500 s; its fit call used
40.108540756 s wall and 447.866396 s CPU, within 600 s / 6000 s.
Runner times include their own setup; the sum of separate information and fit
runner times excludes launch overhead and time between the two units.

[summary.json](summary.json) records the numerical results and no current stop.
[validation.json](validation.json) checks completion, finite available rows,
requested tolerances, replay costs, the density rule, uncertainty assertions,
unchanged interrupted files and the unchanged selected record.
[provenance.json](provenance.json) records input/output and producer hashes,
commands, package versions and the notebook render. The complete change remains
**150 gross added executable lines** against `3f01bc1`, including comments and
blank lines, with no persistent tests. This continuation adds no executable
source lines.

The [analysis notebook](../../joint-recalibration/index.qmd#association-volume-210)
records these numerical-verification results, calibration statistics and fixed-model
comparisons. Its HTML is rendered only under `/tmp`; port 8770 and its preview
service are untouched. A table suffices for the declared scalar checks; this
issue does not produce model curves. The separate density-free issue owns
cost and property acceptance limits, and the 162-state rebuild owns phase
stability. The selected record and manuscript are unchanged. Independent
delivered review and promotion for manuscript use remain open.
