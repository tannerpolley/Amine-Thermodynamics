# Published MEA models on common observations — issue 339

The exact common-data result is the 19 Ma'mun et al. (2005) Table 2 pressures
at 393.15 K and 30 mass% MEA. Current-record pressure AARD is **19.432074704%**,
against published **21.03%** (Baygi–Pahlavanzadeh PC-SAFT), **39.96%**
(Najafloo–Zarei SAFT-HR, reported pressure AAD%), and **13.5%** (Zhang eNRTL).
The first three
comparisons use observations not fitted in the corresponding ternary pressure
objective; Zhang fitted them. Najafloo's methods describe prediction but its
conclusion says ternary data determined parameters; this ambiguity remains.
These different data roles do not rank accuracy under identical assessment.

For this work, Baygi and Zhang, the deviation is 100/n times the sum of absolute
pressure errors divided by measured pressure. Najafloo Table 5 and §3.3 report
pressure AAD% without defining its averaging formula or denominator. Its
equivalence to the mean absolute relative deviation is inferred, not verified;
Eq. 2 defines the pure-component fitting objective, not this pressure metric.
Pressures in `matched-pressure-rows.csv` are Pa; the original
Ma'mun table and source CSV use kPa. All 19 source pressures, their order and
temperatures are checked, including two distinct observations at loading 0.3424.
Source loadings 0.155–0.4182 mol CO2/mol MEA map to 0.1549031–0.4181084 in the
retained analytical-feed calculation. This follows Part I's composition handling;
other authors' conversions and rounding are not independently reproduced.

`matched-score.json` binds the exact retained current-record predictions and
source rows by hash. They were evaluated with wheel 391dfe5d, SHA-256
0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b.
The comparison recalculates deviations only; it neither refits nor reruns an EOS.
`published-deviations.json` owns transcribed published source/property scores;
`property-tables.md` presents them without estimating missing subsets or counts.
Each entry separates observation role from parameter origin and prior data use
in its role note. Unresolved entries identify missing membership evidence;
Baygi’s combined binary entries retain fitted Cai and predicted Park–Lee
membership without inventing separate scores. Najafloo’s binary observations
were not fitted but informed retaining zero interaction (§3.2).
`source-research.json` records primary-source identities, methods, exact-match
verification and unresolved source detail. Missing fitted-parameter totals are
reported as unknown rather than inferred. No full paper text is published.

## Published 2026 model: qualification fails at the first pressure

The original record from MEA commit `7035362` has SHA-256
`868a501831b87e95dedf18ce40e9e7ac949f7c6a4aaf137f717cc493ecfcb7be`.
The complete translation has SHA-256
`be66f6cf9df77201a632d73a3c3e341f66ce7fc77b69c3d657288f4c1899a76b`.
`polley-2026-explicit-born.json` preserves the earlier two-field translation;
`polley-2026-explicit-defaults.json` is the complete translation used here.

Before filling, inspection of the pinned wheel's source at `391dfe5d`
(`engine/src/epcsaft/parameters.py` and
`engine/native/surface/parameter_builder.cpp`, required-field checks and cross
association check) found exactly these three missing required declarations.
The nine components have their required scalar or temperature-law inputs;
all 29 consumed unlike dispersion pairs are explicit, while seven same-sign
ion pairs are excluded by the declared model. Water's diameter is a correlation.
The only site-bearing component pair without an edge is CO2–MEA.

| Declaration | Filled value | Original Engine source locator | Paper locator |
|---|---|---|---|
| electrolyte `c_shell` | 1, dimensionless | `f2d1e01f4:engine/native/contributions/born.hpp`; MEA `7035362:analyses/mea_parameter_bundle/scripts/shared_evaluation.py:MODEL_RUNTIME_DEFAULTS` supplies 1 | Appendix B p.17, extension coefficients; Eqs.122–123 |
| electrolyte `c_dielectric` | 1, dimensionless | Same Born implementation and MEA caller as above | Appendix B p.17, extension coefficients; Eqs.122–123 |
| `topology.no_cross_association`, CO2–MEA | all cross site edges inactive, native value 0 | `f2d1e01f4:engine/native/surface/parameter_builder.cpp:161,297–298,425–426`; reference Engine `443a9da4`, lines 165,342–343,481–482 | Appendix B p.17 and Table 10: only listed pairs active; no CO2–MEA pair |

