# Cation B rank-gate failure: read-only diagnosis (#242, owner request 2026-11-02)

Question: does the AMPH⁺–CO2 k coordinate reach cation B's model, and why is
its weighted calibration column about 10⁻³ of cation A's?

## Observed failure

Preflight (`reactive.py`, `results/reactive/summary.json`, head `c8c4e8a`),
weighted coordinate-scaled Jacobian at each document start, 156 calibration
rows (47 loaded total pressures, 52 binary, 57 NMR):

| Run | s_min/s_max | AMPH⁺–CO2 k column norm | Weakest right vector |
|---|---|---|---|
| A-1 | 2.19e-3 | 0.538 | carbamate-anion σ 0.85, δ 0.39, AMPH⁺ σ 0.23 |
| A-2 | 2.12e-3 | 0.330 | carbamate-anion σ 0.90, δ 0.43 |
| B-1 | 8.5e-6 | 6.6e-4 | AMPH⁺–CO2 k −1.00 |
| B-2 | 4.0e-6 | 1.4e-4 | AMPH⁺–CO2 k −1.00 |

## Coordinate wiring (Engine source at `e6dae5c7`, the pinned wheel's commit)

- The coordinate targets family `k_ij`, pair (protonated-aminomethylpropanol,
  carbon-dioxide). `regression._slot` resolves an unlike pair to the two
  mirrored native slots i·n+j and j·n+i from the component order, which is the
  same in both variant documents.
- `engine/native/contributions/helmholtz.hpp:488–515`: for every pair,
  ε_ij = √(ε_i ε_j)(1 − k_ij); the only exclusion is same-sign ions that are
  not both declared charged molecules. AMPH⁺–CO2 has z_i z_j = 0, so k_ij
  enters identically for the sphere (A) and the charged molecule (B). The pair
  weight is x_i x_j m_i m_j σ_ij³; per unit x_AMPH⁺ x_CO2 it is about 1.6
  times larger for B (m = 4.08, σ = 3.19 Å) than for A (m = 1, σ = 5.3 Å).

**No exclusion or mis-resolved slot was found.**

## Where the column lives (retained matrices, no new Engine call)

Columns of `weighted_jacobian` by observation group: binary rows contribute
exactly 0 (no AMPH⁺); NMR rows 1.4e-5 (A-1) and 8.8e-8 (B-1); the 47 loaded
total-pressure rows carry the column in both variants.

| Hartono 2021 row | A-1 AMPH⁺–CO2 | B-1 AMPH⁺–CO2 | B/A | A-1 AMP–water k | B-1 AMP–water k |
|---|---|---|---|---|---|
| 333 K, α 0.96, 665.0 kPa | 2.91e-1 | 4.26e-4 | 1.5e-3 | 4.06 | 0.237 |
| 353 K, α 0.90, 733.2 kPa | 2.11e-1 | 3.75e-4 | 1.8e-3 | 3.92 | 0.306 |
| 313 K, α 0.95, 609.1 kPa | 1.32e-1 | 5.02e-5 | 3.8e-4 | 4.76 | 0.080 |
| 313 K, α 0.07, 6.8 kPa | 1.65e-9 | 6.57e-10 | 0.40 | 0.469 | 0.447 |
| 353 K, α 0.07, 45.7 kPa | 3.25e-8 | 1.90e-8 | 0.58 | 0.471 | 0.461 |

At low loading B's sensitivity is 0.4–0.6 of A's; at high loading, where CO2
carries most of the measured total pressure, it is 10⁻³–10⁻⁴ of A's, and the
AMP–water column falls about 20-fold in the same rows.

## Engine probe at the A-1 and B-1 starts (owner-approved, `probe_cation_b.py`)

`results/reactive/probe-cation-b.json`; agent-heavy, about 2.5 s. Each row
solved to an available liquid root plus incipient vapor (liquid packing fraction
0.43–0.46, vapor ≤ 0.0007) in both variants: **no phase or root change**. The
prediction's branch and stable-root count are not exposed for an equilibrium
pressure (both `None`). Central difference uses ±0.05 in AMPH⁺–CO2 k.

| Row (T, α, measured P) | Variant | Predicted P / kPa | CO2 share of vapor | Liquid x_CO2 | x_CO3²⁻ | x_AMPH⁺ | d ln P / d k |
|---|---|---|---|---|---|---|---|
| 313 K, 0.07, 6.8 kPa | A | 6.89 | 0.0001 | 9.3e-9 | 1.8e-3 | 6.6e-3 | 3.4e-9 |
| | B | 6.92 | 0.0000 | 1.1e-9 | 3.4e-3 | 8.3e-3 | 1.4e-9 |
| 313 K, 0.95, 609.1 kPa | A | 22.9 | 0.667 | 6.4e-4 | 3.5e-5 | 6.5e-2 | 2.7e-1 |
| | B | 9.08 | 0.011 | 4.0e-6 | 1.6e-3 | 6.7e-2 | 1.0e-4 |
| 333 K, 0.96, 665.0 kPa | A | 90.8 | 0.774 | 1.9e-3 | 1.7e-5 | 6.4e-2 | 6.0e-1 |
| | B | 24.5 | 0.028 | 2.0e-5 | 5.4e-4 | 6.7e-2 | 8.8e-4 |
| 353 K, 0.90, 733.2 kPa | A | 181.5 | 0.733 | 2.4e-3 | 1.6e-5 | 5.9e-2 | 4.3e-1 |
| | B | 56.4 | 0.030 | 3.4e-5 | 4.6e-4 | 6.2e-2 | 7.7e-4 |

## Disposition

**Cause: not wiring, phase or root; a start-state chemical effect.** At B's
start the high-loading liquid holds 70–160 times less molecular CO2 than A's
and 29–46 times more carbonate, with a similar AMPH⁺ fraction. CO2 is then
1–3 % of the predicted vapor (A: 67–77 %), so the predicted total pressure
(9–56 kPa against 609–733 kPa measured) is set by water and AMP. Both the CO2
share and the CO2-fugacity response to k are smaller, giving
d ln P/d k 10⁻³–10⁻⁴ of A's, the empty column seen by the rank gate. Why the
charged-molecule cation binds CO2 so much more strongly at its start (for
example a lower ion activity coefficient from its self-dispersion and
association) is an untested inference. Both starts are also far from the
measured high-loading pressures in both variants (A under-predicts by 4–27×),
so the gate result describes the start, not a fitted endpoint. No fit, gate or
coordinate change was made; the route (A only, return to Design, or B with
seven coordinates) is the owner's.

## Owner decision (2026-11-02)

**Cation B fails its start rank gate for the start-state reason above and is
not fitted.** The study continues with cation A only (`reactive.py` keeps B's
preflight record and fits A from both starts). A is the result by default, not
by a calibration-cost comparison with B; nothing here shows that B would fail
from another start or after fitting.
