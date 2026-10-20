# A7 restricted feasibility fit on wheel 8298c602

**Ineligible: no resolved descent on the 73-point family, but the loaded-density gate fails.**
The single λ = 1 restricted fit (owner decisions, #170 comments 6283064075 and
6283335389) converged to an endpoint with no resolved descent at any family
point. Only 44 of 47 loaded densities meet |e|/s ≤ 2 (worst 2.70). Under the
design's unchanged eligibility rules the endpoint is rejected. It runs no Hartono
x₃ sensitivity or full assessment, and the design authorizes no second fit. The
numbers and unused allocation return to the owner.

| Gate (design §3) | Limit | Endpoint | Retained A6 selected, same wheel |
|---|---|---:|---:|
| Phase family: points with a resolved descent | 0 | **0** (73 passed: 68 two-phase, 5 single-liquid) | 12 (29 descents) |
| Loaded density, rows with \|e\|/s ≤ 2 | 47/47 | **44/47**, max 2.70 | 47/47, max 1.98 |
| CO₂-free density, max \|e\| | ≤ 1.0 kg/m³ | 0.55 | 0.57 |
| Cai cost | ≤ 95.90 | 91.92 | 91.81 |
| C149 | ≤ 35.26 | 24.10 | 24.92 |
| Fitted pressure / species AARD | ≤ 15.81 / 9.89 % | 11.89 / 7.10 % | 12.47 / 7.15 % |
| Vinjarapu eight-row RMSE | ≤ 3.13 kJ/mol | 1.83 | 1.82 |
| 307-row objective (A7-2) | report | 149.246 | 148.238 |

The three failing rows are the warmest loaded states, all at 353.15 K. The model
is low at each:

| Row | T, K | α, mol CO₂/mol MEA | Observed, kg/m³ | Error, kg/m³ | e/s | A6 e/s |
|---|---:|---:|---:|---:|---:|---:|
| Hartono2014_density_80C_alpha0.39 | 353.15 | 0.39 | 1055.16 | −4.89 | −2.70 | −0.91 |
| Amundsen2009_state_081 | 353.15 | 0.30 | 1040.20 | −5.67 | −2.35 | −1.98 |
| Hartono2014_density_80C_alpha0.29 | 353.15 | 0.29 | 1037.04 | −4.30 | −2.12 | −1.75 |

The next-worst rows are the 343.15 K states at −1.90 and −1.87.

## Endpoint

- **Fit:** converged (`Function tolerance reached`, |Δcost|/cost 1.6 × 10⁻⁸)
  after 13 iterations, with cost 529.288 → 149.246. One call took
  72.92 wall-s / 900.48 CPU-s. `fit/usable-budget-endpoint.json` and `fit/native.json`.
- **Cold replay** (`replay/`): all 307 rows available. Predictions agree with the
  fit's native predictions within 2.8 × 10⁻¹² relative, and the cost is 149.2456440 in both.
- **Bound-active coordinates:**
  - MEAH⁺ segment diameter at its restricted lower bound, 5.49 Å (start 5.594, A6 4.155).
  - MEAH⁺–water k at −0.5, the lower bound common to the restricted and original boxes.
  - Carbamate–MEAH⁺ k at −1 and both Born diameters at 5 Å, as in A4 and A6.
  - Total R5 enthalpy shift at its +10,000 J/mol box limit, as in A6.

  Other moves:
  - Carbamate segment diameter 5.798 → 4.689 Å.
  - MEAH⁺ dispersion energy 249.2 → 173.2 K.
  - MEAH⁺–water slope 33.3 → −46.0 K.
  - Unshifted R5 aₖ 2848.5 K; total R2 shift −1,811.9 J/mol.

  The values are in `fit/chemistry-coordinates.json` and the endpoint record.
