# #152 source-corrected fixed-record handoff

## Engineering result

The fresh amended campaign accounts for all355 requested states:352 evaluated,
three explicitly **not evaluated: outside declared reaction domain**. No result
from the stopped `corrected-wave/` generation was spliced. All352 evaluated
states meet the existing tolerance and balance gates; maximum absolute
stationarity5.115907697472721e−13; zero balance failures. This is internal
fixed-record evidence, not a refit, parameter adoption, validation or publication
snapshot. The source/data library still does not admit regression execution.

### #147 strict fitting base

83 states/141 targets =47 pressure+94 species. `vle_obs_0148` at60.106°C remains
report-only above333.15K. The exact source-corrected baseline gives:

| Family | Fixed-record cost | Approved1.10× preservation limit |
|---|---:|---:|
| Pressure | 8.251867051143167 | 9.077053756257484 |
| Species | 24.848444130706152 | 27.33328854377677 |
| Total, descriptive only | 33.10031118184932 | Not a combined pass condition |

Use separate family limits, not the OLD48-pressure cost. The exact target
export is `accepted-wave/strict141-targets.csv`, SHA256
`b2c63743258e949d33eed367d5cdd733968a36ed960ef52fb6fe919d51953e4a`.
`accepted-wave/147-handoff.json` binds costs, limits, parameter/wheel, source,
operator and compressed/content packet hashes. #147 owns recording/read-back
of the amended inputs and its later parameter decision; no GitHub write or
admission change was made here.

### 21-row80°C benchmark

Old AARD20.27025699294711%; corrected AARD20.270256992946948%: both display
**20.270257%**. Exact IDs, observed pressures and temperatures match. Maximum
feed reconstruction difference8.881784197001252e−16mol; maximum relative
prediction difference1.3100631690576847e−13. These are floating-point-level
reconstruction differences, not altered source quantities. Use the actual
corrected full-precision benchmark from the handoff. ID-level observations,
feeds and predictions are in `accepted-wave/benchmark80-id-reconciliation.csv`.

### Three outside-domain rows — preserved, not solved

| Observation ID | Xu Table1 source row | Measured°C | Measured K |
|---|---:|---:|---:|
| vle_obs_0286 |22|120.4|393.54999999999995|
| vle_obs_0287 |23|121.0|394.15|
| vle_obs_0288 |24|121.8|394.95|

Status: **not evaluated: outside declared reaction domain**. Native diagnostic:
`ParameterError: reference_unavailable: reaction R2 temperature outside reaction correlation`.
The pre-dispatch classifier reads the unchanged record's declared reaction
domains (293.15–393.15K). It does not catch solver failures, clip temperatures,
widen domains or remove source rows. Any other outside-domain target/comparison
stops. The three statuses are retained in `accepted-wave/not-evaluated.json`;
canonical requested162 =159 evaluated+3 statuses. High-T requested57 =54
in-domain evaluated+3 statuses. Xu requested18 =15 evaluated+3 statuses;
assessment metrics explicitly distinguish these populations.

Owner amendment2026-10-01 supersedes the earlier stop disposition. It also
requires #147's **final** record reaction domains to cover395.0K so its final
suite evaluates all19 Xu rows. That later qualification is not performed here.

## OLD→new evidence and other comparisons

OLD84/142 replay remains successful: pressure8.14345313051485,
species24.848444130706277, total32.991897261221126; reference difference
−7.105427357601002e−15. All142 prediction comparisons pass. Maximum stationarity
3.979039320256561e−13 and no balance failures.

Corrected142 internal source-effect diagnostic: pressure8.519447990702538,
species24.848444130706152, total33.36789212140869. It is not the strict141 fit.
The identity-matched OLD strict141 pressure cost was7.886627431943632, so the
corrected strict pressure change is+0.36523961919953507. Species change is
−1.2434497875801753e−13 (floating-point level). Source corrections are not
selected for a better fit.

