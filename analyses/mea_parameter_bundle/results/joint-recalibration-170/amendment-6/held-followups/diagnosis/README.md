# Held start B: Engine refusal at the frozen start (#170, 2026-10-19)

**Result.** At the frozen #172 larger-dV F1-B start (rebased onto the Held 16-coordinate declaration,
`../../inputs/held-followups/held-B-start.json` before the owner's start change), the stage-6 information
evaluation stops before any solve with `ParameterError: NOT_RUN: rank-deficient declared equations; nonlinear
solve not run`. This is a numerical refusal by the Engine's pre-solve check, not a fitted result.

**Where it comes from.** Engine `21e761c3`, `engine/native/equilibrium/request_compile.cpp` (end of
`compile_with_basis`): the declared-equation Jacobian is evaluated at `compiled.generic_point()` with the model,
its rank is taken by full-pivot LU, and a nonzero nullity sets `feasible = false`;
`gibbs_minimizer.cpp:778–790` (`structural_result`) then returns NOT_RUN. Because the Jacobian is evaluated with
the model's parameters, this "structural" test depends on parameter values.

**Which rows.** `rows.py.txt` bisects all 307 objective rows (71 evaluations, 21.8 s): 25 CO₂ partial-pressure
rows refuse individually, `vle_obs_0186–0193-pco2` (313.15 K) and 17 rows among `vle_obs_0119–0142-pco2`
(`rows.json`). Every other row evaluates.

**Which parameters** (`probe.py.txt`, one evaluation of all rows per variant; `*.json`, `*-time.json`):

| Variant of start B | Outcome |
|---|---|
| as built | refuses (NOT_RUN) |
| start A's ion parameters (components and pairs) | all rows available |
| start A's pairs only / start A's components only | all rows available |
| start A's value for any single changed entry (pairs 20, 24, 28; components 3, 4) | all rows available |
| start A's chemistry (R2/R5 correlations) | coordinate start outside B's rebased bounds (not informative) |
| carbamate–MEAH⁺ k_ij × (1 − 1e-6), i.e. −0.999999 | refuses |
| carbamate–MEAH⁺ k_ij × (1 − 1e-2), i.e. −0.99 | all rows available |
| carbamate dispersion energy × (1 + 1e-9), × (1 + 1e-3) | refuses |
| MEAH⁺ Born diameter × (1 − 1e-3) | refuses |

The refusal therefore covers a region around B's values with carbamate–MEAH⁺ k_ij at its −1.0 lower bound
(frozen that way in #172), not a single point. Start A's joint endpoint also reached k_ij = −1.0, with its own
other values, and replayed normally.

**Decision (owner, 2026-10-19).** Start B from the frozen values with carbamate–MEAH⁺ k_ij = −0.99, 1 % inside its
bound, recorded as a start modification; the optimizer may return to −1.0. If the fit meets the same refusal on
the way, B is reported as failed with this cause.

**Limits.** This identifies the trigger, not the Engine-internal reason the generic-point Jacobian loses rank
there. The first release attempt is retained under `../held-B-frozen-kij-refused/`.