- **Phase family** (`../fixed-study/wheel-8298c602/restricted-endpoint/`): every
  point has a stability report. All 657 trials are `no_resolved_descent`, and no
  trial optimizer failed. The single-liquid points are 62, 63 and 70–72, where A6
  splits. Per Engine #660 that label means no descent was numerically resolved in
  this finite trial set. It does not certify global stability, and the 73 points
  do not cover the reacting domain.

## Interpretation and limits

In this box, removing the detected splits costs density at the warm, loaded end.
The fit pressed the restricted MEAH⁺ size bound, the only restriction-imposed active bound.
At this endpoint the 80 °C, α 0.29–0.39 densities are 4.3–5.7 kg/m³ (0.41–0.55 %) low.
This is one converged local endpoint from one start. It does not show that every vector in the
box fails density, or that a different bound would pass both gates. The bounds were
set from fixed-vector split evidence (`../fixed-study/README.md`). The density
scales s are the frozen source-local loading secants, not measurement uncertainties.

## Sequence and compute

| Call (`../step-ledger.json`, stage restricted-fit) | Wall-s / CPU-s |
|---|---:|
| Interior-start family (73 passed, no descent) | 33.37 / 33.27 |
| Release (released, binding `fe5d5dd7…`, 14 columns, condition 3.9 × 10⁴) | 169.62 / 169.56 |
| Fit | 72.92 / 900.48 |
| Cold replay | 15.37 / 15.35 |
| Endpoint family | 34.03 / 33.96 |
| Endpoint gates (307-row score) | 14.93 / 14.92 |
| **Stage total** | **340.24 / 1,167.54** of 1,162 / 6,962 |

Unused: restricted-fit 821.76 / 5,794.46; Hartono x₃ 1,200 / 7,000;
final-evidence reserve 1,950.38 / 9,200; qualification 221.27 / 843.12.

## MEAH⁺ size bound probe (owner, 2026-10-20)

At the endpoint, only the MEAH⁺ segment diameter σ moves (packing 0.88σ and
Debye–Hückel σ reapplied); every other parameter is held fixed. No fit is run
(`../fixed-study/wheel-8298c602/size-probe/`, `study.py.txt size`).

| MEAH⁺ σ, Å | Descent points (73) | Loaded within 2s | Min / max e/s | Span, s | 80 °C rows e/s | C149 | Pressure AARD, % |
|---:|---:|---:|---|---:|---|---:|---:|
| 5.49, endpoint | 0 | 44/47 | −2.70 / +1.48 | 4.18 | −2.70, −2.35, −2.12 | 24.10 | 11.89 |
| 5.45 | 0 | 44/47 | −1.38 / +2.62 | 4.01 | −1.01, −1.38, −1.01 | 24.20 | 11.70 |
| 5.40 | 0 | 22/47 | −0.19 / +4.80 | 4.99 | +1.09, −0.19, +0.36 | 24.88 | 12.29 |
| 5.35 | 0 | 7/47 | +0.98 / +6.96 | 5.97 | +3.16, +0.98, +1.71 | 26.20 | 13.39 |
| A6 selected | 12 | 47/47 | −1.98 / +1.22 | 3.20 | | 24.92 | 12.47 |

The 80 °C rows are Hartono α 0.39, Amundsen state 81 (α 0.30) and Hartono α 0.29.
Every probed vector is phase-clean in the same sense as the endpoint: 73 passed
(68 two-phase, 5 single-liquid), with no resolved descent.

**Meaning.** The density miss is a temperature spread, not an offset. With the
other parameters fixed, a smaller MEAH⁺ size raises every loaded density. At
5.45 Å the 80 °C rows pass, but the 20–30 °C α 0.39 Hartono rows exceed +2s.
None of the four evaluated sizes passes all 47 loaded-density limits. The smallest sampled residual span is 4.01s at 5.45 Å, slightly above the 4s gate window. These evaluations do not establish the minimum span between sampled sizes or rule out an untested size that passes. The approved refit tests whether jointly varying the declared coordinates can satisfy all unchanged gates. The three lower-size vectors at 5.45, 5.40 and 5.35 Å show no resolved descent on the 73-point family; they do not certify a continuous interval or the surrounding parameter box.

