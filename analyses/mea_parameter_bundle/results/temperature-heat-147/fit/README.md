# Corrected campaign timing retained; heat denominator incomplete

The replacement timing job passed all 83 corrected pressure/species presolves and completed the 141-target no-heat value/Jacobian evaluation. It did not time the required heat objective: the branch labeled heat contains 141 rows instead of 149 because the driver selects `role_147 == 'calibration'`, whereas the eight frozen Vinjarapu rows use `heat_calibration`. The empty selection omitted every heat observation. Exit 0 does not establish required completeness. This is an application data-role selection defect, not a physical-model failure. No replacement numerical job or fit was started after its discovery.

The authorized one-line import repair adds the repository `src` directory. The prior eight files, including the failed producer, are byte-identical under `previous-e814b92/`; the original archived checksum list and reports are retained unchanged. The current `timing.py` contains only that one-line repair; its heat selection is left at the demonstrated stopping point. The complete live #147 body and all 22 comments were read and rechecked before this handoff; their captured content did not change. The corrected-input amendment and Ready verdict remain the governing data/design authority.

## Basis and numerical evidence

The calculation uses strict 141-target inputs (47 pressure and 94 species, 83 states at or below 333.15 K), frozen restored-source physical parameters `7e9e3f02…`, reactions `c1cb5c74…`, and qualified Engine `c1067020`, wheel SHA-256 `e8ad39e0c5d7da471a6d3ace6ff62d60518c57bc1c96fe5198d8bf18747ba8b5`. All installed wheel-file hashes match the retained identity. Inputs and all 250 earlier tracked records were checked byte-for-byte, allowing the authorized relocation of the earlier fit attempt. The untracked zero-carbon diagnosis directory remains untouched and untracked.

All 83 presolves passed requested convergence, material/charge conservation and stationarity. Maximum stationarity was 4.5474735e-13 (limit 1e-10); maximum absolute material error was 2.5224267e-13 mol and charge error 2.6858311e-14 mol (limits 1e-7 on the declared basis). Recorded state-evaluation time summed to 40.452183 s. All 141 no-heat predictions and five-direction gradients were available and finite. The repeated pressure/species-only evaluation in the mislabeled branch was also complete. At the prespecified all-zero start, both evaluations give pressure cost 114.72140872341997 and species cost 247.32198707625443, total 362.04339579967444. These are starting-point discrepancies, not fitted family costs or selected-record assessments.

## Measured timing and compute

| Evaluation | Actual / required rows | Full residual evaluation (s) | Full five-column Jacobian evaluation (s) | Mean residual / Jacobian per row (s) |
|---|---:|---:|---:|---:|
| No heat | 141 / 141 | 46.712029 | 61.243467 | 0.331291 / 0.434351 |
| Labeled heat; pressure/species only | 141 / 149 | 51.017640 | 63.697658 | 0.361827 / 0.451756 |

The eight Vinjarapu residual/Jacobian times are unavailable. The second row is not the full heat-branch timing. Timing variation between these identical objectives is not a heat cost.

The enclosing `agent-heavy --max 2G --timeout 1800s --wait 180` job took 504.30 s wall time; the driver clock recorded 495.183831 s after setup/import. User/system CPU including children was 415.50/5.91 s; maximum resident memory was 80,756 KiB (78.86 MiB). OMP, OpenBLAS and MKL threads were 1; execution was serial. Available affinity contained 12 CPUs; no pool was started. Charging full elapsed time conservatively to prior approximate 325.29 s gives **829.59 s used and 49,570.41 s remaining** of 50,400 s. The pre-job remainder was 50,074.71 s. No infrastructure failure occurred.

For the requested planning projection, assume the design's **40 native iterations**, with 40 full residual evaluations and 41 full Jacobian evaluations (initial plus one per iteration). Use the measured five-column cost also for the constant form; do not assume endpoint caching. This is a workload scenario, not proof of convergence, a hard runtime bound or a change to the native stopping rules.

- Four no-heat fits: 17,517.853 s; 4,379.463 s per fit at the assumed cap.
- Four nominal heat fits with the eight heat rows missing: 18,609.238 s; 4,652.310 s per fit.
- Eight-fit **incomplete projection**: 36,127.092 s (10.035 h), sequential wall time.
- Eight rescores, pressure/species values plus an 83-state check-time allowance: 714.536 s. Heat rescoring is missing from this number.
- Reserve all six assessment caps, covering both selected branches: 10,800 s.
- **Incomplete projected total: 47,641.628 s**, leaving only 1,928.782 s against the current 49,570.41 s remainder before the omitted heat work, a replacement timing job and remaining setup/phase checks.

Let `R_H` and `J_H` be the full residual and Jacobian seconds for the omitted eight Vinjarapu observations. The corresponding complete-work expression is **47,641.628 + 168 R_H + 164 J_H s**, plus replacement timing and remaining setup/phase checks. The residual coefficient includes four heat fits and heat rescoring of all eight fits, including the controls. Neither missing term is measured; a qualified full prediction is unavailable and the pre-fit timing gate has not passed. The 40-iteration no-heat projection alone exceeds the 2,400 s external / 2,250 s native fit caps: completion under those unchanged caps would require earlier convergence, which has not been established. No compute cap is silently enlarged.

## Measured remaining code and proposed amendment

The first formatted 88-line lower-bound draft is superseded by the **37-line unformatted baseline** requested by the parent. All measurements below use manually authored source in the existing timing/qualification style, including comments and blanks. No formatter count or deletion credit is used. The full documentary fragments and shared-setup diff are in `remaining-code-measurement.md`, and exact accounting is in `code-amendment-measurement.json`. Nothing there is installed or executed. These measurements are a concrete reuse candidate, not proof of an absolute mathematical minimum or a qualified implementation; result-field bindings and integrated call sites still need authorized Build and Review.

