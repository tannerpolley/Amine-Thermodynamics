# Published MEA models on common observations — issue 339

The exact common-data result is the 19 Ma'mun et al. (2005) Table 2 pressures
at 393.15 K and 30 mass% MEA. Current-record pressure AARD is **19.432074704%**,
against published **21.03%** (Baygi–Pahlavanzadeh PC-SAFT), **39.96%**
(Najafloo–Zarei SAFT-HR, reported pressure AAD%), and **13.5%** (Zhang eNRTL).
The first three
comparisons use observations not fitted in the corresponding ternary pressure
objective; Zhang fitted them. Najafloo's methods describe prediction but its
conclusion says ternary data determined parameters; this ambiguity remains.
These different data roles do not rank accuracy under identical assessment.

For this work, Baygi and Zhang, the deviation is 100/n times the sum of absolute
pressure errors divided by measured pressure. Najafloo Table 5 and §3.3 report
pressure AAD% without defining its averaging formula or denominator. Its
equivalence to the mean absolute relative deviation is inferred, not verified;
Eq. 2 defines the pure-component fitting objective, not this pressure metric.
Pressures in `matched-pressure-rows.csv` are Pa; the original
Ma'mun table and source CSV use kPa. All 19 source pressures, their order and
temperatures are checked, including two distinct observations at loading 0.3424.
Source loadings 0.155–0.4182 mol CO2/mol MEA map to 0.1549031–0.4181084 in the
retained analytical-feed calculation. This follows Part I's composition handling;
other authors' conversions and rounding are not independently reproduced.

`matched-score.json` binds the exact retained current-record predictions and
source rows by hash. They were evaluated with wheel 391dfe5d, SHA-256
0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b.
The comparison recalculates deviations only; it neither refits nor reruns an EOS.
`published-deviations.json` owns transcribed published source/property scores;
`property-tables.md` presents them without estimating missing subsets or counts.
Each entry separates observation role from parameter origin and prior data use
in its role note. Unresolved entries identify missing membership evidence;
Baygi’s combined binary entries retain fitted Cai and predicted Park–Lee
membership without inventing separate scores. Najafloo’s binary observations
were not fitted but informed retaining zero interaction (§3.2).
`source-research.json` records primary-source identities, methods, exact-match
verification and unresolved source detail. Missing fitted-parameter totals are
reported as unknown rather than inferred. No full paper text is published.

## Published 2026 model: cross-version qualification and diagnosis

The original record from MEA commit `7035362` has SHA-256
`868a501831b87e95dedf18ce40e9e7ac949f7c6a4aaf137f717cc493ecfcb7be`.
The complete translation has SHA-256
`be66f6cf9df77201a632d73a3c3e341f66ce7fc77b69c3d657288f4c1899a76b`.
`polley-2026-explicit-born.json` preserves the earlier two-field translation;
`polley-2026-explicit-defaults.json` is the complete translation used here.

Before filling, inspection of the pinned wheel's source at `391dfe5d`
(`engine/src/epcsaft/parameters.py` and
`engine/native/surface/parameter_builder.cpp`, required-field checks and cross
association check) found exactly these three missing required declarations.
The nine components have their required scalar or temperature-law inputs;
all 29 consumed unlike dispersion pairs are explicit, while seven same-sign
ion pairs are excluded by the declared model. Water's diameter is a correlation.
The only site-bearing component pair without an edge is CO2–MEA.

| Declaration | Filled value | Original Engine source locator | Paper locator |
|---|---|---|---|
| electrolyte `c_shell` | 1, dimensionless | `f2d1e01f4:engine/native/contributions/born.hpp`; MEA `7035362:analyses/mea_parameter_bundle/scripts/shared_evaluation.py:MODEL_RUNTIME_DEFAULTS` supplies 1 | Appendix B p.17, extension coefficients; Eqs.122–123 |
| electrolyte `c_dielectric` | 1, dimensionless | Same Born implementation and MEA caller as above | Appendix B p.17, extension coefficients; Eqs.122–123 |
| `topology.no_cross_association`, CO2–MEA | all cross site edges inactive, native value 0 | `f2d1e01f4:engine/native/surface/parameter_builder.cpp:161,297–298,425–426`; reference Engine `443a9da4`, lines 165,342–343,481–482 | Appendix B p.17 and Table 10: only listed pairs active; no CO2–MEA pair |

The Born values are explicit MEA caller inputs, not silent Engine defaults.
The historical Engine initializes the association matrix to zero and activates
only declared edges and combining rules. The new declaration preserves that
behavior. The paper PDF (Zotero attachment `QHI67GZ8`) was checked directly;
its SHA-256 remains `c3d35ca54f7f4ac54727d790f18e6c4a90e271bb3f01d5a4d146b85755489459`.
Appendix B, Tables 7–10, Eqs.122–126 and the parameter-provenance paragraphs
were read. No disagreement was found. `translation-table.json` retains the
full table, hashes and source-file hashes; `appendix-check.json` owns the prior
ion, pair and reaction-value checks.

