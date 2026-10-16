# Amendment 4: determine CO₂–MEA dispersion from neutral physical solubility

Design draft for Amine-Thermodynamics #170, 16 October 2026. Endpoint of this
task: verified source extraction, labelled N₂O-to-CO₂ conversion and a proposed
calibration/comparison. **No fits or Engine evaluation probes were run.**
Production code, reactive target admission and parameter adoption are unchanged.
Independent source/data and design-readiness review belong to the parent
before execution. This draft is not a Ready finding or a published amendment.
No GitHub write was authorized or performed.

## Question, prior evidence and intended use

Can nonreacting physical-solubility evidence determine the CO₂–MEA correction
and its reciprocal-temperature slope separately from ion and chemistry
coordinates, and does fixing that correction improve the reacting objective?

**Owner decision:** use the N₂O analogy in unloaded MEA–water to determine the
neutral interaction before another joint comparison. **Repository policy:**
the scientific plan §3 and §5 qualifies physical neutral interactions before
reactive fitting. This changes the information source; it does not retry the
stopped 16-coordinate reacting fit.

Read the retained evidence on branch `170-a2-part-1-requalify-84ca269d-shared`,
commit `468c6fc`, with results root
`analyses/mea_parameter_bundle/results/joint-recalibration-170/` (E below).
`E/amendment-2/amendment-3/information-results.json` reports complete-system
condition 562848.8359854996, projected CO₂–MEA pair condition
6.298512700977455 and 14-coordinate condition 6390.086918958839. The rank
tests alone did not release fitting; all four amendment-3 fits are unrun.
These are local numerical information results, not a physical rejection of
nonzero CO₂–MEA dispersion. The new neutral fit contains no free ion or
reaction coordinate, removing that particular confounding mechanism by design.

The live #170 body and amendment-3 comment were read on 16 October. The body
SHA-256 was `180a8af370db2096eb1c74955832432528e0c09b45c82e184844272af7dd72f0`.
The accepted amendment-3 definition is comment 6211312555; its stopped result
is comment 6211817527. This document supplies the requested next draft only.

## Sources, data and what the literature establishes

Data owner: `data/reference/MEA/physical_solubility/`. Its `sources.json` owns
source identities, inspected PDF hashes and locators. Its README owns the
conversion equations and uncertainty distinctions; `convert_n2o_henry.py`
reproduces the derived table. Do not create another source table in an analysis.

| Source inspected | Evidence and use | Remaining limit |
|---|---|---|
| Hartono et al. 2014, DOI 10.1021/je401081e, §2.2 p.1809, §3.3/Table 11 p.1813; SI DOI 10.1021/je401081e.s001, Table S2 PDF p.10 | Seven own unloaded 30 mass% N₂O Henry measurements, six distinct T, 298.35–360.25 K. SI provides matching partial pressures and mole fractions. Repeat at 312.65 K remains grouped. Article `5VGPDVGB/L7SKR73P`; SI `MTGKTMAL/582BLNR4`. | Exclude the superscript-10 literature value 4.79, all loaded rows and model correlations. Printed composition uncertainty has ambiguous kg unit. |
| Xu and Wang 2018, DOI 10.1021/acs.jced.8b00070, Eq.1 p.2708, §2.3 pp.2709–2711, §3.3/Table 8 p.2715, §4 p.2716 | Sixteen N₂O Henry measurements in the MEA-only block; x(MEA)=0.0394, 0.0870, 0.1456, 0.2197; 293.15–323.15 K. Eq.1 states the water-ratio analogy and cites Versteeg ref.18. `4TDQZ354/S5PK66RR`. | Density/viscosity reach 333.15 K; the N₂O table does not. BmimBF₄ mixtures are excluded. Water calibration differs from ref.18 by up to 7.2% (§2.3). Table S3 gas pressures were not acquired. |
| Versteeg and van Swaaij 1988, DOI 10.1021/je00051a011, Eqs.1–2 p.29, §2.2/Eqs.4–6/Tables I–II p.30, §2.3 pp.30–31 | Water coefficients and analogy definition verified against PDF `ZKJB9G5U/RBJRWHQZ`. Their HE is c/p; use the inverse for the MEA tables' p/c. | Common measured water span is roughly 291–359.4 K. The 360.25 K Hartono row needs a 0.85 K extension. Eq.6's rounded ratio differs from Eqs.4–5; no quantified MEA analogy uncertainty is supplied. |
| Hartono 2013, DOI 10.1016/j.egypro.2013.06.050 | Bounded acquisition created metadata parent `A8URNIZX`. | PDF missing: Elsevier Article Retrieval authentication failure; Connector returned “Publisher requires a human save”. Handoff is the DOI URL. No source contents or measured rows inferred. |

