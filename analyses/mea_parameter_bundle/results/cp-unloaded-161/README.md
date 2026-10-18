# Unloaded 30 wt% MEA Cp admission on Engine 21e761c3 (#161)

**The nominally unloaded #124 state now passes the unchanged 1e-9 raw-residual
gate, and its equilibrium Cp is available.** On the #124 record (`756fec50`),
the worst raw row is **8.5e-14** (it was −7.374e-9 on wheel `48a639e7`).
Equilibrium Cp is **3.8436308 kJ/(kg·K)** on MEA's feed-mass basis and
3.8436879 on the request's molar-mass basis. The second value is the Engine's
number. On the current selected record (`7b0b4bb5`), the same state also passes
(5.7e-14) and gives **3.8437419 kJ/(kg·K)**, −0.333 % from Hilliard's 3.8566.

The 1.5e-5 to 1.6e-5 relative gap between MEA's and the Engine's Cp values
comes entirely from the feed-mass basis, not from the wheel. MEA divides
d(nH)/dT by feed mass computed with `verify_solution_heat_capacity.MOLAR_MASS`
(MEA 61.0831, water 18.01528, CO₂ 44.0095 g/mol). The Engine #261 test uses the
request's `molar_masses_kg_per_mol` (61.0805, 18.0152, 44.0084 g/mol). That
makes MEA's mass larger by 1.4858e-5 (unloaded) and 1.5597e-5 (loaded). On the
same solved state, the request-basis value matches both Engine numbers within
2.1e-9 relative, which is inside their eight-digit rounding.

| Record | Loading (model) | Worst raw row | Admitted (≤1e-9) | Cp, MEA basis | Cp, request basis | Engine #261 | MEA prior | Hilliard |
|---|---:|---:|:-:|---:|---:|---:|---:|---:|
| #124 `756fec50` | 1e-5 | 8.53e-14 | yes | 3.8436308 | 3.8436879 | 3.8436879 | 3.8436308¹ | 3.8566 |
| #124 `756fec50` | 0.358 | 1.28e-13 | yes | 3.3147181 | 3.3147698 | 3.3147698 | 3.3147181² | 3.4707 |
| current `7b0b4bb5` | 1e-5 | 5.68e-14 | yes | 3.8437419 | 3.8437990 | — | — | 3.8566 |
| current `7b0b4bb5` | 0.358 | 1.42e-13 | yes | 3.3426878 | 3.3427399 | — | — | 3.4707 |

All Cp values are in kJ/(kg·K). ¹ #161 scratch replay on wheel `36485a88`
(#124 design comment); this run differs from it by 4.9e-11 relative.
² `density-cp-160/cp-124-assessment/loaded-80C-decomposition.json` on wheel
`48a639e7`; this run differs from it by 3.0e-9 relative. Model minus Hilliard,
on MEA's basis: −0.336 % and −4.494 % for `756fec50`, and −0.333 % and −3.688 %
for `7b0b4bb5`.

**Numerical verification.** Every state, including the sixteen re-solved
neighbours at ±0.1 K and ±0.05 K, passes the unchanged gate. The Cp action
agrees with the centered enthalpy slope of re-solved neighbours to
3.3e-9 relative (unloaded) and 8.3e-9 to 8.4e-9 relative (loaded) at 0.05 K. The
0.1 K differences are about four times larger, as expected for a centered
difference, so both the 1e-6 limit and the half-error rule pass. Classified
residuals are 4.9e-15 to 1.0e-14. Independently re-evaluating the raw rows at
the returned coordinates gives the same maxima. The unloaded reaction
response, equilibrium minus frozen Cp, is 6e-7 kJ/(kg·K) for `756fec50` and
1.4e-5 for `7b0b4bb5`. So at loading 1e-5, Cp is essentially the
frozen-composition liquid value.

## Basis and conditions

- 353.15 K, 101325 Pa, one nine-species liquid, reactions R1 to R5 of each record.
- Feed: 7 mol MEA/kg water through the #124 generator. That is the Amundsen
  mass-fraction path at w = 7·0.0610831/(1 + 7·0.0610831), about 7.00027 mol/kg
  on the request masses. Loading 1e-5 mol CO₂/mol MEA is a numerical proxy for
  zero, with seed scale 0.01. The loaded state is α = 0.358, as in Hilliard
  App. G.2.
- The unloaded request rebuilt by the current code equals the archived
  `cp-124-assessment/solution-request-0.0.json` (`bc8a03e1…`) for both
  records. The two records share the same reaction laws.
- Ideal-gas calorics: `data/reference/MEA/thermal/physical-ideal-gas-calorics.json`
  (`c94d504e…`), the same record as the Engine's `mea-zero-inventory`.
- The record `756fec50` predates #191, and wheel 21e761c3 refuses it without
  the CO₂/MEA `topology.no_cross_association` declaration. `evaluate.py` adds
  that declaration in memory, in the same form as the selected record, after
  asserting that no CO₂/MEA association edge exists. The file bytes and hash
  are unchanged. The #191 adoption showed that this declaration leaves
  predictions bitwise unchanged.

## Identity

- Engine wheel `main-21e761c318c2ac5b555a245365c844d38a93e4cb`, SHA-256
  `d2f61e3a5961b859151fbe0487f4ab633405b11620d9dd64682656a68a110357`. Its
  commit contains the #261 fix `9c31cb9a` as an ancestor. `fit_campaign.verify`
  checked the 12 installed `epcsaft/` files byte-for-byte against the wheel,
  plus all input hashes. NumPy 2.4.4, SciPy 1.17.1, Python 3.13.
- Producer: [`evaluate.py`](evaluate.py), SHA-256 `141173dc…`, recorded in `summary.json`. It composes the existing
  `verify_temperature_reference.solve/request_at`, `verify_reference_calorics.first_actions/record`,
  `shared_evaluation.source_feed_request/corrected_request` and
  `fit_campaign.verify/load/write`. No shared script changed.
- Command, from the repository root, with one numerical-library thread
  (about 2 s):
  `OMP_NUM_THREADS=1 nice -n 15 .venv/bin/python analyses/mea_parameter_bundle/results/cp-unloaded-161/evaluate.py`
- Values: [`summary.json`](summary.json).

## Limits

This is numerical verification of admission and of the equilibrium Cp action
at one temperature and one pressure. The Hilliard comparison is a conditional
prediction for these records, not physical validation. Three things are not
done here: a proxy-convergence check (1e-6 against 1e-7, required later by the
#124 joint-refit design), the C5 replay, and any parameter change.

Engine #261 also reported ten MEA states, at nominal loadings 1e-7 and 1e-5
over 313.15 to 393.15 K, that now reach raw residuals of 5.7e-14 to 2.8e-13.
They were built in the Engine's own comparison and are not declared by any MEA
script, so they were not rerun here.
