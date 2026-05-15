# Phase 2 Comparison To Phase 1

Phase 1 is a retained ideal/apparent Smith-Missen baseline audit. It uses documented reaction constants without ePC-SAFT activity coefficients, but it is not an independent completed reproduction.

Phase 2 uses the nine-species liquid basis and one ePC-SAFT parameter artifact. The current Phase 2 output is a source-verified problem definition and bounded-incomplete scaffold, not a claimed activity-based equilibrium result, because the pinned upstream ePC-SAFT package lacks the required native activity-coupled speciation backend tracked in upstream issue #115.

Next required implementation: generate pressure/speciation tables only after upstream issue #115 lands in a pinned ePC-SAFT dependency, or keep the package blocker explicit.
