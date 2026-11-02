# AMP transfer assessment: source admission (#242, stage 1)

Gates from the accepted design (`analyses/amp_pz_scoping/design-draft-amp.md`
at `842bc73`, "Further reading"). Values: `results/source-preparation.json`,
from `prepare.py` (NumPy only; no Engine call).

## Hartono 2021 uncertainty methods and Supporting Information Part A1

Hartono, Ahmad, Svendsen & Knuutila 2021, DOI 10.1016/j.fluid.2021.113235;
Zotero `JJXAM5ET`, PDF `MTJ4JDPP`. Read §3.1, §§3.2.2–3.2.4, §4.3.1,
Tables 3, 4 and 7. The supplement is the publisher archive
`https://ars.els-cdn.com/content/image/1-s2.0-S0378381221002983-mmc1.zip`
(SHA-256 `a2d057c8…96e2`; enclosed `mmc1.docx` SHA-256 `0949b3c8…e798`).
Like the Ciftja 2014 supplement, it is not attached in Zotero: Companion has
no attachment route for a Word file.

- **Table 7 is calorimeter VLE.** §4.3.1 places the 3.0 M AMP total pressures
  under reaction calorimetry. SI Eqs. A1.1–A1.5 give the CO2 amount absorbed
  from vessel and reactor pressure drops (gas-phase CO2 by an equation of
  state); the loading follows from that amount and the titrated amine.
- **Uncertainty method.** SI Eqs. A1.7–A1.8: Gaussian propagation
  (Eurachem/CITAC) of temperature, pressure, equation-of-state Z, balance,
  vessel and reactor volumes, solvent amount and density. The SI states a
  coverage factor of 2 (95 %) for the heat tables; u(α) uses the same
  propagation. Table 7's u(P) and u(α) are therefore taken as expanded values;
  this is an inference for the VLE columns.
- **Consequence for the residual.** u(P)/P ≤ 0.15/6.8 = 2.2 % in every
  calibration row, so the design's 5 % pressure floor binds in all 47 rows
  whether u(P) is standard or expanded. u(α) (0.01–0.03) enters only the
  post-fit perturbation comparison (§5).
- **Stock.** Table 4: 3.0 mol/dm³, 4.1 mol/kg water, 26.8 mass %. The
  feed uses the mass percent (three significant figures): 13.515 mol water per
  mol AMP; this implies 4.107 mol/kg, consistent with 4.1. Purity ≥ 0.985
  (Table 3), used without purification.
- **Rows.** `inputs/hartono-2021-table-7.csv`: 15 + 17 + 15 = 47 calibration
  rows at 313/333/353 K (both 333 K α = 0.94 rows kept) and 11 + 7
  supplemental rows at 373/393 K. Values copied from the PDF text layer;
  the column footnote's denominator (AMP + PZ) is AMP alone for this solution.
- SI Part B1 corrects subscripts in Hartono 2020's eNRTL table; no fitted
  Hartono quantity is imported here, so it has no effect.

## Kundu hold-out overlap

Kundu 2003 (51 rows) is 2.0, 2.8 and 3.4 mol/L stock at 303–323 K with
measured p_CO2. The calibration packets are Hartono 2021 Table 7 (3.0 M total
pressure, 313–353 K, NTNU calorimeter), Hartono 2013 Table 3 (unloaded
AMP–water VLE), and Ciftja 2014 NMR (30 mass %, no pressure). No stock,
observable and isotherm coincide; the exact row comparison finds **0
identical rows**. Hartono 2021's reference list (pp.17–18) does not cite
Kundu, so no Kundu observation is reused in its Table 7. Hartono 2021 states
that literature data entered its own eNRTL parameter fit; no Hartono fitted
quantity is used here, so that does not compromise Kundu as a test of this
fit. **Overlap check: passed; no redesign needed.**

## Hamborg Table 16 correlation and its uncertainty (D4)

Weighted least squares of Eq. 21, ln K = A/T + B + C ln T, on all 24 runs,
weights 1/u², u = printed ±0.04 (±0.03 run 24):
A = −3850.736 K, B = −55.31796, C = 8.064629. χ² = 17.0 on 21 degrees
of freedom; largest |residual|/u = 1.47, so no run disagrees beyond its
printed scale. The fit reproduces Table 1's printed correlated values
(−21.948 vs −21.95 at 303 K; −20.042 vs −20.04 at 333 K) and its
ΔH°(298.15 K): 52.0 vs 52.2 kJ/mol. Propagated standard error of ln K,
treating the printed values as standard deviations: 0.018 (293 K),
0.012 (313 K), 0.012 (333 K), 0.018 (353 K). Full covariance, its χ²-scaled
form and every run residual are retained. Domain: 293.12–353.22 K. The
four-rounded-value reconstruction in `amp_pz_scoping/sources` is superseded
as an executable law; it remains a transcription check.

## Engine standard-state mapping

Both AMP laws use the basis of the adopted MEA R4 and R5 declarations
(`analyses/solvent_specification_mea/declarations.toml`):
`standard_state_id = "aqueous-molality-infinite-dilution-water-v1"`,
`source_basis = "CommonMolalityInfiniteDilution"`, standard molality
1 mol/kg, reference pressure 10⁵ Pa, water explicit with stoichiometry −1.
The Engine law is ln K = a + b/T + c ln(T/T_ref) + d T.

| Reaction (as written) | Source law | Engine coefficients |
|---|---|---|
| AMPH⁺ + H2O ⇌ AMP + H3O⁺ | Hamborg: A/T + B + C ln T, molality, water explicit, 1 bar | b = A, c = C, a = B + C ln(313.15 K) = −8.97310, T_ref = 313.15 K, 293.12–353.22 K |
| AMPCOO⁻ + H2O ⇌ AMP + HCO3⁻ | Xu/Silkenbäumer (D1): −2546.2/T + 11.555, molality, water explicit | a = 11.555 (δ = 0 origin), b = −2546.2 K, c = d = 0, bounds on a [8.555, 13.555] |

Both are already on the Engine's common molality basis, so no constant
conversion (such as ln 55.51) is applied. The hydrolysis domain is set to the
assessment interval 293.15–393.15 K of the shared R2 law; its use below
313 K is the owner-accepted extrapolation. Evaluation of ln Q = ln K for
every reaction at one solved loaded AMP state is the §7 check run with the
reactive declarations.
