# Fixed-input swaps at the adopted MEA parameter vector

**Classification: inconclusive for attributing all five later-active bounds to one or two refreshes.** The CO₂–water interaction and bicarbonate reset cause the largest cost increases, while the dielectric change makes the largest change in the five-bound Gauss–Newton direction. Every current-definition R2 step points toward increasing its shift, away from the later lower bound. Local linear solves therefore do not establish the cause or location of the later nonlinear optimum.

**The CPU allowance was exceeded.** Aggregate evaluation CPU after all workers were reaped is 1493.824187 s. The complete conservative diagnosis charge is 1523.579561 CPU-s / 181.779298 active wall-s, exceeding 900 CPU-s by 623.579561 s; the 300-s active-wall allowance is met. Per-process CPU limits did not cap the pool total, and the assertion detected this only after completion. All numerical chunks had returned. No further native calculation was made; retained-array arithmetic produced this report. The run is not a budget-compliant execution.

## Basis and fixed-vector method

The owner authorized this diagnosis on 2026-10-16. Work starts at `a379f9631a264fb5659247df9ea13ba5d6cc2169` in the named existing worktree. The adopted record hash is `66ff7715958e9d22e77bd129faf7f67822204e3285b50993bf3f67d72c3b9778`. Engine is merged `84ca269dfa0c7068417a1c4c326acae276d4d965`, wheel SHA-256 `98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a`; all installed wheel files match. This is numerical verification and conditional assessment against calibration observations, without parameter estimation or physical validation.

Only the named fixed inputs are substituted. Fitted ion, interaction and chemistry values are retained, except item 7 explicitly resets its fitted bicarbonate–water coefficient from 0.5 to zero. Water replaces its pure coefficients, self-association and refreshed CO₂–water association edges; combining-rule edges consume the changed water inputs. The dielectric substitution replaces the entire permittivity declaration and removes its superseded coefficients, preserving all other fitted values. Source hashes, exact parameter documents, target definitions, predictions and all 14 exact columns are retained beside this file.

R4 is already a = 2.151, b_k = −1545.3 K, so item 5 reuses the identical baseline. Items 1–4, 6 and 7 differ. The CO₂ dispersion changes from 173.44025 to 169.21 K; bicarbonate–water changes from 0.5 to 0. The adopted record uses solvent-only permittivity; stage 5 changes to solvent-density-temperature with smaller MEA dV = 0.2464540312088979 L/mol and dT = 2436.4423007273617 K. Exact coefficient differences are in `inputs.json`.

The source-relative adopted coordinates are R2 shift -8201.884540544 J/mol, R5 shift 8418.523404172 J/mol and unshifted R5 a_k = 2597.910000000 K, at 313.15 K. All lie within the later Route 2 bounds. The stored effective R5 a_k = 3037.6399534696106 K includes its shift; it is not the unshifted boxed coordinate. Native columns are evaluated as increments about unchanged adopted chemistry, then expressed in the source-increasing Route 2 coordinates.

Cost is C = ½ rᵀr for declared weighted residuals. The exact native Jacobian is multiplied by square-root observation weights; coordinate scales are the unchanged Route 2 scales. Gradient is g = Jᵀr. The reported projected gradient is its infinity norm after removing outward cost-decreasing directions at active box sides. The Gauss–Newton step solves J δq = −r once by SVD least squares, cutoff 1e-14; no model reevaluation, iteration, line search, clipping or fitting follows. The source-increasing R5 column reverses native orientation.

## Costs and movement toward the later bounds

The five signed step entries below are toward bicarbonate–water upper, mutual carbamate–MEAH⁺ lower, carbamate diameter upper, MEAH⁺ Born upper and R2 shift lower, in that order. Positive means toward that later bound; negative means away. Units are dimensionless, dimensionless, Å, Å, kJ/mol. Steps are unconstrained local directions and often exceed the boxes by large factors. They are not feasible proposed parameter updates.

