# Issue #151: completed pre-#152 pipeline verification

**Pipeline verification on pre-#152 data; method development, not manuscript values.**

The five retained evaluations, decomposition, C1/C2, prescribed falsifiers, CSV exports, Born-contribution-to-Q table and pressure-decomposition figure complete. No refit, physics/bound/tolerance change, Engine repair, notebook edit or manuscript promotion occurred. The owner requires #152 corrected inputs → #147 final parameter decision → one final evidence suite → one notebook/manuscript snapshot. These development values must not enter that snapshot.

## Accepted diagnosis and C2 correction

At `vle_obs_0139`, 313.15 K and 8011.150875 Pa, the MEAH⁺–water k intervention has a mechanically stable liquid root at **53038.339141 mol/m³**, below the local adopted-anchor window lower bound **53050.830669 mol/m³**. The Newton candidate left the caller's window; the root did not disappear. Original anchors failed **14/27** pending cases; the documented unanchored liquid route succeeded **27/27**, agreeing with 20-step native continuation within **1.67e−9 mol/m³**. Positive pressure slope establishes local mechanical stability only, not chemical stability or coexistence. Full ignored diagnosis: `runs/c2-root-diagnosis/README.md`. Historical failure: `c2-density-failure.json` and commit `48a4e8a`.

All three C2 call sites (baseline, individual, joint) consistently use `state(T, P=P, x=x, phase='liquid')` without anchors. No downstream solver, retry or tolerance relaxation was introduced. All 48 current pressure states now complete. Exact-zero controls apply to actual unchanged coordinates and the slope move at its actual reference temperature; empty control sets are guarded. Current tested offsets are exactly zero.

## Numerical checks

All checks pass. Errors are dimensionless ln quantities, except the cost checks.

| Check | Maximum absolute error | Tolerance | Evaluations |
|---|---:|---:|---:|
| N1 | 9.379164112e−13 | 1e−8 | 3 |
| N2 | 2.131628207e−14 | 1e−12 | 16510 |
| N3 | 2.374003088e−6 | 1e−5 | 1651 |
| N4 | 3.186414688e−9 | 1e−5 | 1651 |
| N5 | 8.068568036e−11 | 1e−6 | 3 |
| N5a | 4.706183105e−7 | 1e−6 | 420 |
| N6 | 4.606379024e−7 | 1e−6 | 2 |
| N7 | 3.410605132e−13 | 1e−10 | 168 |
| N7-off | 0 | 1e−10 | 504 |
| N8 absolute | 2.376557098e−7 | 1e−6 | 240 |
| N8 differences | 1.287945084e−8 | 1e−6 | 192 |
| N9 | 1.778346437e−6 | 1e−5 | 25 |
| C2-zero | 0 | 0 | 48 |
| Pressure-cost reproduction | 7.105427358e−15 | 1e−8 | 1 |

N2 tests both perturbation scalar errors together per species; its counter is not the number of individual scalars. N9 retains both estimates and all differences for five sentinels per record. N5 compares closure at each **actual** temperature, never at rounded nominal temperature. N1 rechecks the retained evaluator costs against accepted references 32.991897261221126, 34.584032061137975 and 98.79141626677485. Byte-identical state JSONL files and evaluation hashes bind those costs to consumed states.

Coverage: **420 solved states**, **240 record-pressure states**, **192 compared pairs**, **253344 long-format rows**. No unavailable state, missing comparison or undefined phi. The three primary records contribute all 84 states; two no-refit records contribute the 48 pressure states to long-format exports. Temperature cohorts contain 32/16 pressure states, split into loading thirds 11/11/10 and 6/5/5.

N6 salt-free 30 wt% MEA–water at 313.15 K versus pure water:

| Ion | Adopted Born ln gamma* | Original Born ln gamma* |
|---|---:|---:|
| MEAH⁺ | −0.145297157218 | 0.419167213786 |
| MEACOO⁻ | −0.144975423885 | 0.418239046524 |
| H₃O⁺ | −0.421484539362 | 1.215939137427 |