| Remaining piece | Measured gross additions |
|---|---:|
| Share timing setup and retained anchors; correct heat role and enforce the eight-row denominator | 44 (34 removals; no credit) |
| Eight-fit calls and §7 selection baseline | 37 |
| Export, reload and complete pressure/species/heat rescoring | 39 |
| Declared-scale identification, uncentered correlations and projected slope | 25 |
| §9.1 freeze writer | 15 |
| §9.2–9.3 in-domain assessment | 164 |
| Common fit input and result bindings | 20 |
| Common paths and command dispatch | 15 |
| Common assessment bindings | 25 |
| Bounded jobs and invocation filter | 14 |
| **Remaining total** | **398** |

Assessment's 164 lines comprise 38 pressure/species/Wagner, 40 fixed-pressure calorimetry and endpoint/feed/phase checks, 46 independent heat and loading sensitivity, 28 limit reporting, and 12 source-unit mapping. Existing owners reused are `timing.py`, `low-temperature-fit.py` (`design`, source mapping, state checks, observation construction, save), `shared_evaluation.py` (request correction, problem construction, state evaluation, snapshots), `assessment.py` (Wagner construction, native domain transport, metrics), `verify_reference_calorics.py` and native `reg.fit`, `reg.predict`, and equilibrium calls. The old #140 fit driver cannot directly take the eight heat observations or current affine coordinate form; its old `rescore` fixes 142 targets and excludes heat, so direct invocation cannot meet this campaign. No optimizer, generic numerical library, chemistry equation or local caloric equation is proposed.

Actual current gross implementation is **566**: 485 historical + 80 original timing lines + 1 import repair. The measured candidate needs **964 total gross lines** (566 + 398). Proposed owner amendment: **691 → 970**, an increase of 279, preserving the earlier six-line headroom. Keep source/unit roles at 120 and historical qualification at 371; change fit integration/selection allocation **100 → 280** and assessment **100 → 199**. Fit allocation includes its existing 81 lines plus 199 remaining lines (sharing, fit/selection, rescore, identification, freeze, common fit/path bindings and four invocation/control lines); assessment has 199 remaining (164 assessment + 25 bindings + ten bounded-job lines). This is a proposal for the parent to take to the owner, not execution authority. The chemistry, eight-fit menu, bounds, starts, weights, criteria and compute caps are unchanged.

The shared setup measurement includes the role correction and explicit eight/149-row checks; applying it and restarting timing requires a separate parent/owner decision after this completeness stop. Generic mechanisms remain with the Engine. No ninth fit, new start, bound change, high-temperature calibration, adoption or notebook change is proposed.

## Fits, freeze and assessment left open

| Branch | Form | Start | Outcome |
|---|---|---:|---|
| No heat | Constant | 1 | Not started |
| No heat | Constant | 2 | Not started |
| No heat | Slope | 1 | Not started |
| No heat | Slope | 2 | Not started |
| Heat | Constant | 1 | Not started |
| Heat | Constant | 2 | Not started |
| Heat | Slope | 1 | Not started |
| Heat | Slope | 2 | Not started |

Every fit's family costs, parameters, active bounds and start agreement are unavailable. No branch selection, export/reload/rescore, selected-record identification or §9.1 freeze commit exists. The local retention commit is not a selected-record freeze. No loaded solve above 333.15 K was run. Vinjarapu residuals are unavailable.

| §9.3 requirement | Limit | Outcome |
|---|---|---|
| Numerical completeness | 83 states / 141 control / 149 heat targets plus all required assessment states; tolerance, material/charge at most 1e-7, stationarity at most 1e-10 | Presolves and 141-target control pass; heat denominator fails 141/149; required study incomplete |
| Pressure preservation | At most 9.077053756257484 | Selected primary unevaluated |
| Species preservation | At most 27.33328854377677 | Selected primary unevaluated |
| Vinjarapu calibration | Source-scale RMS at most 2, every loading-level absolute mean at most 2 | Unevaluated; no heat residuals |
| Arcis required 14 rows | Each 322.5 K group at 0.51/1.03 MPa: RMS and absolute mean at most 2 | Unevaluated |
| Mathonat 40/80 °C | Source-average absolute residual at most 2; last two finite-ε values within 0.1 kJ/mol at each 2/5/10 MPa | Unevaluated |
| Independent-heat improvement | Primary aggregate RMS at most matched control RMS | Unevaluated |
| Canonical 80 °C pressure | Complete 21-row AARD at most 20.270257% | Unevaluated |
| Identification | Start agreement; singular ratio at least 1e-8; all absolute uncentered correlations below 0.95 | Unevaluated |
| Selected slope | Full rank, interior slope, projected fraction above sqrt(1-0.95²) | Unevaluated |
| Effective interaction | k(T) below 1 at all required endpoints | Selected records unevaluated |

An unavailable selected-record value cannot be labeled as a physical pass or fail. The 80 °C species, separate Wagner cohort, 19-row diagnostic, required heat phases/feed roots and loading sensitivities remain unevaluated. Xu `vle_obs_0286`–`0288` and other outside-domain diagnostics remain unevaluated. No current parameters or notebook were changed, and no push, PR, issue edit, adoption or independent delivered review occurred.

Evidence type: **numerical verification** of the reported presolves and pressure/species prediction/gradient availability; declared-scale starting-point comparison. There is no new fitted **calibration** or selected-branch **conditional comparison**. This is not physical validation. Readiness and §8 qualification are inherited evidence with their original limits, not substitutes for this incomplete timing.