| Swap | Common-149 | Change | Training | Change | Projected gradient | Toward / 5 | Signed physical GN step |
|---|---:|---:|---:|---:|---:|---:|---|
| Adopted vector | 32.056685 | 0.000000 | 57.513699 | 0.000000 | 6.813177 | 2 | +4.182, -14.073, +2.420, -94.775, -112.454 |
| 3 CO₂–water pivot + slope | 109.868029 | 77.811344 | 135.613572 | 78.099874 | 154.366433 | 2 | +3.878, -9.813, +2.699, -86.007, -111.445 |
| 7 Bicarbonate–water = 0 | 89.683372 | 57.626687 | 110.821528 | 53.307829 | 67.775232 | 2 | +7.076, -12.284, +1.984, -56.952, -107.507 |
| 6 Smaller-dV dielectric | 58.713473 | 26.656789 | 82.210427 | 24.696728 | 82.536152 | 4 | +6.405, +3.984, +1.439, +39.508, -194.250 |
| 1 Water + association edges | 48.400908 | 16.344223 | 73.772761 | 16.259062 | 65.449040 | 2 | +4.205, -15.693, +2.402, -99.626, -115.216 |
| 4 CO₂ dispersion/k | 47.525795 | 15.469110 | 72.985908 | 15.472210 | 64.628188 | 2 | +4.204, -14.274, +2.352, -95.208, -111.976 |
| 2 MEA–water interaction | 34.671445 | 2.614760 | 59.675574 | 2.161875 | 30.788939 | 2 | +4.305, -13.963, +2.310, -91.736, -113.037 |
| 5 R4 source law (identical) | 32.056685 | 0.000000 | 57.513699 | 0.000000 | 6.813177 | 2 | +4.182, -14.073, +2.420, -94.775, -112.454 |
| 9 All fixed refreshes | 174.147317 | 142.090632 | 192.795270 | 135.281572 | 126.441455 | 4 | +7.763, +0.067, +1.512, +15.707, -172.684 |
| Old separate Jakobsen comparator | 32.056685 | 0.000000 | 73.198226 | 15.684527 | 5.167841 | 2 | -2.891, -21.752, +7.512, -225.053, +92.378 |

Changes above use the adopted vector on the current 166-row declaration. The final old-definition comparator has 168 rows and its change has the opposite orientation to the requested old → new target swap. For item 8, common-149 remains 32.056684909; old 168-row cost 73.198226007 becomes corrected pooled 166-row cost 57.513698694, a **decrease of 15.684527313**. Its projected-gradient norm changes from 5.167840900 to 6.813177071.

The adopted fit itself used 149 rows. Adding the current 17 rows raises its cost by 25.457013785: 18.328163043 pooled Jakobsen, 3.117048732 restored species and 4.011802011 Cp. That addition is distinct from pooling and correcting the previously declared eight Jakobsen targets. The 168-row comparator holds the other 160 rows and unit Jakobsen weights fixed, and preserves the old incorrect 022 feed; its full declaration is retained. It was never an adopted fit objective.

Cost-increase ranking for individual fixed swaps is **3 > 7 > 6 > 1 > 4 > 2 > 5**. Contributions are not additive: all-fixed training increases by 135.281571732, versus 189.997578303 for the sum of individual increases.

For comparing movement across unlike units, S is the sum of each signed five-bound physical step divided by that coordinate’s full box width. It is a transparent reporting projection, not a fit criterion. Relative to the unchanged current-166 baseline, ΔS ranks **dielectric +51.664547 > bicarbonate reset +16.528887 > CO₂–water +4.871931 > MEA–water +1.133224 > R4 0 > CO₂ energy −0.217121 > water −2.547325**. All-fixed ΔS = +44.227639. Corrected pooled targets versus old separate definitions give ΔS = +42.756630. The full signed vectors must accompany this scalar: R2 points away from its later lower bound for every current-definition variant.

## Training family breakdown