These checks verify model-internal calculations, not physical validation.

## Pipeline-check hypotheses

H1, nominal 313.15 K population (32 states per record):

| Record | Outcome | Median G Born OV | G Born OV at median-loading state | G perm OV at same state |
|---|---|---:|---:|---:|
| Adopted | Rejected | −0.897934520 | −0.878964659 | −0.287366254 |
| Original | Rejected | −0.456148093 | −0.420915212 | −0.420915212 |

The lower-middle loading state is `vle_obs_0188` in both records. Both reject the prescribed positive-transfer criterion on the negative median. This does not say Born is unnecessary.

| Record | Nominal T, K | H2 outcome | Spearman rho | Highest-third mean Q Born ion |
|---|---:|---|---:|---:|
| Adopted | 313.15 | Supported | −1 | −1.752319325 |
| Adopted | 333.15 | Supported | −1 | −1.760662945 |
| Original | 313.15 | Supported | −1 | −1.130885404 |
| Original | 333.15 | Supported | −1 | −1.156359899 |

C is **not rejected**: RMS ΔS = **0.849736472193**, RMS ΔQ = **1.122734957879**, over all 48 states. Pressure cost increases by **54.874400992448**, reproducing the retained difference to 7.105e−15. Missing-state and undefined-phi counts are zero. This inequality does not uniquely allocate deterioration, because S, Q and H can reinforce or cancel. The criteria are prescribed engineering thresholds, not significance tests.

## Retained Born-contribution-to-Q table

Dimensionless values; loading is mol CO₂/mol MEA. Tr/Ion and Perm/Shell are two separate decompositions of total. Nominal temperature is a grouping label.

| T, K | Third | Loading range | Record | Total | Tr | Ion | Perm | Shell | Mean phi |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|
| 313.15 | 1 | 0.088702–0.271905 | Adopted | −0.727703 | −0.175032 | −0.552670 | 0.144570 | −0.872273 | 0.991026 |
| 313.15 | 1 | 0.088702–0.271905 | Original | 0.207909 | 0.544674 | −0.336765 | 0.207909 | 0 | 0.480206 |
| 313.15 | 2 | 0.325907–0.465909 | Adopted | −1.245372 | −0.070192 | −1.175180 | −0.347390 | −0.897982 | 0.386454 |
| 313.15 | 2 | 0.325907–0.465909 | Original | −0.505525 | 0.239633 | −0.745157 | −0.505525 | 0 | −0.175440 |
| 313.15 | 3 | 0.473409–0.641913 | Adopted | −1.766015 | −0.013696 | −1.752319 | −0.760066 | −1.005950 | 0.064109 |
| 313.15 | 3 | 0.473409–0.641913 | Original | −1.077964 | 0.052921 | −1.130885 | −1.077964 | 0 | 0.023509 |
| 333.15 | 1 | 0.056301–0.290906 | Adopted | −0.595092 | −0.176318 | −0.418774 | 0.213287 | −0.808379 | 1.443250 |
| 333.15 | 1 | 0.056301–0.290906 | Original | 0.313882 | 0.565288 | −0.251406 | 0.313882 | 0 | 0.152388 |
| 333.15 | 2 | 0.385908–0.503910 | Adopted | −1.315908 | −0.040559 | −1.275350 | −0.459274 | −0.856634 | 0.256713 |
| 333.15 | 2 | 0.385908–0.503910 | Original | −0.660907 | 0.156254 | −0.817161 | −0.660907 | 0 | −0.092804 |
| 333.15 | 3 | 0.543911–0.667913 | Adopted | −1.773039 | −0.012376 | −1.760663 | −0.781300 | −0.991739 | −0.045360 |
| 333.15 | 3 | 0.543911–0.667913 | Original | −1.118090 | 0.038270 | −1.156360 | −1.118090 | 0 | −0.046888 |

## Pressure-decomposition figure by loading third

