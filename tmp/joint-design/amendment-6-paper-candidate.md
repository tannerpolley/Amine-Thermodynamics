# #170 amendment 6: assess the amendment-4 paper candidate

Design draft, 18 October 2026; implementation base `7adacac`. Starting stage:
`cse:design`, because the remaining question is which existing endpoint and
bounded comparisons can support the paper, with explicit rejection rules.
**This task changes one document only. No thermodynamic evaluation, fit,
parameter adoption, manuscript edit or GitHub write was performed.** The
parent owns publication and independent readiness review before execution.

Abbreviations: MEA = monoethanolamine; ePC-SAFT = electrolyte perturbed-chain
statistical associating fluid theory; SSM+DS = solvation-shell model with
dielectric saturation; AARD = average absolute relative deviation; RMSE =
root mean square error; Cp = isobaric heat capacity; CPU = central processing
unit. MDEA = N-methyldiethanolamine; SAFT-HR = Huang–Radosz statistical
associating fluid theory. JSON = JavaScript Object Notation; CSV =
comma-separated values; PDF = Portable Document Format; SHA-256 identifies
the 256-bit secure hash of file bytes. MEAH⁺ denotes protonated MEA. A loading is mol CO₂ per mol analytical
MEA; solvent mass fractions exclude CO₂. F1–F6 are the paper's existing fit
labels, defined where used below. All recommendations below are reversible
proposals for the parent and owner, not adoption decisions.

## 0. Revision 2 (18 October 2026): density first

Readiness review r1 (GPT-6 Astra, extra high) returned **Revise**; review r2
(same reviewer, new round) returned **Revise** with corrections, all applied
below. This section supersedes §§1–3 and §6 where they conflict, including
§1's deferral of the density fit (#183): positive density weights are
reinstated under the owner's 2026-10-13 #183 decision and the reviewed
stage-6 design, reversing the orchestrator's own away-mode deferral. §§4–5
and 7 apply only after this step and an owner λ choice.

**Known density result.** Both λ = 0 amendment-4 controls fail the unchanged
#183 gate on its 12 fitted loaded rows (each ≤ 2 kg/m³):
- **Larger d_V:** −24.28 to −108.16 kg/m³ (`amendment-5/a0/probe-p-analysis.json`).
- **Smaller d_V:** −24.28 to −108.15 kg/m³ (`amendment-6/smaller-dV-density/`).
  - The two branches differ by at most 0.0087 kg/m³.
  - Information-only call, 19.75 s wall, no new code.
  - Cold replay of the 205 objective rows: 6.9e-12, relative cost difference 1.3e-14.
- **Paper record F1 (`66ff7715`), without translation:** +136 to +190 kg/m³ at the four retained states (323/343 K, loading 0.3/0.4; `heat-final-170/evaluation/density.csv`).
- **The fallback with its empirical translation also misses the gate:** 15 of the 20 required loaded rows lie outside ±2 kg/m³, with errors −3.68 to +3.85 kg/m³ (`heat-final-170/corrected-densities.csv`). It is a disclosed approximation, not a pass.

No retained record meets the density gate.

**Why density next (from retained records).**
- **No density in any fit:** every tracked joint-refit declaration with a `fit_case` (17) has `density_weight = 0`, so the loaded densities have never been in a fitted objective.
- **What acts on the ion diameters at λ = 0:** pressure, species, heat and heat-capacity rows only. Both ion segment diameters end on their 5.8 Å bound.
- **The density-sensitive coordinates:** ion segment diameter sets the hard-sphere volume; packing and Debye–Hückel diameters are tied at 0.88σ, and the Born diameters are separate (Figiel, Yu and Held, Eqs. 3–4).
- **Limit of the evidence:** the old record and the amendment-4 endpoints differ in more than ion size, so their opposite density errors do not establish a bracket on one model. The #183 r1 fixed-size checks on the paper-record basis motivate the test; they are not proof of feasibility here.

**Step 1: first screen of the density-weighted F1 sweep in the reviewed stage-6 design.**
Source: #170 comment 6158000919, "Run F1 at λ = 0, 0.01, 0.1, 1".
- **Scope:** larger d_V, start A only. **The smaller branch and second starts remain outstanding** under the #172 design (both branches, both starts, no branch-selection gate). Reducing that scope permanently needs an explicit owner disposition.
- **Start:** A4 larger control start `matched-larger-dV/control-start-parameters.json` (SHA-256 `e01e1142…`).
- **Release tests:** one information call per λ ∈ {0.01, 0.1, 1} at that start.
  - Declaration: no `fit_case`; `information_starts` holds that start only; `information_density_weights` [λ].
  - Each writes its own `release-tests.json`, which must hold the matching start and λ with both pass fields true. Its hash enters that λ's fit declaration.
  - A λ whose record fails is not fitted, and the failure is retained.
  - Reweighting the retained start Jacobian (r2) gives augmented conditions of about 4,887, 4,521 and 4,031, under 1e4.
- **Fits:** F1 at λ = 0.01, 0.1 and 1, run in that order.
  - Same declaration as `matched-larger-dV/control-fit-spec.json` except: `fit_case.density_weight`; the release path and hash; the wheel path, set to the retained `build/engine-wheels/main-21e761c3…/` file with an unchanged hash; and the budget and ledger fields below.
  - Density rows: weight λ/12, scale 2 kg/m³.
  - Rows: 178 reacting, 217 total.
  - Controls as in amendment 4: function tolerance 1e-6, 600 s native limit, 32 workers, `nice -n 10`, single-threaded numerical libraries.
- **Endpoint evaluation:** one information call per endpoint, with no `fit_case` and density weights [].
  - Cold replay on all 217 fit rows at the fit's λ/12 weights, against the fit's `native.json`, within 1e-8 for rows and relative cost.
  - `check_matched_co2_mea.py` is not reused: it drops density rows.
- **Costs kept distinct:** C149 (common), C166 (all non-density reacting rows), C178 (reacting rows with density), C217 (with Kiepe).
- **Trade-off table for the owner,** for λ = 0 (A4 control), 0.01, 0.1 and 1:
  - C149, C166, C178;
  - pressure and species average absolute relative deviation, and Vinjarapu RMSE, on the common 149;
  - the four Cp values;
  - the 12 densities;
  - both ion segment diameters, both Born diameters, the active bounds, the free-block condition, and the projected gradient.
  - The 8 loaded and 5 unloaded assessment densities follow for any λ the owner considers.

**Hypotheses, pre-stated; none is a necessary outcome.**
- Density weighting may reduce the loaded-density errors and move one or both ion segment diameters off the 5.8 Å bound.
- The location of any optimum, whether the Born diameters move (density residuals do depend on them: retained start derivatives about 0.035 and 0.050 per scaled coordinate), and the change in C149 are open.

**Outcome statements.**
- If no λ produces a converged, replayable endpoint with all 12 densities within 2 kg/m³: "the declared sweep did not produce a candidate satisfying the density requirements." That says nothing about the model form beyond this screen.
- No empirical correction is authorized or transferred automatically.
- A non-converged or non-replaying fit is a numerical failure, kept distinct from a converged endpoint that misses the gate.
- Owner selection and adoption, and the full 20 loaded plus 5 unloaded checks, are unchanged.

**Compute, without raising program caps.**
- **Step allowance:** 1,500 compute-wall s and 15,000 CPU-s.
- **Per-call allowances:**
  - Information calls: `nonfit_wall_s` 180 and `nonfit_cpu_s` 500, as before.
  - Fits: `fit_wall_s` 600 (guard 720) and `fit_cpu_s` 6,000. The A4 fits used 3,008–3,247 CPU-s.
- **Carrying charges:** each declaration's `budget_*` equals the step allowance minus the actual charges of earlier step-1 calls, and its `program_prior_*` equals the program total at launch.
- **Admission:** a call the guard refuses is not run, and the sweep is reported incomplete.
- **Forecast:** about 870 s and 10,020 CPU-s.
- **Ledger before:** 10,638.83 of 21,600 s and 93,726.34 of 144,000 CPU-s.
  - That includes the 0.08 s wall / 0.06 CPU-s setup failure, whose GNU time record is retained in `setup-failure-wheel-path/command-time.json`.
  - Spending the whole allowance leaves 9,461.17 s, above the 1,950.38 s check reserve, and 35,273.66 CPU-s.

**Code:** no new lines. Declarations only. The post-processing that reduces densities and replay is disclosed scratch, with its text retained, as in amendment 5.

**After step 1:** the owner chooses λ, chooses none, or disposes of the outstanding branch/start scope. The §3–4 assessment and the §5 comparison family then run at that λ, with the r1 corrections:
- the weaker Born hypothesis;
- mixed-outcome rules for cost against pressure;
- the zero-weight no-heat route, with the stage6_rows assertion kept;
- verification compute added to the allowance.

The 250-line request stays deferred.

## §0b. Revision 3 (owner decisions 2026-10-19; readiness r1 corrections)

**Authority and question.** This is the single authoritative revision-3 section; it incorporates the
former §0c and supersedes §§0–7 wherever they conflict. The [owner decisions](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6275729199)
authorize combined-source density and Held-form fits; the [accounting decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6276283139)
sets a **1,250-line campaign-code ceiling**. The recorded owner answers additionally authorize stage 2b
and settle #172 as **one second start B and one smaller-d_V fit for the selected form**; further
branch/start combinations are not run. Question: can a density-fitted candidate support the paper within
the stated calibration and phase limits, and which comparison claims survive? This remains Design: the
parent owns independent readiness review/publication before Build; the owner adopts parameters. No
thermodynamic call, fit, implementation, manuscript edit or GitHub write is part of this revision.

Paths: `R` = `analyses/mea_parameter_bundle/results/joint-recalibration-170/`, `A4` = `R/amendment-4/`,
`A6` = `R/amendment-6/`; scripts are in `analyses/mea_parameter_bundle/scripts/`. Campaign accounting base
and the existing cumulative ledger stay fixed; `599497f` is this document revision's starting commit.
Count incremental Build additions against `f387725`, carrying forward the existing 1,000-line charge;
this comparison does not reset or recount the historical campaign.

