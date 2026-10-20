# #170 amendment 7, steps 1–3: fixed-vector study (no fit)

Owner decisions: [#170 comment 6283064075](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6283064075)
(route, strict phase gate, endpoint-only split rule, 5,100.38 s plan). Design:
`tmp/joint-design/amendment-7-phase-stable-density.md` §5. Wheel `d2f61e3a…0357`
(Engine main-21e761c3). Probe: `study.py.txt` (disclosed, outside campaign code).
Calls: `calls.json`, **251.57 wall-s / 250.86 CPU-s** of the 400 / 600 allocation,
charged 252 / 251 in `amendment-4/compute-ledger.json`. Readiness review r1
(GPT-6 Astra, Revise) findings 1–5 are corrected below.

Vectors are the Held A4 control moved toward the selected A6 vector by one path
fraction per block (A7-1 block by block); the uniform-fraction construction
reproduces the design's `path-0p125` and `path-0p25` documents exactly (asserted).
Blocks: MEAH⁺ size (segment, packing and DH diameters), ion dispersion energies
(MEAH⁺, carbamate), ion–water pairs (carbamate, MEAH⁺ and bicarbonate k with the
MEAH⁺ slope), MEA–water k and slope, R2 coefficients, R5 coefficients.

**Missing stability reports.** At some points the final state converged but the
stability evaluation raised `ParameterError: stability correction destroys
positive support` before any trial ran, so the point has no `stability` report.
This is Engine #664 (merged and closed on Engine main), separate from the failed
near-pure-0 trial optimizer of #660. Affected here: t = 0.1875 point 4; the
design's t = 0.125 point 1; both coupled vectors, points 1 and 4; the restricted
start, point 1. These are unresolved, incomplete screens, not zero-descent results.

## Results

**Step 1, onset bracket (all 73 points).**

| Path fraction t | Descent points | Lowest resolved $t_{plane}/(RT)$ | Classified failed / unresolved | Points without a stability report |
|---:|---|---:|---|---|
| 0.125 (design) | none recorded | — | 0 / 73 | 1 |
| **0.1875** | none recorded | — | 0 / 73 | 4 |
| **0.21875** | 70, 71, 72 | −1.34×10⁻⁴ | 3 / 70 | none |
| 0.25 (design) | 70, 71, 72 | −5.30×10⁻⁴ | 3 / 70 | none |

Detected onset lies between t = 0.1875 and 0.21875, at α = 0.5, 333.15 K. The
other unresolved points contain the known failed near-pure-0 trial optimizer (#660).

**Step 2, block exchanges at points 63/70/72.**

| Block | 0.125 with block at 0.25 | 0.25 with block at 0.125 |
|---|---|---|
| MEAH⁺ size | none | 70/72, −2.76×10⁻⁴ |
| ion energies | none | 70/72, −1.16×10⁻³ |
| **ion–water** | **70/72, −7.94×10⁻⁴** | **none** |
| MEA–water | none | 70/72, −5.30×10⁻⁴ |
| R2 | none | 70/72, −5.30×10⁻⁴ |
| R5 | none | 70/72, −5.29×10⁻⁴ |

At these backgrounds and points, the ion–water block alone switches the
detected descent on and off. Moving the ion energies toward A6 suppresses it
(reverting them deepens the descent); moving MEAH⁺ size toward A6 deepens it slightly.

**Step 3, coupled vectors (all 73 points, split-seeded attempts).** Both hold
ion–water, MEA–water, R2 and R5 at 0.125 and the ion energies at A6, changing
only the MEAH⁺ size fraction.

| Vector | MEAH⁺ σ, Å | Descent points | Lowest $t_{plane}/(RT)$ | Converged lower-Gibbs splits, $\Delta G/(RT)$, 333.15 K |
|---|---:|---|---:|---|
| `coupled-half-size-energies-at-selected` | 4.97768 | 63, 70, 71, 72 | −3.17×10⁻³ | 63 (α 0.4): −0.0271; 70/71/72 (α 0.5): −0.0917 / −0.0962 / −0.0962 |
| `coupled-size-energies-at-selected` | 4.15536 | 24, 33, 36, 45, 54, 62, 63, 70, 71, 72 | −5.77×10⁻² | 36 (α 0.2): −0.0561; 45 (α 0.256): −0.0427; 63 (α 0.4): −0.876; 70/71/72 (α 0.5): −1.34257 / −1.34246 / −1.34241 |

Twenty-three split-seeded attempts cover every distinct descending liquid
composition (max |Δx| > 10⁻⁶) at the fourteen descending points: one per point
(`split-summary.json`), then the nine remaining distinct compositions
(`split-summary-distinct.json`, `split-seeded-<point>-<seed>.json`). The
converged states have classified residuals below 8×10⁻¹⁴, positive amounts,
positive pressure–density derivatives and positive reduced-Hessian minima. The
full-size vector's points 24, 33, 54 and 62 remain rejected, unconfirmed descents:
their single distinct composition collapsed back to one phase (24, 54, 62) or
lost a phase (33). They are never passes.

**Scoring of the furthest path vector without recorded descent (t = 0.1875, 307 rows).**
Cost 467.63; loaded densities **0/47 within 2s** (max 41.78 s); CO₂-free max
|e| 0.995 kg/m³ (≤ 1.0); Cai 91.37 (≤ 95.90); C149 28.92 (≤ 35.26); pressure /
species AARD **18.21** / 7.13 % (pressure fails ≤ 15.81); Vinjarapu RMSE
1.84 kJ/mol. The reduction reproduces the retained A6 replay (cost 148.2377,
C149 24.9231, Cai 91.8115) on that replay's rows.

**First-order density contributions.** The selected endpoint's retained Jacobian
is `amendment-6/joint-mea-water/held/fit/native.json:$.physical_jacobian`. It is a
row-major 307 × 20 array of d(prediction)/d(physical parameter), checked against
`optimizer_jacobian` on the density rows. Multiplying it by each block's A4 → A6
change and dividing by $s_j$ gives these mean changes over the 47 loaded rows, in units of $s$:

| Block | Mean change |
|---|---:|
| MEAH⁺ size | +22.8 |
| Ion energies | −2.7 |
| Ion–water | +0.7 |
| ↳ carbamate–water k | +2.40 |
| ↳ MEAH⁺–water k | −1.36 |
| ↳ bicarbonate–water k | −0.33 |
| ↳ MEAH⁺–water slope | −0.01 |
| MEA–water | +0.04 |

R2/R5 were not linearized. The finite change along the path is +28.6, from a mean
of −28.49 at the Held A4 control to +0.07 at A6. These are local linear estimates;
no block's finite change was scored separately.

## Meaning and limits

With ion–water, MEA–water, R2 and R5 held at 0.125 and the ion energies held at
A6, the tested MEAH⁺ diameters 4.97768 and 4.15536 Å predict liquid splits.
Reducing the diameter between these two fixed backgrounds increases the
detected-descent count from four to ten. These calculations do not establish a
split-free diameter interval or the feasibility of a restricted refit. The
three-point exchange with σ = 5.389 Å also kept the energies at 0.125, so it is
not a matched no-descent baseline for those backgrounds. To first order, MEAH⁺
size carries most of the A4 → A6 density change. The MEAH⁺–water k change, which
controls the onset locally, slightly lowers loaded density.

No tested fixed vector combines the density gate with a complete phase pass.
The sampled path vector without recorded descent misses the density gate
substantially. Whether a refit within the approved bounds can satisfy both
requirements remains unresolved. A refit could move coordinates held fixed here:
carbamate size, Born diameters, carbamate–MEAH⁺ k and the energies. In A6,
carbamate size, both Born diameters and carbamate–MEAH⁺ k sit on their bounds.
Sampled vectors do not certify a box, and zero detected descent on 73 points is
not a stability proof. No physical phase-separation data exist for comparison;
the splits are model predictions with numerical verification.

**Step 4 outcome.** The owner chose a restricted feasibility fit (decision
recorded on #170), after a 24-point sub-block probe of the ion–water block
(points 63/70/72):

| Single coefficient | 0.125 with it at 0.25 | 0.25 with it at 0.125 |
|---|---|---|
| **MEAH⁺–water k** | **63/70/72, −4.13×10⁻³** | **none** |
| carbamate–water k | none | 63/70/72, −4.01×10⁻³ |
| bicarbonate–water k | none | 70/72, −7.04×10⁻⁴ |
| MEAH⁺–water slope | none | 70/72, −4.71×10⁻⁴ |

At these backgrounds and points, the MEAH⁺–water k change (−0.204 → +0.027,
weaker MEAH⁺ solvation) alone switches the onset on and off. The carbamate–water
change (−0.045 → −0.187, stronger carbamate solvation) suppresses it. To first
order the carbamate–water change also raises loaded density (+2.40 s mean, table
above), so it stays free.

**Bound proposal for the feasibility fit** (inside the existing boxes; all 16
coordinates retained; everything else unchanged):

| Coordinate | Existing box | Proposed box | Evidence |
|---|---|---|---|
| MEAH⁺ segment diameter (packing 0.88σ, DH σ tied) | [2, 5.8] Å | **[5.49, 5.8] Å** | t = 0.1875 (σ = 5.4916): no recorded descent on 72 points; point 4 has no stability report. σ = 4.978 with the energies at A6 splits. |
| MEAH⁺–water k | [−0.5, 0.5] | **[−0.5, −0.161]** | t = 0.1875 (k = −0.16101): as above. k = −0.14659 alone splits at 63/70/72. |

Start: the path t = 0.125 vector (MEAH⁺ σ 5.5944 Å, MEAH⁺–water k −0.17544;
both well inside), with the declared interior-start treatment for carbamate σ
(5.8 → 5.798 Å, ties reapplied) and its own 73-point screen before release.
These intervals are sampled evidence, not a certified split-free box; the
endpoint's 73-point family with split-seeded attempts for every distinct
descending composition remains the falsifier. Density may simply fail with the
size lever restricted.

## Restricted-fit declaration and start screen

Owner approval of the bounds and start: [#170 comment 6283335389](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6283335389).
`../inputs/build.py.txt` writes `restricted-{start,information,fit}.json` and
`build-check.json`, reusing the A6 follow-up helpers (`declarations`, `rebase`,
`held_sizes`, `check`); no solve.

- **Bounds:** the only coordinate-box changes from the selected A6 Held declaration are the
  two approved bounds and the R2/R5 boxes, rebased by the start's inherited totals.
  The inherited totals are R2 2806.69 J/mol and R5 3831.95 J/mol, with unshifted R5 aₖ 2463.35 K,
  linearly interpolated because both laws are affine in (unshifted aₖ, total shift)
  with the 313.15 K pivot. The rebased R5 aₖ box is [2600.16, 3200.16] K. The other
  declaration fields are identical apart from start, inputs, purpose, URLs, budget and release path.
- **Budget:** 1,200 wall-s / 7,000 CPU-s; fit 600 / 6,000 (+120 s guard); release 300 / 500.
  Program priors are read from the ledger at build time. A rebuild does not renew spent
  allocation: 1,162 wall-s / 6,962 CPU-s remain after the start screen.
- **Checks:** both declarations pass `verify`, the ties check, 16-coordinate construction and an
  identical binding (`f5d8bce3…ee58` on wheel `d2f61e3a…0357`).
- **Start screen:** no resolved descent was recorded. Of the 73 unresolved points, 72
  contain a failed near-pure-0 trial. Point 1 has no stability report because stability
  evaluation raised `ParameterError: stability correction destroys positive support`.
  This is an incomplete screen, not phase qualification. It took 37.21 wall-s /
  37.10 CPU-s, charged 38 / 38 against the restricted-fit allocation.

Strict-gate sequence: qualify the merged #660 wheel; rebuild with
`build.py.txt <wheel_path> <wheel_sha256>`, which rebinds the engine and refreshes the
ledger priors; re-screen the start on that wheel; then fresh release, the single
fit, cold replay and the endpoint's 73-point family with split-seeded attempts.
On that wheel, any point still lacking a stability report or a trial result is
retained and diagnosed before release, never counted as zero descent. Reject an
ineligible endpoint before downstream comparisons; otherwise complete the
sensitivity, assessments, gas-root check and remaining §5 step-5 evidence. There
is no automatic fallback or second fit.
