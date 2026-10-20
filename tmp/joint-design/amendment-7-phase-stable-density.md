# #170 amendment 7: fit density without resolved liquid splits

Design draft, 19 October 2026; implementation base **`cd9b8b41efc41bd86702aaafd963a554d1fd230d`**.
Starting stage: `cse:design`, because the unresolved question is how to retain
the density agreement while excluding the lower-Gibbs liquid splits. **No fit,
parameter adoption, campaign-code edit, notebook edit, manuscript edit or GitHub
write is part of this task.** The owner requested “Record, review, design next”.
The parent owns publication and independent readiness review; the owner chooses
the treatment of unresolved trials and approves the fit bounds before fitting.

**Recommendation:** first map the onset of descent between the A4 control and
the selected A6 vector, then examine coupled coordinate changes near that onset.
Use those numbers to propose a restricted fit, keeping the current density
objective. Do not assert an ion-pair/Born box free of descents: none has been
established. A single lower-density-weight fit is the fallback, as an alternative
use of the fit allowance, with every density and phase limit retained.

Abbreviations: MEA = monoethanolamine; ePC-SAFT = electrolyte perturbed-chain
statistical associating fluid theory; SSM+DS = solvation-shell model with
dielectric saturation; DH = Debye–Hückel; AARD = average absolute relative
deviation; RMSE = root mean square error; Cp = isobaric heat capacity; CPU =
central processing unit. MEAH⁺ is protonated MEA, and carbamate denotes MEACOO⁻.
Loading $\alpha$ is mol CO₂ per mol analytical MEA; solvent mass fractions exclude
CO₂. $s_j$ is the frozen, row-specific density residual scale, in kg/m³.
SHA-256 identifies file bytes. F1 is the existing SSM+DS fit declaration.

Paths are repository-relative: `R` =
`analyses/mea_parameter_bundle/results/joint-recalibration-170/`; `A4` =
`R/amendment-4/`; `A6` = `R/amendment-6/`; `A7` = `R/amendment-7/`.
`P` = `A7/design-probes/`. Script paths are under
`analyses/mea_parameter_bundle/scripts/`.

## 1. Authority, question and retained evidence

**Question.** Within the current Held/larger-branch model, can a joint density,
pressure, species, heat and neutral-mixture fit satisfy every existing fitted-row
gate while admitting **zero resolved-descent points in the unchanged 73-point
phase family**? Any detected descent requires a split-seeded confirmation attempt.
The intended use remains a conditional effective-parameter paper candidate,
primarily 30 mass % MEA. Absorber/stripper qualification, unique ion properties,
new chemistry, charged-chain development and physical validation of liquid–liquid
separation are outside this amendment.

This draft follows amendment 6 **§0b revision 3** and its subsequent owner
decisions, rather than reviving superseded 52-density or 0.5-kg/m³ gates:

