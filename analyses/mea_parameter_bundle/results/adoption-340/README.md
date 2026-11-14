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

The first correction wrongly treated a route's pre-adoption default as its retained scientific input. That assumption is withdrawn. F0 is the owner for the PZ, AMP Kundu/#306, DEA, and MDEA #298 shared substitutions only. Older diagnostic campaigns name their own inputs. The recorded 00e77608 endpoint, 7fccfe8b declaration, and pre/post-260 calorics distinguish those records directly; the older MEA cost is 148.87893934557388, rather than F0's 148.51054565397726.

[older-route-identities.json](older-route-identities.json) gives every bound route's full parameter, declaration and caloric hashes, its evidence file, and verified input hashes. The source declaration was recovered byte-for-byte from its recorded campaign commit b0b1cba: SHA-256 `7fccfe8b6e3ee1d14789940c4238a32a60d9af7e30cef53dd5b59175d4099e64`. It is retained as `pre-F0-declarations.toml`. The existing #297 declaration has relocated dataset paths and SHA-256 39a5d568…; it is not claimed to equal 7fccfe8b…. No equation or unrecorded input was reconstructed.

The two explicit configurations, `analyses/solvent_specification_mea/MEA-pre-260-340.toml` and `MEA-post-260-340.toml`, reference that exact declaration and the immutable endpoint at `results/engine-3e83e19c-refit-chain/restricted-2/attempt-3/run/fit/usable-budget-endpoint.json`, SHA-256 `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91`. Keeping the configuration at the original solvent-input directory lets every unchanged CSV and explicit construction-parameter reference resolve with its recorded hash. All 307 dataset hashes and the explicit construction-parameter hashes were checked. Pre-260 calorics reuse #297's retained `pre-260-caloric.json`, SHA-256 `71c0f65204de5f10a22099db8ee6a939895bf280c725292e2cc46c0b1ebe9ef1`; post-260 calorics remain `inputs/caloric.json`, SHA-256 `d371e5102e6368a51e7db0def4010ac67fa26875b31ee358077ebb904de41efb`.

| Bound route | Endpoint | Declaration | Calorics | Retained evidence |
|---|---|---|---|---|
| #264 calculate: qualification, setup, probe and replay-only | 00e77608… | 7fccfe8b… | post-260; qualification explicitly substitutes old water | `heat-capacity-264/provenance.json` |
| High-temperature `qualify.py`, `run.py`, `check_heat_domain.py` | 00e77608… | 7fccfe8b… | pre-260 | `high_temperature_chemistry/results/qualification.json` |
| MDEA workflow `transfer_probes.py`, MEA comparison branch | 00e77608… | 7fccfe8b… | pre-260 | `transfer-267/input-hashes.json`, `runtime-mea.json`, retained script's baseline assertion |
| Water ideal-gas `compare.py` | 00e77608… | 7fccfe8b… | pre-260; explicit old/new water substitutions retained | `water-ideal-gas/provenance.json`, base commit 30db72af |
| #266 `bicarbonate_carbonate_266.py` and `_prepare.py` | 00e77608… | 7fccfe8b… | pre-260 | `bicarbonate-carbonate-266/baseline-runtime.json` |
| #268 standalone `density_268.bind` | 00e77608… | 7fccfe8b… | pre-260 | `density-268/provenance.json` |
| #261 `pressure_transfer_attribution_261.py` | 00e77608… | 7fccfe8b… | pre-260 | producer commit 0d7d31e's configuration and `pressure-transfer-261/matched-attribution.json` |
| Existing #261 pressure-transfer specification/reference | 00e77608… | 39a5d568… relocated declaration | pre-260 | existing #297 `MEA-pre-260.toml`, #261 `preparation.json`; supported binding preserved |

The #264 fit-coordinate file is deliberately separate from the specification: `analyses/solvent_specification_mea/inputs/fit-coordinates.json`, SHA-256 `ea65e392c34484f2c54b8f61cc465f25c8d6a9377a5b51a1f0db5e60585251af`. Its hash is checked before loading on the common probe/replay-only path. Neither route looks for coordinates inside a frozen directory. The density helper accepts an explicit specification filename; #255's existing snapshot consumer passes `MEA.toml` to preserve its original binding, rather than adopting the standalone #268 configuration.

