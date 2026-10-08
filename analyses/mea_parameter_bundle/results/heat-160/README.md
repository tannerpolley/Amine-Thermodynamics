# Heat of absorption added to #160

Both starts converge to slope **b = 107.96395 K**, conditional SE **22.92962 K**.
The 141-target pressure/species cost rises by **0.8013%**, while heat cost falls
from **7.1466 to 1.7258**. The 80 °C pressure comparison does not improve. Arcis
predictions remain less exothermic than measured by **2.276–13.401 kJ/mol CO₂**.
No parameter adoption or physical validation follows.

| Quantity | #160 baseline | Start A | Start B |
|---|---:|---:|---:|
| Pressure cost | 7.78986350 | 8.38038618 | 8.38038763 |
| Species cost | 22.29989769 | 21.95047973 | 21.95047799 |
| 141-target cost | 30.08976119 | 30.33086591 | 30.33086561 |
| 8-heat cost | 7.14663171 | 1.72581779 | 1.72581808 |
| 149-target cost | 37.23639290 | 32.05668370 | 32.05668370 |
| Pressure AARD (%) | 13.25654630 | 13.81475106 | 13.81475627 |
| Species AARD (%) | 7.93728096 | 7.89143417 | 7.89143401 |
| 80 °C pressure AARD (%) | 19.41121646 | 19.60610588 | 19.60610441 |
| Arcis RMSE (kJ/mol CO₂) | 11.63183464 | 8.36442064 | 8.36442040 |

The [2026-10-08 owner decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/147#issuecomment-6070624850)
keeps #160's chemistry, five coordinates, bounds, 141 targets and scales; adds
8 Vinjarapu Table 4 Difference heat residuals with printed u_H scales and weight
1; and requests two starts. A uses #160 fitted coordinates; B uses the original
#160 coordinates in `new-water-binaries-parameters.json`. Both retain the
HCO₃⁻–water upper bound, +0.5. Conditional errors use the existing #160 calculation
on the native exact weighted Jacobian, with active coordinates held fixed.

Heat basis: 1 mol feed MEA, 30 wt% MEA in the unloaded solvent, mol added
CO₂/mol feed MEA, exactly zero initial carbon, one reacting liquid at each
endpoint, vapor CO₂ feed at source T/P, signed J/mol added CO₂. Physical calorics
come from `verify_reference_calorics.record()`. Fitted data are **calibration**;
Arcis (322.5 K, 0.51/1.03 MPa, α ≤ 0.45) and the previously accessed 21-row
80 °C benchmark are **prediction**. Density checks reuse the four translation
calibration rows; c stays **39.51429527803833 cm³/mol**, with final deviations
−0.153% to +0.250%. Translation is not applied to equilibrium or calorics.

Engine commit: `026b30311b959f1a5db4feef4c15e243f7044a5f`.
Wheel SHA-256: `94b55dfcf72f21b43010c7125d71f103f41fd56f7a6b6fe0774903eef71cc72a`.
The clean detached Engine build used `tools/build-engine.sh --wheel`; the wheel
is installed non-editably in `build/heat-160/venv`. The 141-target equivalence
cost is **30.089761188866785**, relative error **6.38×10⁻¹⁴**: numerical verification.
Missing Arcis/heat-role inputs are pinned copies from branch commit
`c2ca6f06617e43c929be0b67bfad7e2f27294599`; no #147 chemistry or qualification
output is used. `inputs.json`, `engine.json` and `environment.txt` retain hashes
and identities. `baseline.json`, `A/B-native-fit.json`, `A/B-summary.json`,
`A/B-parameters.json` and `comparison.json` contain the full numerical results.

Native times A/B: **623.28/647.45 s**; iterations **4/5**; residual evaluations
**5/6**; Jacobian evaluations **6/6**; rejected trials **0/0**. Relative start-cost
difference is **1.38×10⁻¹²**; slope difference **5.81×10⁻⁶ K**. Four setup errors
were corrected (hash representation, reaction declaration, benchmark mask,
unexposed export field). The first A result was lost during export; B was stopped
before that same error, and both were rerun. Logs and resource reports retain this.

Run `uv run --no-project --python build/heat-160/venv/bin/python
analyses/mea_parameter_bundle/scripts/heat_160.py` with `baseline`, `fit A/B`,
or `assess A/B`, through `agent-heavy` (1 GB; threads 1). Fits use 40 iterations
and 2,250 s. The selected record, notebook and manuscript are unchanged; no push.
Independent delivered review and adoption remain with the owner.
