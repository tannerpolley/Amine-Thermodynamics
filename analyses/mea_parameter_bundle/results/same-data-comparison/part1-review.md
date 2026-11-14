# Part 1 delivered review — 2026-11-13

**Supported**, for the full declaration translation and owner-directed qualification
stop at commit `e429df4e8e91b2882b19e9524688c55ac926553f`. Independent read-only
review by the configured Reviewer (GPT-6 Astra, high effort). Required findings:
none. Optional suggestions: none. No files or EOS calculations were changed or
rerun by the reviewer.

The review independently checked the original/translated mappings, all three
missing required declarations, pinned and historical Engine source, the actual
Zotero PDF Appendix B, the reference and input hashes, retained state, comparison
arithmetic, notebook source and rendered notebook HTML. Removing the three
translated declarations reproduces the original mapping exactly. The cumulative
executable additions are 144/200 lines against `13bb6fbb`.

The first compared CO2 partial pressure (`vle_obs_0119`, Hilliard2008, 313.15 K,
loading 0.1529030581 mol CO2/mol MEA) is 4.394810386862543 Pa on the pinned wheel,
against 4.394811538107617 Pa in the exact-record historical reference. The
relative difference is 2.619555045102473e-7, above the owner-specified 1e-8 limit;
the signed difference is -1.1512450734940671e-6 Pa. The retained solve reports
convergence, one attempt and no cache hit. Stopping with zero scored observations
is supported by the owner's decision on issue #339, comment 6866044132.

This supports numerical reproduction failure at the first pressure and the
resulting stop. It does not qualify the translated model for scoring, diagnose
the cause, establish model-to-measurement deviations, or establish physical
validation. Species, subsequent pressures, heats, heat capacities and stability
were not compared. The site-home refresh limitation is disclosed and protected
site metadata is unchanged. Further numerical work requires the owner's next
direction. Manuscript promotion is not established.

The later closeout change records this review outcome only; scientific values,
translation and interpretation remain those reviewed at `e429df4`.

## Full reference comparison and diagnosis — 2026-11-13

**Supported** at frozen commit `e3fdf0f69404ea3176b6a602676721202edf37e9`,
compared with `0c7760437cae1e08ee5f10d4924e4012c49a79d3`. Independent read-only
review by the configured Reviewer (GPT-6 Astra, high effort). Required defects:
none. This supports the bounded numerical comparison and owner-required stop;
it does not qualify Part I scoring or manuscript promotion.

The reviewer independently recomputed relative differences and distributions,
checked identities against the historical reference, and verified retained input,
result and disposable-probe hashes. Normal replay returns all 371 values;
362 historical numeric values permit comparison (239 pressures, 123 species).
Nine historical blanks remain excluded. Normal-reference maximum absolute
relative difference is 3.6865179709e-7, with uniform signs by quantity.

The finite-reference restoration returns all 362 comparable values, median
absolute relative difference 2.7255975255e-13 and maximum 2.7081559217e-11.
341 rows meet 1e-12 and 21 exceed it. The first exceedance is `vle_obs_0129`,
8.6828322310e-12; the largest is `canonical:vle_obs_0171`, historical
1228.0644953749538 Pa versus restored 1228.0644953416959 Pa.

Source inspection confirms the historical `contractions.back()` and 1e-14 mol/kg
witness, and Engine `3b893fc2c` replacing finite reference with analytic insertion.
Both versions keep the 1e-10 equation-row residual tolerance; this is not a
relative-output guarantee. The disposable probe follows the documented correction.
Historical bicarbonate-labelled targets aggregate bicarbonate and carbonate
mole fractions, as does the replay. The leading difference is attributed to
the reference calculation; the remaining discrepancy is not isolated. The
notebook states that distinction and stops faithfully under the owner's rule.
Further diagnosis is not required by this review.

Optional presentation correction: a missing blank line before the all-row
heading rendered literal `###` text. The implementer inserted that blank line
and rendered the notebook again. Numerical evidence is unchanged.
Executable additions: 177/200 against `13bb6fbb`. Protected site metadata is
unchanged. Home-page refresh remains unavailable because `snakemake` is missing.
No files were edited or Engine evaluations run by the reviewer. Review covers
numerical evidence and source attribution, not physical validation or the
unchanged literature comparisons. Next stage: stop, pending owner decision.
