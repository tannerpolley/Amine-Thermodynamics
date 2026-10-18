# Amendment 4 neutral CO₂–MEA fit (#170)

Run 2026-10-18 on Engine wheel `main-21e761c3` (sha256 `d2f61e3a…0357`), with
the #191 CO₂/MEA `no_cross_association` declaration in each parameter copy.

## Result

**The neutral pair is determined and passes every qualification check:**
k(313.15 K) = **0.098720**, b = **−50.989 K** in
k(T) = k + b(1/T − 1/313.15 K). Both starts, A = (0, 0 K) and
B = (0.10, 100 K), reach it. Fitted to the seven Hartono 2014 rows, the model's
CO₂ Henry constant in 30 wt % MEA is within −1.41 to +1.32 % of the targets
(mean |error| 0.810 %), against the falsifier's 10 % mean and 20 % maximum.

| Row | T/K | Error | | Row | T/K | Error |
|---|---|---|---|---|---|---|
| 1 | 298.35 | −1.24 % | | 5 | 331.75 | +0.57 % |
| 2 | 312.65 | +0.46 % | | 6 | 341.25 | +0.35 % |
| 3 | 312.65 | +0.33 % | | 7 | 360.25 | −1.41 % |
| 4 | 322.25 | +1.32 % | | | | |

This is a calibration to N₂O-analogy targets, not physical validation: the
targets carry the analogy assumption (Versteeg Eqs. 4–5), the B1 vapor-side
correction and the source limitations listed below.

## Basis and conditions

- **Observation:** the model's CO₂ partial pressure at the dilute bubble point
  of gas-free 30 wt % MEA with CO₂ mole fraction 1e-6, as log ratio to
  1e-6 × H_x (design A4-1, addendum A4B-2/5).
- **Targets:** Hartono SI Table S2 primary H_x × the B1 factor f_N₂O/pN
  (0.9940–0.9963, `../b1-vapor-bound/transfer.json`).
- **Weights:** 400/(6 m_g), as `neutral_log_ratio_weight`; Xu rows weight 0.
- **Fixed:** stage-2 water, MEA, CO₂, MEA–water and CO₂–water values.
- **Coordinates:** k (scale 0.01, ±0.5) and b (scale 10 K, ±500 K).
- **Controls:** 100 iterations, function tolerance 1e-6 (fit-control
  amendment), gradient 1e-8, parameter 1e-10, 60 s.

## Checks

| Check | Result | Required |
|---|---|---|
| Interior endpoints | no active bound | interior |
| Rank / condition, starts and endpoints | 2 / 5.4990–5.4992 | 2 / ≤ 1e4 |
| A/B relative cost difference | 8.6e-12 | ≤ 1e-6 |
| A/B largest relative H difference | 4.7e-8 | ≤ 1e-4 |
| Dielectric branches (larger/smaller d_V) | identical predictions | ≤ 1e-8 |
| Cold replay from the written documents | identical | identical |
| Endpoint dilution, H_x change 1e-6 → 1e-7 | 9.8e-6 (298.35 K), 1.17e-5 (360.25 K) | ≤ 1e-4 |
| Endpoint raw equilibrium residual | ≤ 4.7e-14 | ≤ 1e-10 |

- **Dilution fix:** at the endpoint the 1e-5 → 1e-6 change at 360.25 K is
  1.13e-4, over the limit that 1e-5 passed at the starts, so the observation
  uses 1e-6. That moved the pair by 2e-5 in k and −0.03 K in b
  (`endpoint-sentinel.json`).
- **Projected gradient:** 4.2e-7 at A and 1.5e-8 at B, against the design's
  1e-8. Both fits stopped on the cost-change test at 8e-12 relative, below
  even the original 1e-10; a full Newton step from A would move k by about
  1e-8. Immaterial.
- **Conditioning:** (J_wᵀJ_w)⁻¹ without variance factor gives 0.0136 in k and
  64 K in b, correlation 0.49. At these weights that corresponds to about
  12 % per single row, so it describes local conditioning, not a physical
  interval. b is weakly determined: its lever is Δ(1/T) = 5.8e-4 K⁻¹ over
  298–360 K. k(T) above 360.25 K is extrapolation.

## Source limitations carried with the pair

- **B1 transfer:** after correction, signed bound ≤ 0.51 % (rows 1–6) and
  0.83 % (row 7); its full effect on the pair is ≤ 0.0010 in k and ≤ 4.4 K in b.
- **Table 11 vs SI representation (0.85–3.09 %):** on the Table 11 basis the
  pair would be 0.0037 higher in k and 12.3 K lower in b.
- **Peng–Robinson residual δ in the source concentration:** H low by
  0.16–3.85 % depending on the unprinted fill pressure; correcting for it would
  raise k by 0.0005–0.0056 and lower b by 1.7–9.9 K.
- **Apparatus water check:** Hartono 2008 Table 1 lies 5–8 % below Versteeg's
  correlation at 343–353 K. A bias of that size at rows 6–7 would move b by
  tens of kelvin but k by only about 0.001–0.002.

## Xu comparison (zero weight)

At the fitted pair the model's Henry constant is −7.7 to +22.5 % from Xu &
Wang 2018 Table 8 (mean |error| 10.1 %, largest 22.5 %). The error rises with temperature and
MEA content: −7.7 to +7.6 % at 293.15 K, +9.8 to +22.5 % at 323.15 K, and
+15.2 to +17.5 % at 313.15 K for w = 0.37–0.49. Near 30 wt % at 313.15 K the
model is about 12 % above Xu but 0.3–0.5 % from Hartono, so the two sources
disagree at the same state. Concentration transfer away from 30 wt % is not
supported by this fit. Xu's water calibration differs from Versteeg by up to
7.2 % (§2.3).

## Files and accounting

`A/`, `B/` (native results, endpoint documents, evaluations at start and
endpoint for both dielectric branches), `cold-replay.json`,
`endpoint-sentinel.json`, `target-factors.json`, `inputs.json` (input and
wheel hashes; all 12 installed Engine files match the wheel), command times.
Producer: `scripts/fit_neutral_co2_mea.py`. Each fit took about 0.05 s; both
commands together under 1.5 s wall. The superseded run on uncorrected targets
is in `../neutral-fit-superseded/`.
