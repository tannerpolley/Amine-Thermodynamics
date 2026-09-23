# MEA scientific context

- Status: authoritative repository definition under ePC-SAFT Governance D-038
- Scope: aqueous monoethanolamine (MEA)--water--carbon dioxide thermodynamics
- Current parameter status: no active (accepted) MEA parameter set; the exploratory incumbent used for comparisons and fixed-chemistry diagnostics is `analyses/mea_parameter_bundle/results/selected-current-best-parameters.json` (sha256 `868a5018...fcb7be`; explicit `exclude-same-sign-ion-pairs` since 2026-09-22), tracked in `analyses/mea_parameter_bundle/results/parameter-record-history.csv`

## Question and intended use

This repository asks which declared ePC-SAFT model, chemistry, and parameter
record can reproduce source-backed pressure, speciation, and supporting
observations for aqueous MEA within an explicit domain. A parameter record may
support predictive or downstream claims only after its numerical, scientific,
and independent-comparison gates pass.

## Established work and remaining questions

Reconciled against this checkout on 8 September 2026. This is the starting map
for research and estimation work; absence of an accepted parameter set does
not mean the method, data search or regression strategy is unstudied.

| Question | Work already retained | Read before proposing more work |
|---|---|---|
| How should amine ePC-SAFT parameters be estimated? | Literature synthesis, staged neutral/binary/ionic/reactive estimation, observation roles and explicit comparison criteria are documented. | [Scientific plan, §§4–7](PREDICTIVE_MEA_PROGRAM.md); [amine literature synthesis](../ePC-SAFT/amine-epcsaft-model-hierarchy-literature-review.md) |
| What transfers from MDEA to MEA? | Model lineage and parameter provenance distinguish shared methods, common species and MDEA-specific analog seeds. | [Component audit](../ePC-SAFT/full-component-parameter-source-audit.md); Uyan, Wangler, Cleeton and Bülow companions in [the reading shelf](../../literature/README.md) |
| How can MEAH+ and MEACOO- be constrained? | A detailed staged identification plan already uses shared-cation analogs, restricted carbamate correction and coupled density/speciation. It records 128 analog densities and 103 bulk MEA densities, with derived volumes kept separate. | [Volumetric evidence and frozen staged plan](../ePC-SAFT/meah-meacoo-volumetric-evidence.md); [exact objectives, active coordinates, scales and multistart settings](../../analyses/reactive_epcsaft_parameter_evidence/ionic_volumetric_fit_preregistration.json) |
| Which measurement and reaction conventions are known? | Reaction direction, standard-state conversion, source conflicts, aggregate speciation, oxazolidone onset and pressure-pairing limitations have been audited. | [Primary-source audit](../ePC-SAFT/mea-reaction-and-sentinel-primary-source-audit.md); `data/reference/MEA/manifests/` |
| Have neutral and electrostatic choices been studied? | Neutral-family comparisons, CO2–water induced association and Born/permittivity comparisons are retained. Their conclusions belong to the tested parameter/Engine identities. | [Historical parameter evidence](../../analyses/reactive_epcsaft_parameter_evidence/README.md); [later bundle studies](../../analyses/mea_parameter_bundle/README.md) |
| Have coupled fits and predictive comparisons been attempted? | Issue 70 retains a supported-negative decision. Later work includes full retained-state dielectric comparison, Born studies, reaction-temperature fitting and holdout access. The May small fit is not the latest evidence. | [Issue 70 decision](../../analyses/reactive_epcsaft_parameter_evidence/results/issue_70/predictive_mea_parameter_decision.json); [working notebook](../../analyses/mea_parameter_bundle/notebook.qmd); [parameter history](../../analyses/mea_parameter_bundle/results/parameter-record-history.csv) |
| Is further F/S or ionic screening new work? | The September audit records completed diagnostics and evaluator v4 correction in another checkout; this checkout retains v3. | [Checkout and result discrepancies](REPOSITORY_AUDIT_2026-09-08.md); reconcile the reported owner-held results before repeating a screen |

### Completed estimation work to reuse

| Retained study | Established outcome | Exact retrieval |
|---|---|---|
| Coupled estimation and independent-assessment designs, July 2026 | Joint pressure/speciation objectives, frozen bounds, grouped partitions, multistart and identification requirements were already specified. | `git show 7953c00:docs/superpowers/specs/2026-07-13-coupled-regression-parameter-promotion-design.md`; companion `2026-07-13-independent-validation-identifiability-design.md` in the same directory |
| Shared ion-size density/speciation fit, 28 July | Stable converged fitting did not establish publishable parameters: pressure errors worsened. Repeating density-only identification is not a new untested strategy. | `git show aaa6384:analyses/phase3/ionic_epcsaft_regression/results/scipy_regression_experiment/experiment_summary.json` |
| Pressure-first screening, August | Parameter directions, conditioning, bounds and loading trends were screened; pressure-only movement did not resolve the fit. | Commit `327e34e`; [retained pressure-first evidence](../../analyses/reactive_epcsaft_parameter_evidence/pressure_first/) |
| Consolidated predictive comparison, August | Issue 70 returned a supported-negative decision rather than a transferable parameter export. | Commit `0ce3827`; decision linked above |
| Reaction-temperature fitting, September | Retained comparisons improved pressure and heat agreement but barely changed speciation; source-sized reaction corrections did not explain all discrepancies. The later selected vector has separate replay/adoption limitations. | [Experiment account and cohort results](../../analyses/mea_parameter_bundle/results/reaction-temperature-fit/README.md); [September audit](REPOSITORY_AUDIT_2026-09-08.md) |

These are historical findings for their exact configurations, not permission
to rerun retired implementations or substitute their vectors into the current model.

