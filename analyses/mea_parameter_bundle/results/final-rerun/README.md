# Issue 154: corrected-data final evidence

**F1 (SSM+DS) is the selected calibrated record.** On the corrected 141-target base,
its pressure/species costs are 8.438701621598156 / 24.595072621944944. F3's
Born-off refit increases pressure cost by 53.17344870743889 within the same
bounds. This establishes a tested bounded-refit comparison, not physical
necessity of Born or unique physical ion values. Independent delivered review
is pending; manuscript refresh and promotion are separate.

## Fits and numerical evidence

Exactly twelve optimizer runs converged (F1–F6, two starts each). F1–F5 and
their conditional-error/correlation tables are retained unchanged from
`6ad13e1`; no refit was made. `v1-start-parameters.json` is an exact byte copy of the
original selected record at `6ad13e1`, SHA-256 `9055458d…`. The dispatcher now
points at that immutable copy so F1 adoption cannot alter its v1 starts; this
binding-only change was not followed by any fit. The original two F6 jobs stopped before optimizer
invocation because continuation was not feed-normalized. The owner-authorized
continuation used `temperature-reanchor-140/assessment.py::feed_start` for the
two planned starts only, without changing feed, temperatures, observations or
reaction systems. Earlier stops are retained in `F6-{A,B}/pre-optimizer-stop.json`
and `diagnosis.json` (the latter describes the initial, now resolved stop).

`fit-summary.json` contains both starts, exact coordinates, active bounds,
source AARDs, start agreement and independent replay. Selected starts are
F1-B, F2-A, F3-B, F4-B, F5-A and F6-A. The largest relative start-cost difference
is 7.203e-13, below 1e-6. The largest relative replay-cost difference is
9.438e-13, below 1e-8. All selected replay states pass stationarity, element,
charge and declared-domain checks.

| Fit | Pressure cost | Species cost | Total cost |
|---|---:|---:|---:|
| F1 | 8.438702 | 24.595073 | 33.033774 |
| F2 | 11.241012 | 22.900686 | 34.141698 |
| F3 | 61.612150 | 35.026459 | 96.638609 |
| F4 | 10.309525 | 37.317323 | 47.626848 |
| F5 | 11.621034 | 28.077576 | 39.698610 |
| F6 | 8.478968 | 24.579969 | 33.058937 |

The base is 83 states / 141 targets: 47 pressure, 94 species. F4/F5 add the exact
18 Matin pool targets, giving 159 targets. Costs with different target counts
are not used to reselect Born form. Pressure residuals use ln-ratio / 0.3;
species use (prediction-observation)/(0.1*observation+0.001). Costs are half the
sum of squared residuals. `fit-targets.csv` and `fit-aard-by-source-species.csv`
retain the original ten runs; `f6-fit-targets.csv` and
`f6-aard-by-source-species.csv` retain the two completed F6 runs.

## Conditional uncertainty and adoption

`conditional-standard-errors.csv`, `conditional-correlations.csv` and
`conditional-uncertainty.json` remain byte-identical to `6ad13e1`. F1/F2 interior
ranks are 4/4 and 3/3; covariance conditions on each actual active-bound set,
uses physical-unit Jacobian columns and variance 2*cost/(141-p). Interaction
and slope optimizer scales are 0.01 and 10 K. Bound coordinates have no
symmetric interval. Residual independence is assumed despite shared-titration
dependence; errors are conditional and indicative only.

**F1's MEAH+-water reciprocal-temperature slope remains -112.6 K,
conditional SE 119.7 K.** It has not been changed or removed. Replaying residuals
against the retained Jacobians changes SEs by at most 1.40e-14 relative and
correlations by 2.22e-16 (`uncertainty-replay-checks.json`); no Jacobian was
refitted or newly evaluated.

`F1-parameters.json` and `../selected-current-best-parameters.json` have SHA-256
`ae92bac5d2ef7ab690e692f6b1686e18cf06f24ac6b53a6aab4fafeb3046f1aa`.
All model inputs equal the replayed F1-B optimizer export; only description and
document identity changed. `selected-record.json` records that equality and
optimizer/export hashes. The existing #152 selected-record hash assertion in
`tests/test_source_corrections_152.py` was updated in the same adoption commit,
`7fb4643`; no new guard was added. Historical #123 density defaults stay frozen;
#154 explicitly binds record, hash and output to its new comparisons rather
than comparing new parameters with old optimum-specific numerical values.

## Outside-fit and mechanism results

`evaluation/` uses #152's existing `probe.py`, `compare.py` and
`shared_evaluation.py`, with new fixed-record bindings. F6 uses only #140
`assessment.py` scoring, with its exact native reaction inputs. No #140 freeze,
stage selection or structure fitting is invoked. 1,374 state records and twelve
loaded-density comparisons are retained. All required in-domain states are
finite and numerically available. Raw phases/evidence preserve the checks.

