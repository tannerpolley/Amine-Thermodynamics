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

## Disposition

**Cause: not a wiring defect.** The coordinate reaches B's model by the same
equation as A's. The loss is state-level: at B's start, the high-loading total
pressures are nearly insensitive to the liquid's CO2 interactions.
The mechanism (for example a very different AMPH⁺ fraction or CO2 share of the
total pressure at B's start) is **undetermined**: it needs predicted P, p_CO2
and liquid composition at the high-loading rows, an Engine probe not yet run
because it would exceed the 530-line ceiling.