The remaining questions are narrower than “develop an estimation strategy”:

- **Identification evidence:** the volumetric plan records missing counterion/
  transfer uncertainty information and no numerical exact aqueous MEAH+/MEACOO-
  salt-density evidence from its bounded search. Check its source inventory
  before commissioning another search. Existing analog and bulk data are not missing.
- **Model and source applicability:** resolve the documented reaction-domain,
  high-loading chemistry and same-state measurement limitations for the exact
  proposed fit; they are established limitations, not newly discovered topics.
- **Numerical reconciliation:** distinguish the exploratory incumbent, Issue 70
  results and other-checkout corrections by exact inputs and Engine identity.
  A historical unavailable capability is not proof that the current Engine
  lacks it; inspect the pinned capability and current owning work.
- **Independent assessment:** `holdout-evaluations.csv` records previously accessed
  Xu and Kim data. A new untouched comparison cannot be assumed from an old
  “reserved” label. The scientific plan owns the partition rules.
- **Publication/adoption:** the working notebook has unresolved numerical
  freshness and adoption-writer issues recorded in the September audit. These
  do not erase the completed research or justify repeating it.

### Historical retrieval and known documentation defects

The source-lineage review was expanded in commit `48ad7fa` (25 August 2026).
Commit `897bb6e` (10 May 2026) retains the earlier ion-regression plan and
preliminary fit; use it as history, not the latest result. That plan was removed
from the working tree in `5165fe1`; its absence is a documentation-history
change, not a scientific gap. The volumetric
preregistration references `fa09ace9d0185cf59c736fdb6dc5790bfe3e5976` and
`docs/science/mea-coupled-regression-master-plan.md`; that object is not readable
as a tree in this checkout. Some broad history searches also fail on missing
Git trees. Report that retrieval defect explicitly. The local volumetric
synthesis and preregistration remain readable; a broken historical pointer
is not evidence that the plan never existed.

Before declaring a gap, identify the existing decision, its supporting result
or source, and the precise evidence that remains absent or contradictory.
Before repeating a study, state what changed in its question, inputs, method
or evidence. Update the existing owning record when that answer changes.

## Scientific map

- **Formulation:** `docs/latex/sections/epc_saft_equation_of_state.tex` and
  `docs/ePC-SAFT/` describe the selected equations and their literature basis.
- **Methods:** `docs/latex/sections/data_methods.tex`, analysis scripts, and the
  installed `epcsaft` public APIs own executable methods.
- **Verification and decisions:** analysis receipts, exact result tables, and
  GitHub issues own numerical evidence and gate outcomes.
- **Source data:** `data/reference/MEA/` and its manifests preserve observations,
  transformations, locators, and hashes.
- **Analyses:** each populated directory under `analyses/` owns one bounded
  reproduction, diagnostic, or retained evidence set.
- **Research notebooks:** `analyses/mea_parameter_bundle/notebook.qmd` is the
  active exploratory working view; its HTML is not a certified numerical
  publication. `analyses/enrtl_six_species_ideal_comparison/notebook.qmd`
  retains a separate packet-specific comparison. Neither notebook establishes
  an accepted parameter set or replaces its identified inputs and results.
- **Manuscript:** the CAS journal source is `docs/latex/main.tex`.
- **Bibliography:** tracked CAS inputs are `docs/latex/manuscript_references.bib`,
  `docs/latex/project_sources.bib`, and `docs/latex/official_sources.bib`;
  Better BibTeX remains the upstream citation export.

## Calculation ownership

The installed Engine wheel owns generic equations, equilibrium compilation,
exact derivatives, and regression mechanics. New generic ePC-SAFT methods are
first built and debugged in `ePC-SAFT-project/analysis/` or `validation/`.

MEA-Thermodynamics may call those public Engine methods directly to reproduce
an accepted calculation, evaluate MEA observations, and generate retained
tables or figures. Such work records the Engine wheel and method identity,
input and packet identity, and hashes. This upstream-first rule does not ban
direct Engine calculations here.

This repository owns MEA chemistry hypotheses, source translations, data
roles, model selection, the regression question, validation design, parameter
adoption, scientific figures, and the manuscript. It does not copy generic
Engine equations, restore retired APIs, or maintain local generic runtime or
regression wrappers.

## Source and evidence authority

Authority descends from primary source material and verified locators to
retained observations and transformations, then to immutable calculation
inputs and results, and finally to bounded manuscript claims. Generated plots
and prose are consumers, never upstream evidence.

Issue #70 records a supported negative decision and downstream refusal. Its
raw evidence, exact hashes, and decision record remain authoritative history.
The qualified Kiepe CO2--water induced-association evidence is also retained.
Engine Issue #80 owns the current method and parameter campaign. Until that
campaign succeeds and MEA accepts an immutable packet, this repository has no
active MEA parameter set. Once such inputs exist, MEA may reproduce the pinned
calculation directly through the installed Engine API.

The [8 September 2026 audit](REPOSITORY_AUDIT_2026-09-08.md) records a checkout
boundary: this branch still uses shared evaluator v3, while MEA Issues #85/#86
report a reviewed v4 start-volume correction and completed ionic comparison
in another checkout. Those reports retain the exploratory incumbent; they do
not authorize parameter adoption or certify this branch's numerical outputs.
The [scientific plan](PREDICTIVE_MEA_PROGRAM.md) gives the evidence sequence;
GitHub owns task state.

## Claim boundary

Historical fixed-parameter calculations may support only statements about the
observed behavior of those exact calculations. They do not establish an active
parameter set, predictive validity, independent validation, or transfer to a
process model. Predictive and downstream claims require the declared gates,
complete failure accounting, exact plotted rows, parameter and Engine
identity, uncertainty treatment, and an accepted immutable packet.