**Loaded observations and adopted basis.** Fit **52 loaded rows**, without translation, at assumed
100000 Pa and nominal 30 mass % MEA in CO₂-free solvent:

- Amundsen 2009 Table 3 p.3097: all **20** rows, α = 0.1/0.2/0.3/0.4 at 25/40/50/70/80 °C,
  states 060–063, 065–068, 070–073, 075–078, 079–082. The eight former assessment rows become calibration.
- Hartono, Mba & Svendsen 2014 Table 3 p.1810: the **32 own, unsuperscripted** cells at printed
  α = 0.11/0.19/0.29/0.39 and 20/25/30/40/50/60/70/80 °C. **Printed α with nominal solvent
  W = 7.911062165 mol water/mol MEA is an adopted assumption, not a resolved composition.** Select by
  source-cell identity; omit the table's cited literature cells. The eight own α = 0.50 cells are
  assessment only, as are the eight own unloaded cells; six of those unloaded cells already have retained
  observation rows. No optional Hartono unloaded rows are added to stage 2b.

Consume `data/reference/MEA/observations/density_viscosity/Hartono_2014_loaded_density.csv` from
`adopt-hartono-2014-loaded-densities-into`, commit **`b998d03849d9a2f1357aec57d1a0d3949abe15fc`**, SHA-256
**`be0daa47de963643c498af015b430ae785a3f0b0103a23f3d5f9f81102cee7b4`**. Its README, “Adopted fitting basis”,
records the owner decision; the 32 admitted cells are `property_target_candidate`, the eight α = 0.50
cells `validation_only`. The branch must merge to main before Build; verify identical bytes and retain
both adoption and merge identities. This is a merge dependency, not a new composition decision. Preserve
printed α, x₃, alternative α and source IDs. Never use `density-sweep-1b/hartono-check/rows.json` as adopted
observations. The adoption records source PDF `5VGPDVGB`/`L7SKR73P`, Table 3 p.1810, and its separate
supplement; this revision does not re-adjudicate that source review.

**Density scales, weights and ambiguity.** Let ρ be mass density in kg/m³, α mol CO₂/mol analytical MEA,
w the CO₂-free MEA mass fraction, and g the source-local loading slope. Freeze before fitting:

$$
s_j^2=u(\rho_j)^2+[g_j u(\alpha_j)]^2,\qquad
g_j=(\partial\rho/\partial\alpha)_{T,w},\qquad
C_\rho=\frac{1}{2\,52}\sum_{j=1}^{52}[(\rho_j^{calc}-\rho_j^{obs})/s_j]^2.
$$

Use **λ = 1, weight 1/52 per loaded row**, in fitting, information and replay. Each source's four
admitted loaded cells at the same T supply adjacent one-sided secants at endpoints and secants spanning
the two neighbors internally. For Hartono these are at the adopted **nominal** composition; their use
is conditional on that assumption. Exclude α = 0.50 and cross-source/model slopes. Freeze source-cell
pairs, g, both uncertainty contributions, s and input hashes in one table; reuse it for all forms.
Source block shares are 20/52 and 32/52; other A4 weights stay fixed except the CO₂-free block specified below.

Amundsen pp.3096–3100, Experimental Section/uncertainty discussion: u(ρ) = **2 kg/m³**, u(α) = **0.02α**.
Its combined density uncertainty already includes composition and excludes the highest temperatures and
loadings: adding loading again is the owner's operational rule, not an independent-error model; nominal
u(ρ) = 2 at 70/80 °C remains an engineering target. Hartono Table 3 footnotes b–c: **u(ρ) = 0.02 kg/m³,
u(α) = 0.01**. Preserve the separately printed **U(ρ) = 0.02 kg/m³**, coverage factor 2, without halving
u or claiming statistical coverage. The resulting Hartono s is about 1.8–2.2 kg/m³.

**H1/H2 is separate from s:** a possibly systematic effect shared across each temperature series, not
another independent per-row variance. After selecting the final candidate, perform **one sensitivity
refit**, same form/branch/start endpoint, replacing only the 32 fitted Hartono loadings by
`co2_loading_from_mole_fraction_mol_per_mol_mea` at nominal 30 mass %. Keep the frozen scales, weights,
cell IDs, coordinate box and other observations unchanged; run its own release and full replay. Retain
parameter/cost/density changes without selecting a new primary fit or tuning weights. Report H2's
**+0.9 to +2.3 kg/m³** composition-shift estimate from the adopted README; do not fit it, shift targets,
or fold it into s. This one alternate-loading fit tests sensitivity, not resolution of the composition.

**Density gates.** All 52 loaded predictions must be available/finite and satisfy **|error| ≤ 2s**;
report signed errors, maximum |error|/s and counts by source/T/loading. The multiplier 2 is an engineering
tolerance, not a 95% interval or a published MEA standard. Keep the retained **8.5–9.1 kg/m³ Amundsen excess
near α = 0.4** visible on the printed-α basis. Do not average conflict rows, inflate scales or exempt them.
All five Amundsen CO₂-free rows at 25/40/50/70/80 °C must satisfy **|error| ≤ 0.5 kg/m³**, exact zero
analytical carbon, without a multiplier or density correction. Any miss blocks adoption.

**Stage 2b: fix the neutral temperature trend before joint fitting.** The retained
`A6/neutral-slope-probe/{README.md,probe.py.txt,result.json}` predicts Δk ≈ −0.0055, b ≈ −9 K and errors
−0.473…+0.434 kg/m³ at density weight 10, with Cai-only cost 91.33 → 92.26 (about 1%). This is a linear
prediction at the step-1b Hartono-target endpoint, not a completed fit or evidence that the gate passes.

- **Reference and starts:** freeze that endpoint from `ceb40c1`,
  `A6/density-sweep-1b/hartono-fit/fit/usable-budget-endpoint.json`, SHA-256
  `05ac5071c29d23c4f189edfcaa51ee118c912e2a05918477b3dd00137907f405`, as `reference_path`.
  Hold all other parameters fixed, including water, MEA, CO₂, association, ions, chemistry and CO₂–water.
  Reuse stage 2's MEA–water starts **A: k = −0.08031722618968729; B: k = −0.052**, each with b = 0.
- **Two coordinates:** $k(T)=k+b(1/T-1/313.15)$, T and b in K. The constant
  `pair/monoethanolamine/water/k_ij` has bounds [−0.5,0.5], scale 0.01. The slope
  `pair/monoethanolamine/water/k_ij/reciprocal_temperature_slope` has family
  `k_ij_reciprocal_temperature_slope`, target `[monoethanolamine,water]`, bounds [−1000,1000] K, scale 10 K.
  In the start document the MEA–water pair needs a coefficient with that exact identity/family,
  `value={magnitude:0,unit:kelvin}` and `reference_temperature={magnitude:313.15,unit:kelvin}`; retain the
  accepted coefficient provenance/domain fields, citing this amendment for the new MEA–water coefficient.
  Use the existing `additional_coefficients` insertion once, not both insertion and a duplicate coefficient.
- **55 fitted rows:** retain all 50 Cai targets (25 boiling temperatures and 25 vapor-water fractions)
  from `stage2/spec.json`'s `neutral-mea-water`: scales 1 K and 0.01, **weight 1 each**, unchanged feeds,
  pressures, exclusions and neutral domain to 436.85 K. Set **all five** Amundsen rows
  `AMU-DENS-{002,009,016,023,030}` to scale **0.5 kg/m³, weight 10 each**. This replaces the three
  weight-1/3 rows and two zero-weight rows; it does not add duplicate observations. Weight 10 is the
  retained probe's all-five passing linear case, not a statistical uncertainty claim. Freeze this choice;
  no weight scan. The objective is the half-sum of these 55 weighted squared residuals.
- **Executable path and release:** a stage-2 declaration with one case, `coordinates` (two), `starts`
  with `values=[k,0]`, `observations_id=neutral-mea-water`, `target_count=55`, and a hashed copy of its
  amended rows is sufficient. `stage2_study` inserts the slope before creating starts;
  `stage2_native` already iterates coordinate families; `stage2_rows` already constructs the exact-carbon-zero
  density problem. Use 40 iterations, function/parameter tolerances 1e−10 and gradient 1e−8, native fit
  bound 60 s, non-fit bound 60 s. Existing start assessments release both starts only when every declared
  row is finite/available and passes the existing equilibrium checks; no stage-6 release-file imitation.
- **Endpoint checks:** existing `stage2_study` checks both coordinates/bounds/rank, cold serialization replay
  (IDs identical, weighted-row difference ≤1e−8, relative total-cost difference ≤1e−8), material/charge/mass
  balances and zero carbon, raw residual ≤1e−9, positive pressure-density derivatives and nonnegative reduced
  Hessian. Retain centered re-solves for both coordinates at optimizer steps 0.01/0.005, absolute/relative
  errors ≤1e−8/1e−5, all shifted rows and roundoff evidence. Choose the lower replayed-cost complete
  endpoint; report start agreement against 1e−6. Score Cai's 50 rows separately from the five densities.
- **Falsifier:** require all five errors ≤0.5 kg/m³ and Cai-only cost no more than **1.05 times the same-wheel
  constant-k reference's Cai-only cost** (about 91.33, not stage 2's density-inclusive 91.8454). If the
  nonlinear fit cannot meet both, or a required numerical check fails, return the measured trade-off to
  the owner. Do not replace fixing the gate with a limitation sentence or commission another fit.

The neutral slope and two-coordinate fitting need **zero new numerical code**: this follows inspection
of `stage2_native`, `stage2_rows`, `stage2_study` and the existing CO₂–water slope declaration. Stage 2b
uses the whole-launch admission rule below (no new code). Substitute its selected MEA–water
k and b into every joint start document, then freeze them in stage 6. Carry the same five CO₂-free rows,
scale 0.5 and weight 10, through the existing `stage2_rows` added-row path under each case's row-table key.
The joint density-weight replacement must address only the 52 **loaded row IDs**, preserving these five
weights. Ion fitting can move the CO₂-free predictions slightly through trace MEAH⁺; recheck their gate.

