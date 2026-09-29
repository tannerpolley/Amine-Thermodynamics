# MEA repository evidence audit — 8 September 2026

## Scope and result

This is a dated inspection, not a second work queue or parameter-adoption
decision. GitHub Issues own execution; `PREDICTIVE_MEA_PROGRAM.md` owns the
scientific sequence. Inspection began at `c3697059164756bcd923cbedb098cdcefcd5c7f6`
on `codex/born-permittivity-formulation-study` in the saved checkout.
The pre-existing notebook, render, freshness-test, environment and Serena
changes were preserved. No numerical campaign, parameter change, deletion,
commit, publication, or other-checkout mutation is part of this audit.

**Verified:** no accepted MEA parameter set exists in current repository
authority. The selected JSON is an exploratory incumbent. Its SHA-256 remains
`a9186c93759f2e2c02a6c913350ad06a244fff3f82503820c9962b3df8dd40d9`;
the retained notebook Engine wheel is
`40fba7cfb9c8414152f3e49636c49ae2e3f7099e30040d54d464ccb38355f805`.
The bounded HTML check passed 16 stars including the legend, all four fit
anchors, star links, Quarto layout wrappers, and selected-file identity.

**Verified:** strict `result_freshness.py --fingerprint` refuses
`results/figure-calculation-record.json` as unverified generation. HTML layout
and parameter-table identity therefore do not certify numerical publication.

## Coverage and ownership

The tracked-file inventory contains 1,059 existing files: 814 in `analyses`,
114 in `data`, 68 in `docs`, 23 in `src`, 16 in `scripts`, nine in `tests`,
and 15 root/configuration files. The audit inspects active owners, entrypoints,
documentation and retained summaries; it does not revalidate every experimental
row against its primary paper or rerun historical thermodynamics.

| Owner | Role in bundle selection | Limit |
|---|---|---|
| `data/reference/MEA` | Source observations, transforms, reaction/source qualification, domains | Presence of a table does not admit every row to fitting |
| `src/MEA` and root `scripts` | MEA data interpretation, retained baseline methods, validation/rendering | Generic Engine equations and fitting remain upstream |
| `paper_validation/2015_baygi` | Paper-specific neutral reproduction | Reproduction does not adopt a reactive bundle |
| `six_species_solubility_reference` | Six-species pressure/speciation reference | Legacy neutral calculation is a distinct baseline |
| `neutral_pcsaft_pressure_reference` | Neutral pressure/parity reference | Not coupled reactive parameter evidence |
| `ideal_reaction_equilibrium` | Ideal chemistry baseline and manuscript comparison | Does not qualify electrolyte parameters |
| `speciation_evidence_harmonization` | Observation bases and direct/aggregate/ambiguous roles | Harmonization is not parameter estimation |
| `historical_fixed_parameter_epcsaft_evaluation` | Exact historical fixed-parameter comparisons | Cannot be relabeled as selected-vector predictions |
| `reactive_epcsaft_parameter_evidence` | Issue #70 negative decision, neutral/source and electrostatic history | Retain failures and original input identities |
| `enrtl_six_species_ideal_comparison` | Matched species reduction and packet-specific sensitivity | Its perturbation ranges are not uncertainty for the incumbent |
| `mea_parameter_bundle` | Exploratory parameter mapping, working notebook, retained comparisons | No accepted bundle; publication freshness incomplete |
| `film_chemistry_work_package_a` | Source-qualified reaction/transport input checks for film work | No thermodynamic adoption; Work Package B remains blocked |
| `toybox/ionic_parameter_fit_playground` | Retired rejection evidence | Excluded from promotion and manuscript predictions |
| `docs/scientific/latex` | Current fixed-parameter manuscript | New exploratory results have not been promoted for manuscript use |

## Findings established before documentation corrections

1. **Verified — conflicting runtime descriptions.** Root `README.md` says both
   Engine and legacy PC-SAFT are Git-pinned. `pyproject.toml` pins only `pcsaft`;
   the notebook uses an explicitly retained wheel. The historical
   `data/reference/MEA/manifests/engine_artifact_lock.json` requires
   `cfe8e2a0d5af8d35227a49246dc1590de64ab55bf033e3416b6f80e1ff8f410e`,
   a different wheel from the notebook. `scripts/validate_engine_environment.py`
   reads that historical lock. Do not change either identity to make them agree.