### Not frozen, needs its recorded snapshot or restoration

- `parameter-identifiability/calculate.py` is restored byte-for-byte to main dbe0db0. Its retained record is 00e77608 / 7fccfe8b with original calorics and the original source module. Its existing guards remain. The documented five-file b0b1cba restoration remains necessary; because later adoptions also changed the endpoint, declaration and reference, a current restoration must additionally restore those three files from b0b1cba. [parameter-identifiability-restoration-check.json](parameter-identifiability-restoration-check.json) supplies the exact eight-file command and verifies all six existing input guards plus loaded endpoint, declaration and caloric hashes against the Git bytes. No historical campaign was executed. The older wheel and environment requirements remain in force.
- `solvent-domain-285/calibration.py` is restored byte-for-byte to main dbe0db0. No own retained snapshot identity was established for this auxiliary feed inventory; none is guessed. It remains a live dependency, not a frozen historical calculation.

The retained `parameter-identifiability/results/complete-inputs.json` describes the restoration used for the original campaign completion. It has not been rewritten to pretend that the additional files were restored in that historical run.

### Older dependencies with their own guards or restoration requirements

The following are listed without changes: `analyses/solvent_specification_mea/fit.py` (#235); `analyses/mea_parameter_bundle/model-d/born-form-diagnosis/born_form_diagnosis.py`; retained #137 `results/concentration-transfer-137/experiment.py`, #140 `results/temperature-reanchor-140/phase-a.py`, and #161 `results/cp-unloaded-161/evaluate.py`; and historical Engine comparisons such as `scripts/compare_engines.py`. Their existing record, Engine, input or restoration requirements remain their owners. This correction does not claim these older dependencies run against current defaults.

### Numerical checks and preserved adoption

[older-route-replay-checks.json](older-route-replay-checks.json) retains source identities, actual/reference values, units and errors. The checks used wheel 391dfe5d through `agent-heavy` with OMP/OpenBLAS/MKL threads set to one. Most retained older values were calculated on earlier wheels, so finite differences are reported rather than called bitwise identity. No fit or historical result file was regenerated.

| Replayed quantity | Actual | Retained reference | Relative difference |
|---|---:|---:|---:|
| MDEA #267 MEA branch (dimensionless) | 148.87893934554421 | 148.87893934557388 | 1.99305e-13 |
| #266 calculation and preparation (Pa) | 5.0076514042935587 | 5.0076514042933677 | 3.81333e-14 |
| high-temperature qualification/run/check_heat_domain (Pa) | 5.0076514042935587 | 5.0076514042933677 | 3.81333e-14 |
| water ideal-gas comparison (J/(mol feed K)) | 89.642948734753958 | 89.642948734754114 | 1.7438e-15 |
| #264 corrected-caloric baseline (J/(mol feed K)) | 89.800759056476281 | 89.800759056475798 | 5.38046e-15 |
| #261 attribution (Pa) | 6977.0072960659973 | 6977.0072960659891 | 1.1732e-15 |
| #268 density helper (kg/m3) | 1029.7326223072268 | 1029.7326223072262 | 6.62425e-16 |

The #267 cost is compared with its existing 1e-10 relative baseline assertion. Other tabulated differences are numerical reproduction evidence on the adopted wheel, not new physical validation or newly selected scientific tolerances. The exact record/declaration/caloric identities, not agreement alone, justify the bindings.

The repeated PZ, AMP and DEA representative predictions remain at zero difference in `older-route-amine-replays/`. Their F0 source bindings and the MDEA #298 shared substitutions are unchanged. The repeated normal F2 command returns 307 predictions, cost 150.76290287953717, and zero relative differences for predictions, residuals, weighted residuals and costs. Fresh default runtime is retained separately; the original accepted adoption evidence, history row, Part II shared values and checkpoint figure remain unchanged. Manuscript files and the manuscript registry are untouched. Independent review of this corrected head remains pending.

Current branch accounting is **134 gross executable additions / 150 allowed**, with **49 removals**, recorded in `older-route-change-accounting.json`. The earlier 99- and 121-line reports describe their original commits, not this corrected tree. Both updated notebooks rendered as HTML with execution disabled. The preserved #255 binder also reproduces one retained F0 and F2 pressure exactly through the shared density helper; `older-route-caller-checks.json` retains those caller checks.