| Swap | Pressure 47 | Species 94 | Heat 8 | Restored 7 | Jakobsen 6 (old 8) | Cp 4 |
|---|---:|---:|---:|---:|---:|---:|
| Adopted vector | 8.380385 | 21.950482 | 1.725818 | 3.117049 | 18.328163 | 4.011802 |
| 3 CO₂–water pivot + slope | 64.432201 | 21.952194 | 23.483634 | 3.117125 | 18.379183 | 4.249237 |
| 7 Bicarbonate–water = 0 | 58.869829 | 29.204829 | 1.608713 | 3.992693 | 13.113379 | 4.032085 |
| 6 Smaller-dV dielectric | 36.853184 | 19.787309 | 2.072980 | 2.865789 | 16.382511 | 4.248653 |
| 1 Water + association edges | 24.603717 | 21.647159 | 2.150032 | 3.067831 | 18.921764 | 3.382258 |
| 4 CO₂ dispersion/k | 23.345948 | 21.950358 | 2.229490 | 3.117044 | 18.323712 | 4.019358 |
| 2 MEA–water interaction | 10.702150 | 22.290862 | 1.678433 | 3.176949 | 17.819804 | 4.007376 |
| 5 R4 source law (identical) | 8.380385 | 21.950482 | 1.725818 | 3.117049 | 18.328163 | 4.011802 |
| 9 All fixed refreshes | 125.061352 | 27.848819 | 21.237146 | 3.792313 | 11.841966 | 3.013674 |
| Old separate Jakobsen comparator | 8.380385 | 21.950482 | 1.725818 | 3.117049 | 34.012690 | 4.011802 |

## Gradients of the five later-active coordinates

These are source-increasing scaled-coordinate derivatives of current training cost. Negative favors an increase; positive favors a decrease. Divide by 0.01, 0.01, 0.1 Å, 0.1 Å and 2500 J/mol respectively for physical-unit derivatives. All 14 gradients and steps for both objectives are in `coordinate-gradients-and-steps.csv`.

| Swap | Bicarbonate–water | Mutual ions | Carbamate size | MEAH⁺ Born | R2 shift |
|---|---:|---:|---:|---:|---:|
| Adopted vector | +0.047820573 | +0.094438452 | -0.520561326 | -0.157767151 | +0.099333180 |
| 3 CO₂–water pivot + slope | +1.316315655 | -2.400594920 | +2.304010009 | -4.533594806 | -11.723029166 |
| 7 Bicarbonate–water = 0 | -2.048677272 | +0.550136958 | -4.283440552 | +3.239004829 | -2.574968380 |
| 6 Smaller-dV dielectric | -1.170225935 | +1.567319173 | -0.491573351 | +1.418871329 | -3.708419486 |
| 1 Water + association edges | -0.388435712 | +1.336908274 | -1.800585987 | +1.747652102 | -0.621165847 |
| 4 CO₂ dispersion/k | -0.631149362 | +1.302399234 | -1.674348923 | +2.004750331 | -0.585264337 |
| 2 MEA–water interaction | +0.088535521 | -0.361401931 | -0.364997501 | -0.696392549 | +0.043696553 |
| 5 R4 source law (identical) | +0.047820573 | +0.094438452 | -0.520561326 | -0.157767151 | +0.099333180 |
| 9 All fixed refreshes | -2.830955557 | +1.639758428 | -1.922257770 | +2.505267641 | -19.155685252 |
| Old separate Jakobsen comparator | +0.207737374 | +0.168410107 | -0.225230104 | -0.084323920 | +0.099333433 |

## Top contributing targets

The next table ranks increases in per-target cost against the adopted vector on the same current declaration; it isolates the damage attributable to each fixed swap. `P0191`, for example, means `vle_obs_0191-pco2`. `summary.json` also gives the three largest absolute costs for every variant.

| Swap | Largest three increases in target cost |
|---|---|
| 3 CO₂–water pivot + slope | Vinjarapu Table 4 row 02 +6.474565; Vinjarapu Table 4 row 01 +5.542635; P0193 +4.549742 |
| 7 Bicarbonate–water = 0 | P0191 +7.384360; P0200 +6.755138; P0192 +5.647775 |
| 6 Smaller-dV dielectric | P0200 +2.879497; P0191 +2.242038; P0189 +2.123563 |
| 1 Water + association edges | P0194 +1.376240; P0186 +1.351670; P0197 +1.251108 |
| 4 CO₂ dispersion/k | P0197 +1.284303; P0200 +1.215884; P0191 +1.054894 |
| 2 MEA–water interaction | P0132 +0.382013; P0131 +0.355702; P0122 +0.294846 |
| 9 All fixed refreshes | P0200 +13.343748; P0191 +11.246879; P0202 +10.334832 |
| 5 R4 | Identical; every target-cost change is zero. |
| 8 Target definitions | Grouping the old two inorganic numerators: 022 pool cost decreases 11.092565; 011 pool decreases 3.634252; 022 carbamate decreases 0.923398. Definitions and the 022 feed change together in this comparison. |

