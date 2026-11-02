# Draft experiment: do MEA shared-species parameters transfer to AMP?

Design for [#241](https://github.com/tannerpolley/Amine-Thermodynamics/issues/241),
2 November 2026; parent [#220](https://github.com/tannerpolley/Amine-Thermodynamics/issues/220).
This replaces the superseded preparation statements in the earlier #227/#229
draft. The source notes retain their dated findings. **Proposal for owner
decisions and independent readiness review; no fitting or implementation is
authorized by this document.** No fitted reactive AMP result is reported;
§3 records the measured-data pre-fit design and the published-set comparison.

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
excluded. B: m fixed to the accepted §3 neutral endpoint, neutral-style temperature-dependent packing, declared
charged-molecule dispersion including self-dispersion, neutral AMP 2B sites
with zero self-association energy and AMP association volume; cross-association
to water/AMP by the adopted combining rule, none to CO2. Both have
Debye–Hückel diameter sigma and fixed Born diameter 5 Å, solvation factor 1.
Fix u/k to the accepted neutral AMP endpoint in both variants to isolate topology/size
rather than another freely fitted energy. Fit sigma in [4.5,6.5] Å for A,
[3.0,4.2] Å for B; starts 5.3 Å and the refitted neutral sigma respectively, scale 0.25 Å.
Before freezing the reactive declarations, require the refitted B start to lie
strictly inside its proposed [3.0,4.2] Å interval; otherwise return its bounds
to the owner. B inherits the refitted m, u/k and kappa, with unchanged 2B
site counts and zero cation self-association energy. Recompute all
neutral-dependent cross-association strengths, cation starts and initial
Jacobian/phase checks from one hash-bound neutral record. A keeps m=1,
its nonassociating topology and 5.3 Å start, but uses the same refitted u/k.
Do not mix Ayad m/energy/volume with a newly fitted neutral sigma.
These are proposed updates to D2, not additional ion coordinates.

Wangler 2018 §3.1 distinguishes spherical nonassociating inorganic ions from
nonspherical MDEAH+ with cross-association. It is an analog rationale for B,
not an AMP parameter source. MEA's sphere treatment motivates A. Fixing Born
at 5 Å is an explicit reduction of the earlier fourteen-coordinate proposal;
no AMP salt-density or caloric evidence here separates it from other effects.

## 3. Pure-AMP preparation fit

**D3 decided by the owner on 2 November 2026:** estimate neutral AMP's five
PC-SAFT parameters in this repository from measured vapor pressures and
liquid densities before the binary pre-fit. This supersedes the requirement
to reproduce the published parameter set before proceeding. The cause of its
Engine/source-model discrepancy remains unknown; a fit is not its diagnosis.
Use effective 2B (one site of each type), as Ayad §3.1 p.2794 and
Pakravesh SI Table S1 prescribe, with the Engine's dimensionless kappa
multiplying sigma³, not a fitted conversion to d(T)³. Freeze the accepted
neutral endpoint before any binary, dielectric or reactive fitting. Use immutable Engine wheel
`e6dae5c7`, SHA-256
`83ede7d2722d3581603f6e4139c614b8bbfc903ce90609c90b802d46eea77dd6`,
from `/home/tnnrpolley21/Workspaces/Engineering/ePC-SAFT/build/wheels/main-e6dae5c7/`;
no source-checkout imports. This design made no Engine calculation.

### Observations and independent comparisons

All three original pressure PDFs were acquired legitimately through Zotero
Connector into the registered project collection `8RZP275E`. Searches by
Pappa name and DOI found no matching live item before acquisition; it was
added, not merely rediscovered. No source is awaiting a PDF handoff.

| Original source; Zotero parent / PDF | Read measurement evidence and proposed use |
|---|---|
| Klepáčová 2011, DOI 10.1021/je101259r; `W3CN3ITJ` / `AC6FKJD6` | Calibrate all 15 measured Table 10 rows, p.2246: 347.5–452.0 K, 1.94–160.0 kPa. Experimental section p.2242: modified Swietoslawski circulation ebulliometer; T precision 0.1 K, pressure precision 0.5% for 1<P<50 kPa and 0.2% for 50<P<400 kPa. AMP 99% purity, used without further purification (Table 1/p.2243). Table 11's 53 points combine this and literature; they are not 53 new measurements. |
| Belabbaci 2010, DOI 10.1016/j.jct.2010.04.015; `HVW2Q8XJ` / `3MWGVBQX` | Calibrate all 9 pure-AMP Table 2 measurements, p.1159: 293.29–373.00 K, 41.5–8141.8 Pa. Pure static apparatus, MKS differential manometer; §2 pp.1158–1159: sigma(T)=0.02 K, sigma(P)/P=3% below 600 Pa, 1% at 600–1300 Pa, 3% above 1300 Pa. Purity >99 mass%, tested by gas-liquid chromatography. Its abstract's 283–363 K interval does not replace Table 2's pure-AMP range. Table 3 x_AMP=1 endpoints use the second, mixture apparatus; keep as a separate apparatus comparison, not duplicate calibration rows. |
| Pappa 2006, DOI 10.1016/j.fluid.2006.03.014; `4PIGUS3I` / `EKY3MCAB` | Hold back all 23 pure-AMP Table 1 rows, p.194: 373.25–436.85 K, 8.0–101.3 kPa. §2.2: modified Swietoslawski ebulliometer; pressure controlled within ±0.13 kPa, temperature accuracy ±0.1 K. §2.1: 99% AMP, dried over 4A molecular sieves ≥1 week. §2.3.1's prose says 373.3–463.9 K, contradicting its table; use actual table rows, not the prose endpoint. Normal boiling point measured 436.9 K. These are not its 21 interior binary VLE rows (Table 2 p.195). No Pappa Antoine coefficients enter the pure fit or starts. |
| Ayad 2023, DOI 10.1021/acs.jced.2c00767; existing `PX8NU8BD` / `SSBW7YJ5` | Calibrate its three Table 2 experimental liquid densities, p.2790: 927.0, 918.6, 910.1 kg/m³ at 303.15, 313.15, 323.15 K and 0.1 MPa. §2.2 p.2792: vibrating U-tube DSA 5000 M, density uncertainty 0.0005 g/cm³; table footnote p.2792 gives expanded uncertainty 0.5 kg/m³ at 95% confidence, u(T)=0.02 K and u(p)=0.04 MPa. Do not treat expanded uncertainty as a standard deviation. Table 1 p.2789 reports only 0.95 AMP mass purity, without further purification (§2.1), an additional systematic limitation. |

Other reported pure-density measurements are visible in **Ayad Table 2's
literature columns**: e.g. at 303.15 K 925.7 (Zhang 2002, ref.3), 928.39
(Álvarez 2010, ref.1), 926.6 kg/m³ (Balchandani 2019, ref.4); at 313.15 K
917.2 (Aguila-Hernández 2001, ref.6), 919.65 (Henni 2003, ref.7),
921.1 (Xu 1991, ref.10), 919.945 (Rebolledo-Libreros 2006, ref.11),
919.6 kg/m³ (Li–Lie 1994, ref.12). At 323.15 K its reported literature
values span 909.2–913.4 kg/m³. These are verified as Ayad's cited values,
not newly read original datasets: their uncertainty, purity, phase status and
full temperature intervals remain unverified. Do not pool them as extra
observations or call them independent density validation. Their several
kg/m³ spread is a reason to retain source-specific bias, not to claim Ayad's
0.5 kg/m³ uncertainty describes all literature.

### What the original pressure tables show

Hartono 2013 Eq.2 p.152 (`5KUR8PRH` / `SEPZQIPE`) prints
$$\ln(p/{\rm kPa})=15.8097-3986.86067/(t+189.9303).$$
The following line calls t kelvin, but the printed coefficients require
**t=T/K−273.15 in degrees Celsius**. Direct arithmetic gives 97.2127 kPa
at 165 °C, versus 12861.7 kPa if 438.15 is inserted directly. Pappa's
measured 101.3 kPa at 436.85 K independently supports this reading. Treat it
as an inferred correction of a unit typo, not a confirmed author corrigendum.
Hartono reports 20–165 °C validity and 3.5% average absolute relative deviation
against Pappa/Belabbaci/Klepáčová; it is a fitted synthesis, not independent
pressure data. No equality with atmospheric pressure is imposed at 165 °C.

Arithmetic from all original table rows, signed as 100(p_obs/p_Hartono−1):
Belabbaci −2.59% to +4.66% (mean absolute 2.92%, 9 rows);
Klepáčová −5.94% to +10.33% (7.37%, 15 rows, including three temperatures
above Hartono's 438.15 K range); Pappa +1.62% to +8.60% (6.95%, 23 rows,
all inside the stated range). These recalculated campaign errors do **not**
independently reproduce Hartono's aggregate 3.5%; its exact fitting inventory
and weighting remain unresolved. Do not use 3.5% as a measurement uncertainty.

Because temperatures differ, direct same-temperature measurement differences
are unavailable. Log-linear interpolation between adjacent original Belabbaci
Table 2 rows gives Klepáčová differences −8.59%, −5.65%, −3.37%, −1.09% at
347.5, 354.3, 363.6, 371.4 K. Belabbaci's published Antoine interpolation
(Table 1, Eq.1, p.1159) gives −9.16%, −6.09%, −3.59%, −1.52% respectively.
Thus approximately 10% disagreement is supported near the low end of their
overlap, conditional on interpolation, not universal across all temperatures.
Against log-interpolated Pappa Table 1, Klepáčová is +1.96%, +2.89%, +2.47%,
+1.84%, +1.04% at 377.2, 392.3, 402.1, 423.0, 436.2 K. Pappa and Klepáčová
agree much more closely there. Uncertainty in temperature, sample water and
interpolation must remain distinct from EOS error; no source is discarded.

S8's five calculated pressures are −9.22%, −2.55%, +8.85%, +10.86%, +9.63%
relative to this same Hartono reading; 452 K is outside its domain.
The owner's hand comparison gives Engine sigma³ errors +10.0%, +12.4%,
+26.3%, +36.5%, +43.9% at the same five temperatures. Those Engine values
are attributed to the owner/reviewer, not independently rerun here. The
original tables confirm a source spread, but not that it explains the entire
Engine discrepancy. The present calculations use only source-equation
arithmetic in isolated Python (`-I`), not Engine calls or a fit.

Source SHA-256 (full PDFs, checked after acquisition):
Klepáčová `696c2dac68f1d0f6ab95d1b7872c1eb6e93c562594ba1163c450c89b3495e9aa`;
Belabbaci `27be136ec45c638b6330d1084d9e19695a2e727f5ba02909fa9ae5b2bfb6140e`;
Pappa `b185d1f53476b994a9dcf263ed31fee888d078021a2b04215a302b3a750860b9`.
Methods, tables, results and limitations above were read in these PDFs;
Hartono Eq.2 and the three pressure tables were also visually checked.

Do not use either Hartono's or Klepáčová's fitted Antoine pressures as
additional observations. The original measurements own the pressure evidence.
Temperature and pressure errors are correlated within each campaign; the
residual scales below are engineering weights, not independent statistical
standard deviations. The near-ambient tables label observations as liquid without establishing
solid–liquid equilibrium. Retain that limitation; do not
claim a solid-phase model or global liquid stability from them.

### Coordinates, bounds and starts (proposal)

| Coordinate | Start (Ayad Table 5 p.2797) | Proposed bounds | Coordinate scale |
|---|---:|---:|---:|
| m | 3.1552 | [1.5,5.0] | 0.5 |
| sigma / Å | 3.4676 | [2.8,4.2] | 0.25 Å |
| u/k / K | 237.94 | [150,400] | 50 K |
| epsilon_AB/k / K | 3526.15 | [1500,5500] | 500 K |
| kappa_AB | 0.0058 | [0.0005,0.05] | fit ln(kappa/0.0058), scale 1 |

These bounds are proposed search allowances around Ayad, not molecular
confidence intervals. All five remain fitted; no parameter is silently fixed
to make the information check pass. A second declared start is
(3.0, 3.55 Å, 250 K, 3200 K, 0.008), to test dependence on initialization.
No reactive or Kundu/Tong evidence selects a neutral start or endpoint.
Select the lowest-cost admissible neutral endpoint using calibration alone;
if the profile rule below finds practically equivalent, materially different
endpoints, stop before scoring Pappa rather than use it for selection.

For each pressure observation solve pure coexistence with equality of
pressure and chemical potential and distinct mechanically stable vapor and
liquid roots. For density solve the liquid at its reported T and pressure,
not at saturation. Use molar mass 89.14 g/mol (Ayad Table 1), recording any
source rounding in conversion to kg/m³. Proposed residuals are
$$e_{p,i}=\ln(p_{sat,calc,i}/p_{obs,i})/s_{p,i},\qquad
 e_{rho,j}=(rho_{calc,j}-rho_{obs,j})/(0.5\ {\rm kg\,m^{-3}}).$$
Propose s_p=max(0.02,u_p/p_obs,|d ln p_sat/dT|u_T) where a source reports
uncertainty; retain reported precision separately when it is not a standard
uncertainty. The 2% floor limits weighting of precise but mutually displaced
campaigns. Minimize the sum of each pressure campaign's mean squared residual
plus the density campaign's mean squared residual. Thus many pressure rows
do not automatically suppress three density rows. Publish every unscaled
relative pressure error, density error and campaign contribution.

### Information, acceptance and stop rules (proposal)

Pressure plus a narrow density interval weakly determines five associating
PC-SAFT parameters. Inspect the weighted, coordinate-scaled Jacobian at both
starts and endpoints; retain all singular values and weak right-singular
vectors. A full-rank matrix alone does not establish useful identification.
Before adoption, profile the weakest endpoint singular-vector combination at
five scaled displacements (−1,−0.5,0,+0.5,+1), reoptimizing the remaining
four combinations within the same bounds. Record cost, active bounds,
pressure curves over the measured range and densities at 303.15–323.15 K.
Stop if profiles cannot be completed within D8, if a weak direction reaches
arbitrary bounds without a cost increase of 1 in this declared objective,
or if endpoints differing by less than 1 cost unit differ by >5% pressure
or >1 kg/m³ density within the measured domain. These are proposed practical
identification criteria, not likelihood confidence intervals. Fixing a
parameter (for example m) is an alternative requiring an owner decision and
new design; it is not an automatic fallback.

These pressure limits are engineering screening proposals reflecting the
observed campaign spread, not source precision or a confidence interval.
The 1 kg/m³ density allowance is twice Ayad's expanded uncertainty and
does not account for its unspecified impurities. Propose calibration checks: each admitted pressure campaign mean absolute
relative error ≤5%, no row >10%; all three Ayad density errors ≤1 kg/m³.
Apply the same pressure limits to any whole held-back pressure campaign
identified above, only after freezing the endpoint. Report its full row count
and failures. Passing that comparison supports pure-AMP physical assessment
over its measured range, not an independent reactive validation. If no whole
campaign is available, report no independent pure-pressure validation and
return that absence to the owner before adoption. There is no independent
density validation until another original source is admitted.

Stop on nonfinite predictions, merged roots, failed coexistence or negative
compressibility, failed numerical tolerances in §6, endpoint at an arbitrary
bound, failed profile/acceptance checks, or an exhausted stage/global budget.
Retain failed rows; never remove them, widen bounds, add sites, fix a coordinate
or refit on held-back observations without a design amendment. The same
approved wheel must cold-replay the endpoint before it is frozen by hash.

### Published-set comparison retained without an adoption gate

Ayad Table 5 / Pakravesh SI S1's original set is the start above. Pakravesh
SI Table S8 p.19 contains **calculated**, not measured, AMP PC-SAFT pressures:
1872.47, 2934.43, 19992.69, 65312.60, 162508.39 Pa at 347.5, 354.3,
392.3, 423.0, 452.0 K. The earlier independent review on wheel `3e83e19c`
reported +15.3–31.3% errors with kappa sigma³ and +20.5–38.8% with
kappa d(T)³; both density comparisons were within 0.71 kg/m³ of Ayad.
These are inherited reviewer results, not rerun on the newly specified wheel.
Keep both signed source-model comparisons, parameter identity and numerical
residuals when replaying them; neither 0.5% S8 reproduction nor an inferred
association-volume conversion is a gate on the owner-authorized measured-data
fit. Pakravesh Table 2 p.1184 reports 1.47% pressure AAD against Klepáčová;
Ayad Table 6 p.2797 reports 0.0210% density AAD, with no pure-pressure AAD.
Neither supplies new experimental rows or resolves the implementation cause.

## 4. Remaining data roles

These proposals stay in this draft. The merged #240 changes at `35703c2`
are included in this branch; `data-map.md` is unchanged by this correction.
No private CESAR-1 rows or coefficients may be copied or executed.

| Source and locator | Proposed role; admission and reason |
|---|---|
| Hsieh 2007 Tables 2,5 | Preparatory fit of the two MEA-form dielectric coefficients, then freeze; 6 pure and 24 aqueous points, 303.15–328.15 K. Use the fixed-density order, residuals and branch rule below. No claim of loaded-solution permittivity validation. |
| Hamborg 2009 Table 16, Eq.21 | Preparatory weighted correlation of all 24 runs, A/T+B+C ln T, weights 1/u(ln K)^2; then freeze. Printed uncertainties are scales, not established independent standard deviations. Use 293.12–353.22 K only. This is a proposed authorization to estimate the missing unrounded coefficients, not permission to use the ill-conditioned reconstruction of Table 1 as an exact law. Retain covariance and all residuals. |
| Hartono 2013 Table 3, §§2.2,6.1 | AMP–water VLE calibration: all 26 P–T–x–y observations, roughly 333–373 K. Use measured P and y_AMP at reported liquid x and T; do not fit derived activity coefficients as independent observations. This is the Hartono binary campaign indexed in the original map, not an additional 26 rows. |
| Pappa 2006 | All 23 pure pressures reserved for §3 assessment. Its 21 interior binary VLE rows, Table 2 p.195, are supplemental binary comparisons; exclude the six pure endpoints from that count. Methods now read (§3); do not import fitted NRTL/UNIQUAC coefficients. No extension of reactive-law coverage. |
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
First fit, assess and freeze §3's neutral AMP endpoint, then perform the two-coordinate Hartono-2013
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

**D8 revised proposal, not an approved ceiling: 360 gross added executable
lines plus 40 numerical-check lines** for AMP preparation/assessment, measured
against the accepted implementation base after #235 merges. Allocation:
120 source preparation, 100 pure-property calls/residuals/profiles, 100 reused
binary/reactive driver calls and reporting, 40 reference checks. This adds
120 executable and 10 check lines to the previous proposal to include the
pure fit and its information checks. Data declarations and notebook prose
are counted separately; executable logic may not be hidden in declarations.
No generic optimizer, equilibrium solver, new dependency or solvent framework
is included; reuse Engine fitting and property calls. If the approved Engine
cannot represent the pure objective or profiles, stop for its owner rather
than write a local optimizer. This task changes prose only.

**Proposed computation ceiling: 12 hours**, excluding memory-admission waiting
and separate #235 work; estimate 8–12 hours, not an AMP benchmark. Allocate
4 hours pure preparation (two fits, at most 45 min/60 iterations each;
five profile points at most 20 min each; 50 min differentiation/replay),
1 hour binary/source-law/dielectric preparation, 5 hours for four reactive
attempts (two variants × two starts, 75 min/60 iterations each), and 2 hours
phase checks, held-back assessment and retained outputs. Both stage and global
limits stop work; incomplete profiles or budget endpoints cannot pass.
Native controls: function/parameter tolerances 1e−10, gradient 1e−8. Run heavy
work through `agent-heavy` in a background shell. Use full available CPU count
for process workers with one BLAS/OpenMP thread per worker, sized to memory;
record hardware and admitted elapsed time.

Basis: the inherited proposal cites #235's 4.6-hour cumulative MEA fitting
and #228's 280-observation, nine-coordinate MDEA fit with a 2100 s native
ceiling. Those reactive timings justify retaining its 8-hour allowance,
not the new pure-fit duration. The extra 4 hours is explicit arithmetic
for two five-coordinate fits plus five conditional profile solves and
checks. No pure-fit timing was measured in this design. Time the first
residual/Jacobian evaluation and project all remaining solves before starting
the campaign; return to the owner if the declared budget is insufficient.
No automatic ceiling increase or skipped identifiability check.

Retain public source rows with hashes, units/bases, inclusion decisions,
wheel/commit identity, full starts/bounds/ties, calibration Jacobians, fit
histories, all failures, cold replays, phase trials, endpoint parameter and
reaction documents, and untouched Kundu/Tong comparisons. A later authorized
Analyze/Summarize writes the physical comparisons and limitations in the AMP
research notebook; create no empty notebook now. Independent delivered review
checks those numbers before any parameter adoption. No manuscript change,
caloric/absorber qualification, PZ fitting or blend fitting is included.

## Owner decisions and readiness handoff

The decisions already settled in #238 are not reopened. D1, D3, D5 and D7
are decided by the owner in the two 2026-11-02 comments on #241. D2, D4, D6,
D8 and §3 detailed fitting/identification choices remain proposals before Build:

| Decision and status | Content |
|---|---|
| D1 — decided 2026-11-02: Offset interval and water convention | [−3,+2], zero start, explicit water and common molality reference (§1) |
| D2: Anion and cation hypotheses | One nonassociating AMPCOO− sphere; fixed analog energy/Born/water interaction, fitted size; retain A/B cations with fixed energies/Born (§2) |
| D3 — decided 2026-11-02: Pure preparation | Fit m, sigma, u/k, epsilon_AB/k and kappa in this repository, effective 2B, Ayad start, Engine sigma³; freeze before binary preparation (§3). Detailed observation partition, bounds, scales, profiles and acceptance are proposals pending owner approval. |
| D4: Source preparation and data roles | Estimate Hamborg coefficients from Table 16, fit/freeze Hsieh dielectric after binary pre-fit using its hash-bound fixed liquid-density record, 1% relative scale, admissibility and both-branch Hsieh-only selection; Hartono 2013 binary and 2021 Table-7 first-three-isotherm calibration; reserve Kundu; Pappa/Tong comparisons (§4) |
| D5 — decided 2026-11-02: Falsifier and residual policy | Kundu 51-row E_p≤30%; no missing rows; 5% pressure floor, group-normalized objective; NMR RMS≤0.006 calibration check (§5) |
| D6: Coordinates and selection | Eight joint coordinates, two fixed starts, calibration-only rank gate 1e4; rank failure stops for Design, no smaller fallback; CO2 column norms reported only, no dominance stop; calibration-first A/B selection (§6) |
| D7 — decided 2026-11-02: Fitting-path dependency | Wait for delivered #235 qualification on the merged #962 wheel; no duplicate driver repair (§7) |
| D8 — proposed: Limits and exclusions | 360 executable +40 numerical-check lines; 12 h computation including 4 h pure preparation; pressure/speciation only (§8) |

This draft is ready to be **reviewed as a proposal**, not declared Ready for
Build. Independent readiness review is not performed by this implementor;
no subagent or review was authorized in this task. The accountable parent
publishes the accepted design to #241 through its approved issue-change
process and reads it back before Build. No tracker body was changed here.

### Further reading or preparation needed

- Approve §3 observation roles, residual scales, five-coordinate bounds,
  profile/acceptance policy and D8 limits. The three required pressure PDFs
  are now available; additional original density sources remain unadmitted.
- Read Hartono 2021 cited uncertainty methods and SI Part A1 before materializing
  its 47-row calibration packet; retain Table 4 stock composition and reported
  u(P)/u(alpha). Verify no reused Kundu observations. Hartono 2020 original
  calibration inventory and Yi 2024 SI are required if importing their fitted
  quantities is later proposed; none are imported here.
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
For the present revision, Klepáčová's full Experimental/Results/Antoine
sections and Tables 1/10/11, Belabbaci §§2–4 and Tables 1–3, Pappa §§2–4
and Tables 1–4, Hartono Eq.2 and Ayad Tables 1/2/5/6, §§2.1/2.2/4.5
were inspected directly in the live Zotero PDFs. New source identities,
hashes, readings and arithmetic are retained in §3; earlier comparison
numbers remain attributed. The present revision adds three original papers
and PDFs, revises the design only, and performs source-equation arithmetic.
No Engine probe, fitting, repository code or physical validation was performed.
