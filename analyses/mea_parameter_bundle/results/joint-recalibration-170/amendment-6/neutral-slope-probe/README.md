# Amendment 6: CO₂-free density probe for an MEA–water reciprocal-temperature slope (#170)

**Question.** Every density-weighted endpoint misses the CO₂-free 25 °C density gate (0.5 kg/m³) by about 0.5. The five CO₂-free errors trend with temperature: about −0.99 at 298 K to +0.15 at 353 K at the Hartono-targeted endpoint. In stage 2, before any ion fitting, they ran from −0.69 to +0.53 (`stage2/README.md`). A constant MEA–water k_ij cannot change a temperature trend. Can a reciprocal-temperature slope, k(T) = k + b(1/T − 1/313.15 K), the form already used for MEAH⁺–water and CO₂–water, remove it without degrading the Cai 1996 boiling-point rows?

**Method.** This is a one-off disclosed scratch probe (`probe.py.txt`, run 2026-10-19, wheel `main-21e761c3`); there is no fit.
- **Rows:** at the step-1b Hartono-targeted λ = 1 endpoint (`density-sweep-1b/hartono-fit/fit/usable-budget-endpoint.json`, on branch `amendment-6-step1b`), an MEA–water slope coefficient with b = 0 was added. The 55 stage-2 `neutral-mea-water` rows were then evaluated through `fit_observations.stage2_rows` and `predict`: 50 Cai boiling-temperature and vapor-water rows, and 5 CO₂-free densities.
- **Perturbations:** the rows were evaluated at the base, at k + 0.002, and at b = +10 K.
- **Solve:** linear least squares on (k, b), with the stage-2 scales (1 K, 0.01 mole fraction, 0.5 kg/m³) and density weights of 1, 3 and 10.
- **Compute:** 1.12 s wall, 1.02 CPU-s.

**Result (linear prediction).**

| Density weight | Δk | b, K | CO₂-free errors at 298 / 313 / 323 / 343 / 353 K, kg/m³ | Cai cost (base 91.33) |
|---:|---:|---:|---|---:|
| 1 | −0.00503 | −6.91 | −0.536, −0.051, +0.003, +0.440, +0.377 | 91.37 |
| 3 | −0.00534 | −7.66 | −0.505, −0.027, +0.022, +0.449, +0.381 | 91.46 |
| 10 | −0.00555 | −9.04 | −0.473, −0.011, +0.028, +0.434, +0.356 | 92.26 |

- **Sensitivities:** per 0.001 in k, the density errors shift −0.07 to −0.09 kg/m³ at all temperatures. Per +10 K in b, they shift −0.12, 0.00, +0.08, +0.24 and +0.32 kg/m³ from 298 to 353 K.
- **Reading:** together, k and b can bring all five rows within 0.5 kg/m³ at about a 1 % increase in Cai cost.

**Limits.**
- This is a linear prediction at one endpoint; it needs a nonlinear stage-2b fit to confirm.
- The CO₂-free densities also depend slightly on the ion parameters, through trace MEAH⁺ from MEA protonation.
- The final candidate must therefore be checked against these rows as well.