- `old-to-new-targets.csv`:142 ID-level observations/predictions/T/costs/roles.
- `old-to-new-summary.csv`:142/141 family costs and21-row benchmark changes.
- `assessment-metrics.csv`:current in-domain source/cohort scores with explicit
  retained outside-domain counts; no full-Xu AARD fabricated.
- Aronu transfer15wt%33 rows:75.94764009221944% AARD;45wt%37 rows:
  45.90148912022073%. Corrected Aronu loading row99 remains source-faithful.
- Böttinger80°C w=0.31, six states/11 targets:11.848031576410587% AARD.
- Matin bicarbonate pool18 report targets:59.81349181429435% AARD, unchanged
  unverified legacy20°C/feed/observations; state016 display-only.
- `jakobsen-comparisons.csv`:ten comparisons/nine summary rows; nine ratios
  span0.42332177384401587–1.3255619073659304. Printed `maxload` and existing
  seeded-loading interpolation are disclosed; dilution/loading definitions
  remain unresolved. No alternate-loading sweep or new solve was introduced.

## Passing source/admission checks

VLE327 canonical/162 active/Hilliard31; speciation639 canonical/1138 membership
rows;68 context-only2-OXA without native coefficients. Amundsen213 property
rows/103 density rows/10 pure-MEA endpoints; loaded row uncertainties unbound.
All128 analogs non-admissible. Public source-verifying views pass; execution
remains refused. Stale split hashes and original immutable Gate0 source pins
refuse corrected data. Second source/property/volumetric/admission/NEW-packet
regeneration is byte-identical across139 files.

Native construction-only tests preserve measured temperature and recover
Hilliard/Xu analytical molality within relative1e−12; missing molality/contract,
nominal-only temperature and double seed are refused. Seven focused tests pass,
including pre-dispatch exclusion and protected-row stops without a solver call.

Arcis2011's entire source-status row, #147 calorimetry-admission rows, immutable
preregistration/guard, frozen numerical inputs and manuscript bytes remain
unchanged. No Zotero/corpus, manuscript/notebook/figure or GitHub writes.

## Identities, budgets and compute

Selected parameter SHA256:
`9055458d8b7cd767a0d08e9f37e4fd28631e29c363364d7b842ebade645cb241`.
Wheel SHA256:
`28181e72e429c6e87fc6361082af1a7b21c8747e76bda65a1c30abb4a97402f2`.
OLD content SHA256:
`86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448`.
NEW content SHA256:
`02b9b331abe5911c4c3d5050c3f0cdfadbbb3d2dd98a618c751e96c2ade90fc7`.
NEW gzip file SHA256:
`3fca278be8790d58ab30e5474b2b3892c47225d8230ac40fd4f87c066e8eaf2d`.

Domain policy adds exactly12 executable lines; final executable total500/500,
tests140/150. No compressed runtime code or new solver/record. The owner
explicitly authorized using the remaining12 executable lines for this amendment.

Affinity0–11:12 workers, OMP/OpenBLAS/MKL1; one pool and fresh worker namespaces,
load1min≤pool size dispatch gate, per-state90s and cohort/wave deadlines retained.
Fresh wave80.38582715200027s wall; packet77.96957898598703, canonical
169.56047357298667, transfer63.844072105988744 worker-seconds. Jakobsen reuses
accepted-wave predictions through the existing interpolation, without extra
Engine solves. Historical OLD and stopped-wave compute remain separately
accounted; no caches were imported into this fresh generation.

## Remaining delivery boundary

Numerical #147 inputs above are delivered locally. Independent delivered review,
#147's corrected-input read-back, its parameter decision, final qualified suite
and one manuscript snapshot remain separate. Do not certify the old manuscript
or splice #152 results into that final suite. No automatic #120 closure.
Historical stopped evidence in `corrected-wave/` remains retained, but its stop
is superseded by the owner amendment and fresh `accepted-wave/` generation.