The figure plots discrete calculated states, not these means or interpolated curves. The ±0.3 band is one pressure-residual scale, not uncertainty. Means for Born-off refit versus adopted:

| T, K | Third | Δln p refit | Born removal | Dispersion | Other activity | ΔS | ΔH | Δln p no refit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 313.15 | 1 | −0.022092 | 0.727703 | −0.869070 | 0.180623 | −0.061338 | −0.000009 | 0.734646 |
| 313.15 | 2 | 0.589102 | 1.245372 | −0.939884 | 0.472034 | −0.188514 | 0.000095 | 1.288867 |
| 313.15 | 3 | 0.497045 | 1.766015 | −0.973231 | 0.880096 | −1.176446 | 0.000610 | 1.886492 |
| 333.15 | 1 | −0.245416 | 0.595092 | −0.955081 | 0.186178 | −0.071585 | −0.000020 | 0.599763 |
| 333.15 | 2 | 0.494678 | 1.315908 | −1.077479 | 0.757826 | −0.502057 | 0.000480 | 1.383601 |
| 333.15 | 3 | 0.142573 | 1.773039 | −1.141640 | 1.230584 | −1.719898 | 0.000489 | 1.747562 |

## C2 fixed-composition offsets by loading third

Coordinate order: 0 = carbamate–water k; 1 = MEAH⁺–water k; 2 = bicarbonate–water k; 3 = MEAH⁺–carbamate k; 4 = MEAH⁺–water reciprocal-temperature slope. Density independently resolved at fixed pressure with the consistent unanchored liquid route.

| T, K | Third | Born removal | Coord 0 | Coord 1 | Coord 2 | Coord 3 | Coord 4 | Joint | Remainder |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 313.15 | 1 | 0.727703 | 0.828675 | −1.282029 | 0 | −0.248268 | 0 | −0.679323 | 0.022300 |
| 313.15 | 2 | 1.245372 | 0.127180 | −0.164182 | 0 | −0.537111 | 0 | −0.517659 | 0.056453 |
| 313.15 | 3 | 1.766015 | −0.190911 | 0.664701 | 0 | −0.731125 | 0 | −0.170138 | 0.087195 |
| 333.15 | 1 | 0.595092 | 0.883056 | −1.365206 | 0 | −0.187339 | −0.111858 | −0.762459 | 0.018887 |
| 333.15 | 2 | 1.315908 | −0.034911 | 0.127484 | 0 | −0.573440 | 0.014155 | −0.396816 | 0.069897 |
| 333.15 | 3 | 1.773039 | −0.116355 | 0.665483 | 0 | −0.692855 | 0.060789 | 0.009170 | 0.092107 |

## Model-internal meaning and limits

On pre-correction inputs, the retained Born-off refit does not recover the negative, loading-dependent Born contribution to Q. Adopted mean phi decreases strongly across loading thirds. Realized refit shifts in dispersion and speciation partly cancel positive Born removal and other-activity shifts. C2 separates frozen-composition coordinate responses and their nonadditive remainder; C1 includes re-equilibration. Neither proves a unique physical mechanism, global impossibility of compensation, necessity of a Born subterm, applicability outside the calibrated domain or absorber suitability. The local literature shelf is absent; no new literature-backed claim is made.

## Final-generation consumer contract

`ACTIVITY_INPUTS=/absolute/fresh-manifest.json` selects explicit inputs. `ACTIVITY_OUTPUT=/absolute/fresh-output-directory` selects a separate evidence directory; create it before running. Code imports resolve from the script, not this directory. Run `calculate NAME RECORD ...` with all manifest record pairs. Rendering reads only retained CSVs in the selected output directory. The notebook remains untouched until the final rerun.