2. **Verified — missing notebook authority.** `docs/scientific/CONTEXT.md` says no research
   notebook is active, while `analyses/README.md` and the existing notebook
   define an active working view. The correction must distinguish working
   interpretation from an accepted parameter set.
3. **Verified — stale planning sequence.** `PREDICTIVE_MEA_PROGRAM.md` says to
   close #62–#67, run #13/#14, then decide #70. Those issues are closed historical
   evidence; #70 reached a supported negative decision. The live MEA list includes
   #83–#86, #68 and #10. Closure alone is not successful scientific acceptance.
4. **Verified — evaluator discrepancy.** This checkout's
   `shared_evaluation.py` is v3, SHA-256
   `6bc94e6c628aa212ccc4a6cce32226eed42aadaca6d06692e6c9be6984b6e32d`.
   `prepared_problem` multiplies molar volume by total moles before supplying
   a molar-volume start. [Issue #85](https://github.com/tannerpolley/MEA-Thermodynamics/issues/85#issuecomment-5537540222)
   reports the reviewed v4 correction in `codex/reaction-partition-fs-study`,
   SHA-256 `f8b7e0e44989cd946828abe34ac25da15d151fd3c546e1cc2abd01e95e56cc2a`.
   That uncommitted work is not installed here. Reconciliation precedes new
   local comparisons; old caches and scores cannot be relabeled v4.
5. **Verified report, not local replication — newer experiments.**
   [Issue #83](https://github.com/tannerpolley/MEA-Thermodynamics/issues/83#issuecomment-5536532837)
   reports that neither F/S trial survived bicarbonate non-degradation.
   [Issue #86](https://github.com/tannerpolley/MEA-Thermodynamics/issues/86#issuecomment-5538014243)
   reports a corrected 308-request ionic comparison: 298 evaluated states,
   ten retained certificate failures, and no non-degrading direction. Both
   retain the incumbent. The underlying uncommitted result files belong to
   the other checkout and were not independently recalculated here.
6. **Verified — consumed holdouts.** `holdout-evaluations.csv` records one look
   at 18 Xu pressure and 20 Kim–Svendsen 120 °C heat targets during reaction
   selection. They are comparison history for this incumbent, not untouched
   independent validation. The Engine campaign's own partition is a distinct
   record; any transfer must reconcile row access across campaigns.
7. **Verified — candidate/selected mismatch.** The reaction-temperature
   candidate replay changes R1–R5; the selected JSON stores only R2/R4/R5
   changes. Its replay scores are not the selected vector's exact scores.
   The README already forbids the defective `--adopt` writer. Preserve that
   restriction and score only an exactly serialized candidate before adoption.
8. **Verified — fit-summary correction.** Independent retained-result review
   supports the neutral fit, historical ion/speciation values, CO2 grid selection
   and reaction-temperature statistics within their stated limits. The notebook
   sentence listing five pressure, 22 speciation and six heat targets ambiguously
   called them exclusions: they are the 33 retained common targets. The eight
   excluded keys in `reaction-temperature-fit/screen-targets.csv` are one Jou
   pressure row (`vle_obs_0208`), three Böttinger state-067 targets and four
   Matin state-019 targets. This wording is corrected without changing values.
9. **Verified — source-synthesis authority drift.**
   `docs/ePC-SAFT/amine-epcsaft-model-hierarchy-literature-review.md` called
   historical 69/79 pressure and 44/44 speciation coverage the current bundle's
   result. Its cited `permittivity-formulation-comparison.json` belongs to a
   different Engine/parameter identity. This and `full-component-parameter-source-audit.md`
   need exploratory/historical labels instead of accepted/active implication.

## Manuscript alignment

Independent read-only review found that `docs/scientific/latex/main.tex`,
`sections/data_methods.tex`, `sections/conclusion.tex` and the parameter tables
already identify a retired fixed-parameter evaluation. Preserve their original
Engine/version and parameter identities. No new notebook numbers were promoted
to the manuscript and no manuscript source was changed.

Two low-priority wording candidates remain for the manuscript owner:
`tables/parameter_evidence_matrix.tex` calls the basis “primary,” and
`sections/epc_saft_equation_of_state.tex` calls the historical inputs “adopted.”
The surrounding manuscript bounds both, but “historical” would be more precise
in a future source revision. The Austgen/Nasrifar source-choice difference is
already documented in `mea-reaction-and-sentinel-primary-source-audit.md`;
do not silently replace the manuscript reaction table with the current mapping.
MEA [#68's scope comment](https://github.com/tannerpolley/MEA-Thermodynamics/issues/68#issuecomment-5416225752)
supports the negative-result manuscript account rather than its older predictive
issue body.

## Removal and preservation review

No broad deletion is authorized. Exact duplication is only a starting point:
readers, generation, unique provenance and recovery must also be established.

- **replace:** neutral-pressure, Baygi and historical-evaluation READMEs still
  instruct users to run deleted `scripts/generate_data.py` entrypoints;
  neutral and Baygi `analysis.yaml` repeat them. Retained renderers consume
  existing results. Correct those instructions and the neutral metadata's
  nonexistent `Canonical_Combined_VLE.csv` input by naming actual retained
  renderer inputs, without pretending current observations generated historical
  predictions. Renderer missing-file hints also name retired generators;
  code repair is deferred. Zero scientific tables removed.
- **prevent:** `analyses/enrtl_six_species_ideal_comparison/scripts/generate_full_uq.py`
  defaults to sibling-checkout packet paths and implements a temporary local
  SciPy/Newton equilibrium layer. Its outputs are packet-specific historical
  screening evidence, not an approved generic Engine method or posterior UQ.
  Retain results; future execution requires an explicit immutable materialized
  packet and reviewed Engine-owned equilibrium method. Do not run its defaults.
- **investigate:** `scripts/check_no_local_paths.py` reports 464 existing
  violations in five tracked files: `generate_full_uq.py` (2), its
  `results/uq_run_receipt.json` (3), `mea_parameter_bundle/references.bib` (457),
  and `results/best-in-slot-campaign/co2-epsilon-r4-b-smoke-fit-input.json` and
  `co2-epsilon-r4-b-smoke-fit-result.json` (1 each). Relative prefixes above are
  under their owning analysis. Preserve source citation authority and failed-fit
  evidence; bibliography projection belongs to its source owner. Full quick
  validation cannot be claimed while this existing check fails.
- **delete candidate:** `src/MEA/common/plot_export.py` (110 lines) defines
  `save_plot` and `default_output_dir` without repository callers. Replacement:
  nothing for current callers. External users are unknown; before deleting,
  confirm that no external caller imports it and rerun repository import/plot checks.
  The file contains no retained scientific values; recovery is from the reviewed
  original file/commit, subject to this repository's historical-object caveat.
- **delete candidate:**
  `analyses/reactive_epcsaft_parameter_evidence/born_permittivity_sensitivity/scripts/evaluate_calorimetry_consistency.py`
  (230 lines) imports missing `evaluate_co2_water_kij_transfer`/`generate`;
  `run_ion_coefficient_blocks.py` beside it (287 lines) also imports missing
  `generate`. The study README/inventory advertise these dormant methods, but
  no current executable caller was found. Conditional retirement removes those
  references and preserves their result tables and scientific interpretation.
  Unique algorithm details must be reviewed before deletion; replacement work
  belongs to an accepted Engine method, not recreated legacy helpers.
- **investigate:** unused `MEA_DIR`, `LEGACY_BASELINE_OUT`, and
  `SIX_SPECIES_PROCESSED` definitions in `src/MEA/common/config.py` may be removed
  after the same external-reader decision. Do not remove the shared config file.
- **investigate:** the Born/permittivity `predictive_partition_evidence.mpl.yaml`
  names deleted `render_predictive_partitions.py`. A retained `scripts/render.py`
  exists, but changing provenance requires proof that it produced the figure;
  do not rewrite historical provenance just to resolve a path.

- **keep:** the identical
  `analyses/ideal_reaction_equilibrium/figures/pressure/output/ideal_reference_pressure_plot_data.csv`
  and `analyses/ideal_reaction_equilibrium/results/ideal_reference_pressure_results.csv`
  implement the documented plotted-snapshot/result-owner split. Verify the
  sidecar hash if regenerating; zero files proposed for removal.
- **investigate:**
  `analyses/mea_parameter_bundle/results/born-permittivity-study/automatic-extended-sparse-targets.csv`
  and `analyses/mea_parameter_bundle/results/born-permittivity-study/like-charge-explicit-parity-targets.csv`
  are byte-identical, but their records bind different parameter hashes
  (`0ea2…` and `ad5a…`). No current caller beyond retained metadata was found;
  establish experiment/provenance identity before deduplicating. At most one table
  could be removed, with both experiment references redirected to its owner.
- **keep:** selected/history JSON, failures, negative Issue #70 evidence,
  original packets, historical wheel locks and superseded experiment records.
  They explain different scientific calculations and are not redundant merely
  because current adoption is blocked.
- **investigate:** `.codex/environments/README.md`, `.codex/environments/setup.sh`
  and `.serena/` have unresolved user/Claude ownership. No modification or
  deletion is proposed. Current setup can select a sibling-built wheel; that
  is not evidence of the notebook wheel's identity.

net: zero files deleted or renamed; all unique retained values preserved.
Three code files totaling 627 lines are conditional retirement candidates,
with external-reader/algorithm-preservation questions unresolved; no dependency
removal is established. One duplicate table and three unused constants remain
investigations, not approved deletions.
Potential deletions remain conditional on reader/provenance verification and
explicit authorization. Documentation corrections below this audit's evidence
boundary do not change calculation authority.

## Corrections and validation

Updated root/analysis navigation, scientific context/plan/index, the two
parameter-source syntheses, three historical analysis READMEs, two analysis
command/input inventories, and the UQ reproduction-limit note. The working
parameter notebook now identifies retained versus excluded fit targets, consumed
holdouts, owner-reported v4 work and the correct frozen neutral-fit links under
`validation/campaigns/2026-mea-parameter-estimation/analysis/neutral-mea-water/`
at Engine commit `186e81617b632ccf9189131033fef46719109476`.

- `bash analyses/mea_parameter_bundle/render.sh notebook.qmd --working-copy`
  rendered self-contained HTML with `--no-execute`; no model was run.
- Focused repository-layout and result-freshness checks: five passed (0.46 s).
- Selected-file hash, 16 HTML stars, links/anchors and Quarto wrappers passed
  before and after edits. The wheel hash also matches the handoff.
- Changed-document local links and revised analysis input paths passed;
  `git diff --check` passed. Both corrected frozen neutral links were resolved
  against GitHub by the independent reviewer.
- `validate_mea_data_library.py` passed. The existing local-path check fails on
  the five files listed above; no full quick-suite pass is claimed.
- Prose checking of the roadmap/notebook passed; the audit report's one lexical
  hit is the exact official filename `engine_artifact_lock.json`, an allowed
  filename exception. This does not change the lock's authority.
- Strict numerical freshness remains unverified, as expected; no figure
  regeneration, solver campaign, manuscript build or publication was attempted.
- Cleanup audit ran and reported eight Python cache directories. Their prior
  ownership was not established, so no removal mode was used. No persistent
  task-owned process was launched. Environment/Serena changes and the source
  task's Claude terminal were left alone.

Remaining scientific work is the roadmap's numerical-identity and
failure-diagnosis step, followed by source qualification, identifiable
estimation, independent validation and exact-vector adoption. The audit and
documentation update do not resolve those scientific gaps.

Final independent documentation review supported the corrected fit sentence,
neutral links, holdout wording and owner-report boundaries. It found one
remaining generic generation-command example in the root README; that example
was removed in favor of each analysis's supported commands. No numerical
evidence or code changed in that final correction.