Canonical 80 C AARDs for F1/F2/F6 are 19.5827 / 20.0082 / 28.9142%; in-domain
100–120 C values are 27.2447 / 27.1264 / 51.0467%. These do not isolate reaction
laws: F6 changes reaction laws, CO2 epsilon/k and refitted interactions together.
Both F1 and F6 use the matched candidate-extrapolation domain 293.15–393.15 K;
R4's source range ends at 323.15 K. Xu rows 22–24 remain explicitly not evaluated
for F1/F2/F6 (`evaluation/not-evaluated.json`), not silently included in a
full-source score. `evaluation/scores.csv` retains source-resolved 40–80 C and
100–120 C scores, transfer, Wagner, Jou/Böttinger 80 C, and report-only Matin pools.

`evaluation/jakobsen-carbonate-share.csv` retains all ten rows, the existing
nine-row summary mask, printed-maxload ambiguity and existing seeded-feed
1e-4 alignment disclosure. Loaded density remains a limit: F1 overpredicts
four 30 wt% loaded rows by 13.0030–17.7988%, on a CO2-free solvent basis at assumed
101325 Pa; the source does not report numerical pressure. Loaded-row uncertainty
scope remains unbound; raw deviations are not uncertainty-weighted qualification.

`activity-contributions/inputs.json` binds final F1 as `adopted`, F3 as
`off-refit`, corrected state files/masks/cohorts/replay costs and SHA-256s,
including N6's unchanged Born-input reference at F1's final hash. The unchanged
#151 owner reports N1–N9, N5a, N7-off, N8-differences, C2-zero and pressure-cost
reproduction all passed. RMS activity-sum/speciation shifts are
1.0943235793344641 / 0.8193240639722424. H1 is rejected; H2 supported; C not rejected
under the unchanged local rules. `checks.json` retains all errors and outcomes.

Four main-text data groups are `figure-data/pressure.csv`, `speciation.csv`,
`born-off-mechanism.csv` (with `born-activity-sums.csv` companion), and
`pool-effect.csv` (with `pool-effect-costs.csv` companion). They are discrete
retained evaluations, not inferred continuous curves. CSV input hashes are
retained. The mechanism PNG and its input hash are under `figures/`.

## Compute, retained-output refresh and limits

Both fit dispatches used a 12-worker pool sized to CPU affinity, single-threaded
workers and the unchanged 2400 s per-fit timeout; no nested pools. F1–F5 phase
wall time was 478.014251 s, completed F6 phase 239.046400 s (717.060651 s total
optimizer-dispatch wall time across the two authorized phases). Evaluation and
decomposition clocks and any accounting limits are recorded separately.
The fixed-record dispatcher took approximately 125 s (log birth-to-final-write,
second resolution; monotonic total lost at the summary exception); the final
hash-bound decomposition took approximately 35.7 s (filesystem timestamp
proxy). These are not benchmark measurements.

Gross executable additions are 536 lines (51 removed) against `f68e16f`, plus
one changed test line. This exceeds the 350-line advisory, not a scientific
acceptance rule. The added surface dispatches the existing owners and assembles
required evidence; no new admission/preregistration/guard module or Engine
equations were introduced. `change-accounting.json` separates retained outputs
from executable lines.

The verified immutable wheel is
`28181e72e429c6e87fc6361082af1a7b21c8747e76bda65a1c30abb4a97402f2`;
imports resolve to this worktree's installed site-packages, never Engine source.
Corrected packet content SHA-256 is
`02b9b331abe5911c4c3d5050c3f0cdfadbbb3d2dd98a618c751e96c2ade90fc7`.
`input-hashes.json` and `f6-input/input-hashes.json` preserve fit provenance.
The evaluation dispatcher completed solves but exited during summary serialization
because of duplicate `rows` fields in F6 metrics. Correcting that serialization
and running `final_evidence.py summarize` rebuilt tables from retained records;
no solve or fit was repeated to recover that presentation-stage error.

Rebuild retained tables with `uv run --no-project python
analyses/mea_parameter_bundle/scripts/final_evidence.py summarize`, then `present`
for figure data or `render` for the mechanism PNG. These modes read retained
results only; no optimizer or state evaluation is called. The notebook has one
new #154 section; ordinary HTML rendering has model execution disabled.

Supported use remains a calibrated model for 30 wt% MEA, pressure fitted at
40–60 C and species at 20–60 C. Matin remains source-unverified legacy input.
80 C and higher-temperature data also informed inherited reaction shifts and
are not independent temperature predictions. Wagner is absent from these fit
objectives, but earlier #140 outside-fit assessments are retained; no claim of
newly untouched data or independent physical validation is made. Ion values
are effective; active bounds, conditional uncertainty, transfer errors and
loaded-density bias remain limitations. No heat fit, Born-input refit,
parameter-removal fit, fixed-interaction scan, further reaction-law change,
new wheel, push, PR, issue write or manuscript edit was made.
