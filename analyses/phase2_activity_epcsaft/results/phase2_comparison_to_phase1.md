# Phase 2 Comparison To Phase 1

Phase 1 is an ideal/apparent Smith-Missen reproduction baseline. It uses the documented Phase 1 reaction constants without ePC-SAFT activity coefficients.

Phase 2 uses the nine-species liquid basis and one ePC-SAFT parameter artifact. Austgen Table V verifies R1-R5 on the unsymmetric mole-fraction activity H3O+ basis, so the reaction constants are source-ready fixed inputs. The current Phase 2 output is still a convention-safe problem definition and readiness audit, not a claimed activity-based equilibrium result, because the pinned upstream ePC-SAFT package lacks the required native activity-coupled speciation backend tracked in upstream issue #115.

Next required implementation: generate pressure/speciation tables only after upstream issue #115 lands in a pinned ePC-SAFT dependency, or keep the package blocker explicit.
