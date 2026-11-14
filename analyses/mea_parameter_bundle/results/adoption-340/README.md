# F2 adoption, issue #340

The owner selected F2/previous in [the 13 November decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/340#issuecomment-6871176306), from #338 (PR #351), for Part I. Its parameter document SHA-256 is `ae17803e1bcb2ca0a1970e05c7cc235d615c4d8a3a349b5afef0b0401dedefed`. This adoption performs fixed-parameter calculations on Engine commit `391dfe5d64ede5036bf160bc6ae037ad5e14af32`, wheel SHA-256 `0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b`. It runs no fit and changes no manuscript file. Independent delivered review remains with the orchestrator.

## Numerical verification

[f1.json](f1.json) retains the outgoing F0 and incoming F2 replay checks. Both have 307 available predictions, identical observation declarations, and zero maximum relative prediction and cost differences against #338. F0 cost is 148.51054565397726; F2 cost is 150.76290287953717. Costs are dimensionless half-sums of the declared squared weighted residuals. The replay limit is 1e-10 relative, from #340 and #297's same-wheel identity check.

The fresh stability search is retained in [candidate/search.json](candidate/search.json), with the comparison in [f2.json](f2.json). The three sets are the 1908-state enforced grid (including the five historically excluded states), 576-state offset grid, and 162-state census. Supplied trials are read from the single MEA [split registry](../reduced-refit/split-registry.json); its trial-content fingerprint is `72a1956398e09da220aed6756d2aa347bcef987943b85c55890ff6160bdaf65a`. No new registry is created. All 3507 resolved earlier descent compositions are evaluated against each of the 162 census parents (568134 distances). Every grid and offset state is available, with 0 splits; the census has 0 incomplete states and 0 splits. All 568134 supplied distances are available, with 0 negative values. The minimum supplied distance is 4.815477097963594e-06 (dimensionless TPD/RT); the minimum liquid distance is 3.065092460019514e-05. Raw diagnostics and supplied distances accompany the summaries. These are finite numerical checks, not a global stability certificate.

[default-path.json](default-path.json) records 307 predictions, cost 150.76290287953717, and zero maximum relative prediction difference. It compares the normal `analyses/solvent_specification_mea/run.py` output with the incoming replay by observation identity. The endpoint reference is updated to the incoming predictions and residuals; the additional direct comparison to the independently retained #338 replay prevents that reference update from concealing a declaration error.

## Choice, errors, and limits

The [#338 comparison](../reduced-refit/README.md) owns the source-law checks, uncertainties, and all fitted/not-fitted comparisons. The chosen record removes five fitted parameters compared with F0 at a cost increase of 2.252357225559905. F2 has one active bound and three conditional standard errors greater than absolute parameter value. Fitted CO2-pressure average absolute relative deviation is 11.64159%, and fitted heat deviation is 1.968941%. Not-fitted six-source pressure deviation is 24.88715%; the 15/45 mass% pressure deviations are 45.07964%/45.85891%. The #255 group rules remain reported comparisons, not adoption gates. Previously accessed comparisons are not independent physical validation; conditional errors do not estimate global physical prediction uncertainty. No absorber qualification is inferred.

## Retained owner checkpoint

[The checkpoint figure](checkpoint-figure/fig340.png), [SVG](checkpoint-figure/fig340.svg), [curve values](checkpoint-figure/curve-values.csv), [measurements](checkpoint-figure/measurements.csv), [prediction identities](checkpoint-figure/prediction-identity.csv), and [figure account](checkpoint-figure/README.md) retain the exact figure used for the choice. Its 1113 same-state comparisons have zero maximum relative difference. The original scratch producer is not rerun; the README's machine-local paths were replaced with relative descriptions.

## Defaults and historical studies

The selected JSON, solvent endpoint JSON, R2 and R5 laws in both declaration groups, declaration/endpoint hash pins, endpoint reference, and history row change in this adoption commit. The declaration carries no diameter coordinates: the selected F2 document supplies equal segment and Born diameters for MEAH+ and carbamate. The earlier parameter-table producer is frozen to F0 alongside its retained figures.

[historical-spec/](historical-spec/MEA.toml) freezes F0's normal declaration, endpoint, and reference. Its 313 file bindings were checked. Unchanged observation CSVs and caloric inputs remain with their original owner. Earlier #255/#338 searches already use the immutable #297 historical specification and explicit parameter records. MDEA #298, DEA and piperazine source readers now explicitly use the immutable F0 endpoint at `../stable-refit-255/evidence/candidate-parameters.json`; their hashes remain unchanged. The #297 retained-row reducers, display, and fixed-record replay likewise retain F0. No earlier study is rerun, rescored, or relabelled as F2. Generic default consumers continue to follow the selected document.

## Part II inheritance

[part-ii-shared-values.json](part-ii-shared-values.json) retains the completed native R1–R3 laws with reaction reference and standard-state identifiers, plus complete water–bicarbonate and water–carbonate pair nodes. The values are 0.7650000233694618 and -0.25, dimensionless, respectively. [shared-hashes.json](shared-hashes.json) identifies this file, the parameter document, and Engine wheel. The owner's rule is recorded beside the values: each Part II amine ion's Born diameter equals its segment diameter, and water–bicarbonate follows the adopted MEA record. #343–#346 own applying that rule to their amines.

## Reproduction and accounting

[inputs.json](inputs.json) supplies the outgoing/incoming records, replay references, search reference, fixed implementation base, and input hashes to the generalized #297 producer. Run each numerical command in a background shell; the existing producers use AGENT_HEAVY_CORES and single-threaded numerical workers:

```bash
agent-heavy uv run --no-sync python -u analyses/mea_parameter_bundle/scripts/adoption_297.py f1 analyses/mea_parameter_bundle/results/adoption-340/inputs.json
agent-heavy uv run --no-sync python -u analyses/mea_parameter_bundle/scripts/adoption_297.py f2 analyses/mea_parameter_bundle/results/adoption-340/inputs.json
uv run --no-sync python analyses/mea_parameter_bundle/scripts/adoption_297.py adopt analyses/mea_parameter_bundle/results/adoption-340/inputs.json
agent-heavy uv run --no-sync python -u analyses/mea_parameter_bundle/scripts/adoption_297.py default analyses/mea_parameter_bundle/results/adoption-340/inputs.json
```

Adopt checks replay and stability evidence before replacing the defaults. The code remains in `adoption_297.py`; no replacement adoption script or numerical algorithm is copied. Change accounting is measured against branch-creation main `dbe0db0bf5b065a55d4a52bcd346dcb67182e530`, with a 150 gross executable-line ceiling. The final accounting is retained in `change-accounting.json`. New code generalizes record identities, reuses #338's search and supplied-trial evaluation, coordinates defaults, exports inherited values, and checks the normal command. Superseded hard-coded assumptions remain only in the original #297 mode; configured adoption does not use its cost-improvement gate, which #340 explicitly excludes.

Initial adoption commit executable accounting: **99 gross additions / 150 allowed**, with **16 removals**, across ten executable files. `adoption_297.py` accounts for 87 additions; the remaining 12 bind historical consumers explicitly to F0. Tests have 0 additions/removals. JSON/CSV/TOML and figure files are retained inputs or generated numerical evidence, classified as other files by the accounting tool.

The populated notebook rendered to `analyses/_site/mea_parameter_bundle/notebook.html` using Quarto HTML, presentation profile, with execution disabled. The standard refresh entry was not used because it can rewrite the excluded manuscript registry; `analyses/_cse-manuscript.json` is untouched. No scientific calculation ran during rendering. Independent review and manuscript promotion remain pending.


## Historical-reader correction after independent review

The delivered review found mixed records: PZ and DEA law readers used the live F2 declaration alongside F0 parameters, while AMP's #304/#306 shared-input readers used both live files. These readers now use `historical-spec/` for their endpoint and R1–R3 laws. At 353.15 K, F0's R2 gives ln K = -14.579871440000895; F2 gives -14.552898662714009. These are dimensionless aqueous-molality infinite-dilution constants. The difference is preserved, rather than substituting F2 into the earlier studies.

The full source audit is in [historical-declaration-identity.json](historical-declaration-identity.json), with code hashes and the single frozen R1–R3 declaration. The newly bound files are:

- PZ: `analyses/pz_transfer/speciation.py` (reaction-source generation).
- AMP: `analyses/amp_transfer/kundu.py` (shared substitution and endpoint provenance), `refit_306.py` (shared endpoint).
- DEA: `analyses/dea_transfer/prepare.py` (declaration generation), `reactive.py` (shared-law check).
- MDEA workflow: `analyses/mdea_mea_workflow/scripts/transfer_probes.py` (its MEA comparison branch; the MDEA-specific declarations are unchanged).
- Historical MEA diagnostics: `analyses/high_temperature_chemistry/{qualify,run,check_heat_domain}.py`; `analyses/mea_parameter_bundle/water-ideal-gas/compare.py`, `heat-capacity-264/calculate.py`, `parameter-identifiability/calculate.py`, `solvent-domain-285/calibration.py`, and `scripts/{bicarbonate_carbonate_266,bicarbonate_carbonate_266_prepare,density_268,pressure_transfer_attribution_261}.py`.

The #261 pressure-transfer producer already uses `adoption-297/historical-spec/MEA-pre-260.toml`; its remaining reference read now uses that existing historical owner too. It is not moved to F0. Historical diagnostics with older wheel or calibration restrictions retain those restrictions; binding the source file freezes their pre-adoption default, and does not qualify or rerun those older campaigns.

Existing F0 readers retained from the first adoption commit are PZ `binary.py` and `speciation.py` parameter construction, DEA `pinned.py`, MDEA `refit_298.py`, and bundle `a7_presentation.py`, `check_a7_selected.py`, `reduce_a7_evidence.py`, `render_parameter_tables.py`, and `render_regression_overview.py`. Existing #255/#338 fixed-record binds remain unchanged. The remaining live readers are the authorized default/adoption commands, unchanged hash-pinned caloric and observation inputs, and the permittivity presentation's component identifiers (identical in F0 and F2); none supplies changing endpoint values or reaction laws to a historical calculation.

Representative checks ran through `agent-heavy` with OMP/OpenBLAS/MKL threads set to one, using the pinned wheel. The JSON files retain source conditions, identities, reference hashes and producing functions:

| Amine | Representative retained output | Reproduced pressure / Pa | Absolute difference / Pa |
|---|---|---:|---:|
| PZ | Hilliard 2008 D.5 row 1, A12 | 66.24863229244855 | 0 |
| AMP | Kundu 2003 row 0, current #304 record | 3483.3663636642273 | 0 |
| DEA | Lawson–Garst 1976 row 0, frozen B-2 | 2519.623568138359 | 0 |
| MDEA | Kuranov row `fit:0`, B1 #302 adoption | 74002.65996087721 | 0 |

PZ's check regenerates source reactions through `speciation.reactions`, supplies those R1–R3 declarations to `reactive.pressure_problem`, and uses the retained A12 endpoint and offsets. AMP's check applies `kundu.current_shared` in memory and verifies unchanged current endpoint and R1–R3 laws before prediction. DEA's native `checks` confirms the shared-law identity before prediction from the frozen selection. Each representative prediction equals its retained value exactly. MDEA B1's own declaration is preserved: R1/R3 have their existing narrower intervals and omitted zero e/f fields; the newly frozen MEA-side reader has exact F0 declarations. No MDEA domain is altered to force structural equality.

The repeated normal F2 command still gives 307 predictions, cost 150.76290287953717, and zero maximum relative prediction difference. Its fresh runtime is retained separately in `historical-freeze-default-runtime.json`; the original supported outputs and pins are preserved. These are finite numerical identity checks, not new fits or physical validation. Part II remains for #343–#346.

The correction adds 22 executable lines and removes 22; complete-branch accounting is **121 gross executable additions / 150 allowed**, with **38 removals**, against the original branch base. [historical-freeze-change-accounting.json](historical-freeze-change-accounting.json) retains the accounting. The original 99-line accounting remains historical. No persistent test, model equation, fit control, Engine source, manuscript file, or manuscript registry is added or changed. Independent delivered review of the corrected head remains pending.
