# MEA association-volume refits on Engine 3e83e19c

**Stopped at the second restricted information calculation.** The stage-2
neutral fit, stage-5 reduction, A6 comparison, Hartono x₃ sensitivity and first
restricted fit completed their existing checks. The host turn interruption
terminated the second restricted information calculation before it returned
its native result or release checks. Its fit never started. No new reported
candidate, reported-candidate density decision or conditional uncertainty exists.
This is an execution interruption; it establishes no physical-model failure.

Authority: [issue #212](https://github.com/tannerpolley/Amine-Thermodynamics/issues/212),
based on main at `3f01bc1`. Every calculation uses the merged Engine commit
`3e83e19ccc771b51d8ebc038931ab25192f4c5b5`, wheel SHA-256
`0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`.
The MEA self-association volume is fixed at `0.036305439` throughout the
calculated mappings. The installed Engine files were verified byte for byte
against that wheel by `fit_campaign.verify`; Engine source was never imported.

## Fit and reduction results

Costs are dimensionless, one half of the sum of squared weighted residuals.
The three joint fits each retain all 307 available, finite objective rows.

| Calculation | Numerical completion | Iterations | Native final cost |
|---|---|---:|---:|
| Neutral MEA–water, start A | Converged, usable; all checks pass | 1 | 91.80963081696791 |
| Neutral MEA–water, start B | Converged, usable; all checks pass | 1 | 91.80963081698934 |
| Stage-5 reduction | 14 rows; rank 2; both roots pass | Direct calculation | 1.9338548589681683 |
| A6 comparison | Converged, usable; fresh information checks pass | 5 | 148.2115075904099 |
| Hartono x₃ sensitivity | Converged, usable; fresh information checks pass | 5 | 148.31366430715744 |
| First restricted fit | Converged, usable; fresh information checks pass | 4 | 149.21952645124134 |
| Second restricted fit | Information interrupted; fit not started | Unavailable | Unavailable |

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

The following subgroup costs are reductions of the retained native weighted
residuals. They are calibration statistics, not the unperformed fixed replays.

| Completed joint fit | 307-row native cost | 149-quantity native cost | Native Cai cost |
|---|---:|---:|---:|
| A6 comparison | 148.2115075904099 | 24.920645016885917 | 91.7776478432832 |
| Hartono x₃ sensitivity, its own composition basis | 148.31366430715744 | 24.91033009406157 | 91.77853317050315 |
| First restricted fit | 149.21952645124134 | 24.10250358939657 | 91.88937725031957 |
| New reported candidate | Unavailable | Unavailable | Unavailable |

## Parameter changes and prepared starts

The association volume changes by `+0.000018439` (+0.0508143412241%).
The selected neutral interaction changes from −0.0843938800264997 to
−0.08439986221195522: absolute change −0.00000598218545553, relative change
+0.0000708841145075 (the denominator is the signed preceding value).
The larger-branch dielectric volume changes by −0.000002237977358 L/mol
(−0.000306157534164%), and its temperature by +0.001648694910 K
(+0.000161782898013%). These are upstream inputs, not a new reported candidate.

[parameter-changes.csv](parameter-changes.csv) and
[parameter-changes.json](parameter-changes.json) retain every changed
coefficient against each preceding endpoint, including absolute and signed
relative changes. The JSON comparison is also retained beside each completed
joint fit. Values with a zero preceding denominator would have an unavailable
relative change rather than an invented ratio.

The joint starts preserve observations, scales, ties, controls and physical
bounds. Reaction bounds are rebuilt from the original unshifted boxes using
each endpoint's own inherited R2/R5 totals. A6 and x₃ carbamate segment
diameters move from 5.8 to 5.798 Å; the first restricted MEAH⁺ diameter moves
from 5.49 to 5.492 Å. Packing and Debye–Hückel ties are reapplied. Born
diameters and interactions are not moved. The three fresh information
calculations pass all 307 rows and both size-column checks.

The second restricted start is the **new** first restricted endpoint,
SHA-256 `d0af148a8db25760f541f6c702768d51c7b2e51a38b3a31691034216eccfb858`,
with its own chemistry file. Its inherited totals are R2 =
−1811.930108185226 J/mol and R5 = 10000 J/mol. The MEAH⁺ lower size bound
is 5.35 Å. Re-evaluating the inward rule gives no diameter move; this is
recorded in [restricted-2/preparation.json](restricted-2/preparation.json).

## Stop and unavailable downstream quantities

[restricted-2/stop.json](restricted-2/stop.json) retains the stopping point.
Five information evaluations are retained: the baseline and MEAH⁺ size
perturbations at ±0.01 and ±0.005 optimizer units. The last retained write
was at `2026-10-24T06:59:16.907935+00:00`, at least 109.4521 seconds after
the command record. Terminal wall and CPU measurements are unavailable because
the process was terminated externally. No calculation process remained on
resumption, so none was stopped by a command-line match or restarted.

The existing numerical-completion requirement cannot be met at this point.
No information retry, added start, altered bound, tolerance or enlarged budget
was used. The following remain uncalculated:

- The new reported candidate's 307-row, 149-quantity and Cai costs.
- Its loaded-density count within twice the assigned scale, miss IDs and
  largest CO₂-free density error. No density pass or failure is asserted.
- The fixed 307-row replays, reported permittivity, Cai calculation with the
  new constant interaction, Arcis heats and conditional uncertainty. The
  conditional rank and active set are unavailable; the historical rank-ten
  and active-set assertions were not reached and were not removed.

The stage-2 constant is retained for the later Cai-only calculation; there was
no duplicate Cai fit. No selected record or manuscript file was changed.
These completed fits provide numerical verification and calibration evidence
for their stated inputs. They establish neither independent physical
validation nor phase stability. The new reported candidate is absent, so no
adoption or downstream qualification follows. Scalar costs, completion states
and unavailable quantities answer the bounded stopping question; a plot would
not resolve the interrupted information calculation.

## Reproduction and measured computation

Run from the task checkout with the pinned environment:

```bash
nice -n 10 .venv/bin/python -I analyses/mea_parameter_bundle/scripts/association_volume_refit_chain.py stage2
nice -n 10 .venv/bin/python -I analyses/mea_parameter_bundle/scripts/association_volume_refit_chain.py stage5
nice -n 10 .venv/bin/python -I analyses/mea_parameter_bundle/scripts/association_volume_refit_chain.py a6
nice -n 10 .venv/bin/python -I analyses/mea_parameter_bundle/scripts/association_volume_refit_chain.py held-x3
nice -n 10 .venv/bin/python -I analyses/mea_parameter_bundle/scripts/association_volume_refit_chain.py restricted
nice -n 10 .venv/bin/python -I analyses/mea_parameter_bundle/scripts/association_volume_refit_chain.py restricted-2
```

These document the executed commands, not permission to retry the stopped
call. The three first joint calculations ran concurrently, with ten native
fit workers each on the 32-core host. Available physical memory was measured
when each declaration was prepared; the existing 256 MiB worker allowance
and the three concurrent calculations determined worker sizing. The second
restricted declaration requested 32 workers; its information calculation was
interrupted before fitting. Native BLAS/OpenMP threads remained at one.

| Completed command | Wall seconds | CPU seconds |
|---|---:|---:|
| Stage 2 | 4.385524814 | 8.112982 |
| Stage 5 | 0.142625518 | 0.140989 |
| A6, including information | 257.984296032 | 550.000186 |
| Hartono x₃, including information | 254.708852475 | 558.682329 |
| First restricted, including information | 245.751963953 | 500.790417 |

The per-fit `command.json`, `command-timing.json`, `spec.json`,
`information-spec.json`, `preparation.json`, `release/` and `run/` files retain
the declarations, start hashes, inherited chemistry, verified installed
Engine files, native results and timing. [summary.json](summary.json) is the
machine-readable account. [provenance.json](provenance.json) inventories input,
output and producer byte hashes and package versions. The initially executed
122-line producer is in commit `ff714da`; the 123-line joint producer is in
`95439c7`. The final producer also contains the unexecuted fixed-calculation
commands. The total change is **150 gross added executable lines** against
`3f01bc1`, including comments and blanks, with no persistent tests.

The [analysis notebook](../../joint-recalibration/index.qmd#association-volume-210)
records this partial numerical result. Its HTML is rendered only under `/tmp`;
the preview service is untouched. Independent delivered review and promotion
for manuscript use remain open.