### Exact-record reference and first difference

The retained `qualification-reference.csv` is reused, not regenerated. Its 371
`adopted` rows name the original `868a5018…` record and wheel SHA-256
`b66c7b962541a586f5ec50043a5e8b4e62cf52e24eaec02ef33f43e558762a58`.
MEA commit `8d6e261` first retained these values through
`analyses/mea_parameter_bundle/calibration-misfit/compare.py`, consuming the
read-only adopted `probe.py` evaluations. The shared evaluator in that commit
identifies Engine `443a9da492fd5ac7724525945d108c6a2a854d51`.
The original packet was retrieved from that same commit. Its decompressed
SHA-256 is `86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448`;
the reference CSV SHA-256 is
`8242648f41c087d1a9acf810b3f9e35c21bbb021bad20ace38968a31ac8a9916`.
No historical wheel was built or run for this continuation.

### Full cross-version comparison, owner decision 2026-11-13

The former $10^{-8}$ relative-output limit is superseded openly. It assumed
identical equations across Engine versions and has no valid origin for this
comparison. Both versions name `EQUILIBRIUM_ROW_RESIDUAL = 1e-10`:
`443a9da4:engine/native/core/numerical_policy.hpp:272–277` and
`391dfe5d:engine/native/core/numerical_policy.hpp:295–300`.
This is the dimensionless classified equation-row infinity norm, not a relative
pressure or composition error bound. The caller supplies this same tolerance
in `shared_evaluation.py:279`. The policy did not loosen between commits.
The newer `MIXTURE_FORWARD_ERROR = 1e-7` at the latter file's line 339 is a
refinement target for relative pressure, log density, **absolute** mole fractions
and feed-scaled amounts; it cannot be used as one relative-output limit here.

All 371 adopted reference rows from MEA commit `8d6e261` were evaluated with
translated record `be66f6cf…` on the pinned `391dfe5d` wheel, using the original
packet and canonical CSV from that same MEA commit. Of these, **362** have
historical values: **239 pressures and 123 species quantities**. Nine historical
values are blank (`non_evaluable`): one pressure and eight species targets.
The pinned wheel returned values for all 371, but the nine blanks have no
relative difference and are excluded from distribution statistics. The retained
`qualification-all-rows.csv` contains every row; `qualification-canonical-inputs.csv`
retains the additional original pressure inputs. Signed difference is
$(q_{391dfe5d}/q_{443a9da4})-1$; reported maxima and medians use its absolute value.

| Quantity | Comparable n | Max absolute relative difference | Median absolute relative difference | Sign (new − historical) |
|---|---:|---:|---:|---|
| HCO3- | 23 | 3.6865179709e-07 | 2.9666346957e-07 | 23 positive / 0 negative |
| MEA | 18 | 1.1066876238e-07 | 2.5842215590e-09 | 0 positive / 18 negative |
| MEA + MEAH+ | 23 | 5.3243650155e-08 | 9.3614960228e-09 | 23 positive / 0 negative |
| MEACOO- | 41 | 1.4203497167e-07 | 6.2631123843e-08 | 0 positive / 41 negative |
| MEAH+ | 18 | 7.4604015632e-08 | 6.4684448575e-08 | 18 positive / 0 negative |
| co2-partial-pressure | 239 | 3.0491072822e-07 | 2.5672845194e-07 | 0 positive / 239 negative |

Signs are uniform within each quantity. Magnitudes vary with composition and
quantity; they are not a constant offset or randomly alternating signs.
Pressure magnitudes span 1.2941315664e-7–3.0491072822e-7. The overall maximum,
3.6865179709e-7, is `Matin2012_state_001::HCO3-` (historical 0.0015561964247065652,
new 0.0015561969984011737). These are numerical cross-version differences,
not deviations from experiment or propagated measurement uncertainties.

The explicit owner rule stops scoring when a relative difference exceeds the
named tolerance. The owner subsequently clarified that 1e-10 remains only a
solver-residual tolerance and required restoration of the old finite reference
on all 362 comparable rows before scoring. No Part I group has yet been scored.

### Bounded reference diagnosis

Historical `443a9da4:engine/native/properties/infinite_dilution_reference.cpp:318–352`
uses the last finite reference contraction; `engine/native/core/numerical_policy.hpp:191–194`
sets its witness molality to 1e-14 mol/kg. Engine commit **3b893fc2c** replaces
this finite-dilution calculation with analytic solvent insertion. The old code
itself describes a square-root ionic-strength bias at that finite molality.
The new implementation is documented in `391dfe5d:engine/docs/science/algorithms.md`
in its reference-calculation section.

