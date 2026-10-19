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

Readiness review r1 (GPT-6 Astra, extra high) returned **Revise**. This
section supersedes §§2–3 and §6's execution order where they conflict; §§4–5
and 7 apply only after the step below and an owner λ choice. Revisions by the
orchestrator.

**Known density result (r1 correction 1).** Both λ = 0 controls fail the
unchanged #183 gate (20 loaded rows ≤ 2 kg/m³) on its 12 fitted rows:
- **Larger d_V:** −24.28 to −108.16 kg/m³ (`amendment-5/a0/probe-p-analysis.json`).
- **Smaller d_V:** −24.28 to −108.15 kg/m³ (`amendment-6/smaller-dV-density/`).
  - Information-only call, 19.75 s wall, no new code.
  - Cold replay of all 205 objective rows against `matched-smaller-dV/control/native.json`: 6.9e-12, with relative cost difference 1.3e-14.
- **Paper record F1 (`66ff7715`), without translation:** **+136 to +190** kg/m³ at 323/343 K, loading 0.3/0.4 (`heat-final-170/evaluation/density.csv`).

So no λ = 0 record passes. Density cannot choose between the λ = 0 candidate
and the fallback. The fallback passes only through the empirical translation.

**Why (diagnosis from retained records, not a new calculation).**
- **No density in any fit:** every joint-refit fit so far has `fit_case.density_weight = 0`. That covers the amendment-2 Route 2 and 2b fits and all four amendment-4 arms.
- **Nothing constrains ion volume:** the loaded densities were never in the objective. At λ = 0, only speciation and pressure act on the ion segment diameters, and both reach their 5.8 Å bound.
- **Opposite signs bracket the target:** the speciation-only paper ions over-predict density, and the 5.8 Å ions under-predict it. An interior size therefore exists that matches density, as the #183 r1 fixed-size checks found on the paper-record basis, an older model (worst loaded row 2.77 kg/m³ at MEAH⁺/carbamate 4.2/5.8 Å; 5.05 kg/m³ at 5.1/5.1 Å). That is evidence on that basis, not a result for this one.

**Step 1: the density-weighted F1 sweep already in the reviewed stage-6 design.**
Source: #170 comment 6158000919, "Run F1 at λ = 0, 0.01, 0.1, 1"; owner decision of 2026-10-13 on #183, which sets no trade-off limits in advance, reports each candidate's trade-off, and leaves the choice to the owner.
- **Branch:** larger d_V only. The branches agree on density within 0.01 kg/m³ and on C149 within 0.15 %. The smaller branch runs only if the owner wants both.
- **Start:** A4 larger control start `matched-larger-dV/control-start-parameters.json` (SHA-256 `e01e1142…`). Its A4 release test passed at λ = 0 (condition 3.45e3 mandatory, 6.39e3 augmented).
- **Release test:** one information call per λ ∈ {0.01, 0.1, 1} at that start, each with `information_density_weights` [λ] and its own `release-tests.json`. The fit path requires every record in its file to pass (`fit_campaign.py:510`), so one failing λ does not block the others. A λ whose record fails is not fitted, and the failure is retained.
- **Fits:** F1 at λ = 0.01, 0.1 and 1. Same declaration as the A4 control except `fit_case.density_weight`. Each density row has weight λ/12 and scale 2 kg/m³. Rows 166 + 12 = 178 reacting, 217 total. All amendment-4 controls apply: function tolerance 1e-6, 600 s per call, 32 workers, `nice -n 10`, single-threaded numerical libraries.
- **Endpoint evaluation:** one information call per endpoint (about 20 s), giving the 12 fitted densities and every common row. A4 cold replay applies.
- **Trade-off table for the owner:** for λ = 0 (A4 control), 0.01, 0.1 and 1, report:
  - C149, C166 and C178;
  - pressure and species deviation, and Vinjarapu RMSE, on the common 149;
  - the four Cp values;
  - the 12 densities;
  - both ion segment diameters, both Born diameters, the active bounds, and the free-block condition.
  - The 8 loaded and 5 unloaded assessment densities follow for the chosen λ only.

**Pre-stated expectations.**
- As λ rises, both ion segment diameters leave the 5.8 Å bound toward roughly 4–5 Å.
- Loaded-density errors fall toward a few kg/m³ by λ = 1, while C149 rises; the size of that rise is the trade-off.
- The Born-diameter bound may persist, since density does not see the Born term.

**Falsifiers.**
- If at λ = 1 both diameters stay at 5.8 Å, or any of the 12 densities stays more than 20 kg/m³ off, then size cannot reconcile density with this form. Density is then reported with a disclosed empirical translation, and the follow-up owns the form.
- A fit that fails to converge or replay is retained as a numerical failure, not a physical result.

**Compute, without raising program caps.**
- **Allowance:** 1,200 compute-wall s and 15,000 CPU-s.
  - Three start information calls: about 20 s each.
  - Three fits: about 250 s and 3,300 CPU-s each, possibly more with the density rows.
  - Three endpoint information calls: about 20 s each.
- **Ledger before:** 10,638.83 of 21,600 s, and 93,726.34 of 144,000 CPU-s. That adds the whole-command times of the 19.75 s smaller-d_V call and its 0.08 s setup failure, which stopped at the wheel-path check before any calculation.

**Code:** no new lines. Declarations only, and none hide executable code.

**After step 1:** the owner chooses λ, or none. The §3–4 assessment and the §5 comparison family then run at that λ, with the r1 corrections applied:
- the weaker Born hypothesis;
- mixed-outcome rules for cost against pressure;
- the zero-weight no-heat route, with the stage6_rows assertion kept;
- verification compute added to the allowance.

The 250-line request is deferred until the remaining work is known (r1 correction 3).

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