| Existing authority | What remains fixed |
|---|---|
| [Source-conflict decision 6278610430](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6278610430) | Exclude only the five Amundsen loading-0.4 rows from objective and density gate; retain them and Han 2012 as assessment evidence. |
| [Joint-fit decision 6278891898](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6278891898) | Fit MEA–water $k$ and reciprocal-temperature slope jointly with all 50 Cai rows; 16 coordinates. |
| [Held and unloaded-gate decision 6279085063](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6279085063) | Held form selected; all five CO₂-free density errors must be within 1.0 kg/m³. |
| [Selected-vector account 6279829306](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6279829306), main `cd9b8b4`, notebook “Amendment 6, revision 3” | Adoption withheld. Fitted metrics and the gas-root check pass; dense-liquid splits block replacement. Supplied delivered review: Supported. |
| [Code-account decision 6278338236](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6278338236), `A4/compute-ledger.json` | Campaign gross additions 1,321 / 1,325; no deletion credit. Disclosed one-off probes remain excluded under [6276283139](https://github.com/tannerpolley/Amine-Thermodynamics/issues/170#issuecomment-6276283139). Wall cap 21,600 s and CPU cap 200,000 CPU-s. |

The selected vector has C149 **24.9231**, pressure/species AARD **12.47/7.15%**,
Vinjarapu RMSE **1.82 kJ/mol**, Cai cost **91.8115**, 47/47 loaded densities
within $2s$ (maximum **1.976$s$**) and maximum CO₂-free error **0.571 kg/m³**.
Its family has **0 passed / 61 unresolved / 12 failed**. Split-seeded solutions
at 333.15 K give $\Delta G/(RT)=-2.1105$ at $\alpha=0.4$ and **−3.2496** at
$\alpha=0.5$, for the stated finite feed. These are model predictions with
numerical verification, without measured phase-separation validation.
Sources: `A6/selected-assessment/summary.json`, `A6/joint-mea-water/summary.json`
and `A6/selected-checks/phase-diagnosis/report.md`.

The same-driver A4 control has **0/73/0**, with **no resolved descent**; tied
joint has **0/59/14**. The paper successor `7b0b4bb5` has **48** descent points
and 16 other unavailable final states. Exact old record `66ff7715` cannot be
constructed on this wheel because it lacks the CO₂–MEA cross-association
declaration. Neither is a phase-qualified fallback. A4 also misses the density
gate by a large margin. Preserve these different failure meanings.

**Closest literature actually read.** The main checkout's ignored shelf was
used because this worktree has no `literature/`. Its index and current Zotero
source bytes agree for all four papers below; keys/hashes are in
`P/source-reading.json`. Root `BANNED.md` is absent; the installed CSE ban list
and terminology reference apply. No new equation transcription is adopted.

| Source and locator | Model, fitted/predicted quantities, domain and assessment relevant here |
|---|---|
| [Baygi & Pahlavanzadeh 2015](https://doi.org/10.1016/j.cherd.2014.07.017), §§2, 3.1–3.3, Table 5, §4 | PC-SAFT with ideal-activity reaction speciation; pure-MEA and binary MEA–water parameters fitted, ternary CO₂ pressures compared without ternary fitting. The reported comparison spans 298–443 K; source-wise pressure deviations and high-loading discrepancies are reported. This differs from the present joint calibration. |
| [Uyan et al. 2015](https://doi.org/10.1016/j.fluid.2015.02.026), §§3, 4.1–4.3, §5 | Reactive ePC-SAFT for MDEA; binary interactions fitted, ion information transferred, ternary pressures assessed over 313–413 K. Low-temperature/concentration and dielectric assumptions limit transfer. It supplies an amine analogy, not MEA stability data. |
| [Held et al. 2008](https://doi.org/10.1016/j.fluid.2008.06.010), §2 between Eqs.2–3, §3, §§4–5 | DH diameter equals ion segment diameter; ion sizes and energies fitted to salt densities and mean ionic activities near 20–30 °C, with vapor pressure and other-temperature comparisons. That formulation omits ion–ion dispersion and Born solvation; it does not prescribe the present unlike-ion $k$ or Born bounds. |
| [Pereira et al. 2012](https://doi.org/10.1016/j.compchemeng.2011.07.009), §§3.1, 3.3.3, 3.4, 4, 6 | SRK/SAFT multiphase-method examples, with repeated-start and known-phase comparisons. A negative tangent-plane result can expose instability; failure to find one with local searches does not prove global stability. Trace components require explicit treatment. This is a method analogy, not a tolerance source or reactive-MEA validation. |

The density/calibration limits and finite-family requirement are repository/owner
decisions. The path and fit ordering below are engineering recommendations.

## 2. Candidate identity and fixed-vector design evidence

| Record | Document / SHA-256 |
|---|---|
| Selected A6 Held, larger, A | `A6/joint-mea-water/held/fit/usable-budget-endpoint.json`; `ceefc95cd051fb291e0c08675c4cb6f159bf10dca0116ef1251ba78c243f79c7` |
| A4 larger control | `A4/matched-larger-dV/control/usable-budget-endpoint.json`; `365758b80c7f701ac7c09c4319d4e216cf5b270374e856381f7d2ba8d1ea7f29` |
| Actual selected fit declaration | `A6/joint-mea-water/held/fit-spec.json`; `f78d0f2ac9461c5de2ffd54813c7350cb8ddd956bb9d0bd649d2666c65c21ccb` |
| Engine | Merged `21e761c318c2ac5b555a245365c844d38a93e4cb`; wheel `d2f61e3a5961b859151fbe0487f4ab633405b11620d9dd64682656a68a110357` |

**New probes, no fitting.** A4 has the tied DH form; it is not silently treated
as Held. First set **all six** A4 DH diameters to their segment diameters, leave
packing at $0.88\sigma$, and supply the missing MEA–water slope as zero. This
defines the Held control $\theta_{0,H}$. Interpolate every identified coefficient
magnitude to the selected vector, retaining units and using the selected
declaration's fixed model choices:

$$
\tag{A7-1}
\theta_H(t)=(1-t)\theta_{0,H}+t\theta_{A6,H},\qquad 0\leq t\leq1.
$$

This is an exploratory input path, not a fitted relationship or a physical
mixture. Both stored coefficients of each changed reaction law move together;
no enthalpy shift is applied a second time. Size, packing and DH ties remain
consistent. Source: the two exact parameter documents and `P/path.py.txt`.
The original tied A4 evidence is reused separately, without recharging it.

| Held path fraction $t$ | Passed / unresolved / failed, all 73 | Descent points | Loaded within $2s$ | Maximum $|e|/s$ | Maximum CO₂-free $|e|$, kg/m³ | Cai cost |
|---|---|---|---|---:|---:|---:|
| 0 | 0 / 73 / 0 | 0 | 0/47 | 53.925 | 1.0888 | 91.3290 |
| 0.125 | 0 / 73 / 0 | 0 | 0/47 | 45.740 | 1.0265 | 91.3525 |
| 0.25 | 0 / 70 / 3 | 70, 71, 72 | 0/47 | 37.917 | 0.9628 | 91.3865 |
| 0.5 | 0 / 69 / 4 | 63, 70, 71, 72 | 0/47 | 23.747 | 0.8326 | 91.4862 |
| 1, retained A6 | 0 / 61 / 12 | 12 points | 47/47 | 1.976 | 0.571 | 91.8115 |

Sources: each `P/path-*/{summary,reduction}.json`, `P/density-cai-summary.json`
and the A6 records. Near the high-loading end, detected descent appears between
the tested $t=0.125$ and 0.25 vectors, well before density passes. This is a
sampled bracket; no monotonicity, continuous stable interval or stable parameter
box has been demonstrated. The family itself has **313.15–333.15 K**, loading
**$10^{-5}$–0.5** and pressure **2412.756–72744.890 Pa**. Do not confuse this
finite domain with the broader reaction/assessment domain.

Split-seeded attempts were made for all **seven** descending path-vector points:
five converge to lower-Gibbs states. At $t=0.25$, point 72 gives
$\Delta G/(RT)=-0.0187565$; at $t=0.5$, point 63 gives **−0.205510** and points
70–72 give **−0.515967 to −0.515893**. Maximum classified residual across these
five solves is below $10^{-10}$; complete states are retained. At $t=0.25$,
point 70 exhausts work and point 71 loses a phase: neither is a converged split
confirmation. Their original finite, conserved descending trials remain, with
$\Delta G/(RT)$ about **−0.0155** versus estimated error about **$5.8\times10^{-8}$**.
They remain rejected/unconfirmed cases, never passes. No global-minimum claim
is made. See `P/split-summary.json` and each `split-seeded-*.json`.

Three reversions on the selected vector were also tested at points **21/63/70**:

| Changed block, all other selected values fixed | Descent points / attempted | Lowest resolved $t_{plane}/(RT)$ at 21 / 63 / 70 |
|---|---:|---|
| MEAH⁺ segment size and both ties restored to Held A4 values | 3/3 | −0.000746 / −0.08919 / −0.06191 |
| All common changed pair coefficients restored to A4 values | 2/3, plus one unavailable final state | unavailable / −0.05101 / −0.04756 |
| Both ion dispersion energies restored to A4 values | 3/3 | −0.01323 / −0.19949 / −0.21614 |

The pair block includes the common MEA–water constant and ion–water terms; the
new neutral slope remains at its selected value. Exact identities are in each
`provenance.json`. These are partial diagnostics, without full-family or
split-seeded qualification of the block reversions. None establishes a single
coordinate repair. In particular, **both original endpoints have unlike-ion
$k=-1$ and both Born diameters 5 Å**. Bounds on those coordinates alone cannot
exclude the selected vector while retaining the control. $k$ here modifies
unlike-ion dispersion; it is not an ion-pair formation equilibrium constant.

All diagnostic commands use the requested pinned interpreter, `nice -n 10`,
`PYTHONPATH=src:analyses/mea_parameter_bundle/scripts` and single-threaded BLAS.
The wheel was verified at its installed main-checkout archive path; no
declaration needed a worktree wheel copy. `P/calls.json` retains every command,
script hash, log, GNU-time record and failure. One density-selection attempt
used an incorrect Cai ID prefix and stopped at an assertion; the original text
is retained, the corrected calculation supplies the table, and both are charged.

## 3. What stays fixed in the fit and assessments

Primary fitting retains the actual selected declaration's **307 positive-weight
rows**: 166 original non-density reacting rows (including four Cp and eight
Vinjarapu targets), 47 loaded densities, five CO₂-free densities, 50 Cai targets
and 39 Kiepe pressures. The reacting-plus-density subset is **218**. Keep every
row identity, observation, source basis, scale, uncertainty treatment and weight.
The source tables' superseded direct-row weights do not override
`fit_campaign.stage6_weights`: the loaded objective uses **$1/47$**, not $1/52$.

$$
\tag{A7-2}
C(\theta;\lambda)=\frac12\sum_{i\notin D}w_i r_i(\theta)^2
 +\frac{\lambda}{2\,47}\sum_{j\in D}
 \left[\frac{\rho_j^{calc}(\theta)-\rho_j^{obs}}{s_j}\right]^2,
 \qquad \lambda=1\ \text{for the primary fit}.
$$

Here $D$ is exactly the retained 15 Amundsen plus 32 Hartono loaded IDs. Other
residual forms/scales come unchanged from the declaration and its native rows.
Five CO₂-free rows keep scale **0.5 kg/m³**, weight **10**; Cai keeps 25 boiling
temperatures and 25 vapor-water fractions, scales **1 K / 0.01**, weight **1**.
Kiepe keeps its 39-row normalization. Frozen $s_j$ values retain the source-local
loading secants and uncertainty caveats; the five excluded Amundsen cells do
not re-enter either the scale construction or the gate.

Retain nominal 30 mass % solvent and Hartono printed loadings, assumed
100000 Pa for Amundsen/Hartono densities, exact analytical zero carbon for
CO₂-free density, and no empirical volume correction. The Cai-only neutral
domain still extends to **436.85 K**; the reacting domain remains
**293.15–393.15 K**. Neither extension enlarges the 73-point phase evidence.

Retain Held DH=$\sigma$ for all six ions, packing=$0.88\sigma$, independent
Born diameters, larger dielectric branch, SSM+DS constants, water and neutral
pure-component parameters, trace-ion parameters, association topology, CO₂–water
binary, zero CO₂–MEA interaction and all unchanged reaction coefficients/ideal
calorics. Keep all **16 coordinate families/scales** and existing physical
bounds until an explicit bound amendment is accepted. No bound widening or
weak-column freezing is inferred. Rebase R2/R5 increments from the serialized
law and retained `chemistry-coordinates.json` to the same total-shift boxes;
never restart an endpoint with zero inherited shifts.

| Unchanged eligibility or reporting rule | Numerical limit / treatment |
|---|---|
| Loaded density | All 47 available and finite; every $|e_j|/s_j\leq2$. |
| CO₂-free density | All five available at exact zero analytical carbon; every $|e|\leq1.0$ kg/m³. |
| Cai | Cost $\leq95.90$ on the same 50 definitions. |
| Common calibration | C149 $\leq35.26$; fitted pressure/species AARD $\leq15.81/9.89\%$. Calibration-improvement claims additionally require the same-wheel paper comparison. |
| Heat | Vinjarapu eight-row RMSE $\leq3.13$ and combined Arcis 14-row RMSE $\leq9.36$ kJ/mol. Arcis is outside the objective and previously accessed. |
| Numerical consistency | Available finite required rows; row/conservation/charge/local-minimum/positive pressure-density derivative checks from A6; cold weighted-row and relative-cost differences $\leq10^{-8}$; all 39 Kiepe residual differences $\leq10^{-8}$. Preserve centered/native derivative decay and roundoff rules. |
| Conditioning, bounds, projected gradient | Report actual values, spectra and stopping reason; no revived rank/condition/gradient adoption gate. Current controls: 180 iterations, function $10^{-6}$, parameter $10^{-10}$, gradient $10^{-8}$. |
| Assessments | Refresh the final candidate's full A6 selected-vector assessment, including all 210 densities, four Hilliard Cp states with enthalpy checks, heats, pressure/transfer/Matin cohorts and corrected ten-row Jakobsen share. Preserve their report-only roles and exclusions. |

Do not repeat the already completed B/smaller-A scope merely because a new fit
starts. Those outcomes remain evidence for their old vectors, not checks of a
new endpoint. A new B/smaller fit or comparison family needs a separate owner
scope/budget decision. One Hartono $x_3$ sensitivity fit follows an otherwise
eligible new primary vector, with frozen scales and no replacement selection.
The old sensitivity is not transferable to changed parameters.

## 4. New phase falsifier and the unresolved-trial decision

Use the entire unchanged `A6/inputs/revision-3/phase/family-points.txt`, SHA-256
**`6e1231d9506fd6dd9e965a64120ff952cebf1c4778da5d66cfb0f888e8b7f44b`**:
feed **9.7292821 mol MEA + 76.9751925 mol water + $\alpha\times9.7292821$ mol CO₂**,
nine-species liquid and neutral CO₂/MEA/water vapor, row tolerance **$10^{-10}$**.
Retain cold → two nearest same-temperature starts → liquid/bubble diagnosis →
two bubble starts, every attempt, and both declared stability supports. A changed
vector always gets its own family, chemistry, reference and bubble pressures.

$$
\tag{A7-3}
N_{descent}(\theta)=\sum_{p=1}^{73}
\mathbf{1}\{\text{any declared trial at point }p\text{ has resolved descent}\}.
\qquad \text{Necessary requirement: }N_{descent}=0.
$$

Use native tangent-plane, donor, finite-split, estimated numerical-error and
`resolved_descent` evidence; do not invent an absolute Gibbs tolerance. A tiny
negative value inside its error estimate is unresolved, not a resolved descent.
For **every descending point**, retain all trials and attempt a native split-seeded
equilibrium solve for each distinct descending liquid composition, reusing its
physical amounts/compositions/packing and the original balances/reference.
Retain split $\Delta G/(RT)$, pressure-density derivatives, positive amounts,
classified residuals and local-minimum evidence. Request liquid/vapor roots
for the trial to distinguish dense-liquid from vapor-like trace-ion behavior.
Any converged lower-Gibbs liquid split fails the candidate. A resolved finite
descent whose split solve fails still prevents acceptance: retain it as a
rejected vector with incomplete confirmation, without calling it stable.
Do not average Gibbs values across points, subtract counts, remove a seed,
change supports or weaken the classifier.

**Owner choice required; none is assumed:**

1. **Strict qualification, recommended.** Retain A6's failed=unresolved=0 gate
   for adoption and wait for an accepted merged-main Engine fix of
   [#660](https://github.com/tannerpolley/ePC-SAFT/issues/660). Fixed-vector
   investigation may continue after design approval; fitting waits for the
   wheel qualification and the numerical bounds decision. Repeat the final
   candidate's complete family on that wheel before claiming a phase pass.
2. **Exploratory fitting pending #660.** Permit a bounded fit with
   $N_{descent}=0$ as a provisional screen, while retaining every unresolved
   trial and explicitly identifying its cause. Only the demonstrated
   trace-ion/near-zero limitation can be attributed to #660; any new unresolved
   cause stops for diagnosis. Such a result is “no resolved descent on 73
   points; stability unresolved”, with adoption and phase-stability claims
   withheld until the complete fixed-wheel rerun passes. This changes fitting
   admission, not the classifier or the physical acceptance gate.

The current wheel's A4 comparison has 72 failed-trial-optimizer points and 46
indeterminate-trial points (overlapping sets); all 73 are unresolved. The selected
vector has a failed near-pure optimizer at every point. This supports an Engine
method limitation on these tested vectors, not a proof that every conceivable
parameter vector must fail. Engine #660 owns its correction; MEA supplies inputs
and consumes evidence. #661's unscaled pre-solve rank test is separately open;
the recorded −0.99 B-start workaround is not a stability remedy. New input
refusals remain numerical failures, without silent parameter nudges.

Keep the independent gas-root falsifier unchanged: **318.15 K,
3699.0803800848512 Pa, $\alpha=0.25557798094241313$**, both density-root requests,
new physical solve, Gibbs/closure comparisons and $10^{-6}$–100 mol/m³ dilution
scan with permittivity →1 and bulk Born →0. A stable ionic gas root fails;
incomplete root evidence is unresolved. The old candidate's gas-root pass
does not transfer to a changed vector or exclude dense-liquid splits.

The new requirement concerns the **retained endpoint and its declared family**.
Existing fitting calls do not test all intermediate parameter vectors for
stability. Requiring every optimizer iterate to be split-free is an additional
Engine fitting-method requirement, addressed by option (d) below.

## 5. Candidate methods, primary recommendation and fallback

| Method | Evidence and feasibility | Disposition |
|---|---|---|
| **(a) Restrict unlike-ion/Born bounds immediately** | A4 and A6 share $k=-1$ and Born diameters 5 Å. Existing −1→−0.8 probe removes descent at 21 but not 70; 5→4.5 Å Born probes leave both. No tested full region free of descents exists. Bounds alone are available through declarations, but their physical usefulness is unknown. | Do not guess a new box or label one stable. Use restrictions only after the coupled study supplies evidence and the owner accepts numerical bounds. |
| **(b) Path plus coupled-coordinate study** | New full-family probes locate detected onset between 0.125 and 0.25; straight-path density remains poor. Single block reversions retain descents. This identifies a specific unanswered question: which off-path combinations improve density without the detected high-loading split? Existing fixed-state and phase producers suffice. | **Primary.** Retain the current objective; spend a bounded diagnostic allowance before committing to fit bounds. |
| **(c) Reduce loaded-density weight** | A4 at zero weight has no detected descent and poor density; A6 at one fits density and splits. Earlier 0.1 fits use different rows/coordinates and have no matching phase qualification, so they do not answer this new 307-row question. The relation between weight and phase behavior need not be monotonic. | **Fallback:** one $\lambda=0.1$ fit with the same 307 rows/scales and original 16-coordinate physical box, starting at the screened Held $t=0.125$ vector with the interior-start treatment below (carbamate 5.798 Å, re-screened). It competes for the single primary-fit allowance, not an additional scan. All density/Cai/calibration/phase gates stay unchanged. |
| **(d) Stability term or constraint inside the objective** | Existing `stage6_rows`/`reg.fit` fits declared property observations; `final_evidence.stability` is a separate post-fit call. There is no declared stability residual/constraint in this campaign. Replacing failed trials by a penalty would hide missing evidence. | Not feasible within four remaining campaign lines. Engine would need a declared finite-split or stability inequality, parameter derivatives through its changing trial/donor solution, explicit treatment of incomplete searches and optimizer constraint handling; MEA would then declare states/scales and retain endpoint confirmation. No Engine equations, local differentiator or penalty wrapper is commissioned here. |

**Primary sequence after owner approval:**

1. **Bracket and explain before fitting.** Reuse the four families above. Run
   $t=0.1875$ over all 73 points, then at most one midpoint of the remaining
   sampled bracket. Treat each measured result separately; do not assume
   stability is monotone along the path.
2. **Resolve coupling near onset.** At $t=0.125$ and 0.25 exchange, in both
   directions, these six complete blocks: MEAH⁺ size with its ties; the two ion
   dispersion energies; changed ion–water pairs with the MEAH⁺ temperature
   slope; neutral MEA–water constant/slope; linked R2 coefficients; linked R5
   coefficients. Evaluate points 63/70/72 (at most 36 point evaluations).
   Preserve both reaction coefficients and total-shift identities. The existing
   selected-to-A4 reversions are not repeated as though new evidence.
3. **Test at most two coupled fixed vectors** suggested by those signed
   changes on all 73 points, with split attempts for detected descents. Score
   at most two no-resolved-descent vectors on the exact 307-row objective and
   density gates. Report achieved density errors, C149, Cai, bounds and phase
   counts together. A failed solve or unexplained unresolved trial is not a
   no-split result.
4. **Return the actual numerical bound proposal to the owner and independent
   readiness review before any fit.** Bound intervals must be inside the
   existing physical boxes, state each changed coordinate and its evidence,
   retain all 16 coordinates, and bind start/rows/ties/scales/wheel. A path
   segment or a few checked vectors do not certify its surrounding rectangle.
   If no useful restriction emerges, stop this method; choose the declared
   fallback or return a measured unresolved feasibility question. This draft
   does not pre-approve unknown bounds.
5. Once bounds and the #660 choice are settled, run **one** released primary
   fit at $\lambda=1$, starting at the proposed no-descent fixed vector, then
   cold replay and immediately evaluate all 73 phase points. Reject a
   descending endpoint before downstream comparisons. If otherwise eligible,
   run the single Hartono loading-basis sensitivity, the full final assessment
   and all numerical verification. A sensitivity-vector descent is reported
   as sensitivity evidence and returned to the owner; it cannot replace the
   primary result.

**Start treatment for the release check (readiness r1 correction).** The
release evaluates centered segment-diameter derivatives at optimizer steps up to
0.01 with scale 0.1 Å, i.e. ±0.001 Å, and Engine `21e761c3` rejects an evaluated
point outside the declared box; A6 already lost 115.72 wall-s this way
(`A6/held-followups/held-x3-at-bound-release-failed/`). Every vector proposed
here has the carbamate segment diameter on its 5.8 Å upper bound: both path
endpoints, $t=0.125$, and every block exchange in step 2, none of which changes
it. Each fit start (primary, fallback and the Hartono sensitivity) is therefore
**declared** as an interior start: any segment diameter within two largest steps
(0.002 Å) of a bound starts that distance inside it (carbamate 5.8 → 5.798 Å),
with its packing (0.88σ) and Debye–Hückel (σ) ties reapplied, exactly as the A6
$x_3$ start (`A6/inputs/held-followups/build.py.txt`, `x3`). The box is
unchanged, the derivative gate is not skipped, and the optimizer may return to
the bound. Because the moved start is a different parameter identity, it gets
its own 73-point phase screen (≈35 s) before release, and its release and fit
proceed only if that screen shows no resolved descent; a descent returns the
start to the owner. This treatment is part of owner decision 5.

The fallback is a measured density/phase trade-off, not permission to relax
density. If the primary fit has already run and failed, this design authorizes
no automatic second fit: return its numbers and unused budget to the owner.
If fallback is selected before the fit slot is used, it replaces step 5's
primary fit and still requires fresh release, replay, phase checks and final
evidence. No extra starts, branch sweep, weight scan or comparison fits follow
from either result.

## 6. Code, compute and ordering

**Campaign code: zero additions proposed.** Keep 1,321 / 1,325. Bounds, starts,
weights and input hashes use existing declarations; property differentiation,
parameter fitting, write-back and replay retain their current owners.
`P/*.py.txt` are disclosed one-off fixed-vector probes, outside campaign imports
and calls. They are not a reusable stability-penalty implementation. Any need
to change a producer or Engine method stops for a separate, quantified owner
decision; the four lines are not assumed enough.

**Current design compute, already charged here:** **189.43 wall-s /
189.12 CPU-s**, within the authorized **300 / 400**. The sum includes every
whole-command GNU-time record and the failed density attempt; overlapping
commands are charged separately. `A4/compute-ledger.json` charges **190 / 190**
after rounding the aggregates up once. Program totals are now **16,380 /
21,600 wall-s** and **127,750.61 / 200,000 CPU-s**, leaving **5,220 wall-s /
72,249.39 CPU-s**. Do not add this charge again at integration.

**Proposed additional allocation, only after owner approval:**

| Work, including failed attempts and cleanup | Wall-s | CPU-s | Basis / stop |
|---|---:|---:|---|
| Accepted merged #660 wheel qualification, if required | 350 | 1,000 | Immutable wheel/hash; replay affected quantities; both A4-control and A6 diagnostic families. New physical descents or changed equations return to Design. No source-checkout runtime. |
| Remaining path/block study and reductions | 400 | 600 | At most four new full families (two bracket, two coupled vectors), 36 point probes and two fixed 307-row evaluations. New allowance, not use of this task's unused diagnostic permission. Stop at aggregate allowance. |
| **One selected-method fit**, release and replay | 1,200 | 7,000 | Typical release ≈180 s, fit 35–400 s / 450–4,200 CPU-s; plan release allowance 300 + native fit 600 + cleanup allowance 120 + replay 180, which also covers the ≈35 s phase screen of the interior start. Primary and fallback are alternatives. |
| One eligible-candidate Hartono $x_3$ sensitivity, release/replay | 1,200 | 7,000 | Same one-fit allowance; skip only if no eligible primary exists, not to qualify a primary incompletely. |
| Protected final evidence/verification reserve | **1,950.38** | **9,200** | Full selected assessment, 73-point family, split confirmations, gas-root check, replays/derivatives and affected-wheel checks. Family measured ≈35 s; gas root ≈5 s; retain margin for failures. |
| **Total reserved** | **5,100.38** | **24,800** | Leaves **119.62 wall-s / 47,449.39 CPU-s** unallocated after this design charge. |

This fits the remainder **as a planning allocation** for one chosen method
and one sensitivity fit. It does **not** conservatively fund an additional
primary-plus-fallback sequence, another start/branch or ten A6 comparison fits.
A third fit's additional 1,200 wall-s would exceed the wall remainder by
1,080.38 s under this table, despite ample CPU budget. Do not raise the wall
cap to accommodate slow fitting. If #660 qualification or mandatory work costs
more, stop before a later launch rather than spending the protected reserve.

Before each launch the operator reads the cumulative ledger, call fields and
remaining stage allocation, and records the arithmetic. Fit admission still
requires `fit_wall_s+120` and `fit_cpu_s=6000`; information calls require their
declared wall and CPU allowance. Set the call/stage budget from the actual
remainder, not an old A6 prior. The CPU check is post-call and teardown joins
are not proven lifetime bounds: the table is not a hard execution guarantee.
Charge incomplete/failed calls and any overrun; an overrun or runner stop
requires return to the owner before another fit.

Use `nice -n 10`, all discovered CPUs in the existing fit process pool, one
numerical-library thread per worker, sequential fits and no subagents. Complete
fixed study → bound decision/readiness → release → one fit → replay/phase
rejection check → sensitivity/final mandatory evidence. No optional comparison
may pre-empt those checks. Waiting for the Engine owner consumes no model
compute allowance.

## 7. Stop rules, retained outputs and owner decisions

**For a fitted candidate, stop or reject when** optimization does not converge,
any density/Cai/calibration/heat/numerical gate fails;
any candidate point has a resolved descent; split confirmation is incomplete;
a stable ionic gas root appears; a required trial/state is unavailable; or
mandatory evidence cannot fit the remaining budget. Keep physical mismatch,
Engine refusal, incomplete optimization and unresolved stability distinct.
No unsupported failure penalty, source-row omission, scale inflation, density
translation, classifier edit or unplanned fit is a remedy under this design.

The boundary/coupling study may end with **no fit-ready restriction**. Its
positive result would be an identified no-descent fixed vector and a tested
proposal for numerical bounds; its negative result is the measured trade-off
over these finite paths, not proof that no ePC-SAFT parameterization can work.
Neither a box nor a completed optimizer certifies global phase stability.
If the owner requires split-free optimizer iterates, stop before fitting and
resolve method (d) with the Engine owner.

Retain future declarations, exact start documents, bound proposals, scales,
wheel/source hashes, every attempted state/trial/split, per-row objective values,
gas-root evidence, GNU-time records and stage charges under `A7/`. Reuse the
single A4 cumulative compute ledger; no separate program total is introduced.
Design probes are exploratory and unpromoted. This task leaves the research
notebook unchanged. After authorized execution, the investigator records the
retained result in the existing notebook, including the density/phase trade-off,
all 73 classifications, unresolved causes, sensitivity, limits and omissions;
render without rerunning the model. Independent delivered review precedes
owner adoption, and exact notebook promotion precedes manuscript use.

**Decisions for the owner, returned through the parent:**

1. Approve the path/coupling-first method and the staged fit decision, or
   choose the single $\lambda=0.1$ fallback. Recommendation: primary, because
   no tested single-coordinate change removes the observed splits.
2. Choose strict qualification waiting for #660, or exploratory fitting with
   unresolved trials retained and adoption withheld. Recommendation: strict;
   do not describe zero detected descent as a completed stability pass.
3. Confirm that the endpoint/family condition is the intended new requirement.
   Requiring every optimization iterate free of splits needs method (d) and
   new Engine work, outside the current code/compute proposal.
4. Accept the 5,100.38-wall-s / 24,800-CPU-s allocation, protected checks and
   absence of automatic additional fits/comparisons; caps remain unchanged.
5. After the bounded fixed study, accept/reject its **actual numerical bounds**
   and the declared interior-start treatment of §5 (re-screened start), and
   obtain independent readiness **Ready** before fitting. No useful bounds
   are claimed by this draft; the owner is not asked to approve invented ones.
6. After complete evidence and delivered review, decide adoption or continued
   withholding. Neither A4 nor the old paper successor is automatically
   qualified as a fallback by this amendment.

**Readiness and delivery limit.** This is a committed Design draft with retained
exploratory numbers, not an independent readiness verdict or fit authority.
Open gates are the owner choices, the numerical bound proposal if the primary
study is chosen, and parent-owned independent readiness/publication. Engine
#660 remains with its orchestrator; no Engine or GitHub write is made here.
All fitting, parameter promotion, mainline integration and remote delivery
remain outside this task.