The manifest supplies `packet`, `records`, `states`, `evaluation_paths`, `sha256`, `state_ids`, `target_ids`, `state_count`, `target_count`, `cohorts`, `N1_expected_costs`, `N6_by_record_sha256`, `c2_reference_temperature_K` and `status`. Mask and hash assertions support 84/142 development or **83/141 corrected** populations. Corrected data require 47 pressure +94 species targets, excluding report-only `vle_obs_0148`. `cohorts` must cover exactly selected pressure-state IDs with nominal 313.15/333.15 K labels derived from retained source/series identities. All EOS and correlation calls retain actual measured temperatures; never round them to form cohorts or force slope zeros.

N6 expectations are independently derived and keyed to the exact selected record hash, not chosen by a shell-switch heuristic; an unfamiliar record without expectations fails. N1 and pressure-cost reproduction read the same explicit pinned evaluation paths. Supply newly evaluated states/evaluations, selected cost/reference values, immutable wheel/source hashes and a fresh manifest. Do not reuse development caches as final evidence.

Structural smoke testing on retained development IDs verifies that dropping `vle_obs_0148` yields 83 states/141 objective targets, including 47 pressure targets. This is **not** corrected-data numerical evidence. A relocated-output negative test successfully imported the code and verified provenance, then failed at the intended missing-record-arguments assertion before any EOS state call. Evidence is retained under `runs/final-mask-smoke.json` and `runs/relocated-output-smoke.json`.

**Shared-owner prerequisite:** `p1` currently imports `born_form_diagnosis.py`, which loads legacy defaults and asserts 84 observations before this consumer reads its manifest. The existing owner must reconcile 83-state selection, packet path, wheel verification and import-time provenance before the corrected suite. No shared driver or distribution metadata was edited here. Consumer readiness is conditional on that interface and #152/#147 decisions; no final 83/141 numerical run has occurred.

## Execution, accounting and review

Source is **380/380 gross added executable lines** from base `76ea465`; no existing executable driver changed. The affinity-sized process pool has 12 workers (CPUs 0–11), each single-threaded with OMP/OpenBLAS/MKL limits of 1. Parent checks returned perturbation errors. Final calculation monitored one-minute load every 0.2 s and would terminate the process group above pool size; maximum observed **4.657715 <12**. External timeout 1800 s, kill-after 5 s, address-space ceiling 2 GiB per process.

The initial successful development calculation used 71.79 s wall/146.23 s CPU. Independent implementation review found two path defects (cost provenance and relocated code import); both were corrected before the exact final source was rerun: **64.57 s wall/138.37 s CPU**, maximum RSS 656460 KiB. Rendering used **3.36 s wall/3.14 s CPU**, RSS 207396 KiB, timeout 300 s. New numerical/render total: **139.72 s wall/287.74 s CPU**. Earlier evaluator/diagnosis costs are historical; earlier CPU measurement was incomplete. The five evaluations were reused byte-identically. Import/setup/metadata/QA commands are outside these numerical totals. One metadata-generation stdin command failed with an unterminated-string SyntaxError before any writes; it did not invoke the Engine.

PDF visual QA confirms readable discrete-state panels, labels and residual band. All numerical/display outputs are labeled method development. Input parameter mappings remain immutable inputs, not new publication outputs. Historical stopped JSON is explicitly marked historical. The final read-only implementation review confirmed both findings resolved, matching source/output hashes, checks, hypothesis outcomes and C2 group means; no further consequential implementation defect was found. Its accounting-refresh housekeeping item is resolved by the final `change-accounting.json`. This implementation review is not the independent delivered scientific review needed before investigator promotion. No notebook edit/render, manuscript promotion, push, PR, tag or GitHub comment occurred.

Runtime wheel SHA-256: `28181e72e429c6e87fc6361082af1a7b21c8747e76bda65a1c30abb4a97402f2`; Engine commit `8c670d3aa9673459867154fa5c344c97526a7818`. The #141 interpreter is read-only; all analysis writes/source imports are from this #151 worktree. No Engine source import or distribution metadata change. Exact commands, input/output/source hashes, evaluator diagnostics and all sentinel estimates are retained in `execution-commands.json`, `inputs.json`, `checks.json` and ignored `runs/`.