**Literature practice:** the actual N₂O tables and Xu Eq.1 support an indirect
physical-solubility estimate. They do not supply a CO₂–MEA ePC-SAFT parameter
or establish that the present model can represent these observations.
Baygi 2015 §§3.1–3.3 fits neutral MEA/pair properties then compares reacting
MEA using ideal-activity chemistry; Nasrifar 2010 §§5–7 similarly separates
binary correlations and acid-gas predictions and discusses limitations of
ideal chemistry. Uyan 2015 §§4.1–4.3 fits MDEA neutral binaries, transfers ion
inputs and predicts ternary solubility. These complete relevant passages were
read in hash-matched Zotero Markdown companions. They support binary-first
practice in their formulations; they provide no transferable MEA correction,
no present identifiability threshold and no uncertainty for the N₂O analogy.

The retained table has **23 measured N₂O rows / 22 distinct states**, with
gas-free MEA mass fractions 0.12208545–0.48838927 and T=293.15–360.25 K.
Derived CO₂ H spans 2787.9155–8667.2022 Pa m³ mol⁻¹. Proposed primary rows:
all seven Hartono observations and eight Xu observations at w=0.24418628 and
0.36619575, **15 rows / 14 distinct states**. Xu's remaining eight rows are
concentration-transfer comparisons. The 24–37% primary interval is an explicit
engineering extension of the repository's 25–35% discovery interval. It does
not establish concentration transfer or data coverage above 360.25 K.

**Explicit physical assumption:** the CO₂/N₂O concentration-solubility ratio in
unloaded MEA–water equals the ratio in water. The retained conversion follows
Xu Eq.1 and Versteeg Eqs.4–5 exactly:

$$
H_{CO_2,s}=H_{N_2O,s}\frac{1.17}{3.54}\exp(240/T),\qquad H=p/c.
\tag{A4-1}
$$

The separate inverse of Versteeg Eq.6 is retained as an alternative; it lowers
H by 0.47233468%. Select A4-1 for the proposed fit and disclose that choice.
Do not fit both representations as separate data. Propagated expanded N₂O
uncertainty excludes analogy and water-correlation errors. Neither source is
an untouched independent validation set once used to select this model.

## Neutral model and Engine observation

Keep water, pure MEA, pure CO₂, MEA–water, CO₂–water and the reciprocal
CO₂–water association topology at refreshed stage-2 values. Freeze pure CO₂
dispersion at 169.21 K, as amendment 3 requires. In particular:

- `E/stage2/neutral-mea-water/A/parameters.json`, SHA-256
  `36c827bdb5e8b27997f3bc82439ef22d70f7fe8648526e0aa2ac1b6079e6d237`,
  gives MEA–water k=−0.0843938800264992.
- `E/stage2/co2-water/slope/co2-water/B/parameters.json`, SHA-256
  `b1ec1ddc22abe5ced8d08116fc91a7b3da1361864db1b34c33dda121b642a5e2`,
  gives k(313.15 K)=−0.046416901120577676 and b=−35.66505220645838 K.
- Water is `analyses/mea_parameter_bundle/results/water-124/lambda-0.1-A/parameters.json`,
  SHA-256 `59acacc310a6dbea73b33599e9fdca3a474e4eccf12ccd139c27816cbef75a7f`.

