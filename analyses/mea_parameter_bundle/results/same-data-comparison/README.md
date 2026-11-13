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

## Published 2026 model: qualification stopped

`polley-2026-parameters.json` is the unchanged record from commit 7035362,
SHA-256 868a501831b87e95dedf18ce40e9e7ac949f7c6a4aaf137f717cc493ecfcb7be.
`appendix-check.json` confirms the specified ion, pair and reaction values against
Polley and Hedengren (2026), Appendix B, Tables 7–9 and Eqs.124–126. The historical
Engine Born implementations (hashes retained there) and MEA's historical caller
supply the shell and dielectric-saturation form with dimensionless coefficients
(1,1), matching Eq.9 and Appendix B Eqs.122–123. Engine accepts explicit values;
MEA's caller supplied them, rather than the Engine silently defaulting them.

The translated record adds only `c_shell=1.0` and `c_dielectric=1.0` and has SHA-256
cbf9727810cb76ecf6ae6702a5e4285d2e8ba731acb4c7d90925dbc620872dc1.
Wheel 391dfe5d then refuses it with:

> missing cross association or no_cross_association: carbon-dioxide/monoethanolamine

This is the first refusal after the authorized Born translation. The association
model was not changed to bypass it. Zero pressure, species, heat, density,
heat-capacity or stability observations were scored for the published model.
No first differing numerical quantity exists, because mapping construction stops
before evaluation. `qualification.json` preserves the earlier missing-c_shell
refusal; `translation-qualification.json` records the new refusal and both hashes.

Retained exact-record per-observation references exist in
`calibration-misfit/variant-states.csv` and `speciation-states.csv` under 868a5018.
The reference CSV and original state packet were retrieved with `git show` from
8d6e261, which first wrote the pressure reference; their hashes are retained in
`translation-qualification.json`. The decompressed packet matches its recorded
86f60041… hash. `qualification-reference.csv` preserves the full variant table;
only its `adopted` rows qualify as references. Refusal prevented comparing those
values. No historical wheel was built or run. The pressure/species pass limit
remains 1e-8 relative (#339/#255); heats do not gate, but no heat differences
could be evaluated here.

The adoption receipt's aggregate statistics were scored with five reaction
shifts, whereas the published record retains only R2/R4/R5. Those aggregates
are **not an exact-record reference**. R1 and R3 shifts omitted from the published
record are -0.000679939316315813 and -0.21602074127857132 kJ/mol.

## Reproduction and scope

Run each command in an `agent-heavy` background shell:

```
uv run --no-project --python <pinned-environment-python> analyses/mea_parameter_bundle/scripts/same_data_comparison.py
uv run --no-project --python <pinned-environment-python> analyses/mea_parameter_bundle/scripts/same_data_comparison.py tables
```

The first command preserves the explicit-Born refusal and reference provenance;
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