The Born values are explicit MEA caller inputs, not silent Engine defaults.
The historical Engine initializes the association matrix to zero and activates
only declared edges and combining rules. The new declaration preserves that
behavior. The paper PDF (Zotero attachment `QHI67GZ8`) was checked directly;
its SHA-256 remains `c3d35ca54f7f4ac54727d790f18e6c4a90e271bb3f01d5a4d146b85755489459`.
Appendix B, Tables 7–10, Eqs.122–126 and the parameter-provenance paragraphs
were read. No disagreement was found. `translation-table.json` retains the
full table, hashes and source-file hashes; `appendix-check.json` owns the prior
ion, pair and reaction-value checks.

### Exact-record reference and first difference

The retained `qualification-reference.csv` is reused, not regenerated. Its 371
`adopted` rows name the original `868a5018…` record and wheel SHA-256
`b66c7b962541a586f5ec50043a5e8b4e62cf52e24eaec02ef33f43e558762a58`.
MEA commit `8d6e261` first retained these values through
`analyses/mea_parameter_bundle/calibration-misfit/compare.py`, consuming the
read-only adopted `probe.py` evaluations. The shared evaluator in that commit
identifies Engine `443a9da492fd5ac7724525945d108c6a2a854d51`.
The original packet was retrieved from that same commit. Its decompressed
SHA-256 is `86f60041b28ec4493729b04c0238f44e86fba4becf33d6ddf47d86b7efb82448`;
the reference CSV SHA-256 is
`8242648f41c087d1a9acf810b3f9e35c21bbb021bad20ace38968a31ac8a9916`.
No historical wheel was built or run for this continuation.

One qualification replay used pinned Engine `391dfe5d`, wheel SHA-256
`0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b`.
The fully translated mapping loads. The first comparison fails:

| Quantity and state | Historical reference | Pinned-wheel translation | Relative difference | Required limit |
|---|---:|---:|---:|---:|
| CO2 partial pressure / Pa, `vle_obs_0119`, Hilliard2008, 313.15 K, loading 0.1529030581 mol/mol | 4.394811538107617 | 4.394810386862543 | 2.6195550451 × 10⁻⁷ | 10⁻⁸ |

The absolute difference is −1.151245074 × 10⁻⁶ Pa. The relative limit is from
#339/#255. This numerical reproduction failure does not measure disagreement
with experiment. It is the first and only compared quantity, not a maximum
over all reference pressures or species. The retained `qualification-state.json`
and `translation-qualification.json` contain the state and comparison.

The owner's stop rule applies: no species or later pressures were compared,
no heat or heat-capacity differences were obtained, and zero Part I observations
were scored. There is no 2026-model deviation beside `f8f64820…` for any Part I
group and no stability-search result. No historical-wheel fallback was used.
A scalar first difference is shown as a table because a plot adds no trend.
The cause of the cross-wheel difference is unresolved; translation acceptance
alone does not establish numerical equivalence or physical validation.

The adoption receipt's five-shift aggregates are not an exact-record reference;
the published record retains R2/R4/R5 only. The omitted R1 and R3 shifts were
−0.000679939316315813 and −0.21602074127857132 kJ/mol.
Independent delivered review returned **Supported** at commit `e429df4` for
the translation and qualification stop, with no required corrections
(`part1-review.md`). This does not qualify scoring or promote manuscript use. Notebook HTML rendered with `--no-execute` and
contains the retained first difference. The site home-page refresh could not
complete because `snakemake` is unavailable. Standard refresh would alter the
protected site metadata, so direct Quarto rendering was used; the metadata
was not changed.

## Reproduction and scope

Run each command in an `agent-heavy` background shell:

```
uv run --no-project --python <pinned-environment-python> analyses/mea_parameter_bundle/scripts/same_data_comparison.py
uv run --no-project --python <pinned-environment-python> analyses/mea_parameter_bundle/scripts/same_data_comparison.py tables
```

The first command reproduces the full translation and stops at the first failed comparison;
the second rebuilds the matched score and property tables from retained values.
There is no process pool; evaluation uses a single worker with BLAS/OpenMP
threads set to one. The script reuses the existing MEA evaluator and does not
implement thermodynamic equations. Base for the 200-line gross executable budget:
13bb6fbb7aebfb2ca642e6061f6f32f9167d6f35.

These are fixed-parameter model-to-measurement deviations, not uncertainty
intervals or independent physical validation. Published aggregate values retain
each author's data processing. Source uncertainties are not converted into
agreement thresholds, and source selection differences are not approximated.
The Hong model belongs to #246; #341 owns any later adopted-record replay.
Manuscript promotion requires the owner's confirmation of a reviewed notebook.