**Retained step-1b expectations.** Evidence is **`ceb40c1`**, merged to main as **`f387725`**, delivered
review **Supported**; use `A6/density-sweep-1b/{README.md,summary.json,reduce.py.txt,*-spec.json}` and
nested declarations. These source-specific λ = 1 fits used 12 densities, scale 2, weight 1/12:

| λ = 1 target source | C149 / C166 | Pressure / species AARD | Vinjarapu RMSE | All 20 Amundsen errors | Hartono 32 errors, printed α |
|---|---:|---:|---:|---:|---:|
| Amundsen | 24.726 / 41.313 | 12.44 / 7.10% | 1.881 kJ/mol | −4.52…+2.87 kg/m³ | +0.55…+6.26 kg/m³ |
| Hartono diagnostic | 24.678 / 41.147 | 12.40 / 7.10% | 1.855 kJ/mol | −10.12…+1.03 kg/m³ | −3.42…+2.05 kg/m³ |

Replay differences are ≤5.3e−12 on 217 Amundsen-fit rows and ≤2.2e−12 on **201 shared** Hartono-fit rows;
Hartono-fit Cp was not replayed. Neither fit was assessed under the new objective. Both pass only 4/5
CO₂-free rows (25 °C errors −0.980/−0.985 kg/m³); the stage-2b correction is now required. Born diameters
remain 5 Å. A loaded-density compromise and heats near 1.9 rather than A4's 1.515 kJ/mol are plausible;
no all-row pass is predicted. A smaller Born-off penalty than the old 80% pressure error remains an
inference, not a required outcome; Held-form density/calibration/phase ordering remains unknown.

**Matched F1 fits and selection.** Initially fit larger d_V, zero CO₂–MEA, both tied and Held forms.
Use A4 start A `matched-larger-dV/control-start-parameters.json`, SHA-256
`e01e114226597f04a1d1460fa4a4d00b6bb94bc05d17a7489768f8651ae4337d`, with the stage-2b neutral pair
substituted and the resulting start rehashed. Keep §5's 14 coordinates/scales/boxes, chemistry pivot and
other frozen quantities; use 180 iterations, function 1e−6, parameter 1e−10, gradient 1e−8, achieved
gradient reported. Pin merged Engine `21e761c3` and §2's immutable wheel hash.

In the tied form, all ion Debye–Hückel diameters remain 0.88σ. For Held initialize **all six** start-document
`debye_huckel_diameter` values to σ, set the two fitted diameter target factors and serialized ties to 1,
keep packing 0.88σ and Born independent. Four trace-ion sizes stay fixed. Held 2008 §2 between Eqs.2–3
and Held 2014 §§2.1/2.4 Eq.21 motivate this change; no Engine equation changes. A factor-only edit leaves
an incorrect start offset. Each start/objective gets fresh information (`fit_case` absent, one
`information_starts`, `information_density_weights=[1]`); bind release to start/rows/scales/weights/ties/wheel.
Release gates are available finite rows/columns, correct ties and consistent centered size derivatives at
0.01/0.005 under §4's decay rule. Spectra, rank, dispersion projections and conditioning are reports;
retain both dispersion coordinates, without fabricated old pass fields. Endpoint rank alone is not a stop;
nonconvergence remains a stop. Recheck packing and DH relations at start and cold-replayed endpoint.

Retain both complete endpoints. Prefer a candidate meeting density and §4 common-row/§3 heat ceilings;
among equally eligible vectors choose lower combined-objective cost, preferring Held within 1% of the lower
cost. No Wagner/transfer-based choice. If neither qualifies, an ineligible comparison vector can be chosen
by the same cost rule but cannot be adopted. For the selected **form only**, run the owner-authorized
larger-branch **B** and one **smaller-branch A** fit with the same objective, neutral pair and bounds.
B uses the frozen #172 `larger-dV/F1-B` coordinate values rebased onto the corrected current declaration,
not the CO₂–MEA variant or a comparison-family start. Smaller A uses its A4 control start with only its
dielectric branch change and the same corrections. Freeze hashes/total reaction shifts before release.
Select among those form's eligible endpoints by the same cost rule; report branch/start disagreement and
all combinations not run. Then do the single Hartono loading-sensitivity refit and selected-vector checks.

**Rows, assessments and comparisons.** Replace the original 12 loaded `direct_rows` by the frozen 52,
retain four Cp rows and append five CO₂-free rows through the added-row table. F1/F2/F3 have **223 reacting
/ 262 total** positive-weight rows (166 + 5 + 52, plus 39 Kiepe). Retain scores separately for common149,
original non-density166, five CO₂-free densities, 52 loaded densities, Kiepe and the complete actual
objective. Information/replay uses precisely the same IDs, scales and weights; assessment-only rows remain
separate. No cross-row-count cost ranking.

Run §3's complete selected-vector assessment: all 103 Amundsen densities, Hartono assessment cells, four
Hilliard Cp values and proxy/enthalpy checks, 8 Vinjarapu/14 Arcis heats, 23 Wagner pressures, canonical and
packet 100–120 °C cohorts, 33/37 transfer pressures, 19 Matin pools and the corrected ten-row Jakobsen
carbonate share. Preserve §3's feeds, row IDs, exclusions and source limitations; Cp adequacy is report-only.
Use `stage6_rows`, `stage2_rows`, `heat_items`/`predict` and existing native enthalpy actions with explicit
parameter documents, not old forced substitutions or candidate density translation.

Run §4's entire hashed **73-point** phase family, candidate reactions/reference, cold → two nearest
same-T starts → liquid/bubble diagnosis → two bubble starts, retaining every attempt. Apply #172 amendment 2:
every declared stability trial must finish without descent or failed/unresolved trial; failed, unresolved,
passed-two-phase and passed-single-liquid counts sum to 73. Frozen **old index 63 must classify unresolved**;
a newly completed calculation may pass. Run §4's exact gas-root state, both root requests, new physical
solve and 10⁻⁶–100 mol/m³ contribution scan. Retain Gibbs comparisons, positive pressure-density derivatives,
ε → 1 and bulk Born → 0; require absence of a stable ionic gas root. Finite shell is disclosed. These are
finite-support numerical checks, not proof of global phase stability.

For the selected form/branch run **F3, F2, no-heat, F4, F5 × A/B**: A = selected endpoint; B = its corrected
branch's A4 control start. Rebase R2/R5 increments/bounds to the same total-shift box; persist by identity.
F3 uses `fully-dissociated-debye-huckel`, removes Born-only records/two coordinates (**12 remain**);
F2/F5 keep `born` with `c_shell=c_dielectric=0`; F1/F4 keep both at 1. F4/F5 add 19 pools: **242/281** rows.
No-heat sets only eight Vinjarapu weights to zero in both target table and `observations` weights:
**215/254 positive-weight rows**, **262 constructed** for information/replay; evaluate excluded heats later.
Keep all density/Cp rows, scales and weights. Choose lower-cost complete A/B; report incomplete/single starts.
Keep §5's weaker Born hypothesis and §7's >1% **both-cost-and-pressure** F3 reversal stop. Mixed ordering
is reported with both numbers, never a general advantage. Missing heat gain/high-T trade-off retires those
claims. F6 stays excluded; a diagnostic comparison does not authorize adoption.

**One cumulative code account.** Under the 2026-10-19 owner decision the ceiling counts **campaign code
only**: `fit_campaign.py`, `fit_observations.py` and shared producers through which these fits/checks run,
including copied numerical methods, launch/guard code, imports and executable checks. The existing
`A4/compute-ledger.json:campaign_executable_*` account is **1,000 of 1,000** (891 + 56 neutral fitter + 39
matched check + 12 coordinate helper + 1 release assertion + 1 R2 write-back). Keep its established
nonblank/noncomment gross-addition basis; deletions buy no additions. Planned additions below are **206
(ceiling 250; cumulative at most 1,250, with 44 lines of margin)**. This is an estimate to be tested in Build, not proof of feasibility;
stop before exceeding it, without compressed statements, weaker checks or omitted numerical evidence.

Excluded, disclosed one-off scratch: `A4/neutral-fit/figure.py` (the disputed 17 presentation lines),
`A6/neutral-slope-probe/probe.py.txt`, step-1b's `reduce.py.txt`, `unloaded-eval-scratch.py.txt`,
`hartono-fit/unloaded-eval-scratch.py.txt`, and `linear-screens/round{1,2}/*.py.txt` at `ceb40c1`;
the previous `tmp/` diagnostic texts remain excluded. Future `A6/reduce.py.txt` reduces/plots retained
fit/assessment arrays only. Retain their text, hashes and invocation. No fit, phase solve, runtime guard,
or shared input/check function is concealed in these exclusions; anything imported or run by the campaign
is counted. The 17 lines are excluded under the decision, not added again to the ledger.

| Counted file / function | Responsibility and replacement | Maximum additions |
|---|---|---:|
| `fit_observations.py:stage6_rows` | Replace fixed `165+added` assertion by common + added + declared-direct counts; preserve uniqueness/zero-weight construction and five added CO₂-free rows. | 4 |
| `fit_campaign.py:stage6_study` weights | Replace both λ/12 rules by λ/N **only for frozen loaded IDs**; preserve CO₂-free weight 10 and use identical information/fit/replay weights. | 6 |
| `fit_campaign.py:stage6_study` write-back | Replace column-9/80 assumption by R5 identity/declared scale; preserve linked laws, unshifted reference and total shifts for 12/14 columns. | 6 |
| `fit_campaign.py:stage6_study` release/consumer | Replace obsolete condition predicates with finite/tie/derivative gates; bind input identities, retain diagnostic spectra and separate nonconvergence from rank reporting. | 10 |
| `fit_campaign.py` source preparation / `verify` | Compute/freeze secants and s from declared source/T groups; reuse `checked`/`write` for hashes/table output. The ID/basis/scale and start-coefficient assertions are included in the check row below. | 10 |
| `final_evidence.py:selected/main`; `heat_evidence_170.py:select/main` | Accept explicit retained documents/declared widths; bypass displaced old-record, no-heat, translation and nominal-Jakobsen paths. Existing native row/heat/Cp producers do evaluations; one-off reductions score their retained arrays. | 8 |
| `final_evidence.py` phase functions, detailed below | Replace retired screen drivers by the candidate-only producer, including stability, attempts, classification, serialization and dispatch. | 150 |
| `final_evidence.py` / existing check calls | Executable persistence/replay, Kiepe, weights/scales, tie/derivative and frozen-classification assertions. | 12 |
| **Total** | **No new Engine equations, fitting algorithm, standalone screen driver, CPU guard or test suite.** | **206** |

