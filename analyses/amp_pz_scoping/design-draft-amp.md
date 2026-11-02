# Draft experiment: do MEA shared-species parameters transfer to AMP?

Design for [#241](https://github.com/tannerpolley/Amine-Thermodynamics/issues/241),
2 November 2026; parent [#220](https://github.com/tannerpolley/Amine-Thermodynamics/issues/220).
This replaces the superseded preparation statements in the earlier #227/#229
draft. The source notes retain their dated findings. **Proposal for owner
decisions and independent readiness review; no fitting or implementation is
authorized by this document.** No fitted reactive AMP result is reported;
§3 records the reviewer-reported pure-property discrepancy and this source
diagnosis.

## Question, basis and limits

Can the adopted MEA ePC-SAFT formulation describe aqueous AMP pressure and
carbamate speciation while every shared-species quantity stays fixed?
The proposed result is a single-amine transfer assessment, conditional on its
ion representations and source-law slope. It may later seed AMP/PZ work; it
does not qualify an absorber, transport properties, calorics or universal ions.
AMP first, PZ second, blend third remains the proposed order.

Use the MEA hard-chain, dispersion, association, Debye–Hückel and SSM+DS Born
formulation and its density-, temperature- and composition-dependent
permittivity. Freeze H2O, CO2, H3O+, OH−, HCO3−, CO3²−, their shared pairs from the adopted MEA record. Freeze R1–R3 separately
from `analyses/solvent_specification_mea/declarations.toml`,
`chemistry.reactions.aqueous`, including R2's MEA enthalpy shift, reference
identities and temperature domains. Remove zero-stoichiometry MEA entries
when declaring AMP reactions; do not change nonzero stoichiometry. Parameter
owner: `analyses/mea_parameter_bundle/results/selected-current-best-parameters.json`,
SHA-256 `00e77608a8489fc9e03a7d2a86c08cb5ff782bb441368a62fa6390b8bfe9cc91`.
Shared bicarbonate–water interaction and R2 shift contain MEA calibration
information; an AMP failure cannot identify either alone as its cause.

The [chemistry record](chemistry.md) owns the balanced reaction list: nine
liquid species, five independent reactions, vapor H2O/CO2/AMP only. Feed is
one mole analytical AMP, source water and alpha moles CO2; alpha is mol
CO2/mol total analytical AMP. Stock composition is CO2-free. Loaded mass
includes CO2. Use reported temperatures, not rounded nominal isotherm labels.
The primary reactive assessment is 298.15–353.22 K; the actual pressure test
is 303–323 K and NMR is 298.15–318.15 K. The source carbamate slope originates
at 313–373 K: its use below 313 K is an explicit owner-accepted extrapolation,
not experimental confirmation of the slope there.

## Settled owner decisions from #238

1. Fix the Xu/Silkenbäumer hydrolysis slope. On a dimensionless molality
   convention (standard molality 1 mol/kg), the starting law is
   $$L_{h,m}(T)=\ln K_{h,m}=-2546.2/T+11.555.$$
   Fit only an additive natural-log offset delta, starting at zero.
2. Exclude Ciftja 2011 from fitting and scoring. Its balance failures are
   recorded in [the Ciftja assessment](sources/ciftja-2014.md), §3.
3. All 57 usable Ciftja 2014 SI Tables S1–S3 rows calibrate. No NMR
   temperature block is held out.
4. Use one residual per row for carbamate per total analytical AMP,
   $$r_c=\frac{x_{\mathrm{AMPCOO^-}}}
   {x_{\mathrm{AMP}}+x_{\mathrm{AMPH^+}}+x_{\mathrm{AMPCOO^-}}},\qquad
   e_c=(r_{c,calc}-r_{c,obs})/0.003.$$
   Do not fit the complementary amine sum, carbonate sum, pH-derived split
   species or a constant estimated from these same rows as extra observations.

The slope is an apparent source-model slope, not a thermodynamically verified
AMP law. Xu 1992 Eq.7/Table 2 and Silkenbäumer 1998 Table 5 reaction IV are
its origin; Ciftja 2014 Eq.19 supplies corroborating apparent temperature
behavior. The adopted offset will absorb some difference in activity models.

## 1. Carbamate offset bounds

**Recommend delta in [−3.0,+2.0], start 0, scale 1.0.** These are physical
bounds on the additive ln K coordinate, not optimizer defaults.
At 298.15 K the baseline formation constant is about 0.049 kg/mol.
The [common-basis comparison](sources/carbamate-law-sources.md), table in
“Conversion”, gives model-derived formation constants about 0.115
(Mehdizadeh) and 0.32 (Hartono), and the updated Ciftja I→0 apparent value
about 0.76 kg/mol. Since the fitted direction is hydrolysis, their offset
comparisons are ln(0.049/K_formation): approximately −0.85, −1.88 and −2.74.
The excluded 2011 value 0.0075 corresponds to +1.88. The proposed interval
covers these values after rounding outwards; its positive extent is a
stress allowance, not rehabilitation of the excluded 2011 data. It permits
formation constants about 0.0066–0.98 kg/mol at 298 K. Hartono’s fitted
formation constant is a non-binding comparison inside these bounds, not an
imported constant or law.

This is an engineering search interval informed by model spread, not a
confidence interval or a claim of equal source standards. The Ciftja 2014
finite-composition ratios and I→0 extrapolation differ; water activity and
the solute standard state introduce further conversion uncertainty. Ciftja
§2.6 gives ±0.0002 in measured mole fraction. The retained source assessment
propagates this to approximately 0.0025–0.003 in r_c, with larger relative
error near detection. That supports the fixed absolute residual scale, not
narrow statistical bounds on delta. An endpoint on either bound stops
parameter adoption; no automatic widening is allowed.

For the reaction AMPCOO− + H2O ⇌ AMP + HCO3− retain water explicitly:
$$K_h=a_{\mathrm{AMP}}a_{\mathrm{HCO3^-}}/
(a_{\mathrm{AMPCOO^-}}a_w).$$
The source water convention differs by about 0.1 in ln K at 30 mass% in the
source synthesis; treat this as a convention uncertainty absorbed by delta,
not another coordinate. Use the Engine's common infinite-dilution molality
reference for solutes and pure-liquid water. If an intermediate mole-fraction
law is needed, the ideal standard conversion for net solute stoichiometry
+1 is L_h,x=L_h,m+ln(M_w m°), about L_h,m−4.0165. Finite-composition x_w and
activity factors belong in the activities, not a second constant conversion.
Verify this mapping with the Engine reaction reference before any fit.

## 2. AMPCOO− and AMPH+ representations

**Recommend AMPCOO− as one nonassociating sphere in both cation variants.**
A chain with neutral AMP's sites is an alternative hypothesis, not a sourced
AMP ion model. No verified AMP anion PC-SAFT set was found in the retained
source work. The adopted MEA document gives MEACOO− m=1, no association
sites, sigma=4.866108647520244 Å, packing diameter 0.88 sigma,
Debye–Hückel diameter sigma, u/k=207.21694618033155 K, Born diameter 5 Å
and solvation factor 1. These are repository precedent, not measurements of
AMP. The distinction between packing and Debye–Hückel diameters matters.

| AMPCOO− quantity | Proposed treatment and bounds |
|---|---|
| m, charge, association | Fixed 1, −1, no sites or cross-association |
| sigma | Fit [4.5,6.5] Å; start 5.3 Å; scale 0.25 Å |
| Packing / Debye–Hückel diameters | Tied 0.88 sigma / sigma respectively |
| u/k, Born diameter, solvation factor | Fixed to MEACOO−: 207.21694618033155 K, 5 Å, 1 |
| AMPCOO−–water k | Fixed to adopted MEACOO−–water value from the hash-bound document |
| Other new anion dispersion corrections | Fixed zero; shared same-sign exclusion retained |

The size interval brackets the MEA analog and allows a larger effective
sphere for AMP's two extra methyl groups. It is a declared modeling allowance,
not a published AMP radius. Fixing dispersion, Born and water interaction
avoids using 57 small carbamate signals to estimate size, solvation and law
offset independently. This is a conditional transfer hypothesis whose rank
and phase checks can reject it; do not release those fixed quantities to
rescue a fit. No AMPH+–AMPCOO− coordinate is proposed.

Retain the earlier two AMPH+ alternatives so the comparison changes the
cation alone. A: m=1, packing 0.88 sigma, no association, same-sign dispersion
excluded. B: m=3.1552, neutral-style temperature-dependent packing, declared
charged-molecule dispersion including self-dispersion, neutral AMP 2B sites
with zero self-association energy and AMP association volume; cross-association
to water/AMP by the adopted combining rule, none to CO2. Both have
Debye–Hückel diameter sigma and fixed Born diameter 5 Å, solvation factor 1.
Fix u/k to neutral AMP's 237.94 K in both variants to isolate topology/size
rather than another freely fitted energy. Fit sigma in [4.5,6.5] Å for A,
[3.0,4.2] Å for B; starts 5.3 and 3.4676 Å, scale 0.25 Å.

Wangler 2018 §3.1 distinguishes spherical nonassociating inorganic ions from
nonspherical MDEAH+ with cross-association. It is an analog rationale for B,
not an AMP parameter source. MEA's sphere treatment motivates A. Fixing Born
at 5 Å is an explicit reduction of the earlier fourteen-coordinate proposal;
no AMP salt-density or caloric evidence here separates it from other effects.

## 3. Neutral AMP source diagnosis and reproduction gate

**The cause of the pure-pressure mismatch remains unresolved. Do not adopt
this parameter set numerically yet.** The printed candidate is Ayad 2023
Table 5 p.2797 / Pakravesh 2025 SI Table S1 p.2: m=3.1552,
sigma=3.4676 Å, u/k=237.94 K, epsilon_AB/k=3526.15 K,
kappa_AB=0.0058, effective 2B with one site of each type.

### What the source comparison establishes

Pakravesh SI Table S8 p.19 explicitly labels its entries **calculated**
saturation pressures. The AMP PC-SAFT column is 1872.47, 2934.43, 19992.69,
65312.60 and 162508.39 Pa at 347.5, 354.3, 392.3, 423.0 and 452.0 K.
These are source-model numerical comparators, not experimental observations.
Its saturated-density columns belong to MEA; there is no AMP saturated-density
reference in this table.

Pakravesh main Table 2 p.1184 reports AMP PC-SAFT vapor-pressure AAD **1.47%**
(P-rho-T-SAFT-HR: 1.57%). Figure 1 and §3 p.1185 compare vapor pressure
with experiments; the AMP source is ref.78, Klepáčová et al. (2011),
*Vapor Pressures of Several Commercially Used Alkanolamines*, JCED 56,
2242–2248 (bibliography p.1193). SI Table S3 p.4 gives 347–452 K for AMP
vapor pressure. This experimental AAD is distinct from reproducing Table S8.
Ayad §4.5 p.2800 says its AMP parameters were fitted to its measured liquid
densities and literature vapor pressures from ref.66, Belabbaci et al.
(2010), JCT 42, 1158–1162. **Ayad does not report a pure-AMP vapor-pressure
AAD** in its parameter/results discussion or tables: Table 6 p.2797 reports
0.0210% for density only. Neither that density AAD nor Pakravesh's 1.47%
can explain or excuse a 15–39% source-model reproduction error. The two
papers cite different pressure datasets; their references alone do not prove
different implementations.

The independent readiness review of `a805048` reported, on immutable Engine
wheel `3e83e19c`, SHA-256
`0d08dff9be39fb8fc9018119c47612f53d823cd0e456914d7dd44c6941596804`:

| Association-volume candidate | Saturation-pressure error relative to S8 | Ayad Table-2 liquid-density check |
|---|---|---|
| kappa sigma³ | +15.3% to +31.3% | absolute error ≤0.71 kg/m³ |
| kappa d(T)³ | +20.5% to +38.8% | absolute error ≤0.71 kg/m³ |

These are reviewer-reported calculations, reused rather than rerun here.
Both pressure candidates fail the proposed **0.5% per-point numerical
reproduction tolerance**; both satisfy the proposed 1.0 kg/m³ density check.
The latter compares 927.0, 918.6 and 910.1 kg/m³ at 303.15, 313.15 and
323.15 K, 0.1 MPa (Ayad Table 2; expanded density uncertainty
0.5 kg/m³). Density cannot discriminate the two
candidates. This is a numerical reproduction discrepancy, not evidence that
the reactive AMP model has failed a physical validation.

### Conventions checked and the remaining causal gap

Ayad §3.1 p.2794 explicitly uses **2B**, describing one oxygen site and
one hydrogen site for the associating compounds. Pakravesh SI S1 also labels
AMP 2B. AMP contains OH and NH2, but this is an effective two-site model;
counting every chemical donor/acceptor or changing to 3B/4C would change the
published model rather than resolve a unit conversion. Ayad calls kappa the
“effective volume of interaction”; Table 5 and SI S1 give a bare kappa_AB
(no dimensional volume unit), consistent with a dimensionless reduced
association volume. They do not prescribe a conversion to m³/mol. The
separate SAFT-HR block's volume units and powers of ten must not be applied
to the PC-SAFT block.

Engine `3e83e19c`, `engine/docs/equations.md`, `association_strength` uses
$$\Delta^{ij}_{AB}=g^{hs}_{ij}
[\exp(\epsilon^{ij}_{AB}/k_BT)-1]\sigma_{ij}^3\kappa^{ij}_{AB},$$
and `neutral_segment_diameter` uses
$$d(T)=\sigma[1-0.12\exp(-3(u/k_B)/T)].$$
Its `dispersion_helmholtz` and `dispersion_chain_coefficients` use the Gross
2001 chain perturbation and segment-count interpolation. Ayad §3.1 refers
the detailed EOS to refs.58,59,63 rather than printing these expressions;
Pakravesh §2.2 p.1183 gives the hard-chain + dispersion + association
sum and SI S1 cites Ayad for AMP. Neither inspected paper specifies an
alternative segment-number, dispersion or diameter expression that explains
the mismatch. Common PC-SAFT lineage is insufficient to verify identical
implementation. Gross 2002 §2 Eq.3's unlike-volume rule alone does not settle
the pure prefactor. The source-author prefactor and actual implementation
remain unverified; there is no evidence here for an Engine defect, a new
site multiplicity, a dimensional kappa conversion or a parameter correction.
Changing sigma³ to d³ alone demonstrably does not close the discrepancy.

The smallest resolving evidence is an author/reference implementation or a
worked pure-AMP coexistence state with the exact five parameters, site
multiplicities, association strength/contact expression, diameter and
dispersion conventions, both phase densities and equality of pressure and
chemical potential. An author correction to S1/S8 or to the printed parameter
set could also resolve it. Obtain that evidence before assigning a cause.
No neutral fitting, tolerance widening or Engine source edit is proposed.

### Owner choice before numerical preparation

**D3 option A (recommended):** retain Ayad as a source candidate and pause
its numerical adoption while obtaining the resolving source evidence above.
**Option B:** authorize source review of another published pure-AMP parameter
set, with its own equations and numerical references, then amend this design;
no alternative set is selected or imported here. Either route leaves Build
blocked until the source and its numerical reproduction are settled. A change
to the neutral source also requires revisiting cation B's source-derived
m, energy, sites and starts in §2, rather than silently retaining a mixed set.

For any subsequent convention test, **always evaluate both candidates on
all the same five S8 points and three Ayad density points**, independently
of which candidate passes first. The sigma³ candidate keeps kappa=0.0058;
the d³ candidate uses
$$\kappa_{Engine}(T)=0.0058[1-0.12\exp(-3\cdot237.94/T)]^3.$$
Retain pressures, densities, coexistence residuals and signed errors for both.
One passing interpretation plus resolved source provenance supports numerical
adoption; both passing is ambiguous; neither passing retains the source gate.
Keep the 0.5% pressure and 1.0 kg/m³ density proposals unchanged. No constant
conversion is fitted. Obtain independent AMP saturated-liquid densities if
claiming their reproduction; proposed agreement is ≤0.1% relative once the
same conventions/precision are established. None are invented from S8.

## 4. Remaining data roles

These proposals stay in this draft. The merged #240 changes at `35703c2`
are included in this branch; `data-map.md` is unchanged by this correction.
No private CESAR-1 rows or coefficients may be copied or executed.

| Source and locator | Proposed role; admission and reason |
|---|---|
| Hsieh 2007 Tables 2,5 | Preparatory fit of the two MEA-form dielectric coefficients, then freeze; 6 pure and 24 aqueous points, 303.15–328.15 K. Use the fixed-density order, residuals and branch rule below. No claim of loaded-solution permittivity validation. |
| Hamborg 2009 Table 16, Eq.21 | Preparatory weighted correlation of all 24 runs, A/T+B+C ln T, weights 1/u(ln K)^2; then freeze. Printed uncertainties are scales, not established independent standard deviations. Use 293.12–353.22 K only. This is a proposed authorization to estimate the missing unrounded coefficients, not permission to use the ill-conditioned reconstruction of Table 1 as an exact law. Retain covariance and all residuals. |
| Hartono 2013 Table 3, §§2.2,6.1 | AMP–water VLE calibration: all 26 P–T–x–y observations, roughly 333–373 K. Use measured P and y_AMP at reported liquid x and T; do not fit derived activity coefficients as independent observations. This is the Hartono binary campaign indexed in the original map, not an additional 26 rows. |
| Pappa 2006 | Reserve as unloaded VLE comparison, not required calibration. Exact paper/tables and uncertainties remain unread here; do not admit its indexed 21 rows until source checked. Hartono 2013 Fig.2b compares it but is not a replacement for the measurements. Broader high-temperature binary data do not extend reactive-law coverage. |
| Hartono 2021 Table 7 | Loaded-pressure calibration: its own pure-AMP measured **total** pressures, first three columns/isotherms (313,333,353 K), 15+17+15=47 rows, including both 333 K alpha=0.94 measurements. Table 4 owns the 3 M stock conversion. Retain row u(P) and u(alpha), method §§3.2.2–3.2.4. No model-subtracted partial pressure is made. Its 373/393 K columns are supplemental extrapolation only. |
| Hartono 2020 | Comparison/model lineage only in this bounded first design. Do not import its fitted reaction law or coefficients, its mixed-source pressure compilation, or the indexed overlapping 109/82-row files. This avoids unresolved source overlap while the 2021 own measurements supply calibration. |
| Ciftja 2014 SI Tables S1–S3 | All 57 usable loaded rows calibrate r_c at fixed scale 0.003, as settled above. Use the source-reviewed inclusion list, not a new loading-based selection. |
| Kundu 2003 Tables 1–3 p.790 | Primary hold-out: all 51 transcribed rows (7+25+19), 18/25/30 mass% stock, 303/313/323 K, alpha 0.412–0.966, measured pCO2 3.20–94.0 kPa. Freeze every CSV row before fitting. |
| Tong 2012 Table 4 p.43 | Separate total-pressure comparison: 40 loaded rows and 5 zero-loading binary baselines. Report each isotherm, with the rows above Hamborg's range explicitly extrapolations; no pooled reactive pass claim over all five. |
| Yi 2024 Table 4; §2.1.2 | Published-model comparison only. It fitted Kundu and Tong and omitted AMPCOO−. No imported Yi constants or endpoints. |

### Dielectric preparation with fixed density

Propose the existing MEA procedure in
`analyses/mea_parameter_bundle/scripts/fit_campaign.py:276–350`, adapted to
Hsieh's actual temperatures rather than MEA's single 298.15 K isotherm.
First settle §3's pure-AMP gate, then perform the two-coordinate Hartono-2013
binary VLE pre-fit. Freeze its neutral AMP–water endpoint as the **named,
hash-bound density parameter record** for dielectric preparation. At each
of the 30 Hsieh rows evaluate that fixed EOS at the reported T and unloaded
mole fraction, P=101325 Pa, on the mechanically stable liquid branch
(dP/drho>0). Retain molar density in mol/L, mass density, pressure and dP/drho.
Ambiguous/unstable liquid selection stops preparation. No density fit or
loaded-state density enters this step. This fixed EOS is the density source;
Hsieh permittivity is not used to change it.

Keep the adopted water dielectric coefficients fixed. Fit only AMP's two
MEA-form coefficients against all 30 measured permittivities, using
$$e_{\epsilon,i}=(\epsilon_{calc,i}-\epsilon_{obs,i})/
(0.01\epsilon_{obs,i}).$$
The 1% relative scale is a declared residual policy following MEA, not
Hsieh's measured uncertainty. Retain source replicate uncertainties separately,
all residuals, coefficient covariance/conditioning, and native replay at the
same fixed densities. Because Hsieh spans six temperatures, do not apply the
single-temperature quadratic reduction as an exact solution for the full fit.
Use the Hsieh 313.15 K isotherm and its fixed densities for the MEA
quadratic reduction that supplies the two root-derived starts; then evaluate
both on the full multi-temperature objective. Admit only finite real coefficients with
positive dielectric volume and dielectric temperature >393.15 K (the MEA
admissibility rule), and finite permittivity >1 across the declared assessment
states. Select the admissible branch with the lowest **Hsieh-only** cost;
if two distinct admissible coefficient pairs have indistinguishable costs
at retained numerical precision, stop for an owner choice. Two starts
converging to the same coefficient pair count as one branch. No reactive pressure, NMR or Kundu result selects the branch.
If neither is admissible or two coefficients are not independently determined,
return to Design. Retain both branch results, including rejections.

Freeze the selected coefficients before joint fitting. Joint neutral-water
coordinates may subsequently move as declared in §6, but do not rerun this
dielectric fit or silently replace its fixed-density reference. Report that
conditional density assumption with the eventual transfer result. D4 requests
owner approval of this sequence and residual/branch policy; no fit runs here.

Kundu is compromised for independent assessment of Hartono- or Yi-derived
models (Hartono 2020 Table 2; Yi 2024 Table 4; source notes). It can be
independent of **our calibration and model selection**: use only Hartono
2021's own measurements, no Hartono/Yi fitted quantities, the fixed
Xu/Silkenbäumer law, and no Kundu residuals for coordinate/start selection.
Before fitting, compare original source provenance and exact prepared rows
for duplicates or reuse. Shared laboratory history of Hartono and Ciftja
also limits claims about independent calibration groups. If overlap with
Kundu is discovered, stop and redesign the partition before scoring; do not
silently remove inconvenient hold-out rows. Reading the published Kundu rows
for design is not fitting to them.

## 5. Objective and numerical falsifier

Recommend the frozen primary statistic
$$E_p=\frac{100}{51}\sum_{i=1}^{51}
\left|p_{CO2,calc,i}/p_{CO2,obs,i}-1\right|\leq30.0\%.$$
Every one of the 51 Kundu rows must return a finite positive prediction and
meet numerical tolerances; unavailable or unstable states prevent a pass.
Report errors by table and isotherm and signed log ratios as well as E_p.
The 30% limit is an **owner-selectable engineering screening limit**, not
Kundu's uncertainty and not the MEA 24.2% limit. It asks for useful
cross-campaign transfer at about a third relative pressure error. Literature
provides scale, not a universal tolerance: Baygi 2015 reports about 36% on
MEA pressure with ideal speciation and different fitted information; Wangler
2018 §6.2 reports about 19% in one MDEA concentration region after osmotic
calibration, with weaker results elsewhere. Neither establishes AMP accuracy.
A 30% AMP pass remains conditional physical comparison evidence in this
measured region, insufficient for absorber use.

Kundu's ±2% is loading/solubility accuracy, not pCO2 accuracy. Its total
pressure accuracy ±0.2 kPa omits gas-composition uncertainty. Report a
sensitivity envelope at alpha±0.02 alpha without refitting; do not subtract
it from E_p, replace rows by their most favorable value, or call it a
confidence interval. A failure is retained; no fitting or variant choice
may use it. Freeze the selected variant from calibration first, then score
both frozen variants and identify the preselected result. An unselected
passing variant does not rescue the selected one without a new assessment.

For calibration use log-pressure residuals and the fixed NMR residual above.
Recommend pressure scale s_logP=max(u(P)/P,0.05), Hartono 2013 vapor fraction
scale max(0.0001,0.05 y_AMP), and group-normalized objective
$$C=\tfrac12\left[\tfrac{100}{9N_L}\sum_L e_P^2+
\tfrac{1}{N_B}\sum_B e_B^2+\tfrac{1}{57}\sum e_c^2\right].$$
Here L has 47 loaded total pressures; B has 52 scalar binary observations
(26 P and 26 y). Five-percent floors and the 100/9 group preference are
proposed residual policies, not measured uncertainties; the latter follows
#222's pressure emphasis. Report every group separately. Table-7 u(alpha)
is propagated in a post-fit perturbation comparison; the fit holds measured
loading fixed. Pressure/y and within-isotherm correlations preclude a
chi-square interpretation. Owner approval of this policy precedes fitting.
A supplementary chemistry check is RMS(r_c,calc−r_c,obs)≤0.006 on the 57
calibration rows, twice the fixed scale. It prevents pressure success with
missing carbamate; it is calibration agreement, not independent validation.

## 6. Coordinates, starts, ties and identification

Replace the fourteen-free-coordinate proposal with **eight EOS/reaction
coordinates per cation variant**, plus the separate three protonation and
two dielectric preparation coefficients. No joint release of the latter.
Use k(T)=k_ref+s(1/T−1/313.15 K), with s in kelvin.

| Joint coordinate | Physical bounds; start; scale |
|---|---|
| AMP–water k_ref | [−0.5,0.5]; binary pre-fit; 0.05 |
| AMP–water s | [−1000,1000] K; binary pre-fit; 100 K |
| AMPH+–water k_ref | [−0.5,0.5]; 0; 0.05 |
| AMPH+–water s | [−1000,1000] K; 0; 100 K |
| AMPH+–CO2 k | [−0.5,0.5]; 0; 0.05 |
| AMPH+ sigma | A [4.5,6.5] Å, 5.3; B [3.0,4.2] Å, 3.4676; 0.25 Å |
| AMPCOO− sigma | [4.5,6.5] Å; 5.3; 0.25 Å |
| Carbamate delta | [−3,2]; 0; 1 |

The driver assigns an absolute coefficient, not an increment: declare the
carbamate `reaction_coordinate` on `a` with origin equal to the converted
source-law a coefficient, scale 1, and absolute coefficient bounds
[origin−3,origin+2]. Optimizer zero then represents delta=0. Keep the b
coefficient −2546.2 K fixed; do not put [−3,+2] on the absolute a value.

All other new pair corrections are zero except the fixed analog
AMPCOO−–water value above. AMP–CO2 and AMPH+–HCO3− are zero. All shared pairs
remain untouched. Ion energy and Born quantities are fixed as in §2.
Binary-only initialization estimates two AMP–water coordinates first; use a
phase-admissible start, not an unchecked zero-k mixture. Neutral coordinates
remain in the joint objective with binary data so their correlations with
reactive quantities are visible. The second joint start changes the two
ion-water coefficients to +0.1 and +100 K, leaving other starts fixed.
Freeze the binary endpoint and both full starts before joint fitting.

Before fitting run observation-aware `reg.differentiate` at both starts on
calibration only. Retain weighted scaled Jacobian, column norms, singular
values and right vectors. Require eight nonzero independent columns,
s_min/s_max≥1e−4 (condition≤1e4); this is a proposed numerical information
limit, not proof of global identification. Report a calibration-only
diagnostic comparing the AMPH+–CO2 and omitted
AMP–CO2 constant-k columns, both scaled by 0.05 in physical k (the declared
cation-k scale), at each full start for each variant. Use the 47 Hartono-2021
loaded total-pressure rows, with log-pressure residuals, scales and group
weights exactly as in §5. Report the Euclidean norms of these weighted
columns and the ratio norm(AMP–CO2)/norm(AMPH+–CO2) (undefined when
the denominator is zero). This is
raw column-norm sensitivity, not information remaining after projection on
the other columns. It has **no dominance threshold or automatic stop/model
selection consequence**. Retain the eight-column rank gate above; any proposed
coordinate swap requires a new owner-approved Design amendment.
Tied diameters have one
coordinate; do not count packing or Debye–Hückel targets as separate columns.

If the eight-column rank gate fails, stop and return to Design with the
failed matrix. No six-coordinate fallback or automatic anion-size fixing is
specified; any smaller model requires an explicit coordinate list and owner
amendment before another fit.
At endpoints retain active bounds, rank, profiles along weak combinations
and comparison of the two starts. Select the lowest calibration cost among
converged, phase-admissible, identified endpoints; ties within 1% prefer A.
No arbitrary-bound endpoint is adopted. Similar cost but materially different
predictions along unresolved combinations stops promotion; local covariance
is conditional on fixed ion/Born/dielectric/source-law choices.

## 7. Fitting path, numerical checks and dependency

**AMP joint-fitting Build must wait for #235's successful delivered check.**
Preparation of published input tables may proceed separately under approved
source authority. #233's 213-row fixed replay alone does not qualify fitting.
The #235 review comment on 2 November identified two distinct problems:

- Paper wheel `3e83e19c` refuses tied laws with different temperature bounds.
  Engine [#962](https://github.com/tannerpolley/ePC-SAFT/issues/962) is now
  merged through #963 at `e6dae5c7353ae10e0aa2d8e46055847b9d64bbe4`.
  Synthetic Engine checks passed; MEA downstream qualification remains.
- `SolventSpecification.fitted_reactions` currently copies temperature_min,
  temperature_max and standard_state_id from a completed law into every
  destination. #235 must copy fitted coefficients/reference representation,
  preserve destination bounds and reject standard-state disagreement, with
  its two-domain check. Do not repair it again inside AMP.

Use a SHA-256-pinned immutable wheel built from merged Engine main containing
#962. First reproduce #233's 213 rows at 1e−10 relative per field and cost
45.37796168239049, then complete #235's perturbed-start fitting check under
its own limits. Use observation-aware `reg.differentiate` for completed laws;
`reg.evaluate_coordinates` returns empty reaction_laws in the reviewed path.
AMP needs a tied natural-log `a` coefficient coordinate for delta, no new
enthalpy shift. Equal initial AMP temperature bounds would not remove the
need to qualify the common fitting path. No domain narrowing to evade #235.

Engine owns equations, equilibrium, derivatives and parameter fitting.
MEA owns species/feed declarations, source preparation, residual choices,
variant comparison and retained results. Reuse `SolventSpecification`, its
TOML declarations, prepared CSV mappings, native fit report and Engine
`document_mapping` export. #232 already demonstrates fitted-document reload;
the earlier draft's #928 serialization blocker is superseded. Requalify export
on the selected #962 wheel, retaining component order and separate reaction
laws. Do not copy the MDEA runner or add a local optimizer/law updater.

Before joint fitting verify native admission of all nine species, atom and
charge balance, source-law reference conversion and reciprocal reaction
constants, unchanged shared-only water/CO2 results, and one loaded state.
Proposed numerical tolerances: equilibrium residual≤1e−10, replay≤1e−8
relative, derivative comparison≤1e−5 relative with declared absolute scale
near zero. Hamborg correlation residuals must be retained against all 24
printed runs; disagreement beyond their printed scales requires review,
not row removal. Missing caloric references needed by native construction
must be resolved, even though no heat/Cp observation enters this study.

At each endpoint run the driver's declared liquid/vapor tangent-plane trials
on all fitted and scored states, including carbon-free supports at alpha=0.
Retain packing classifier 0.10 and ambiguity interval [0.05,0.35] from
`analyses/solvent_specification_mdea/declarations.toml`; distinguish gas evolution from a second dense liquid. Dense descent,
unresolved searches or unavailable predictions block adoption. A finite
search is not proof of global stability. No fit may proceed through native
refusal or rescue a state by altering shared parameters.

## 8. Code, runtime and retained outputs

**Proposed owner ceiling: 240 gross added executable lines plus 30 test lines**
for AMP preparation/assessment, measured against the accepted implementation
base after #235 merges (design inspected at `0b54cd7`). Planning allocation:
120 source preparation, 80 reuse of driver calls/assessment, 40 reference
checks. TOML/JSON/CSV declarations and the research notebook are counted
separately, not used to hide executable logic. No shared-driver additions
are budgeted; #235 owns that repair. No new solver, dependency or general
solvent framework is proposed. Check additions before exceeding the ceiling.
The present task changes prose only, zero executable lines.

**Estimate: 4–8 hours computation, proposed hard ceiling 8 hours total**,
excluding memory-admission waiting and separate #235 work. Allocate at most
1 hour to source-law/dielectric/binary preparation and sensitivity checks,
4 joint attempts (2 variants × 2 starts) at 75 minutes and 60 iterations each,
and 2 hours to replay, phase trials, hold-out and outputs. Stop on the first
exhausted global or stage budget; keep incomplete results without a pass.
Native controls: function/parameter tolerances 1e−10, gradient 1e−8; a budget
endpoint is not a converged endpoint. Run heavy work as `agent-heavy` in a
background shell, use available cores via the Engine process workers and one
BLAS/OpenMP thread per worker, record hardware and admitted wall time.

Basis: #235 reports 4.6 hours cumulative MEA fitting time; #228's MDEA
280-observation nine-coordinate fitting used a 2100 s native ceiling, 32
workers and one BLAS thread per worker. AMP has 104 reactive observations and
52 binary scalar observations and eight joint coordinates per attempt, but
reactive difficulty/phase-search work does not scale linearly with rows.
These are planning estimates, not an AMP benchmark or a promised duration.
Stop after timing initial differentiation if the projected work cannot fit
the allowance; no unattended enlarged campaign.

Retain public source rows with hashes, units/bases, inclusion decisions,
wheel/commit identity, full starts/bounds/ties, calibration Jacobians, fit
histories, all failures, cold replays, phase trials, endpoint parameter and
reaction documents, and untouched Kundu/Tong comparisons. A later authorized
Analyze/Summarize writes the physical comparisons and limitations in the AMP
research notebook; create no empty notebook now. Independent delivered review
checks those numbers before any parameter adoption. No manuscript change,
caloric/absorber qualification, PZ fitting or blend fitting is included.

## Owner decisions and readiness handoff

The decisions already settled in #238 are not reopened. The following are
recommendations for one owner decision round before numerical Build:

| Decision | Recommendation |
|---|---|
| D1: Offset interval and water convention | [−3,+2], zero start, explicit water and common molality reference (§1) |
| D2: Anion and cation hypotheses | One nonassociating AMPCOO− sphere; fixed analog energy/Born/water interaction, fitted size; retain A/B cations with fixed energies/Born (§2) |
| D3: Pure source and reproduction | A (recommended): obtain author/reference clarification before adopting Ayad; B: authorize review of another published pure-AMP set and amend source-dependent choices. Both convention candidates always tested; retain 0.5% / 1 kg/m³ checks. Cause unresolved (§3) |
| D4: Source preparation and data roles | Estimate Hamborg coefficients from Table 16, fit/freeze Hsieh dielectric after binary pre-fit using its hash-bound fixed liquid-density record, 1% relative scale, admissibility and both-branch Hsieh-only selection; Hartono 2013 binary and 2021 Table-7 first-three-isotherm calibration; reserve Kundu; Pappa/Tong comparisons (§4) |
| D5: Falsifier and residual policy | Kundu 51-row E_p≤30%; no missing rows; 5% pressure floor, group-normalized objective; NMR RMS≤0.006 calibration check (§5) |
| D6: Coordinates and selection | Eight joint coordinates, two fixed starts, calibration-only rank gate 1e4; rank failure stops for Design, no smaller fallback; CO2 column norms reported only, no dominance stop; calibration-first A/B selection (§6) |
| D7: Fitting-path dependency | Wait for delivered #235 qualification on the merged #962 wheel; no duplicate driver repair (§7) |
| D8: Limits and exclusions | 240 executable +30 test lines, 8 h computation ceiling, pressure/speciation only (§8) |

This draft is ready to be **reviewed as a proposal**, not declared Ready for
Build. Independent readiness review is not performed by this implementor;
no subagent or review was authorized in this task. The accountable parent
publishes the accepted design to #241 through its approved issue-change
process and reads it back before Build. No tracker body was changed here.

### Further reading or preparation needed

- Resolve D3’s source-model discrepancy with author/reference evidence or an
  approved alternative source; neither volume candidate currently passes.
  Obtain an independent saturated-liquid-density calculation if that reproduction claim is required.
  The pressure and measured-density checks alone do not establish it.
- Read Hartono 2021 cited uncertainty methods and SI Part A1 before materializing
  its 47-row calibration packet; retain Table 4 stock composition and reported
  u(P)/u(alpha). Verify no reused Kundu observations. Hartono 2020 original
  calibration inventory and Yi 2024 SI are required if importing their fitted
  quantities is later proposed; none are imported here.
- Read Pappa's original measurement tables/uncertainties before admitting that
  supplemental comparison. It is not a prerequisite to the proposed fit.
- Retain the uncertainty of the proposed Hamborg Table-16 correlation and
  verify Engine standard-state mapping, water factors and reference pressure.
  The four-rounded-value reconstruction is not the executable source law.
- Use #240’s merged data map (`35703c2`) when freezing preparation; do not
  count its Hartono 2013 source as a second campaign.

Sources actually inspected in this design: all requested scoping Markdown
records and the retained source tables; main-checkout literature README and
hash-verified Baygi/Uyan/Wangler reading copies (their current Zotero companions
match the indexed hashes); adopted MEA parameter document and density/joint
records; driver source; #235 comments and current #962 closeout; Ayad §3.1,
Table 5 and surrounding parameter discussion, Gross 2002 §2, Hartono 2013
methods/Table 3/results and Hartono 2021 methods/Table 7/model discussion in
current Zotero PDFs. Ciftja 2014 methods/results were checked in its PDF;
exact equation sign and SI transcription verification are inherited from #238.
Xu/Silkenbäumer/Mehdizadeh/Hartono-2020/Yi numerical comparisons here rely on
the cited retained source assessments, not newly claimed full-paper readings.
For this correction, Ayad §3.1, Tables 5/6, §4.5 and ref.66, Pakravesh
§2.2, Table 2, Figure 1/§3 and ref.78, and SI S1/S3/S8/ref.4 were read in
the current Zotero PDFs (keys SSBW7YJ5, TTAMHITN, 467677SZ). PDF SHA-256:
Ayad `6cc9a2780f4bfd6176aae097a49a95dea365263e6033ceaf7c5dac0d371da9c8`;
Pakravesh main `29b1f1e115eecb11cde903aa12d1f9e6a98d2f85499879a5e05b34f429d6e0ea`;
SI `96a0e25ce0b975372b6261a1df36a5f13d3c8c77e2a9fedb43273b1d4f36bc82`.
The main-checkout reading shelf is available; this worktree has no local
literature shelf. Source equations were read at Engine `3e83e19c` from the
read-only clone after fetching main; no source checkout was imported.
Belabbaci/Klepáčová are identified from the papers' references, not claimed
as newly read original measurement papers. No new Engine calculation was
run: the pressure/density ranges are explicitly the independent review's
evidence. No CESAR-1 content, new literature attachment, fit or physical
validation was produced by this correction.