Use the same merged Engine commit `84ca269dfa0c7068417a1c4c326acae276d4d965`,
wheel SHA-256 `98a140a00796782b536c892695b3546547ab5986a4905ae723190aceee38d83a`.
Static inspection compared all 12 installed `epcsaft/` files with that wheel:
all were byte-identical. No Engine source checkout was imported or edited.

`epcsaft.regression.observation` supports pressure, temperature, mole_fraction,
partial_pressure, phase_density, phase_fraction, amount_ratio and equilibrium
isobaric heat capacity. **It has no Henry-constant kind.** Installed
`regression.py` SHA-256 is
`51449736b0789a1386dafec973b92c922064fa0a9dcb53c6d310fb2b00382d8a`.
`equilibrium.Problem` accepts `reactions=()` and explicit phase support;
`equilibrium/problem.py` SHA-256 is
`5b58691077220a6e946021888a8e447ebba5f0aafbe43e2b95b496fe9473ba54`.
The existing `fit_observations.py::stage2_rows` already declares neutral
two-phase problems without reactions. This is interface evidence, not a
successful numerical Henry calculation.

**Proposed MEA-owned source translation:** use native partial_pressure
observations on a dilute neutral bubble state, rather than inventing a Henry
kind or adding a local equation-of-state/fitting implementation. For each
source (T,w), set neutral support in both phases to CO₂, MEA and water; omit
ions and all reactions. Liquid amount is free and incipient vapor amount is
pinned to zero; T is fixed, P is free. Feed mole fractions are
$(\epsilon,(1-\epsilon)x_s,(1-\epsilon)(1-x_s))$, with $x_s$ calculated from
the reported gas-free w. Vapor includes all three neutral species; do not
equate total bubble pressure with CO₂ partial pressure.

Compute and freeze the gas-free solvent molar density $\rho_{s,0}(T,w)$ at
its neutral bubble reference pressure using the fixed stage-2 model. All
changing CO₂–MEA coordinates vanish in this zero-CO₂ reference. Translate H
to the observation target and the returned partial pressure to H by

$$
p^{obs}_{CO_2}=H^{obs}_{CO_2}\rho_{s,0}\epsilon,\qquad
H^{calc}_{CO_2,\epsilon}=\frac{p^{calc}_{CO_2}}{\rho_{s,0}\epsilon}.
\tag{A4-2}
$$

Use `regression.observation` with kind `partial_pressure`, phase `V`,
species `['carbon-dioxide']` and residual form `log_ratio`. The fixed density is a
deterministic units/basis translation conditional on stage 2, not a measured
density target. It makes the log pressure residual the desired log H residual
in the dilute limit. Preserve H and the reference density alongside every
translated target. Do not use SI N₂O pressure/mole-fraction fields as extra
rows, or as direct CO₂ measurements.

**Required preflight before any fit:** demonstrate the A4-2 dilute limit at
$\epsilon=10^{-5},10^{-6},10^{-7}$ on the cold lowest and highest primary
states and both parameter starts. Select the largest epsilon whose H differs
from the next decade by ≤1e-4 relative; if neither adjacent pair passes, stop.
Verify the liquid-density change against $\rho_{s,0}$ is ≤1e-4 relative.
Compare the H reference at the solvent bubble pressure and at 101325 Pa;
if its pressure dependence exceeds 1%, stop for a pressure-specific source
translation, including obtaining Xu Table S3. These limits are engineering
checks that the numerical/basis approximation is small relative to the
proposed 5% residual scale, not published source uncertainties.

Retain raw closure ≤1e-10, liquid/vapor branch identity, positive densities,
normalization and phase support. Check centered derivatives at optimizer
steps 0.01 and 0.005 against native derivatives (relative 1e-5, absolute
1e-8), and repeat serialized cold evaluation. Confirm the two dielectric
branches give the same neutral outputs within 1e-8 weighted residual units;
the neutral fit is shared across branches. Allocate at most **120 CPU-s total**
to these evaluation probes; stop with incomplete preflight when exhausted.
This task used **0 CPU-s of Engine evaluation probes**. If the supported
observables cannot satisfy these checks, the neutral fit is blocked on an
Engine-owned observable; do not patch a local generic Henry fitter or post
an Engine request without the parent's authority.