The earlier **122-line phase estimate is withdrawn**. At `5ebcb37`, the seven historical functions contain
**150 nonblank/noncomment lines**: `flash_problem` 6, `family_job` 16, nearest `recover` 21, `diagnose` 20,
bubble `recover` 20, `contribution` 8, `falsifier` 59. They lack the required stability calls and current
classification. The replacement's function-level allowance is:

| Function in `final_evidence.py` | Reuse, deletion and required work | Lines |
|---|---|---:|
| `flash_problem` | Keep feed/support/tolerance; use candidate `_problem_from_request` reactions and `_neutral_reference`; drop old basis/Engine-case dispatch. | 6 |
| phase-result serialization | One explicit serializer shared by cold/recovery/bubble/root paths; `_phase_payload`, `_jsonable`, `write_json` carry lists/atomic writing, not native-object stringification. | 12 |
| `family_job` | Candidate model/problem; cold attempt and numerical evidence via serializer; no model-variant loops. | 10 |
| nearest `recover` | Pass model/problem/retained rows in; existing `solve_equilibrium_starts` and `EquilibriumWorkLimits` own two 400-iteration starts. Reuse serializer, remove duplicate setup/payloads. | 12 |
| `diagnose` | One liquid solve and candidate bubble solve, full evidence through serializer; remove historical file loading and duplicate model/problem setup. | 12 |
| bubble `recover` | Reuse that bubble state and common serializer; keep both amount starts and all native batch causes/results, no redundant bubble re-solve. | 10 |
| `contribution` | Keep every original contribution plus pressure-density derivative; reuse for solved, witness and low-density states. | 9 |
| `falsifier` | One candidate instead of basis/variant loops; reuse problem/model/serializer/contribution. Keep both witness evaluations, their Gibbs/closure evidence, new physical state, both root requests and all seven density-scan points. | 43 |
| stability/classification | Call `eq.stability_test(eq.compile_problem(model,problem),result,options)` on both declared trial supports; serialize report/trials and apply amendment-2 ordered failed/unresolved/two-phase/single-liquid rules. | 22 |
| imports, `main` launch and reduction | Reuse `final_evidence` imports, pool, `table`, `s.write_json` and counted-call owner; load/hash 73 inputs, bound each point across attempts, retain timings, assert counts, reduce classifications. | 14 |
| **Phase subtotal** | Reductions in duplicated setup/serialization fund new stability/classification; historical numerical evidence is retained. | **150** |

The serializer must retain result coordinates, phase amounts/compositions/densities/packing, pressure,
raw/classified residuals, balance/charge/pressure closure, stationarity and reduced-Hessian evidence,
iterations/evaluations/messages and each attempt's outcome. Stability serialization explicitly retains
`completed`, standards/plane/present-phase quantities and, for every trial, optimizer success/work,
`evidence`, `message`, composition, raw coordinates/residuals, basis/row transformation, quantities,
donor, split checks/coordinates and `resolved_descent`. `_jsonable` alone turns these native objects into
strings: it is not sufficient. Bound each point to 300 s **across all attempts**, using the common bounded
process owner; do not mistake a future wait timeout for termination of its worker. Phase dispatch and the per-point bound use the existing bounded child-process owner in
`fit_campaign.py`; they are included in the 150 above.

**Executable-check locations.** The 12-line assertion allowance and existing check calls must cover:

- `stage6_study` persistence plus explicit-document assessment: construct one 14-coordinate case and F3's
  12-coordinate case, check named R5 reference/linked reaction totals, serialize, and replay each width.
- `stage6_rows`/`stage6_study`: exact ID sets, 52 weights = 1/52, five = 10, frozen s values, Cp present,
  no-heat's eight zero weights, declared constructed/positive counts; then cold **full-objective** replay
  against `native.json`, ≤1e−8 weighted-row/relative-cost differences. Do not use the density-dropping
  `check_matched_co2_mea.py`; compare the fixed 39 Kiepe weighted rows at ≤1e−8 as well.
- Release and endpoint checks: packing = 0.88σ and DH = 0.88σ or σ, all six at start and after
  write-back (two fitted, four fixed); centered derivative evidence for each changed family/tie at
  0.01/0.005 under §4. Cp proxy/enthalpy verification for the selected vector runs as a **disclosed probe script**
  (owner scope 2026-10-19: one-off probe scripts are excluded from the ceiling): the four declared Hilliard
  requests at exactly 7 mol MEA/kg water, the native Cp against the centered-enthalpy proxy, and nominal-zero
  loadings 1e−6 and 1e−7 compared; its text, inputs and errors are retained. `verify_solution_heat_capacity`
  is not reused (it binds the default record and the historical `vle_obs_0130` composition).
- Phase classification: feed the frozen screen index-63 evidence through the **same** classifier used for
  new points; assert unresolved and the 73-count sum. A convergence flag without completed stability
  cannot pass.

**Compute allocation and admission.** Main **`f387725`**'s `A4/compute-ledger.json` already includes step 1b:
**9,536 of 21,600 compute-wall s and 36,721.39 of 144,000 CPU-s remained** before the neutral-slope probe (charged 2 s / 2 CPU-s, rounded up). **Owner, 2026-10-19: the program CPU cap rises to 200,000 CPU-s** (wall cap unchanged). Remaining: **9,534 compute-wall s and 92,719.39 CPU-s**. Do not add step 1b again.
Measured λ = 1 fits used **777 and 1,655 CPU-s** (67–136 wall-s); λ = 0.1 used **2,967**, λ = 0.01
**3,954 CPU-s**; information calls about **20 s**. New rows/forms may cost more. Allocations are aggregate
allowances, not predicted call costs or a guarantee that every comparison fits:

| Work, including its calls/cleanup | Wall-s / CPU-s |
|---|---:|
| Stage 2b A/B, release/replay/derivative/equilibrium checks | 300 / 2,000 |
| Two combined-density F1 forms, fresh releases and replays | 1,500 / 12,000 |
| Selected-form B and smaller-A fits; one Hartono loading-sensitivity fit, releases/replays | 1,600 / 15,000 |
| Selected-vector fixed assessment, Cp probe and bounded fallback replay | 1,000 / 2,000 |
| Selected-vector full phase family and gas-root evidence | 2,000 / 3,500 |
| Up to ten comparison fits, releases/replays | 2,600 / 45,000 |
| Other derivatives/persistence checks, reductions and contingency | 400 / 6,000 |
| **Reserved total** | **9,400 / 85,500** |

Leave **134 wall-s / 7,219.39 CPU-s** unallocated. Protect **1,950.38 wall-s** within the selected-vector
assessment/phase/verification allocations, and their **9,200 CPU-s**, until completed evidence releases
that reserve. Pending stage 2b and selected-form/sensitivity work also remain earmarked ahead of comparison
fits. Allocations may transfer only within these totals and without consuming still-required checks.

**Budget control by ordering (orchestrator revision after readiness r4, 2026-10-19; replaces runtime guards and launch bounds).**
Readiness rounds 2–4 established three things:
- the runner checks CPU only after a call;
- its teardown joins are untimed, so no launch lifetime is a proven bound;
- any executable preflight would be counted launch code.

The program caps are the owner's **planning budget**. Protecting the mandatory evidence does not need a
proven per-launch bound if mandatory work cannot be pre-empted by optional work. Hence:

1. **Order protects the reserve.** Every mandatory launch precedes every optional one:
   - stage 2b;
   - the two combined-density F1 forms;
   - the selected-form start B and smaller-branch A;
   - the Hartono loading-sensitivity fit;
   - the selected-vector fixed assessment, Cp probe, phase family, gas-root evidence and verification;
   - only then any comparison fit.

   Nothing optional runs while mandatory evidence is outstanding.
2. **Operator check before each launch, not code.** The orchestrator reads the program ledger and the declared call's
   wall fields, and records the arithmetic beside the launch in the step ledger:
   - **Mandatory launch:** launched while the program remainder covers it at the measured scale (≤ 4,000 CPU-s and 300 s per fit so far). If the remainder could not plausibly cover the outstanding mandatory work, stop and return to the owner (cap decision) rather than skipping evidence.
   - **Optional comparison fit:** launched only while the program remainder is at least **26,880 CPU-s**, which is 32 processors × 840 s, a conservative allowance, not a proven bound. It also needs **840 wall-s**.
   - **Runner fields:** stage-6 `fit_cpu_s` stays at the runner's existing post-call check value (3,000), so a fit that runs past it is still charged and reported. Each declaration's `budget_*` is that launch's own declared budget, capped by the program remainder. For stage 2b, `budget_wall_s = 300` and `budget_cpu_s = 13,440`.
3. **Charge everything and report overruns.** After each launch, charge the measured whole-command time (GNU `time`, children included) to the step and program ledgers. A mandatory launch that ends above the program cap is charged, reported to the owner and does not authorize optional work. Interrupted or failed launches are charged and recorded as incomplete.

This adds no counted code, no CPU guard and no claimed bound. With 92,719.39 CPU-s remaining and measured fits of 777–3,954 CPU-s, the mandatory sequence plus most or all comparison fits is expected to fit. The drop order governs any that do not.

