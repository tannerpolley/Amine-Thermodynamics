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

Final executable accounting: **99 gross additions / 150 allowed**, with **16 removals**, across ten executable files. `adoption_297.py` accounts for 87 additions; the remaining 12 bind historical consumers explicitly to F0. Tests have 0 additions/removals. JSON/CSV/TOML and figure files are retained inputs or generated numerical evidence, classified as other files by the accounting tool.

The populated notebook rendered to `analyses/_site/mea_parameter_bundle/notebook.html` using Quarto HTML, presentation profile, with execution disabled. The standard refresh entry was not used because it can rewrite the excluded manuscript registry; `analyses/_cse-manuscript.json` is untouched. No scientific calculation ran during rendering. Independent review and manuscript promotion remain pending.
