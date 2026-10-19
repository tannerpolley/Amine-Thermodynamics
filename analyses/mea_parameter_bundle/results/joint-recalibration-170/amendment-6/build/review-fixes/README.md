# Four authorized review fixes — 2026-10-19

Implemented against `242d788`, with **21 gross added campaign lines**, carrying
the prior 1,300 charge to **1,321 of 1,325**. Authority is
[#170 comment 6278338236](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6278338236).
Deletions and replacements receive no credit. Implementation is complete;
**native Cp numerical qualification is incomplete** after two failed attempts.
No fit was run, and this work establishes no physical validation or parameter adoption.

| Item and final owner (script paths relative to `analyses/mea_parameter_bundle/scripts/`) | Gross additions | Qualification |
|---|---:|---|
| Inherited reaction totals, `fit_campaign.py:620–625` | 5 | Actual persistence statements executed for 14/12 coordinates in reversed order, zero/nonzero inherited totals and zero/nonzero increments: eight cases passed; eight corrupted linked R5 coefficients rejected. |
| Final phase-state persistence, `final_evidence.py:488` | 1 | Actual `family_job` and classifier with synthetic states: both `RuntimeError` and `SystemExit` during stability retain `final` and classify unresolved. This is persistence qualification, not a real timeout or phase calculation. |
| Declared Cp feeds, `heat_evidence_170.py:81–97,279,296–304` | 11 | Actual Cp function and main assessment expression pass a synthetic feed/action check: both records use four source states, exactly 7 mol MEA/kg water, and both 1e-6/1e-7 proxies for each unloaded temperature. Native attempts returned no values. Explicit-document callers now supply `declaration=` with their fit declaration. |
| No-heat assertion, `fit_observations.py:113–116` | 4 | Actual no-solve `stage6_rows` construction: 262 rows, 215 reacting / 254 total positive, exactly eight Vinjarapu zeros in table and observation weights; ninth zero and table/observation mismatch rejected. |

Reaction convention: at Engine commit `21e761c318c2ac5b555a245365c844d38a93e4cb`,
`engine/native/regression/coordinates.cpp:29–44` defines the enthalpy direction
as `(1/(R*T_pivot), -1/R, 0, 0)` and R5 `a_k = -b/ln(10)`.
Thus the inherited contribution to `a_k` is positive and is removed when
recovering the unshifted reference. The zero-increment inherited case writes
`R5_unshifted_a_k = 2472.3956785580126`, with totals
`R2 = 2719.454475528878` and `R5 = 2950.799195553639 J/mol`.
The executable assertion checks the serialized R5 reference plus total against
the endpoint coefficient; the probe explicitly checks both named totals.

The Cp observations are the four `direct_rows` in `inputs/revision-3/tied-fit.json`:
318.15/353.15 K × source loadings 0/0.358, at 101325 Pa. Their source values are
3.7195, 3.3675, 3.8566 and 3.4707 kJ/(kg K), respectively. The fit feed's nominal
zero uses 1e-6; the assessment also retains 1e-7. These are declared inputs,
not newly calculated physical results.

| Timed invocation | User / system CPU-s | Wall-s | Outcome |
|---|---:|---:|---|
| No-heat object construction | 7.15 / 0.09 | 7.26 | Passed; Kiepe continuation disabled in memory for construction only, with a solve-forbidden sentinel. |
| Four-state Cp information, proxy 1e-6 | 0.39 / 0.05 | 0.45 | Signal 8, shell exit 136; zero predictions returned. |
| Four-state Cp information, proxy 1e-7 | 0.38 / 0.06 | 0.45 | Signal 8, shell exit 136; zero predictions returned. |
| Requested pytest command, once | 18.11 / 0.48 | 12.26 | 94 passed, 17 subtests passed, two known failures. |

Both failed Cp attempts called `reg.differentiate` with four observations and
an empty coordinate list. The cause of signal 8 was not diagnosed. Both attempts
are retained; the two-call limit precluded a retry. No native Cp values,
proxy-relative changes, frozen Cp values or centered-enthalpy comparisons are
claimed. The pure-Python probes were not timed. Total measured time is
20.42 wall-s and 26.71 CPU-s, including pytest; the two Cp attempts account for
0.90 wall-s and 0.88 CPU-s. The parent charges program time at merge.

The requested pytest run used the main-checkout `.venv/bin/python` and failed only:

- `test_campaign_routing.py::test_campaigns_use_candidate_reactions_and_retain_failures`
- `test_shared_evaluation.py::test_pinned_engine_state_and_cached_replay`

Read [persistence-results.json](persistence-results.json),
[cp-feed-results.json](cp-feed-results.json),
[no-heat-results.json](no-heat-results.json),
[cp-attempts.json](cp-attempts.json), and [pytest.log](pytest.log).
The disclosed `.py.txt` probes are retained beside their outputs;
[commands.json](commands.json) records exact argument lists and script hashes.
The Engine environment is the owner-specified `tmp/a6/venv`, with wheel SHA-256
`d2f61e3a5961b859151fbe0487f4ab633405b11620d9dd64682656a68a110357`.
`fit_campaign.verify` checked the installed package against the copied wheel.
The stage-2b worktree was read only for that wheel copy; nothing there was written.

[campaign-accounting.json](campaign-accounting.json) owns this increment's count.
The final tree has 309 nonblank/noncomment added campaign lines against `f387725`;
12 previously charged replaced lines are carried, yielding 321 new plus the
historical 1,000. Both campaign ledgers now record 1,321 / 1,325. Independent
delivered review and the broader campaign qualifications remain with the parent.
