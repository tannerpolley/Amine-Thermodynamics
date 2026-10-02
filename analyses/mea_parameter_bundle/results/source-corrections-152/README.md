# #152 source corrections — stopped fixed-record evaluation

## Engineering result and limit

The historical fixed-record qualification reproduces all 84 states/142 targets:
pressure cost 8.14345313051485, species cost 24.848444130706277, total
32.991897261221126. Difference from the replay reference is −7.105427357601002e−15;
all 142 row prediction comparisons pass (relative 1e−8, species floor 1e−12).
Maximum stationarity is 3.979039320256561e−13; no balance failures.

The corrected campaign is **incomplete and stopped**, not an accepted #147
baseline or publication result. Its coordinator retained 195 evaluated records
and one non-evaluable record before stopping. The failed state is
`canonical:vle_obs_0286`, Xu2011 Table1 source row22, measured120.4°C,
molality6.86 mol/kgwater, loading0.314 molCO2/molMEA, pCO2=50kPa.
The native diagnostic is:

> ParameterError: reference_unavailable: reaction R2 temperature outside reaction correlation

The final request uses393.54999999999995K (120.4+273.15). The unchanged selected
record's R2 candidate domain ends at393.15K (120°C). This is a declared
reaction-correlation domain conflict, **not evidence of solver divergence or a
bad physical model**. No source temperature was rounded back, record/domain
changed, row dropped, retry attempted, or tolerance/method altered. The faithful
source correction is retained. Xu source rows23/24 also report121.0/121.8°C;
their record-domain conflict follows from the same unchanged bound, but they
were not rerun or claimed as evaluated.

`corrected-wave/stop.json` contains failed/pending identities. Worker caches
retain additional completed/in-flight evidence but are not promoted into a
complete merge. No strict141 family-cost/1.10×limit or21-row benchmark handoff
is accepted; transfer and Jakobsen comparisons are incomplete. No numerical
agreement/improvement, parameter adoption, validation, or absorber-use claim
is made. Publication remains deferred to #147 selection and one winning suite.

## Passing non-numerical evidence

- VLE327 canonical/162 active; Hilliard31 active. Source row42
  (`vle_obs_0148`,60.106°C) remains outside the strict333.15K fit ceiling.
- Speciation639 canonical/1138 membership rows;68 context-only2-OXA records,
  no2-OXA native coefficients; Matin state016 non-target-eligible. Matin packet
  feed/20°C/observed values remain unverified legacy values, not source corrections.
- Amundsen213 property rows/103 density rows;10 pure-MEA endpoints. Loaded
  row uncertainties remain unbound. All128 analog rows remain non-admissible.
- Public source-verifying loaders pass for both retained roles. Execution is
  still refused; stale split hashes are refused; original immutable Gate0
  source pins correctly refuse corrected data.
- A second source/property/volumetric/admission/NEW-packet generation is
  byte-identical across139 checked files (`determinism-check.json`).
- Actual native Problem construction (no solve) preserves measured Hilliard/Xu
  temperature and recovers analytical-feed molality within relative1e−12.
  Missing molality/contract, nominal-only temperature and double seed are refused.
- Six focused tests pass (`tests/test_source_corrections_152.py`). Initial guard
  test expected the word “hash”; the guard actually reports a SHA-based source
  artifact drift. The owner approved correcting only that expected-message
  regex; no guard/checksum/tolerance changed.
- Arcis2011's entire source-status row, #147 calorimetry-admission manifest,
  immutable preregistration/guard, frozen numerical inputs and manuscript bytes
  are preserved. No Zotero/corpus, manuscript/notebook/figure or GitHub write.

## Numerical identities and compute

Selected parameter SHA256:
`9055458d8b7cd767a0d08e9f37e4fd28631e29c363364d7b842ebade645cb241`.
Historical wheel SHA256:
`28181e72e429c6e87fc6361082af1a7b21c8747e76bda65a1c30abb4a97402f2`.
All18 installed distribution file hashes were verified; no Engine checkout import.
OLD content SHA256:
`86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448`.
NEW content SHA256:
`02b9b331abe5911c4c3d5050c3f0cdfadbbb3d2dd98a618c751e96c2ade90fc7`.

Affinity0–11 gave12 workers, each OMP/OpenBLAS/MKL1. OLD launch load1min3.1699.
The owner confirmed #147 had no competing pool. Corrected dispatch monitored
load≤pool size; one pool covered packet/canonical/transfer requests, each with
its own worker-second ceiling. No nested pools. The stopped coordinator
terminated its worker process groups; no corrected wave was retried.

Gross additions against76ea465:488 executable lines (source/property189,
feed/native/packet110, admission/validators139, scheduling50),118 test lines.
The live issue body changed only to record the two approved budget amendments
(total500/source200/admission140); other scientific constraints remain unchanged.

## Remaining decision

The exact source/record-domain conflict must be resolved through an explicitly
accepted design/qualification boundary before further calculations. Extending
R2's domain changes the frozen record/hash; dropping/rounding the Xu rows changes
the accepted source/cohort basis. Neither is authorized by #152. Do not silently
resume or splice partial results. Preserve the OLD successful qualification,
corrected source facts and failed request while obtaining the bounded amendment.
Independent delivered review, complete numerical handoff and #147's corrected
input read-back remain pending. No #120 issue closure or external publication
has been performed.
