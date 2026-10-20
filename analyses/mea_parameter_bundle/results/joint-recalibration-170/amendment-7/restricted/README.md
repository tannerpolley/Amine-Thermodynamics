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
