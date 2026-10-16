# Engine cf26a17b unchanged-record requalification

Historical evidence, superseded for further calibration by [#170 amendment 2](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6204801680) on 15 October 2026. No stopped endpoint here is adopted or supplies a start or calibration input for either amended sequence. Both sequences wait for the one merged-main wheel supplied for [Engine #557](https://github.com/tannerpolley/ePC-SAFT/issues/557), followed by its required qualification. Reuse is limited to the inputs and checks explicitly retained by amendment 2. Earlier design, next-step and pending-decision statements below describe the historical calculation; they do not authorize another ions-first fit or the I₀/S₁/I₁/S₂ sequence.

All four records reproduce their retained costs and weighted residuals at the required relative cost and absolute residual limits of $10^{-8}$. This is numerical verification; no parameters were estimated or adopted.

| Record | Relative cost difference | Maximum weighted-row difference | Result |
|---|---:|---:|---|
| water | 8.41880722e-13 | 4.56412685e-13 | Pass |
| neutral-mea-water | 6.09619669e-14 | 1.18149934e-12 | Pass |
| co2-water | 5.58114104e-14 | 2.17222074e-14 | Pass |
| current | 5.38835939e-13 | 3.67549102e-10 | Pass |

Engine commit `cf26a17b2f15bb855f30d6d56485d647b893dae8`; wheel SHA-256 `32ce708a671c24dbb0112f53bc4a18021eaa1bd10a1f04e96b9ce8d3145da52f`. Installed in a fresh Python 3.13.14 environment with NumPy 2.5.4 and SciPy 1.18.1. Each declaration verifies installed Engine files against wheel bytes and verifies every declared input hash.

Water retains 63 objective targets, 42 heat-capacity states and 39 saturation states. MEA–water retains 53 fitted and two assessment targets; CO₂–water retains all 39 Kiepe targets. The current comparison retains 149 common and 14 Arcis targets. Original round-1 and round-2 results remain in `stage3/`.

Whole-process plus child CPU is 11.251984 s; active wall is 11.278406 s. These include imports, declarations, file verification, native calls and child overhead, at `nice -n 10` with single-thread BLAS/OpenMP. Each call has a 60 s wall limit. Qualification used the existing 1200 CPU-s / 300 wall-s allowance.

Prior program charges are 1162.351879 CPU-s / at least 420.426116 wall-s. At exit: 1173.603863 CPU-s / at least 431.704522 wall-s. Remaining program allowance: at most 142826.396137 CPU-s / 21168.295478 wall-s. Earlier unmetered startup/verification overhead remains unknown and is not assigned zero.

The live issue and all 18 comments were retrieved. The published ions-first amendment (comment 6203595442) states readiness r2 Ready; the supplied execution task authorizes this work. No GitHub write, Engine edit, additional worktree or subagent was used. Independent delivered review remains with the parent.
