# Amendment 4 matched reacting comparison, smaller-d_V branch (#170)

Run 2026-10-18 on Engine wheel `main-21e761c3`, after the larger-d_V branch
(`../matched-larger-dV/README.md`), with the same declarations and checks.

## Result

**The same null as the larger branch.** Fixing the CO₂–MEA pair at the neutral
value (0.098720, −50.989 K) raises the non-Kiepe cost C166 by 0.06 %, against
the required 10 % reduction (A4-5). The decision is formally **not decidable**
for the same two endpoint flags as the larger branch.

| | Zero control | Neutral-fixed variant |
|---|---|---|
| Status, iterations | converged, 76 | converged, 76 |
| Cost, start → end | 196.8658 → 39.7373 | 196.8656 → 39.7608 |
| C166 | 39.7366 | 39.7601 (×1.000590) |
| C149 | 24.5966 | 24.5968 (×1.000011) |
| Active bounds | carbamate–MEAH⁺ k = −1; both segment diameters 5.8 Å; both Born diameters 5.0 Å | the same |
| Wall / CPU | 202 s / 2,991 CPU-s | 206 s / 3,008 CPU-s |

| Endpoint check | Control | Variant | Limit |
|---|---|---|---|
| Rows available, rank | 205, 14 | 205, 14 | 205, 14 |
| Cold replay, largest weighted row difference | 6.9e-12 | 6.9e-12 | ≤ 1e-8 |
| Kiepe rows against the fixed-binary start | 3.2e-15 | 3.2e-15 | ≤ 1e-8 |
| Free-block condition | 37,363 | 37,362 | ≤ 1e4 |
| Centered derivatives | miss at the two ion dispersion energies (≤ 6.4e-7 absolute; h² convergence) | the same | 1e-8 absolute or 1e-5 relative |

The two d_V branches end within 0.12 % of each other in C166 (39.6902 vs
39.7366 for the controls); the dielectric branch choice does not change the
bound activity either. Files mirror the larger branch.