Use `nice -n 10`, all discovered CPUs in one process pool, numerical-library threads one, sequential fits
and no subagents. First complete stage 2b → two F1 forms → selected-form B/smaller-A → loading sensitivity
→ selected-vector fixed/phase checks. Then comparison order is F3 A/B → F2 A/B → no-heat A/B → F4 A/B →
F5 A/B → remaining verification/notebook/review. Before optional launches, drop unneeded alternate/old-record
**phase families**, then F5 B/A, F4 B/A, F2 B and no-heat B. Comparison allocations must not displace the
selected-form fits/sensitivity or mandatory evidence. Protect both F3 starts and one start in each retained
family if affordable; retire any missing comparison's claim and label one-start evidence. If mandatory
work cannot finish, report unresolved and withhold adoption. Never omit a flash point/trial/observation to
pass, or launch another fitting screen to use a surplus.

**Falsifiers, output and remaining gates.** Density/neutral-Cai misses, failed/unresolved phase points,
a stable ionic gas root, missing low-density limit, unavailable checks, replay/Kiepe/derivative inconsistency,
calibration-ceiling miss or unfinished mandatory evidence prevent replacement. Distinguish physical
mismatch from numerical failure; the stage-2b trade-off and §7 Born-off reversal return to the owner.
Retain fallback **66ff7715** with its **existing empirical density correction**, corrected Jakobsen
comparison and calibration-dependency disclosure; it is not a density-gate pass (15/20 translated rows
missed the old ±2 limit). Preserve §7's immutable-record/successor distinction; transfer no correction.

The parent's remaining gates are the adopted-data merge and independent readiness **Ready**, then execution,
complete retained results/notebook and independent delivered review, followed by owner adoption and exact
notebook promotion before manuscript use. No #172 scope or Hartono basis question remains open. Retain
inputs/scales/hashes, all fits/attempts/timings and accounting under A6; update the existing notebook after
execution. This revision reports calibration expectations and numerical falsifiers, with no new physical
validation. Its checks were static source/declaration/history inspection and retained-number arithmetic;
no scientific calculation was run. The new line and runtime-guard estimates still require Build evidence.

## 1. Authority, question and retained evidence

