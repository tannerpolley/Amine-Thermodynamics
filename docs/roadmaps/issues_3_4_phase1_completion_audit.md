# Issues 3 and 4 Phase 1 Completion Audit

## Objective

Complete the Phase 1 scope of GitHub issues #3 and #4 for this repository:

- Issue #3 Phase 1: remove downstream optimizer ownership for ePC-SAFT production regression and delegate production fitting to the package-native regression API.
- Issue #4 Phase 1: build the reproducible Smith-Missen-style MEA--CO2--H2O baseline, including data inventory, parameter and reaction provenance, pressure/speciation artifacts, and limitations.

## Prompt-to-artifact checklist

| Requirement | Evidence | Status |
| --- | --- | --- |
| Issue #3: `scipy.optimize.least_squares` is not imported in production regression | `src/MEA/epcsaft_ionic/regress_parameters.py`; `tests/test_epcsaft_ionic_artifact_promotion.py` AST guard | Complete |
| Issue #3: no MEA production regression script calls SciPy optimizers | Production modules checked by `test_production_regression_modules_do_not_import_or_call_scipy_optimizers` | Complete |
| Issue #3: MEA builds target rows and delegates fitting to `epcsaft.fit_reactive_electrolyte_parameters` | `src/MEA/epcsaft_ionic/native_regression.py`; `src/MEA/epcsaft_ionic/regress_parameters.py` | Complete |
| Issue #3: package-native backend and derivative ownership are explicit | Native problem metadata records `optimizer_backend=ceres` and `derivative_backend=autodiff`; regression call passes those fields to the package | Complete |
| Issue #4: all Phase 1 source families inventoried | `data/reference/MEA/manifests/phase1_data_inventory.csv`; `source_status_manifest.csv`; `extraction_target_manifest.csv` | Complete |
| Issue #4: Wong, Amundsen, dielectric, pH, and ionic activity gaps are explicit | `data/reference/MEA/manifests/source_status_manifest.csv`; `docs/roadmaps/mea_data_curation_plan.md` | Complete |
| Issue #4: MEA association scheme and MEA--H2O binary basis documented | `data/reference/MEA/manifests/phase1_parameter_provenance.csv`; `docs/roadmaps/phase1_parameter_audit.md` | Complete |
| Issue #4: reaction constants have source, basis, temperature form, and conversion notes | `data/reference/MEA/manifests/reaction_constant_manifest.csv`; `docs/roadmaps/phase1_reaction_constant_basis.md` | Complete |
| Issue #4: ideal/apparent Smith-Missen speciation runs reproducibly | `analyses/phase1_smith_missen_baseline/scripts/generate_data.py`; `phase1_speciation_results.csv`; `phase1_speciation_metrics.csv` | Complete |
| Issue #4: CO2 pressure parity is generated | `phase1_pressure_results.csv`; `phase1_pressure_metrics.csv`; `phase1_pressure_vs_loading.png`; `phase1_pressure_vs_loading.svg` | Complete |
| Issue #4: speciation vs loading is generated | `phase1_speciation_results.csv`; `phase1_speciation_metrics.csv`; `phase1_speciation_vs_loading.png`; `phase1_speciation_vs_loading.svg` | Complete |
| Issue #4: Phase 1 limitations and Phase 2/3 boundaries are explicit | `docs/roadmaps/phase_acceptance_gates.md`; `docs/roadmaps/mea_manuscript_phase_plan.md`; `phase1_data_inventory.csv` | Complete |
| Issue #4: manuscript-facing text avoids internal operational language | `docs/latex` safety scan for local paths, agent terms, and overclaiming status language | Complete |

## Revised scorecard

Scores use a 10-point scale. The visual score covers figure, table, and presentation quality for non-plot steps.

| Step | Accuracy | Design | Visuals | Relevance | Basis |
| --- | ---: | ---: | ---: | ---: | --- |
| Issue #3 Phase 1 optimizer ownership removal | 9.4 | 9.1 | 9.0 | 9.5 | Production regression no longer imports local optimizer functions, native target rows are serialized, and the package call owns optimizer and derivative backends. |
| Issue #4 data and provenance inventory | 9.5 | 9.2 | 9.0 | 9.6 | Source status, extraction targets, Phase 1 inventory, and data-curation roadmap agree on present and missing sources. |
| Issue #4 parameter audit | 9.4 | 9.1 | 9.0 | 9.5 | Baygi 3B MEA / 4C water and `k_ij=-0.0520` are separated from the retained repo parity path. |
| Issue #4 reaction-constant audit | 9.5 | 9.2 | 9.0 | 9.6 | R1--R5 include mole-fraction basis, temperature function, source, and conversion status. |
| Issue #4 Smith-Missen pressure baseline | 9.2 | 9.3 | 9.1 | 9.4 | Pressure metrics and parity curves reproduce the retained baseline, and the revised figure separates temperature and role legends. |
| Issue #4 Smith-Missen speciation baseline | 9.5 | 9.3 | 9.4 | 9.6 | The baseline now solves the explicit five-reaction, nine-species ideal Smith-Missen system, reports trace/unobserved limits, and renders full-coverage continuous curves. |
| Issue #4 limitation and claim boundary | 9.5 | 9.2 | 9.0 | 9.6 | Phase 1 is described as an explicit ideal-speciation baseline with pressure and trace-species limits; it does not promote Phase 2/3 activity-based or coupled-fit claims. |

## Completion standard

The Phase 1 work is complete when the validation commands pass on the committed tree and the generated Phase 1 artifacts match the manifests and roadmaps above. Any future native package regression result must still pass the approval gate before it changes Phase 2/3 claims or manuscript conclusions.
