# Amendment 6 revision 3: the two combined-density F1 candidate fits (#170)

Run 2026-10-19 on Engine wheel `main-21e761c3` (sha256 `d2f61e3a…0357`), from main
`242d788` content (branch `amendment-6-stage2b`). Declarations:
`../inputs/revision-3/{tied,held}-{information,fit}.json`; launched specs, outputs and
command times under `../tied/` and `../held/`. Basis: design §0b (Ready `352bda1`),
build `78b87ca` reviewed launchable for these fits (2026-10-19).

## Result

**Neither form is eligible.** Both converge, both endpoint replays pass, and both meet every
calibration ceiling. Both miss the same five loaded-density rows: Amundsen 2009 at α = 0.4
(states 063, 068, 073, 078, 082; 25/40/50/70/80 °C), where Amundsen sits 8.5–9.1 kg/m³ above
Hartono 2014 on the printed-α basis. The Held form also misses the CO₂-free 25 °C gate.

| | Tied (DH = 0.88σ) | Held (DH = σ) | Gate |
|---|---:|---:|---|
| Status, iterations | converged, 32 | converged, 46 | |
| Cost (start → end) | 2073.684 → **56.6003** | 2072.130 → **56.6632** | |
| Loaded densities within 2s | **47/52** | **47/52** | 52/52 |
| Hartono 32 rows: error range, max \|e\|/s | −3.14…+2.75 kg/m³, 1.55 | −3.21…+2.99 kg/m³, 1.58 | ≤ 2 |
| Amundsen 20 rows: error range, max \|e\|/s | −9.79…+1.64 kg/m³, 3.41 | −11.07…+1.83 kg/m³, 3.85 | ≤ 2 |
| Amundsen α = 0.4 errors | −6.76, −6.78, −6.93, −8.65, −9.79 | −6.37, −6.80, −7.25, −9.61, −11.07 | |
| CO₂-free errors, 25/40/50/70/80 °C (kg/m³) | −0.489, −0.020, +0.023, +0.435, +0.359 | **−0.526**, −0.058, −0.015, +0.398, +0.323 | ≤ 0.5 |
| C149 | 25.086 | 23.783 | ≤ 35.26 |
| Pressure / species AARD | 12.57 / 7.15 % | 11.78 / 7.13 % | ≤ 15.81 / 9.89 % |
| Vinjarapu RMSE | 1.884 kJ/mol | 1.842 kJ/mol | ≤ 3.13 |
| Hilliard Cp errors (four fitted rows) | +5.79, +2.43, +1.35, −1.69 % | +5.79, +2.61, +1.35, −2.00 % | report |
| Coordinates at a bound | 7 of 14 | 6 of 14 | report |

**Is the density gate satisfiable at α ≈ 0.4?** The two sources' 2s bands overlap at each
temperature, but only by **+0.44 to +1.01 kg/m³** (data-only arithmetic: Amundsen α = 0.40 minus
Hartono α = 0.39 is +10.4 to +11.0 kg/m³; 2s_A + 2s_H is 9.3 kg/m³; the fitted model rises
2.1–2.2 kg/m³ between the two loadings). A single model passes both only by overpredicting
Hartono 0.39 by about 3.1–3.6 kg/m³. The least-squares objective has no reason to land there.
The x₃ loading basis widens the gap (+10.6 to +11.2 kg/m³, Hartono README), so the planned
x₃ sensitivity fit cannot close it. The slopes dρ/dα differ only above α = 0.3: Amundsen
rises 200 → 220 → 256 kg/m³ per unit α; Hartono's own sequence is 167 → 200 → 220 → **179** → 190.

**Parameters at bounds.** Both forms end with bicarbonate–water k_ij = +1.0 (upper), carbamate–MEAH⁺
k_ij = −1.0 (lower), both Born diameters 5.0 Å (upper), and R5 enthalpy shift +10,000 J/mol (upper).
The tied form also has the carbamate segment diameter at 5.8 Å and the R5 unshifted coefficient at
2,400 K. Held has MEAH⁺–water k_ij at −0.5. These endpoints are box-constrained, so their local
covariance is conditional on the active set (`endpoint-values.json`; `../<form>/fit/native.json`).

**Selection rule.** §0b: if neither qualifies, an ineligible vector may be chosen by the cost rule
(lower cost; prefer Held within 1 %) but cannot be adopted. Held is 0.11 % above tied, so the rule
names Held, although Held misses one more gate than tied. No selection is recorded here; the next
fits (selected-form B, smaller-branch A) wait for the owner's decision on the α = 0.4 conflict.

## Checks

- **Release:** fresh information calls at both substituted starts; both segment-diameter columns
  passed at steps 0.01/0.005; ties correct. Tied binding `d79917c9…`, Held `d8347b02…`. At the starts,
  rank 14, condition 3,435 (tied) / 3,543 (Held); local linearization only.
- **Endpoint cold replay** (`final_evidence.main`, explicit documents): every weighted residual and the
  relative cost within 1e-8 of `native.json`, ordered IDs identical, ties checked, and the 39 Kiepe rows
  within 1e-8 of `../<form>/kiepe-reference.json`. That reference is √w·r of the release call at the
  start; Kiepe rows are CO₂–water only, so fitted parameters cannot move them. The replay checks the
  physical endpoint only; `chemistry-coordinates.json` is not consumed by it.

## Compute

Six calls, 612.96 s wall and 4,081.51 CPU-s (`step-ledger.json`), within the §0b allocation of
1,500 s / 12,000 CPU-s; charged 613 / 4,082 to the program ledger.

## Files

`step-ledger.json` (operator checks, calls), `summary.json` (scores, all 57 density rows),
`endpoint-values.json`, and disclosed one-off scratch: `reduce.py.txt`, `endpoint-values.py.txt`,
`candidate.py.txt` (launcher), `release.sh.txt`.