## Neutral coordinates, objective, starts and falsifier

Use the existing unlike-dispersion correction and reciprocal-temperature form:

$$
u_{ij}=\sqrt{u_i u_j}[1-k_{ij}(T)],\qquad
k_{CO_2,MEA}(T)=k_p+b\left(\frac1T-\frac1{313.15\,{\rm K}}\right). \tag{A4-3}
$$

The dispersion combining rule is literature practice (Baygi §3.2 Eq.11).
The pivot law, boxes and scales are repository/engineering choices inherited
from amendment 3, not literature MEA parameter ranges:
$k_p\in[-0.5,0.5]$ with optimizer scale 0.01; $b\in[-500,500]$ K with scale
10 K. These are the **only two free coordinates**. Starts A=(0,0 K) and
B=(0.10,100 K) are independent and interior. Each begins from the same
fixed neutral parameter document; no reacting endpoint is a neutral start.
No box widening, slope deletion, or extra interaction is authorized.

For source s, let $n_s$ be the number of distinct (T,w) groups (Hartono 6,
Xu 8) and $m_g$ the repeat count within group g. With two sources, use

$$
C_N=\frac12\sum_s\frac1{2n_s}\sum_{g\in s}\frac1{m_g}
\sum_{i\in g}\left[\frac{\ln(H_i^{calc}/H_i^{obs})}{0.05}\right]^2.
\tag{A4-4}
$$

This gives equal source weight and keeps the repeated Hartono state from
doubling that temperature's contribution. The 0.05 log scale is transparent
engineering weighting for this conditional comparison, not an experimental
standard deviation or a quantified analogy uncertainty. Report raw H errors,
each source cost and all eight concentration-transfer rows separately.
Keep the full water-ratio uncertainty as a shared systematic limitation; do
not report 23 statistically independent CO₂ measurements or infer physical
confidence intervals from this objective.

Use native parameter fitting, ≤100 iterations, function and parameter
tolerances 1e-10 and projected-gradient maximum 1e-8. Release only after the
scaled two-column Jacobian is rank 2 at relative singular cutoff 1e-14 and
condition ≤1e4 at the starts and endpoints. Retain both singular values,
unscaled/weighted columns, parameter correlation and the weakest direction.
Require interior endpoints, start-relative-cost agreement ≤1e-6 and maximum
relative H prediction disagreement ≤1e-4 across primary states. Parameter
separation or flat directions despite similar cost prevent unique adoption.
These are numerical identification checks conditional on the residual scale;
they do not quantify source or analogy uncertainty.

**Numerical/physical falsifier (engineering judgment):** stop if no interior,
identified, cold-replayable common pair can attain, on each source, mean
absolute H relative error ≤10% and maximum error ≤20%. These thresholds make
the proposed approximation testable; they are not established literature
validation standards. A failure means this fixed neutral formulation and
these source assumptions do not support the proposed common correction.
It does not disprove the N₂O analogy or reactive thermodynamics. Report source
bias before proposing a different model. A zero or negligible fitted pair is
a legitimate possible outcome, not a reason to add coordinates.

Retain both complete native results, exact primary/transformed rows, source
and wheel hashes, per-row predictions, derivatives, singular values, active
bounds, cold replay, runtime and parameter documents. No selected neutral
value exists yet. The 393 K value of A4-3 remains extrapolation even if a
subsequent reactive comparison includes that temperature.

## Matched reacting comparison

After neutral qualification and independent review, perform **larger-dV
control and neutral-fixed variant first**, then the smaller branch only if
the remaining ledger admits both arms. Each branch is a separate decision;
an unrun or incomplete branch remains inconclusive. A larger-branch result
cannot stand in for the smaller branch.

Both arms release exactly the **same 14 coordinates**, in the same order,
with the same bounds, ties and scales: the first 14 entries of
`E/amendment-2/amendment-3/information-spec.json::information_coordinates`.
They are four ion-pair corrections; MEAH⁺–water slope; two ion segment
diameters with their 0.88 packing/Debye–Hückel ties; two Born diameters; R5
unshifted correlation coordinate; R2 and R5 linked enthalpy shifts; and two
ion dispersion energies. Copy these declarations, including the retained
HCO₃⁻–water upper bound 1.0. No nuisance direction is frozen only in one arm.

