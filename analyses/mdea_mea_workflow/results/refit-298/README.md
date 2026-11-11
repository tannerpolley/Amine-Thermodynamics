# Issue 298: historical-wheel confirmation stops refitting

The historical d5138209 wheel does **not** reproduce either retained fitted
cost. No fit was started, as required by the owner's resume instruction.
The wheel change alone cannot explain the discrepancy; its cause remains
unresolved. This is numerical verification evidence, with no physical
transfer-penalty or pressure-recovery conclusion.

| Record | Historical retained cost | d5138209 replay, 280 rows | 391dfe5d replay, 280 rows |
|---|---:|---:|---:|
| A3, single-sphere cation | 403.71498514705206 | 403.72944037107754 | 403.72944037066316 |
| B1, charged-molecule cation | 374.45201342397434 | 374.44674128851324 | 374.4467412886684 |

For A3 and B1 respectively, the old-wheel relative cost differences from the
retained values are 3.58055176481e-5 and 1.40796023845e-5. Maximum relative
prediction differences are 2.76249490445e-5 and 2.73222348882e-5; maximum
absolute weighted-residual differences are 0.00136131949642 and
0.00136131949630. All exceed the applicable 1e-8 confirmation tolerance.
Every old-wheel prediction was available and met its requested tolerance.

The old- and new-wheel predictions agree within 5.88e-12 relative for A3 and
2.59e-12 for B1. Their absolute cost differences are 4.14e-10 and 1.55e-10.
The earlier new-wheel discrepancy from retained predictions was localized to
heat capacity, with the largest difference at Weiland row 35 (30 wt% MDEA,
loading 0.50, 298.15 K, 101325 Pa). These results do not identify whether the
remaining discrepancy arises from application declarations, historical
producer behavior or another unverified difference.

The historical wheel was installed in a throwaway virtual environment in
`/tmp/mdea-298-old-wheel/venv`, never imported from Engine source. Its SHA-256
is `ca7093ca721fdc80226c74d018a582f31705684c6995e80b0492c193334dd5d5`.
Installed package and native-library bytes were checked against that wheel.
The interpreter was Python 3.13.14, with NumPy 2.4.4 and SciPy 1.17.1.
The identical A3/B1 endpoint documents and existing capped objective were
used; endpoint and row-result hashes are retained in `F1.json`.

The [owner amendment](https://github.com/tannerpolley/Amine-Thermodynamics/issues/298#issuecomment-6804381312)
authorizes same-wheel baselines and excludes Kuranov source rows 28 and 72
(393.17 and 393.16 K) from both baselines and refits. Future comparisons must
therefore use the same 278 rows. The adopted R2 domain remains
293.15–393.15 K. No 278-row run was started after the failed historical-wheel
confirmation. The 280-row values above confirm provenance and are not the
approved 278-row fitting baselines. The earlier fixed-substitution replays
retain their original 278/280 availability and have no complete fitted cost.

- `F1.json`: historical-wheel confirmation, cross-wheel differences and owner amendment.
- `F1-fitted-replays.json`: earlier 391dfe5d qualification statistics, preserved.
- `{A3,B1}-historical/old-wheel-fitted-replay.json`: all 280 old-wheel row predictions per record.
- `logs/old-wheel-confirmation-command.txt`: exact executed scratch calculation.
- `logs/old-wheel-confirmation.log`: completed historical-wheel replay output.
- `identity.json`: earlier checked 391dfe5d wheel, adopted/shared inputs and source identities.
- `disposition.json`: F1–F5 and all four unstarted fits.

F2 pressure recovery and the older 24.2% Ermatchkov criterion remain
unassessed. F3 group preservation and outside-fit heat availability, including
B1 at 333.15 K / 60 wt%, remain unassessed. F4 phase, rank and equal-cost
checks remain unassessed. F5 has no admissible endpoint because no fit was
attempted. No new fitted parameters, MDEA pressure AARDs or frozen selection
exist. No parameter adoption or downstream export occurred.

The historical readers changed in the earlier attempt remain unchanged in
this continuation. The adopted R2 declaration, Engine pin and manuscript
files are unchanged. No Engine source was edited. Independent delivered
review remains with the orchestrator; this evidence is not promoted for
manuscript or absorber use. A table is sufficient for this scalar numerical
confirmation; it does not describe a physical trend.