**Supplied decision, 2026-10-18.** Seek a submission candidate from amendment
4; disclose the five bound-limited ion coordinates as effective parameters.
Defer charged-chain development (amendment 5), density fitting (#183) and
solution-Cp qualification (#124). Assess first, then obtain delivered review
and the owner's adoption decision. This supersedes the older #170 instruction
to make solution Cp pass before submission; it does not change measured Cp
values, numerical validity requirements, or the density/phase requirements.

**Question.** Does an amendment-4 endpoint improve the paper's calibration
while meeting the existing density and phase-use boundaries, and which Born,
observation-pool and heat-fitting conclusions survive matched comparisons?
The intended Fluid Phase Equilibria paper concerns conditional effective-parameter fits, primarily
30 wt% solvent, within the declared 293.15–393.15 K reaction domain. Different
row families have narrower source domains. No absorber/stripper qualification,
unique ion properties or broad physical validation is sought.

**Source facts.** Analysis paths below are relative to
`analyses/mea_parameter_bundle/`; manuscript paths are repository-relative. `R` means
`results/joint-recalibration-170/`, `A4` means `R/amendment-4/`.

| Evidence owner | Fact used here |
|---|---|
| [#170 joint design, part 2 §§6–8](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6158000919), [amendment 2](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6204801680), `A4/matched-*/README.md` | The current objective has 205 positive-weight rows: 149 common paper rows, seven restored species, six corrected Jakobsen ratios, four Hilliard Cp values and 39 fixed-binary Kiepe pressures. The 12 loaded densities have zero weight. The earlier 168/180-row design counts are superseded. |
| `A4/matched-larger-dV/README.md`, `matched-smaller-dV/README.md`; [delivered correction](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6247144877) | All four fits replay; five coordinates are on bounds. Free-block condition is about 3.7×10⁴; projected gradients are 0.008–0.010. Fixed-step ion-energy derivative errors show second-order truncation. Density and per-row caloric assessment remain unfinished. |
| `A4/README.md`, `b1-vapor-bound/README.md`, `neutral-fit/README.md`; [Xu disposition](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6252469842) | The Hartono-only neutral pair is determined, but changes reacting cost by only about 0.06%. Xu remains comparison-only; Hartono's Peng–Robinson source limitation still needs ratification. |
| `A4/final-prerequisites/README.md` | This records the earlier source-transfer stop, subsequently resolved by `b1-vapor-bound/`. Its old ledger, wheel and statements that fits are unrun are historical, not the current endpoint evidence. |
| `results/heat-final-170/`, `docs/scientific/latex/sections/mea_system_modeling_results.tex` §§heat, Born, pool and transfer | The old paper uses record `66ff7715…`: common-row cost 32.057, pressure/species AARD 13.81/7.89%, Vinjarapu RMSE 2.13 kJ/mol. Its five-coordinate contrasts cannot simply be relabeled as new-model results. |

The supplied common-row comparison is 32.06 → 24.56, pressure 13.81 →
12.76%, species 7.89 → 7.17%, Vinjarapu RMSE 2.13 → 1.52 kJ/mol.
Execution must reproduce these from exact row identities; they are retained
calibration evidence, not new predictions from this design.

**Literature boundary.** Baygi 2015 §§3.1–3.3, Table 5 and Conclusion fits
pure/binary properties, then assesses ternary MEA pressures and ideal-activity
species without ternary fitting. Najafloo 2018 §§3.1–3.3, Table 4 and Conclusion
uses SAFT-HR, selecting pure-MEA parameters and binary assumptions before
ternary comparisons; its Conclusion's broad fitting wording differs from
§3.2's explicit zero-pair choices. Uyan 2015 §§4.1–4.3 transfers protonated
MDEA inputs and fits binary properties before ternary assessment. These are
different formulations/data uses, not an accuracy ranking or a requirement
that this paper identify single-ion properties. Matin 2012, method and Figs.
2–3 discussion, pp.6616–6617, supports treating its bicarbonate report as an
inorganic-carbon pool and disclosing disagreement with nuclear magnetic
resonance measurements. Figiel, Yu & Held 2025, “Born Term”, “Model Parameters”
and “Gibbs Energy of Solvation in Water”, fits Born diameters to solvation
energies and distinguishes fitted finite-concentration interactions from
predictions. This campaign has no such independent ion-solvation constraint.
The numerical limits here are repository decisions or explicit recommendations,
not asserted published MEA standards.

## 2. Candidate identity and branch selection

**Recommend larger d_V, zero CO₂–MEA pair**, the existing F1 SSM+DS control.
Here d_V is the Schreckenberg dielectric-volume coefficient; larger/smaller
refer to the two measured-permittivity branches, not ion diameters. Keep the
smaller control as the sole alternate candidate. No new F1 fit is commissioned
to select the branch.

Reasons: larger has slightly lower common-149 cost (24.5609 versus 24.5966,
about 0.15%) and non-Kiepe cost (39.6902 versus 39.7366). That is a bookkeeping
preference, not statistically resolved superiority. The zero pair already
achieves the gain and avoids adding Hartono analogy/source-pressure dependence
to the paper's selected vector. This does not establish zero physical
CO₂–MEA interaction. The neutral-fixed endpoints remain sensitivity evidence;
their negligible reacting effect does not justify another comparison family.

Exact endpoint documents, all under `A4/` (SHA-256 of the complete JSON bytes):

| Branch / pair | Endpoint document | SHA-256 |
|---|---|---|
| **Primary: larger / (0, 0)** | `matched-larger-dV/control/usable-budget-endpoint.json` | `365758b80c7f701ac7c09c4319d4e216cf5b270374e856381f7d2ba8d1ea7f29` |
| **Alternate: smaller / (0, 0)** | `matched-smaller-dV/control/usable-budget-endpoint.json` | `c64a891d30aadaa573750dc1235d3c7c7614f8b26deda6337c28466e5bac06cf` |
| Larger / neutral-fixed | `matched-larger-dV/variant/usable-budget-endpoint.json` | `17d107229c08c6e90e8433c465b8ee316c4df8fe23d4fc7a0db4d7f62587830d` |
| Smaller / neutral-fixed | `matched-smaller-dV/variant/usable-budget-endpoint.json` | `0d6702894d7ebd35dc85a45ad717feb6f8dda3c3a0f015f9ba1f2c872ac35aec` |

Neutral-fixed means k(313.15 K) = 0.098720 and reciprocal-temperature slope
b = −50.989 K; use serialized full precision rather than these rounded values.
The filename “usable-budget-endpoint” does not confer adoption; native results
record convergence on function tolerance and the documented gradient miss.
Bind each document to its own `native.json`, fit declaration, chemistry and
`matched-checks.json`. Use the installed merged-main Engine `21e761c3`, wheel
SHA-256 `d2f61e3a5961b859151fbe0487f4ab633405b11620d9dd64682656a68a110357`.

**Selection rule, stated before assessment:** evaluate the two controls on the
same mandatory density, calibration, replay and phase checks. If larger passes,
retain larger even if smaller has a better report-only error. If larger fails
and smaller passes, recommend smaller with the failure disclosed. If neither
passes, do not replace the paper record. Do not select on Wagner, transfer,
Jakobsen carbonate-share or high-temperature errors and still call those
comparisons untouched. Owner adoption remains separate in every case.

## 3. Stage-7 assessment: fixed parameters, no fitting

Reuse source rows, scales and native equations; retain observed/predicted
values, signed errors, source locators, parameter/wheel hashes and every
unavailable case. No empirical volume translation enters these calculations.
Run the inexpensive density checks first on both controls; if both fail, stop
the replacement campaign before comparison refits. Complete the candidate's
phase checks before launching those refits. Assess the alternate's phase
family only if needed for selection; do not multiply every comparison by both
dielectric branches.

| Assessment rows and basis | Existing producer/method to reuse | Metric and disposition |
|---|---|---|
| **12 loaded densities**, Amundsen Table 3 states 060–063, 070–073, 075–078: 30 wt%, 25/50/70 °C, loading 0.1–0.4 | `fit_observations.stage6_rows` direct rows and native `phase_density`, mass basis | Every absolute error ≤2 kg/m³: **gate**. Retain all signed errors. These rows were zero-weight at amendment 4. |
| **Eight further loaded densities**, states 065–068, 079–082: 30 wt%, 40/80 °C, loading 0.1–0.4 | Same native density method, source selection below | Every absolute error ≤2 kg/m³: **gate**. #183 requires **20**, not only the 12 originally proposed fit rows. |
| **Five unloaded densities**, 30 wt%, 25/40/50/70/80 °C; three stage-2 fit rows and two temperature comparisons | `fit_observations.stage2_rows`, `shared_evaluation.unloaded_density_problem` | Exact zero analytical carbon, protonation retained; every absolute error ≤0.5 kg/m³: **gate**. Native density, no positive-carbon proxy. |
| **Other 78 Amundsen densities**: three 30 wt%/loading-0.5, 45 loaded 20/40 wt%, 30 unloaded non-30 wt% | Same density methods; pure-MEA support at neat-MEA endpoints | Signed/absolute errors and counts: **report**. Together with 25 gated rows, denominator 103. Do not reuse the old translated-density summary. |
| **Four Hilliard Cp states**, Appendix G.2 p.937/PDF994: 318.15/353.15 K × loadings 0/0.358, exactly 7 mol MEA/kg water, assumed 101325 Pa | `stage6_rows`' four direct observations; native equilibrium Cp and `verify_solution_heat_capacity` enthalpy actions | Observations 3.7195, 3.3675, 3.8566, 3.4707 kJ/(kg K), ordered by increasing T then loading. Relative errors against **3%**, frozen-composition Cp alongside equilibrium Cp: **report, not adoption gate**. Include both unloaded states, not the old three-state subset. |
| **Eight Vinjarapu heats**, Table 4 rows 1–8, 313.15 K/1.734 MPa, loading 0.11–0.45; **14 Arcis heats**, Table 5, 322.5 K, eight at 0.51 MPa/six at 1.03 MPa, loading ≤0.45 | `fit_observations.heat_items/predict`; per-row reduction in `heat_evidence_170.main` | Integral addition enthalpy per mol CO₂ from zero loading; negative releases heat. Per-row error, bias, AARD and RMSE in kJ/mol, Arcis also by pressure. Vinjarapu is fitted; Arcis previously accessed, outside objective. **Gate:** inherited #172 RMSE ceilings 3.13/9.36 kJ/mol; all detailed trends are reports. |
| **23 Wagner pressures**, 11 near 353 K and 12 near 392 K | `final_evidence.observations`, `job`, `score_rows`; admission/IDs in `results/temperature-reanchor-140/` | AARD, mean ln(calc/obs), individual errors and availability: **report**. No fitting or selection on these rows. “Untouched” means no fit/selection use, not never evaluated. |
| **100–120 °C pressure cohorts**: canonical 18+36 = 54; Hilliard/Jou packet 10+10 = 20, separately | `final_evidence` groups; `heat_evidence_170` high-temperature reduction | AARD and signed bias by source/T and with/without heat on identical IDs: **report**. Keep the full canonical 159-pressure set and packet 79 distinct; their overlap is not independent replication. Three canonical rows above 393.15 K remain explicitly inadmissible. |
| **15/45 wt% transfer**, 33/37 pressures | `final_evidence` transfer groups and frozen admitted IDs | AARD, signed bias and all failed/inadmissible counts: **report**. No concentration-transfer qualification or tuning. |
| **19 Matin pools**, original 18 plus restored state 016 at printed loading 0.455; source Table S.1, 21 °C represented as 20 °C | `stage2_rows` species sum on the corrected state requests; `final_evidence.score_rows` | Compare x(HCO₃⁻)+x(CO₃²⁻), AARD, mean ln(calc/obs), pool cost, common-row trade-off: **report**. F1/F2 omit these from fitting; F4/F5 below fit all 19. The paper's former exclusion of state 016 is retired. |
| **Jakobsen carbonate share**, the ten Table A2 nominal-30 wt% rows selected historically by maxload≤0.5 at 20/40 °C; original nine-state summary plus the previously excluded 40 °C/maxload-0.21 state displayed separately | Corrected-feed construction in `shared_evaluation.source_feed_request`/amendment-2 requests; replace `final_evidence`'s old nominal-state interpolation | Direct share n(CO₃²⁻)/[n(CO₂)+n(MEACOO⁻)+n(HCO₃⁻)+n(CO₃²⁻)], observed from printed species; calc/obs and range: **report**. Use w=0.2714274817259226 and each printed `loadNMR`; keep historical row membership without keeping maxload as the modeled loading. Fitted ratio state 011 overlaps this subset; state 022 is outside it. |
| **73 flash-family points** and **one gas-root falsifier**, §4 | Historical screen methods, incorporated in the existing assessment owner; native equilibrium/root/stability calls | **Candidate gates**, with the exact classification and root evidence below. Old-record comparison failures are retained, not substituted into the candidate count. |

Density selection is the existing `tmp/183-design/density-selection.csv`,
SHA-256 `d9d5f36e70290afd2535902d24645db2a6e12f6f705aabd2e6c9d7b22c8f3119`
(found in the main checkout, absent from this worktree). Materialize that
source-backed table under the retained run inputs before execution, without
its old predictions becoming new results. #183 [owner range decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/183#issuecomment-6156257968)
and #170 part 2 §7 own the groups. Density pressure is assumed 100000 Pa;
70/80 °C limits are engineering targets, not newly asserted measurement
uncertainties. Unreported high-loading cells remain absent.

Hilliard feeds use one mol MEA and n(water)=1/[7 M(water)], with the declared
molar masses and complete loaded-feed mass conversion. Keep the existing
10⁻⁶ nominal-zero Cp proxy and compare with 10⁻⁷ (relative change ≤10⁻⁶);
verify native Cp against re-solved total enthalpy at steps 0.1/0.05 K to 10⁻⁶
relative with convergence/roundoff evidence. A failed numerical Cp check
makes that Cp unavailable for interpretation; it does not silently relax the
check or restore solution-Cp adequacy as an adoption gate. Reuse the unchanged
#189 pure-water qualification by exact input identity. No new water fit or
full water sweep is needed. Direct thermodynamic Cp checks do not update the
absorber-owned thermodynamic qualification check C5 or claim a new column result.

The Jakobsen correction follows [#184's owner decision](https://github.com/tannerpolley/Amine-Thermodynamics/issues/184):
approximate 10% dilution, D₂O counted mole-for-mole as water, dioxane omitted,
printed `loadNMR` used as inferred liquid loading. The source CSV still carries
nominal compositions/maxload; execution must bind a corrected request table,
preserving printed fields. Never overwrite the observations to match a feed.
This assessment does not resolve droplet masses, isotope/dioxane activity
effects or the source mole-fraction denominator. Table A2 has 16 rows in
total; the ten-row comparison is the existing low-loading subset, not all
16. In the observed share retain the old sum-of-printed-carbon-species
convention: blank molecular-CO₂ cells are unreported and contribute zero to
that sum, not new evidence of zero molecular CO₂. Disclose this approximation
beside the model's total dissolved-carbon share. Do not refit the separate
carbonate species that amendment 2 deliberately pooled with bicarbonate.

## 4. Phase-use boundary and numerical checks

**Flash gate.** Materialize only the needed inputs/methods from screen commit
`5ebcb37`, `results/permittivity-screen-172/inputs/family-points.txt`, SHA-256
`6e1231d9506fd6dd9e965a64120ff952cebf1c4778da5d66cfb0f888e8b7f44b`.
Use candidate chemistry/reference, feed 9.7292821 mol MEA, 76.9751925 mol water
and loading×MEA mol CO₂; nine-species liquid, neutral CO₂/MEA/water vapor;
row tolerance 10⁻¹⁰. Follow cold solve → at most two nearest converged
same-temperature starts (400 iterations each) → single-liquid/bubble diagnosis
→ at most two bubble-based starts. Keep every attempt and phase amount,
pressure closure, balance, density and local-minimum evidence.

Apply [#172 design amendment 2](https://github.com/tannerpolley/Amine-Thermodynamics/issues/172#issuecomment-6131424985),
not withdrawn amendment 1. Stability searches must complete on both declared
trial supports; no resolved descent, failed trial optimizer, `unresolved`,
`indeterminate` or `negative_plane_without_positive_donor` evidence is allowed
for a pass. After the whole attempt sequence classify, in order:

1. **Failed:** no admissible final state, or any resolved descent.
2. **Unresolved:** other missing stability evidence, or pressure on the phase
   boundary within the Engine's own closure uncertainty.
3. **Passed two-phase / passed single-liquid:** respectively below / above
   that candidate's own bubble pressure, with the required stability and
   numerical evidence.

The four counts must sum to 73; eligibility requires failed=unresolved=0.
No guessed pressure band or density cutoff. Frozen screen index 63 must
classify unresolved from its old evidence; a newly completed calculation can
earn a pass. This is the one classification reference, not a new test suite.

**Gas-root gate.** Preserve 318.15 K, 3699.0803800848512 Pa, loading
0.25557798094241313 and the same feed. Reuse screen gas/physical witnesses;
request both native vapor and liquid density roots at the gas composition;
solve the new physical state. Retain root counts/densities, positive
pressure-density derivatives, closure and native Gibbs comparisons. Scan
fixed-composition density 10⁻⁶–100 mol/m³ for relative permittivity →1 and
bulk Born →0. The stable gas-density ionic root must be absent. A lower-Gibbs
ionic gas root fails the candidate; a missing root search or inconclusive
physical solve is unresolved. Old packing-coordinate Gibbs values are only
witness evaluations, never a new converged state. A finite SSM+DS shell term
is disclosed, not separately rejected. These finite supports do not prove
global phase stability.

**Other endpoint checks, proposed amendment to the old identification gates:**

| Check | Requirement for this paper-candidate use |
|---|---|
| Wheel/input identity, available finite rows, conservation/charge/stationarity, positive pressure-density derivative, phase support and native local-minimum evidence | **Gate**. Raw caloric residual ≤10⁻⁹; flash and declared reacting rows retain their 10⁻¹⁰ requirement. No omission, penalty replacement or denominator change. |
| Cold document replay | **Gate**: identical row definitions, cost relative difference ≤10⁻⁸ and maximum weighted-row difference ≤10⁻⁸. Preserve the corrected R2 serialization; both coefficients of linked reaction changes travel together. |
| Kiepe invariance | **Gate**: all 39 weighted residuals differ by ≤10⁻⁸ from the same-wheel fixed stage-2 binary. They add a fixed cost to the objective; ion/Born/chemistry contrasts cannot improve them. |
| Centered/native derivatives | **Gate for derivative consistency** on each newly changed family/tie, using optimizer steps 0.01/0.005 and, if needed, smaller halved steps. Retain the 10⁻⁸ absolute / 10⁻⁵ relative fixed-step limits and their misses. Accept demonstrated second-order decay toward the native derivative with no resolved nonzero offset, or a justified roundoff plateau; an inconsistent/nondecaying discrepancy stops the affected comparison. A4's ratio-of-four decay is evidence of truncation, not an undetected derivative defect or a claim that its fixed-step limit passed. |
| Full/free singular spectra, native relative rank cutoff 10⁻¹⁴, active bounds, weak directions, conditional covariance availability | **Report**. Retain condition 3.7×10⁴ versus former 10⁴ limit explicitly; no bound widening, weak-column freezing or inverse-covariance claims for deficient/bound directions. Full rank is evidence about local sensitivity, not ion identification. |
| Projected gradient and stopping reason | **Report**, including former 10⁻⁸ limit and the 0.008–0.010 miss. Retain function tolerance 10⁻⁶, parameter tolerance 10⁻¹⁰ and 100 iterations. The ≤3.6×10⁻⁴ Gauss–Newton predicted decrease is a local estimate, not a rigorous bound on a better optimum. No claim of global or tightly stationary optimality. |

No `checks_passed` aggregate from the old neutral-pair experiment decides this
new use. Conditioning and gradient limits are changed in the declared paper
assessment, not retrospectively marked passed for amendment 4. Comparisons
report achieved costs/errors. As a recommended reporting rule, differences
below 1% are described as near-equivalent within this bounded fitting exercise;
do not assert a precise ordering or spend the allowance polishing them.
This is a scientific reporting resolution, not a measurement uncertainty or
an optimizer error bound. A/B cost agreement at 10⁻⁶ remains reported; different
complete minima remain visible.

For the selected candidate retain #172's common-row ceilings: C149≤35.26,
pressure AARD≤15.81%, species AARD≤9.89%, plus §3's heat ceilings. Recommend
requiring C149 below the same-wheel paper-record C149 before calling this a
calibration improvement. Compare only common 149 definitions, never C205 to
the old cost. A transfer or Cp shortfall is reported within its stated scope.

## 5. Matched comparison fits and expected outcomes

**Common declaration.** F1 is the selected amendment-4 SSM+DS control, reused
without refitting. After §3–4 gates, run only the selected branch's alternatives.
For every alternative use start A = that candidate endpoint; start B = its
`A4/matched-<branch>-dV/control-start-parameters.json`. Apply only the stated
Born/target change. These are deterministic local-basin checks; two starts do
not prove a global minimum. Never copy old full F2–F6 parameter records onto
the new water, chemistry and dielectric model. No forced F1-A selection or
live selected-record substitution is permitted.

Keep the **A4** objective, not the superseded original stage-6 counts:
149 common + 7 restored + 6 Jakobsen + 4 Cp = **166** reacting rows, plus 39
Kiepe = **205** total; density weight stays zero. F4/F5 add 19 pools:
**185/224** reacting/total. No-heat removes only eight Vinjarapu rows:
**158/197**. Cp remains a fitted block, although its physical adequacy is
report-only. Arcis, all density rows and all transfer/phase rows remain outside
these fitting objectives. Score every endpoint on common 149 as well as its
actual objective; score no-heat's eight heat rows only after fitting.

**Coordinates and bounds.** Preserve all 14 A4 coordinate definitions, scales
and ties for F2/F4/F5/no-heat: carbamate–water and MEAH⁺–water k in [−0.5,0.5];
bicarbonate–water k in **[−0.5,1]**; mutual-ion k in [−1,1]; MEAH⁺–water
reciprocal-temperature slope in [−1000,1000] K; both segment diameters in
[2,5.8] Å with packing and Debye–Hückel diameters tied at 0.88σ; both Born
diameters in [2,5] Å; unshifted R5 reciprocal-T coefficient in [2400,3000] K;
both pivot-preserving R2/R5 enthalpy shifts in [−10000,10000] J/mol; MEAH⁺
dispersion/k in [50,950] K and carbamate dispersion/k in [50,1000] K.
Scales respectively 0.01 for k, 10 K for interaction slope, 0.1 Å for diameters,
80 K for R5 reference, 2500 J/mol for each shift, 10 K for dispersion energies.
The exact owner is the selected A4 `control-fit-spec.json`'s
`information_coordinates`, including source/native conversion and reaction
pivot at 313.15 K. R5's unshifted reference is recovered from the retained
chemistry coordinates; it is not the endpoint's already shifted stored
coefficient. At an endpoint start, rebase incremental shifts and translated
bounds to the same total-shift box, as amendment 2 specifies. Do not apply a
shift twice or reset the physical box around the new start.

F3 removes the two inactive Born coordinates, leaving **12** coordinates.
Retain both ion-energy coordinates across these comparisons; the A4 release
was already made. Their information diagnostics remain reported under §4,
rather than conditionally changing the fitted model between cases. Freeze
water, neutral MEA/CO₂, neutral binaries, association, dielectric branch, trace
ions, shell/solvation constants, remaining reaction coefficients and ideal
calorics exactly as in the candidate. No density translation is used.

The objective is the existing half-sum of squared weighted residuals, using
the unchanged pressure log-ratio weights, species difference scales, heat
interval scales, corrected ratios and Cp weights from the A4 declaration.
New Matin pools use scale 0.1x(observed)+0.001 and weight one, source Table S.1.

| Comparison, two starts each | What changes / claim tested | Pre-stated expected outcome and consequences |
|---|---|---|
| **F3: Born removed** | Remove all Born contributions; retain Debye–Hückel electrostatics. Same 205 rows, 12 coordinates. Tests the paper's old 13.81 →80.25% pressure-AARD contrast. | **Expect a substantially smaller penalty than the old 80% result; a near-equivalent fit is plausible.** Both Born diameters at their 5 Å upper bounds mean the fit pushes toward a weaker Born contribution. This is a parameter-direction inference, not proof the whole contribution is negligible. If F3 is clearly worse, report the new penalty within this model/box. If near-equivalent, retire “Born is needed for this accuracy”; if better in cost and pressure, the old Born-off ordering is reversed and §7 applies. Never retain the old 80% number as the candidate's result. |
| **F2: original Born versus F1 SSM+DS** | Change only the Born form, keeping its two diameters free; 205 rows/14 coordinates. | **Expect the cost gap to shrink; no confident pressure ordering is predicted.** If F1 remains lower, retain an empirical within-objective ordering with new numbers. If near-equivalent, neither form is preferred by this fit. If F2 is lower, remove the SSM+DS fit-quality advantage; a separate phase advantage may still justify retaining F1 for owner review. No mechanism or identified solvation radius follows. |
| **F4 and F5: Matin pool fitted**, respectively SSM+DS and original Born | Add all 19 distinct pools; 224 rows/14 coordinates each. Compare F4 with F1, F5 with F2, and F4 with F5 on the same 224 rows. | **Expect lower pool error and a higher base-149 cost**, because the pool competes with other species. Do not predict preservation of the old F4<F5 ordering. Persistence supports a bounded form ordering; reversal retires it. If the pool is accommodated with little trade-off, retire the explanation that excluding it is needed for fit quality; its analytical meaning/source discrepancy still stands. Objective totals across 205 and 224 rows are never directly ranked. |
| **Matched no-heat F1** | Set only eight Vinjarapu weights to zero; 197 rows/14 coordinates. Evaluate those eight and 14 Arcis heats afterward. | **Expect poorer Vinjarapu heat agreement and possibly improved high-temperature pressures**, as in the old fit, but neither magnitude nor high-T sign is guaranteed after joint chemistry fitting. If heats do not improve, retire the heat-fit gain claim. If high-T pressure no longer worsens, retire that trade-off statement. No attribution to heat alone is made from an unmatched old record. |

**Retire F6's source-law comparison for this candidate.** The old F6 changed
chemistry, CO₂ energy and interactions together. No F6 refit is needed for the
four specified claims; remove its candidate-relative numerical advantage,
temperature-law attribution and plotted comparisons in the later manuscript
stage. Keep it as explicitly historical evidence only. Re-establishing F6 is
an optional scope addition, not a hidden two-fit requirement.

## 6. Code, compute and order

**Zero new counted lines is not credible.** Static inspection found these
specific gaps; no execution was used to discover them:

- `fit_observations.stage6_rows` asserts 165+added rows, fixing the common and
  direct counts; a real no-heat omission fails it. Replace that assertion with
  counts from the declared row families while retaining uniqueness checks.
- `fit_campaign.stage6_study` indexes the R5 reference as optimizer column 9
  and requires the former conditioning release; removing two Born columns or
  starting from the candidate requires named-coordinate persistence and the
  explicitly amended information rule. Preserve total reaction shifts and
  cold replay; do not fabricate passing release-test records.
- `heat_evidence_170.select/conditional/main` and `final_evidence.summarize`
  contain forced F1-A/old-no-heat substitutions, five-column assumptions,
  nominal Jakobsen interpolation and density translation. Use existing native
  row/heat methods and retained-row reductions; retire these assumptions from
  the new assessment path. The old five-coordinate covariance presentation
  is not needed for effective-parameter claims.
- Historical `permittivity_probe.py`, `recover_family.py`,
  `diagnose_family.py`, `bubble_starts.py` at `5ebcb37` supply methods/inputs,
  **not a complete current producer**: they bind old chemistry, use fixed
  worker counts and omit amendment-2 stability classification. Incorporate
  only the needed calls/attempt sequence in `final_evidence.py`; do not
  restore five standalone drivers or import retired fit paths.

**Smallest planned executable change:** replacements in the existing owners,
with a proposed **250 gross added-line ceiling** relative to `7adacac`:
10 campaign/observation lines, 50 explicit row/comparison mappings and
reductions, 160 phase/root/stability assessment lines (including copied
historical code), 30 endpoint-check lines. This is a conservative design
estimate, not a measured implementation minimum or authority to add code.
Build must report actual additions/removals and stop before exceeding it;
no generic Engine equations, solvers or fit wrappers are added. Declarations
and source-backed input tables extend the existing campaign owner; they must
not hide executable Python in JSON, notebooks or ignored scratch.

The ledger counts **gross additions** at 1,000/1,000. Removing obsolete
selection/translation/five-column code is warranted, but **does not buy new
gross additions** under the current rule. This proposal needs an explicit
campaign-ceiling amendment to at most 1,250, plus disposition of the pending
17-line presentation exclusion (1,267 if counted). Ratifying that exclusion
alone creates no headroom. A net-line allowance would itself require an owner
rule change; it is not assumed. Design introduces zero executable lines.

**Compute source:** `A4/compute-ledger.json`, SHA-256
`1d213f36523820e0b4ca0f5c4c9cfd9caebdc9c7361a277b91cae75634a19674`:
10,981 of 21,600 compute-wall seconds remain; 144,000−93,706.61 =
**50,293.39 CPU-s** remain. Research/review/reporting do not spend compute
allowance. The old final-prerequisites mixed-wall ledger is superseded.

**Recommend an allowance of 9,000 compute-wall s and 50,000 CPU-s**, without
raising program caps:

| Work | Wall / aggregate CPU allowance | Basis |
|---|---:|---|
| Fixed-record properties, replay/derivatives, candidate phase tests and bounded old-record comparison | 4,500 / 12,500 s | Reserve mandatory checks first, including the existing 1,950.38 s wall reserve. At most three 73-point families: primary, alternate if needed, same-wheel old record. Allocate at most 2,000 CPU-s / 1,000 wall-s per family; the remaining assessment allowance serves rows/checks. These are caps, not measured forecasts. |
| Ten comparison fits: F3, F2, no-heat, F4, F5 × two starts | 3,000 / 35,000 s | Measured A4 reference: 200–225 wall-s and 3,000–3,250 CPU-s each on 32 workers; ten calls imply about 2,000–2,250 / 30,000–32,500 s. Allowance includes margin; changed alternatives may cost more. |
| Retained contingency | 1,500 / 2,500 s | Whole-run scheduling/numerical margin, not extra fits or a cap increase. |

This leaves 1,981 program wall-s and 293.39 CPU-s outside the proposed
allowance. The aggregate CPU allowance, rather than wall, is restrictive.
Use `nice -n 10`, discovered full CPU count for one worker pool (32 in the
reference runs), and one thread each for OpenMP/OpenBLAS/MKL. Run fits
sequentially; no nested pools or worker subagents. Keep the native 600 s
per-fit limit; non-fit native calls ≤60 s and each family point ≤300 s across
attempts. Check remaining aggregate CPU/wall between bounded calls, preserving
failures and any final-call overrun. The existing extra 120 s fit-process
join allowance is cleanup overhead, not permission for >600 s native fitting.

**Order:** readiness and code authority → input/row binding and same-wheel
replay → both controls' density gates → primary gas-root/flash checks (then
alternate only if needed) and all fixed candidate reports → choose branch
under §2 → F3 A/B → F2 A/B → no-heat A/B → F4 A/B → F5 A/B → row reductions,
notebook and delivered review. The old-record phase family is a comparison,
never a substitute for candidate checks; retain a failed old family as such.

**Drop order if CPU runs short:** optional F6 is already absent; omit any
unneeded alternate/extra control phase families first, then F5 B, F5 A, F4 B,
F4 A. Dropping a comparison retires its corresponding pool/form-ordering
claim; one start is labeled one start. Protect both Born-off starts and the
candidate's full mandatory checks. If F2 or no-heat cannot complete, retire
their conclusions as well, with explicit incomplete comparisons in review.
Do not omit density, a flash point, stability evidence or unavailable rows
to manufacture eligibility. If mandatory work cannot complete, return an
unresolved candidate and do not adopt. Never launch an extra fit solely to
spend the contingency.

## 7. Falsifiers, output and owner decisions

**Do not replace record 66ff7715 when** either control fails any in-range
density gate and neither alternate passes; a candidate flash point remains
failed/unresolved; the gas-root falsifier persists; complete replay/Kiepe or
derivative-consistency checks fail; common-row calibration loses the stated
eligibility/improvement; or required work is budget-stopped. Preserve the
specific physical discrepancy separately from a numerical failure. A detected
mapping/serialization defect requires diagnosis and affected evidence refresh,
not a limitation sentence or an unplanned fitting loop.

**Born-off reversal is a scientific decision stop, not an automatic new-model
selection.** Define it as both a lower common-149 cost and lower fitted-pressure
AARD for a complete F3 than F1, by more than the §4 1% relative reporting
resolution for each; smaller differences are near-equivalent. Such a result
undermines the chosen Born narrative, not numerical correctness. Recommend
withholding the SSM+DS replacement and returning to the owner with the new
ordering and phase evidence; do not adopt F3 through this design. If F3 is
near-equivalent, F1 may still proceed with the necessity claim removed. An
F2/F5 ordering reversal or missing heat trade-off retires those claims without
automatically rejecting a physically eligible F1. None establishes a unique
ion property or mechanism.

**Fallback:** retain the paper on immutable
`results/heat-160/A-parameters.json`, SHA-256
`66ff7715958e9d22e77bd129faf7f67822204e3285b50993bf3f67d72c3b9778`,
with a same-wheel replay. The current declaration-only successor
`results/selected-current-best-parameters.json` has SHA-256
`7b0b4bb5669c1b2061fd7ec26e5fb4c8491005bdb5ba8f9e22e4c0b0b4b84308`;
record that distinction rather than silently relabeling it 66ff7715. Recompute
the old record's Jakobsen comparison at §3's corrected states, disclose that
its fixed ion inputs were calibrated under the older Jakobsen conventions,
and retain density-translation, Cp and phase-use limitations. The fallback is
a paper basis for owner consideration, not certification of its phase family
or automatic permission to submit. No new ion-development campaign follows
automatically from amendment 6 failing.

**Retained output:** `R/amendment-6/`, with frozen declarations/row IDs/source
and wheel hashes in `inputs/`, per-candidate `assessment/<branch>/`, comparison
fits in `comparisons/<case>/<start>/`, row tables and phase attempts/classifications
alongside their numerical results, and one updated compute ledger referenced
from A4's program ledger. Preserve A4, old paper evidence and raw source rows
unchanged. The result tables distinguish C149, reacting C166 and total C205
(or the actual alternative row counts); every unavailable quantity carries
its reason. No empty-file or success-code result is accepted.

**Notebook:** add “Amendment 6: paper-candidate assessment” to
`analyses/mea_parameter_bundle/notebook.qmd`, reading retained tables only.
It must show selected/fallback identity, density errors/counts, four Cp values,
per-row heats, pressure/species comparisons, bounds/weak directions and
gradient/derivative qualifications, all 73 phase classifications and the
gas-root result, comparison outcomes versus expectations, compute used,
omitted claims, and the recommendation with limits. Render through the
existing static path without model execution or preview-service changes.

Then obtain **independent delivered review** of the identified commit,
complete notebook and retained results. Only after Supported review does the
owner decide adoption. Investigator promotion names the exact notebook commit,
intended manuscript use and limitations before later writing. **Manuscript
refresh, live selected-record/history updates, submission and push are outside
this task.**

**Open owner questions for the parent, with recommendations:**

1. Ratify the larger/zero primary and smaller/zero gate-based alternate;
   retain neutral-fixed as sensitivity only. This avoids needing the still
   pending Hartono source-limitation ratification to select the paper vector.
2. Accept §4's explicit effective-parameter interpretation: conditioning and
   projected-gradient misses are reported; numerical replay, consistency,
   density and phase gates remain. This does not reopen amendment 4's old
   neutral-pair decision as “passed”.
3. Approve the minimum planned owner changes and proposed 250 added-line
   allowance, or choose assessment-only/fallback with the present ceiling;
   settle the 17-line presentation exclusion separately.
4. Accept the 50,000 CPU-s/9,000 compute-wall-s allocation, F6 retirement and
   claim-removal order under shortage. No cap increase or open-ended fitting.
5. After evidence and review, adopt the passing candidate, retain the old
   paper basis with corrected comparison/dependency disclosure, or hold
   submission. This final decision is not made by this design.

**Inspection limits.** Read the live #170 body, stages 6–7 design and amendment
history through 18 October; #172 including amendment 2; #183/#124 and #184;
all requested A4 records and the fit/observation/paper-evidence producers;
historical screen source at `5ebcb37`; and the amendment-5 house design.
The ignored literature shelf was absent from this worktree; the existing main
checkout shelf and its index were read instead. Baygi, Najafloo, Uyan, Figiel
and Matin passages cited above were read directly; local/source hashes were
checked against the index (including Matin's PDF source hash). Exact Born
equation transcription was not adopted or changed; source/model equations
remain with the accepted Engine. No new literature search, source conversion,
scientific evaluation, implementation trial or independent readiness finding
is claimed here.