- Control fixes CO₂–MEA $(k_p,b)=(0,0)$.
- Variant fixes both values at the shared qualified neutral result. They are
  **not** re-estimated in the reacting objective.

All other fixed quantities, each dielectric branch and its pure/neutral
parameters remain identical. Independently initialize both arms from the
branch's amendment-3 source/seed A record, replacing only the variant's pair:
`route2b/larger-dV/start-parameters.json`, SHA-256
`aee26a2dc1149854ff0840d4bd5bfac58ec423aac1cfec7b870b1ccbbbc2d202`, and
`route2b/smaller-dV/start-parameters.json`, SHA-256
`f9a9d6ea7a46e900721eefbf8eb77a94a21fadfcee89ab44e43774b6ab6a3815`.
Paths here are under `E/amendment-2/`. A neutral-fixed variant and zero control
have different starting predictions by construction, but the same nuisance
starting coordinates. Do not initialize either from another fit's endpoint.

Use identical ordered rows, weights, residuals and input hashes from amendment
3: 47 common pressure + 94 common species + 8 Vinjarapu heat = common 149;
7 restored species + 6 pooled Jakobsen ratios + 39 Kiepe pressure + 4 Hilliard
Cp = **205 positive-weight rows**. The additional 12 loaded-density requests
remain zero-weight assessment, not part of those 205. Neutral-solubility rows
remain outside this reacting objective. CO₂–water stays fixed at stage 2.

With $C=\tfrac12\sum r_w^2$, calculate non-Kiepe $C_{166}$ and common
$C_{149}$ from the same complete evaluated rows. **Inherited amendment-3
decision, per branch:**

$$
C_{166}^{variant}\le0.90 C_{166}^{control},\qquad
C_{149}^{variant}\le1.01 C_{149}^{control}. \tag{A4-5}
$$

Require both converged endpoints and retained numerical checks before this
rule is decided. Repeat the 14-column rank/condition check for each arm;
fixing the neutral pair does not guarantee that either arm passes. Preserve
the amendment-3 derivative, projected-gradient and cold-replay tolerances,
39-row Kiepe invariance ≤1e-8 weighted residual units, and existing loaded
density/Cp/heat assessments. A bound-active but numerically complete control
can serve its matched comparison, with adoption still withheld. Do not
silently discard failed rows or use time-limited vectors as fit endpoints.

## Budget, order and stops

The handoff ledger gives about **9794.489424 active wall-s** and
**92572.391086 CPU-s** remaining. Mandatory-check reserve is
1950.38 wall-s / 17950.44 CPU-s. These are entry figures, not a claim that
this source/design task consumes no time. Before execution the parent must
debit this task's actual or conservatively charged preparation, source work,
checking and commit overhead and refresh both remainders. Unknown overhead
is disclosed; the earlier idle-wall exclusion remains unchanged.

Smallest potentially decisive sequence:

1. Source/data review and ≤120 CPU-s neutral observation preflight; no fit on
   unresolved units, dilution, derivative or pressure basis.
2. Neutral starts A and B only. Proposed native allowance 60 s each,
   crash backstop 180 s from launch, then ≤60 s teardown: **240 s complete
   per neutral fit**, within the overall 1380 s ceiling. If either cannot
   finish, stop and return its actual timing before enlarging it.
3. Larger-dV zero control, then its neutral-fixed variant. Preserve the
   inherited reactive native limit 1200 s, crash backstop 1320 s, own-PID
   teardown ≤60 s: **1380 s complete per fit**. Same controls in both arms.
4. Smaller-dV pair only if neutral and larger-branch evidence leave enough
   allowance. Report a larger-branch decision even if the smaller branch
   must remain unrun. No extra starts, model variants or repeated campaigns.

