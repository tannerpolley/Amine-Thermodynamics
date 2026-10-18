# Engine 84ca269d unchanged-record requalification

All four unchanged records reproduce their retained objective costs and weighted residuals within the two $10^{-8}$ limits, with identical observation definitions. This is numerical verification. No parameters were fitted or adopted.

| Record | Relative cost difference | Maximum weighted-row difference | Result |
|---|---:|---:|---|
| water | 8.421666383e-13 | 4.763550665e-13 | Pass |
| neutral-mea-water | 0 | 0 | Pass |
| co2-water | 0 | 0 | Pass |
| current | 5.388359388e-13 | 3.675491023e-10 | Pass |

Engine commit `84ca269dfa0c7068417a1c4c326acae276d4d965`; wheel SHA-256 `98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a`. A fresh Python 3.13.14 environment contains NumPy 2.5.4 and SciPy 1.18.1. The existing calculation owners verify input hashes and installed Engine files against wheel bytes. Frozen declarations and all row values are retained here. The four parameter records are unchanged.

The objective counts are 63 water, 53 MEA–water, 39 CO₂–water and 149 common comparison quantities. The water assessment also retains 42 Cp and 39 saturation states; the comparison retains 14 Arcis heats outside the common objective. Each native call has a 60 s wall limit, with `nice -n 10` and single-thread BLAS/OpenMP.

The qualification charge is 13.950683000 aggregate process-plus-child CPU-s and 14.095519601 active wall-s, allocated once to Route 1's 7800 CPU-s / 600 s precursor block. GNU time's final-call rounding is charged conservatively by 0.02 CPU-s and 0.01 wall-s. Two comparison-reader invocation errors are retained in `summary.json` and failure files: the optional scale on log rows and the declaration's `baseline` ID. Neither changed a prediction, tolerance, parameter record or observation. The already calculated CO₂–water rows were reused for the completed comparison.

Cumulative charge at this boundary: 1412.742213720 CPU-s / at least 481.436209429 active wall-s. Remaining shared allowance: at most 142587.257786280 CPU-s / 21118.563790571 wall-s. Earlier unmetered overhead remains unknown and is not assigned zero. Remaining Route 1 precursor allowance after qualification: 7786.049317000 CPU-s / 585.904480399 wall-s.

Authority: [published amendment 2](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6204801680), [merged-wheel delivery](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6205497286), and the part-1 implementation instruction. The live issue and all 22 comments were read through the execution-start comment. The local amendment text equals the published text. Implementation base is `5082ba4f03850c2bdeed2f3e0e2e8c1c0718b221`. No numerical stop condition was reached. Independent delivered review belongs to the parent.