A disposable read-only probe on the pinned wheel evaluated that finite composition
using the original neutral solute ratios (including their 0.125 scale), at each
reaction's reference pressure and 313.15 K. It compared the finite contraction
with the normal analytic-reference diagnostic, then added that difference to
the source log-equilibrium constant for this one isothermal solve. This restores
the old reference numerically without editing the Engine or retained producer.
`reference-limit-probe.json` retains the five contraction differences and pressure.
R1/R2 changes are about -2.257755e-7 and R3 about -4.515509e-7 in dimensionless
log-equilibrium units; R4/R5 differences are roundoff. The restored pressure is
4.394811538110804 Pa, versus historical 4.394811538107617 Pa, about 7.25e-13 relative.
This identifies the reference change as the cause at the first state; the owner
requires its confirmation over every comparable row before scoring.

### All-row finite-reference check: stop before Part I scoring

The owner required the same disposable finite-reference probe on all **362**
comparable rows, with reproduction to roundoff, about $10^{-12}$ relative,
before scoring. The probe completed with 362 returned values. Median absolute
relative difference is **2.7255975255e-13**, and maximum is
**2.7081559217e-11**. **341 rows** are within $10^{-12}$;
**21** exceed it. The largest is `canonical:vle_obs_0171`,
CO2 partial pressure: historical **1228.0644953749538 Pa**, restored finite
reference **1228.0644953416959 Pa**. The signed difference is
$-2.7081559217\times10^{-11}$ relative (about $-3.33\times10^{-8}$ Pa).

`qualification-finite-reference-rows.csv` retains all 362 comparisons;
`qualification-finite-reference-summary.json` records the distribution, first
row above $10^{-12}$, input method and disposable-script hash. The calculation
used one worker in an `agent-heavy` background shell with numerical-library
threads set to one, reusing the historical packet and canonical CSV. For each
state it evaluated the finite reference at each reaction's reference pressure,
subtracted the analytic contraction and added that difference to the source
log-equilibrium coefficient. Pressure-dependent corrections were evaluated at
the normal analytic endpoint. The pinned wheel then solved that isothermal
state with the restored finite reference. No Engine source changed; no
historical wheel was run. Probe code and caches are disposable and excluded
from the retained implementation, as the owner requested.

The finite-reference change explains the leading cross-version difference and
reduces the maximum to 2.71e-11, but **not every row reproduces near 1e-12**.
The remaining discrepancy has not been isolated between historical solver
termination, arithmetic and other Engine changes. The owner's explicit stop
therefore applies. No Part I observation group was scored; no heat or
heat-capacity difference or 162-state stability result is claimed. The original
analytic cross-version maximum remains 3.6865179709e-7 (pressures 3.0491072822e-7),
with uniform signs by quantity and nine blank historical reference values.
Both Engine solver residual tolerances remain 1e-10; neither this tolerance
nor the old 1e-8 output limit is asserted as a cross-version error bound.

This is numerical verification and a bounded diagnosis, not physical validation
or a parameter-adoption decision. No manuscript promotion is requested here.
The earlier Supported review covered only the earlier translation and stop;
this continuation's independent delivered review returned **Supported** at
`e3fdf0f`, with no required defects (`part1-review.md`). The normal replay's maximum
classified row residual is 5.1159076975e-13, below its 1e-10 solver tolerance.
Executable additions total 177/200 from base 13bb6fbb (144 previously used).
Notebook HTML rendered from retained numbers; home-page refresh still fails
because `snakemake` is unavailable. Protected site metadata was not changed.

## Reproduction and scope

Run each command in an `agent-heavy` background shell:

```
uv run --no-project --python <pinned-environment-python> analyses/mea_parameter_bundle/scripts/same_data_comparison.py
uv run --no-project --python <pinned-environment-python> analyses/mea_parameter_bundle/scripts/same_data_comparison.py tables
```

The first command reproduces the full translation and evaluates every retained reference row;
the second rebuilds the matched score and property tables from retained values.
There is no process pool; evaluation uses a single worker with BLAS/OpenMP
threads set to one. The script reuses the existing MEA evaluator and does not
implement thermodynamic equations. Base for the 200-line gross executable budget:
13bb6fbb7aebfb2ca642e6061f6f32f9167d6f35.

These are fixed-parameter model-to-measurement deviations, not uncertainty
intervals or independent physical validation. Published aggregate values retain
each author's data processing. Source uncertainties are not converted into
agreement thresholds, and source selection differences are not approximated.
The Hong model belongs to #246; #341 owns any later adopted-record replay.
Manuscript promotion requires the owner's confirmation of a reviewed notebook.