At full 32-worker capacity, a single 1380 s call reserves 44160 CPU-s.
The inherited admission is before **each** call: remaining CPU must cover
44160 plus the still-required check reserve, and remaining active wall must
cover 1380 plus remaining checks. After reap, measure aggregate process and
worker CPU, retain the 12000 CPU-s post-call stop, and update the ledger.
Use every available core when work permits, with process workers or threaded
linear algebra, not both; begin calculations with `nice -n 10`. Stop only
captured child PIDs and reap them. No live CPU monitor, detached wait loop,
or change to the machine's CPU/memory limits is proposed.

Two full reactive reservations plus checks are
88320+17950.44=**106270.44 CPU-s**, exceeding the entry remainder by
13698.048914 CPU-s. Thus the inherited single-call admission **does not
guarantee completion of a pair**; after the first arm a second may be
inadmissible. Nominal 12000 CPU-s per fit is a post-call stop, not a hard
44160-to-12000 reservation replacement. Two bounded neutral calls plus four
full reactive calls and wall checks cost at most 480+5520+1950.38=7950.38 s
before preparation, leaving 1844.109424 entry wall-s for other work. This
does not prove CPU admission for all four calls.

**Recommended budget choice for the parent:** if guaranteed larger-pair
admission is desired, use equal 900 s native / 1020 s crash / 60 s teardown
limits (1080 s complete) for its two reactive arms. Their worst-case CPU
reservation is 69120; with the check reserve this is 87070.44 CPU-s. It
fits the entry CPU remainder only if all preparation, preflight and neutral
work charge ≤5501.951086 CPU-s. Confirm that condition from measured work
before admitting the pair, and reserve both calls. This is a proposed runtime
amendment, not a silent relaxation of endpoint convergence. If the parent
retains 1380 s calls, keep sequential admission and accept a possible
inconclusive pair. No second-branch completion promise is justified now.

Other hard stops: failed source/data or readiness review; unsupported native
observation; incomplete dilution/pressure/derivative checks; rank loss,
condition >1e4, nonunique or bound-active neutral result; source-error
falsifier; missing rows; loss of fixed binary behavior; failed cold replay;
unreaped child; or insufficient actual ledger allowance. Do not convert any
of these to evidence of thermodynamic impossibility.

## Evidence labels, delivery and open decisions

- **Literature practice:** N₂O physical-solubility measurement, Xu's water-ratio
  analogy, Versteeg's water coefficients, and neutral-first estimation in the
  specifically read MEA/MDEA model papers.
- **Repository policy:** source/data owners, primary locators, stage-2 freeze,
  immutable wheel, native equilibrium/parameter-fitting ownership, grouped
  observations, independent reviews and separate investigator adoption.
- **Engineering judgment:** 24–37% primary interval, Eqs.4–5 rather than Eq.6,
  slight 360.25 K water extension, two-parameter law and bounds, residual
  scale, neutral error limits and proposed runtime allocation.
- **Current evidence:** source extraction and arithmetic conversion verified
  against PDF tables/equations; static Engine capability inspection. No
  parameter calibration, neutral numerical solution verification, prediction
  assessment, physical validation or parameter promotion is claimed.
- **After future execution:** record numbers and exact rows in the existing
  `analyses/mea_parameter_bundle/notebook.qmd`, then obtain independent
  delivered review. Do not update manuscript numbers from this draft or
  promote a calibration to global physical validation.

Open decisions with recommended answers: (1) keep Hartono 2013 as a missing
PDF gap without blocking already verified tables; (2) accept the 24–37%
bracketing rows as conditional calibration candidates, keeping the strict
25–35% inventory counts intact; (3) use the printed Eqs.4–5 water ratio and
retain Eq.6 as a 0.47% alternative; (4) permit the labelled 0.85 K extension
for the highest Hartono row while withholding 360–393 K qualification;
(5) require successful native-observation preflight before any fit;
(6) choose the equal 1080 s reactive caps if the measured ≤5501.951086 CPU-s
condition holds and guaranteed larger-pair admission matters. The parent
resolves these in the reviewed amendment; the owner was not asked to wait.
