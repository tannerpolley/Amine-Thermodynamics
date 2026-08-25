# MEA parameter qualification and reactive regression

This analysis owns the practical parameter sequence that precedes the final
nine-species reactive fit. CO2-water induced association is fixed in every
retained parameter document.

## Current neutral result

The Cai (1996) MEA-water study fits one `k_MEA,H2O` value on the 101.33 kPa
series and tests it on the independent 66.66 kPa series. Three Baygi MEA
association candidates are evaluated under the same fixed Held 2B water.

| MEA family | Fitted `k_MEA,H2O` | Fit log-RMSE | Held-out log-RMSE | Held-out typical factor |
|---|---:|---:|---:|---:|
| 2B | -0.058566 | 0.06883 | 0.15891 | 1.172 |
| 3B | -0.019567 | 0.05900 | **0.11123** | **1.118** |
| 4C | -0.036274 | **0.05244** | 0.12577 | 1.134 |

All 25 binary rows evaluate, exact derivatives pass the centered-difference
check, and three starts agree for every candidate. The 3B MEA family gives the
best pressure-level transfer and is the retained neutral candidate. The
source-resolution-normalized residuals remain stringent because the source
reports composition resolution rather than a statistical covariance model;
selection therefore uses both the raw log closure and the independent pressure
level.

The exact plotted rows and the complete comparison table are retained under
`results/figures/cai_held_water_mea_family_*`.

## Reactive calculation

The generic GREPE calculation under `results/grepe_gate0` solves the declared
nine-species liquid and incipient neutral vapor and exposes exact parameter
derivatives. Its earlier two-coordinate fit is diagnostic. It is regenerated
only after the retained neutral packet is updated with the selected 3B MEA
family and the physical CO2-water interaction is qualified. That binary
qualification is now complete in `../co2_water_induced_association`.

## Next calculation

Compare direct and screened Born formulations against independent dielectric,
solvation, and activity observations before reopening MEAH+ and MEACOO-
parameters. The retained neutral inputs are the Held-water/3B-MEA result above
and the source CO2-water temperature correlation qualified on all 39 Kiepe
rows.

Commands and retained outputs are declared in `analysis.yaml`.