Charge (stage bound-probe, allowance 180 / 200): 153.51 wall-s / 152.00 CPU-s.
A7 calls total 614.48 wall-s so far.

## Second restricted fit, MEAH⁺ size ≥ 5.35 Å (owner, 2026-10-20)

**Also ineligible on the same three rows: no resolved descent, loaded density 44/47 (worst 2.43s).**
The declaration is `../inputs/restricted-2-*.json`, built by `build-2.py.txt`
(readiness review r1 Ready). It starts at the first endpoint and changes only the
MEAH⁺ size box, to [5.35, 5.8] Å. Outputs are in `../restricted-2/`. The phase
family and gates are in `../fixed-study/wheel-8298c602/restricted-2-endpoint/`.

| Gate | Limit | First endpoint | Second endpoint |
|---|---|---:|---:|
| Points with a resolved descent (73) | 0 | 0 | **0** (69 two-phase, 4 single-liquid; 657 `no_resolved_descent` trials; 0 failed trial optimizers) |
| Loaded density within 2s | 47/47 | 44/47, max 2.70 | **44/47, max 2.43** |
| Loaded e/s min / max (span) | | −2.70 / +1.48 (4.18) | −2.43 / +1.45 (3.88) |
| CO₂-free max \|e\| | ≤ 1.0 kg/m³ | 0.55 | 0.56 |
| Cai cost | ≤ 95.90 | 91.92 | 91.91 |
| C149 | ≤ 35.26 | 24.10 | 23.87 |
| Pressure / species AARD | ≤ 15.81 / 9.89 % | 11.89 / 7.10 | 11.86 / 7.10 |
| Vinjarapu RMSE | ≤ 3.13 kJ/mol | 1.83 | 1.83 |
| 307-row objective | report | 149.246 | 148.905 |

The failing rows are the same three 353.15 K states:

| Row | α, mol CO₂/mol MEA | Error, kg/m³ | e/s |
|---|---:|---:|---:|
| Hartono2014_density_80C_alpha0.39 | 0.39 | −4.41 | −2.43 |
| Amundsen2009_state_081 | 0.30 | −5.52 | −2.28 |
| Hartono2014_density_80C_alpha0.29 | 0.29 | −4.16 | −2.05 |

The fit converged on function tolerance (|Δcost|/cost 3.6 × 10⁻⁹) after 12 iterations, with cost
149.246 → 148.905, in 45.51 wall-s / 560.75 CPU-s. The cold replay agrees with its native
predictions within 3.3 × 10⁻¹³ relative. The MEAH⁺ segment diameter again ends on
its lower bound, now 5.35 Å. Over the same fit the carbamate segment diameter moved
4.689 → 4.866 Å; no causal link between the two is established. MEAH⁺–water k stays at
−0.5, unlike-ion k at −1, Born diameters at 5 Å, and the total R5 shift at +10,000 J/mol.
Total R2 shift: −1,387.4 J/mol. Unshifted R5 aₖ: 2831.7 K.

**Meaning and limits.** Lowering the size bound by 0.14 Å narrowed the worst
loaded-density miss from 2.70s to 2.43s and the span from 4.18s to 3.88s. The
same 80 °C rows still fail, at 0.40–0.53 % of the measured density. Both are single
local fits from one start. They show that these two declared boxes did not yield an eligible
endpoint. They do not show that no eligible vector exists. Under the owner's
scope, no further fit is authorized.

Charge (stage second-fit, allowance 1,200 / 7,000): release 186.27 / 185.66,
fit 45.51 / 560.75, replay 15.21 / 15.16, family 34.56 / 34.43, gates 28.59 / 28.15;
total 310.14 / 824.15. All A7 calls: 924.62 wall-s / 2,263.71 CPU-s.
