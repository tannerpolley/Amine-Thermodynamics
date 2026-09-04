# MEA scientific context

- Status: authoritative repository definition under ePC-SAFT Governance D-038
- Scope: aqueous monoethanolamine (MEA)--water--carbon dioxide thermodynamics
- Current parameter status: no active (accepted) MEA parameter set; the exploratory incumbent used for comparisons and fixed-chemistry diagnostics is `analyses/mea_parameter_bundle/results/selected-current-best-parameters.json` (sha256 `a9186c93...40d9`, 2026-09-03), tracked in `analyses/mea_parameter_bundle/results/parameter-record-history.csv`

## Question and intended use

This repository asks which declared ePC-SAFT model, chemistry, and parameter
record can reproduce source-backed pressure, speciation, and supporting
observations for aqueous MEA within an explicit domain. A parameter record may
support predictive or downstream claims only after its numerical, scientific,
and independent-comparison gates pass.

## Project terminology

| Avoid | Prefer | Meaning | Scope | Exceptions | Evidence |
|---|---|---|---|---|---|
| best available parameter set | active MEA parameter set | A parameter packet accepted after the repository's declared scientific gates | README, authority documents, analyses, and manuscript claims | Historical quotation and immutable Git history | Issue #70 decision; Engine Issue #80 |
| promoted parameter | historical diagnostic parameter | A value retained to explain an earlier calculation, not current calculation authority | Historical result tables, audits, and captions | A future reviewed packet may explicitly adopt a value | Source audit and Issue #70 refusal record |
| validation | diagnostic comparison | A comparison that has not met the declared independence and preregistration requirements | Analysis and manuscript prose | Use validation only for a genuinely independent, preregistered comparison | Predictive program and Issue #70 decision |
| upstream-only calculation | upstream-first method, MEA reproduction | A new generic method is built and debugged upstream; MEA may then execute the pinned Engine method directly against MEA-owned inputs | ePC-SAFT calculations and validation work | MEA chemistry, data, model selection, adoption, figures, and manuscript remain MEA-owned | Governance D-038 and Engine Issue #80 |

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
- **Research notebooks:** none are active. After Review Pass, a future accepted
  immutable parameter packet may be summarized in
  `analyses/<short-id>/notebook.qmd`; it must read retained results rather than
  become calculation authority.
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

## Claim boundary

Historical fixed-parameter calculations may support only statements about the
observed behavior of those exact calculations. They do not establish an active
parameter set, predictive validity, independent validation, or transfer to a
process model. Predictive and downstream claims require the declared gates,
complete failure accounting, exact plotted rows, parameter and Engine
identity, uncertainty treatment, and an accepted immutable packet.
