# Why 62 of 63 drawn MDEA starts were refused (issue #429)

Diagnosis only. Probes run on the study wheel `c9fbf898…80bb` (Engine `05e94210`) against the
retained #440 MDEA manifest. No refit was run. Base commit `17c122356`.

## Result

The campaign reports the first unavailable row and stops, so its seven refusal labels are not seven
causes. Evaluating all 281 fitted rows one at a time at every draw gives three causes.

| Cause | Draws | Rows unavailable per draw | Kind |
|---|---|---|---|
| MDEA–water liquid splits at a fitted row's own temperature | 26 | 6–154 | physical, from the start box |
| Only the Merkley saturation search is unavailable | 25 | 1–4 of 281 | Engine search rules |
| Model bubble pressure beyond vapor-like CO2 | 11 | 6–54 | physical, from the start box |
| Evaluable (LHS-53) | 1 | 0 | |

Start A (control) has 0 unavailable rows. Draw 17 was never evaluated by the campaign.

**MDEA–water liquid split (26 draws).** The slope bound `a1 ∈ [−0.01, 0.01] K⁻¹` lets
`k(T) = a0 + a1 (T − 423 K)` range from −1.8 to +1.1 at 288.71 K among the draws. The retained #411 gap-onset
value is −0.13 there. A liquid Gibbs-energy hull, which does not use the bubble solve, was compared
with the solver status of each binary bubble row at each draw (`gap.py`):

| Hull at the row's feed | Available | Unavailable |
|---|---|---|
| stable | 2,587 | 0 |
| inside the gap, positive curvature | 54 | 9 |
| inside the gap, negative curvature | 0 | 1,256 |

A gap exists exactly where `k(T)` exceeds the retained #411 onset, in 2,268 of 2,268 draw–temperature pairs.

**Merkley saturation search (25 draws).** 68 searches are unavailable: 26 report no crossing, 21 a
failed node and 21 a slope reversal (`saturation.py`). In 64 of them every solved node lies below
the 1.121 MPa target (median highest pressure 23 % of target), so the capped loading is the source
cap. All 21 failed nodes converge when the same declared node is solved cold through
`solve_equilibrium` (`nodes.py`). The same search produced all 21 trial failures in the retained A
fit (row 124, node at loading 1.5, beyond the accepted root at 0.911) and 19 in LHS-53.

**Bubble pressure beyond vapor-like CO2 (11 draws).** 203 Kuranov rows fail from the declared start.
Marching the CO2 loading upward with warm starts (`continuation.py`) reaches 66 of them, at
10.5–1,325 MPa against 0.07–5 MPa measured. Of the 137 that stall, 100 stop with no vapor-like
root for the CO2-rich phase; 37 stop on a residual or work budget and remain undecided.

**One coordinate at a time from A (`scan.py`).** Of 72 scan points, 21 keep every row available and
34 lose only Merkley rows. `a1 ≤ 0` alone loses 40–157 rows.

## Related refusals at the selected endpoint

- **Zheng row 6** (`zheng.py`): at 50 wt % MDEA, 323.15 K and the source loading 1.177, the model
  bubble pressure is 38.1 MPa against 4.19 MPa measured. The CO2-rich phase has 21,129 mol/m³.
- **Unfinished stability searches** (`searches.py`): 1,086 of the 1,315 are grid states. Their 549
  distinct states have a model bubble pressure of at least 30 MPa (233) or cannot be reached by the
  loading march (314), with 2 exceptions. Of 1,186 marched states below 7.4 MPa, 1,185 are
  available. The other 229 unfinished searches were not examined.

## Probes

| Script | Question | Wall time, 8 processes |
|---|---|---|
| Retained census, `summarize.py` | Which rows are unavailable at each draw? | 509 s |
| `saturation.py` | What did each Merkley search solve before refusing? | 103 s |
| `gap.py` | Do binary failures coincide with a liquid–liquid gap? | 122 s |
| `continuation.py` | Does a loading march reach rows that fail cold? | 385 s |
| `scan.py` | Which single coordinate causes which failure? | 266 s |
| `nodes.py` | Do failed search nodes converge cold? | 12 s |
| `searches.py` | What bubble pressure lies behind the unfinished searches? | 269 s |
| `zheng.py` | Zheng row 6 bubble pressure along loading | 2 s |
| `outlook.py` | Per-draw cause from the retained records | under 5 s |

`retained_starts.py` binds the historical declaration to the shared start evaluator. `results/`
holds the records used above. For #427, `stage0.py` passes the slope-bound declaration to
`census.py` and writes to `../results/MDEA_slope_bound/`.
