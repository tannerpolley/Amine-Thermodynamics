# Reactive Speciation Feasibility Result

**Conclusion:** Feasible as an MEA-side diagnostic solver and seed generator; not suitable as a regression execution lane in its current form.

The experiment constructed the nine-species MEA model through the clean provider's public parameter-record API, evaluated a documented mole-fraction activity standard state, solved three fixed 313.15 K and 30 wt% MEA states, compared every species and residual with pinned `epcsaft` 1.5.2, and repeated every solve from two perturbed seeds.

## Results

| CO2 loading | Maximum clean-versus-pinned mole-fraction difference | Maximum three-seed spread | Nominal activity calls | Nominal public EOS calls | Nominal elapsed time |
|---:|---:|---:|---:|---:|---:|
| 0.20 | 0.00202 | 1.3e-16 | 58 | 1624 | 8.7 s |
| 0.40 | 0.00481 | 1.6e-15 | 58 | 1450 | 7.8 s |
| 0.60 | 0.00627 | 1.1e-13 | 41 | 1070 | 5.7 s |

All nine solves passed the fixed residual tolerance. The largest final residual was 2.7e-10, and the repeat-seed solutions were numerically indistinguishable at the scale relevant to the manuscript.

The infinite-dilution reference log fugacities agreed with the pinned lane within 3.3e-4. Component log activity coefficients differed by as much as 0.412, and the largest reaction-combination difference was 0.438 in log units. The clean model therefore demonstrates a usable public activity interface and stable MEA-side solve, but it is not numerically interchangeable with the pinned 1.5.2 model without a dedicated upstream parity/validation step.

## Decision

Keep this solver as a small diagnostic oracle and possible initializer. Do not use it to fit or promote parameters, admit regression execution, or replace the immutable final-integration lane. The dominant cost is the public pressure-to-density solve: each nominal solve required roughly 1,100–1,600 public EOS evaluations and took about 6–9 seconds, versus about 0.04–0.06 seconds for the pinned native reactive solver. A production path would need a provider-supported density continuation or direct reactive sensitivity contract rather than this finite-difference Python loop.