The corrected target-only vector’s three largest absolute costs are Jakobsen 022 inorganic pool 8.581666012, Jakobsen 011 MEAH⁺ ratio 6.382255230 and Matin 017 MEA 2.378233687. These are also item 5’s top three absolute contributions.

## Numerical coverage, failures and limits

Every current-definition case returns all 166 rows; the old comparator returns all 168, with all 14 exact columns and zero returned solve failures. Every weighted Jacobian has rank 14. Training condition numbers span 7387.469–20170.431. The largest normal-equation residual of a one-step solve is 2.34e-11. The adopted common-149 cost reproduces 32.056684908725686, and maximum weighted residual difference from the qualified unchanged replay is 2.06e-11, below its retained 1e-8 limit.

Two command failures are retained. The first declaration assembly left old constant-permittivity coefficients in the new dielectric declaration; removing superseded coefficients corrected that inert assembly. The second command returned every chunk, reaped the pool, and then failed its CPU assertion. Neither is a returned thermodynamic row failure. The latter is a real allowance violation.

No measurement-uncertainty propagation or physical validation is performed. Conditioning, very large unconstrained steps, non-additive input effects and opposing R2 directions prevent inference of the constrained nonlinear optimum from this point. The original adopted fit released fewer than these 14 coordinates, so its full-14 gradient need not vanish. The absent literature shelf is recorded; no new paper-validity judgment is made. Existing declarations and retained precursor/R4 diagnoses supply the source basis. Independent delivered review and any notebook promotion remain with the parent.

## Options for the parent, without selection

- Retain the adopted CO₂–water interaction or bicarbonate–water coefficient in a new declared comparison. This removes the two largest isolated cost increases, but relinquishes the corresponding refreshed fixed value and requires an explicit consistency decision with its earlier estimation stage.
- Re-estimate the influential binary, dielectric or bicarbonate inputs jointly with reactive quantities. This may resolve compensation, but changes the free set and identification problem; it requires a new design and authority, with no fit authorized by this diagnosis.
- Revisit source and target bases before choosing fixed values: CO₂–water law, dielectric temperature dependence and the Jakobsen preparation/pooling conventions. This can distinguish incompatible input assumptions from compensation, but the present cost ranking alone does not establish that any source is wrong.

## Resources, files and delivery

The authorized stdlib pool has 32 processes, each at nice 10 and single-thread BLAS/OpenMP. Measured per-process peak RSS is 72,433,664 bytes; free memory before the pool is 18,116,419,584 bytes; the sizing rule reserves twice measured RSS per process. No native fitting worker interface is used. Native exact evaluation remains serial inside each host process. All workers are reaped before aggregate CPU is recorded.

The initial failed command is conservatively charged 14.580000 CPU-s / 14.600000 s; the evaluation command 1493.870000 CPU-s / 152.120000 s; reduction 0.129561 CPU-s / 0.059298 s; preparation/reporting/verification/commit reserve 15 CPU-s / 15 active wall-s. This reserve includes this report and is not charged twice. Total 1523.579561 CPU-s / 181.779298 active wall-s; cumulative program 23523.323519 CPU-s / at least 3327.228996 s. Earlier unmetered overhead remains unknown.

Production executable additions: **0**; campaign remains **812/900**. Diagnostic scripts are inert `.py.txt` files, counted separately: `evaluate.py.txt` 230 total lines (200 statement lines), `reduce.py.txt` 122 total lines (94 statement lines), `report.py.txt` 117 total lines (63 statement lines). They preserve the actual failed aggregate-limit approach for inspection; `evaluate.py.txt` must not be rerun under this exhausted diagnosis allowance.

`ranking.csv`, `family-costs.csv`, `target-costs.csv`, `coordinate-gradients-and-steps.csv`, parameter documents and exact matrices retain the numerical evidence. `verification.json` and `timing-and-program-accounting.json` retain checks and charges. Route 2’s README now attributes retaining the partial to the orchestrator and records the owner’s later diagnosis authorization. No fit, production-path change, notebook edit, service action, subagent, push, merge or GitHub write occurs.
