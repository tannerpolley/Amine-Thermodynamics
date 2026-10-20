# #170 amendment 7, steps 1–3: fixed-vector study (no fit)

Owner decisions: [#170 comment 6283064075](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6283064075)
(route, strict phase gate, endpoint-only split rule, 5,100.38 s plan). Design:
`tmp/joint-design/amendment-7-phase-stable-density.md` §5. Wheel `d2f61e3a…0357`
(Engine main-21e761c3). Probe: `study.py.txt` (disclosed, outside campaign code).
Calls: `calls.json`, **239.78 wall-s / 239.09 CPU-s** of the 400 / 600 allocation,
charged 240 / 240 in `amendment-4/compute-ledger.json`.

Vectors are the Held A4 control moved toward the selected A6 vector by one path
fraction per block (A7-1 block by block); the uniform-fraction construction
reproduces the design's `path-0p125` and `path-0p25` documents exactly (asserted).
Blocks: MEAH⁺ size (segment, packing and DH diameters), ion dispersion energies
(MEAH⁺, carbamate), ion–water pairs (carbamate, MEAH⁺ and bicarbonate k with the
MEAH⁺ slope), MEA–water k and slope, R2 coefficients, R5 coefficients.

## Results

**Step 1, onset bracket (all 73 points).**

| Path fraction t | Descent points | Lowest resolved $t_{plane}/(RT)$ | Classified failed / unresolved |
|---:|---|---:|---|
| 0.125 (design) | none | — | 0 / 73 |
| **0.1875** | none | — | 0 / 73 |
| **0.21875** | 70, 71, 72 | −1.34×10⁻⁴ | 3 / 70 |
| 0.25 (design) | 70, 71, 72 | −5.30×10⁻⁴ | 3 / 70 |

Detected onset lies between t = 0.1875 and 0.21875, at α = 0.5, 333.15 K. All
unresolved points carry the known failed near-pure-0 trial optimizer (#660).

**Step 2, block exchanges at points 63/70/72.**

| Block | 0.125 with block at 0.25 | 0.25 with block at 0.125 |
|---|---|---|
| MEAH⁺ size | none | 70/72, −2.76×10⁻⁴ |
| ion energies | none | 70/72, −1.16×10⁻³ |
| **ion–water** | **70/72, −7.94×10⁻⁴** | **none** |
| MEA–water | none | 70/72, −5.30×10⁻⁴ |
| R2 | none | 70/72, −5.30×10⁻⁴ |
| R5 | none | 70/72, −5.29×10⁻⁴ |

Near the onset, the ion–water block alone switches the detected descent on and
off. Moving the ion energies toward A6 suppresses it (reverting them deepens
the descent); moving MEAH⁺ size toward A6 deepens it slightly.

**Step 3, coupled vectors (all 73 points, split-seeded attempts).** Both hold
ion–water, MEA–water, R2 and R5 at 0.125 and the ion energies at A6, isolating
the MEAH⁺ size change, which is the largest density change between A4 and A6.

| Vector | MEAH⁺ σ, Å | Descent points | Lowest $t_{plane}/(RT)$ | Converged lower-Gibbs splits, $\Delta G/(RT)$ |
|---|---:|---|---:|---|
| step-2 exchange: size at 0.25, all else at 0.125 (energies too; three points only) | 5.389 | none at 63/70/72 | — | — |
| `coupled-half-size-energies-at-selected` | 4.978 | 63, 70, 71, 72 | −3.17×10⁻³ | 63: −0.0271 (α 0.4) |
| `coupled-size-energies-at-selected` | 4.155 | 24, 33, 36, 45, 54, 62, 63, 70, 71, 72 | −5.77×10⁻² | 36: −0.0561 (α 0.2); 70/71/72: −1.342 (α 0.5) |

Unconverged confirmations (phase vanished, phases coincide, work exhausted)
remain rejected, unconfirmed descents, never passes (`*/split-summary.json`).

**Scoring of the furthest split-free path vector (t = 0.1875, 307 rows).**
Cost 467.63; loaded densities **0/47 within 2s** (max 41.78 s); CO₂-free max
|e| 0.995 kg/m³ (≤ 1.0); Cai 91.37 (≤ 95.90); C149 28.92 (≤ 35.26); pressure /
species AARD **18.21** / 7.13 % (pressure fails ≤ 15.81); Vinjarapu RMSE
1.84 kJ/mol. The reduction reproduces the retained A6 replay (cost 148.2377,
C149 24.9231, Cai 91.8115) on that replay's rows.

## Meaning and limits

The coordinate that carries most of the loaded-density fit, the MEAH⁺ segment
diameter shrinking from 5.8 toward 4.16 Å, predicts liquid–liquid splits by
itself: half of that change already gives a confirmed split at α = 0.4,
333.15 K, with the ion–water, MEA–water and reaction blocks held near A4 and the
split-suppressing ion energies at their A6 values. The ion–water block controls
the onset on the straight path, but holding it back does not remove the
size-driven splits. No tested fixed vector is both split-free and close to the
density gate; the split-free frontier sampled here misses it by about 40 s.

These are fixed vectors, not fits: a fit restricted to MEAH⁺ σ ≥ about 5.4 Å
could move the coordinates held fixed here (carbamate size, Born diameters,
carbamate–MEAH⁺ k, energies), although in A6 carbamate size, both Born
diameters and carbamate–MEAH⁺ k already sit on their bounds. Sampled vectors do not certify a box, and zero detected descent on
73 points is not a stability proof. No physical phase-separation data exist for
comparison; the splits are model predictions with numerical verification.

**Step 4 outcome: no bound restriction that keeps the density fit.** The owner
chose a restricted feasibility fit instead of stopping (decision recorded on #170),
after a 24-point sub-block probe of the ion–water block (points 63/70/72):

| Single coefficient | 0.125 with it at 0.25 | 0.25 with it at 0.125 |
|---|---|---|
| **MEAH⁺–water k** | **63/70/72, −4.13×10⁻³** | **none** |
| carbamate–water k | none | 63/70/72, −4.01×10⁻³ |
| bicarbonate–water k | none | 70/72, −7.04×10⁻⁴ |
| MEAH⁺–water slope | none | 70/72, −4.71×10⁻⁴ |

The MEAH⁺–water k change (−0.204 → +0.027, weaker MEAH⁺ solvation) alone
switches the onset on and off; the carbamate–water change (−0.045 → −0.187,
stronger carbamate solvation) suppresses it. That carbamate–water change also
raises the loaded density (linearized, about +33 s in the mean), so it stays free.

**Bound proposal for the feasibility fit** (inside the existing boxes; all 16
coordinates retained; everything else unchanged):

| Coordinate | Existing box | Proposed box | Evidence |
|---|---|---|---|
| MEAH⁺ segment diameter (packing 0.88σ, DH σ tied) | [2, 5.8] Å | **[5.49, 5.8] Å** | t = 0.1875 (σ = 5.4916) has no descent on 73 points; σ = 4.978 with the energies at A6 splits |
| MEAH⁺–water k | [−0.5, 0.5] | **[−0.5, −0.161]** | t = 0.1875 (k = −0.16101) has no descent on 73 points; k = −0.14659 alone splits at 63/70/72 |

Start: the screened path t = 0.125 vector (MEAH⁺ σ 5.5944 Å, MEAH⁺–water k
−0.17544; both well inside), with the declared interior-start treatment for
carbamate σ (5.8 → 5.798 Å, ties reapplied) and its own 73-point screen before
release. These intervals are sampled evidence, not a certified split-free box;
the endpoint's 73-point family with split-seeded confirmation remains the
falsifier, and density may simply fail with the size lever removed.
