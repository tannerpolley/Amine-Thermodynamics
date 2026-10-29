# Draft experiment: do MEA shared-species parameters transfer to AMP?

Parent: [#220](https://github.com/tannerpolley/Amine-Thermodynamics/issues/220); research/design delivery: [#227](https://github.com/tannerpolley/Amine-Thermodynamics/issues/227). Reuses [#222](https://github.com/tannerpolley/Amine-Thermodynamics/issues/222) and the merged [#228](https://github.com/tannerpolley/Amine-Thermodynamics/issues/228) driver. **Draft requiring owner decisions and independent readiness review; no fitting authorized.** Source gaps listed below prevent calling this Ready for execution.

## Question and intended use

Can the adopted MEA ePC-SAFT formulation describe aqueous AMP pressure and speciation, with supporting caloric/volumetric comparisons where source data become admissible, while every shared-species quantity stays fixed? The intended result is a bounded single-amine transfer assessment and a parameter record that can later seed AMP/PZ predictions. It does not qualify a rate-based absorber or establish universal ions.

Recommend AMP first, PZ second, blend third. AMP tests a new amine with one protonated cation and a weak but observed carbamate; PZ adds two protonation equilibria and several carbamate forms, followed by cross-solvent interactions in the blend. AMP is simpler in species count, but a bicarbonate-only copy of MDEA is not an adequate starting claim. Read [chemistry](chemistry.md) and [source map](data-map.md) together with this proposal.

## Model and frozen inputs

Use the MEA hard-chain, dispersion, association, Debye–Hückel and SSM+DS Born formulation with the adopted density-, temperature- and composition-dependent permittivity and its derivatives. Generic equations, phase solving and parameter fitting remain Engine-owned.

Freeze full H2O, CO2, H3O+, OH−, HCO3− and CO3²− records and all shared–shared interactions from `analyses/mea_parameter_bundle/results/selected-current-best-parameters.json`, SHA-256:

`00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91`.

Freeze adopted R1–R3 separately from that parameter document, including the MEA R2 enthalpy shift and reference conventions. Preserve the #222 limitation that bicarbonate–water interaction and R2 shift are MEA calibration quantities with uncertainty. A failed AMP comparison cannot by itself isolate either as the cause.

Before any numerical work, bind the then-approved immutable merged-main Engine wheel by commit and SHA-256. #228 reproduction used `d513820`; no new wheel is adopted by this draft. Runtime source imports remain prohibited.

## Chemistry and analytical feed

Nine liquid species and five independent reactions are given in [chemistry](chemistry.md): six shared species plus AMP, AMPH+, AMPCOO−; three shared reactions plus AMP dissociation and carbamate hydrolysis. Vapor contains only H2O, CO2, AMP. Feed basis: one mole analytical AMP, source water amount, and α moles added CO2, with α in mol CO2/mol analytical AMP. Include loaded CO2 mass in density/Cp conversions. Preserve unloaded versus loaded composition basis per paper.

AMPH+ dissociation: use Hamborg & Versteeg 2009 Table 1 (p.1320), the correlation form ln K = A/T + B + C ln T in Eq.21 (p.1319), and the 24 AMP experimental runs in Table 16 (p.1325). Table 4 describes DMMEA; Eq.35/Table 15 do not provide the AMP dissociation law. The source uses hydronium, explicit water activity, and an infinite-dilution molality standard state. Transcribe the AMP measurements and establish the numerical correlation and its uncertainty before adoption. Document the mapping into the Engine reaction-reference convention, including water factors, standard pressure, direction, and temperature domain; verify source reference values and reciprocal constants for reversed reactions. Carbamate hydrolysis: establish an activity-based baseline from an original source before fitting. Ciftja 2011's concentration-only apparent constant is not that baseline. Ciftja 2014 and its temperature dependence are missing. No numerical carbamate law is invented here.

## Two AMPH+ representations

| Quantity | A: MEA single-sphere convention | B: charged-molecule convention |
|---|---|---|
| Segment number | 1 | fixed to the adopted neutral AMP segment count |
| Packing diameter | 0.88σ, independent of T | neutral-style temperature-dependent segment diameter |
| Like-ion dispersion | excluded | explicitly declared, including molecular self-dispersion |
| Association | none | proposed neutral-AMP site topology, zero self-energy, neutral association volume, cross-association by the adopted combining rule |
| Debye–Hückel diameter | fitted σ | fitted σ |
| Born diameter | separate fitted value | separate fitted value |

B is a modeling hypothesis adapted from #222, not a published AMP ion parameterization. Declare no cross-association to CO2. Both variants have the same coordinates, data and pass bar. AMPCOO− uses one fixed representation in both so the comparison changes AMPH+ alone. Site topology and unlike association for the carbamate require a source-backed declaration in preparation; do not silently inherit neutral sites.

The retained MDEA notebook reports different outside-fit performance for its two conventions. That comparison does **not** prove AMPH+ representation is the cause of any AMP failure: chemistry, correlations, starts, bounds, data and model error also affect inference. Keep both results even if one fails. Selection uses fitted evidence and identifiability before the hold-out is scored.

## Pure AMP and permittivity

Numerical AMP model construction is blocked until the selected PC-SAFT parameter table and its defining equations are readable and verified. Check Pakravesh SI Table S1 and its cited original source, including Ayad if that is the lineage. Retain the association scheme, parameter units, association-volume convention, source domain, and a defined pure-property reproduction check. If these sources cannot establish an applicable set, return to the owner to select another published PC-SAFT set or authorize a separate neutral-parameter design. Do not substitute another SAFT family. Independently resolve the AMPCOO− representation and the thermodynamic carbamate-hydrolysis law, including temperature dependence; species detection and an apparent NMR constant do not supply these inputs.

Candidate PC-SAFT source: Pakravesh & Zarei 2025, DOI [10.1021/acs.jced.4c00390](https://doi.org/10.1021/acs.jced.4c00390), §2.2 and SI Table S1. Ayad et al. 2023, JC.E.D. 68, 2789–2806 (Pakravesh ref.37), is the original-parameter-source candidate identified in the main text; the SI citation lineage must still be checked. The publisher's SI index lists an AMP 2B PC-SAFT set; verify the actual supplement and original Ayad equations before adopting values. Pakravesh Table 1 is **PρT-SAFT-HR**, a different EOS, and must not supply PC-SAFT parameters. This source distinction is a preparation blocker, as it was for DEA in #220.

Fix neutral m, σ, u/k, association energy and volume after the source convention is verified. Determine whether association volume multiplies d³ or σ³. If conversion is required, use the existing MEA source-model comparison method; retain saturation pressure and saturated-liquid-density comparisons with a predeclared source-model tolerance. No conversion, new neutral fit or Engine calculation belongs to #227.

Fit the two coefficients of the adopted MEA dielectric law beforehand to Hsieh 2007 pure and aqueous AMP observations (Tables 2 and 5; see data map), then freeze. Report conditioning, both minima if applicable and the composition coverage; aqueous x=0.2–0.8 is not direct evidence for every dilute absorber state. Independent ideal-gas AMP Cp, units, temperature range and reference anchors must be established before any heat/Cp objective is admitted.

## Proposed fitted coordinates

The table below lists 14 candidate coordinates, not an approved joint fit. The executable coordinate set and count remain undetermined. After verifying the calibration sources, propose the smallest set supported by distinct observable sensitivities, with source-backed fixed values or ties for the remaining quantities. Record the scaled sensitivity rank and weak combinations on calibration data before joint fitting, and require endpoint identification checks afterward. Fourteen coordinates may not proceed solely because the number of rows exceeds fourteen or an optimizer converges.

| Fitted quantity | Count |
|---|---:|
| AMP–water k at 313.15 K and reciprocal-temperature slope | 2 |
| AMPH+–CO2 constant k; AMP–CO2 fixed to zero | 1 |
| AMPH+–water k at 313.15 K and slope | 2 |
| AMPH+–HCO3− constant k | 1 |
| AMPH+ σ, u/k, Born diameter | 3 |
| AMPCOO− σ, u/k, Born diameter | 3 |
| AMPCOO−–water constant k | 1 |
| Carbamate hydrolysis log-law constant offset | 1 |
| Total | 14 |

All other AMP-specific dispersion corrections start fixed to zero, including AMPH+–AMPCOO−; this is an explicit reduction hypothesis, not a fitted result. Neutral quantities and association topology stay fixed. The carbamate temperature slope/enthalpy is fixed to a verified source law; **no enthalpy-shift coordinate is included** without independent heat evidence. If fourteen coordinates are weakly constrained, return to Design to tie or fix quantities on source evidence. Do not add more pair coefficients to cure a pressure residual.

AMPH+–CO2 is a proposed initial coordinate, not an inference from MDEA. Before the owner freezes it, compare raw pressure-Jacobian column norms for neutral–CO2 and cation–CO2 at the declared starts on a preselected calibration subset; both k coordinates are dimensionless. Retain the columns and rank information. Disagreement across variants returns the coordinate choice to the owner. Never use the outside-fit set for this choice.

Use k(T)=k_ref+s(1/T−1/T_ref), T_ref=313.15 K, so s has kelvin units. Proposed bounds needing approval: k_ref and constant neutral/ion-water/CO2 k in [−0.5,0.5]; cation–bicarbonate k in [−1,1]; slopes ±1000 K; Born diameters [2,7] Å; u/k [50,950] K. Sphere σ [3,7] Å; molecular σ bounds should bracket the verified AMP segment diameter and must be frozen in preparation. Carbamate σ bounds and law-offset bounds require original-source uncertainty/sensitivity evidence, so are deliberately unresolved. No optimizer may use an implicit bound.

Declare starts before joint fitting: phase-admissible binary-VLE pre-fit as the common neutral-water start, plus source-derived ion initializations and at least two distinct ion-water starts whose full vectors and bounds are retained. Do not use zero binary k blindly: #222 found an unphysical binary split at its original starts. Initial vectors cannot be finalized until the pure AMP and carbamate source records exist.

## Data roles, objective and pre-registered falsifier

Proposed roles, **owner approval required before execution**:

- Calibration: paper-checked AMP-water Hartono/Pappa VLE; Hsieh dielectric preparation; one complete loaded-pressure campaign from Hartono after pressure and composition bases are resolved; Ciftja 2014 NMR after original acquisition, uncertainty assessment and independence review. Keep its overlapping NMR species as measured sums. Do not also fit a law estimated from those rows as independent evidence.
- Separately reported total-pressure comparison: Tong 2012 Table 4, 30 mass% AMP, five isotherms. Its measured P is **total pressure**. Preserve its five zero-loading solvent baselines as binary comparisons; score the forty positive-loading rows as total bubble pressure. Counts/conditions checked against Table 4 p.43: 45 rows total, 40 loaded, 5 baselines. Do not subtract an eNRTL-calculated vapor pressure and call the remainder an independent measured CO2 partial pressure.
- Supplemental outside-fit: independently verified Chen, Dash, Jahangiri and Kundu campaigns; Ciftja 2011 as earlier speciation evidence only after resolving overlap with the 2014 paper. No random row split within one campaign. High-temperature data outside reaction/source domains are reported as extrapolation, not pooled into the primary score.
- Heat, density and Cp remain outside-fit/unscored until original datasets and caloric inputs are admitted. Arcis 2007 (DOI 10.1016/j.jct.2006.11.011) is an absorption-heat lead requiring source review. Hilliard PZ heat capacity is not AMP heat capacity.

Propose bounded least squares with pressure log ratios, measured species-sum difference residuals, and source uncertainty scales recorded per group. Proposed weights: loaded-pressure 100/9, binary pressure 1, species 1, following #222 as repository precedent. NMR scales cannot be supplied from the private model or silently set to zero; freeze them after source review. Report each objective contribution. No heat/density/Cp residual is created to fill a missing stage.

No numerical pressure acceptance limit is adopted yet. The MEA/MDEA 24.2% CO2 partial-pressure limit is not transferred to Tong total pressure. Prefer a whole, independently verified CO2 partial-pressure campaign, excluded from calibration and model selection, with an owner-approved metric and limit justified for the intended transfer assessment. Retain Tong's 40 loaded total pressures and five solvent baselines as separately reported comparisons. Freeze the primary campaign, eligible temperatures, row identities, uncertainty treatment, and acceptance limit before fitting. A primary test over all five Tong isotherms requires supported reaction-law coverage or an explicit owner-approved extrapolation test; it cannot simultaneously be described as wholly within the source domain.

No other statistic becomes a pass bar without a design amendment. Failures return to Design; no retuning on Tong. NMR nonzero carbamate is a chemistry constraint, but the detection/uncertainty threshold needed for a numerical species falsifier is not yet known.

## Numerical checks, phase gate and identifiability

Use #222 numerical tolerances as proposed repository choices: equilibrium residual 1e−10, independent prediction replay 1e−8 relative, derivative checks 1e−5 relative. Verify element and charge balances, reaction direction/reference conversion, shared-only water/CO2 invariance, neutral saturation convention, and one loaded state before statistical fitting.

Run declared tangent-plane searches on every fitted and scored state for each endpoint. Carbon-free supports at zero loading; distinguish a dense second liquid from gas evolution. Propose #222's packing fraction >0.10 as the dense classifier, predeclared before reading endpoints. Gas evolution is recorded separately; unavailable liquid-only caloric observables are not silently scored. A descending dense split or unresolved/ambiguous phase search blocks selection. A source showing precipitation requires a solid-phase treatment or an owner-approved domain restriction; no unmodeled PZ solid may later be treated as a liquid prediction.

Retain native scaled-Jacobian rank, singular values/vectors, active bounds, covariance limitations and profiles along weak combinations at starts and endpoints. Separate experimental uncertainty from conditional standard errors. Different vectors with similar fitted objective but materially different outside-domain predictions require redesign. Active arbitrary bounds stop this AMP design; #222's later owner acceptance of bounds was a task-specific decision and is not inherited automatically.

## What the AMP specification must contain

Use `SolventSpecification` in `src/MEA/solvent_specification.py`; do not clone the MDEA runner. The outer variant file follows `analyses/solvent_specification_mdea/B1.toml`: the format identifier `solvent-specification-1`, hash-bound `declarations`, `start`, `endpoint`, `coordinates` and `caloric`, plus optimizer controls. The included declarations supply `[phase_states]`, `[phase_policy]` and `[composition]`. Retain wheel identity and hand-off provenance beside the run outputs as #228 does; they are not extra required outer-TOML fields. The future `declarations.toml` must contain:

1. `[chemistry]` reaction groups with names, full stoichiometry, `ReactionLogPolynomial` coefficients, pivot, valid T interval and standard-state id; `reference` records with source basis and standard pressure. Neutral-reference amounts cover every declared solute, including carbamate, without importing a private constant.
2. `[templates]` for unloaded binary bubble, loaded reactive bubble, loaded liquid and zero-loading liquid; optional initial/final heat templates only after calorics admission. Feed contains literal species ids, source water, one AMP and added CO2. Liquid/vapor supports and carbon-free zero-loading phase-search supports are explicit.
3. `[[datasets]]` per source/observable/role: name, group, `role="calibration"` or comparison, public prepared CSV path and SHA-256, column mapping, filters, weight, constructor, kind, arguments, template and assessment-temperature domain. Inputs carry `identity` and JSON `source` metadata with original locator, units, basis, uncertainty and campaign; identities have a sortable integer in the second colon-separated field.
4. Separate pressure entries for `pressure` (total) and native CO2 partial-pressure observable. Observations are source checked; no private CSV is used as a runtime input.

5. Coordinate JSON referenced by the outer file with origins/scales/bounds and tied parameter targets, plus `kind="reaction_coordinate"` for the carbamate law's a offset. Optional future `reaction_enthalpy_shift` requires a declared pivot and independent caloric evidence.

Preserve each paper's reported observation basis. Either compare reported mole fractions directly or retain the explicit conversion to ratios per total analytical AMP, including AMPCOO− in the denominator and propagating normalization uncertainty. Do not fit the normalized AMP+AMPH+ sum and normalized carbamate as independent observations: they are complementary. Use a nonredundant observation set compatible with the driver's scalar residuals, and document remaining correlations and uncertainty assumptions. Do not score pH-derived protonation splits as independent NMR measurements.

Include `[composition]` with analytical amines, amount basis, loading denominator and pressure/temperature units; `[phase_states]` binds the prepared phase rows by path/hash; `[phase_policy]` declares ion/neutral species and the density/ambiguity classifier. These are separate from the reaction and measurement tables.

### Driver limits established by reading #228 and current code

- Phase-state row expansion hard-codes `T`, `P`, `water`, `alpha`, `amine`. Single AMP can use those fields directly. Dataset `columns`/`bind` actually accepts extra named fields, but phase-state loading does not. Variable AMP/PZ ratios therefore need explicit composition-specific templates with literal feeds, or a separately approved general row-expansion change. A single `amine` scalar cannot represent independent blend amounts. Define PZ loading per molecule, not per site.
- `cp_polynomial` constructs **zero h and s anchors** at its supplied reference temperature. AMP's source caloric convention must be transformed consistently with reaction standards before use. Shomate has a separate formation-enthalpy field; it is not a silent workaround for an incompatible reference state.
- Reaction coefficient and enthalpy-shift coordinates are implemented in the merged driver. #228 tested a coefficient shift and a pivot-preserving enthalpy shift numerically on MDEA. AMP must declare the correct reaction name and coefficient, with physical shift q=origin+scale·v. Do not claim shifts are unsupported or copy local law-updating code.
- Carbamate species can be listed in parameter documents, supports and reaction stoichiometry; no MDEA-specific ban was found in `problem()`. However **no carbamate or diamine calculation has been qualified through this driver**. Native admission of all nine AMP species, reaction references, thermochemistry and sensitivities is a preparation gate, not a result established here.
- #228's `run.py` and preparation code reproduce MDEA only. The driver does not independently discover source data, generate AMP phase states, guarantee identifiability or run the whole AMP phase campaign merely by reading TOML.
- Fitted Engine parameter JSON serialization remains unavailable under ePC-SAFT#928. A fit report and fitted reaction laws are available, but a reloadable final parameter/column hand-off is blocked. No new Engine issue is authorized by #227.

## Sequence, stop conditions and owner decisions

Readiness verdict: Block for numerical Build. Continue Research/Design to resolve the pure-AMP source, AMP protonation correlation, thermodynamic carbamate law and representation, admissible calibration sources, nonredundant NMR observables, assessment domain, coordinate declaration, and primary falsifier. Source acquisition and transcription may proceed as separately authorized preparation. A numerical preparation Build issue requires settled equations, named inputs, and explicit reference checks and tolerances; it must not delegate unresolved model choices to the implementer. Joint fitting additionally requires retained preparation results, owner-frozen data roles, scales, weights, bounds and starts, and a Ready review. PZ/blend source gaps and absorber transport gaps remain later work and do not enlarge the first AMP task.

Only the sources actually selected for the first AMP assessment must be transcribed before its execution; verifying all 48 indexed files is not necessary.

| Open decision | Recommendation | Effect |
|---|---|---|
| First amine | AMP, then PZ, then blend | Limits the first species/interaction expansion |
| Carbamate | Include AMPCOO−; resolve Ciftja 2014 and activity law first | Bicarbonate-only design cannot claim NMR agreement |
| Ion convention | Assess A and B side by side; common carbamate convention | Prevents claiming MDEA determines AMP behavior |
| Pure AMP source | Verify Pakravesh SI and original Ayad PC-SAFT; no SAFT-HR substitution | Blocks numerical declarations until verified |
| Coordinates | Executable set and count undetermined; select the smallest supported set with sourced fixed values or ties | No unapproved enlarged fit or implicit bounds |
| Primary hold-out and tolerance | Prefer an independently verified partial-pressure campaign; no numerical limit adopted | Must freeze before optimizer; proposal only |
| Missing heat/Cp/density | Begin pressure/speciation assessment only; retain those property gaps | No absorber or caloric qualification claim |
| Source preparation authority | Acquire/read missing originals in a later authorized step; none added here | No CESAR-1 data may be copied |

Stop for unresolved source identity/basis, circular calibration, missing carbamate constants/parameters, native refusal, absent uncertainty scale or bounds, incompatible caloric references, phase instability, weakly determined predictions or hold-out failure. Preserve failures and missing predictions. Do not change shared species, loosen gates or fit blend data to rescue a single-amine failure.

## PZ and blend outline

PZ preparation adds two protonation and three carbamate-related equilibria, the neutral zwitterion and doubly charged ions. Resolve pure PZ PC-SAFT and solid solubility before fitting; verify Ermatchkov NMR, Dugas plus its correction, Kamps/Xu pressures and Hilliard/Liu calorics. Freeze separate molecule/site loading conversions and independently select PZ campaign blocks. Do not reuse AMP's coordinate count or pass bar without design.

For the blend, first freeze accepted AMP and PZ single-amine records and predict unloaded Hartono VLE and untouched loaded Brúder/Dash/Hartono/Jahangiri/Li campaigns under declared cross-pair defaults. Then, only by owner approval, fit a small subset of blend pairs to designated calibration campaigns and test an untouched blend campaign. SEPPL/TCM plant comparisons belong to the column after transport and kinetic inputs are supplied; see [absorber gaps](absorber-gaps.md). Retain a research notebook only when a later authorized study produces numbers. This draft contains no physical validation or parameter promotion.
