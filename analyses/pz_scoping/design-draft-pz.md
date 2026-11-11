# Design revision: aqueous PZ transfer assessment

Design-only revision for [#308](https://github.com/tannerpolley/Amine-Thermodynamics/issues/308), 11 November 2026. The issue body and [readiness findings and owner decisions](https://github.com/tannerpolley/Amine-Thermodynamics/issues/308#issuecomment-6807792799) supersede the earlier draft. **No fitting or Engine calculation was performed. Numerical Build remains blocked by the unavailable pure-PZ reference correlations and the new parameter choices requiring owner decision below.** Independent re-review follows delivery of this revision.

## Question, intended use and fixed identities

Can the adopted MEA formulation, with shared species fixed, describe aqueous PZ CO2 pressure and NMR speciation in the source-observed liquid states? The endpoint is a conditional single-amine parameter assessment for later AMP/PZ work, not absorber, caloric or precipitation qualification. NMR agreement is calibration. The untouched Ermatchkov 2006 pressure campaign tests transfer beyond calibration; it does not validate individual ion parameters.

Freeze H2O, CO2, H3O+, OH−, HCO3−, CO3²− and every shared–shared interaction from `analyses/mea_parameter_bundle/results/selected-current-best-parameters.json`, SHA-256 `f8f64820b161377a0d97d1e4ad4f6cea764cd0558dc63231d58e2096988eef97` (#255/#297). Use Engine merged commit `391dfe5d64ede5036bf160bc6ae037ad5e14af32`, wheel SHA-256 `0962e21d2fa7a8ba1ed4622f1110b3e8053bacd878fa41c999d85e8b9afab66b`. Never import Engine source.

R1–R3 are completed declarations in `analyses/solvent_specification_mea/declarations.toml`, `chemistry.reactions.aqueous` (file SHA-256 `fa5893fa2e81dfb747befe9ce22e9519a5fc299d697f4ce7272d731b687ce8b8`). Copy their nonzero stoichiometry, correlations, reference bases and domains unchanged, dropping only zero MEA entries. R2 already includes the adopted MEA enthalpy shift: do not apply it twice. In Engine polynomial form, reference temperature 313.15 K:

| Law | a | b (K) | c | d,e,f | Source basis; domain (K) |
|---|---:|---:|---:|---|---|
| R1 | 3.7290977365566675 | −13445.9 | −22.4773 | 0 | RawMoleFractionInfiniteDilution; 273.15–498.15 |
| R2 | 23.87092013089665 | −12017.430996556475 | −36.7816 | 0 | CommonMolalityInfiniteDilution; 293.15–393.15 |
| R3 | 12.145792981306897 | −12431.7 | −35.4819 | 0 | RawMoleFractionInfiniteDilution; 273.15–498.15 |

Below 293.15 K, R2 is also extrapolated. Keep that label on the 283 K NMR results; extending the evaluation domain must not relabel the source domain.

## Chemistry and source laws

[Chemistry](chemistry.md) owns twelve liquid species, P1–P5, numerical source anchors and balanced reactions; vapor contains H2O/CO2/PZ only. PZH2²+ is retained. HPZCOO is neutral and liquid-only, with no Debye–Hückel or Born contribution. Feed basis is one mole analytical PZ and source water, with alpha moles CO2. Alpha is mol CO2/mol PZ; multiply per-alkalinity loadings by two. Preserve original molality and isotope basis.

Fit Hamborg Table 16's 24 runs per protonation step to Eq.21, ln K=A/T+B+C ln T, using ±0.04 ln K as the reported run scale. Retain coefficient covariance and all run residuals. Map Table 9/first block to P2 (pKa about 5.4), Table 10/second block to P1 (about 9.7); Hetzer is an independent cross-check, not extra calibration. Fit/freeze these laws in stage 3, not here. Keep Ermatchkov 2003 Table 5 slopes for P3–P5 and allow only additive natural-log offsets. Source hydrolysis laws are minus ln(10) times (A+B/T): P3 (−3.750,1570.4 K), P4 (4.354,1517.0 K), P5 (−1.587,574.2 K). No extra temperature coordinate.

Declare the source molality standard and Engine ReactionReference once; do not manually convert as well. If a diagnostic uses mole-fraction constants, the ideal conversion is ln Kx=ln Km+Delta_nu ln(0.0180153), Delta_nu=+1 for each P law. Explicit water activity stays in the reaction. Verify source anchors, reciprocal reversal and reference mapping before fitting. Ermatchkov's D2O rows are accepted as H2O treatment by owner decision; isotope bias remains unquantified.

## Pure-PZ reproduction and dielectric inputs

Razavi 2019 Table 1 p.11040 uses refs **100/136 for vapor pressure**, **130 (Yaws 2014) for density**. [Pure-PZ source note](sources/pure-pz-pcsaft.md) gives the exact bibliographic binding and unresolved correlation inputs. Neither pressure nor density coefficients are available in the inspected local library. Missing coefficient sets, phase classification or reference grid stops stage 1; an independently chosen correlation cannot silently replace them. The reported 0.33% pressure and 1.65% density AARDs are reproduction targets for the original fit, not measurement uncertainties or pointwise error gates.

Freeze Razavi's effective 2B neutral set: m=2.6519, sigma=3.7136 Å, u/k=274.10 K, epsilon_AB/k=1923.25 K, kappa_AB=0.07275; one donor and one acceptor, sigma cubed association prefactor (Eq.7). Reproduction must retain per-point and aggregate errors on 323–630 K pressure and 420–570 K density separately. Once the exact reference grid is obtained, report whether aggregate AARD rounds to the printed figures at their stated precision; if grid/weighting is unrecoverable, report a comparison, not exact reproduction. Diagnose any difference and ask the owner about continuation or refit. No invented percentage margin. Subcooled use down to 283 K is owner-accepted conditional on this check, not physical validation of pure liquid PZ there.

The [dielectric source assessment](sources/dielectric-and-uncertainty.md) found an analog-based PZ permittivity estimate, not sufficient measurements to determine the adopted two-coefficient law, and no zwitterion measurements. Apply the owner's fallback: both neutral PZ and HPZCOO have fixed dielectric_volume=0.7309865858310542 L/mol and dielectric_temperature=1019.0802597119892 K, copied from adopted neutral MEA. These are a transfer assumption, not PZ data. No dielectric coordinate enters either variant. Freeze shared-water/CO2 dielectric coefficients unchanged. This assumption limits ion-solvation and low-temperature interpretation.

## Complete parameter declarations proposed for owner decision

The original issue accepts the A/B comparison, not numeric bounds or every tie. The two tables below are complete proposals; new unsupported choices remain owner decisions. F=fixed; V=free; T=tied. For fixed/tied quantities the scale is not applicable and bounds equal their value or their parent bounds. All free scales are affine optimizer units. **Search bounds are engineering allowances, never measured uncertainty.** They do not constitute uncertainty on ion properties. A bound endpoint goes to the owner, without automatic widening.

Both variants use m=1 nonassociating spheres for both carbamates, packing diameter 0.88 sigma, Debye–Hückel diameter sigma, solvation factor 1; charge is −1/−2 respectively. The neutral zwitterion has its own fixed m=2.6519 and no association sites (including cross-association), standard neutral temperature-dependent diameter, and fitted sigma/u. These are declared hypotheses without a measured PZ-ion parameter source. Same-sign ion dispersion exclusion follows adopted MEA for spheres. B uses charged-molecule dispersion including cation self-dispersion and neutral-style packing. Cross-association for B cations uses neutral PZ's 2B sites and kappa with zero cation self energy, adopted combining rule to water/PZ, none to CO2; no sites for either carbamate. All species masses/formulas come from the balanced chemistry, not the analog.

Use k(T)=k0+k1(T−353.15 K), dimensionless k0 and k1 in K−1. Fit these two to Hartono only, then freeze for reactive fitting. Shared pairs stay unchanged; unspecified new dispersion corrections are fixed zero, no extra association corrections. Both tables cover every new quantity; no other parameter may be released.

### Variant A: single-sphere cations

| Quantity | Status | Start/value | Scale | Bounds | Basis |
|---|---|---|---|---|---|
| Shared species/pairs; R1–R3 | F | hash-bound above | — | fixed | adopted MEA |
| Neutral PZ m,sigma,u,epsilon_AB,kappa,2B sites | F | values above | — | fixed | Razavi Table 1/Eq.7, conditional reproduction |
| PZ and HPZCOO dielectric coefficients | F | MEA values above | — | fixed | owner-authorized transfer |
| PZ–water k0; k1 | V then F | 0; 0 K−1 | 0.05; 0.001 K−1 | [−0.5,0.5]; [−0.005,0.005] K−1 | proposed engineering search |
| PZH+ m,charge,sites | F | 1,+1,none | — | fixed | MEA sphere convention |
| PZH+ sigma | V | 5 Å | 0.25 Å | [3,7] Å | proposed effective sphere |
| PZH+ u/k | V | 274.10 K | 50 K | [100,500] K | neutral PZ seed; search allowance |
| PZH+ Born diameter | V | 5 Å | 0.5 Å | [3,8] Å | MEA seed; search allowance |
| PZH+ packing,DH,solvation | T/F | 0.88 sigma,sigma,1 | — | parent/fixed | adopted sphere rule |
| PZH2²+ m,charge,sites | F | 1,+2,none | — | fixed | owner keeps species; sphere hypothesis |
| PZH2²+ sigma,u,Born,packing,DH,solvation | T | respective PZH+ values | — | parent | no independent +2 coordinate |
| PZH+–water k; PZH+–HCO3− k | V | 0;0 | 0.05;0.05 | [−0.5,0.5] each | proposed search |
| Corresponding PZH2²+ pair k | T | corresponding PZH+ pair | — | parent | no extra coordinate |
| PZCOO− m,charge,sites,packing,DH,solvation | F/T | 1,−1,none,0.88 sigma,sigma,1 | — | fixed/parent | common carbamate hypothesis |
| PZCOO− sigma;u/k;Born | V | 5 Å;274.10 K;5 Å | 0.25 Å;50 K;0.5 Å | [3,7] Å;[100,500] K;[3,8] Å | proposed search |
| PZCOO−–water k | V | 0 | 0.05 | [−0.5,0.5] | proposed search |
| PZ(COO)2²− m,charge,sites,packing,DH,solvation | F/T | 1,−2,none,0.88 sigma,sigma,1 | — | fixed/parent | same representation |
| PZ(COO)2²− sigma;u/k;Born | V | 5 Å;274.10 K;5 Å | 0.25 Å;50 K;0.5 Å | [3,7] Å;[100,500] K;[3,8] Å | proposed search |
| PZ(COO)2²−–water k | T | PZCOO−–water k | — | parent | no extra pair |
| HPZCOO m,charge,sites | F | 2.6519,0,none | — | fixed | neutral-chain hypothesis |
| HPZCOO sigma;u/k | V | 3.7136 Å;274.10 K | 0.25 Å;50 K | [3,5] Å;[100,500] K | neutral PZ seed/search |
| HPZCOO electrostatics/packing | F/T | no DH/Born; neutral d(T) | — | fixed/parent | neutral zwitterion hypothesis |
| P1/P2 coefficients | F after stage 3 | Table-16 weighted correlation | — | frozen source fit | Hamborg; covariance retained |
| P3/P4/P5 additive ln K offsets | V | 0 each | 1 each | [−3,3] each | source-law starts; engineering allowance |
| Every other new pair/association correction | F | zero | — | fixed | avoids unbounded model expansion |

### Variant B: charged-molecule cations

| Quantity | Status | Start/value | Scale | Bounds | Basis |
|---|---|---|---|---|---|
| Shared species/pairs; R1–R3 | F | same hash-bound record | — | fixed | adopted MEA |
| Neutral PZ five values,sites | F | 2.6519,3.7136 Å,274.10 K,1923.25 K,0.07275,2B | — | fixed | Razavi |
| PZ and HPZCOO dielectric coefficients | F | MEA values above | — | fixed | transfer assumption |
| PZ–water k0;k1 | V then F | 0;0 K−1 | 0.05;0.001 K−1 | [−0.5,0.5];[−0.005,0.005] K−1 | same binary fit |
| PZH+ m,charge,sites,kappa,self energy | F | 2.6519,+1,2B,0.07275,0 K | — | fixed | charged-molecule analog, Wangler §3.1 |
| PZH+ sigma;u/k;Born | V | 3.7136 Å;274.10 K;5 Å | 0.25 Å;50 K;0.5 Å | [3,5] Å;[100,500] K;[3,8] Å | proposed search |
| PZH+ packing,DH,solvation | T/F | neutral d(T),sigma,1 | — | parent/fixed | B convention |
| PZH2²+ m,charge,sites,kappa,self energy | F | 2.6519,+2,2B,0.07275,0 K | — | fixed | same topology |
| PZH2²+ sigma,u,Born,packing,DH,solvation | T | respective PZH+ values | — | parent | no +2 coordinate |
| PZH+–water k;PZH+–HCO3− k | V | 0;0 | 0.05;0.05 | [−0.5,0.5] each | same search |
| Corresponding PZH2²+ pair k | T | corresponding PZH+ pair | — | parent | same ties |
| PZCOO− m,charge,sites,packing,DH,solvation | F/T | 1,−1,none,0.88 sigma,sigma,1 | — | fixed/parent | same carbamate as A |
| PZCOO− sigma;u/k;Born | V | 5 Å;274.10 K;5 Å | 0.25 Å;50 K;0.5 Å | [3,7] Å;[100,500] K;[3,8] Å | same search |
| PZCOO−–water k | V | 0 | 0.05 | [−0.5,0.5] | same search |
| PZ(COO)2²− m,charge,sites,packing,DH,solvation | F/T | 1,−2,none,0.88 sigma,sigma,1 | — | fixed/parent | same carbamate as A |
| PZ(COO)2²− sigma;u/k;Born | V | 5 Å;274.10 K;5 Å | 0.25 Å;50 K;0.5 Å | [3,7] Å;[100,500] K;[3,8] Å | same search |
| PZ(COO)2²−–water k | T | PZCOO−–water k | — | parent | same tie |
| HPZCOO m,charge,sites | F | 2.6519,0,none | — | fixed | same neutral hypothesis |
| HPZCOO sigma;u/k | V | 3.7136 Å;274.10 K | 0.25 Å;50 K | [3,5] Å;[100,500] K | same search |
| HPZCOO electrostatics/packing | F/T | no DH/Born; neutral d(T) | — | fixed/parent | same hypothesis |
| P1/P2 coefficients | F after stage 3 | Table-16 weighted correlation | — | frozen source fit | same source |
| P3/P4/P5 offsets | V | 0 each | 1 each | [−3,3] each | same search |
| Every other new pair/association correction | F | zero | — | fixed | same model boundary |

Each variant has two binary coordinates followed by seventeen reactive coordinates. Before optimization and at each endpoint, retain the uncertainty-scaled calibration Jacobian singular spectrum and right singular vectors, perturb coordinates by their scales, and compare changes to source uncertainty. Report numerical rank with derivative-step sensitivity; no arbitrary condition-number threshold is a scientific acceptance gate. A direction unresolved at measurement resolution is a rank/identification concern and goes to the owner.

Only proposed reductions, in this order, are: tie dicarbamate sigma/u/Born to monocarbamate (removes 3); fix P4 offset at 0 (removes 1); fix both carbamate Born diameters at 5 Å (removes 1 after the tie); fix HPZCOO u/k at 274.10 K (removes 1). Each requires owner continuation approval after the singular vectors and observable effects are shown; recheck rank on calibration data. Do not drop PZH2²+, release dielectric coefficients, change shared parameters or add pairs to rescue a fit. Select A/B on calibration evidence and identification only, before opening the hold-out.

## Domain, data roles and temperature reports

Calibration uses source rows down to 283.15 K: Ermatchkov 2003 all 121 NMR rows (including 66 at 283/298 K), Hilliard D.5 62 pressure rows and Hartono Table 6 23 binary rows; the 80 °C x=0.0472 outlier is reported apart. Row admission below still applies. Hilliard D.2 is an unloaded comparison, not additional binary calibration. Derks 58 dilute rows, Kamps total pressure, Dugas 80/100 °C, Xu Pt and Bishnoi remain secondary comparisons; no hold-out selection by residual size. The [data map](data-map.md) retains their source bases, duplicates and uncertainties.

| Report | Extrapolated inputs to label |
|---|---|
| Below 313 K, separate calibration/comparison summaries by source and temperature | Pure PZ below pressure 323 K/density 420 K; Hamborg below 293 K; R2 below 293.15 K; binary k below Hartono 333 K |
| Ermatchkov 2006 313 K | Pure PZ pressure/density; binary k below 333 K; carbamate and Hamborg laws inside source ranges |
| Ermatchkov 2006 353 K | Pure PZ density; carbamate laws above 333 K; Hamborg at upper measured boundary |
| Ermatchkov 2006 393 K | Pure PZ density; carbamate and Hamborg above their ranges; binary k above 373 K |

Use actual row temperatures; corrected Kamps blocks remain separate, including 374–395 K and pressures below 0.2 MPa. No pooled pressure metric may hide one of the three primary isotherms. Calibration below 313 K is authorized extrapolation, not proof that a pure subcooled state exists.

## Operational residuals and uncertainty

[Uncertainty source note](sources/dielectric-and-uncertainty.md) records exact passages and interpretation. For any positive pressure report signed log ratio and its asymmetric source interval: log((p−Delta p)/p), log((p+Delta p)/p); when p−Delta p<=0 use the linear interval without logging its lower endpoint. A normalized scalar diagnostic is (p_calc−p_obs)/Delta p, and the fit uses that difference form when needed. State whether a source supplies a bound, standard deviation or repeatability; do not call all of them Gaussian standard errors. Report per-row intervals, signed bias, RMS scaled residual, fraction within intervals and near-miss distances, grouped by campaign/temperature. None is an automatic continuation threshold.

- **Ermatchkov 2006:** use the total uncertainty printed in parentheses beside p in Tables 1–3 exactly once (the review's total Delta p*). Do not add 0.02p, temperature or composition propagation again. The Results paragraph p.1789 decomposes the total into a propagated contribution plus calibration; Delta p_repr in the last column is repeatability, not another independent scale. Retain both columns and raw symbols to prevent confusing these quantities. No pressure fitting on this campaign.
- **NMR:** let f0=(PZ+PZH++PZH2²+)/PZtotal, f1=(PZCOO−+HPZCOO)/PZtotal, f2=PZ(COO)2²−/PZtotal. Ermatchkov Eqs.2–7 give f0=A2/S, f1=(A1+A4)/S, f2=A3/S with S=sum A. Use only f1,f2. As a proposed operational uncertainty model, assign relative peak-area scale q=0.02 to each A; propagate through the normalization Jacobian J to C=J diag((q A_i)^2) J^T, then use the two-dimensional covariance submatrix for (f1,f2). Source 2±1.9% is an estimated area consistency error, not four independent measured standard deviations: repeat diagnostics with q=0.039 and report sensitivity. This independence assumption and covariance use require owner acceptance; do not claim a source covariance. The tabulated groups reconstruct A/S, with A1=A4=f1 S/2 only as an uncertainty-model assumption. **Ten blank dicarbamate entries are missing observations, not zero and not a detection limit**: omit f2, retain a scalar f1 residual with scale q f1 (and q=0.039 sensitivity), a declared group-error approximation because missing peak 3 prevents reconstructing full area covariance; normalization still uses analytical PZtotal. Do not close the blank by subtracting rounded f0/f1 or add a censored penalty without a measured detection limit. Retain blank identity, source precision and material balances. Isotope bias is separate and unquantified.
- **Hartono:** prefer fitting (P,y) rather than (P,yP) as independent observations: P scale 0.3 kPa, vapor y rounding half-width 0.00005 (four decimal places), plus source titration uncertainty, retained separately. Kim 2008 p.2528 reports less than 1% repeatability of three parallel titrations of standards; propose 0.01y as an analog method scale and report rounding bounds explicitly. This is not demonstrated Hartono PZ accuracy; the Hartono less-than-2% statement concerns NMR, not binary titration. Return consequential low-y disagreement to the owner rather than treating the analog scale as known total uncertainty. Use the same treatment for liquid x and its printed precision through input sensitivity. If scoring (P,pPZ=yP), propagate one shared pressure error: Var(pPZ)=y² Var(P)+P² Var(y), Cov(P,pPZ)=y Var(P), Var(y)=(0.01y)²+(0.00005/sqrt(3))² for the declared uniform rounding approximation. Whiten this 2x2 covariance; do not independently count P twice. Across-row pressure calibration correlation is unknown: retain a campaign-common ±0.3 kPa sensitivity comparison rather than assume independence proves information. T scale 0.05 K propagates once; shared inputs produce covariance. This is an operational weighting convention, not a source confidence interval.
- **Hilliard/Derks/Kamps and secondary rows:** source scales and input propagation are retained by row; missing uncertainty means candidate/unscored, never a default percentage. Derks loading uncertainty propagates into pressure; Kamps uses the printed apparatus full-scale pressure bound (or conservative 10% below 0.1 MPa), not partial-pressure uncertainty. Shared preparation/calibration errors remain grouped. Do not score a derived activity coefficient alongside its generating P,y observations.

The falsifier is the frozen model's disagreement with source uncertainty intervals on each Ermatchkov 2006 isotherm. Agreement within an interval supports that observable at that state only. Near-misses remain near-misses. Consequential decisions on continuation, stage acceptance, representation selection under ambiguous calibration, or hold-out disagreement go to the owner with residual patterns and source limitations. No transferred MEA percentage cutoff, no automatic retuning on the hold-out.

## Row admission against solids and fluid phases

**This assessment declares no qualified solid model.** The pinned Engine has SolidSpec; availability is not PZ solid qualification. Do not claim the Engine lacks solids. Source-observed liquid states support those measurements, not a universal solid-free envelope. Apply the [source-specific admission table](sources/solid-phase.md#row-admission-for-308) before looking at residuals. Every prepared row must retain source/table/row, analytical mPZ, alpha per PZ, T, phase evidence, decision and reason. A source-marked precipitate is excluded; a boundary or phase ambiguity is quarantined and sent to the owner. Never use Freeman's 8/10 m curves for dilute rows.

Run declared liquid/vapor tangent-plane trials and the adopted dense/gas classifier at all fitted/scored states; unresolved trials stop adoption. These check fluid phases only. The review already admitted twelve-species structure on the pinned wheel; that is not reactive numerical qualification. Verify balances, reaction/reference anchors, unchanged shared-only predictions, one loaded state, replay, derivatives and retained phase trials before reactive fitting; inherit numeric tolerances from the adopted MEA driver, not measurement error. Generic EOS, equilibrium and regression mechanics remain Engine-owned.

## #308 sequence, delivery and decisions

1. Independent readiness re-review of this revised design. Only Ready permits numerical Build after the owner resolves the named choices and missing source inputs.
2. Pure-PZ reproduction; retain the reference coefficients, grids, residuals and convention comparison. Missing references or mismatch stops for the owner; a refit is not silently authorized by a discrepancy.
3. PZ–water calibration; retain fitted k0,k1 and covariance, comparison with Hilliard D.2, outlier and phase evidence.
4. Speciation laws; Hamborg transcription/correlation, source-reference checks and Ermatchkov slope/offset declarations.
5. Reactive fitting; calibration-only rank, A/B selection and any owner-authorized reductions.
6. Freeze endpoint; score untouched Ermatchkov 2006 separately at 313/353/393 K and the declared secondary comparisons. Do not fit or select on hold-out results.

Each numerical stage needs a delivered-result review and owner continuation decision when a stop condition fires. AMP proceeds in parallel; AMP-first is superseded by #308. Blend and manuscript are out of scope. Keep the wheel immutable; no Engine edits, no edits to `analyses/_cse-manuscript.json`. A later authorized Analyze/Summarize retains numbers and uncertainties in the PZ research notebook; no empty result notebook is created by this design revision.

| Open item | Recommendation | Gate |
|---|---|---|
| Exact Yaws 2014 density and Yaws 2015/HYSYS V9 pressure coefficients, phase and reference grid | Obtain lawful source records before stage 1; retain Block until bound; if unavailable ask owner to replace the reproduction prerequisite with a separately sourced pure-data design | source blocker, not an inferred fit failure |
| New numeric parameter bounds, carbamate spheres, +2 ties, neutral nonassociating zwitterion and fixed m | Approve both complete tables as conditional hypotheses; keep engineering bounds distinct from evidence | owner decision before Build |
| Rank reductions | Permit only the listed order, with each actual continuation call returned to owner | owner decision at rank concern |
| NMR covariance and blank policy | Accept area-based propagation with q=0.02 and 0.039 sensitivity; blanks unscored for f2 | owner decision before scoring |
| Unsupported solid boundary or marginal source-scale agreement | Admit source-observed rows as limited evidence, quarantine unresolved rows and decide continuation from the named cohort | owner decision when encountered |

The original accepted decisions (laws, H2O treatment, kept +2 species, cation comparison, Hartono calibration, separate comparisons and domain restriction) are not reopened. The owner already authorized low-temperature extrapolation and the dielectric fallback. No measurement result or physical validation is claimed by this revision.
